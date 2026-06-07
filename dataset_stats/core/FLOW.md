# 🗺 core/ FLOW — Comment l'infrastructure orchestre tout

> Le rôle de chaque fichier `core/` dans le pipeline d'exécution d'une analyse.

---

## 🚀 Initialisation au démarrage

```
import core   (depuis run.py ou une analyse)
        │
        ▼
1️⃣  config.py exécuté
        ├─ PKG_ROOT, BASE_DIR, FIGURES_DIR, ... calculés
        ├─ CLASSES, CLASS_LABELS, CLASS_COLORS définis
        └─ FIGURES_DIR.mkdir() + DATA_OUT_DIR.mkdir()  ← side-effect
        │
        ▼
2️⃣  data.py disponible
        └─ list_class_files, load_npy, sample_class, ...
        │
        ▼
3️⃣  plotting.py disponible
        ├─ setup_matplotlib (idempotent)
        ├─ save_figure / save_data
        └─ set_current_category / get_current_category
        │
        ▼
4️⃣  registry.py disponible
        ├─ discover() pour scan analyses/
        └─ run_one() / run_many()
```

---

## 📊 Pipeline d'une analyse — qui fait quoi

```
run.py orchestrateur
        │
        ▼
discover()  [registry.py]
        │
        ├─ glob(analyses/fig*.py)
        ├─ importlib.import_module pour chacun
        ├─ lecture des 6 attrs requis (NAME, TITLE, CATEGORY, ...)
        └─ retourne list[RegisteredAnalysis] triée par ORDER
        │
        ▼
for item in items :
        │
        ├─ is_runnable()  [registry.py]
        │     ├─ "data" → DATA_DIR.exists() ?         [config.py]
        │     ├─ "logs" → training_history_*.csv ?     [data.py]
        │     └─ "results" → test_results.csv ?         [data.py]
        │
        ├─ set_current_category(item.category)  [plotting.py]
        │
        ├─ item.run()    ←  exécute analyses/figXX_*.py
        │     │
        │     │  └─ utilise :
        │     │
        │     ├─ list_class_files(cls)          [data.py]
        │     ├─ load_npy(path)                  [data.py]
        │     ├─ CLASS_COLORS[cls]               [config.py]
        │     ├─ matplotlib plot                 (stdlib)
        │     └─ save_figure(fig, NAME)          [plotting.py]
        │           │
        │           └─ écrit outputs/figures/<category>/XX_*.png
        │
        ├─ set_current_category(None)  [plotting.py]   (finally)
        │
        └─ save_data(NAME, data, category=item.category)  [plotting.py]
              │
              └─ écrit outputs/data/<category>/XX_*.json
```

---

## 🧠 Le secret du contexte de catégorie

```
plotting.py module-level state
        │
        │  _CURRENT_CATEGORY: Optional[str] = None
        │
        ▼
set_current_category(cat) ←── posé par registry.run_one() avant chaque run()
        │
        ▼
save_figure(fig, name)
        │
        ├─ cat = category param OR _CURRENT_CATEGORY
        ├─ FIGURES_DIR / cat (mkdir si nécessaire)
        └─ fig.savefig(...)
        │
        ▼
set_current_category(None) ←── libéré par registry (finally)
```

→ **Aucune analyse ne touche au context.** Transparent et déterministe.

---

## 📁 Les 4 fichiers et leurs responsabilités

```
config.py
        ├─ Constants immuables (paths, classes, colors, seeds)
        └─ Side-effect : crée outputs/figures et outputs/data

data.py
        ├─ list_class_files(cls)    → liste les .npy
        ├─ load_npy(path)            → charge avec validation
        ├─ sample_class(cls, n)      → échantillon aléatoire
        ├─ latest_training_csv()     → CSV training le plus récent
        └─ test_results_csv()        → results/test_results.csv

plotting.py
        ├─ setup_matplotlib()        → defaults globaux (idempotent)
        ├─ save_figure(fig, name)    → écrit PNG dans bon sous-dossier
        ├─ save_data(name, dict)     → écrit JSON dans bon sous-dossier
        └─ set_current_category(cat) → context global

registry.py
        ├─ @dataclass RegisteredAnalysis (name, title, run, ...)
        ├─ discover()                → scan analyses/
        ├─ is_runnable()             → check REQUIRES vs filesystem
        ├─ run_one(item)             → exécute + save figure + save data
        └─ run_many(items)           → boucle simple
```

---

## 🔌 API publique exposée par `__init__.py`

```python
from core import (
    # config
    CLASSES, CLASS_LABELS, CLASS_COLORS, CLASS_INDEX,
    DATA_DIR, LOGS_DIR, RESULTS_DIR, FIGURES_DIR,
    DEFAULT_PIXEL_SAMPLE, DEFAULT_HIST_SAMPLE, RANDOM_SEED,

    # data
    list_class_files, load_npy, sample_class,
    latest_training_csv, test_results_csv,

    # plotting
    setup_matplotlib, save_figure, save_data,
    set_current_category, get_current_category,

    # registry
    discover, run_one, run_many, RegisteredAnalysis,
)
```

---

> Voir [`README.md`](README.md) pour les détails d'API et les bonnes pratiques.
