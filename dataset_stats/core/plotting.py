"""Matplotlib defaults and figure-saving helpers (with category-based subfolders)."""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import seaborn as sns

from .config import DATA_OUT_DIR, FIGURES_DIR

_INITIALIZED = False

# Per-run category context (set by registry before run_one() invokes the analysis)
_CURRENT_CATEGORY: Optional[str] = None


# ─── Category context (used by the registry) ─────────────────────────────────
def set_current_category(category: Optional[str]) -> None:
    """Set the current analysis category for organising outputs into subfolders."""
    global _CURRENT_CATEGORY
    _CURRENT_CATEGORY = category


def get_current_category() -> Optional[str]:
    return _CURRENT_CATEGORY


def _resolve_subdir(base: Path, category: Optional[str]) -> Path:
    """Return base/<category>/ (creating it if necessary), or base if category is None."""
    if not category:
        return base
    subdir = base / category
    subdir.mkdir(parents=True, exist_ok=True)
    return subdir


# ─── matplotlib setup ────────────────────────────────────────────────────────
def setup_matplotlib() -> None:
    """Apply project-wide matplotlib & seaborn defaults (idempotent)."""
    global _INITIALIZED
    if _INITIALIZED:
        return

    # Force UTF-8 console on Windows so banners & icons print fine
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    sns.set_style("whitegrid")
    plt.rcParams.update({
        "figure.dpi":         100,
        "savefig.dpi":        150,
        "savefig.bbox":       "tight",
        "font.family":        "sans-serif",
        "font.sans-serif":    ["Inter", "Arial", "DejaVu Sans"],
        "axes.titleweight":   "bold",
        "axes.titlesize":     14,
        "axes.labelsize":     11,
        "axes.spines.top":    False,
        "axes.spines.right":  False,
    })

    _INITIALIZED = True


# ─── Save helpers ────────────────────────────────────────────────────────────
def save_figure(
    fig: plt.Figure,
    name: str,
    *,
    close: bool = True,
    category: Optional[str] = None,
) -> Path:
    """
    Save a figure to ``outputs/figures/<category>/<name>.png`` (subfolder per
    category) or ``outputs/figures/<name>.png`` if category is None.

    The category is automatically picked up from the registry context
    (``set_current_category()``) — analyses don't need to pass it explicitly.

    Args:
        fig: matplotlib Figure
        name: base filename without extension (e.g. "01_class_distribution")
        close: whether to close the figure after saving (default True)
        category: optional override. If None, uses the current registry context.
    """
    cat = category if category is not None else _CURRENT_CATEGORY
    out_dir = _resolve_subdir(FIGURES_DIR, cat)
    path = out_dir / f"{name}.png"
    fig.savefig(path)
    if close:
        plt.close(fig)
    return path


def save_data(name: str, data: dict, *, category: Optional[str] = None) -> Path:
    """Save a per-analysis JSON in ``outputs/data/<category>/<name>.json``."""
    cat = category if category is not None else _CURRENT_CATEGORY
    out_dir = _resolve_subdir(DATA_OUT_DIR, cat)
    path = out_dir / f"{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    return path
