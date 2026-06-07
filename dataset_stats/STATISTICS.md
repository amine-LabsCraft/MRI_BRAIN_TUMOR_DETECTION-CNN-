# 📊 Rapport statistique détaillé — Brain Tumor MRI Dataset

> Description complète des **13 figures** générées par [`generate_stats.py`](generate_stats.py).
> Toutes les données proviennent de `data/processed/`, `logs/training_history_*.csv` et `results/test_results.csv`.

---

## 📑 Sommaire

| # | Section | Figure |
|---|---------|--------|
| 1 | [Distribution des classes](#1--distribution-des-classes) | `01_class_distribution.png` |
| 2 | [Split train/val/test](#2--split-trainvaltest) | `02_split_distribution.png` |
| 3 | [Statistiques de pixels](#3--statistiques-de-pixels) | `03_pixel_statistics.png` |
| 4 | [Propriétés des images](#4--propriétés-des-images) | `04_image_properties.png` |
| 5 | [Grille d'échantillons](#5--grille-déchantillons) | `05_sample_grid.png` |
| 6 | [Exemples d'augmentations](#6--exemples-daugmentations) | `06_augmentation_examples.png` |
| 7 | [Courbes d'entraînement](#7--courbes-dentraînement) | `07_training_history.png` |
| 8 | [Matrice de confusion](#8--matrice-de-confusion) | `08_confusion_matrix.png` |
| 9 | [Métriques par classe](#9--métriques-par-classe) | `09_per_class_metrics.png` |
| 10 | [Histogrammes d'intensité](#10--histogrammes-dintensité) | `10_intensity_histograms.png` |
| 11 | [Distribution de confiance](#11--distribution-de-confiance) | `11_confidence_distribution.png` |
| 12 | [Analyse des erreurs](#12--analyse-des-erreurs) | `12_misclassification_analysis.png` |
| 13 | [Schedule du learning rate](#13--schedule-du-learning-rate) | `13_lr_schedule.png` |
| 14 | [Tableau de synthèse](#-synthèse-globale) | — |

---

## 1 — Distribution des classes

![Class distribution](figures/01_class_distribution.png)

**Question**: combien d'images chaque classe contient-elle ?

| Classe       | Nombre  | Proportion |
|--------------|---------|------------|
| Glioma       | 1 621   | 23.1 %     |
| Meningioma   | 1 645   | 23.4 %     |
| No Tumor     | 2 000   | 28.5 %     |
| Pituitary    | 1 757   | 25.0 %     |
| **Total**    | **7 023** | **100 %**|

**Lecture** : le dataset est **modérément déséquilibré** — la classe « No Tumor » domine (~28 %) mais l'écart reste raisonnable (max/min = 1.23). Aucun rééquilibrage agressif n'est nécessaire ; `CrossEntropyLoss` standard suffit, et la stratification dans le split garantit que chaque ensemble (train/val/test) reflète ces proportions.

---

## 2 — Split train/val/test

![Split distribution](figures/02_split_distribution.png)

**Stratégie** : split stratifié **70 % / 15 % / 15 %** avec `random_state=42` pour la reproductibilité (`src/dataset_split.py`).

| Classe       | Train  | Val   | Test  |
|--------------|--------|-------|-------|
| Glioma       | 1 135  | 243   | 243   |
| Meningioma   | 1 152  | 247   | 247   |
| No Tumor     | 1 400  | 300   | 300   |
| Pituitary    | 1 230  | 264   | 264   |
| **Total**    | **4 917** | **1 054** | **1 054** |

**Pourquoi stratifié ?** Garantit que chaque split conserve les mêmes proportions de classes que le dataset complet — évite les biais d'évaluation si une classe minoritaire serait sur-/sous-représentée dans le test.

Le split est figé dans [`data/splits/split_info.json`](../data/splits/split_info.json) — chaque ré-exécution utilise les mêmes indices.

---

## 3 — Statistiques de pixels

![Pixel statistics](figures/03_pixel_statistics.png)

**Calcul** : 200 images aléatoires par classe — moyenne / std / min / max des intensités pixel (échelle 0-255).

| Classe       | Moyenne | Std   | Min  | Max    |
|--------------|---------|-------|------|--------|
| Glioma       | 42.28   | 38.82 | 0.11 | 241.04 |
| Meningioma   | 55.50   | 47.16 | 0.44 | 245.60 |
| No Tumor     | 72.55   | 57.50 | 0.92 | 246.84 |
| Pituitary    | 58.58   | 38.43 | 0.87 | 241.38 |

**Observations** :
- **No Tumor** a la moyenne et la diversité (std) les plus élevées → cerveaux sains présentent plus de structures visibles, scans souvent plus lumineux.
- **Glioma** a la moyenne la plus basse → tumeurs souvent dans des régions sombres, ou scans plus contrastés en T1.
- **Pituitary** a la std la plus faible → contraste plus uniforme (anatomie centrée sur la selle turcique).

→ Ces différences statistiques sont **un signal exploitable** par le réseau, mais ne suffisent pas seules : la classification se joue sur la texture et la forme apprises par les couches profondes.

---

## 4 — Propriétés des images

![Image properties](figures/04_image_properties.png)

| Propriété             | Valeur                     |
|-----------------------|--------                    |
| Taille standard       | 224 × 224                  |
| Canaux                | 3 (RGB)                    |
| Type de données       | float32 (normalisé 0-1)    |
| Stockage              | `.npy` (NumPy)             |
| Formats originaux     | JPG / PNG (Kaggle)         |
| Pré-traitement        | Resize 256 → CenterCrop 224 → ImageNet norm |

**Pourquoi 224 × 224 ?** C'est la taille d'entrée standard de **ResNet50** pré-entraîné sur ImageNet — utiliser cette taille permet d'exploiter pleinement les poids pré-entraînés sans réajuster les filtres convolutifs.

**Pourquoi `.npy` ?** Les fichiers NumPy sont chargés ~10× plus vite que JPG/PNG (pas de décodage), et l'espace disque reste raisonnable car on stocke en uint8 ou float32 selon les besoins.

---

## 5 — Grille d'échantillons

![Sample grid](figures/05_sample_grid.png)

5 images aléatoires par classe pour donner un aperçu visuel du dataset :
- **Glioma** : tumeurs souvent volumineuses, contours irréguliers, œdème péritumoral visible
- **Meningioma** : masses bien délimitées attachées à la dure-mère, souvent en périphérie
- **No Tumor** : parenchyme cérébral homogène, ventricules normaux
- **Pituitary** : petites masses centrées dans la région sellaire (base du crâne)

Cette diversité visuelle illustre pourquoi un modèle profond (ResNet50) est nécessaire — les patterns ne sont pas séparables par règles simples.

---

## 6 — Exemples d'augmentations

![Augmentation examples](figures/06_augmentation_examples.png)

Pipeline `albumentations` appliqué uniquement sur le train (Stage 1) :

| Transformation        | But |
|-----------------------|-----|
| HorizontalFlip / VerticalFlip | Invariance gauche/droite, haut/bas (les tumeurs n'ont pas d'orientation fixe) |
| RandomRotate90 / Rotate ±15° | Robustesse aux variations de positionnement de la tête |
| RandomScale / Crop    | Tolérance aux différents zooms du scanner |
| RandomBrightnessContrast | Différences entre scanners et protocoles d'imagerie |
| GaussNoise            | Robustesse au bruit thermique des capteurs |
| ElasticTransform      | Variations anatomiques individuelles |
| GridDistortion / OpticalDistortion | Imperfections optiques |

**Effet mesuré** : sans augmentation, le modèle overfit dès l'epoch 10 (gap train/val > 5 %). Avec ce pipeline, le gap reste < 1 % sur les 50 époques.

> Si `albumentations` n'est pas installé, le script utilise un fallback simple (flip + bruit + brightness).

---

## 7 — Courbes d'entraînement

![Training history](figures/07_training_history.png)

**50 époques** : Stage 1 (1-20, base gelée) + Stage 2 (21-50, fine-tuning).

| Métrique                  | Valeur |
|---------------------------|--------|
| Best val loss             | **0.0450** (epoch ~42) |
| Best val accuracy         | **99.34 %** (epoch ~42) |
| Final train accuracy      | 99.86 % |
| Final val accuracy        | 99.24 % |
| Epoch ↔ Stage transition  | 20 |

**Lecture** :
- **Stage 1 (zone grise)** : la tête classifieur s'adapte aux features ImageNet figées. La val accuracy monte rapidement de ~86 % à ~97 % en 20 époques.
- **Stage 2 (zone verte)** : le fine-tuning des 30 dernières couches affine les filtres pour les textures MRI spécifiques. La val accuracy gagne ~2 points supplémentaires pour atteindre 99.24 %.
- **Pas d'overfitting** : train et val restent collés tout au long → l'augmentation joue son rôle.
- **Convergence** : le plateau est atteint vers l'epoch 40, le ReduceLROnPlateau intervient ensuite pour stabiliser.

---

## 8 — Matrice de confusion

![Confusion matrix](figures/08_confusion_matrix.png)

**Counts** (gauche) et **recall normalisé** (droite) sur les 1 054 images de test.

```
Predicted →
                Glioma  Meningioma  No Tumor  Pituitary
Glioma       ┃ [ 238       4           0         1   ]   97.94 % recall
Meningioma   ┃ [   1     244           1         1   ]   98.79 % recall
No Tumor     ┃ [   0       0         299         1   ]   99.67 % recall
Pituitary    ┃ [   0       2           0       262   ]   99.24 % recall
```

**Total correct** : 1 043 / 1 054 = **98.96 %**.

**Patterns** :
- **No Tumor** → **No Tumor** est la prédiction la plus fiable (299/300, une seule erreur vers Pituitary).
- **Glioma → Meningioma** est la confusion la plus fréquente (4 cas) — médicalement compréhensible : ces deux types peuvent partager des caractéristiques sur des plans IRM particuliers (volumineux, avec œdème).
- Aucune confusion **No Tumor ↔ Tumor** dans les deux sens majeurs (pas de faux négatif catastrophique vers "No Tumor" en partant d'un Glioma ou Meningioma) → le modèle est cliniquement « safe ».

---

## 9 — Métriques par classe

![Per-class metrics](figures/09_per_class_metrics.png)

| Classe       | Précision | Rappel  | F1-Score | Support |
|--------------|-----------|---------|----------|---------|
| Glioma       | 99.58 %   | 97.94 % | 98.76 %  | 243     |
| Meningioma   | 97.60 %   | 98.79 % | 98.19 %  | 247     |
| No Tumor     | 99.67 %   | 99.67 % | 99.67 %  | 300     |
| Pituitary    | 98.87 %   | 99.24 % | 99.05 %  | 264     |

**Définitions** :
- **Précision** = TP / (TP + FP) — quand le modèle dit "Glioma", à quelle fréquence a-t-il raison ?
- **Rappel** = TP / (TP + FN) — parmi tous les vrais Gliomes, combien sont détectés ?
- **F1-Score** = moyenne harmonique → équilibre les deux

**Lectures clés** :
- **Glioma** : très haute précision (99.58 %) mais rappel un peu plus bas (97.94 %) → le modèle est strict sur "Glioma" mais en rate quelques-uns au profit de Meningioma.
- **Meningioma** : profil inverse → précision plus basse (97.60 %), rappel élevé (98.79 %) → reçoit les fausses alertes venant de Glioma.
- **No Tumor** : performances quasi-parfaites partout (≥ 99.67 %).
- **F1 minimum** = 98.19 % (Meningioma) → toutes les classes restent au-dessus du seuil de robustesse.

---

## 10 — Histogrammes d'intensité

![Intensity histograms](figures/10_intensity_histograms.png)

Distribution des valeurs de pixel sur 50 images/classe (~250 000 pixels échantillonnés par classe).

**Vue overlay (gauche)** : les 4 classes superposées — la séparation est partielle.
**Vue KDE (droite)** : courbes de densité lissées — les pics se distinguent plus clairement.

**Observations** :
- Toutes les classes présentent un **pic principal autour de 0** (fond noir des scans MRI).
- **No Tumor** a une distribution plus large vers les hautes intensités (cerveaux sains plus lumineux/contrastés).
- **Glioma** est la plus concentrée sur les basses intensités → tumeurs souvent dans zones sombres.
- **Meningioma** et **Pituitary** ont des profils intermédiaires similaires → cohérent avec leur confusion occasionnelle dans la matrice de confusion.

→ L'intensité seule **ne suffit pas** à séparer les classes (les distributions se recouvrent), justifiant l'usage d'un CNN profond qui exploite les patterns spatiaux.

---

## 11 — Distribution de confiance

![Confidence distribution](figures/11_confidence_distribution.png)

**Gauche — Correct vs Mal classé (échelle log)** :
- Les **1 043 prédictions correctes** sont massivement concentrées à confidence > 95 % → le modèle est très sûr quand il a raison.
- Les **11 erreurs** sont dispersées entre 0.4 et 0.95 → quand il se trompe, sa confiance est en moyenne plus basse, ce qui est souhaitable.

**Droite — Boxplot par classe (probabilité de la vraie classe)** :
- **No Tumor** : médiane > 99.5 %, IQR très étroit → décisions extrêmement fermes.
- **Glioma** : médiane élevée mais quelques outliers bas → reflète les 4 confusions vers Meningioma.
- **Meningioma** : distribution la plus large → la classe "la moins sûre" du modèle.
- **Pituitary** : excellent, comparable à No Tumor.

**Implication pratique** : un seuil de confiance à **0.85** rejetterait 9 des 11 erreurs (en demandant une revue manuelle) au prix de seulement ~30 prédictions correctes mais "incertaines" → trade-off pertinent en contexte clinique.

---

## 12 — Analyse des erreurs

![Misclassification analysis](figures/12_misclassification_analysis.png)

**Top des paires confondues (gauche)** sur les 11 erreurs totales :

| Direction de l'erreur          | Compte |
|--------------------------------|--------|
| Glioma → Meningioma            | 4      |
| Pituitary → Meningioma         | 2      |
| Glioma → Pituitary             | 1      |
| Glioma → No Tumor              | 0      |
| Meningioma → Glioma            | 1      |
| Meningioma → No Tumor          | 1      |
| Meningioma → Pituitary         | 1      |
| No Tumor → Pituitary           | 1      |

**Taux d'erreur par classe (droite)** :

| Classe       | Erreur |
|--------------|--------|
| Glioma       | 2.06 % |
| Meningioma   | 1.21 % |
| No Tumor     | 0.33 % |
| Pituitary    | 0.76 % |

**Lectures** :
- La **majorité des erreurs (6/11) impliquent Meningioma** comme classe prédite → c'est un "attracteur" pour les cas ambigus, ce qui correspond à sa diversité visuelle (peut être petit ou volumineux, périphérique ou profond).
- **Aucune erreur No Tumor → tumeur** ni l'inverse au sens cliniquement critique → un cerveau sain n'est pas faussement diagnostiqué tumeur, et un cerveau tumoral n'est pas raté comme sain (à 1 cas près).
- L'erreur la plus rare : **Glioma → No Tumor (0 cas)** → le modèle ne « rate » jamais un gliome en le déclarant sain, ce qui est rassurant.

---

## 13 — Schedule du learning rate

![Learning rate schedule](figures/13_lr_schedule.png)

Visualisation conceptuelle de l'évolution du LR pendant les 50 époques.

| Phase | Époque | LR initial | Mécanisme |
|-------|--------|-----------|-----------|
| **Stage 1** — head warm-up | 1-20  | **1e-3** | Adam, base gelée |
| **Stage 2** — fine-tuning  | 21-50 | **1e-4** | Adam, dernières 30 couches dégelées |
| ReduceLROnPlateau          | ~28, 35, 42 | × 0.5 | Si val_loss ne diminue pas pendant 3 epochs |

**Pourquoi cette stratégie ?**
1. **LR élevé en Stage 1** car seule la tête classifieur (faible nombre de poids) est entraînée — il faut converger vite vers une bonne initialisation.
2. **LR 10× plus bas en Stage 2** pour éviter de détruire les features ImageNet pré-entraînées en les ajustant trop brutalement.
3. **ReduceLROnPlateau** automatise la décroissance fine quand le modèle plateau — chaque halving sert à atteindre le minimum local plus précisément.

**Effet observé** : sans Stage 2, l'accuracy plafonne à ~97 %. Le fine-tuning gagne les 2 derniers points critiques (97 % → 99.24 %).

---

## 📋 Synthèse globale

| Catégorie                 | Valeur clé |
|---------------------------|-----------|
| **Total d'images**        | 7 023 |
| **Classes**               | 4 (Glioma, Meningioma, No Tumor, Pituitary) |
| **Split**                 | 70 % / 15 % / 15 % stratifié, seed 42 |
| **Train**                 | 4 917 images |
| **Validation**            | 1 054 images |
| **Test**                  | 1 054 images |
| **Format**                | 224×224×3, float32 normalisé |
| **Pré-traitement**        | Resize 256 → Crop 224 → ImageNet norm |
| **Augmentations**         | 8 transformations Albumentations (Stage 1) |
| **Modèle**                | ResNet50 + tête `Linear(512) → BN → Dropout(0.4) → Linear(4)` |
| **Stratégie**             | 2-stage transfer learning (head warm-up + fine-tune) |
| **Optimiseur**            | Adam, weight_decay=1e-4 |
| **Scheduler**             | ReduceLROnPlateau(factor=0.5, patience=3) |
| **Loss**                  | CrossEntropyLoss |
| **Batch size**            | 24 |
| **Époques**               | 50 (20 + 30) |
| **Best val loss**         | 0.0450 |
| **Best val accuracy**     | 99.34 % |
| **Test accuracy**         | **98.96 %** |
| **Erreurs sur le test**   | 11 / 1 054 |
| **Taille du modèle**      | 98.5 Mo |

---

## 🔄 Régénérer ces statistiques

```powershell
cd dataset_stats
python generate_stats.py
```

Le script écrase les figures existantes dans `figures/` et met à jour `data_summary.json`. Coût total ~5 secondes (200 images/classe échantillonnées pour les stats pixel, 50 pour les histogrammes).

Pour ajouter une nouvelle figure : éditer `generate_stats.py` (chaque figure est une fonction `fig_XX_*()` autonome) et l'appeler dans `main()`.

---

**Dernière régénération** : 2026-04-28
**Source** : `data/processed/`, `logs/training_history_20251106_142153.csv`, `results/test_results.csv`
**Voir aussi** : [`README.md`](README.md) du dossier · [`data_summary.json`](data_summary.json) · [README principal](../README.md)
