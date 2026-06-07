"""
BrainScan AI — FastAPI Backend
Port 8000 | ResNet50 | 4 classes
"""

import sys
import os
import pathlib
import hashlib
import random
import time
import base64
import io
from contextlib import asynccontextmanager
from pathlib import Path

# ── Pathlib patch (cross-platform PyTorch checkpoint loading) ─────────────────
if not hasattr(pathlib, "_local"):
    pathlib._local = pathlib.Path
sys.modules["pathlib._local"] = pathlib

import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.cm as cm_module
import cv2

from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional

# ── Paths & settings ──────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent
SRC_DIR    = BASE_DIR / "src"
DATA_DIR   = BASE_DIR / "data" / "processed"
sys.path.insert(0, str(SRC_DIR))

from api.settings import settings, get_logger          # noqa: E402
from model_architecture import ResNet50Classifier      # noqa: E402

MODEL_PATH = settings.MODEL_PATH
log = get_logger("brainscan.api")

# ── Optional rate limiter (slowapi) ───────────────────────────────────────────
_LIMITER = None
if not settings.DISABLE_RATELIMIT and settings.RATE_LIMIT > 0:
    try:
        from slowapi import Limiter
        from slowapi.util import get_remote_address
        from slowapi.errors import RateLimitExceeded
        from slowapi.middleware import SlowAPIMiddleware
        _LIMITER = Limiter(key_func=get_remote_address,
                           default_limits=[f"{settings.RATE_LIMIT}/minute"])
        log.info(f"Rate limiting enabled: {settings.RATE_LIMIT} req/min/IP")
    except ImportError:
        log.warning("slowapi non installé — rate limiting désactivé")

# ── Constants ─────────────────────────────────────────────────────────────────
CLASS_NAMES  = ["Glioma", "Meningioma", "No Tumor", "Pituitary"]
CLASS_KEYS   = ["glioma", "meningioma", "no_tumor", "pituitary"]
DATA_FOLDERS = {
    "glioma":      DATA_DIR / "glioma",
    "meningioma":  DATA_DIR / "meningioma",
    "no_tumor":    DATA_DIR / "notumor",
    "pituitary":   DATA_DIR / "pituitary",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_CACHE     = 100

MEDICAL_INFO = {
    "glioma": {
        "class":       "Glioma",
        "description": "Malignant tumor originating from glial cells of the brain or spinal cord.",
        "prevalence":  "~3 per 100,000 people annually",
        "grade":       "WHO Grade I-IV",
        "typical_mri": "Irregular borders, surrounding edema, ring enhancement on T1",
        "symptoms":    ["Headaches", "Seizures", "Cognitive changes", "Vision loss", "Weakness"],
        "urgency":     "High — immediate neurological evaluation required",
        "color":       "#EF4444",
    },
    "meningioma": {
        "class":       "Meningioma",
        "description": "Usually benign tumor arising from the meninges surrounding the brain and spinal cord.",
        "prevalence":  "~7.8 per 100,000 people",
        "grade":       "WHO Grade I (90% benign)",
        "typical_mri": "Well-defined, dural attachment, homogeneous enhancement",
        "symptoms":    ["Headaches", "Focal weakness", "Vision problems", "Seizures"],
        "urgency":     "Moderate — specialist referral recommended",
        "color":       "#F59E0B",
    },
    "no_tumor": {
        "class":       "No Tumor",
        "description": "No tumor detected on this MRI. The brain appears within normal limits.",
        "prevalence":  "N/A",
        "grade":       "N/A",
        "typical_mri": "Normal brain parenchyma, no mass lesion identified",
        "symptoms":    [],
        "urgency":     "Low — routine follow-up if symptomatic",
        "color":       "#10B981",
    },
    "pituitary": {
        "class":       "Pituitary Tumor",
        "description": "Tumor developing in the pituitary gland, usually a benign adenoma.",
        "prevalence":  "~77 per 100,000 people",
        "grade":       "Usually benign adenoma",
        "typical_mri": "Sellar/suprasellar mass, homogeneous T1 signal",
        "symptoms":    ["Hormonal imbalance", "Vision changes", "Headaches", "Fatigue"],
        "urgency":     "Moderate — endocrinology and neurosurgery referral needed",
        "color":       "#3B82F6",
    },
}

# ── Globals ───────────────────────────────────────────────────────────────────
predictor = None
prediction_cache: dict = {}
session_stats = {
    "total":           0,
    "class_counts":    {k: 0 for k in CLASS_KEYS},
    "total_conf":      0.0,
    "total_time_ms":   0.0,
}

# ── Image preprocessing ───────────────────────────────────────────────────────
TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def load_pil_from_bytes(raw: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(raw))
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def load_pil_from_npy(path: Path) -> Image.Image:
    arr = np.load(str(path))
    if arr.ndim == 2:
        arr = np.stack([arr] * 3, axis=-1)
    if arr.max() <= 1.0:
        arr = (arr * 255).astype(np.uint8)
    else:
        arr = arr.astype(np.uint8)
    return Image.fromarray(arr).convert("RGB")


def pil_to_base64(img: Image.Image, fmt: str = "JPEG") -> str:
    buf = io.BytesIO()
    img.save(buf, format=fmt, quality=85)
    return base64.b64encode(buf.getvalue()).decode()


def ndarray_to_base64_png(arr: np.ndarray) -> str:
    buf = io.BytesIO()
    Image.fromarray(arr.astype(np.uint8)).save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


# ── Model loader ──────────────────────────────────────────────────────────────
def load_model() -> ResNet50Classifier:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Checkpoint introuvable : {MODEL_PATH}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ResNet50Classifier(num_classes=4, pretrained=False)

    orig_win  = pathlib.WindowsPath
    orig_pos  = pathlib.PosixPath
    try:
        pathlib.WindowsPath = pathlib.PureWindowsPath
        pathlib.PosixPath   = pathlib.PurePosixPath
        checkpoint = torch.load(str(MODEL_PATH), map_location=device, weights_only=False)
    finally:
        pathlib.WindowsPath = orig_win
        pathlib.PosixPath   = orig_pos

    state = checkpoint["model_state_dict"] if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint else checkpoint
    model.load_state_dict(state)
    model.to(device)
    model.eval()
    model._device = device  # keep reference
    log.info(f"Modèle chargé sur {device}")
    return model


# ── Prediction ────────────────────────────────────────────────────────────────
def run_predict(model: ResNet50Classifier, pil_img: Image.Image):
    tensor = TRANSFORM(pil_img).unsqueeze(0).to(model._device)
    with torch.no_grad():
        out   = model(tensor)
        probs = F.softmax(out, dim=1)[0].cpu().numpy()
    idx        = int(probs.argmax())
    confidence = float(probs[idx])
    return idx, confidence, probs, tensor


# ── Grad-CAM (PyTorch hooks — inline, no TF dependency) ──────────────────────
def compute_gradcam(model: ResNet50Classifier, tensor: torch.Tensor, target_idx: int):
    activations, gradients = [], []

    fwd = model.base_model.layer4[-1].register_forward_hook(
        lambda m, i, o: activations.append(o)
    )
    bwd = model.base_model.layer4[-1].register_full_backward_hook(
        lambda m, gi, go: gradients.append(go[0])
    )
    try:
        img_t = tensor.clone().requires_grad_(True)
        with torch.enable_grad():
            out = model(img_t)
            model.zero_grad()
            one_hot = torch.zeros_like(out)
            one_hot[0][target_idx] = 1.0
            out.backward(gradient=one_hot)
    finally:
        fwd.remove()
        bwd.remove()

    if not activations or not gradients:
        return None

    acts  = activations[0].squeeze(0)
    grads = gradients[0].squeeze(0)
    w     = grads.mean(dim=(1, 2))
    cam   = (w[:, None, None] * acts).sum(dim=0)
    cam   = F.relu(cam)
    mn, mx = cam.min(), cam.max()
    if (mx - mn).item() < 1e-8:
        return None
    cam = ((cam - mn) / (mx - mn)).detach().cpu().numpy()
    return cam


def gradcam_images(pil_img: Image.Image, cam: np.ndarray, alpha: float = 0.45):
    img224 = np.array(pil_img.resize((224, 224)))
    cam224 = cv2.resize(cam, (224, 224))

    # heatmap (jet colormap → RGB)
    heatmap_rgb = (cm_module.jet(cam224)[:, :, :3] * 255).astype(np.uint8)
    # overlay
    overlay = (alpha * heatmap_rgb + (1 - alpha) * img224).astype(np.uint8)
    return heatmap_rgb, overlay


# ── FastAPI lifespan ──────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global predictor
    log.info("Chargement du modèle…")
    try:
        predictor = load_model()
        log.info("Modèle prêt.")
    except Exception as exc:
        log.error(f"Erreur chargement modèle : {exc}")
        predictor = None
    yield
    log.info("Arrêt de l'API.")


app = FastAPI(
    title="BrainScan AI API",
    version="2.0.0",
    description="Détection de tumeurs cérébrales par IRM — ResNet50",
    lifespan=lifespan,
)

# ── CORS (configurable via .env) ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-API-Key"],
)
log.info(f"CORS origins: {settings.CORS_ORIGINS}")

# ── Rate limiter ──────────────────────────────────────────────────────────────
if _LIMITER is not None:
    app.state.limiter = _LIMITER
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"detail": f"Rate limit dépassé : {settings.RATE_LIMIT} req/min."},
        )


# ── Optional API key auth ────────────────────────────────────────────────────
async def require_api_key(x_api_key: Optional[str] = Header(None)):
    """Dependency: enforce X-API-Key header if BRAINSCAN_API_KEY is set."""
    if not settings.API_KEY:
        return  # auth disabled
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Clé API invalide ou manquante (X-API-Key)")


if settings.API_KEY:
    log.info("Auth par API key activée (header X-API-Key requis)")


# ── /health ───────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {
        "status":   "ok" if predictor is not None else "model_not_loaded",
        "model":    "ResNet50",
        "accuracy": "98.96%",
        "classes":  CLASS_NAMES,
        "version":  "2.0.0",
        "device":   str(predictor._device) if predictor else "N/A",
    }


# ── /predict ──────────────────────────────────────────────────────────────────
@app.post("/predict", dependencies=[Depends(require_api_key)])
async def predict(file: UploadFile = File(...)):
    if predictor is None:
        raise HTTPException(503, "Modèle non chargé")

    # Validate MIME
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(400, "Format invalide — JPEG ou PNG uniquement")

    raw = await file.read()
    if len(raw) > MAX_FILE_SIZE:
        raise HTTPException(413, "Fichier trop grand (max 10 Mo)")

    # MD5 cache
    md5 = hashlib.md5(raw).hexdigest()
    if md5 in prediction_cache:
        result = dict(prediction_cache[md5])
        result["from_cache"] = True
        return JSONResponse(result)

    try:
        pil_img = load_pil_from_bytes(raw)
    except Exception:
        raise HTTPException(400, "Image corrompue ou illisible")

    t0 = time.perf_counter()
    idx, confidence, probs, tensor = run_predict(predictor, pil_img)
    inference_ms = (time.perf_counter() - t0) * 1000

    # Grad-CAM
    gradcam_heatmap = None
    gradcam_overlay = None
    try:
        cam = compute_gradcam(predictor, tensor, idx)
        if cam is not None:
            heatmap_arr, overlay_arr = gradcam_images(pil_img, cam)
            gradcam_heatmap = ndarray_to_base64_png(heatmap_arr)
            gradcam_overlay = ndarray_to_base64_png(overlay_arr)
    except Exception as e:
        log.warning(f"Grad-CAM erreur : {e}")

    class_key = CLASS_KEYS[idx]
    probabilities = {CLASS_NAMES[i]: round(float(probs[i]), 6) for i in range(4)}

    result = {
        "predicted_class":   CLASS_NAMES[idx],
        "predicted_key":     class_key,
        "confidence":        round(confidence, 6),
        "probabilities":     probabilities,
        "original_image":    pil_to_base64(pil_img.resize((400, 400))),
        "gradcam_heatmap":   gradcam_heatmap,
        "gradcam_overlay":   gradcam_overlay,
        "inference_time_ms": round(inference_ms, 2),
        "from_cache":        False,
    }

    # Store cache (LRU-like eviction)
    if len(prediction_cache) >= MAX_CACHE:
        oldest = next(iter(prediction_cache))
        del prediction_cache[oldest]
    prediction_cache[md5] = result

    # Update session stats
    session_stats["total"] += 1
    session_stats["class_counts"][class_key] += 1
    session_stats["total_conf"]    += confidence
    session_stats["total_time_ms"] += inference_ms

    return JSONResponse(result)


# ── /random ───────────────────────────────────────────────────────────────────
@app.get("/random")
async def random_example():
    if predictor is None:
        raise HTTPException(503, "Modèle non chargé")

    cls_key  = random.choice(CLASS_KEYS)
    cls_dir  = DATA_FOLDERS[cls_key]
    npy_files = list(cls_dir.glob("*.npy"))
    if not npy_files:
        raise HTTPException(404, f"Aucun fichier dans {cls_dir}")

    npy_path = random.choice(npy_files)
    pil_img  = load_pil_from_npy(npy_path)

    t0 = time.perf_counter()
    idx, confidence, probs, tensor = run_predict(predictor, pil_img)
    inference_ms = (time.perf_counter() - t0) * 1000

    gradcam_heatmap = None
    gradcam_overlay = None
    try:
        cam = compute_gradcam(predictor, tensor, idx)
        if cam is not None:
            heatmap_arr, overlay_arr = gradcam_images(pil_img, cam)
            gradcam_heatmap = ndarray_to_base64_png(heatmap_arr)
            gradcam_overlay = ndarray_to_base64_png(overlay_arr)
    except Exception as e:
        log.warning(f"Grad-CAM /random erreur : {e}")

    class_key = CLASS_KEYS[idx]
    probabilities = {CLASS_NAMES[i]: round(float(probs[i]), 6) for i in range(4)}

    result = {
        "predicted_class":   CLASS_NAMES[idx],
        "predicted_key":     class_key,
        "confidence":        round(confidence, 6),
        "probabilities":     probabilities,
        "original_image":    pil_to_base64(pil_img.resize((400, 400))),
        "gradcam_heatmap":   gradcam_heatmap,
        "gradcam_overlay":   gradcam_overlay,
        "inference_time_ms": round(inference_ms, 2),
        "from_cache":        False,
        "true_class":        CLASS_NAMES[CLASS_KEYS.index(cls_key)],
        "true_key":          cls_key,
        "source_file":       npy_path.name,
    }

    session_stats["total"] += 1
    session_stats["class_counts"][class_key] += 1
    session_stats["total_conf"]    += confidence
    session_stats["total_time_ms"] += inference_ms

    return JSONResponse(result)


# ── /explain/{class_name} ────────────────────────────────────────────────────
@app.get("/explain/{class_name}")
async def explain(class_name: str):
    key = class_name.lower().replace(" ", "_").replace("-", "_")
    if key not in MEDICAL_INFO:
        raise HTTPException(404, f"Classe inconnue : {class_name}. Valides : {CLASS_KEYS}")
    return JSONResponse(MEDICAL_INFO[key])


# ── /sample/{class_name} ────────────────────────────────────────────────────
@app.get("/sample/{class_name}")
async def sample(class_name: str):
    key = class_name.lower().replace(" ", "_").replace("-", "_")
    if key not in DATA_FOLDERS:
        raise HTTPException(404, f"Classe inconnue : {class_name}")

    cls_dir   = DATA_FOLDERS[key]
    npy_files = list(cls_dir.glob("*.npy"))
    if not npy_files:
        raise HTTPException(404, "Aucun fichier disponible")

    npy_path = random.choice(npy_files)
    pil_img  = load_pil_from_npy(npy_path)

    return JSONResponse({
        "class":        CLASS_NAMES[CLASS_KEYS.index(key)],
        "image_base64": pil_to_base64(pil_img.resize((400, 400))),
        "filename":     npy_path.name,
    })


# ── /batch ────────────────────────────────────────────────────────────────────
@app.post("/batch", dependencies=[Depends(require_api_key)])
async def batch_predict(files: List[UploadFile] = File(...)):
    if predictor is None:
        raise HTTPException(503, "Modèle non chargé")
    if len(files) > 20:
        raise HTTPException(413, "Maximum 20 fichiers par lot")

    results = []
    for f in files:
        if f.content_type not in ("image/jpeg", "image/png", "image/jpg"):
            results.append({"filename": f.filename, "error": "Format invalide"})
            continue
        raw = await f.read()
        if len(raw) > MAX_FILE_SIZE:
            results.append({"filename": f.filename, "error": "Fichier trop grand"})
            continue
        try:
            pil_img = load_pil_from_bytes(raw)
            t0 = time.perf_counter()
            idx, conf, probs, _ = run_predict(predictor, pil_img)
            ms = (time.perf_counter() - t0) * 1000
            results.append({
                "filename":          f.filename,
                "predicted_class":   CLASS_NAMES[idx],
                "confidence":        round(conf, 6),
                "probabilities":     {CLASS_NAMES[i]: round(float(probs[i]), 6) for i in range(4)},
                "inference_time_ms": round(ms, 2),
            })
        except Exception as exc:
            results.append({"filename": f.filename, "error": str(exc)})

    return JSONResponse({"count": len(results), "results": results})


# ── /stats ────────────────────────────────────────────────────────────────────
@app.get("/stats")
async def stats():
    total = session_stats["total"]
    dominant = max(session_stats["class_counts"], key=lambda k: session_stats["class_counts"][k])
    return JSONResponse({
        "total_predictions": total,
        "class_distribution": session_stats["class_counts"],
        "avg_confidence":    round(session_stats["total_conf"] / total, 4) if total else 0.0,
        "avg_inference_ms":  round(session_stats["total_time_ms"] / total, 2) if total else 0.0,
        "most_frequent_class": CLASS_NAMES[CLASS_KEYS.index(dominant)] if total else "N/A",
    })
