# 🧠 BrainScan AI — Détection et classification de tumeurs cérébrales

[![PyTorch](https://img.shields.io/badge/PyTorch-2.11-EE4C2C?logo=pytorch)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/Tests-17%20passed-2ED573)](.)
[![Accuracy](https://img.shields.io/badge/Accuracy-98.96%25-2ED573)](.)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](.)
[![License](https://img.shields.io/badge/License-Educational-blue)](.)

> Système complet d'IA médicale : **classification de tumeurs cérébrales par IRM** via ResNet50 (transfer learning).
> 98.96 % d'accuracy sur 1 054 images de test, avec interface web moderne, API FastAPI, Grad-CAM, **22 statistiques modulaires**, et déploiement Docker.

---

## ⚡ Démarrage en 1 commande

```bash
# Windows : double-clic sur start.bat
# OU (cross-platform) :
python start.py
```

→ L'API + l'interface web démarrent automatiquement, le navigateur s'ouvre sur `http://localhost:3000`.

📚 **Documentation détaillée par dossier** : voir le tableau des [READMEs](#-documentation-par-dossier) plus bas.

---

## 📁 Architecture du projet

```
mri_brain_tumor-main/
│
├── 🚀 LANCEURS                                    1 commande pour tout démarrer
│   ├── start.py                                   Lanceur intelligent cross-platform (recommandé)
│   ├── start.bat                                  Lanceur Windows (double-clic)
│   └── stop.bat                                   Arrêt propre des serveurs
│
├── 📡 api/                                        Backend FastAPI — port 8000
│   ├── app.py                                     7 endpoints : /health /predict /random /explain ...
│   ├── settings.py                                Configuration centralisée (.env, logger)
│   └── README.md
│
├── 🌐 interface/                                  Frontend Vanilla JS — port 3000
│   ├── index.html                                 Layout HTML5 (header, upload, résultats, historique)
│   ├── styles.css                                 Design system light + dark (922 lignes)
│   ├── app.js                                     16 blocs (1350 lignes) · Chart.js · jsPDF
│   └── README.md
│
├── 🎨 streamlit_app/                              Frontend alternatif Streamlit (port 8501)
│   ├── app.py                                     UI mono-fichier avec Grad-CAM intégré
│   └── README.md
│
├── 🧱 src/                                        Modules PyTorch réutilisables
│   ├── model_architecture.py                      ResNet50Classifier (transfer learning)
│   ├── model_trainer.py                           PyTorchTrainer 2 stages
│   ├── data_loaders.py                            DataLoaders + Albumentations
│   ├── data_preprocessing.py                      Resize 256 → CenterCrop 224 + ImageNet norm
│   ├── dataset_split.py                           Split stratifié 70/15/15
│   ├── data_pipeline.py                           Pipeline orchestrateur end-to-end
│   ├── train_model.py                             CLI d'entraînement avancée
│   └── README.md
│
├── 🛠 scripts/                                    Scripts CLI (entry points utilisateur)
│   ├── train.py                                   Entraîner un modèle (Stage 1 + Stage 2)
│   ├── evaluate.py                                Évaluer le modèle PyTorch sur test set
│   ├── predict.py                                 Prédiction sur une image unique
│   ├── visualize_training.py                      Tracer les courbes loss/accuracy
│   ├── fix_model.py                               Patcher un checkpoint .pth corrompu
│   ├── quick_start.py / quick_train.py            Guides pédagogiques phases 1/2
│   └── README.md
│
├── 📊 dataset_stats/                              22 analyses modulaires auto-découvertes
│   ├── run.py                                     CLI : --list --only --except --filter --category
│   ├── core/                                      Infrastructure (config, data, plotting, registry)
│   │   └── README.md
│   ├── analyses/                                  22 modules autonomes (figXX_*.py)
│   │   └── README.md
│   ├── outputs/                                   Généré : figures/<cat>/ + data/<cat>/ + summary.json
│   └── README.md
│
├── 🧪 tests/                                      Suite pytest (17 tests, 100 % passing)
│   ├── conftest.py                                Fixtures partagées
│   ├── test_api.py                                13 tests E2E de l'API FastAPI
│   ├── test_dataset_stats.py                      4 tests du registry auto-découverte
│   └── README.md
│
├── 🗄 legacy/                                     Ancien code TensorFlow archivé (NE PAS UTILISER)
│   ├── *_tf.py                                    Fichiers Keras pré-migration PyTorch
│   └── README.md
│
├── 📂 data/                                       Dataset Brain Tumor MRI (Kaggle)
│   ├── raw/{Traning,Testing}/                     Images JPG/PNG brutes (4 GB)
│   ├── processed/                                 Images .npy normalisées 224×224
│   ├── splits/split_info.json                     train/val/test stratifié 70/15/15
│   └── README.md
│
├── 💾 models/                                     Checkpoints PyTorch
│   ├── final_model_20251106_142153.pth            Modèle entraîné (98.5 MB · 98.96 % acc)
│   └── README.md
│
├── 📋 logs/                                       Historiques d'entraînement
│   ├── training_history_<ts>.csv                  Métriques par époque
│   ├── stage1_<ts>/, stage2_<ts>/                 TensorBoard event files
│   └── README.md
│
├── 📈 results/                                    Résultats d'évaluation
│   ├── evaluation_summary.txt                     Métriques globales
│   ├── test_results.csv                           Prédictions par image
│   ├── confusion_matrix.png · class_performance.png · training_history.png
│   └── README.md
│
├── 📚 docs/                                       Guides de setup et phases historiques
│   ├── INSTALLATION.md · GPU_SETUP.md · QUICK_START.md
│   ├── PHASE{1,2,3}_COMPLETE.md
│   └── README.md
│
├── 🤖 .github/                                    CI/CD GitHub Actions
│   ├── workflows/ci.yml                           Pipeline lint → test → docker
│   └── README.md
│
├── ⚙️ CONFIGURATION
│   ├── .env.example                               Template config (CORS, API_KEY, RATE_LIMIT…)
│   ├── config.json                                Métadonnées projet (classes, paths)
│   ├── pyproject.toml                             Config black + ruff + pytest + mypy
│   ├── pytest.ini                                 Config pytest (markers, paths)
│   ├── requirements.txt                           Dépendances production
│   ├── requirements-dev.txt                       Dépendances dev (pytest, black, ruff…)
│   ├── runtime.txt                                Python 3.11.9 (pour Render)
│   ├── .pre-commit-config.yaml                    Hooks pre-commit (lint avant push)
│   ├── .gitattributes                             Git LFS pour *.pth, *.pt, *.h5
│   ├── .gitignore
│   └── .dockerignore
│
├── 🐳 DOCKER
│   ├── Dockerfile                                 Image multi-stage Python 3.11 + FastAPI
│   └── docker-compose.yml                         API (8000) + Nginx serving interface (3000)
│
└── 🔬 venv/                                       Environnement virtuel Python
```

---

## 🚀 Démarrage rapide

### 1️⃣ Installation (premier lancement uniquement)

```bash
cd mri_brain_tumor-main

# Créer le venv si absent
python -m venv venv

# Installer les dépendances production
venv\Scripts\pip install -r requirements.txt

# (Optionnel) Pour développer/tester :
venv\Scripts\pip install -r requirements-dev.txt
```

### 2️⃣ Lancement automatique

| Méthode | Commande | Usage |
|---|---|---|
| 🟢 **Windows simple** | Double-clic sur `start.bat` | Ouvre 2 fenêtres + navigateur |
| 🔵 **Cross-platform** | `python start.py` | Lanceur intelligent unifié (recommandé) |
| 🐳 **Docker** | `docker compose up` | API + Nginx en containers |
| 🟡 **Manuel** | Voir [Lancement manuel](#-lancement-manuel) | Contrôle séparé de chaque service |

`start.py` détecte les ports occupés, attend que l'API soit prête, ouvre le navigateur, et tue proprement les 2 serveurs avec `Ctrl+C`.

```bash
python start.py --help              # toutes les options
python start.py --no-browser        # ne pas ouvrir le navigateur
python start.py --api-port 9000     # API sur un autre port
python start.py --no-reload         # désactive l'auto-reload
```

### 3️⃣ Tester l'interface

- **Web app** : http://localhost:3000
- **API health** : http://localhost:8000/health
- **API docs** (Swagger) : http://localhost:8000/docs
- **Streamlit** (alternative) : http://localhost:8501 (après `streamlit run streamlit_app/app.py`)

Cliquez sur **"Random Example"** pour voir une analyse complète sur une image du dataset.

---

## 🔧 Configuration via `.env`

Toute la configuration runtime de l'API passe par les **variables d'environnement** :

```bash
# Copier le template
cp .env.example .env

# Éditer selon vos besoins :
# BRAINSCAN_CORS_ORIGINS=https://monsite.com,https://app.monsite.com
# BRAINSCAN_API_KEY=ma-cle-secrete-32-chars
# BRAINSCAN_RATE_LIMIT=120
# BRAINSCAN_LOG_LEVEL=DEBUG
```

| Variable | Défaut | Effet |
|---|---|---|
| `BRAINSCAN_MODEL_PATH` | `models/final_model_20251106_142153.pth` | Chemin du checkpoint |
| `BRAINSCAN_CORS_ORIGINS` | `*` | Liste séparée par virgules ou `*` |
| `BRAINSCAN_API_KEY` | (vide) | Si défini → header `X-API-Key` requis sur `/predict` et `/batch` |
| `BRAINSCAN_RATE_LIMIT` | `60` | Req/min/IP. `0` = désactivé |
| `BRAINSCAN_DISABLE_RATELIMIT` | `0` | `1` pour bypass complet (utilisé par les tests) |
| `BRAINSCAN_LOG_LEVEL` | `INFO` | DEBUG / INFO / WARNING / ERROR |

📚 Détails : [`api/README.md`](api/README.md) section "Configuration via .env"

---

## 🧪 Tests automatisés

```bash
# Tous les tests (17 au total)
venv\Scripts\python.exe -m pytest tests/

# Avec couverture
venv\Scripts\python.exe -m pytest --cov=api --cov=src tests/

# API uniquement (13 tests E2E)
venv\Scripts\python.exe -m pytest tests/test_api.py -v

# dataset_stats (4 tests, plus rapide, pas de modèle nécessaire)
venv\Scripts\python.exe -m pytest tests/test_dataset_stats.py -v
```

**État actuel** : ✅ 17/17 PASSED en ~10 s

📚 Détails : [`tests/README.md`](tests/README.md)

---

## 🐳 Docker

### Lancement

```bash
# Build + lance API (port 8000) + Nginx (port 3000)
docker compose up --build

# En arrière-plan
docker compose up -d

# Stop
docker compose down
```

### Image production

Le `Dockerfile` est **multi-stage** :
- Stage 1 (builder) : installe les dépendances avec gcc disponible
- Stage 2 (runtime) : copie seulement les packages installés, image finale ~1.5 GB

L'image tourne en **utilisateur non-root** (`brainscan`) pour la sécurité.

---

## 🛠 Scripts CLI

Tous les scripts utilisateur sont dans `scripts/`. Lancer depuis la racine :

```bash
# Entraîner un modèle (Stage 1 + Stage 2 — 30 min GPU / 4-6 h CPU)
venv\Scripts\python.exe scripts\train.py

# Évaluer le modèle sur le test set
venv\Scripts\python.exe scripts\evaluate.py

# Prédire sur une image unique
venv\Scripts\python.exe scripts\predict.py --image path\to\mri.jpg

# Visualiser l'historique d'entraînement
venv\Scripts\python.exe scripts\visualize_training.py

# Réparer un checkpoint corrompu
venv\Scripts\python.exe scripts\fix_model.py
```

📚 Détails de chaque script : [`scripts/README.md`](scripts/README.md)

---

## 📊 Statistiques & figures (22 analyses, architecture modulaire)

Le dossier `dataset_stats/` utilise un **registre auto-découvert** : 1 fichier = 1 analyse.
Les outputs sont **organisés automatiquement** dans des sous-dossiers par catégorie.

```bash
# Lister les 22 analyses disponibles (groupées par catégorie)
venv\Scripts\python.exe dataset_stats\run.py --list

# Tout exécuter (génère 22 figures + 22 JSON + summary)
venv\Scripts\python.exe dataset_stats\run.py

# Sélection précise
venv\Scripts\python.exe dataset_stats\run.py --only 01,03,07,14,15
venv\Scripts\python.exe dataset_stats\run.py --category evaluation     # 5 figures
venv\Scripts\python.exe dataset_stats\run.py --category image          # 9 figures
venv\Scripts\python.exe dataset_stats\run.py --filter training         # match titre/nom
```

**Structure des sorties** (organisée automatiquement par catégorie) :

```
dataset_stats/outputs/
├── figures/
│   ├── overview/   (2 PNG)   ← distributions classes & splits
│   ├── image/      (9 PNG)   ← propriétés visuelles, augmentation, similarité
│   ├── training/   (2 PNG)   ← courbes loss + LR schedule
│   ├── evaluation/ (5 PNG)   ← confusion, ROC, PR, calibration, top-K
│   └── errors/     (4 PNG)   ← confidence, misclassif, focus erreurs
├── data/           (22 JSON, même structure miroir)
└── summary.json    (agrégat de tous les runs)
```

📚 Doc complète : [`dataset_stats/README.md`](dataset_stats/README.md)

---

## 🌐 Frontends disponibles

Le projet propose **deux interfaces** au choix :

| Interface | URL | Lancement | Avantages |
|---|---|---|---|
| **FastAPI + JS** (par défaut) | `localhost:3000` | `start.py` | Multi-utilisateurs · API REST · historique persisté · export PDF/PNG/CSV |
| **Streamlit** (alternative) | `localhost:8501` | `streamlit run streamlit_app\app.py` | Démarrage en 1 ligne · Grad-CAM intégré · idéal pour démos |

---

## 🔌 API FastAPI — Endpoints

| Méthode | Endpoint | Auth ? | Description                                       |
|---     |---                     |---  |---                                       |
| `GET`  | `/health`              | ❌ | Statut API + métadonnées modèle          |
| `POST` | `/predict`             | ✅ | Prédire sur une image (multipart upload) |
| `GET`  | `/random`              | ❌ | Image aléatoire du dataset + prédiction  |
| `GET`  | `/explain/{class}`     | ❌ | Informations médicales sur une classe    |
| `POST` | `/batch`               | ✅ | Prédire sur plusieurs images (max 20)    |
| `GET`  | `/sample/{class}`      | ❌ | Image d'exemple sans prédiction          |
| `GET`  | `/stats`               | ❌ | Statistiques de session                  |

**Auth** : appliquée seulement si `BRAINSCAN_API_KEY` non-vide dans `.env` (header `X-API-Key`).
**Rate limit** : 60 req/min/IP par défaut (configurable via `.env`).

Documentation interactive Swagger : `http://localhost:8000/docs`

---

## 🧠 Modèle

| Aspect | Détail |
|---|---|
| **Architecture** | ResNet50 (ImageNet pretrained) + tête Dense 2048→512→4 |
| **Classes** | Glioma · Meningioma · No Tumor · Pituitary |
| **Input** | RGB 224×224, normalisé ImageNet |
| **Stratégie** | Transfer learning en 2 stages (frozen → fine-tune 30 dernières couches) |
| **Paramètres** | ~24.6M total · ~1M trainable Stage 1 · ~15M trainable Stage 2 |
| **Loss / Optim** | CrossEntropyLoss · Adam (lr=1e-3 → 1e-4) |
| **Test accuracy** | **98.96 %** sur 1 054 images |
| **Inférence CPU** | ~36 ms/image |
| **Inférence GPU (RTX 2050)** | ~10 ms/image |
| **Grad-CAM** | Implémenté inline en pur PyTorch (hooks sur `layer4[-1]`) |

📚 Détails : [`src/README.md`](src/README.md)

---

## ⚙️ Lancement manuel

Si vous préférez contrôler chaque service séparément :

```bash
# Terminal 1 — API FastAPI
venv\Scripts\python.exe -m uvicorn api.app:app --port 8000 --reload

# Terminal 2 — Frontend HTML/JS
cd interface
python -m http.server 3000

# Terminal 3 (optionnel) — Streamlit
venv\Scripts\python.exe -m streamlit run streamlit_app\app.py
```

---

## 🤖 CI/CD GitHub Actions

À chaque push sur `main` / `master` / `develop` ou pull request :

```
🚦 Pipeline (3-5 min) :
   ├─ Job 1 : LINT       (ruff + black --check)
   ├─ Job 2 : TEST       (compileall + pytest tests/test_dataset_stats.py)
   └─ Job 3 : DOCKER     (build sans push, cache GHA)
```

Pour activer le **pre-commit local** (lint/format avant chaque commit) :
```bash
venv\Scripts\pip install pre-commit
pre-commit install
```

📚 Détails : [`.github/README.md`](.github/README.md)

---

## 📚 Documentation par dossier

Chaque dossier dispose de son propre README **détaillé** :

| Dossier | README | Contenu |
|---|---|---|
| 📡 **api/** | [api/README.md](api/README.md) | FastAPI · 7 endpoints · Grad-CAM PyTorch · cache MD5 |
| 🌐 **interface/** | [interface/README.md](interface/README.md) | Frontend Vanilla JS · 16 blocs `app.js` · design system |
| 🎨 **streamlit_app/** | [streamlit_app/README.md](streamlit_app/README.md) | Streamlit mono-fichier · alternative à FastAPI |
| 🧱 **src/** | [src/README.md](src/README.md) | Modules PyTorch · architecture · trainer 2 stages |
| 🛠 **scripts/** | [scripts/README.md](scripts/README.md) | 7 entry points CLI (train, evaluate, predict…) |
| 📊 **dataset_stats/** | [dataset_stats/README.md](dataset_stats/README.md) | 22 analyses auto-découvertes |
| 📊 **dataset_stats/core/** | [dataset_stats/core/README.md](dataset_stats/core/README.md) | Infrastructure (config, registry, plotting) |
| 📊 **dataset_stats/analyses/** | [dataset_stats/analyses/README.md](dataset_stats/analyses/README.md) | Contrat d'une analyse + catalogue des 22 |
| 🧪 **tests/** | [tests/README.md](tests/README.md) | 17 tests pytest · fixtures · TestClient |
| 🗄 **legacy/** | [legacy/README.md](legacy/README.md) | Code TF archivé (référence uniquement) |
| 📂 **data/** | [data/README.md](data/README.md) | Dataset Kaggle · raw → processed → splits |
| 💾 **models/** | [models/README.md](models/README.md) | Checkpoints PyTorch · format · chargement |
| 📋 **logs/** | [logs/README.md](logs/README.md) | TensorBoard + CSV par-époque |
| 📈 **results/** | [results/README.md](results/README.md) | Outputs d'évaluation (matrice confusion, etc.) |
| 📚 **docs/** | [docs/README.md](docs/README.md) | Guides historiques par phase |
| 🤖 **.github/** | [.github/README.md](.github/README.md) | CI/CD GitHub Actions |

---

## 🛠 Stack technique

| Catégorie | Technologies |
|---|---|
| **Deep Learning** | PyTorch 2.11 · torchvision · CUDA 11.8 (optionnel) |
| **Backend** | FastAPI · uvicorn · python-multipart · slowapi · python-dotenv |
| **Frontend** | Vanilla JS ES2020 · Chart.js 4.4 · Lucide · jsPDF · Inter font |
| **UI alternative** | Streamlit 1.25+ |
| **Data** | NumPy · Pandas · OpenCV · Pillow · Albumentations |
| **Visualisation** | Matplotlib · Seaborn · Scikit-learn |
| **Tests** | pytest · pytest-cov · httpx (TestClient) |
| **Lint/Format** | ruff · black · mypy |
| **Container** | Docker multi-stage · docker compose · Nginx |
| **CI/CD** | GitHub Actions · pre-commit |

---

## 📦 Outputs générés

```
logs/
└── training_history_<timestamp>.csv     ← métriques par époque

results/
├── evaluation_summary.txt
├── test_results.csv                     ← prédictions par image
├── confusion_matrix.png
├── training_history.png
└── class_performance.png

dataset_stats/outputs/
├── figures/{overview,image,training,evaluation,errors}/*.png  ← 22 figures par catégorie
├── data/{overview,image,training,evaluation,errors}/*.json    ← 22 JSON même structure
└── summary.json                                               ← agrégat de tous les runs
```

---

## 🚦 État du projet

| Composant | Statut | Détails |
|---|---|---|
| **API FastAPI** | ✅ | 7 endpoints · 13 tests passants |
| **Frontend Vanilla JS** | ✅ | 16 blocs · 0 framework · responsive |
| **Streamlit alternative** | ✅ | Mono-fichier · démo en 1 ligne |
| **Modèle ResNet50** | ✅ | 98.96 % accuracy · 95 MB |
| **Statistiques modulaires** | ✅ | 22 analyses · auto-découvertes |
| **Tests pytest** | ✅ | 17/17 passing |
| **Docker + compose** | ✅ | Multi-stage · non-root user |
| **CI/CD GitHub Actions** | ✅ | Lint + Test + Docker build |
| **Pre-commit hooks** | ✅ | ruff + black + check large files |
| **Documentation** | ✅ | 16 READMEs détaillés |

---

## ⚠️ Avertissement médical

> Cet outil est destiné à un **usage éducatif et de recherche uniquement**.
> Il ne remplace en aucun cas un diagnostic médical professionnel.
> Consultez toujours un professionnel de santé qualifié pour tout sujet médical.

---

## 📜 Licence

Projet à usage **éducatif**. Dataset Kaggle : [Brain Tumor Classification MRI](https://www.kaggle.com/datasets/sartajbhuvaji/brain-tumor-classification-mri).

---

> **BrainScan AI** · ResNet50 · 98.96 % accuracy · 4 classes · Educational use only
