# 🗺 models/ FLOW — Vie d'un checkpoint

> Du `train.py` qui sauvegarde, jusqu'à l'API qui charge en production.

---

## 💾 Pipeline d'un checkpoint

```
1️⃣  Entraînement (Phase 2)
        │
        └─ scripts/train.py
              │
              ├─ PyTorchTrainer.train_two_stages()
              │
              ├─ Stage 1 : 20 epochs frozen base
              │     └─ Save sur best val_loss → models/best_stage1.pth
              │
              ├─ Stage 2 : 30 epochs unfreeze 30
              │     └─ Save sur best val_loss → models/best_stage2.pth
              │
              └─ Final save :
                    │
                    ▼
                    torch.save({
                        "model_state_dict":  model.state_dict(),
                        "epoch":             best_epoch,
                        "val_loss":          best_val_loss,
                        "val_acc":           best_val_acc,
                        "config":            training_config,
                    }, "models/final_model_<timestamp>.pth")
        │
        ▼
2️⃣  Le checkpoint contient :
        │
        ├─ model_state_dict  : ~95 MB (les poids ResNet50)
        ├─ epoch             : int   (numéro de l'époque finale)
        ├─ val_loss          : float (meilleure loss validation)
        ├─ val_acc           : float (meilleure accuracy validation)
        └─ config            : dict  (tous les hyperparamètres)
        │
        ▼
3️⃣  Format binaire PyTorch (.pth)
        │
        ├─ Pickle interne avec pathlib resolution
        ├─ ⚠ ATTENTION : pathlib._local objects (bug Windows ↔ Linux)
        └─ Patch automatique appliqué par api/app.py au chargement
        │
        ▼
✅ Checkpoint prêt à servir
```

---

## 🔌 Pipeline de chargement (consommé par api/streamlit/scripts)

```
1️⃣  api/app.py @lifespan startup
        │
        ▼
2️⃣  Patch pathlib._local (cross-OS portability)
        │
        ├─ pathlib.WindowsPath = PureWindowsPath  (temporaire)
        └─ pathlib.PosixPath   = PurePosixPath
        │
        ▼
3️⃣  Création modèle vide
        │
        └─ model = ResNet50Classifier(num_classes=4, pretrained=False)
        │     ↑ pretrained=False → on n'a pas besoin des poids ImageNet,
        │       on va les écraser avec notre checkpoint
        │
        ▼
4️⃣  Chargement du checkpoint
        │
        ├─ try torch.load(MODEL_PATH, weights_only=True, mmap=True)
        │     ↑ weights_only=True : sécurité (pas de code arbitraire)
        │     ↑ mmap=True : moins de RAM utilisée (memory-mapped)
        │
        ├─ except → torch.load(..., weights_only=False, mmap=True)
        │
        └─ except → torch.load(..., weights_only=False)
        │
        ▼
5️⃣  Extraction du state_dict
        │
        ├─ if "model_state_dict" in checkpoint :
        │       state = checkpoint["model_state_dict"]
        │
        └─ else : state = checkpoint   (cas legacy ou direct state_dict)
        │
        ▼
6️⃣  Restauration des poids
        │
        ├─ model.load_state_dict(state)
        ├─ model.to(device)        (GPU si dispo, sinon CPU)
        └─ model.eval()             (désactive dropout/BN tracking)
        │
        ▼
7️⃣  Stockage en singleton global
        │
        └─ predictor = model
        │
        ▼
✅ Modèle prêt à servir des requêtes
   (chargé UNE seule fois, partagé pour toute la durée de vie de l'API)
```

---

## 📊 Caractéristiques du checkpoint actuel

| Aspect | Valeur |
|---|---|
| **Fichier** | `final_model_20251106_142153.pth` |
| **Taille** | ~95 MB |
| **Architecture** | ResNet50Classifier (PyTorch) |
| **Paramètres totaux** | ~24.6M |
| **Test accuracy** | 98.96 % (1043/1054) |
| **Date d'entraînement** | 6 novembre 2025 |
| **Stage 1 epochs** | 20 (LR=1e-3) |
| **Stage 2 epochs** | 30 (LR=1e-4, unfreeze last 30) |
| **Augmentation** | Albumentations (8 transformations) |
| **Optimizer** | Adam |
| **Loss** | CrossEntropyLoss + class weights |

---

## 🛠 Utilisation par les autres composants

```
api/app.py               ──► load au lifespan startup (singleton)
streamlit_app/app.py     ──► load via @st.cache_resource (singleton)
scripts/predict.py       ──► load à chaque appel CLI (1×)
scripts/evaluate.py      ──► load une fois pour évaluer test set
tests/test_api.py        ──► load via TestClient lifespan (1×)
```

---

## 🔧 Maintenance

```
Checkpoint cassé Windows ↔ Linux ?
        │
        ▼
python scripts/fix_model.py
        │
        ├─ PathedUnpickler custom remplace pathlib._local → pathlib
        └─ Re-sauvegarde un .pth propre cross-OS
```

```
Réduire la taille du checkpoint ?
        │
        ▼
Quantization (post-training) :
        │
        ├─ torch.quantization.quantize_dynamic()
        ├─ Réduit ~95 MB → ~25 MB (4× plus petit)
        └─ ⚠ Risque de perte d'accuracy (~0.5-1%)
        │
        Non implémenté actuellement (compromise non désiré)
```

---

> Voir [`README.md`](README.md) pour les conventions de nommage et la stratégie de sauvegarde.
