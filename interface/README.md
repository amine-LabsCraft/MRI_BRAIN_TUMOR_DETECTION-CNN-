# 🌐 interface/ — Frontend HTML / CSS / JS (port 3000)

> **Interface web premium en vanilla JS** consommant l'API FastAPI. Zéro framework, ~1700 lignes au total.

---

## ⚡ En 30 secondes

| | |
|---|---|
| 🎯 **Rôle** | UI web pour uploader IRM + visualiser prédiction + Grad-CAM + historique |
| 🚪 **Port** | 3000 (servi via `python -m http.server`) |
| 🔌 **Backend** | API FastAPI sur port 8000 (REST) |
| 📦 **Stack** | HTML5 + CSS3 + JS vanilla + Chart.js + jsPDF + Lucide |
| 💾 **Persistance** | localStorage (historique max 100, thème) |
| 🌗 **Thème** | Light + Dark (toggle, palette navy/cyan) |

---

## 🗺️ Position dans le projet

```
   Utilisateur
        │
        ▼
   ┌──────────────┐                          ┌──────────────┐
   │  index.html  │ ←─ structure ─           │  api/app.py  │
   │  styles.css  │ ←─ design ───            │   port 8000  │
   │  app.js      │ ←─ logique ──           └──────┬───────┘
   └──────┬───────┘                                │
          │                                        │
          └──── HTTP fetch (/predict /random ...) ─┘
          │
          ▼
   localStorage (historique, thème)
```

---

## 📂 Fichiers

| Fichier | Lignes | Rôle |
|---|---:|---|
| `index.html` | ~388 | Structure HTML5 sémantique (header, upload, résultats, historique, modales) |
| `styles.css` | ~922 | Design system complet (variables CSS, light + dark, animations, responsive) |
| `app.js` | ~1350 | Toute la logique applicative en 16 blocs |

---

## 🧩 Architecture de `app.js` (16 blocs)

```
┌──────────────────────────────────────────────────────────┐
│  BLOC 1   CONFIG · CLASS_STYLES · AppState · DOM cache  │
│  BLOC 2   API object (fetch wrappers)                   │
│  BLOC 3   Toasts (max 3, auto-dismiss)                  │
│  BLOC 4   API status polling (30s)                      │
│  BLOC 5   File handling + heuristique qualité IRM       │
│  BLOC 6   Loader + clearUpload                          │
│  BLOC 7   displayResults (badge, confiance, alerte)     │
│  BLOC 8   Chart.js horizontal bars (labels intelligents)│
│  BLOC 9   History (compress, save, load)                │
│  BLOC 10  Filters + pagination + render                 │
│  BLOC 11  Session stats + CSV export                    │
│  BLOC 12  Zoom modal + dark mode + opacity slider       │
│  BLOC 13  Export PNG (canvas) + Export PDF (jsPDF)      │
│  BLOC 14  Compare mode (2 IRM)                          │
│  BLOC 15  Batch analysis (max 20)                       │
│  BLOC 16  Listeners + DOMContentLoaded                  │
└──────────────────────────────────────────────────────────┘
```

---

## 🚀 Pipeline d'analyse

```
1️⃣  Drag & drop image                      ←  zone upload
2️⃣  Validation type + taille                ←  bloc 5
3️⃣  Heuristique qualité IRM (canvas)         ←  bloc 5 (badge MRI-like)
4️⃣  Click "Analyze"                          ←  bloc 16
5️⃣  POST /predict → JSON {prediction, probas, Grad-CAM}
6️⃣  displayResults (badge + barre confiance) ←  bloc 7
7️⃣  Chart.js bars + Grad-CAM grid            ←  bloc 8
8️⃣  GET /explain/{class} → infos médicales   ←  bloc 7
9️⃣  Historique (localStorage)                ←  bloc 9
🔟  Stats session mises à jour               ←  bloc 11
```

---

## 🎨 Composants UI

| Section | Élément clé | Bloc JS |
|---|---|---|
| **Header** | Logo, badge API status, theme toggle | 4, 12 |
| **Upload zone** | Drag & drop, preview, MRI quality badge | 5 |
| **Action bar** | Analyze · Random · Compare · Batch · Clear | 16 |
| **Diagnosis card** | Prediction badge, confidence bar, alert level, accordion explain | 7 |
| **Probabilities chart** | Horizontal Chart.js avec labels smart inside/outside | 8 |
| **Grad-CAM grid** | 3 colonnes : original / heatmap / overlay (zoomable) | 7, 12 |
| **History table** | Filtres (classe, date, conf), pagination, miniatures | 9, 10 |
| **Session stats** | Total, classe la plus fréquente, conf moyenne, latence | 11 |
| **Modals** | Zoom · Compare (2 slots) · Batch (20 fichiers) | 12, 14, 15 |

---

## 🎯 Fonctionnalités utilisateur

| ⚡ Action | Résultat | Stockage |
|---|---|---|
| Upload + Analyze | Prédiction + Grad-CAM + infos médicales | localStorage (entrée historique) |
| Random Example | Image aléatoire du dataset analysée | localStorage (avec true_class) |
| Compare Mode | 2 IRM analysées en parallèle | Session uniquement |
| Batch Analysis | Jusqu'à 20 IRM analysées en série | localStorage + CSV export |
| Export PNG | Carte de résultat rendue en canvas | Téléchargement direct |
| Export PDF | Rapport jsPDF brandé | Téléchargement direct |
| Export CSV | Historique complet | Téléchargement direct |
| Toggle thème | Light/Dark + repaint Chart.js | localStorage |

---

## 🌐 Endpoints consommés

| API call | Quand ? | Bloc |
|---|---|---|
| `GET /health` | Toutes les 30s (polling) | 4 |
| `POST /predict` | Click Analyze ou Compare | 16 |
| `GET /random` | Click Random | 16 |
| `GET /explain/{class}` | Après chaque prédiction | 7 |
| `POST /batch` | Click Run Analysis (modal batch) | 15 |

---

## 🚀 Lancement

```bash
# Méthode 1 : via le lanceur global (lance API + frontend)
python start.py

# Méthode 2 : manuel
cd interface
python -m http.server 3000           # ou 8080 si 3000 bloqué (Windows)
```

→ Ouvrir http://localhost:3000

---

## 🎨 Design system (`styles.css`)

| Variable | Light | Dark |
|---|---|---|
| `--bg-body` | `#F1F5F9` | `#061B2E` |
| `--bg-card` | `#FFFFFF` | `#0A2540` |
| `--cyan` | `#00D4AA` | `#00D4AA` |
| `--text-primary` | `#0F172A` | `#E2E8F0` |
| `--border` | rgba(10,37,64,0.08) | rgba(255,255,255,0.08) |

Couleurs par classe :
| Classe | Hex |
|---|---|
| Glioma | `#EF4444` 🔴 |
| Meningioma | `#F59E0B` 🟠 |
| No Tumor | `#10B981` 🟢 |
| Pituitary | `#3B82F6` 🟣 |

---

## ⚠️ Pièges courants

| Symptôme | Cause | Solution |
|---|---|---|
| Badge API rouge "Offline" | API pas lancée | `uvicorn api.app:app --port 8000 --reload` |
| Port 3000 réservé (Windows) | Hyper-V réservé port | `python -m http.server 8080` |
| CORS blocked | Origin non autorisée | `BRAINSCAN_CORS_ORIGINS=*` dans `.env` |
| Historique vide après refresh | localStorage cleared | Vérifier "incognito mode" off |
| Chart.js disparaît en dark | Stale colors | Toggle thème pour forcer repaint |

---

## 🔗 Liens

- Backend consommé : [`../api/`](../api/)
- Modèle inférencé : [`../models/`](../models/)
- Lanceur unifié : [`../start.py`](../start.py)
- Alternative Streamlit : [`../streamlit_app/`](../streamlit_app/)
