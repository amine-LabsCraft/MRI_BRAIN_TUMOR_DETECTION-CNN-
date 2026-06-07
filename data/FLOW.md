# 🗺 data/ FLOW — Phase 1 : Préparation des données

> Du dataset Kaggle brut aux `.npy` normalisés, voici les étapes exactes.

---

## 🎬 Pipeline complet de préparation

```
1️⃣  Installation des dépendances
        │
        └─ pip install -r requirements.txt
        │
        ▼
2️⃣  Téléchargement du dataset Kaggle
        │
        ├─ URL : kaggle.com/datasets/sartajbhuvaji/brain-tumor-classification-mri
        ├─ Décompresser dans data/raw/
        └─ Structure attendue :
              data/raw/
                ├─ Traning/                         (~5500 images)
                │   ├─ glioma/      (~1300)
                │   ├─ meningioma/  (~1300)
                │   ├─ notumor/     (~1600)
                │   └─ pituitary/   (~1300)
                └─ Testing/                          (~1300 images)
                    ├─ glioma/
                    ├─ meningioma/
                    ├─ notumor/
                    └─ pituitary/
        │
        ▼
3️⃣  Lancer le pipeline de prétraitement
        │
        └─ python -m src.data_pipeline
              │
              ▼
        ┌─── À l'intérieur de data_pipeline.py ──────────────────┐
        │                                                        │
        │  3a. Validation                                        │
        │      ├─ Liste tous les fichiers JPG/PNG               │
        │      ├─ Détecte fichiers corrompus (PIL.open)         │
        │      └─ Skip + log les invalides                      │
        │                                                        │
        │  3b. Conversion couleur                                │
        │      ├─ Si grayscale → convert("RGB")                 │
        │      └─ Si RGBA → drop alpha                           │
        │                                                        │
        │  3c. Resize                                            │
        │      ├─ Resize(256, 256) avec keep aspect ratio       │
        │      └─ Padding noir si nécessaire                    │
        │                                                        │
        │  3d. Center crop                                       │
        │      └─ CenterCrop(224, 224)                          │
        │                                                        │
        │  3e. Normalisation                                     │
        │      ├─ Convert uint8 [0,255] → float32 [0,1]         │
        │      └─ Normalize ImageNet (mean/std par canal)        │
        │                                                        │
        │  3f. Sauvegarde format .npy                            │
        │      ├─ data/processed/glioma/Te-gl_0001.npy           │
        │      ├─ data/processed/meningioma/Te-me_*.npy          │
        │      ├─ data/processed/notumor/Te-no_*.npy             │
        │      └─ data/processed/pituitary/Te-pi_*.npy           │
        │                                                        │
        │      → Format .npy = 4× plus rapide à charger         │
        │        que JPEG en runtime (binaire numpy)            │
        │                                                        │
        └─────────────────────────────────────────────────────────┘
        │
        ▼
4️⃣  Augmentation (côté DataLoader, runtime)
        │
        ├─ Albumentations.Compose appliqué uniquement au train set
        │
        ├─ HorizontalFlip(p=0.5)
        ├─ RandomRotate90(p=0.3)
        ├─ Rotate(limit=15, p=0.4)         ← rotation -15° / +15°
        ├─ RandomResizedCrop(scale=0.85)   ← zoom in/out léger
        ├─ RandomBrightnessContrast(0.2)   ← luminosité ± 20%
        ├─ GaussNoise(var_limit=(10, 50))  ← bruit Gaussien
        ├─ ElasticTransform(p=0.2)          ← déformation organique
        └─ Normalize ImageNet
        │
        ▼ (val/test reçoivent seulement Normalize, pas d'augmentation)
        │
        ▼
5️⃣  Split stratifié
        │
        └─ create_stratified_split(seed=42, ratios=(0.70, 0.15, 0.15))
              │
              ├─ Préserve la distribution des classes
              ├─ train : 4915 images
              ├─ val   : 1054 images
              ├─ test  : 1054 images
              │
              └─ Sauvegarde data/splits/split_info.json
                    {
                      "train": {"paths": [...], "labels": [...], "size": 4915},
                      "val":   {"paths": [...], "labels": [...], "size": 1054},
                      "test":  {"paths": [...], "labels": [...], "size": 1054},
                      "class_names": ["glioma", "meningioma", "notumor", "pituitary"]
                    }
        │
        ▼
6️⃣  Vérification (optionnel mais recommandé)
        │
        ├─ python dataset_stats/run.py --only 01,02,03,04,05,06
        │     │
        │     └─ Génère figures :
        │           ├─ class_distribution.png (équilibre vérifié)
        │           ├─ split_distribution.png (stratification ok)
        │           ├─ pixel_statistics.png   (stats par classe)
        │           ├─ image_properties.png   (info card)
        │           ├─ sample_grid.png        (exemples visuels)
        │           └─ augmentation_examples.png (transformations)
        │
        ▼
✅ Phase 1 terminée
   Données prêtes pour entraînement (Phase 2 → scripts/train.py)
```

---

## 📊 Résumé des chiffres

| Métrique | Valeur |
|---|---|
| **Images totales** | ~7 023 |
| **Train / Val / Test** | 4 915 / 1 054 / 1 054 |
| **Ratio split** | 70% / 15% / 15% |
| **Format final** | `.npy` (numpy) 224×224×3 float32 |
| **Taille totale processed/** | ~2 GB |
| **Classes** | 4 (équilibrées : ~1700 chacune) |

---

## 📁 Structure finale

```
data/
├── raw/                          ← Images brutes Kaggle (4 GB)
│   ├── Traning/{glioma,...}/    ← Note : faute de frappe Kaggle, géré par le code
│   └── Testing/{glioma,...}/
│
├── processed/                    ← Images normalisées .npy (2 GB)
│   ├── glioma/   (1621 .npy)
│   ├── meningioma/ (1645 .npy)
│   ├── notumor/  (2000 .npy)
│   └── pituitary/ (1757 .npy)
│
└── splits/
    └── split_info.json          ← Mappings train/val/test (617 KB)
```

---

> Voir [`README.md`](README.md) pour les détails du dataset Kaggle et les conventions.
