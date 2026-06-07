# 📡 api/ — Backend FastAPI (port 8000)

> **Le cœur production** du projet : expose le modèle ResNet50 via REST.

---

## ⚡ En 30 secondes

| | |
|---|---|
| 🎯 **Rôle** | Servir le modèle ResNet50 entraîné via 7 endpoints REST |
| 🚪 **Port** | 8000 |
| 🧠 **Modèle** | Chargé une seule fois au démarrage (singleton) |
| 🔥 **Grad-CAM** | Calculé en temps réel via hooks PyTorch |
| 💾 **Cache** | LRU MD5 — 100 entrées (réponses instantanées sur image répétée) |
| 🛡️ **Sécurité** | CORS · rate limiting (slowapi) · API key optionnelle |

---

## 🗺️ Position dans le projet

```
                    ┌──────────────┐
                    │  interface/  │ (frontend HTML/JS)
                    └──────┬───────┘
                           │ HTTP fetch
                           ▼
   data/processed/  ──►  ┌──────────────┐  ──►  réponse JSON
                         │   api/       │       (prediction +
                         │   app.py     │        Grad-CAM base64)
   models/         ──►   └──────────────┘
   *.pth                        │
                                ▼
                      consomme src/model_architecture.py
```

---

## 📂 Fichiers

| Fichier                         | Lignes |                Rôle                                                    |
|---                              |---    :|                  ---                                                   |
| `app.py`                        | ~530   | Application FastAPI complète (routes, middlewares, lifespan, Grad-CAM) |
| `settings.py`                   | ~80    | Configuration centralisée (lecture `.env`, logger)                     |
| `__init__.py`                   | 0      |             Marqueur de package Python                                 |

---

## 🔌 Les 7 endpoints

| # | Méthode | Route | Entrée | Sortie | Cache ? |
|---|---|---|---|---|---|
| 1 | `GET` | `/health` | — | statut + métadonnées modèle | ❌ |
| 2 | `POST` | `/predict` | multipart `file` (JPEG/PNG ≤10MB) | classe + probas + Grad-CAM | ✅ MD5 |
| 3 | `GET` | `/random` | — | image dataset aléatoire + prédiction | ❌ |
| 4 | `GET` | `/explain/{class}` | path param | infos médicales (description, urgence...) | ❌ |
| 5 | `GET` | `/sample/{class}` | path param | image base64 d'exemple (sans prédiction) | ❌ |
| 6 | `POST` | `/batch` | multipart `files[]` (max 20) | liste de prédictions | ❌ |
| 7 | `GET` | `/stats` | — | stats de session (total, distribution, latence) | ❌ |

📚 Documentation Swagger interactive : **http://localhost:8000/docs**

---

## 🚀 Pipeline d'une requête `/predict`

```
1️⃣  Client uploade IRM (multipart)
        │
        ▼
2️⃣  Validation MIME + taille (≤10MB)
        │
        ▼
3️⃣  Calcul MD5 → cache hit ?
        │
        ├─ OUI → retour instantané
        │
        └─ NON ▼
4️⃣  Préprocessing (Resize 224 + ImageNet norm)
        │
        ▼
5️⃣  Forward pass ResNet50
        │
        ▼
6️⃣  Softmax + argmax → classe + probas
        │
        ▼
7️⃣  Hook backward sur layer4[-1] → Grad-CAM
        │
        ▼
8️⃣  Encodage base64 (image + heatmap + overlay)
        │
        ▼
9️⃣  Mise en cache + mise à jour stats session
        │
        ▼
🔟  Retour JSON (~150 ms GPU / ~700 ms CPU)
```

---

## 🚀 Lancement

| Méthode | Commande |
|---|---|
| Dev (auto-reload) | `uvicorn api.app:app --port 8000 --reload` |
| Prod | `uvicorn api.app:app --host 0.0.0.0 --port 8000 --workers 2` |
| Via `start.py` | `python start.py` (lance API + frontend) |
| Tests | `pytest tests/test_api.py -v` |

---

## ⚙️ Configuration via `.env`

| Variable | Défaut | Rôle |
|---|---|---|
| `BRAINSCAN_API_KEY` | (vide) | Si défini → header `X-API-Key` requis |
| `BRAINSCAN_DISABLE_RATELIMIT` | `0` | `1` désactive slowapi (utile en tests) |
| `BRAINSCAN_CORS_ORIGINS` | `*` | Liste CSV des origines autorisées |
| `BRAINSCAN_MAX_FILE_SIZE` | `10485760` | Taille max upload (bytes) |
| `BRAINSCAN_LOG_LEVEL` | `INFO` | DEBUG / INFO / WARNING / ERROR |

Template : `.env.example` à la racine du projet.

---

## 🧠 Stratégie de chargement du modèle

```
api lifespan startup
        │
        ▼
🔧 Patch pathlib._local (cross-platform)
        │
        ▼
📦 Création ResNet50Classifier(num_classes=4, pretrained=False)
        │
        ▼
💾 torch.load(MODEL_PATH, map_location=device)
   ├─ try weights_only=True (sécurité)
   └─ fallback weights_only=False (compat)
        │
        ▼
⚙️ load_state_dict(checkpoint["model_state_dict"])
        │
        ▼
✅ model.eval() + .to(device) + cache global → predictor
```

---

## 🛡 Middlewares

| Couche | Outil | Activation |
|---|---|---|
| **CORS** | `fastapi.middleware.cors` | Toujours (origines configurables) |
| **Rate limit** | `slowapi` | Sauf si `BRAINSCAN_DISABLE_RATELIMIT=1` |
| **API Key** | Custom dependency | Sauf si `BRAINSCAN_API_KEY` vide |
| **Lifespan** | FastAPI 0.95+ | Charge modèle au start, libère au stop |

---

## ⚠️ Pièges courants

| Symptôme | Cause | Solution |
|---|---|---|
| `ModuleNotFoundError: api` | Lancé hors racine projet | `cd` à la racine puis `uvicorn api.app:app` |
| `pathlib._local` AttributeError | Checkpoint Windows sur Linux | Patch déjà appliqué dans `app.py` (ligne ~25) |
| `429 Too Many Requests` | slowapi actif | `export BRAINSCAN_DISABLE_RATELIMIT=1` |
| Modèle introuvable | Path absolu | Vérifier `models/final_model_20251106_142153.pth` |
| Latence > 1s sur GPU | Modèle pas en VRAM | Vérifier `torch.cuda.is_available()` |

---

## 🔗 Liens

- Modèle servi : [`../models/`](../models/)
- Frontend client : [`../interface/`](../interface/)
- Tests E2E : [`../tests/test_api.py`](../tests/test_api.py)
- Configuration : [`../.env.example`](../.env.example)
- Docker : [`../Dockerfile`](../Dockerfile)
