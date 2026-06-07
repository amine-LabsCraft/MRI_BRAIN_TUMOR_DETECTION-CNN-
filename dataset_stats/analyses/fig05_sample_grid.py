"""05 — Sample grid: random images per class."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from core import (
    CLASSES, CLASS_COLORS, CLASS_LABELS,
    list_class_files, load_npy, save_figure,
)
from core.config import RANDOM_SEED

NAME        = "05_sample_grid"
TITLE       = "Sample grid"
DESCRIPTION = "Random samples per class (5 each)"
CATEGORY    = "image"
REQUIRES    = ["data"]
ORDER       = 5


def run(n_per_class: int = 5) -> dict:
    fig, axes = plt.subplots(len(CLASSES), n_per_class,
                             figsize=(n_per_class * 2.6, len(CLASSES) * 2.6))
    rng = np.random.default_rng(RANDOM_SEED)

    for i, cls in enumerate(CLASSES):
        files = list_class_files(cls)
        idx = rng.choice(len(files), n_per_class, replace=False)
        for j, k in enumerate(idx):
            arr = load_npy(files[k])
            axes[i, j].imshow(arr, cmap="gray" if arr.ndim == 2 else None)
            axes[i, j].axis("off")
            if j == 0:
                axes[i, j].set_ylabel(CLASS_LABELS[cls], fontsize=14, fontweight="bold",
                                      color=CLASS_COLORS[cls], rotation=0,
                                      labelpad=60, va="center")
                axes[i, j].axis("on")
                axes[i, j].set_xticks([]); axes[i, j].set_yticks([])
                for spine in axes[i, j].spines.values():
                    spine.set_visible(False)

    plt.suptitle("Random Sample Grid — 5 images per class",
                 fontsize=15, fontweight="bold", y=1.01)
    plt.tight_layout()
    save_figure(fig, NAME)

    return {"n_per_class": n_per_class}
