"""Centralized constants and paths for the dataset_stats package."""
from __future__ import annotations

from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
PKG_ROOT     = Path(__file__).resolve().parent.parent
BASE_DIR     = PKG_ROOT.parent

DATA_DIR     = BASE_DIR / "data" / "processed"
LOGS_DIR     = BASE_DIR / "logs"
RESULTS_DIR  = BASE_DIR / "results"

OUTPUTS_DIR  = PKG_ROOT / "outputs"
FIGURES_DIR  = OUTPUTS_DIR / "figures"
DATA_OUT_DIR = OUTPUTS_DIR / "data"
SUMMARY_JSON = OUTPUTS_DIR / "summary.json"

# Ensure output dirs always exist
for _d in (FIGURES_DIR, DATA_OUT_DIR):
    _d.mkdir(parents=True, exist_ok=True)


# ─── Class metadata ───────────────────────────────────────────────────────────
CLASSES: list[str] = ["glioma", "meningioma", "notumor", "pituitary"]

CLASS_LABELS: dict[str, str] = {
    "glioma":     "Glioma",
    "meningioma": "Meningioma",
    "notumor":    "No Tumor",
    "pituitary":  "Pituitary",
}

CLASS_COLORS: dict[str, str] = {
    "glioma":     "#EF4444",
    "meningioma": "#F59E0B",
    "notumor":    "#10B981",
    "pituitary":  "#3B82F6",
}

# Index → key (must match training order: alphabetical)
CLASS_INDEX: dict[int, str] = {
    0: "glioma",
    1: "meningioma",
    2: "notumor",
    3: "pituitary",
}


# ─── Sampling defaults ────────────────────────────────────────────────────────
DEFAULT_PIXEL_SAMPLE = 200    # images per class for pixel-level stats
DEFAULT_HIST_SAMPLE  = 50     # images per class for intensity histograms
RANDOM_SEED          = 42
