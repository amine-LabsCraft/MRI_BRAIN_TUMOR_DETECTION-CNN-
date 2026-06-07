# 🗺 scripts/ FLOW — Pipeline projet de bout en bout

> Les 3 phases historiques du projet (data → train → eval), enchaînées par les scripts CLI.

---

## 🚀 Pipeline complet (en 5 commandes)

```
1️⃣  pip install -r requirements.txt
        │
        ▼
2️⃣  python scripts/quick_start.py        ← PHASE 1 : Préparation
        │
        ├─ Vérifie data/raw/{Traning,Testing}/
        ├─ Affiche commande pour data_pipeline
        └─ Suggère : python -m src.data_pipeline
        │
        ▼ (lance ensuite manuellement le pipeline)
        │
        ├─ Resize 256 → CenterCrop 224
        ├─ Normalize ImageNet [0,1] float32
        ├─ Save .npy → data/processed/{class}/
        ├─ Stratified split 70/15/15 (seed 42)
        └─ Write data/splits/split_info.json
        │
        ▼
3️⃣  python scripts/train.py              ← PHASE 2 : Entraînement
        │
        ├─ Détecte GPU/CPU
        ├─ create_model(freeze_base=True)
        ├─ create_data_loaders(batch_size=24)
        ├─ PyTorchTrainer.train_two_stages()
        │     ├─ Stage 1 : 20 epochs · base frozen · LR=1e-3
        │     └─ Stage 2 : 30 epochs · unfreeze 30 last · LR=1e-4
        │
        └─ OUTPUT :
              ├─ models/final_model_<ts>.pth (95 MB)
              ├─ logs/training_history_<ts>.csv
              └─ logs/stage{1,2}_<ts>/ (TensorBoard)
        │
        ▼ (~30 min GPU / 4-6 h CPU)
        │
        ▼
4️⃣  python scripts/visualize_training.py ← Vérification courbes
        │
        ├─ Lit logs/training_history_*.csv
        ├─ Génère grille 2×2 :
        │     ├─ Loss curve (train/val)
        │     ├─ Accuracy curve (train/val)
        │     ├─ Loss scatter Stage 1 vs 2
        │     └─ Accuracy scatter Stage 1 vs 2
        └─ Output : results/training_history.png
        │
        ▼
5️⃣  python scripts/evaluate.py           ← PHASE 3 : Évaluation
        │
        ├─ Charge dernier checkpoint dans models/
        ├─ Forward sur 1054 images test
        ├─ classification_report + confusion_matrix
        │
        └─ OUTPUT :
              ├─ results/evaluation_summary.txt
              ├─ results/test_results.csv (par image)
              ├─ results/confusion_matrix.png
              └─ results/class_performance.png
        │
        ▼
✅ Test accuracy : 98.96 % (1043/1054 corrects)
        │
        ▼
6️⃣  python scripts/predict.py --image path/to/mri.jpg   ← Inférence ad-hoc
        │
        └─ Console output :
           ============================================================
              PREDICTION RESULT
           ============================================================
              Image: mri.jpg
              Predicted: Glioma
              Confidence: 99.79%
              All probabilities:
                - Glioma:     99.79%
                - Meningioma:  0.18%
                - No Tumor:    0.02%
                - Pituitary:   0.01%
           ============================================================
```

---

## 🛠 Maintenance — `fix_model.py`

```
fix_model.py
    │
    └─ Usage rare : checkpoint .pth Windows ↔ Linux
        │
        ├─ PathedUnpickler custom remplace pathlib._local → pathlib
        ├─ Re-sauvegarde le checkpoint patché
        └─ Output : models/<name>_fixed.pth
        │
    Note : le patch est aussi appliqué inline dans api/app.py.
    En pratique on n'a presque jamais besoin de ce script.
```

---

## 🆚 train.py vs quick_train.py vs train_model.py

```
quick_start.py           ──►  Guide pédagogique Phase 1 (no execution)
quick_train.py           ──►  Guide pédagogique Phase 2 + suggestions

train.py                 ──►  Wrapper minimal (defaults raisonnables)
                              4 lignes : create_model + loaders + trainer + train

src/train_model.py       ──►  CLI complet avec argparse (avancé)
                              --epochs-stage1 --batch-size --lr-stage1 ...
```

---

## 📁 Inventaire

| Script | Phase | Durée | Output principal |
|---|---|---|---|
| `quick_start.py` | 1 | <1 s | (guide) |
| `train.py` | 2 | 30 min GPU | `models/final_model_*.pth` |
| `quick_train.py` | 2 | 30 min GPU | (guide → train.py) |
| `evaluate.py` | 3 | ~30 s | `results/*.{txt,csv,png}` |
| `predict.py` | inférence | ~1 s | console |
| `visualize_training.py` | post-train | ~2 s | `results/training_history.png` |
| `fix_model.py` | maintenance | ~5 s | checkpoint patché |

---

> Voir [`README.md`](README.md) pour les détails de chaque script et leurs E/S.
