# 🗺 src/ FLOW — Pipeline d'entraînement complet

> Du module importé au checkpoint final, les étapes du `PyTorchTrainer.train_two_stages()`.

---

## 🏋 Pipeline d'entraînement (consommé par scripts/train.py)

```
1️⃣  scripts/train.py
        │
        ▼
2️⃣  sys.path.insert(0, "src/")
        │
        ▼
3️⃣  from model_architecture import create_model
    from model_trainer    import PyTorchTrainer, get_default_config
    from data_loaders     import create_data_loaders
        │
        ▼
4️⃣  config = get_default_config()
        │
        ├─ batch_size=24, lr_s1=1e-3, lr_s2=1e-4
        ├─ epochs_s1=20, epochs_s2=30
        └─ dropout=0.4, weight_decay=1e-4
        │
        ▼
5️⃣  model = create_model(num_classes=4, freeze_base=True)
        ├─ ResNet50(weights=ImageNet1K_V1)
        ├─ base_model.fc = Identity()
        ├─ classifier = Sequential(Linear→ReLU→BN→Dropout→Linear)
        └─ freeze_base_layers()  ← all base params frozen
        │
        ▼
6️⃣  loaders = create_data_loaders(batch_size=24)
        │
        ├─ Lit data/splits/split_info.json
        ├─ BrainTumorDataset wrappe les .npy
        ├─ Albumentations augmentation pour train :
        │     ├─ HorizontalFlip(p=0.5)
        │     ├─ RandomRotate90(p=0.3)
        │     ├─ RandomBrightnessContrast(p=0.4)
        │     ├─ GaussianBlur(p=0.2)
        │     └─ ElasticTransform(p=0.2)
        ├─ Val/test : seulement Normalize
        └─ DataLoader avec class_weights pour imbalance
        │
        ▼
7️⃣  trainer = PyTorchTrainer(model, loaders, config, device)
        │
        ▼
8️⃣  trainer.train_two_stages()
        │
        ├──── STAGE 1 (20 epochs · LR 1e-3) ────────────────────┐
        │                                                        │
        │   for epoch in range(20):                              │
        │       train_epoch()  ← forward + backward + step       │
        │       val_epoch()    ← evaluate sans gradient          │
        │       Log to logs/training_history_<ts>.csv            │
        │       Log to TensorBoard logs/stage1_<ts>/             │
        │       if val_loss < best:                              │
        │           save_checkpoint("models/best_stage1.pth")    │
        │       ReduceLROnPlateau.step(val_loss)                 │
        │       EarlyStopping check (patience=7)                 │
        │                                                        │
        ├────────────────────────────────────────────────────────┘
        │
        ├──── TRANSITION ─────────────────────────────────────┐
        │   model.unfreeze_base_layers(num_layers=30)         │
        │   optimizer = Adam(trainable_params, lr=1e-4)       │
        ├──────────────────────────────────────────────────────┘
        │
        ├──── STAGE 2 (30 epochs · LR 1e-4) ────────────────────┐
        │                                                        │
        │   Idem boucle Stage 1, mais :                          │
        │   - 15M params trainable (head + last 30 layers)       │
        │   - LR 10× plus petit pour fine-tuning                 │
        │                                                        │
        ├────────────────────────────────────────────────────────┘
        │
        ▼
9️⃣  Save final
        ├─ models/final_model_<ts>.pth (95 MB)
        │     └─ {model_state_dict, epoch, val_loss, val_acc, config}
        ├─ logs/training_history_<ts>.csv (50 lignes : epoch, train_loss, val_loss, ...)
        └─ logs/stage{1,2}_<ts>/ (TensorBoard event files)
        │
        ▼
✅ Modèle prêt — accuracy attendue ~98.96 % sur test set
```

---

## 🧬 Architecture modulaire (graphe de dépendances)

```
            ┌──────────────────────────────────┐
            │  data_preprocessing.py           │  validate, resize, normalize
            └─────────────┬────────────────────┘
                          │
            ┌─────────────▼────────────────────┐
            │  dataset_split.py                │  stratified split
            └─────────────┬────────────────────┘
                          │
            ┌─────────────▼────────────────────┐
            │  data_pipeline.py                │  orchestrateur
            └─────────────┬────────────────────┘
                          │ produit data/splits/split_info.json
                          ▼
            ┌──────────────────────────────────┐
            │  data_loaders.py                 │  DataLoader + Albumentations
            └─────────────┬────────────────────┘
                          │
            ┌─────────────▼────────────────────┐  ┌─────────────────────────┐
            │  model_architecture.py           │  │  model_trainer.py       │
            │  ResNet50Classifier              │──│  PyTorchTrainer (2 stg) │
            └──────────────────────────────────┘  └─────────────┬───────────┘
                                                                │
                                                                ▼
                                                     models/final_model_*.pth
```

---

## 📁 Fichiers

| Fichier | Lignes | Imports clés |
|---|---:|---|
| `model_architecture.py` | ~240 | `ResNet50Classifier`, `create_model` |
| `model_trainer.py` | ~370 | `PyTorchTrainer`, `get_default_config` |
| `data_loaders.py` | ~210 | `create_data_loaders`, `BrainTumorDataset` |
| `data_preprocessing.py` | ~170 | `DataPreprocessor` |
| `dataset_split.py` | ~120 | `create_stratified_split` |
| `data_pipeline.py` | ~150 | `run_pipeline` |
| `train_model.py` | ~180 | CLI legacy avancée |

---

> Voir [`README.md`](README.md) pour le détail de chaque module et l'API publique.
