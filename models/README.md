# 💾 models/ — Checkpoints PyTorch

> **Le modèle final** consommé par toutes les interfaces (API, Streamlit, scripts).

---

## ⚡ En 30 secondes

| | |
|---|---|
| 🧠 **Modèle** | ResNet50 + tête custom (Dense 2048→512→4) |
| 📦 **Format** | `.pth` (PyTorch state_dict) |
| 💾 **Taille** | 98.5 MB |
| 🎯 **Test accuracy** | **98.96 %** (1 043/1 054) |
| 📅 **Trained** | 2025-11-06 14:21:53 |

---

## 🗺️ Cycle de vie d'un checkpoint

```
1️⃣  Initialisation                       ← src/model_architecture.py
        │
        ▼
2️⃣  Stage 1 (20 ep, frozen base)         ← src/model_trainer.py
        │   ├─ best_model_stage1.pth (gitignoré)
        │   └─ TensorBoard logs/stage1_*/
        ▼
3️⃣  Stage 2 (30 ep, fine-tune)
        │   ├─ best_model_stage2.pth (gitignoré)
        │   └─ TensorBoard logs/stage2_*/
        ▼
4️⃣  Save final                           ← models/final_model_<timestamp>.pth ✅
        │
        ▼
5️⃣  Évaluation                           ← scripts/evaluate.py
        │   └─ results/{evaluation_summary.txt, ...}
        ▼
6️⃣  Servi par                            ← api/app.py
                                           ← streamlit_app/app.py
                                           ← scripts/predict.py
```

---

## 📂 Inventaire

| Fichier | Tracké Git | Rôle |
|---|:---:|---|
| `final_model_20251106_142153.pth` | ✅ | **Modèle de référence (98.96 %)** |
| `best_model_stage1.pth` | ❌ | Best stage 1 (intermédiaire) |
| `best_model_stage2.pth` | ❌ | Best stage 2 (intermédiaire) |

Configuration `.gitignore` :
```
models/*.pth
!models/final_model_20251106_142153.pth
```

---

## 🧩 Structure du checkpoint

```python
{
    "epoch":            50,
    "model_state_dict": OrderedDict([...]),     # poids du modèle
    "val_loss":         0.0450,
    "val_acc":          0.9934,
    "config": {
        "batch_size":      24,
        "image_size":      [224, 224],
        "num_classes":     4,
        "stage1_epochs":   20,
        "stage2_epochs":   30,
        "stage1_lr":       1e-3,
        "stage2_lr":       1e-4,
        "unfreeze_layers": 30,
        "pretrained":      true,
        "dense_units":     512,
        "dropout_rate":    0.4,
    }
}
```

---

## 📊 Métadonnées du modèle final

| Aspect | Valeur |
|---|---|
| **Architecture** | ResNet50 + Linear(2048→512) + ReLU + BN + Dropout(0.4) + Linear(512→4) |
| **Total params** | ~24.6 M |
| **Trainable Stage 1** | ~1.05 M |
| **Trainable Stage 2** | ~15 M |
| **Optimizer** | Adam (weight_decay=1e-4) |
| **Loss** | CrossEntropyLoss |
| **Scheduler** | ReduceLROnPlateau (factor=0.5, patience=3) |
| **Best val accuracy** | 99.34 % @ epoch ~42 |
| **Best val loss** | 0.0450 |
| **Test accuracy** | **98.96 %** |

---

## 🏷 Mapping classes ↔ indices (figé)

| Index | Class | F1-Score |
|:---:|---|---:|
| 0 | Glioma | 98.76 % |
| 1 | Meningioma | 98.19 % |
| 2 | No Tumor | 99.67 % |
| 3 | Pituitary | 99.05 % |

---

## 🚀 Pipeline de chargement

```
┌──────────────────────────────────────┐
│  1. Patch pathlib (cross-platform)   │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  2. ResNet50Classifier(num_classes=4)│
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  3. torch.load(MODEL_PATH,           │
│     map_location=device,             │
│     weights_only=False)              │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  4. model.load_state_dict(           │
│     ckpt["model_state_dict"])        │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  5. model.to(device).eval()          │
└──────────────────────────────────────┘
```

### Code minimal
```python
import torch, pathlib, sys
if not hasattr(pathlib, "_local"): pathlib._local = pathlib.Path
sys.modules["pathlib._local"] = pathlib

from src.model_architecture import ResNet50Classifier

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model  = ResNet50Classifier(num_classes=4, pretrained=False)
ckpt   = torch.load("models/final_model_20251106_142153.pth",
                    map_location=device, weights_only=False)
model.load_state_dict(ckpt["model_state_dict"])
model.to(device).eval()
```

---

## 🔧 Cross-platform : le patch pathlib

Le checkpoint a été créé sous **Windows** (contient `WindowsPath`). Pour le charger ailleurs :

```python
orig_win, orig_pos = pathlib.WindowsPath, pathlib.PosixPath
try:
    pathlib.WindowsPath = pathlib.PureWindowsPath
    pathlib.PosixPath   = pathlib.PurePosixPath
    ckpt = torch.load(MODEL_PATH, map_location=device)
finally:
    pathlib.WindowsPath = orig_win
    pathlib.PosixPath   = orig_pos
```

→ Déjà appliqué dans `api/app.py` et `streamlit_app/app.py`.

---

## 🆕 Générer un nouveau modèle

```bash
# Étape 1 — préparer les données
venv\Scripts\python.exe scripts\quick_start.py

# Étape 2 — entraîner (~3-4 h GPU)
venv\Scripts\python.exe scripts\train.py

# Étape 3 — évaluer
venv\Scripts\python.exe scripts\evaluate.py
```

Génère :
- `models/final_model_<timestamp>.pth`
- `logs/training_history_<timestamp>.csv`
- `results/{evaluation_summary.txt, ...}`

---

## 🩺 Réparer un checkpoint

```bash
venv\Scripts\python.exe scripts\fix_model.py models\<corrupted>.pth
```

Le script :
1. Tente de re-patcher les `WindowsPath`
2. Valide le state_dict (toutes les couches présentes)
3. Réécrit un checkpoint propre

---

## 💡 Recommandations production

| Stratégie | Bénéfice |
|---|---|
| **Versioning** : conserver chaque `final_model_<ts>.pth` | Rollback possible |
| **Manifest JSON** | Métadonnées sans toucher aux .pth |
| **Validation avant deploy** | `scripts/evaluate.py` puis remplacement |
| **Quantization int8** | Taille ÷4, latence ÷2-3, accuracy −2-3 % |

---

## ⚠️ Pièges courants

| Symptôme | Cause | Solution |
|---|---|---|
| `pathlib._local` AttributeError | Checkpoint Win → Linux | Patch déjà fait dans api/, streamlit/ |
| `RuntimeError: size mismatch` | Architecture différente | Vérifier `num_classes=4` et `dense_units=512` |
| `FileNotFoundError` | Path absolu | Utiliser path relatif depuis racine projet |
| Inférence très lente | CPU | `torch.cuda.is_available()` doit être True |
| `weights_only=True` échec | Checkpoint contient config | Fallback `weights_only=False` (déjà fait) |

---

## 🔗 Liens

- Architecture : [`../src/model_architecture.py`](../src/model_architecture.py)
- Trainer : [`../src/model_trainer.py`](../src/model_trainer.py)
- Script train : [`../scripts/train.py`](../scripts/train.py)
- Script repair : [`../scripts/fix_model.py`](../scripts/fix_model.py)
- Métriques : [`../results/evaluation_summary.txt`](../results/evaluation_summary.txt)
- Logs : [`../logs/`](../logs/)
