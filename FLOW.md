# 🗺️ FLOW — BrainScan AI · Vue d'ensemble

> **Le projet en un seul flow** : du dataset Kaggle au déploiement en production, les étapes clés.

---

## 🚀 Pipeline de bout en bout

```
   📥 INSTALLATION
   ──────────────
   pip install -r requirements.txt
              │
              ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │  PHASE 1 — Préparation des données                              │
   │  (~5 min)                                                       │
   │                                                                 │
   │  Kaggle dataset (raw JPG/PNG, 4 GB)                            │
   │      │                                                          │
   │      ▼                                                          │
   │  data_pipeline.py orchestre :                                  │
   │     ├─ validate (images corrompues ?)                           │
   │     ├─ resize 256 → CenterCrop 224                             │
   │     ├─ convert RGB                                             │
   │     ├─ normalize ImageNet [0,1] float32                        │
   │     ├─ save .npy → data/processed/{class}/                     │
   │     ├─ stratified split 70/15/15 (seed 42)                     │
   │     └─ write data/splits/split_info.json                       │
   └────────────────────────────┬────────────────────────────────────┘
                                ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │  PHASE 2 — Entraînement (Transfer Learning 2 stages)            │
   │  (~30 min GPU / 4-6 h CPU)                                      │
   │                                                                 │
   │  scripts/train.py                                              │
   │      │                                                          │
   │      ▼                                                          │
   │  ResNet50 (ImageNet) + tête custom (2048→512→4)                │
   │      │                                                          │
   │      ▼                                                          │
   │  Stage 1 : 20 époques · LR 1e-3 · base FROZEN                  │
   │      ├─ Albumentations augmentation                             │
   │      ├─ Adam (head only, ~1M params)                            │
   │      └─ ReduceLROnPlateau                                       │
   │      ▼                                                          │
   │  Stage 2 : 30 époques · LR 1e-4 · UNFREEZE 30 last layers      │
   │      ├─ Adam (head + last 30 layers, ~15M params)               │
   │      └─ ReduceLROnPlateau                                       │
   │      ▼                                                          │
   │  Outputs:                                                       │
   │     ├─ models/final_model_<ts>.pth (95 MB)                     │
   │     ├─ logs/training_history_<ts>.csv                          │
   │     └─ logs/stage{1,2}_<ts>/ (TensorBoard)                     │
   └────────────────────────────┬────────────────────────────────────┘
                                ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │  PHASE 3 — Évaluation                                           │
   │  (~30 s)                                                        │
   │                                                                 │
   │  scripts/evaluate.py                                           │
   │      │                                                          │
   │      ▼                                                          │
   │  Forward pass sur 1 054 test images                            │
   │     ├─ Confusion matrix + classification report                 │
   │     ├─ Per-image predictions CSV                                │
   │     └─ Per-class P/R/F1 metrics                                 │
   │      ▼                                                          │
   │  Outputs:                                                       │
   │     ├─ results/evaluation_summary.txt                          │
   │     ├─ results/test_results.csv                                │
   │     ├─ results/confusion_matrix.png                            │
   │     └─ results/class_performance.png                           │
   │                                                                 │
   │  ✅ Test accuracy : 98.96 % (1043/1054 correct)                 │
   └────────────────────────────┬────────────────────────────────────┘
                                ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │  PHASE 4 — Statistiques & Figures                               │
   │  (~20 s pour les 22 analyses)                                   │
   │                                                                 │
   │  python dataset_stats/run.py                                   │
   │      │                                                          │
   │      ▼                                                          │
   │  registry.discover() → 22 analyses fig*.py                     │
   │      ▼                                                          │
   │  for each analysis :                                            │
   │     ├─ check REQUIRES (data/logs/results)                       │
   │     ├─ set_current_category(cat)                                │
   │     ├─ run() → matplotlib figure                                │
   │     ├─ save_figure → outputs/figures/<cat>/XX_*.png            │
   │     └─ save_data → outputs/data/<cat>/XX_*.json                │
   │      ▼                                                          │
   │  outputs/                                                       │
   │     ├─ figures/{overview,image,training,evaluation,errors}/    │
   │     ├─ data/{idem}/                                             │
   │     └─ summary.json                                             │
   └────────────────────────────┬────────────────────────────────────┘
                                ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │  PHASE 5 — Déploiement                                          │
   │  (1 commande)                                                   │
   │                                                                 │
   │  python start.py    OR    docker compose up                    │
   │      │                                                          │
   │      ▼                                                          │
   │  ┌────────────────┐         ┌────────────────┐                 │
   │  │  api/          │  REST   │  interface/    │                 │
   │  │  FastAPI       │ ◄────── │  Vanilla JS    │                 │
   │  │  port 8000     │         │  port 3000     │                 │
   │  └────────┬───────┘         └────────────────┘                 │
   │           │                                                     │
   │  charge   ▼                                                     │
   │  models/final_model_*.pth (singleton)                          │
   │           │                                                     │
   │  servir   ▼                                                     │
   │     ├─ /health    statut + métadonnées                          │
   │     ├─ /predict   image → classe + Grad-CAM (LRU MD5 cache)    │
   │     ├─ /random    image dataset aléatoire                       │
   │     ├─ /explain   infos médicales                               │
   │     ├─ /sample    image d'exemple                               │
   │     ├─ /batch     jusqu'à 20 images                            │
   │     └─ /stats     stats de session                              │
   │                                                                 │
   │  Sécurité : CORS · slowapi rate limit · API key optionnelle    │
   └────────────────────────────┬────────────────────────────────────┘
                                ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │  PHASE 6 — Vérification continue                                │
   │                                                                 │
   │  Tests :     pytest tests/        →  17/17 ✅                   │
   │  Lint :      ruff + black         →  CI GitHub Actions          │
   │  Pre-commit: hooks Git pré-push                                 │
   │  Docker :    multi-stage non-root                               │
   └─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Quel dossier pour quel besoin ?

| Question | Dossier | FLOW associé |
|---|---|---|
| Préparer les données ? | `data/` | [data/FLOW.md](data/FLOW.md) |
| Entraîner le modèle ? | `scripts/` + `src/` | [scripts/FLOW.md](scripts/FLOW.md) |
| Servir l'API ? | `api/` | [api/FLOW.md](api/FLOW.md) |
| Interface web ? | `interface/` | [interface/FLOW.md](interface/FLOW.md) |
| Démo rapide ? | `streamlit_app/` | [streamlit_app/FLOW.md](streamlit_app/FLOW.md) |
| Générer figures ? | `dataset_stats/` | [dataset_stats/FLOW.md](dataset_stats/FLOW.md) |
| Tester ? | `tests/` | [tests/FLOW.md](tests/FLOW.md) |
| CI/CD ? | `.github/` | [.github/FLOW.md](.github/FLOW.md) |
| Code archivé ? | `legacy/` | [legacy/FLOW.md](legacy/FLOW.md) |

---

> Pour les détails complets, voir [`README.md`](README.md). Chaque dossier dispose de son propre `README.md` + `FLOW.md`.
