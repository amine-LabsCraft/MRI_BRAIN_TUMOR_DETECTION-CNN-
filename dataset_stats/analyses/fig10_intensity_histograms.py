"""10 — Pixel intensity histograms (overlay + KDE)."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from tqdm import tqdm

from core import CLASSES, CLASS_COLORS, CLASS_LABELS, list_class_files, load_npy, save_figure
from core.config import DEFAULT_HIST_SAMPLE, RANDOM_SEED

NAME        = "10_intensity_histograms"
TITLE       = "Intensity histograms"
DESCRIPTION = "Per-class pixel intensity distributions (overlay + KDE)"
CATEGORY    = "image"
REQUIRES    = ["data"]
ORDER       = 10


def run() -> dict:
    rng = np.random.default_rng(RANDOM_SEED)
    histograms: dict[str, np.ndarray] = {}

    for cls in CLASSES:
        files = list_class_files(cls)
        files = list(rng.choice(files, min(DEFAULT_HIST_SAMPLE, len(files)), replace=False))
        chunks = []
        for f in tqdm(files, desc=f"  {cls}", ncols=70, leave=False):
            arr = load_npy(f).reshape(-1)
            chunks.append(rng.choice(arr, min(5000, len(arr)), replace=False))
        histograms[cls] = np.concatenate(chunks)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for cls in CLASSES:
        axes[0].hist(histograms[cls], bins=64, color=CLASS_COLORS[cls],
                     alpha=0.45, label=CLASS_LABELS[cls],
                     density=True, edgecolor="none")
    axes[0].set_title("Pixel Intensity Distributions (overlay)")
    axes[0].set_xlabel("Pixel value (0-255)")
    axes[0].set_ylabel("Density"); axes[0].legend()

    for cls in CLASSES:
        sns.kdeplot(histograms[cls], color=CLASS_COLORS[cls],
                    label=CLASS_LABELS[cls], lw=2.2, ax=axes[1])
    axes[1].set_title("Pixel Intensity Distributions (KDE)")
    axes[1].set_xlabel("Pixel value (0-255)")
    axes[1].set_ylabel("Density"); axes[1].legend()

    plt.tight_layout()
    save_figure(fig, NAME)

    return {cls: int(len(arr)) for cls, arr in histograms.items()}
