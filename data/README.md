# 📂 data/ — Dataset Brain Tumor MRI

> **Source unique** des images : raw → processed → split. 7 023 images, 4 classes, format `.npy`.

---

## ⚡ En 30 secondes

| | |
|---|---|
| 🧠 **Source** | Kaggle — Brain Tumor MRI Dataset |
| 📊 **Total** | 7 023 images |
| 🏷 **Classes** | 4 (glioma, meningioma, notumor, pituitary) |
| 🎯 **Split** | 70/15/15 stratifié, seed 42 |
| 💾 **Format** | `.npy` 224×224×3 float32 [0,1] |

---

## 🗺️ Pipeline data

```
┌────────────────┐
│  Kaggle .zip   │  ← téléchargement manuel
└────────┬───────┘
         │ extract
         ▼
┌────────────────┐
│  data/raw/     │  ← Training/ + Testing/ (gitignoré, ~150 MB)
│  *.jpg, *.png  │
└────────┬───────┘
         │ scripts/quick_start.py
         │  • resize 256 → centercrop 224
         │  • RGB convert
         │  • normalize [0,255] → [0,1]
         ▼
┌────────────────────┐
│  data/processed/   │  ← *.npy 224×224×3 (gitignoré, ~4 GB)
│  {class}/*.npy     │
└────────┬───────────┘
         │ src/dataset_split.py
         │  • stratified train/val/test
         │  • seed 42 (reproductible)
         ▼
┌─────────────────────┐
│  data/splits/       │  ← committé Git (~600 KB)
│  split_info.json    │
└─────────────────────┘
```

---

## 📂 Inventaire

```
data/
├── raw/                       gitignoré · ~150 MB
│   ├── Training/
│   │   ├── glioma/      *.jpg
│   │   ├── meningioma/  *.jpg
│   │   ├── notumor/     *.jpg
│   │   └── pituitary/   *.jpg
│   └── Testing/         (idem)
│
├── processed/                 gitignoré · ~4 GB
│   ├── glioma/      1621 × .npy
│   ├── meningioma/  1645 × .npy
│   ├── notumor/     2000 × .npy
│   └── pituitary/   1757 × .npy
│
└── splits/                    committé
    └── split_info.json        indices train/val/test
```

---

## 🏷 Mapping classes ↔ indices

⚠️ **Ordre figé par l'entraînement** (alphabétique) — ne pas changer.

| Index | Folder | Class label | Échantillons | % du dataset |
|:---:|---|---|---:|---:|
| **0** | `glioma`      | Glioma     | 1 621 | 23.1 % |
| **1** | `meningioma`  | Meningioma | 1 645 | 23.4 % |
| **2** | `notumor`     | No Tumor   | 2 000 | 28.5 % |
| **3** | `pituitary`   | Pituitary  | 1 757 | 25.0 % |
| | | **Total** | **7 023** | 100 % |

---

## 📊 Split stratifié (70/15/15, seed 42)

| Classe       | Train (70%) | Val (15%) | Test (15%) | Total |
|--------------|------------:|----------:|-----------:|------:|
| Glioma       | 1 135       | 243       | 243        | 1 621 |
| Meningioma   | 1 152       | 247       | 247        | 1 645 |
| No Tumor     | 1 400       | 300       | 300        | 2 000 |
| Pituitary    | 1 230       | 264       | 264        | 1 757 |
| **Total**    | **4 915**   | **1 054** | **1 054**  | **7 023** |

---

## 💾 Format `.npy`

| Propriété | Valeur |
|---|---|
| **Shape** | `(224, 224, 3)` |
| **Dtype** | `float32` |
| **Range** | `[0.0, 1.0]` (déjà normalisé /255) |
| **Layout** | RGB (HWC) |
| **Taille fichier** | ~600 KB par image |

### Exemple
```python
import numpy as np
arr = np.load("data/processed/glioma/Te-gl_0010.npy")
# arr.shape  → (224, 224, 3)
# arr.dtype  → float32
# arr.min()  → ~0.0
# arr.max()  → ~0.98
```

---

## 🎯 split_info.json

| Champ | Type | Description |
|---|---|---|
| `seed` | int | 42 (figé) |
| `ratios` | dict | `{train:0.70, val:0.15, test:0.15}` |
| `method` | str | "stratified" |
| `classes` | list | `["glioma","meningioma","notumor","pituitary"]` |
| `train.files` | list[str] | chemins .npy |
| `train.labels` | list[int] | indices de classe |
| `val.{files,labels}` | … | idem |
| `test.{files,labels}` | … | idem |

---

## 🔌 Consommé par

| Composant | Quoi ? | Comment ? |
|---|---|---|
| `src/data_loaders.py` | Tout | `create_data_loaders(split_info_path=...)` |
| `api/app.py` `/random` | `processed/` | Choix aléatoire |
| `api/app.py` `/sample` | `processed/` | Image exemple par classe |
| `dataset_stats/` | `processed/` | fig01, fig03, fig05, fig10 |
| `tests/test_api.py` | Indirect | Via API |

---

## 📊 Statistiques pixel par classe

(Calculé sur 200 images/classe — voir `dataset_stats/outputs/figures/03_pixel_statistics.png`)

| Classe       | Mean | Std  | Particularité |
|--------------|-----:|-----:|---|
| Glioma       | 42.3 | 38.8 | Bords irréguliers, œdème péri-tumoral |
| Meningioma   | 55.5 | 47.2 | Bien délimité, attache durale |
| No Tumor     | 72.5 | 57.5 | Plus lumineux (parenchyme intact) |
| Pituitary    | 58.6 | 38.4 | Masse sellaire centrale |

---

## 🚀 Régénération depuis raw/

```bash
# Étape 1 : télécharger Kaggle dataset → data/raw/
# Étape 2 :
venv\Scripts\python.exe scripts\quick_start.py
```

Génère :
1. `data/processed/{class}/*.npy` (tous les .npy)
2. `data/splits/split_info.json` (split déterministe)

---

## ⚠️ Pièges courants

| Symptôme | Cause | Solution |
|---|---|---|
| Dossier `notumor` (sans underscore) | Convention Kaggle | Mapping explicite côté code (`no_tumor` → `notumor`) |
| Ordre des classes différent | Modification manuelle | Toujours `[glioma, meningioma, notumor, pituitary]` (alphabétique) |
| Métriques non reproductibles | Seed changé | Garder `seed=42` partout |
| Inférence sur JPG/PNG fonctionne | Pipeline auto-décode | Pas besoin de `.npy` côté API |

---

## 🔗 Liens

- Pipeline : [`../src/data_pipeline.py`](../src/data_pipeline.py)
- Split : [`../src/dataset_split.py`](../src/dataset_split.py)
- DataLoaders : [`../src/data_loaders.py`](../src/data_loaders.py)
- Statistiques : [`../dataset_stats/`](../dataset_stats/)
- Configuration : [`../config.json`](../config.json)
- **Source Kaggle** : [Brain Tumor MRI Dataset](https://www.kaggle.com/datasets/sartajbhuvaji/brain-tumor-classification-mri)
