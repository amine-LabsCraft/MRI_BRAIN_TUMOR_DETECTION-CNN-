"""Shared infrastructure for dataset_stats analyses."""
from .config import (
    CLASSES, CLASS_LABELS, CLASS_COLORS, CLASS_INDEX,
    BASE_DIR, DATA_DIR, LOGS_DIR, RESULTS_DIR,
    OUTPUTS_DIR, FIGURES_DIR, DATA_OUT_DIR, SUMMARY_JSON,
)
from .data import load_npy, list_class_files, latest_training_csv, test_results_csv
from .plotting import setup_matplotlib, save_figure
from .registry import discover, run_one, run_many

__all__ = [
    "CLASSES", "CLASS_LABELS", "CLASS_COLORS", "CLASS_INDEX",
    "BASE_DIR", "DATA_DIR", "LOGS_DIR", "RESULTS_DIR",
    "OUTPUTS_DIR", "FIGURES_DIR", "DATA_OUT_DIR", "SUMMARY_JSON",
    "load_npy", "list_class_files", "latest_training_csv", "test_results_csv",
    "setup_matplotlib", "save_figure",
    "discover", "run_one", "run_many",
]
