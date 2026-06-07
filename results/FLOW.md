# 🗺 results/ FLOW — Phase 3 : Évaluation

> Tout ce qui est généré par `scripts/evaluate.py` après le test sur 1054 images.

---

## 🎯 Pipeline d'évaluation

```
1️⃣  python scripts/evaluate.py
        │
        ▼
2️⃣  Charge dernier checkpoint
        │
        ├─ glob("models/final_model_*.pth") → max(mtime)
        ├─ ResNet50Classifier(num_classes=4, pretrained=False)
        ├─ load_state_dict(checkpoint["model_state_dict"])
        ├─ model.to(device) + .eval()
        │
        ▼
3️⃣  Crée test_loader
        │
        ├─ Lit data/splits/split_info.json
        ├─ BrainTumorDataset(test_paths, test_labels)
        └─ DataLoader (no augmentation, just Normalize)
        │
        ▼
4️⃣  Forward pass sans gradient
        │
        ├─ Pour chaque batch :
        │     ├─ outputs = model(images)
        │     ├─ probs = softmax(outputs)
        │     └─ predictions = argmax(probs)
        │
        ├─ Accumule : y_true, y_pred, y_proba
        │
        ▼ (~10 s sur 1054 images)
5️⃣  Calculs sklearn
        │
        ├─ accuracy_score()                     → 0.9896
        ├─ classification_report()               → P/R/F1 par classe
        ├─ confusion_matrix()                    → [4×4]
        └─ accuracy_score normalize="recall"     → recall norm
        │
        ▼
6️⃣  Sauvegarde des outputs
        │
        ├─ results/evaluation_summary.txt
        │     ├─ Accuracy globale
        │     ├─ Classification report formatté
        │     └─ Confusion matrix counts
        │
        ├─ results/test_results.csv             (1054 lignes)
        │     ├─ filename, true_class, predicted_class, confidence
        │     └─ Une ligne par image test
        │
        ├─ results/confusion_matrix.png         (heatmap seaborn)
        │     ├─ Counts (annotated)
        │     ├─ Recall normalized (couleur)
        │     └─ Diagonale = bonnes prédictions
        │
        └─ results/class_performance.png        (bar chart)
              ├─ 4 groupes (1 par classe)
              ├─ 3 barres : Precision / Recall / F1
              └─ Lignes en pointillés à 99%
        │
        ▼
✅ Résultats prêts à analyser
```

---

## 📊 Format `evaluation_summary.txt`

```
╔════════════════════════════════════════════════════════╗
║          MODEL EVALUATION SUMMARY                      ║
╠════════════════════════════════════════════════════════╣

Test Set Size:    1054
Test Accuracy:    98.96%

CLASSIFICATION REPORT
═════════════════════
                  precision    recall  f1-score   support
Glioma                0.99      0.99      0.99       260
Meningioma            0.98      0.98      0.98       257
No Tumor              1.00      1.00      1.00       273
Pituitary             0.99      0.99      0.99       264
─────────────────────────────────────────────────────────
accuracy                                  0.99      1054
macro avg             0.99      0.99      0.99      1054
weighted avg          0.99      0.99      0.99      1054

CONFUSION MATRIX
════════════════
                 Glioma  Meningioma  No Tumor  Pituitary
Glioma             257           2         0          1
Meningioma           3         252         0          2
No Tumor             0           1       272          0
Pituitary            1           1         0        262
```

---

## 📊 Format `test_results.csv`

```
filename,true_class,predicted_class,confidence,prob_glioma,prob_meningioma,prob_notumor,prob_pituitary
Te-gl_0001.npy,glioma,glioma,0.9985,0.9985,0.0010,0.0003,0.0002
Te-gl_0002.npy,glioma,glioma,0.9921,0.9921,0.0050,0.0021,0.0008
...
Te-pi_0264.npy,pituitary,pituitary,0.9912,0.0012,0.0034,0.0042,0.9912
```

→ 1054 lignes (une par image de test).

---

## 🔌 Consommation par dataset_stats/

```
results/test_results.csv
        │
        ├──► fig08_confusion_matrix.py        Matrice 4×4
        ├──► fig09_per_class_metrics.py        P/R/F1
        ├──► fig11_confidence_distribution.py  Boxplot conf vs erreur
        ├──► fig12_misclassification.py        Top patterns d'erreur
        ├──► fig14_roc_curves.py                ROC + AUC par classe
        ├──► fig15_pr_curves.py                 PR + AP par classe
        ├──► fig16_calibration.py               Reliability + Brier
        ├──► fig18_top_predictions.py           Top-K accuracy
        └──► fig22_class_focus_confusion.py     4 mini-matrices "1 vs rest"
        │
        ▼
9 figures dérivées dans dataset_stats/outputs/figures/
```

---

## 🛠 Régénérer

```bash
# Si tu re-entraînes le modèle, regénère :
venv\Scripts\python.exe scripts\evaluate.py
        │
        └─ Re-écrit tous les fichiers results/ avec le nouveau modèle

# Puis regénère les figures dérivées :
venv\Scripts\python.exe dataset_stats\run.py --category evaluation
venv\Scripts\python.exe dataset_stats\run.py --category errors
```

---

## 📁 Fichiers générés

| Fichier | Format | Taille | Source |
|---|---|---|---|
| `evaluation_summary.txt` | Texte plain | ~1 KB | `evaluate.py` |
| `test_results.csv` | CSV | ~62 KB | `evaluate.py` |
| `confusion_matrix.png` | PNG 150 DPI | ~117 KB | `evaluate.py` |
| `class_performance.png` | PNG 150 DPI | ~99 KB | `evaluate.py` |
| `training_history.png` | PNG 150 DPI | ~645 KB | `visualize_training.py` |

---

> Voir [`README.md`](README.md) pour les conventions et l'analyse détaillée des résultats.
