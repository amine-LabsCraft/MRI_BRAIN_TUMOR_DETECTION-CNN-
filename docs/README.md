# 📚 docs/ — Documentation par phase

> **Hub de documentation** : guides setup + comptes-rendus phase par phase.

---

## ⚡ En 30 secondes

| | |
|---|---|
| 🎯 **Rôle** | Centraliser tous les guides détaillés |
| 📁 **Format** | Markdown (lisible sur GitHub) |
| 📊 **Contenu** | 12 fichiers (~3 000 lignes) |

---

## 🗺️ Cartographie des docs

```
   docs/
     │
     ├──── 🚀 ONBOARDING ────►  QUICK_START.md
     │                          INSTALLATION.md
     │                          GPU_SETUP.md
     │
     ├──── 📊 PHASES ────────►  PHASE1_COMPLETE.md   (data prep)
     │                          PHASE2_COMPLETE.md   (training)
     │                          PHASE2_SUMMARY.md
     │                          PHASE3_COMPLETE.md   (evaluation)
     │                          PHASE3_SUMMARY.md
     │                          PHASE3_STATUS.txt
     │
     └──── 📋 META ──────────►  PROJECT_STATUS.md
                                SUMMARY.md
                                README.md           (← ce fichier)
```

---

## 📂 Inventaire

### 🚀 Guides d'onboarding

| Fichier | Pour qui | Quand le lire |
|---|---|---|
| `QUICK_START.md` | Tout nouveau utilisateur | Premier contact |
| `INSTALLATION.md` | Setup détaillé | Si problème d'install |
| `GPU_SETUP.md` | Avoir le GPU | Avant d'entraîner |

### 📊 Comptes-rendus de phase

| Phase | Fichier | Contenu |
|---|---|---|
| **1** Data prep | `PHASE1_COMPLETE.md` | Téléchargement, prétraitement, split |
| **2** Training | `PHASE2_COMPLETE.md` | Architecture, 2-stage, hyperparams |
| **2** Training | `PHASE2_SUMMARY.md` | Résumé court phase 2 |
| **3** Evaluation | `PHASE3_COMPLETE.md` | Métriques, confusion, Grad-CAM |
| **3** Evaluation | `PHASE3_SUMMARY.md` | Résumé court phase 3 |
| **3** Evaluation | `PHASE3_STATUS.txt` | Notes de statut |

### 📋 Méta-documentation

| Fichier | Contenu |
|---|---|
| `PROJECT_STATUS.md` | État global, milestones |
| `SUMMARY.md` | Résumé exécutif (1-2 pages) |

---

## 🚀 Parcours recommandé

```
1️⃣  QUICK_START.md                   ← démarrage rapide
        │
        ▼
2️⃣  INSTALLATION.md (si besoin)      ← setup complet
        │
        ▼
3️⃣  GPU_SETUP.md (si GPU dispo)      ← accélération CUDA
        │
        ▼
4️⃣  scripts/quick_start.py (run)     ← Phase 1
        │
        ▼
5️⃣  PHASE1_COMPLETE.md (lecture)     ← comprendre la prep
        │
        ▼
6️⃣  scripts/train.py (run)           ← Phase 2 (3-4h GPU)
        │
        ▼
7️⃣  PHASE2_COMPLETE.md (lecture)     ← comprendre l'entraînement
        │
        ▼
8️⃣  scripts/evaluate.py (run)        ← Phase 3
        │
        ▼
9️⃣  PHASE3_COMPLETE.md (lecture)     ← comprendre l'évaluation
```

---

## 📊 Tableau récap des phases

| Phase | Statut | Durée typique | Output |
|---|---|---|---|
| **1** Data prep | ✅ Complete | ~5 min | `data/processed/` + `data/splits/` |
| **2** Training | ✅ Complete | ~30 min GPU | `models/final_model_*.pth` |
| **3** Evaluation | ✅ Complete | ~30 s | `results/*.{txt,csv,png}` |
| **4** UI Streamlit | ✅ Complete | instant | `streamlit_app/app.py` |
| **5** API REST + Web | ✅ Complete | instant | `api/` + `interface/` |
| **6** Cloud deploy | 🔜 Planned | — | Docker, Render |
| **7** Mobile companion | 🔮 Future | — | React Native |

---

## 🎓 Parcours apprentissage

### Pour débutants
```
1️⃣  INSTALLATION.md
2️⃣  PHASE1_COMPLETE.md            ← comprendre la data prep
3️⃣  PHASE2_SUMMARY.md             ← vue d'ensemble training
4️⃣  Lancer scripts/quick_start.py
5️⃣  PROJECT_STATUS.md             ← prochaines étapes
```

### Pour utilisateurs expérimentés
```
1️⃣  PROJECT_STATUS.md             ← skim
2️⃣  PHASE{2,3}_SUMMARY.md         ← quick refs
3️⃣  PHASE{X}_COMPLETE.md          ← deep-dive selon besoin
4️⃣  GPU_SETUP.md
5️⃣  Lancer scripts/train.py
```

---

## 🔍 Recherche par sujet

### Data Processing
| Sujet | Doc |
|---|---|
| Preprocessing | [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md#preprocessing) |
| Augmentation | [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md#augmentation) |
| Splitting | [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md#dataset-splitting) |

### Architecture & Training
| Sujet | Doc |
|---|---|
| ResNet50 | [PHASE2_COMPLETE.md](PHASE2_COMPLETE.md#architecture) |
| Transfer Learning | [PHASE2_COMPLETE.md](PHASE2_COMPLETE.md#transfer-learning) |
| Two-Stage Training | [PHASE2_COMPLETE.md](PHASE2_COMPLETE.md#two-stage-training) |
| Hyperparamètres | [PHASE2_COMPLETE.md](PHASE2_COMPLETE.md#hyperparameters) |
| Callbacks | [PHASE2_COMPLETE.md](PHASE2_COMPLETE.md#callbacks) |
| GPU Setup | [GPU_SETUP.md](GPU_SETUP.md) |

### Evaluation
| Sujet | Doc |
|---|---|
| Métriques | [PHASE3_COMPLETE.md](PHASE3_COMPLETE.md#metrics) |
| Visualisations | [PHASE3_COMPLETE.md](PHASE3_COMPLETE.md#visualizations) |
| Grad-CAM | [PHASE3_COMPLETE.md](PHASE3_COMPLETE.md#gradcam) |
| Interprétation | [PHASE3_COMPLETE.md](PHASE3_COMPLETE.md#interpreting-results) |

### Troubleshooting
| Sujet | Doc |
|---|---|
| Installation | [INSTALLATION.md](INSTALLATION.md#troubleshooting) |
| GPU | [GPU_SETUP.md](GPU_SETUP.md#troubleshooting) |
| Training | [PHASE2_COMPLETE.md](PHASE2_COMPLETE.md#troubleshooting) |
| Evaluation | [PHASE3_COMPLETE.md](PHASE3_COMPLETE.md#troubleshooting) |

---

## 🔗 Liens vers les ressources

| Resource | Localisation |
|---|---|
| Code source | [`../src/`](../src/) |
| Scripts CLI | [`../scripts/`](../scripts/) |
| Backend API | [`../api/`](../api/) |
| Frontend web | [`../interface/`](../interface/) |
| App Streamlit | [`../streamlit_app/`](../streamlit_app/) |
| Statistiques | [`../dataset_stats/`](../dataset_stats/) |
| Tests | [`../tests/`](../tests/) |
| README principal | [`../README.md`](../README.md) |

---

## ⚠️ Note de versioning

Les `PHASE*_COMPLETE.md` sont **figés** une fois la phase terminée. Pour un statut à jour :

- [`PROJECT_STATUS.md`](PROJECT_STATUS.md) — milestones courants
- [`../README.md`](../README.md) — point d'entrée à jour

---

## ✨ Tips

| Astuce | Bénéfice |
|---|---|
| Démarrer par `INSTALLATION.md` puis `PHASE1_COMPLETE.md` | Onboarding fluide |
| Utiliser les fichiers `_SUMMARY.md` pour quick-ref | Lookup rapide |
| GPU training | 5-10× plus rapide |
| Checker `PROJECT_STATUS.md` régulièrement | Toujours à jour |
