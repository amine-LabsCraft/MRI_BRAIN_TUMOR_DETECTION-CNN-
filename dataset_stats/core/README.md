# 🧱 dataset_stats/core/ — Infrastructure partagée

> **Le moteur** : config centralisée, helpers data, defaults matplotlib, et registre auto-découverte. Tout ce qui est consommé par les 22 analyses.

---

## ⚡ En 30 secondes

| | |
|---|---|
| 🎯 **Rôle** | Fournir les blocs réutilisables aux 22 analyses |
| 🔌 **API publique** | Exposée via `core/__init__.py` |
| 🏗 **Pattern** | Registry-based auto-discovery + context manager pour catégorie |
| 🧪 **Stable** | Une fois écrit, ne change presque jamais |

---

## 📂 Inventaire

```
core/
├── __init__.py        ← Re-exports publics (CLASSES, save_figure, etc.)
├── config.py          ← Constantes : paths, classes, couleurs, seeds
├── data.py            ← Helpers I/O dataset (load_npy, list_class_files...)
├── plotting.py        ← matplotlib defaults + save_figure / save_data
├── registry.py        ← Auto-découverte des analyses (le cœur)
└── README.md          ← Ce fichier
```

---

## 🧠 `config.py` — Constantes et chemins

Centralise toutes les **constantes immuables** du projet :

```python
# Paths (résolus relatifs à la racine projet)
PKG_ROOT     = dataset_stats/
BASE_DIR     = racine projet
DATA_DIR     = BASE_DIR / "data" / "processed"
LOGS_DIR     = BASE_DIR / "logs"
RESULTS_DIR  = BASE_DIR / "results"
OUTPUTS_DIR  = PKG_ROOT / "outputs"
FIGURES_DIR  = OUTPUTS_DIR / "figures"
DATA_OUT_DIR = OUTPUTS_DIR / "data"
SUMMARY_JSON = OUTPUTS_DIR / "summary.json"

# Métadonnées des classes
CLASSES       = ["glioma", "meningioma", "notumor", "pituitary"]
CLASS_LABELS  = {"glioma": "Glioma", ...}            # Affichage humain
CLASS_COLORS  = {"glioma": "#EF4444", ...}            # Couleurs cohérentes
CLASS_INDEX   = {0: "glioma", 1: "meningioma", ...}   # Ordre du modèle

# Defaults
DEFAULT_PIXEL_SAMPLE = 200    # Images/classe pour stats pixel
DEFAULT_HIST_SAMPLE  = 50     # Images/classe pour histogrammes
RANDOM_SEED          = 42     # Reproductibilité
```

**Side-effect au import** : crée `outputs/figures/` et `outputs/data/` si absents.

---

## 📥 `data.py` — Helpers I/O

Toutes les fonctions de **chargement/listing du dataset** :

```python
def list_class_files(cls: str, limit: int | None = None) -> list[Path]
    """Liste les .npy d'une classe (data/processed/<cls>/*.npy)."""

def load_npy(path: Path) -> np.ndarray
    """Charge un .npy avec validation shape (224, 224, 3)."""

def sample_class(cls: str, n: int, seed: int = 42) -> list[np.ndarray]
    """Échantillonne aléatoirement n images d'une classe."""

def latest_training_csv() -> Path | None
    """Retourne le CSV training le plus récent dans logs/."""

def test_results_csv() -> Path
    """Retourne results/test_results.csv (raise si absent)."""
```

→ Tout le code I/O est **isolé ici** : si on change le format de stockage (.npy → .h5), on ne modifie qu'un fichier.

---

## 🎨 `plotting.py` — Defaults matplotlib + save helpers

### `setup_matplotlib()` (idempotent)

Configure le **style global** de tous les plots :

```python
sns.set_style("whitegrid")
plt.rcParams.update({
    "savefig.dpi":     150,           # haute résolution
    "savefig.bbox":    "tight",       # pas de marge
    "font.sans-serif": ["Inter", "Arial", "DejaVu Sans"],
    "axes.titleweight":"bold",
    "axes.spines.top":  False,        # spines minimalistes
    "axes.spines.right":False,
})
```

→ Toutes les figures ont le **même look cohérent** : police Inter, fond blanc, titres en gras.

Aussi : force `stdout` en UTF-8 sur Windows pour éviter `UnicodeEncodeError` sur les emojis.

### `save_figure(fig, name)` — la magie de l'organisation par catégorie

```python
def save_figure(fig, name, *, close=True, category=None):
    cat = category or _CURRENT_CATEGORY    # ← context global posé par registry
    out = FIGURES_DIR / cat if cat else FIGURES_DIR
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{name}.png")
```

→ Si appelé **dans un contexte `run_one()`**, écrit dans `outputs/figures/<category>/`.
→ Si appelé **hors contexte**, écrit en flat dans `outputs/figures/`.

### `save_data(name, data)` — équivalent JSON

Identique mais pour `outputs/data/<category>/<name>.json`.

### Context manager `set_current_category(cat)`

```python
_CURRENT_CATEGORY = None

def set_current_category(cat: str | None) -> None:
    global _CURRENT_CATEGORY
    _CURRENT_CATEGORY = cat
```

→ Module-level state, posé/libéré par `registry.py` autour de chaque `run()`.
→ **Aucune analyse n'a besoin d'y toucher** — c'est transparent.

---

## 🔍 `registry.py` — Le cœur de l'auto-découverte

### `discover()` → liste des `RegisteredAnalysis`

```python
@dataclass
class RegisteredAnalysis:
    name: str           # "01_class_distribution"
    title: str          # "Class distribution"
    description: str    # "Total samples per class"
    category: str       # "overview"
    requires: list[str] # ["data"]
    order: int          # 1
    run: Callable       # mod.run
    module_path: Path
```

Procédure :
1. Glob `analyses/fig*.py`
2. Pour chaque fichier : `importlib.import_module("analyses.figXX_*")`
3. Lecture des attributs obligatoires (`NAME`, `TITLE`, `CATEGORY`, etc.)
4. Si interface incomplète → warning + skip silencieux
5. Tri par `ORDER` croissant

→ **Rien à enregistrer manuellement**. Déposer un fichier dans `analyses/` suffit.

### `run_one(item)` — exécute une analyse

```python
def run_one(item):
    # 1. Vérification des prérequis (data/, logs/, results/)
    ok, why = item.is_runnable()
    if not ok:
        print(f"  [skip] {item.name}  ({why})")
        return None

    # 2. Pose la catégorie dans le contexte global
    set_current_category(item.category)

    # 3. Exécute la run
    try:
        data = item.run() or {}
    except Exception as e:
        print(f"  [FAIL] {item.name}: {e}")
        return None
    finally:
        set_current_category(None)         # ← TOUJOURS libère

    # 4. Sauvegarde le JSON dans le sous-dossier de catégorie
    save_data(item.name, {...}, category=item.category)
```

### `run_many(items)` — exécute plusieurs

Boucle simple sur `run_one()`, retourne un dict `{name: data}`.

### `is_runnable()` — détection de prérequis

```python
def is_runnable(self) -> tuple[bool, str | None]:
    for req in self.requires:
        if req == "data" and not DATA_DIR.exists():
            return False, f"missing {DATA_DIR}"
        if req == "logs" and not list(LOGS_DIR.glob("training_history_*.csv")):
            return False, "missing training_history_*.csv"
        if req == "results" and not (RESULTS_DIR / "test_results.csv").exists():
            return False, "missing test_results.csv"
    return True, None
```

→ Si une analyse demande `["results"]` mais `test_results.csv` n'existe pas, elle est `[skipped]` au lieu de planter.

---

## 🔌 `__init__.py` — API publique

Toutes ces imports sont disponibles via `from core import ...` :

```python
# Constantes (config.py)
CLASSES, CLASS_LABELS, CLASS_COLORS, CLASS_INDEX
DATA_DIR, LOGS_DIR, RESULTS_DIR, FIGURES_DIR, DATA_OUT_DIR
DEFAULT_PIXEL_SAMPLE, DEFAULT_HIST_SAMPLE, RANDOM_SEED

# Helpers data (data.py)
list_class_files, load_npy, sample_class
latest_training_csv, test_results_csv

# Helpers plot (plotting.py)
setup_matplotlib
save_figure, save_data
set_current_category, get_current_category

# Registry (registry.py)
discover, run_one, run_many, RegisteredAnalysis
```

---

## 🧬 Comment ces 4 fichiers s'enchaînent

```
                   run.py
                     │
                     ▼
          setup_matplotlib() ──────  plotting.py
                     │
                     ▼
              discover() ─────────── registry.py
                     │ (utilise importlib)
                     ▼
        liste de RegisteredAnalysis
                     │
                     ▼
              filter_items()
                     │
                     ▼
            ┌────────────────────┐
            │  pour chaque item: │
            │   run_one(item)    │
            └────────┬───────────┘
                     │
                     ▼
          set_current_category(cat) ── plotting.py
                     │
                     ▼
              item.run() ─────────── analyses/figXX_*.py
              │     │
              │     └─ save_figure(fig, NAME)  ─── plotting.py (utilise contexte)
              │     └─ list_class_files(cls)   ─── data.py
              │     └─ CLASS_COLORS[cls]       ─── config.py
              │
              ▼
         save_data(name, data)  ─── plotting.py
                     │
                     ▼
            outputs/data/<cat>/<name>.json
```

---

## 🧪 Cheat sheet

```python
# Une analyse type utilise ces 5 imports
from core import (
    CLASSES, CLASS_COLORS, CLASS_LABELS,    # ← config
    list_class_files, load_npy,              # ← data
    save_figure,                             # ← plotting
)

NAME = "XX_my_analysis"
CATEGORY = "image"

def run() -> dict:
    fig, ax = plt.subplots()
    # ... plot ...
    save_figure(fig, NAME)   # auto-rangé dans outputs/figures/image/
    return {"metric": 42}
```

---

## 🐛 Modifications fréquentes

| Besoin | Fichier à éditer |
|---|---|
| Ajouter une classe (au-delà des 4) | `config.py` (CLASSES + maps) |
| Changer la palette de couleurs | `config.py` (CLASS_COLORS) |
| Modifier la résolution PNG | `plotting.py` (setup_matplotlib) |
| Ajouter un type de prérequis | `registry.py` (`is_runnable`) |
| Changer la nomenclature des dossiers | `config.py` (FIGURES_DIR, DATA_OUT_DIR) |
| Supporter un autre format que .npy | `data.py` (load_npy) |

---

## 📚 Voir aussi

- [`../README.md`](../README.md) — Vue d'ensemble du package dataset_stats
- [`../analyses/README.md`](../analyses/README.md) — Contrat des modules d'analyse
- [`../run.py`](../run.py) — CLI qui orchestre tout

---

> **Convention** : les modules de `core/` ne dépendent **que** de la stdlib + matplotlib + numpy + pandas. Aucune dépendance circulaire vers `analyses/`.
