# 📊 dataset_stats/analyses/ — 22 analyses modulaires

> **1 fichier = 1 analyse autonome.** Auto-découvert par le registre. Aucun import central à modifier pour en ajouter une.

---

## ⚡ En 30 secondes

| | |
|---|---|
| 🎯 **Rôle** | Chaque fichier produit 1 figure + 1 JSON |
| 🔢 **Nombre actuel** | **22 analyses** (fig01 → fig22) |
| 🏗 **Pattern** | Module Python avec metadata + fonction `run()` |
| 🔌 **Auto-découverte** | Le registre scanne `fig*.py` |

---

## 📂 Inventaire (22 fichiers)

```
analyses/
├── __init__.py                          (vide, marqueur de package)
├── README.md                            (ce fichier)
│
├── 🌐 OVERVIEW (2)
│   ├── fig01_class_distribution.py
│   └── fig02_split_distribution.py
│
├── 🖼 IMAGE (9)
│   ├── fig03_pixel_statistics.py
│   ├── fig04_image_properties.py
│   ├── fig05_sample_grid.py
│   ├── fig06_augmentation_examples.py
│   ├── fig10_intensity_histograms.py
│   ├── fig17_mean_image.py
│   ├── fig19_channel_stats.py
│   ├── fig20_image_entropy.py
│   └── fig21_class_similarity.py
│
├── 🏋 TRAINING (2)
│   ├── fig07_training_history.py
│   └── fig13_lr_schedule.py
│
├── 📊 EVALUATION (5)
│   ├── fig08_confusion_matrix.py
│   ├── fig09_per_class_metrics.py
│   ├── fig14_roc_curves.py
│   ├── fig15_pr_curves.py
│   └── fig16_calibration.py
│
└── 🔥 ERRORS (4)
    ├── fig11_confidence_distribution.py
    ├── fig12_misclassification.py
    ├── fig18_top_predictions.py
    └── fig22_class_focus_confusion.py
```

---

## 🧬 Contrat d'une analyse

Chaque fichier `figXX_*.py` **doit** exposer 6 attributs et 1 fonction :

```python
"""XX — One-line description of the analysis."""
from __future__ import annotations
import matplotlib.pyplot as plt
from core import save_figure  # + autres imports selon besoin

# ─── Métadonnées (lues par registry.discover()) ──────────────────────────────
NAME        = "XX_my_analysis"        # str  — filename stem (= ORDER + slug)
TITLE       = "My analysis"           # str  — affiché dans --list
DESCRIPTION = "Short description"     # str  — 1 ligne de doc
CATEGORY    = "image"                 # str  — overview|image|training|evaluation|errors|misc
REQUIRES    = ["data"]                # list — sous-ensemble de data|logs|results
ORDER       = XX                      # int  — ordre d'exécution (1, 2, 3, ...)


# ─── Fonction run (point d'entrée) ───────────────────────────────────────────
def run() -> dict:
    """Compute, plot, save → return data for summary.json."""
    fig, ax = plt.subplots(figsize=(10, 6))
    # ... votre code matplotlib ...

    save_figure(fig, NAME)   # auto-rangé dans outputs/figures/<CATEGORY>/

    return {"my_metric": 42, "items_processed": 100}
```

### Détails du contrat

| Attribut | Type | Effet |
|---|---|---|
| `NAME` | `str` | Doit commencer par `"XX_"` (préfixe à 2 chiffres). Devient le nom du PNG/JSON. |
| `TITLE` | `str` | Phrase courte pour `--list` |
| `DESCRIPTION` | `str` | 1 ligne explicative (utilisée éventuellement dans futures docs) |
| `CATEGORY` | `str` | Strict parmi `{overview, image, training, evaluation, errors, misc}` |
| `REQUIRES` | `list[str]` | Sous-ensemble de `{"data", "logs", "results"}`. Vide = aucune dépendance externe |
| `ORDER` | `int` | Trie l'exécution. Utiliser `XX` comme dans le filename pour cohérence. |
| `run()` | `→ dict` | Calcule, sauvegarde la figure, retourne un dict pour `summary.json` |

→ Si une attribute manque, `registry.discover()` log un warning et **skip** le fichier (pas de crash).

---

## ➕ Ajouter une 23ᵉ analyse en 4 étapes

### 1. Créer le fichier

```bash
# analyses/fig23_my_new_thing.py
```

### 2. Coller le squelette

```python
"""23 — Description courte."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from core import (
    CLASSES, CLASS_COLORS, CLASS_LABELS,
    list_class_files, load_npy,
    save_figure,
)

NAME        = "23_my_new_thing"
TITLE       = "My new thing"
DESCRIPTION = "What this analysis computes"
CATEGORY    = "image"          # adapter selon le sujet
REQUIRES    = ["data"]
ORDER       = 23


def run() -> dict:
    # 1. Compute
    results = {}
    for cls in CLASSES:
        files = list_class_files(cls, limit=100)
        imgs = [load_npy(f) for f in files]
        results[cls] = float(np.mean([img.mean() for img in imgs]))

    # 2. Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(
        [CLASS_LABELS[c] for c in CLASSES],
        [results[c] for c in CLASSES],
        color=[CLASS_COLORS[c] for c in CLASSES],
    )
    ax.set_title("My new thing — mean intensity per class")
    ax.set_ylabel("Mean intensity (0-1)")
    save_figure(fig, NAME)

    # 3. Return data for summary.json
    return {"means": results}
```

### 3. Tester

```bash
python dataset_stats/run.py --list
# → Votre analyse 23 apparaît automatiquement

python dataset_stats/run.py --only 23
# → Génère outputs/figures/image/23_my_new_thing.png
#   + outputs/data/image/23_my_new_thing.json
```

### 4. C'est tout

→ **Aucun fichier `core/` ou `run.py` ne change.**

---

## 📋 Catalogue détaillé des 22 analyses

### 🌐 Overview — distribution générale du dataset

| # | Fichier | Description |
|:--:|---|---|
| 01 | `fig01_class_distribution.py` | Bar + pie chart : combien d'images par classe |
| 02 | `fig02_split_distribution.py` | Répartition train/val/test stratifiée 70/15/15 |

### 🖼 Image — propriétés visuelles

| # | Fichier | Description |
|:--:|---|---|
| 03 | `fig03_pixel_statistics.py` | Mean / std / min / max des pixels par classe |
| 04 | `fig04_image_properties.py` | Carte info : tailles, channels, dtype, pipeline |
| 05 | `fig05_sample_grid.py` | Grille 5 exemples par classe |
| 06 | `fig06_augmentation_examples.py` | Original vs 7 transformations Albumentations |
| 10 | `fig10_intensity_histograms.py` | Distribution des intensités (overlay + KDE) |
| 17 | `fig17_mean_image.py` | Image moyenne pixel-wise par classe (anatomie typique) |
| 19 | `fig19_channel_stats.py` | Mean/std par canal R/G/B (validation grayscale) |
| 20 | `fig20_image_entropy.py` | Distribution Shannon entropy (complexité visuelle) |
| 21 | `fig21_class_similarity.py` | Matrice cosine entre images moyennes |

### 🏋 Training — entraînement du modèle

| # | Fichier | Description |
|:--:|---|---|
| 07 | `fig07_training_history.py` | Courbes loss/accuracy par époque (Stage 1+2) |
| 13 | `fig13_lr_schedule.py` | Visualisation du LR scheduler (lr=1e-3 → 1e-4) |

### 📊 Evaluation — qualité du modèle

| # | Fichier | Description |
|:--:|---|---|
| 08 | `fig08_confusion_matrix.py` | Matrice de confusion (counts + recall normalisé) |
| 09 | `fig09_per_class_metrics.py` | Precision / Recall / F1 par classe (bar chart) |
| 14 | `fig14_roc_curves.py` | Courbes ROC one-vs-rest + AUC par classe |
| 15 | `fig15_pr_curves.py` | Courbes Precision-Recall + Average Precision |
| 16 | `fig16_calibration.py` | Reliability diagram + Brier score |

### 🔥 Errors — analyse des erreurs

| # | Fichier | Description |
|:--:|---|---|
| 11 | `fig11_confidence_distribution.py` | Distribution confiance correct vs erreur (boxplot) |
| 12 | `fig12_misclassification.py` | Top patterns d'erreur + error rate par classe |
| 18 | `fig18_top_predictions.py` | Top-K accuracy (Top-1 vs Top-2 vs Top-3) |
| 22 | `fig22_class_focus_confusion.py` | 4 mini-matrices "1 vs rest" |

---

## 🛡 Robustesse et conventions

### Robustesse

| Garantie | Mécanisme |
|---|---|
| **Prérequis manquants** | `REQUIRES = [...]` → analyse `[skipped]` au lieu de crash |
| **Run lui-même crashe** | `[FAIL]` log + traceback, autres analyses continuent |
| **Output skip silencieux** | Retourner `{"skipped": "raison"}` au lieu de crash |
| **Reproductibilité** | `RANDOM_SEED = 42` partout dans `core/config.py` |

### Conventions

| Convention | Exemple |
|---|---|
| **Filename** | `figXX_<slug>.py` où XX est sur 2 chiffres |
| **NAME** | `XX_<slug>` (sans préfixe `fig`) → utilisé pour le PNG/JSON |
| **CATEGORY** | toujours en lowercase parmi 5 valeurs prédéfinies |
| **TITLE** | phrase courte commençant par majuscule |
| **save_figure** | toujours appeler avant `return` |
| **return** | toujours `dict` (jamais `None`) |
| **Imports** | toujours `from core import ...` (pas relatifs) |

---

## 🧪 Tester une seule analyse

```bash
# Test isolation
python dataset_stats/run.py --only 17

# Test avec --list pour vérifier l'enregistrement
python dataset_stats/run.py --list | grep 17

# Test depuis Python
python -c "
import sys
sys.path.insert(0, 'dataset_stats')
from analyses.fig17_mean_image import run
result = run()
print(result)
"
```

---

## ⚠️ Pièges courants

| Symptôme | Cause | Solution |
|---|---|---|
| `[FAIL] ImportError: cannot import name 'CLASS_X'` | Classe inexistante dans `core/config.py` | Ajouter à `CLASSES` ou typo |
| `[FAIL] FileNotFoundError` | Prérequis manquant non déclaré | Ajouter à `REQUIRES = [...]` |
| Figure pas dans le bon sous-dossier | `save_figure` appelé hors `run()` | Toujours dans `run()` |
| `[skip]` alors qu'on s'y attend pas | `is_runnable()` failed | Vérifier `REQUIRES` |
| `[FAIL] AttributeError: NAME` | Metadata manquante | Réparer le fichier (les 6 attrs obligatoires) |
| Numéro déjà utilisé | Doublon `ORDER` | Vérifier les fichiers existants |

---

## 📚 Voir aussi

- [`../README.md`](../README.md) — Vue d'ensemble dataset_stats
- [`../core/README.md`](../core/README.md) — Infrastructure (config, helpers)
- [`../run.py`](../run.py) — CLI qui orchestre tout
- [`../outputs/`](../outputs/) — Où sont écrits les résultats

---

> **Convention** : 1 fichier = 1 analyse · zéro état partagé · idempotent · catégorisé.
