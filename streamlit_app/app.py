"""
Brain Tumor Detection Web Application — NeuroScan AI
Premium UI with Grad-CAM, session history, and downloadable reports.
"""

import os
import sys
import io
import base64
from datetime import datetime
from contextlib import contextmanager

# CRITICAL: Patch pathlib before any imports that might use it
import pathlib
if not hasattr(pathlib, '_local'):
    pathlib._local = pathlib.Path
sys.modules['pathlib._local'] = pathlib

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms

import streamlit as st
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import cv2

_HERE = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(_HERE)  # project root (one level up)
sys.path.append(os.path.join(BASE_DIR, 'src'))

MODEL_PATH = os.path.join(BASE_DIR, 'models', 'final_model_20251106_142153.pth')

from model_architecture import ResNet50Classifier

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NeuroScan AI — Brain Tumor Detection",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Constants ────────────────────────────────────────────────────────────────
CLASS_NAMES = ['Glioma', 'Meningioma', 'No Tumor', 'Pituitary']

CLASS_COLORS = {
    'Glioma':      '#FF4757',
    'Meningioma':  '#FFA502',
    'No Tumor':    '#2ED573',
    'Pituitary':   '#A29BFE',
}
CLASS_ICONS = {
    'Glioma':      '🔴',
    'Meningioma':  '🟠',
    'No Tumor':    '🟢',
    'Pituitary':   '🟣',
}
CLASS_EMOJI = {
    'Glioma':      '⚡',
    'Meningioma':  '🔶',
    'No Tumor':    '✅',
    'Pituitary':   '💜',
}

TUMOR_INFO = {
    'Glioma': {
        'description': (
            'Glioma is a tumor originating from glial cells in the brain or spine. '
            'It can be high-grade (aggressive) or low-grade (slow-growing) and accounts '
            'for about 30% of all brain tumors.'
        ),
        'severity': 'High',
        'prevalence': '~30% of brain tumors',
        'treatment': 'Surgery, radiotherapy, chemotherapy',
        'recommendation': 'Immediate neurological consultation required. This is a serious condition needing urgent expert evaluation.',
        'symptoms': ['Persistent headaches', 'Seizures', 'Memory loss', 'Personality changes', 'Nausea'],
        'color': '#FF4757',
    },
    'Meningioma': {
        'description': (
            'Meningioma is a tumor forming on the meninges — membranes covering the brain and '
            'spinal cord. Usually benign and slow-growing, it is the most common primary brain tumor.'
        ),
        'severity': 'Moderate to High',
        'prevalence': '~37% of brain tumors',
        'treatment': 'Observation, surgery, stereotactic radiosurgery',
        'recommendation': 'Medical consultation recommended. While often benign, professional evaluation is essential.',
        'symptoms': ['Headaches', 'Vision problems', 'Weakness', 'Numbness', 'Speech difficulties'],
        'color': '#FFA502',
    },
    'No Tumor': {
        'description': (
            'No tumor was detected in this MRI scan. '
            'Brain structures appear within normal imaging parameters.'
        ),
        'severity': 'None',
        'prevalence': 'N/A',
        'treatment': 'N/A',
        'recommendation': 'No tumor detected. Consult a doctor if you have ongoing symptoms.',
        'symptoms': [],
        'color': '#2ED573',
    },
    'Pituitary': {
        'description': (
            'Pituitary tumor develops in the pituitary gland at the base of the brain. '
            'It can affect hormone production and vision, but is usually benign (adenoma).'
        ),
        'severity': 'Moderate',
        'prevalence': '~15% of brain tumors',
        'treatment': 'Medication, surgery (transsphenoidal), radiotherapy',
        'recommendation': 'Endocrinology consultation recommended. Hormone level testing is advised.',
        'symptoms': ['Hormone imbalances', 'Vision changes', 'Headaches', 'Fatigue', 'Unexplained weight change'],
        'color': '#A29BFE',
    }
}

MODEL_STATS = {
    'Glioma':     99.2,
    'Meningioma': 98.4,
    'No Tumor':   99.6,
    'Pituitary':  98.8,
}

# ─── CSS ──────────────────────────────────────────────────────────────────────
PREMIUM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Globals ── */
html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif; }
#MainMenu, footer, header { visibility: hidden; }

.stApp {
    background: radial-gradient(ellipse at 0% 0%, #0f1a3a 0%, #0a0e1a 40%, #150a2e 100%);
    min-height: 100vh;
}

/* ── Hero header ── */
.neuro-hero {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
}
.neuro-title {
    font-size: clamp(2.2rem, 5vw, 3.6rem);
    font-weight: 900;
    background: linear-gradient(135deg, #00d4ff 0%, #7b2fff 50%, #ff2d55 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -2px;
    line-height: 1.1;
    margin-bottom: 0.6rem;
}
.neuro-subtitle {
    color: rgba(255,255,255,0.45);
    font-size: 1.05rem;
    font-weight: 400;
    letter-spacing: 0.5px;
}
.neuro-badge {
    display: inline-block;
    margin-top: 0.8rem;
    padding: 0.35rem 1.2rem;
    border-radius: 50px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(123,47,255,0.15));
    border: 1px solid rgba(123,47,255,0.35);
    color: rgba(255,255,255,0.7);
}

/* ── Glass card ── */
.glass {
    background: rgba(255,255,255,0.035);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 1.6rem;
    margin: 0.8rem 0;
    transition: border-color 0.3s ease, background 0.3s ease;
}
.glass:hover {
    border-color: rgba(123,47,255,0.25);
    background: rgba(255,255,255,0.05);
}

/* ── Result cards ── */
.result-card {
    border-radius: 20px;
    padding: 2rem 2rem 1.5rem;
    margin: 1rem 0;
    position: relative;
    overflow: hidden;
}
.result-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 20px 20px 0 0;
}
.card-tumor {
    background: linear-gradient(135deg, rgba(255,71,87,0.08), rgba(255,71,87,0.03));
    border: 1px solid rgba(255,71,87,0.25);
}
.card-tumor::before { background: linear-gradient(90deg, #ff4757, #ff6b81); }

.card-meningioma {
    background: linear-gradient(135deg, rgba(255,165,2,0.08), rgba(255,165,2,0.03));
    border: 1px solid rgba(255,165,2,0.25);
}
.card-meningioma::before { background: linear-gradient(90deg, #ffa502, #ffcc02); }

.card-clean {
    background: linear-gradient(135deg, rgba(46,213,115,0.08), rgba(46,213,115,0.03));
    border: 1px solid rgba(46,213,115,0.25);
}
.card-clean::before { background: linear-gradient(90deg, #2ed573, #7bed9f); }

.card-pituitary {
    background: linear-gradient(135deg, rgba(162,155,254,0.08), rgba(162,155,254,0.03));
    border: 1px solid rgba(162,155,254,0.25);
}
.card-pituitary::before { background: linear-gradient(90deg, #a29bfe, #d0c8ff); }

/* ── Section titles ── */
.section-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: rgba(255,255,255,0.9);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Sidebar overrides ── */
[data-testid="stSidebar"] {
    background: rgba(10,14,26,0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] .block-container { padding: 1rem; }

/* ── File uploader ── */
[data-testid="stFileUploader"] > div:first-child {
    background: rgba(123,47,255,0.04) !important;
    border: 2px dashed rgba(123,47,255,0.35) !important;
    border-radius: 16px !important;
    transition: all 0.3s ease !important;
}
[data-testid="stFileUploader"] > div:first-child:hover {
    border-color: rgba(123,47,255,0.6) !important;
    background: rgba(123,47,255,0.08) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: rgba(255,255,255,0.5) !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(123,47,255,0.35) !important;
    color: white !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important;
    padding: 1rem 1.2rem !important;
}

/* ── Progress bars ── */
.stProgress > div > div { background: linear-gradient(90deg, #7b2fff, #00d4ff) !important; border-radius: 50px !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #7b2fff !important; }

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* ── Alerts ── */
.stSuccess { background: rgba(46,213,115,0.1) !important; border: 1px solid rgba(46,213,115,0.25) !important; color: #2ed573 !important; border-radius: 12px !important; }
.stError   { background: rgba(255,71,87,0.1)  !important; border: 1px solid rgba(255,71,87,0.25)  !important; border-radius: 12px !important; }
.stInfo    { background: rgba(0,212,255,0.07)  !important; border: 1px solid rgba(0,212,255,0.2)   !important; border-radius: 12px !important; }
.stWarning { background: rgba(255,165,2,0.08)  !important; border: 1px solid rgba(255,165,2,0.25)  !important; border-radius: 12px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.03); }
::-webkit-scrollbar-thumb { background: rgba(123,47,255,0.4); border-radius: 3px; }
</style>
"""

# ─── Model loading ─────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        return None

    try:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = ResNet50Classifier(num_classes=4, pretrained=False)

        @contextmanager
        def _portable_pathlib_patch():
            original_windows = pathlib.WindowsPath
            original_posix = pathlib.PosixPath
            try:
                pathlib.WindowsPath = pathlib.PureWindowsPath
                pathlib.PosixPath = pathlib.PurePosixPath
                yield
            finally:
                pathlib.WindowsPath = original_windows
                pathlib.PosixPath = original_posix

        def _portable_torch_load(weights_only_flag):
            with _portable_pathlib_patch():
                try:
                    return torch.load(MODEL_PATH, map_location=device,
                                      weights_only=weights_only_flag, mmap=True)
                except TypeError:
                    try:
                        return torch.load(MODEL_PATH, map_location=device,
                                          weights_only=weights_only_flag)
                    except TypeError:
                        return torch.load(MODEL_PATH, map_location=device)

        try:
            checkpoint = _portable_torch_load(weights_only_flag=True)
        except Exception:
            checkpoint = _portable_torch_load(weights_only_flag=False)

        state_dict = checkpoint['model_state_dict'] if (
            isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint
        ) else checkpoint

        model.load_state_dict(state_dict)
        model.to(device)
        model.eval()
        return model, device

    except Exception as e:
        st.error(f"❌ Erreur chargement modèle : {e}")
        return None


# ─── Preprocessing ─────────────────────────────────────────────────────────────
def preprocess_image(image: Image.Image) -> torch.Tensor:
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])
    if image.mode != 'RGB':
        image = image.convert('RGB')
    return transform(image).unsqueeze(0)


# ─── Prediction ────────────────────────────────────────────────────────────────
def predict(model, device, image_tensor):
    with torch.no_grad():
        image_tensor = image_tensor.to(device)
        outputs = model(image_tensor)
        probs = F.softmax(outputs, dim=1)
        conf, idx = torch.max(probs, 1)
    return idx.item(), conf.item(), probs[0].cpu().numpy()


# ─── PyTorch Grad-CAM ──────────────────────────────────────────────────────────
def generate_gradcam(model, device, image_tensor, target_class):
    """Grad-CAM via hooks on ResNet50's layer4 — pure PyTorch, no TF needed."""
    model.eval()
    activations, gradients = [], []

    fwd = model.base_model.layer4[-1].register_forward_hook(
        lambda m, i, o: activations.append(o)
    )
    bwd = model.base_model.layer4[-1].register_full_backward_hook(
        lambda m, gi, go: gradients.append(go[0])
    )

    img = image_tensor.clone().to(device).requires_grad_(True)
    with torch.enable_grad():
        out = model(img)
        model.zero_grad()
        one_hot = torch.zeros_like(out)
        one_hot[0][target_class] = 1.0
        out.backward(gradient=one_hot)

    fwd.remove()
    bwd.remove()

    if not activations or not gradients:
        return None

    acts  = activations[0].squeeze(0)   # [C, H, W]
    grads = gradients[0].squeeze(0)     # [C, H, W]
    weights = grads.mean(dim=(1, 2))    # [C]
    cam = (weights[:, None, None] * acts).sum(dim=0)
    cam = F.relu(cam)
    cam_min, cam_max = cam.min(), cam.max()
    if cam_max - cam_min < 1e-8:
        return None
    cam = (cam - cam_min) / (cam_max - cam_min)
    return cam.detach().cpu().numpy()


def apply_gradcam_overlay(pil_image: Image.Image, cam: np.ndarray, alpha: float = 0.45):
    img_rgb = np.array(pil_image.resize((224, 224)).convert('RGB'))
    cam_resized = cv2.resize(cam, (224, 224))
    heatmap = cm.jet(cam_resized)[:, :, :3]
    heatmap = (heatmap * 255).astype(np.uint8)
    overlay = (alpha * heatmap + (1 - alpha) * img_rgb).astype(np.uint8)
    return overlay, cam_resized


# ─── HTML helpers ──────────────────────────────────────────────────────────────
def confidence_gauge_svg(pct: float, color: str) -> str:
    r = 52
    circ = 2 * 3.14159 * r
    offset = circ * (1 - pct / 100)
    return f"""
    <div style="text-align:center; padding:0.5rem 0;">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>
        <circle cx="70" cy="70" r="{r}"
                fill="none" stroke="rgba(255,255,255,0.07)" stroke-width="11"/>
        <circle cx="70" cy="70" r="{r}"
                fill="none" stroke="{color}" stroke-width="11"
                stroke-dasharray="{circ:.1f}" stroke-dashoffset="{offset:.1f}"
                stroke-linecap="round"
                transform="rotate(-90 70 70)"
                filter="url(#glow)"/>
        <text x="70" y="63" text-anchor="middle"
              fill="white" font-size="21" font-weight="800"
              font-family="Inter, sans-serif">{pct:.1f}%</text>
        <text x="70" y="82" text-anchor="middle"
              fill="rgba(255,255,255,0.45)" font-size="10"
              font-family="Inter, sans-serif">confiance</text>
      </svg>
    </div>"""


def prob_bars_html(all_probs: np.ndarray, predicted_class: int) -> str:
    html = '<div style="margin-top:0.5rem;">'
    for i, (name, prob) in enumerate(zip(CLASS_NAMES, all_probs)):
        pct = prob * 100
        color = CLASS_COLORS[name]
        icon  = CLASS_ICONS[name]
        is_pred = i == predicted_class
        weight = "700" if is_pred else "400"
        name_color = "white" if is_pred else "rgba(255,255,255,0.6)"
        glow = f"box-shadow: 0 0 8px {color}55;" if is_pred else ""
        html += f"""
        <div style="margin:0.75rem 0;">
          <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
            <span style="font-weight:{weight}; color:{name_color}; font-size:0.9rem;">
              {icon} {name}{"  ✓" if is_pred else ""}
            </span>
            <span style="font-weight:{weight}; color:{color}; font-size:0.9rem;">{pct:.2f}%</span>
          </div>
          <div style="background:rgba(255,255,255,0.07); border-radius:50px; height:9px; overflow:hidden;">
            <div style="width:{pct:.2f}%; height:100%; border-radius:50px;
                        background:linear-gradient(90deg, {color}88, {color}); {glow}"></div>
          </div>
        </div>"""
    html += '</div>'
    return html


def severity_badge(severity: str) -> str:
    mapping = {
        'High':             ('badge-high',     '#FF4757', 'rgba(255,71,87,0.15)'),
        'Moderate to High': ('badge-mod-high', '#FFA502', 'rgba(255,165,2,0.15)'),
        'Moderate':         ('badge-mod',      '#FFA502', 'rgba(255,165,2,0.15)'),
        'None':             ('badge-none',     '#2ED573', 'rgba(46,213,115,0.15)'),
    }
    _, text_color, bg_color = mapping.get(severity, ('', '#aaa', 'rgba(170,170,170,0.15)'))
    return (
        f'<span style="display:inline-block; padding:0.25rem 0.9rem; border-radius:50px; '
        f'font-size:0.78rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; '
        f'color:{text_color}; background:{bg_color}; border:1px solid {text_color}44;">'
        f'{severity}</span>'
    )


def card_class(tumor_type: str) -> str:
    return {
        'Glioma':     'card-tumor',
        'Meningioma': 'card-meningioma',
        'No Tumor':   'card-clean',
        'Pituitary':  'card-pituitary',
    }.get(tumor_type, 'card-clean')


def generate_text_report(filename, tumor_type, confidence_pct, all_probs) -> str:
    info = TUMOR_INFO[tumor_type]
    lines = [
        "=" * 58,
        "       NEUROSCAN AI — BRAIN TUMOR DETECTION REPORT",
        "=" * 58,
        f"  Date       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"  File       : {filename}",
        f"  Model      : ResNet50 (Transfer Learning — ImageNet)",
        f"  Test Acc.  : 98.96% on 1,054 test images",
        "",
        "─" * 58,
        "  DIAGNOSIS",
        "─" * 58,
        f"  Classification : {tumor_type}",
        f"  Confidence     : {confidence_pct:.2f}%",
        f"  Severity       : {info['severity']}",
        f"  Prevalence     : {info['prevalence']}",
        "",
        "─" * 58,
        "  DESCRIPTION",
        "─" * 58,
        f"  {info['description']}",
        "",
        "─" * 58,
        "  PROBABILITY BREAKDOWN",
        "─" * 58,
    ]
    for name, prob in zip(CLASS_NAMES, all_probs):
        marker = " ◀ predicted" if name == tumor_type else ""
        bar = "█" * int(prob * 30)
        lines.append(f"  {name:<12} {prob*100:6.2f}%  {bar}{marker}")
    lines += [
        "",
        "─" * 58,
        "  TREATMENT OPTIONS",
        "─" * 58,
        f"  {info['treatment']}",
        "",
        "─" * 58,
        "  RECOMMENDATION",
        "─" * 58,
        f"  {info['recommendation']}",
        "",
        "─" * 58,
        "  DISCLAIMER",
        "─" * 58,
        "  This report is generated by an AI model for",
        "  EDUCATIONAL PURPOSES ONLY.",
        "  It must NOT replace professional medical diagnosis.",
        "  Always consult qualified healthcare professionals.",
        "=" * 58,
    ]
    return "\n".join(lines)


# ─── Sidebar ──────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding:1rem 0 0.5rem;">
          <div style="font-size:2.4rem;">🧠</div>
          <div style="font-size:1.1rem; font-weight:800; color:white; letter-spacing:-0.5px;">NeuroScan AI</div>
          <div style="font-size:0.75rem; color:rgba(255,255,255,0.4); margin-top:2px;">v2.0 · ResNet50</div>
        </div>
        <hr style="border-color:rgba(255,255,255,0.07); margin:0.8rem 0;">
        """, unsafe_allow_html=True)

        # ── Model status
        model_ok = os.path.exists(MODEL_PATH)
        if model_ok:
            st.markdown("""
            <div style="display:flex; align-items:center; gap:0.5rem; padding:0.6rem 0.8rem;
                        background:rgba(46,213,115,0.1); border:1px solid rgba(46,213,115,0.25);
                        border-radius:10px; margin-bottom:0.8rem;">
              <span style="font-size:1rem;">✅</span>
              <span style="color:#2ed573; font-size:0.85rem; font-weight:600;">Modèle chargé · 98.5 MB</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.error("❌ Modèle introuvable dans /models")

        # ── Device
        device_name = "GPU (CUDA)" if torch.cuda.is_available() else "CPU"
        device_icon = "⚡" if torch.cuda.is_available() else "💻"
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:0.5rem; padding:0.6rem 0.8rem;
                    background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);
                    border-radius:10px; margin-bottom:1rem;">
          <span>{device_icon}</span>
          <span style="color:rgba(255,255,255,0.7); font-size:0.85rem;">Inférence : <b>{device_name}</b></span>
        </div>""", unsafe_allow_html=True)

        # ── Performance
        st.markdown('<div class="section-title">📊 Performance du modèle</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07);
                    border-radius:14px; padding:1rem 1.1rem; margin-bottom:1rem;">
          <div style="display:flex; justify-content:space-between; padding:0.35rem 0;
                      border-bottom:1px solid rgba(255,255,255,0.06);">
            <span style="color:rgba(255,255,255,0.55); font-size:0.82rem;">Accuracy globale</span>
            <span style="color:#00d4ff; font-weight:700; font-size:0.9rem;">98.96%</span>
          </div>
          <div style="display:flex; justify-content:space-between; padding:0.35rem 0;
                      border-bottom:1px solid rgba(255,255,255,0.06);">
            <span style="color:rgba(255,255,255,0.55); font-size:0.82rem;">🔴 Glioma</span>
            <span style="color:#ff4757; font-weight:600; font-size:0.85rem;">99.2%</span>
          </div>
          <div style="display:flex; justify-content:space-between; padding:0.35rem 0;
                      border-bottom:1px solid rgba(255,255,255,0.06);">
            <span style="color:rgba(255,255,255,0.55); font-size:0.82rem;">🟠 Meningioma</span>
            <span style="color:#ffa502; font-weight:600; font-size:0.85rem;">98.4%</span>
          </div>
          <div style="display:flex; justify-content:space-between; padding:0.35rem 0;
                      border-bottom:1px solid rgba(255,255,255,0.06);">
            <span style="color:rgba(255,255,255,0.55); font-size:0.82rem;">🟢 No Tumor</span>
            <span style="color:#2ed573; font-weight:600; font-size:0.85rem;">99.6%</span>
          </div>
          <div style="display:flex; justify-content:space-between; padding:0.35rem 0;">
            <span style="color:rgba(255,255,255,0.55); font-size:0.82rem;">🟣 Pituitary</span>
            <span style="color:#a29bfe; font-weight:600; font-size:0.85rem;">98.8%</span>
          </div>
        </div>""", unsafe_allow_html=True)

        # ── Tumor guide
        st.markdown('<div class="section-title">🔬 Guide des tumeurs</div>', unsafe_allow_html=True)
        for name, info in TUMOR_INFO.items():
            with st.expander(f"{CLASS_ICONS[name]} {name}"):
                st.markdown(f"""
                <div style="font-size:0.83rem; color:rgba(255,255,255,0.7); line-height:1.6;">
                  <b style="color:{info['color']};">Sévérité :</b> {info['severity']}<br>
                  <b style="color:{info['color']};">Prévalence :</b> {info['prevalence']}<br>
                  <b style="color:{info['color']};">Traitement :</b> {info['treatment']}<br><br>
                  {info['description']}
                </div>""", unsafe_allow_html=True)

        # ── Disclaimer
        st.markdown('<hr style="border-color:rgba(255,255,255,0.07); margin:1rem 0;">', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(255,165,2,0.07); border:1px solid rgba(255,165,2,0.2);
                    border-radius:12px; padding:0.9rem; font-size:0.78rem;
                    color:rgba(255,255,255,0.55); line-height:1.6;">
          ⚠️ <b style="color:#ffa502;">Usage éducatif uniquement.</b><br>
          Cet outil ne remplace pas le diagnostic médical professionnel.
          Consultez toujours un professionnel de santé qualifié.
        </div>""", unsafe_allow_html=True)


# ─── Upload zone ───────────────────────────────────────────────────────────────
def render_upload_zone():
    st.markdown('<div class="section-title">📤 Importer une IRM cérébrale</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color:rgba(255,255,255,0.45); font-size:0.9rem; margin-top:-0.5rem; margin-bottom:0.8rem;">'
        'Glissez-déposez ou cliquez pour sélectionner une IRM — PNG, JPG, JPEG ou NPY</p>',
        unsafe_allow_html=True
    )
    return st.file_uploader(
        "Choisir une image IRM…",
        type=['png', 'jpg', 'jpeg', 'npy'],
        help="IRM cérébrale au format PNG, JPG, JPEG ou NPY",
        label_visibility="collapsed",
    )


# ─── No-image placeholder ──────────────────────────────────────────────────────
def render_placeholder():
    st.markdown("""
    <div style="text-align:center; padding:3rem 2rem;
                background:rgba(255,255,255,0.02); border:1px dashed rgba(255,255,255,0.1);
                border-radius:20px; margin:1rem 0;">
      <div style="font-size:4rem; margin-bottom:1rem;">🧠</div>
      <div style="font-size:1.15rem; font-weight:600; color:rgba(255,255,255,0.7); margin-bottom:0.5rem;">
        Aucune image importée
      </div>
      <div style="font-size:0.88rem; color:rgba(255,255,255,0.35); line-height:1.7;">
        Importez une IRM cérébrale pour démarrer l'analyse.<br>
        L'IA classifiera la tumeur en moins d'une seconde.
      </div>
    </div>

    <div style="margin-top:1.5rem;">
      <div class="section-title">💡 Comment utiliser</div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.8rem;">
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07);
                    border-radius:14px; padding:1rem;">
          <div style="font-size:1.4rem; margin-bottom:0.4rem;">1️⃣</div>
          <div style="font-size:0.85rem; color:rgba(255,255,255,0.7);">
            Importez une IRM cérébrale au format PNG, JPG ou NPY
          </div>
        </div>
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07);
                    border-radius:14px; padding:1rem;">
          <div style="font-size:1.4rem; margin-bottom:0.4rem;">2️⃣</div>
          <div style="font-size:0.85rem; color:rgba(255,255,255,0.7);">
            L'IA analyse l'image et identifie la classe de tumeur
          </div>
        </div>
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07);
                    border-radius:14px; padding:1rem;">
          <div style="font-size:1.4rem; margin-bottom:0.4rem;">3️⃣</div>
          <div style="font-size:0.85rem; color:rgba(255,255,255,0.7);">
            Visualisez la Grad-CAM : les zones qui ont influencé la décision
          </div>
        </div>
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07);
                    border-radius:14px; padding:1rem;">
          <div style="font-size:1.4rem; margin-bottom:0.4rem;">4️⃣</div>
          <div style="font-size:0.85rem; color:rgba(255,255,255,0.7);">
            Téléchargez le rapport et consultez un professionnel de santé
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Session history ───────────────────────────────────────────────────────────
def render_history():
    history = st.session_state.get('history', [])
    if not history:
        return
    st.markdown('<div class="section-title" style="margin-top:1.5rem;">🕒 Historique de session</div>', unsafe_allow_html=True)
    header = """
    <div style="display:grid; grid-template-columns:2fr 2fr 1.5fr 1.5fr;
                gap:0.5rem; padding:0.4rem 0.8rem;
                color:rgba(255,255,255,0.4); font-size:0.78rem; font-weight:600;
                text-transform:uppercase; letter-spacing:1px;
                border-bottom:1px solid rgba(255,255,255,0.07);">
      <span>Fichier</span><span>Résultat</span><span>Confiance</span><span>Heure</span>
    </div>"""
    rows = ""
    for h in history:
        rows += f"""
        <div style="display:grid; grid-template-columns:2fr 2fr 1.5fr 1.5fr;
                    gap:0.5rem; padding:0.5rem 0.8rem; align-items:center;
                    border-bottom:1px solid rgba(255,255,255,0.04); font-size:0.83rem;">
          <span style="color:rgba(255,255,255,0.65); overflow:hidden; text-overflow:ellipsis; white-space:nowrap;"
                title="{h['file']}">{h['file'][:18]}{'…' if len(h['file'])>18 else ''}</span>
          <span style="color:{h['color']}; font-weight:600;">{CLASS_ICONS[h['prediction']]} {h['prediction']}</span>
          <span style="color:rgba(255,255,255,0.7);">{h['confidence']:.1f}%</span>
          <span style="color:rgba(255,255,255,0.4);">{h['time']}</span>
        </div>"""
    st.markdown(
        f'<div style="background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.07); '
        f'border-radius:14px; overflow:hidden; margin-top:0.5rem;">{header}{rows}</div>',
        unsafe_allow_html=True
    )


# ─── Main analysis view ────────────────────────────────────────────────────────
def render_analysis(uploaded_file):
    # ── Load image
    if uploaded_file.name.endswith('.npy'):
        arr = np.load(uploaded_file)
        if arr.max() <= 1.0:
            arr = (arr * 255).astype('uint8')
        else:
            arr = arr.astype('uint8')
        if len(arr.shape) == 2:
            arr = np.stack([arr] * 3, axis=-1)
        image = Image.fromarray(arr)
    else:
        image = Image.open(uploaded_file)

    # ── Load model & predict
    model_loaded = load_model()
    if model_loaded is None:
        st.error("❌ Impossible de charger le modèle.")
        return
    model, device = model_loaded

    image_tensor = preprocess_image(image)

    with st.spinner('🔄 Analyse en cours…'):
        predicted_idx, confidence, all_probs = predict(model, device, image_tensor)
        # Grad-CAM (may fail gracefully)
        try:
            cam = generate_gradcam(model, device, image_tensor, predicted_idx)
            cam_overlay, cam_raw = apply_gradcam_overlay(image, cam) if cam is not None else (None, None)
        except Exception:
            cam_overlay, cam_raw = None, None

    tumor_type    = CLASS_NAMES[predicted_idx]
    confidence_pct = confidence * 100
    info           = TUMOR_INFO[tumor_type]
    color          = CLASS_COLORS[tumor_type]

    # ── Update session history
    if 'history' not in st.session_state:
        st.session_state.history = []
    st.session_state.history.insert(0, {
        'time':       datetime.now().strftime('%H:%M:%S'),
        'file':       uploaded_file.name,
        'prediction': tumor_type,
        'confidence': confidence_pct,
        'color':      color,
    })
    if len(st.session_state.history) > 8:
        st.session_state.history.pop()

    # ── Image metadata
    width, height = image.size
    file_size_kb  = uploaded_file.size / 1024

    # ────────────────────────────────────────────────────────────────────────
    # TOP ROW: Original | Grad-CAM | Confidence gauge
    # ────────────────────────────────────────────────────────────────────────
    col_img, col_cam, col_gauge = st.columns([1.4, 1.4, 1])

    with col_img:
        st.markdown('<div class="section-title">📷 Image importée</div>', unsafe_allow_html=True)
        st.image(image, use_container_width=True)
        st.markdown(
            f'<div style="font-size:0.78rem; color:rgba(255,255,255,0.35); margin-top:0.3rem;">'
            f'{width}×{height}px · {file_size_kb:.1f} KB · {uploaded_file.name}</div>',
            unsafe_allow_html=True
        )

    with col_cam:
        st.markdown('<div class="section-title">🔥 Grad-CAM (zones d\'attention)</div>', unsafe_allow_html=True)
        if cam_overlay is not None:
            fig, axes = plt.subplots(1, 2, figsize=(7, 3.5),
                                     facecolor='none', constrained_layout=True)
            axes[0].imshow(np.array(image.resize((224, 224)).convert('RGB')))
            axes[0].set_title('Original', color='white', fontsize=9, fontweight='bold')
            axes[0].axis('off')
            axes[1].imshow(cam_overlay)
            axes[1].set_title('Grad-CAM overlay', color='white', fontsize=9, fontweight='bold')
            axes[1].axis('off')
            fig.patch.set_alpha(0.0)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            st.markdown(
                '<div style="font-size:0.78rem; color:rgba(255,255,255,0.35);">'
                '🔴 Rouge = zones décisives · 🔵 Bleu = zones neutres</div>',
                unsafe_allow_html=True
            )
        else:
            st.info("Grad-CAM non disponible pour cette image.")

    with col_gauge:
        st.markdown('<div class="section-title">🎯 Score</div>', unsafe_allow_html=True)
        st.markdown(confidence_gauge_svg(confidence_pct, color), unsafe_allow_html=True)
        # Quick verdict chip
        verdict = "Aucune tumeur détectée" if tumor_type == 'No Tumor' else f"{tumor_type} détecté(e)"
        st.markdown(
            f'<div style="text-align:center; margin-top:0.5rem; padding:0.6rem 0.8rem; '
            f'background:{color}18; border:1px solid {color}44; border-radius:12px; '
            f'font-weight:700; color:{color}; font-size:0.9rem;">'
            f'{CLASS_EMOJI[tumor_type]} {verdict}</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div style="text-align:center; margin-top:0.5rem;">'
            f'{severity_badge(info["severity"])}</div>',
            unsafe_allow_html=True
        )

    st.markdown('<hr>', unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────────────────
    # TABS: Résultats | Détails médicaux | Rapport
    # ────────────────────────────────────────────────────────────────────────
    tab_res, tab_med, tab_report = st.tabs(["📊 Probabilités", "🏥 Informations médicales", "📄 Rapport"])

    with tab_res:
        col_bars, col_metrics = st.columns([1.6, 1])
        with col_bars:
            st.markdown('<div class="section-title">Distribution des probabilités</div>', unsafe_allow_html=True)
            st.markdown(prob_bars_html(all_probs, predicted_idx), unsafe_allow_html=True)
        with col_metrics:
            st.markdown('<div class="section-title">Métriques clés</div>', unsafe_allow_html=True)
            st.metric("Classe prédite", f"{CLASS_ICONS[tumor_type]} {tumor_type}")
            st.metric("Confiance", f"{confidence_pct:.2f}%")
            st.metric("Précision modèle", f"{MODEL_STATS[tumor_type]}%")

    with tab_med:
        card_css = card_class(tumor_type)
        st.markdown(
            f'<div class="result-card {card_css}">',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div style="font-size:1.6rem; font-weight:800; color:{color}; margin-bottom:0.4rem;">'
            f'{CLASS_EMOJI[tumor_type]} {tumor_type}</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<p style="color:rgba(255,255,255,0.7); font-size:0.95rem; line-height:1.7; margin-bottom:1rem;">'
            f'{info["description"]}</p>',
            unsafe_allow_html=True
        )

        meta_col1, meta_col2 = st.columns(2)
        with meta_col1:
            st.markdown(f"""
            <div style="font-size:0.85rem; line-height:2;">
              <span style="color:rgba(255,255,255,0.45);">Sévérité :</span>
              <span style="color:{color}; font-weight:600;"> {info['severity']}</span><br>
              <span style="color:rgba(255,255,255,0.45);">Prévalence :</span>
              <span style="color:white; font-weight:500;"> {info['prevalence']}</span><br>
              <span style="color:rgba(255,255,255,0.45);">Traitement :</span>
              <span style="color:white; font-weight:500;"> {info['treatment']}</span>
            </div>""", unsafe_allow_html=True)
        with meta_col2:
            if info['symptoms']:
                st.markdown(
                    '<div style="color:rgba(255,255,255,0.45); font-size:0.85rem; margin-bottom:0.3rem;">Symptômes associés :</div>',
                    unsafe_allow_html=True
                )
                for s in info['symptoms']:
                    st.markdown(
                        f'<div style="color:rgba(255,255,255,0.75); font-size:0.85rem;">• {s}</div>',
                        unsafe_allow_html=True
                    )

        st.markdown(
            f'<div style="margin-top:1.2rem; padding:1rem; '
            f'background:{color}12; border:1px solid {color}30; border-radius:12px; '
            f'font-size:0.88rem; color:rgba(255,255,255,0.8); line-height:1.6;">'
            f'{"⚠️" if tumor_type != "No Tumor" else "✅"} <b>Recommandation :</b> {info["recommendation"]}</div>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_report:
        report_text = generate_text_report(
            uploaded_file.name, tumor_type, confidence_pct, all_probs
        )
        st.code(report_text, language=None)
        st.download_button(
            label="⬇️ Télécharger le rapport (.txt)",
            data=report_text.encode('utf-8'),
            file_name=f"neuroscan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True,
        )


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    st.markdown(PREMIUM_CSS, unsafe_allow_html=True)
    render_sidebar()

    # Hero header
    st.markdown("""
    <div class="neuro-hero">
      <div class="neuro-title">🧠 NeuroScan AI</div>
      <div class="neuro-subtitle">Détection et classification de tumeurs cérébrales par IRM</div>
      <div class="neuro-badge">ResNet50 · Transfer Learning · 98.96% Accuracy</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    uploaded_file = render_upload_zone()

    if uploaded_file is not None:
        try:
            render_analysis(uploaded_file)
            render_history()
        except Exception as e:
            st.error(f"❌ Erreur lors de l'analyse : {e}")
            st.info("Vérifiez que l'image est une IRM cérébrale valide.")
    else:
        render_placeholder()
        render_history()


if __name__ == '__main__':
    main()
