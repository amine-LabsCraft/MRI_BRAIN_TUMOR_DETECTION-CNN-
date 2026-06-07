# 🧪 tests/ — Suite pytest automatisée

> **Garantit la non-régression** de l'API et de l'architecture modulaire `dataset_stats/`. Zero-config : pas de port, pas d'uvicorn.

---

## ⚡ En 30 secondes

| | |
|---|---|
| 🎯 **Rôle** | Tests E2E API + tests structurels du registre |
| 🐍 **Framework** | pytest 7+ |
| 🚀 **Mode** | In-process via FastAPI `TestClient` |
| ⏱ **Durée totale** | ~30s (modèle chargé 1 fois en `scope="session"`) |
| 📊 **Tests** | 16 (12 API + 4 registry) |

---

## 🗺️ Pyramide de tests

```
            ┌─────────────────────┐
            │   Tests E2E API     │  ← test_api.py (12 tests)
            │  (heavyweight)      │     charge le modèle 98 MB
            ├─────────────────────┤
            │ Tests structurels   │  ← test_dataset_stats.py (4 tests)
            │  (registry, smoke)  │     pure Python, pas de modèle
            └─────────────────────┘
```

Pas (encore) de tests unitaires fins — l'effort est mis sur le contrat **API JSON** et l'**auto-découverte** des analyses.

---

## 📂 Fichiers

| Fichier | Lignes | Rôle |
|---|---:|---|
| `conftest.py` | ~55 | Fixtures pytest : `client`, `fake_jpeg_bytes`, `fake_png_bytes` |
| `test_api.py` | ~140 | Tests E2E des 7 endpoints FastAPI |
| `test_dataset_stats.py` | ~50 | Tests du registre auto-découvert |
| `__init__.py` | 0 | Marqueur de package |

---

## 🚀 Pipeline d'exécution

```
1️⃣  pytest démarré
        │
        ▼
2️⃣  conftest.py : env vars (DISABLE_RATELIMIT=1, API_KEY=)
        │
        ▼
3️⃣  Fixture `client` (scope="session")
        │  ← 1 seule fois pour toute la suite
        │  ← FastAPI TestClient lance app in-process
        │  ← Modèle ResNet50 (98 MB) chargé une fois
        ▼
4️⃣  Tests test_api.py (12 tests)         ┐
        │                                  │  ~30s total
        ▼                                  │
5️⃣  Tests test_dataset_stats.py (4 tests) ┘
        │
        ▼
6️⃣  Rapport (passed / failed / skipped)
```

---

## 📋 Catalogue des tests

### test_api.py (12 tests)

| # | Test | Endpoint | Vérifie |
|---|---|---|---|
| 1 | `test_health_ok` | `GET /health` | status, model name, accuracy, classes |
| 2 | `test_predict_jpeg` | `POST /predict` | classe valide, conf ∈ [0,1], somme proba ≈ 1 |
| 3 | `test_predict_png` | `POST /predict` | accepte PNG (200 OK) |
| 4 | `test_predict_invalid_format` | `POST /predict` | rejette text/plain (400) |
| 5 | `test_predict_cache_hit` | `POST /predict` ×2 | 2ᵉ retourne `from_cache=True` |
| 6 | `test_random_returns_prediction` | `GET /random` | predicted_class + true_class + Grad-CAM |
| 7 | `test_explain_glioma` | `GET /explain/glioma` | description + urgency |
| 8 | `test_explain_no_tumor` | `GET /explain/no_tumor` | 200 OK |
| 9 | `test_explain_unknown_class` | `GET /explain/xyz` | 404 |
| 10 | `test_sample_pituitary` | `GET /sample/pituitary` | classe + image base64 |
| 11 | `test_sample_unknown_class` | `GET /sample/xyz` | 404 |
| 12 | `test_stats` | `GET /stats` | total_predictions, class_distribution |
| 13 | `test_batch` | `POST /batch` | 2 fichiers → count=2 |

### test_dataset_stats.py (4 tests)

| # | Test | Vérifie |
|---|---|---|
| 1 | `test_registry_discovers_13_analyses` | Registre trouve **exactement 13** analyses |
| 2 | `test_all_analyses_have_required_attributes` | NAME, TITLE, CATEGORY valide, REQUIRES, run callable |
| 3 | `test_analyses_sorted_by_order` | Triées par ORDER croissant |
| 4 | `test_no_dependency_analysis_runs` | fig04 (sans deps) tourne et retourne dict |

---

## 🧰 Fixtures

| Fixture | Scope | Type | Utilisée par |
|---|---|---|---|
| `client` | session | FastAPI TestClient | tous les tests API |
| `fake_jpeg_bytes` | function | bytes JPEG 224×224 | predict, batch, cache_hit |
| `fake_png_bytes` | function | bytes PNG 64×64 | predict (test resize) |

---

## 🚀 Commandes

```bash
# Tous les tests
venv\Scripts\python.exe -m pytest tests/ -v

# Un fichier
venv\Scripts\python.exe -m pytest tests/test_api.py -v

# Un test précis
venv\Scripts\python.exe -m pytest tests/test_api.py::test_predict_jpeg -v

# Filtre par mot-clé
venv\Scripts\python.exe -m pytest tests/ -k "predict" -v

# Avec couverture
venv\Scripts\python.exe -m pytest tests/ --cov=api --cov-report=html

# Mode CI (sortie courte)
venv\Scripts\python.exe -m pytest tests/ --tb=short -q
```

---

## 📊 Couverture estimée

| Module | Tests directs | Couverture |
|---|---|---:|
| `api/app.py` | 12 E2E | ~85 % |
| `api/settings.py` | indirect | ~70 % |
| `dataset_stats/core/registry.py` | 4 directs | ~90 % |
| `dataset_stats/analyses/*` | 1 (fig04) | ~10 % |

---

## 💡 Pourquoi c'est rapide

| Optimisation | Bénéfice |
|---|---|
| **Modèle scope="session"** | Chargé 1 fois, pas par test |
| **TestClient in-process** | Pas d'uvicorn, pas de port |
| **Fixtures bytes en mémoire** | Pas d'I/O disque |
| **Rate limit désactivé** | Pas de 429 → pas de retry |
| **API key désactivée** | Pas de header à propager |

---

## ➕ Ajouter un test

### Pour un endpoint
```python
# tests/test_api.py
def test_my_endpoint(client, fake_jpeg_bytes):
    r = client.post("/my-route", files={"file": ("a.jpg", fake_jpeg_bytes, "image/jpeg")})
    assert r.status_code == 200
    assert "expected_field" in r.json()
```

### Pour un module Python
```python
# tests/test_<module>.py  (auto-découvert)
def test_model_output_shape():
    import torch
    from src.model_architecture import ResNet50Classifier
    model = ResNet50Classifier(num_classes=4, pretrained=False)
    out = model(torch.randn(1, 3, 224, 224))
    assert out.shape == (1, 4)
```

---

## ⚠️ Pièges courants

| Symptôme | Cause | Solution |
|---|---|---|
| `ModuleNotFoundError: api` | Lancé hors racine | `cd` à la racine puis `pytest tests/` |
| Premier test très lent | Modèle 98 MB chargé | Normal, suivants instantanés |
| `429 Too Many Requests` | DISABLE_RATELIMIT pas set | Vérifier `conftest.py` ligne 22 |
| CI plante | Modèle absent | `git lfs pull` ou télécharger le `.pth` |

---

## 🔗 Liens

- Backend testé : [`../api/`](../api/)
- Registre testé : [`../dataset_stats/core/registry.py`](../dataset_stats/core/registry.py)
- Config pytest : [`../pytest.ini`](../pytest.ini)
- Pre-commit : [`../.pre-commit-config.yaml`](../.pre-commit-config.yaml)
- Deps test : [`../requirements-dev.txt`](../requirements-dev.txt)
