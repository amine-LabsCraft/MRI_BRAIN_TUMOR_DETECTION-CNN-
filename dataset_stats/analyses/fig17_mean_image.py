"""17 — Mean image per class (averaged pixels)."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from core import (
    CLASS_COLORS, CLASS_LABELS, CLASSES,
    list_class_files, load_npy, save_figure,
)
from core.config import RANDOM_SEED

NAME        = "17_mean_image"
TITLE       = "Mean image per class"
DESCRIPTION = "Average pixel intensity image per class (visual prototype)"
CATEGORY    = "image"
REQUIRES    = ["data"]
ORDER       = 17

N_SAMPLE = 200


def run() -> dict:
    rng   = np.random.default_rng(RANDOM_SEED)
    means = {}

    for cls in CLASSES:
        files = list_class_files(cls)
        if len(files) > N_SAMPLE:
            files = list(rng.choice(files, N_SAMPLE, replace=False))
        accumulator = np.zeros((224, 224, 3), dtype=np.float64)
        for f in tqdm(files, desc=f"  {cls}", ncols=70, leave=False):
            accumulator += load_npy(f).astype(np.float64)
        means[cls] = (accumulator / len(files)).astype(np.uint8)

    fig, axes = plt.subplots(1, len(CLASSES), figsize=(len(CLASSES) * 3, 3.4))
    for ax, cls in zip(axes, CLASSES):
        ax.imshow(means[cls])
        ax.set_title(CLASS_LABELS[cls],
                     color=CLASS_COLORS[cls], fontweight="bold", fontsize=12)
        ax.axis("off")

    plt.suptitle(f"Mean Image per Class — N={N_SAMPLE} samples",
                 fontweight="bold", y=1.04)
    plt.tight_layout()
    save_figure(fig, NAME)

    return {
        cls: {"mean_intensity": float(means[cls].mean())}
        for cls in CLASSES
    }
