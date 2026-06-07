# 🛠 scripts/ — Scripts CLI utilisateur

> **Les commandes terminales** : entraîner, évaluer, prédire, réparer.

---

## ⚡ En 30 secondes

| | |
|---|---|
| 🎯 **Rôle** | Entry points CLI pour utilisateur final |
| 📁 **Lancement** | Toujours **depuis la racine du projet** |
| 🐍 **Format** | Scripts Python autonomes (`if __name__ == "__main__"`) |
| 🔌 **Importent** | Modules de `../src/` |

---

## 🗺️ Quel script lancer ?

```
┌────────────────────────────────────────────┐
│  Quel est votre objectif ?                 │
└──────────────────────┬─────────────────────┘
                       │
   ┌───────────────────┼────────────────────────┐
   │                   │                        │
   ▼                   ▼                        ▼
"Préparer        "Entraîner            "Voir les
 dataset"         un modèle"            résultats"
   │                   │                        │
   ▼                   ▼                        ▼
quick_start.py    train.py              evaluate.py
                  quick_train.py
                                   ┌────────────┴────────────┐
                                   ▼                         ▼
                              "Tester sur          "Visualiser
                               1 image"             courbes"
                                   │                         │
                                   ▼                         ▼
                              predict.py            visualize_training.py

   ┌────────────────────────────┐
   ▼                            ▼
"Checkpoint cassé"     "Tutoriel pas-à-pas"
   │                            │
   ▼                            ▼
fix_model.py           quick_train.py
```

---

## 📂 Inventaire

| Script | Phase | Durée | Sortie |
|---|---|---|---|
| `quick_start.py` | Phase 1 — préparation | ~5 min | `data/processed/` + `data/splits/` |
| `train.py` | Phase 2 — entraînement | ~30 min GPU / 4-6 h CPU | `models/final_model_*.pth` + `logs/` |
| `quick_train.py` | Phase 2 — guide pédagogique | ~30 min GPU | Idem train.py |
| `evaluate.py` | Phase 3 — évaluation | ~30 s | `results/*.{txt,csv,png}` |
| `predict.py` | Inférence single image | ~1 s | Console + visu matplotlib |
| `visualize_training.py` | Post-entraînement | ~2 s | `results/training_history.png` |
| `fix_model.py` | Maintenance | ~5 s | `.pth` réparé |

---

## 🚀 Pipeline projet complet

```
1️⃣  python scripts/quick_start.py
        │
        │  • Lit data/raw/{Training,Testing}/
        │  • Resize → normalize → save .npy
        │  • Crée data/splits/split_info.json
        ▼

2️⃣  python scripts/train.py
        │
        │  • 50 époques (Stage 1 : 20 + Stage 2 : 30)
        │  • Save models/final_model_<timestamp>.pth
        │  • Save logs/training_history_<timestamp>.csv
        ▼

3️⃣  python scripts/evaluate.py
        │
        │  • Inference sur 1054 images test
        │  • Génère results/evaluation_summary.txt
        │  • Génère results/test_results.csv
        │  • Génère results/{confusion_matrix,class_performance}.png
        ▼

4️⃣  python scripts/visualize_training.py
        │
        │  • Lit logs/training_history_*.csv
        │  • Génère results/training_history.png
        ▼

5️⃣  python scripts/predict.py --image data/processed/glioma/Te-gl_0010.npy
        │
        │  • Charge modèle final
        │  • Prédiction + probabilités
        ▼

   ✅ Pipeline terminé
```

---

## ⚙️ Détail des E/S

### `train.py`
```
ENTRÉE                          SORTIE
──────                          ──────
data/processed/    ──┐
data/splits/       ──┼──► train.py ──► models/final_model_<ts>.pth
src/model_*.py     ──┘                  logs/training_history_<ts>.csv
                                        logs/stage{1,2}_<ts>/  (TensorBoard)
```

| Étapes internes | Rôle |
|---|---|
| 1 | Détecte GPU/CPU (`torch.cuda.is_available()`) |
| 2 | Crée modèle via `create_model(num_classes=4, freeze_base=True)` |
| 3 | Crée DataLoaders via `create_data_loaders()` |
| 4 | Instancie `PyTorchTrainer(...)` |
| 5 | Lance `train_two_stages(stage1=20, stage2=30)` |
| 6 | Sauve checkpoint final + historique CSV |

### `evaluate.py`
```
ENTRÉE                              SORTIE
──────                              ──────
models/final_model_<ts>.pth   ──┐
data/processed/               ──┼──► results/evaluation_summary.txt
data/splits/test              ──┘    results/test_results.csv
                                     results/confusion_matrix.png
                                     results/class_performance.png
```

### `predict.py --image PATH`
```
ENTRÉE                  SORTIE
──────                  ──────
PATH (jpg/png/npy) ──► console (top class + probas)
                       (optionnel) matplotlib visualization
```

Sortie typique :
```
============================================================
   PREDICTION RESULT
============================================================
   Image: mri_test.jpg
   Predicted: Glioma
   Confidence: 99.79%

   All probabilities:
     - Glioma:     99.79%
     - Meningioma:  0.18%
     - No Tumor:    0.02%
     - Pituitary:   0.01%
============================================================
```

### `visualize_training.py`
Layout 2×2 produit :
```
┌─────────────────────────────┬─────────────────────────────┐
│  Loss curve (line)          │  Accuracy curve (line)      │
│  - train_loss               │  - train_acc                │
│  - val_loss                 │  - val_acc                  │
│  Vertical bars Stage1↔Stage2│  Vertical bars Stage1↔Stage2│
├─────────────────────────────┼─────────────────────────────┤
│  Loss scatter               │  Accuracy scatter           │
│  Stage 1 vs Stage 2         │  Stage 1 vs Stage 2         │
└─────────────────────────────┴─────────────────────────────┘
```

Permet de **diagnostiquer** :

| Symptôme visuel | Diagnostic |
|---|---|
| `train_loss << val_loss` | Overfitting |
| Les 2 plateau hauts | Underfitting |
| `val_acc` s'effondre début Stage 2 | Catastrophic forgetting |
| Oscillations de la loss | LR mal réglé |

### `fix_model.py`

Répare un checkpoint Windows ↔ Linux via `PathedUnpickler` custom :
```python
class PathedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == 'pathlib._local':
            module = 'pathlib'
            name = 'Path'
        return super().find_class(module, name)
```

→ En pratique rarement nécessaire (patch fait à la volée dans `api/app.py`).

---

## 🧪 Cheat sheet

```bash
# Préparation des données (1 fois)
venv\Scripts\python.exe scripts\quick_start.py

# Entraînement complet
venv\Scripts\python.exe scripts\train.py

# Évaluation
venv\Scripts\python.exe scripts\evaluate.py

# Visualisation courbes
venv\Scripts\python.exe scripts\visualize_training.py

# Prédiction sur une image
venv\Scripts\python.exe scripts\predict.py --image path\to\mri.jpg

# Réparation checkpoint
venv\Scripts\python.exe scripts\fix_model.py
```

---

## 🆚 train.py vs quick_train.py

| Critère | `train.py` | `quick_train.py` |
|---|---|---|
| **Public** | Power users | Débutants / pédagogie |
| **Configuration** | Code/CLI | Interactive (input prompts) |
| **Output** | Identique | Identique |
| **Recommandé pour** | Reproduire publication | Premier run |

---

## 🔌 Comment chaque script trouve `src/`

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))
from model_architecture import ResNet50Classifier
```

→ Permet d'**exécuter depuis n'importe où** : `python scripts/train.py` ou un path absolu fonctionnent.

---

## ⚠️ Pièges courants

| Symptôme | Cause | Solution |
|---|---|---|
| `FileNotFoundError: data/processed/` | Données pas préparées | `python scripts/quick_start.py` d'abord |
| `Model loading failed pathlib._local` | Checkpoint Win ↔ Linux | `python scripts/fix_model.py <fichier>` |
| `CUDA out of memory` | Batch size trop grand | Modifier `batch_size` dans `get_default_config()` |
| Train très lent | CPU only détecté | Vérifier `torch.cuda.is_available()` |
| Mauvais checkpoint utilisé | Plusieurs `.pth` | Vérifier le timestamp |
| `ModuleNotFoundError: model_architecture` | sys.path mal calculé | Ne pas déplacer le script hors de `scripts/` |

---

## 🔗 Liens

- Modules importés : [`../src/`](../src/)
- Configuration : [`../src/model_trainer.py`](../src/model_trainer.py) `get_default_config()`
- Données : [`../data/`](../data/)
- Modèles : [`../models/`](../models/)
- Résultats : [`../results/`](../results/)
- Logs : [`../logs/`](../logs/)
- API alternative : [`../api/`](../api/)
