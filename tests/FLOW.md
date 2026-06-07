# 🗺 tests/ FLOW — pytest en 10 secondes

> 17 tests couvrent l'API et l'auto-découverte. TestClient en mémoire, pas besoin d'uvicorn.

---

## 🚀 Pipeline de test

```
1️⃣  pytest tests/   (depuis la racine)
        │
        ▼
2️⃣  pytest discovery
        ├─ lit pytest.ini (testpaths=tests)
        ├─ collecte tests/test_*.py
        └─ collecte fixtures depuis conftest.py
        │
        ▼
3️⃣  conftest.py exécuté (session-level)
        │
        ├─ env BRAINSCAN_DISABLE_RATELIMIT=1     ← bypass slowapi
        ├─ env BRAINSCAN_API_KEY=""               ← bypass auth
        │
        ├─ fixture client (session) :
        │     ├─ from fastapi.testclient import TestClient
        │     ├─ from api.app import app
        │     └─ TestClient(app) → load_model() en mémoire (~2 s)
        │
        └─ fixture fake_jpeg_bytes / fake_png_bytes :
              └─ génère PIL Image aléatoire 224×224 RGB
        │
        ▼
4️⃣  Exécution séquentielle des tests
        │
        ├─── test_api.py (13 tests, ~7 s) ────────────────────┐
        │   │                                                  │
        │   ├─ test_health_ok                                  │
        │   ├─ test_predict_jpeg                               │
        │   ├─ test_predict_png                                │
        │   ├─ test_predict_invalid_format     (attendu 400)   │
        │   ├─ test_predict_cache_hit          (MD5 cache)     │
        │   ├─ test_random_returns_prediction                  │
        │   ├─ test_explain_glioma                             │
        │   ├─ test_explain_no_tumor                           │
        │   ├─ test_explain_unknown_class      (attendu 404)   │
        │   ├─ test_sample_pituitary                           │
        │   ├─ test_sample_unknown_class       (attendu 404)   │
        │   ├─ test_stats                                      │
        │   └─ test_batch                                      │
        │                                                      │
        └────────────────────────────────────────────────────────┘
        │
        ├─── test_dataset_stats.py (4 tests, ~2 s) ───────────┐
        │   │                                                  │
        │   ├─ test_registry_discovers_all_analyses (>= 22)    │
        │   ├─ test_all_analyses_have_required_attributes      │
        │   ├─ test_analyses_sorted_by_order                   │
        │   └─ test_no_dependency_analysis_runs                │
        │                                                      │
        └────────────────────────────────────────────────────────┘
        │
        ▼
✅ 17 passed in ~10 s
```

---

## 🧪 Couverture par fichier

```
tests/
├── conftest.py                          ← Fixtures session (TestClient, images)
├── test_api.py            13 tests      ← E2E tous les endpoints
├── test_dataset_stats.py   4 tests      ← Registry + discoverabilité
└── __init__.py                          ← Marqueur de package
```

---

## 🎯 Test typique (ex: test_predict_jpeg)

```
1️⃣  client fixture déjà initialisé (modèle chargé)
        │
        ▼
2️⃣  fake_jpeg_bytes fixture → génère JPEG aléatoire 224×224
        │
        ▼
3️⃣  client.post("/predict", files={"file": ("test.jpg", bytes, "image/jpeg")})
        │
        ▼
4️⃣  TestClient appelle l'app FastAPI in-process (pas de réseau)
        │
        ├─ même pipeline que prod : preprocess → forward → Grad-CAM → JSON
        │
        ▼
5️⃣  assertions
        ├─ response.status_code == 200
        ├─ predicted_class ∈ {Glioma, Meningioma, No Tumor, Pituitary}
        ├─ 0 ≤ confidence ≤ 1
        ├─ sum(probabilities.values()) ≈ 1.0
        └─ data["original_image"] présent
```

---

## 🚀 Commandes utiles

```bash
# Tous les tests
pytest tests/

# Avec verbose
pytest tests/ -v

# API uniquement
pytest tests/test_api.py -v

# dataset_stats (rapide, pas besoin du modèle)
pytest tests/test_dataset_stats.py -v

# Avec couverture
pytest --cov=api --cov=src tests/

# Test spécifique
pytest tests/test_api.py::test_predict_jpeg -v
```

---

## 🤖 En CI GitHub Actions

```
Push sur main/develop
        │
        ▼
.github/workflows/ci.yml
        │
        ├─ Job lint   → ruff + black --check
        ├─ Job test   → pytest tests/test_dataset_stats.py
        │              (test_api.py skip car .pth absent en CI)
        └─ Job docker → docker build
```

→ Pour activer `test_api.py` en CI : commit le `.pth` via Git LFS.

---

> Voir [`README.md`](README.md) pour les détails des fixtures et conventions.
