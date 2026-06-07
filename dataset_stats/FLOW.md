# 🗺 dataset_stats/ FLOW — Auto-découverte → 22 figures

> Du `python run.py` aux 22 PNG organisés par catégorie, voici les étapes.

---

## 🚀 Pipeline complet

```
1️⃣  python dataset_stats/run.py [--list | --only N | --category C | ...]
        │
        ▼
2️⃣  setup_matplotlib()
        ├─ Force stdout UTF-8 sur Windows
        ├─ sns.set_style("whitegrid")
        └─ rcParams (Inter font, dpi=150, no top/right spines)
        │
        ▼
3️⃣  registry.discover()
        │
        ├─ glob analyses/fig*.py
        ├─ for each : importlib.import_module
        ├─ lecture metadata (NAME, TITLE, CATEGORY, REQUIRES, ORDER, run)
        ├─ skip si interface incomplète (avec warning)
        └─ tri par ORDER croissant
        │
        ▼
4️⃣  filter_items() → applique --only/--except/--filter/--category
        │
        ▼
5️⃣  pour chaque RegisteredAnalysis :
        │
        ├─── 5a. is_runnable() ?
        │       ├─ "data" + DATA_DIR exists ?
        │       ├─ "logs" + training_history_*.csv exists ?
        │       └─ "results" + test_results.csv exists ?
        │       │
        │       ├─ NON → [skip] log + continue
        │       │
        │       └─ OUI ▼
        │
        ├─── 5b. set_current_category(item.category)
        │
        ├─── 5c. data = item.run()
        │       │
        │       ├─ Charge données (load_npy, list_class_files, csv...)
        │       ├─ Calculs numpy/pandas/sklearn
        │       ├─ matplotlib figure construction
        │       └─ save_figure(fig, NAME)  ← lit context = item.category
        │             │
        │             └─ outputs/figures/<category>/XX_*.png
        │
        ├─── 5d. set_current_category(None)  [finally]
        │
        └─── 5e. save_data(NAME, data, category=item.category)
              │
              └─ outputs/data/<category>/XX_*.json
        │
        ▼
6️⃣  Master summary.json écrit
        ├─ version, generated_by, n_run, n_total, elapsed_sec
        └─ analyses: { "01_*": {title, category, data, ...}, ... }
        │
        ▼
✅ Done · 22 figures + 22 JSON + 1 summary en ~20 s
```

---

## 🗂 Structure de sortie générée

```
outputs/
├── figures/
│   ├── 🌐 overview/   (2)  ← 01, 02
│   ├── 🖼  image/      (9)  ← 03, 04, 05, 06, 10, 17, 19, 20, 21
│   ├── 🏋  training/   (2)  ← 07, 13
│   ├── 📊 evaluation/ (5)  ← 08, 09, 14, 15, 16
│   └── 🔥 errors/     (4)  ← 11, 12, 18, 22
│
├── data/             ← Même structure miroir (22 JSON)
│
└── summary.json      ← Agrégat
```

---

## 🔧 Comment l'auto-découverte fonctionne

```
analyses/figXX_my_analysis.py
        │
        ├─ NAME, TITLE, CATEGORY, REQUIRES, ORDER, run()
        │
        ▼
registry.discover() le trouve via glob
        │
        ▼
RegisteredAnalysis dataclass instancié
        │
        ▼
listé dans --list, exécutable via --only XX
```

→ **Aucun import central** à modifier pour ajouter une analyse.

---

## ⚙️ Modes CLI

```
--list                   ← liste sans exécuter (groupé par catégorie)
--only 01,03,07          ← exécuter ID spécifiques
--except 06,10           ← tout sauf ces ID
--filter training        ← match titre/nom (substring)
--category evaluation    ← seulement la catégorie donnée
(aucun arg)              ← tout exécuter
```

---

## 📁 Sous-dossiers

| Sous-dossier | Rôle | FLOW dédié |
|---|---|---|
| `core/` | Infrastructure partagée | [`core/FLOW.md`](core/FLOW.md) |
| `analyses/` | Les 22 modules d'analyse | [`analyses/FLOW.md`](analyses/FLOW.md) |
| `outputs/` | Généré automatiquement | (voir [`README.md`](README.md)) |

---

> Voir [`README.md`](README.md) pour le catalogue complet des 22 analyses et la doc d'architecture.
