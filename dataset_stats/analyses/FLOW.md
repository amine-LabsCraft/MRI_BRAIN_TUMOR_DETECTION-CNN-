# 🗺 analyses/ FLOW — Vie d'une analyse

> De la création du fichier `figXX_*.py` à la figure PNG finale, voici les étapes.

---

## ➕ Étapes pour créer une nouvelle analyse

```
1️⃣  Créer le fichier
        │
        └─ analyses/figXX_my_analysis.py
        │
        ▼
2️⃣  Déclarer les 6 metadata + run()
        │
        ├─ NAME        = "XX_my_analysis"
        ├─ TITLE       = "My analysis"
        ├─ DESCRIPTION = "..."
        ├─ CATEGORY    = "image"   ← overview|image|training|evaluation|errors
        ├─ REQUIRES    = ["data"]   ← data|logs|results
        ├─ ORDER       = XX
        └─ def run() -> dict: ...
        │
        ▼
3️⃣  Importer depuis core
        │
        ├─ CLASSES, CLASS_COLORS, CLASS_LABELS  ← config
        ├─ list_class_files, load_npy            ← data
        └─ save_figure                            ← plotting
        │
        ▼
4️⃣  Coder la logique dans run() :
        │
        ├─ Charger données
        ├─ Calculs (numpy, pandas, sklearn)
        ├─ matplotlib plot
        ├─ save_figure(fig, NAME)
        └─ return {"metric": value}
        │
        ▼
5️⃣  Test
        │
        ├─ python dataset_stats/run.py --list   ← l'analyse apparaît auto
        └─ python dataset_stats/run.py --only XX
        │
        ▼
✅ Output : outputs/figures/<CATEGORY>/XX_*.png + outputs/data/<CATEGORY>/XX_*.json
```

---

## 🎬 Pipeline d'exécution d'une analyse (côté registry)

```
run_one(RegisteredAnalysis(name="XX_my_analysis", ...))
        │
        ▼
1️⃣  is_runnable(REQUIRES) ?
        │
        ├─ Si "data" → DATA_DIR exists ?
        ├─ Si "logs" → training_history_*.csv exists ?
        └─ Si "results" → test_results.csv exists ?
        │
        ├─ Manque ? → [skip] log + return None
        │
        ▼
2️⃣  set_current_category(item.category)   ← context global
        │
        ▼
3️⃣  data = item.run()
        │
        │  Inside run() :
        │  ├─ files = list_class_files("glioma")          [from data]
        │  ├─ imgs  = [load_npy(f) for f in files]         [from data]
        │  ├─ stats = compute_stats(imgs)                  (custom)
        │  ├─ fig, ax = plt.subplots(...)
        │  ├─ ax.bar(..., color=CLASS_COLORS["glioma"])    [from config]
        │  ├─ save_figure(fig, NAME)                       [from plotting]
        │  │     └─ écrit dans outputs/figures/<cat>/XX_*.png
        │  └─ return {"my_metric": 42, "stats": stats}
        │
        ▼
4️⃣  set_current_category(None)   (finally)
        │
        ▼
5️⃣  save_data(NAME, {
            "title": item.title,
            "category": item.category,
            "elapsed_sec": elapsed,
            "data": data,
        }, category=item.category)
        │
        └─ écrit dans outputs/data/<cat>/XX_*.json
        │
        ▼
✅ Analyse exécutée + figure + JSON
```

---

## 📋 Catalogue des 22 analyses (par catégorie)

```
🌐 OVERVIEW (2)
   01_class_distribution         Bar + pie chart par classe
   02_split_distribution         Stratified train/val/test 70/15/15

🖼  IMAGE (9)
   03_pixel_statistics           Mean/std/min/max par classe
   04_image_properties           Carte info (sizes, channels, dtype)
   05_sample_grid                Grille 5 exemples par classe
   06_augmentation_examples      Original vs 7 transformations
   10_intensity_histograms       Distribution intensité (overlay+KDE)
   17_mean_image                 Image moyenne pixel-wise par classe
   19_channel_stats              Mean/std par canal R/G/B
   20_image_entropy              Distribution Shannon entropy
   21_class_similarity           Matrice cosine inter-classes

🏋 TRAINING (2)
   07_training_history           Courbes loss/acc par époque (Stage 1+2)
   13_lr_schedule                LR vs époque (visualisation)

📊 EVALUATION (5)
   08_confusion_matrix           Matrice de confusion (counts + recall norm)
   09_per_class_metrics          Precision/Recall/F1 par classe
   14_roc_curves                 ROC one-vs-rest + AUC
   15_pr_curves                  Precision-Recall curves + AP
   16_calibration                Reliability diagram + Brier score

🔥 ERRORS (4)
   11_confidence_distribution    Confiance correct vs erreur (boxplot)
   12_misclassification          Top patterns d'erreur + error rate
   18_top_predictions            Top-1 vs Top-2 vs Top-3 accuracy
   22_class_focus_confusion      4 mini-matrices "1 vs rest"
```

---

## 🛡 Robustesse — comportement en cas de souci

```
Erreur runtime dans run()
        │
        ▼
[FAIL] catch + traceback → continue avec autres analyses
        │
        ▼
Le run global ne s'arrête pas
```

```
Prérequis manquant
        │
        ▼
[skip] message → continue
        │
        ▼
Pas de PNG/JSON généré pour cette analyse
```

```
Metadata incomplète (NAME, TITLE manquants...)
        │
        ▼
discover() warn + skip silencieusement
        │
        ▼
L'analyse n'apparaît pas dans --list
```

---

> Voir [`README.md`](README.md) pour le contrat complet et le tutoriel détaillé d'ajout.
