# 🧱 src/ — Modules PyTorch réutilisables

> **La bibliothèque interne** : architecture du modèle, pipeline data, trainer 2-stages. Importé par `api/`, `streamlit_app/`, `scripts/`, `tests/`.

---

## ⚡ En 30 secondes

| | |
|---|---|
| 🎯 **Rôle** | Code "métier" PyTorch réutilisable (modèle, données, entraînement) |
| 📦 **Type** | Modules Python importables (pas de scripts à lancer directement) |
| 🧠 **Modèle** | ResNet50 + tête custom (Dense 2048→512→4) |
| 🏋️ **Stratégie** | Transfer learning 2 stages (frozen → fine-tune 30 dernières couches) |

---

## 🗺️ Graphe de dépendances internes

```
                  ┌─────────────────────────┐
                  │  model_architecture.py  │  ← ResNet50Classifier
                  └────────────┬────────────┘
                               │
                  ┌────────────┴────────────┐
                  │   model_trainer.py      │  ← PyTorchTrainer (2 stages)
                  └────┬───────────────┬────┘
                       │               │
        ┌──────────────┘               └──────────────┐
        ▼                                              ▼
┌─────────────────┐                        ┌─────────────────────┐
│ data_loaders.py │ ←─── DataLoader        │training_callbacks.py│ (✗ déplacé)
└────────┬────────┘                        └─────────────────────┘
         │
         ▼
┌─────────────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│ data_preprocessing  │ →  │ data_augmentation   │ →  │ dataset_split.py │
│ (resize, normalize) │    │ (Albumentations)    │    │ (stratified 70/15│
└─────────────────────┘    └─────────────────────┘    └──────────────────┘
         │                          │                          │
         └──────────────┬───────────┴────────────┬─────────────┘
                        ▼                        ▼
              ┌───────────────────┐    ┌───────────────────┐
              │ data_pipeline.py  │    │  train_model.py   │
              │ (orchestrateur)   │    │  (CLI legacy)     │
              └───────────────────┘    └───────────────────┘
```

---

## 📂 Fichiers

| Fichier | Lignes | Rôle | Import principal |
|---|---:|---|---|
| `model_architecture.py` | ~240 | Architecture ResNet50Classifier | `ResNet50Classifier`, `create_model` |
| `model_trainer.py` | ~370 | Trainer 2 stages + checkpointing | `PyTorchTrainer`, `get_default_config` |
| `data_loaders.py` | ~210 | DataLoaders PyTorch + transforms | `create_data_loaders`, `BrainTumorDataset` |
| `data_preprocessing.py` | ~170 | Resize, normalize, validation | `DataPreprocessor` |
| `data_augmentation.py` | ~90 | Pipeline Albumentations | `DataAugmentor` |
| `dataset_split.py` | ~120 | Split stratifié 70/15/15 | `create_stratified_split` |
| `data_pipeline.py` | ~150 | Pipeline orchestrateur end-to-end | `run_pipeline` |
| `train_model.py` | ~180 | CLI d'entraînement (legacy, simplifié) | (script) |

---

## 🧠 Architecture du modèle (`model_architecture.py`)

```
Input: RGB tensor (B, 3, 224, 224)
        │
        ▼
┌───────────────────────────────────┐
│  ResNet50 backbone                │
│  • conv1 → bn1 → relu → maxpool   │
│  • layer1 (3× Bottleneck, 256)    │
│  • layer2 (4× Bottleneck, 512)    │
│  • layer3 (6× Bottleneck, 1024)   │
│  • layer4 (3× Bottleneck, 2048) ◄─── hooks Grad-CAM
│  • avgpool → flatten              │
│  base_model.fc = Identity()       │
└───────────────┬───────────────────┘
                │  (B, 2048)
                ▼
┌───────────────────────────────────┐
│  Custom classifier head           │
│  Linear(2048 → 512)               │
│  ReLU                             │
│  BatchNorm1d(512)                 │
│  Dropout(0.4)                     │
│  Linear(512 → 4)                  │
└───────────────┬───────────────────┘
                │  (B, 4)
                ▼
        Logits → Softmax → 4 classes
```

| Couches                | Paramètres    | Trainable Stage 1 | Trainable Stage 2                    |
|---                     |---        :   |---                 |---                                   |
| ResNet50 backbone      | ~23.5M        | ❌ frozen         | ⚠️ 30 dernières couches             |
| Tête custom            | ~1.05M        |  ✅               |         ✅                          |
| **Total**              | **~24.6M**    | ~1.05M             | ~15M                                |

---

## 🏋️ Pipeline d'entraînement (`model_trainer.py`)

```
get_default_config()
        │
        ▼
PyTorchTrainer.train_two_stages()
        │
        ├── Stage 1 : 20 époques · LR=1e-3
        │     │
        │     ├─ model.freeze_base_layers()
        │     ├─ Adam optimizer (head only)
        │     ├─ ReduceLROnPlateau
        │     └─ Save best on val_loss
        │
        ├── Stage 2 : 30 époques · LR=1e-4
        │     │
        │     ├─ model.unfreeze_base_layers(num_layers=30)
        │     ├─ Adam optimizer (head + 30 last layers)
        │     ├─ ReduceLROnPlateau
        │     └─ Save best on val_loss
        │
        └── Save final_model_<timestamp>.pth + history CSV
```

| Hyperparamètre | Stage 1 | Stage 2 |
|---|---|---|
| Époques | 20 | 30 |
| Learning rate | 1e-3 | 1e-4 |
| Weight decay | 1e-4 | 1e-4 |
| Trainable params | ~1M | ~15M |
| Augmentation | Full | Light |

---

## 📦 Pipeline data (`data_pipeline.py` orchestrateur)

```
1️⃣  Lister images dans data/raw/{Training,Testing}/{class}/
2️⃣  Validation (corruption, format)             ← data_preprocessing
3️⃣  Resize 256 → CenterCrop 224                 ← data_preprocessing
4️⃣  Conversion RGB                              ← data_preprocessing
5️⃣  Normalisation [0,255] → [0,1] float32       ← data_preprocessing
6️⃣  Sauvegarde data/processed/{class}/*.npy
7️⃣  Split stratifié 70/15/15 (seed 42)           ← dataset_split
8️⃣  Écriture data/splits/split_info.json
```

---

## 🔌 Comment ce dossier est consommé

```
┌────────────────────────┐
│  api/app.py            │ ──► from model_architecture import ResNet50Classifier
└────────────────────────┘
┌────────────────────────┐
│  streamlit_app/app.py  │ ──► from model_architecture import ResNet50Classifier
└────────────────────────┘
┌────────────────────────┐
│  scripts/train.py      │ ──► from model_trainer import PyTorchTrainer
└────────────────────────┘     from data_loaders import create_data_loaders
┌────────────────────────┐
│  scripts/predict.py    │ ──► from model_architecture import ResNet50Classifier
└────────────────────────┘
┌────────────────────────┐
│  tests/test_api.py     │ ──► (indirectement via api/)
└────────────────────────┘
```

---

## 🧪 Cheat sheet — utilisation rapide

```python
# Charger un modèle
from src.model_architecture import ResNet50Classifier
model = ResNet50Classifier(num_classes=4, pretrained=False)
model.load_state_dict(torch.load("models/final_model_20251106_142153.pth")["model_state_dict"])

# Créer les DataLoaders
from src.data_loaders import create_data_loaders
loaders, classes = create_data_loaders(
    split_info_path="data/splits/split_info.json",
    batch_size=24,
)

# Entraîner from scratch
from src.model_trainer import PyTorchTrainer, get_default_config
config = get_default_config()
trainer = PyTorchTrainer(model, loaders, config)
trainer.train_two_stages()

# Régénérer les données processed/
from src.data_pipeline import run_pipeline
run_pipeline()
```

---

## ⚠️ Pièges courants

| Symptôme | Cause | Solution |
|---|---|---|
| `ModuleNotFoundError: src` | Import direct sans `sys.path` | Lancer depuis racine OU `sys.path.insert(0, "src")` |
| BatchNorm1d crash | Batch size = 1 | `drop_last=True` dans DataLoader train |
| OOM CUDA | Batch size trop grand | Réduire à 16 ou 8 |
| Inversion d'ordre des classes | Modification non cohérente | Ne JAMAIS changer `["glioma","meningioma","notumor","pituitary"]` |
| `_local` AttributeError | Checkpoint Windows ↔ Linux | Patch dans `api/app.py` & `streamlit_app/app.py` |

---

## 🔗 Liens

- Modèles produits : [`../models/`](../models/)
- Logs trainer : [`../logs/`](../logs/)
- Évaluation : [`../results/`](../results/)
- Scripts CLI : [`../scripts/`](../scripts/)
- Tests : [`../tests/`](../tests/)
