# 🗺 api/ FLOW — Pipeline d'une requête HTTP

> Du `uvicorn` au JSON de réponse, voici les étapes exactes.

---

## 🚀 Démarrage du serveur

```
uvicorn api.app:app --port 8000 --reload
        │
        ▼
1️⃣  Pathlib patch (cross-OS pour les .pth)
        │
        ▼
2️⃣  load .env via python-dotenv (api/settings.py)
        │
        ▼
3️⃣  get_logger("brainscan.api") → handler stream + formatter
        │
        ▼
4️⃣  Lifespan startup (@asynccontextmanager)
        │
        ├─ ResNet50Classifier(num_classes=4, pretrained=False)
        ├─ torch.load(MODEL_PATH, weights_only=True/False fallback)
        ├─ load_state_dict(checkpoint["model_state_dict"])
        ├─ model.to(device) + .eval()
        └─ predictor = model  (singleton global)
        │
        ▼
5️⃣  Middlewares montés
        ├─ CORSMiddleware (settings.CORS_ORIGINS)
        ├─ SlowAPIMiddleware (60 req/min/IP par défaut)
        └─ require_api_key (si BRAINSCAN_API_KEY défini)
        │
        ▼
✅ API READY sur :8000  →  /docs (Swagger) accessible
```

---

## 📡 Pipeline d'une requête `POST /predict`

```
   📥 Client → POST multipart/form-data {file: IRM.jpg}
        │
        ▼
1️⃣  CORS check (origine autorisée ?)
        │
        ▼
2️⃣  SlowAPI rate limit (60/min/IP)
        │
        ├─ trop de requêtes → 429 Too Many Requests
        │
        ▼
3️⃣  require_api_key (si activé)
        │
        ├─ X-API-Key absent/invalide → 401
        │
        ▼
4️⃣  Validation
        ├─ MIME ∈ {jpeg, png, jpg} ?  → sinon 400
        └─ taille ≤ 10 MB ?           → sinon 413
        │
        ▼
5️⃣  Calcul MD5 du contenu
        │
        ├─ HIT cache → retour instantané {... "from_cache": true}
        │
        ▼ MISS
6️⃣  Preprocessing (~5 ms)
        ├─ PIL.Image.open(BytesIO)
        ├─ convert("RGB")
        ├─ Resize(224, 224)
        ├─ ToTensor()
        └─ Normalize(ImageNet mean/std)
        │
        ▼
7️⃣  Forward pass ResNet50 (~30 ms CPU / ~10 ms GPU)
        ├─ model(tensor) → logits [1, 4]
        ├─ softmax → probabilities [4]
        └─ argmax → predicted_idx
        │
        ▼
8️⃣  Grad-CAM (~80 ms CPU)
        ├─ register_forward_hook(layer4[-1])  → activations
        ├─ register_full_backward_hook(layer4[-1]) → gradients
        ├─ backward avec one-hot sur predicted_idx
        ├─ weights = grads.mean(dim=(1,2))
        ├─ cam = (weights × activations).sum() · ReLU · normalize
        ├─ cm.jet(cam) → colorize heatmap
        └─ overlay = α·heatmap + (1-α)·image
        │
        ▼
9️⃣  Encodage base64
        ├─ original_image  (resized 400×400 JPEG)
        ├─ gradcam_heatmap (PNG colorisé)
        └─ gradcam_overlay (PNG superposé)
        │
        ▼
🔟  Cache write (LRU, max 100 entrées)
        │
        ▼
1️⃣1️⃣  Update session_stats (counter, conf moyenne, latence)
        │
        ▼
   📤 JSON response (~150 ms total CPU)
        {
          "predicted_class": "Glioma",
          "confidence":      0.9979,
          "probabilities":   {...},
          "original_image":  "<base64>",
          "gradcam_heatmap": "<base64>",
          "gradcam_overlay": "<base64>",
          "inference_time_ms": 36.2,
          "from_cache":      false
        }
```

---

## 📁 Fichiers concernés

| Fichier | Rôle |
|---|---|
| `app.py` | Toute la logique (530 lignes) |
| `settings.py` | Config + logger (80 lignes) |
| `__init__.py` | Marqueur de package |

---

> Voir [`README.md`](README.md) pour les détails de configuration et de déploiement.
