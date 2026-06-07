# 📈 results/ — Résultats d'évaluation

> **Tous les artefacts** produits par `scripts/evaluate.py` après le test du modèle final sur 1 054 images.

---

## ⚡ En 30 secondes

| | |
|---|---|
| 🎯 **Rôle** | Documenter la performance officielle du modèle |
| 📊 **Test accuracy** | **98.96 %** (1 043/1 054) |
| 🖼 **Fichiers** | 1 TXT + 1 CSV + 3 PNG |
| 🔄 **Régénérables** | Tous via `scripts/evaluate.py` |

---

## 🗺️ Pipeline de génération

```
  models/final_model_*.pth
            │
            ▼
   scripts/evaluate.py
            │
            ▼
  ┌───────────────────────────────────────────────┐
  │  Inference sur 1054 images du test set       │
  └────────────┬──────────────────────────────────┘
               │
       ┌───────┼───────┬─────────────┬────────────┐
       ▼       ▼       ▼             ▼            ▼
   summary.txt  CSV  matrix.png  perf.png   training_history.png
                                              (via visualize_training.py)
```

---

## 📂 Fichiers

| Fichier                  | Type|    Lignes/Pixels |                    Rôle                  |
|---                       |---  |---               |---                                       |
| `evaluation_summary.txt` | TXT |     ~45          | Résumé ASCII (accuracy, P/R/F1, matrice) |
| `test_results.csv`       | CSV | 1 055 (+ header) | 1 ligne par image testée                 |
| `confusion_matrix.png`   | PNG | ~600×600         | Heatmap 4×4                              |
| `class_performance.png`  | PNG | ~900×500         | Bar chart P/R/F1 par classe              |
| `training_history.png`   | PNG | ~900×400         | Courbes loss/acc 50 époques              |

Tous **committés Git** (taille raisonnable, utiles pour la doc).

---

## 📊 Performance globale

| Métrique          | Valeur               |
|---                |---:                  |
| **Test accuracy** |       **98.96 %**    |
| Total samples     |     1 054            |
| Correct           |      1 043           |
| Errors            |         11           |
| Best val accuracy (training) | 99.34 % |

---

## 📊 Performance par classe

| Classe       | Précision | Rappel  | F1-Score | Support |
|--------------|----------:|--------:|---------:|--------:|
| Glioma       | 99.58 %   | 97.94 % | 98.76 %  | 243     |
| Meningioma   | 97.60 %   | 98.79 % | 98.19 %  | 247     |
| No Tumor     | 99.67 %   | 99.67 % | 99.67 %  | 300     |
| Pituitary    | 98.87 %   | 99.24 % | 99.05 %  | 264     |

---

## 🎯 Matrice de confusion

```
                    Predicted →
                    Gli   Men   Not   Pit
True   Gli   ┃ │   238    4     0     1   │ ← 4 confondus avec meningioma
       Men   ┃ │     1   244    1     1   │
       Not   ┃ │     0     0   299    1   │ ← 1 confondu avec pituitary
       Pit   ┃ │     0     2     0   262  │ ← 2 confondus avec meningioma
```

### Top des confusions
| Vraie classe | Prédite comme | Nombre |
|---|---|:---:|
| Glioma → Meningioma | (visuellement similaires) | **4** |
| Pituitary → Meningioma | | **2** |
| Glioma → Pituitary | | 1 |
| Meningioma → Glioma | | 1 |
| Meningioma → No Tumor | | 1 |
| Meningioma → Pituitary | | 1 |
| No Tumor → Pituitary | | 1 |

→ Confusion principale : **Glioma ↔ Meningioma** (5/11 erreurs).

---

## 📋 test_results.csv — schéma

| Colonne | Type | Description |
|---|---|---|
| `True_Label` | int | 0=glioma, 1=meningioma, 2=notumor, 3=pituitary |
| `Predicted_Label` | int | argmax des probas |
| `Correct` | bool | True si correct |
| `Prob_glioma` | float32 | Probabilité softmax |
| `Prob_meningioma` | float32 | … |
| `Prob_notumor` | float32 | … |
| `Prob_pituitary` | float32 | … |

### Cas d'usage
```python
import pandas as pd
df = pd.read_csv("results/test_results.csv")

# Compter erreurs
errors = df[~df["Correct"]]
print(f"Erreurs: {len(errors)}/{len(df)} = {(1-df.Correct.mean())*100:.2f}%")

# Confiance moyenne
df["max_prob"] = df.iloc[:, 3:].max(axis=1)
print(f"Conf correct: {df[df.Correct].max_prob.mean():.4f}")
print(f"Conf erreur:  {df[~df.Correct].max_prob.mean():.4f}")
```

---

## 🔌 Consommé par

| Outil | Lit quoi ? |
|---|---|
| `dataset_stats/analyses/fig08_confusion_matrix.py` | `test_results.csv` |
| `dataset_stats/analyses/fig09_per_class_metrics.py` | `test_results.csv` |
| `dataset_stats/analyses/fig11_confidence_distribution.py` | `test_results.csv` |
| `dataset_stats/analyses/fig12_misclassification.py` | `test_results.csv` |
| Tests API (`test_health_ok`) | Compare la valeur "98.96%" |
| README principal | Copie les nombres officiels |

---

## 🚀 Régénération

```bash
# Re-évaluer le modèle existant
venv\Scripts\python.exe scripts\evaluate.py

# Régénère :
#   evaluation_summary.txt
#   test_results.csv
#   confusion_matrix.png
#   class_performance.png

# Re-générer training_history.png
venv\Scripts\python.exe scripts\visualize_training.py
```

---

## 🚀 Workflow complet (après nouvel entraînement)

```
1️⃣  scripts\train.py
       │
       ▼  produit models/final_model_<ts>.pth
2️⃣  scripts\evaluate.py
       │
       ▼  produit results/{summary, csv, png}
3️⃣  scripts\visualize_training.py
       │
       ▼  produit results/training_history.png
4️⃣  dataset_stats\run.py
       │
       ▼  produit dataset_stats/outputs/figures/*.png (13 figures)
✅  README + docs cohérents avec les nouveaux résultats
```

---

## ⚠️ Pièges courants

| Symptôme | Cause | Solution |
|---|---|---|
| Nombres dans README ≠ TXT | Modèle changé sans regen | Re-lancer evaluate.py et visualize_training.py |
| Test_results.csv vide | Erreur silencieuse pendant evaluate | Vérifier les logs du script |
| confusion_matrix.png blanche | Matplotlib backend headless | `matplotlib.use("Agg")` (déjà fait) |
| Training_history désynchro | CSV `latest` différent | Vérifier timestamp dans logs/ |

---

## 🎨 Versions enrichies

`dataset_stats/outputs/figures/` contient des versions **plus détaillées** des mêmes figures :

| Figure de base (`results/`) | Version enrichie (`dataset_stats/outputs/figures/`) |
|---|---|
| `confusion_matrix.png` | `08_confusion_matrix.png` (+ recall normalisé) |
| `class_performance.png` | `09_per_class_metrics.png` (annotations) |
| `training_history.png` | `07_training_history.png` (shading + best line) |

---

## 🔗 Liens

- Script générateur : [`../scripts/evaluate.py`](../scripts/evaluate.py)
- Visualisation : [`../scripts/visualize_training.py`](../scripts/visualize_training.py)
- Modèle évalué : [`../models/final_model_20251106_142153.pth`](../models/)
- Données : [`../data/processed/`](../data/processed/)
- Logs : [`../logs/training_history_20251106_142153.csv`](../logs/)
- Figures enrichies : [`../dataset_stats/outputs/figures/`](../dataset_stats/outputs/figures/)
