# 📊 dataset_stats/ — Architecture modulaire pour stats & figures

> **Auto-découverte** + **CLI flexible** : 1 fichier = 1 analyse, ajoutée sans modifier le code central.

---

## ⚡ En 30 secondes

| | |
|---|---|
| 🎯 **Rôle** | Générer toutes les figures et statistiques du projet |
| 📊 **Analyses** | **22** (auto-découvertes) |
| 🐍 **CLI** | `python run.py [--list] [--only] [--except] [--filter] [--category]` |
| 🧱 **Architecture** | Registry-based, modulaire, idempotente |

---

## 🗺️ Architecture

```
dataset_stats/
│
├── run.py                          ← Entry point CLI
│
├── core/                           ← Infrastructure partagée
│   ├── config.py                   ← Constantes (classes, paths, couleurs)
│   ├── data.py                     ← Chargement .npy + listing
│   ├── plotting.py                 ← matplotlib defaults + save_figure
│   └── registry.py                 ← Auto-découverte des analyses
│
├── analyses/                       ← 1 fichier = 1 analyse
│   ├── fig01_class_distribution.py
│   ├── ...
│   ├── fig13_lr_schedule.py
│   ├── fig14_roc_curves.py             ← courbes ROC one-vs-rest + AUC
│   ├── fig15_pr_curves.py              ← courbes Precision-Recall + AP
│   ├── fig16_calibration.py            ← reliability diagram + Brier
│   ├── fig17_mean_image.py             ← image moyenne par classe
│   ├── fig18_top_predictions.py        ← Top-1/2/3 accuracy
│   ├── fig19_channel_stats.py          ← stats par canal R/G/B
│   ├── fig20_image_entropy.py          ← Shannon entropy distribution
│   ├── fig21_class_similarity.py       ← matrice de similarité inter-classes
│   └── fig22_class_focus_confusion.py  ← mini-matrices "1 vs rest"
│
└── outputs/                        ← Généré automatiquement (organisé par catégorie)
    ├── figures/                    ← 22 figures haute résolution PNG 150 DPI
    │   ├── overview/   (2 PNG)     ←  01-02 : distribution classes & splits
    │   ├── image/      (9 PNG)     ←  03,04,05,06,10,17,19,20,21
    │   ├── training/   (2 PNG)     ←  07,13 : courbes loss/LR
    │   ├── evaluation/ (5 PNG)     ←  08,09,14,15,16 : confusion, ROC, PR, calib
    │   └── errors/     (4 PNG)     ←  11,12,18,22 : analyse erreurs
    ├── data/                       ← Même structure miroir en JSON
    │   ├── overview/   (2 JSON)
    │   ├── image/      (9 JSON)
    │   ├── training/   (2 JSON)
    │   ├── evaluation/ (5 JSON)
    │   └── errors/     (4 JSON)
    └── summary.json                ← Master summary (tout-en-un)
```

---

## 🚀 Pipeline

```
1️⃣  run.py démarre
        │
        ▼
2️⃣  setup_matplotlib()                      ← UTF-8 stdout, style global
        │
        ▼
3️⃣  discover()                              ← scan analyses/fig*.py
        │   └─ pour chaque module : import + lecture des metadata
        ▼
4️⃣  filter_items()                          ← --only, --except, --filter, --category
        │
        ▼
5️⃣  Pour chaque analyse sélectionnée :
        ├─ is_runnable() ?                  ← REQUIRES = ["data","logs","results"]
        │     ├─ NON → [skip]
        │     └─ OUI ▼
        ├─ run() retourne dict
        ├─ save_figure(fig, NAME)           ← outputs/figures/<name>.png
        └─ save_data(NAME, data)            ← outputs/data/<name>.json
        │
        ▼
6️⃣  Master summary.json écrit
```

---

## 📋 Catalogue des 22 analyses

### 📂 Phase 1 — Données & exploration (overview · image)

| # | Nom | Catégorie | Requires | Description |
|:---:|---|---|---|---|
| 01 | Class distribution           | overview   | `data`    | Bar + pie chart par classe |
| 02 | Train/Val/Test split         | overview   | `data`    | Stratified 70/15/15 |
| 03 | Pixel statistics             | image      | `data`    | Mean/std/min/max par classe |
| 04 | Image properties             | image      | —         | Tailles, channels, dtype |
| 05 | Sample grid                  | image      | `data`    | 5 exemples par classe |
| 06 | Augmentation examples        | image      | `data`    | Original vs 7 transformations |
| 10 | Intensity histograms         | image      | `data`    | Distribution intensité (overlay+KDE) |
| 17 | **Mean image per class**     | image      | `data`    | Image moyenne pixel-wise (révèle anatomie typique) |
| 19 | **Per-channel statistics**   | image      | `data`    | Mean/std par canal R/G/B (validation grayscale) |
| 20 | **Image entropy**            | image      | `data`    | Distribution Shannon entropy (complexité visuelle) |
| 21 | **Inter-class similarity**   | image      | `data`    | Matrice de similarité cosine entre images moyennes |

### 🏋️ Phase 2 — Entraînement (training)

| # | Nom | Catégorie | Requires | Description |
|:---:|---|---|---|---|
| 07 | Training history             | training   | `logs`    | Courbes loss/acc 50 époques |
| 13 | Learning rate schedule       | training   | —         | LR vs époque (2 stages + ReduceLR) |

### 📊 Phase 3 — Évaluation (evaluation · errors)

| # | Nom | Catégorie | Requires | Description |
|:---:|---|---|---|---|
| 08 | Confusion matrix             | evaluation | `results` | Heatmap counts + recall norm |
| 09 | Per-class metrics            | evaluation | `results` | P/R/F1 par classe |
| 11 | Confidence distribution      | errors     | `results` | Conf correct vs erreur + boxplot |
| 12 | Misclassification analysis   | errors     | `results` | Top patterns + error rate par classe |
| 14 | **ROC curves**               | evaluation | `results` | Courbes ROC one-vs-rest + AUC par classe |
| 15 | **Precision-Recall curves**  | evaluation | `results` | Courbes PR + Average Precision par classe |
| 16 | **Calibration diagram**      | evaluation | `results` | Reliability + Brier score (sur/sous-confiance) |
| 18 | **Top-K predictions**        | evaluation | `results` | Top-1 vs Top-2 vs Top-3 accuracy |
| 22 | **Class focus confusion**    | errors     | `results` | 4 mini-matrices "1 vs rest" (confusion ciblée) |

---

## 🚀 CLI — exemples

```bash
# Lister toutes les analyses (groupées par catégorie)
python dataset_stats/run.py --list

# Tout exécuter
python dataset_stats/run.py

# Sélection précise
python dataset_stats/run.py --only 01,03,07

# Tout sauf certaines
python dataset_stats/run.py --except 06,10

# Recherche par mot-clé (titre/nom)
python dataset_stats/run.py --filter training

# Filtrer par catégorie
python dataset_stats/run.py --category evaluation
```

---

## 🧱 Pourquoi cette architecture est adaptative ?

| Principe | Bénéfice |
|---|---|
| **Auto-découverte** | Ajouter un fichier `figXX_*.py` → automatiquement disponible |
| **1 fichier = 1 analyse** | Édition / suppression sans toucher au reste |
| **Détection de prérequis** | Manque `data/` ? Skip propre, pas de crash |
| **Catégorisation** | Filtrage CLI par `overview / image / training / evaluation / errors` |
| **Sortie standardisée** | Chaque `run()` retourne dict → JSON automatique |
| **Helpers centralisés** | Style mpl, couleurs, palettes dans `core/` |
| **CLI flexible** | `--only`, `--except`, `--filter`, `--category` |
| **Idempotent** | Réexécution écrase proprement |

---

## ➕ Ajouter une nouvelle analyse (1 étape)

### Créer `analyses/fig14_my_analysis.py`

```python
"""14 — My new analysis."""
import matplotlib.pyplot as plt
from core import CLASSES, CLASS_COLORS, list_class_files, save_figure

NAME        = "14_my_analysis"
TITLE       = "My new analysis"
DESCRIPTION = "Description courte"
CATEGORY    = "image"           # overview | image | training | evaluation | errors | misc
REQUIRES    = ["data"]          # data | logs | results | (vide)
ORDER       = 14

def run() -> dict:
    fig, ax = plt.subplots(figsize=(8, 5))
    # ... votre code ...
    save_figure(fig, NAME)
    return {"my_metric": 42}
```

### C'est tout

```bash
python dataset_stats/run.py --list
# → Votre analyse apparaît
python dataset_stats/run.py --only 14
# → Exécutée
```

**Aucun fichier `core/` ou `run.py` à modifier.**

---

## 🧪 API publique de `core/`

| Import | Type | Description |
|---|---|---|
| `CLASSES` | list | `["glioma","meningioma","notumor","pituitary"]` |
| `CLASS_LABELS` | dict | `{"glioma":"Glioma",...}` |
| `CLASS_COLORS` | dict | `{"glioma":"#EF4444",...}` |
| `CLASS_INDEX` | dict | `{0:"glioma", ...}` |
| `DATA_DIR` | Path | `data/processed` |
| `LOGS_DIR` | Path | `logs/` |
| `RESULTS_DIR` | Path | `results/` |
| `FIGURES_DIR` | Path | `outputs/figures/` |
| `load_npy(path)` | fn | Charge .npy → uint8 |
| `list_class_files(cls)` | fn | Liste fichiers .npy d'une classe |
| `latest_training_csv()` | fn | Retourne le CSV training le plus récent |
| `test_results_csv()` | fn | Retourne `results/test_results.csv` |
| `save_figure(fig, name)` | fn | Save → `outputs/figures/<name>.png` |
| `save_data(name, dict)` | fn | Save → `outputs/data/<name>.json` |

---

## 📁 Outputs générés

| Chemin | Contenu | Format |
|---|---|---|
| `outputs/figures/01_*.png` | 22 figures haute résolution | PNG 150 DPI |
| `outputs/data/01_*.json` | Données numériques par analyse | JSON |
| `outputs/summary.json` | Agrégat de tous les runs | JSON |

---

## 🗂 Organisation automatique par catégorie

Depuis la v2.1, **chaque figure et JSON est rangé dans un sous-dossier** correspondant à sa catégorie. Aucun changement requis dans les analyses : le `registry.py` injecte automatiquement la catégorie via `set_current_category()` avant chaque `run()`, et `save_figure()` / `save_data()` la lisent.

### Structure générée

```
outputs/
├── figures/
│   ├── overview/         🌐 Vue d'ensemble dataset (2 figures)
│   │   ├── 01_class_distribution.png
│   │   └── 02_split_distribution.png
│   │
│   ├── image/            🖼 Propriétés visuelles (9 figures)
│   │   ├── 03_pixel_statistics.png
│   │   ├── 04_image_properties.png
│   │   ├── 05_sample_grid.png
│   │   ├── 06_augmentation_examples.png
│   │   ├── 10_intensity_histograms.png
│   │   ├── 17_mean_image.png
│   │   ├── 19_channel_stats.png
│   │   ├── 20_image_entropy.png
│   │   └── 21_class_similarity.png
│   │
│   ├── training/         🏋 Courbes d'entraînement (2 figures)
│   │   ├── 07_training_history.png
│   │   └── 13_lr_schedule.png
│   │
│   ├── evaluation/       📊 Qualité du modèle (5 figures)
│   │   ├── 08_confusion_matrix.png
│   │   ├── 09_per_class_metrics.png
│   │   ├── 14_roc_curves.png
│   │   ├── 15_pr_curves.png
│   │   └── 16_calibration.png
│   │
│   └── errors/           🔥 Analyse des erreurs (4 figures)
│       ├── 11_confidence_distribution.png
│       ├── 12_misclassification_analysis.png
│       ├── 18_top_predictions.png
│       └── 22_class_focus_confusion.png
│
├── data/                 (même structure miroir en .json)
│
└── summary.json          (agrégat de tous les runs)
```

### Pourquoi cette organisation ?

| Avantage | Détail |
|---|---|
| **Lisibilité** | On trouve immédiatement les figures pertinentes par sujet |
| **Présentation** | Pour un rapport, on prend tout `evaluation/` ou tout `image/` d'un coup |
| **Évolutivité** | Une nouvelle analyse trouve sa place toute seule (juste `CATEGORY = "..."`) |
| **Compatibilité** | Aucune analyse à modifier — la magie est dans le registry |
| **Symétrie figures/data** | Trouver le JSON d'une figure se fait en remplaçant `figures/` par `data/` et `.png` par `.json` |

### Override manuel

Si une analyse veut **forcer un autre sous-dossier** ou rester en flat :

```python
save_figure(fig, NAME, category="custom_subfolder")  # forcer un dossier custom
save_figure(fig, NAME, category=None)                # forcer racine outputs/figures/
```

---

## 🚦 Exemple de sortie

```
═══════════════════════════════════════════════
  Running 13 / 13 analyses
═══════════════════════════════════════════════
  [run ] 01_class_distribution               Class distribution
         ↳ ✓ 0.18s
  [run ] 02_split_distribution               Train/Val/Test split
         ↳ ✓ 0.05s
  ...
  [skip] 08_confusion_matrix                 (missing results/test_results.csv)
  ...
═══════════════════════════════════════════════
  ✅ Done — 13 analyses in 8.42s
═══════════════════════════════════════════════
  Figures        → dataset_stats/outputs/figures
  Per-analysis   → dataset_stats/outputs/data
  Summary JSON   → dataset_stats/outputs/summary.json
```

---

## ⚠️ Pièges courants

| Symptôme | Cause | Solution |
|---|---|---|
| `[skip]` partout | Lancé hors racine | `cd` à la racine projet |
| Caractères Unicode cassés | Console Windows cp1252 | `setup_matplotlib()` force UTF-8 (déjà fait) |
| Albumentations indisponible | Module non installé | fig06 a un fallback automatique |
| `ModuleNotFoundError: core` | sys.path mauvais | `run.py` ajoute `dataset_stats/` au sys.path |

---

## 🔗 Liens

- Tests du registre : [`../tests/test_dataset_stats.py`](../tests/test_dataset_stats.py)
- Données source : [`../data/processed/`](../data/processed/)
- Logs source : [`../logs/`](../logs/)
- Résultats source : [`../results/`](../results/)
- Statistiques détaillées : [`STATISTICS.md`](STATISTICS.md)
