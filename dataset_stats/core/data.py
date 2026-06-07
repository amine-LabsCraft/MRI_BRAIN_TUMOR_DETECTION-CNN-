"""Data loading helpers: .npy reading, file listing, CSV discovery."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from .config import DATA_DIR, LOGS_DIR, RESULTS_DIR


def load_npy(path: str | Path) -> np.ndarray:
    """Load a .npy file and return a uint8 array in [0, 255]."""
    arr = np.load(path)
    if arr.dtype == np.uint8:
        return arr
    if arr.max() <= 1.0:
        return (arr * 255).astype(np.uint8)
    return arr.astype(np.uint8)


def list_class_files(cls: str) -> list[Path]:
    """List all .npy files for a given class (sorted)."""
    return sorted((DATA_DIR / cls).glob("*.npy"))


def latest_training_csv() -> Path | None:
    """Return the most recent training_history_*.csv (or None)."""
    candidates = sorted(LOGS_DIR.glob("training_history_*.csv"))
    return candidates[-1] if candidates else None


def test_results_csv() -> Path | None:
    """Return results/test_results.csv if it exists."""
    p = RESULTS_DIR / "test_results.csv"
    return p if p.exists() else None
