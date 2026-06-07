"""20 — Shannon entropy distribution per class (texture complexity)."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from core import (
    CLASS_COLORS, CLASS_LABELS, CLASSES,
    list_class_files, load_npy, save_figure,
)
from core.config import RANDOM_SEED

NAME        = "20_image_entropy"
TITLE       = "Image entropy"
DESCRIPTION = "Shannon entropy distribution per class (texture complexity)"
CATEGORY    = "image"
REQUIRES    = ["data"]
ORDER       = 20

N_SAMPLE = 100


def shannon_entropy(arr: np.ndarray) -> float:
    """Compute Shannon entropy of pixel intensity histogram (256 bins)."""
    hist, _ = np.histogram(arr.flatten(), bins=256, range=(0, 256))
    p = hist / hist.sum()
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))


def run() -> dict:
    rng       = np.random.default_rng(RANDOM_SEED)
    entropies = {cls: [] for cls in CLASSES}

    for cls in CLASSES:
        files = list_class_files(cls)
        if len(files) > N_SAMPLE:
            files = list(rng.choice(files, N_SAMPLE, replace=False))
        for f in tqdm(files, desc=f"  {cls}", ncols=70, leave=False):
            entropies[cls].append(shannon_entropy(load_npy(f)))

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Boxplot
    data = [entropies[c] for c in CLASSES]
    bp = axes[0].boxplot(
        data, labels=[CLASS_LABELS[c] for c in CLASSES],
        patch_artist=True, widths=0.55,
        medianprops=dict(color="white", lw=2),
    )
    for patch, cls in zip(bp["boxes"], CLASSES):
        patch.set_facecolor(CLASS_COLORS[cls])
        patch.set_alpha(0.85)
        patch.set_edgecolor("white")
    axes[0].set_title("Shannon Entropy per Class")
    axes[0].set_ylabel("Entropy (bits)")
    axes[0].grid(axis="x", visible=False)

    # Overlay histogram
    for cls in CLASSES:
        axes[1].hist(entropies[cls], bins=20, color=CLASS_COLORS[cls],
                     alpha=0.5, label=CLASS_LABELS[cls], edgecolor="white")
    axes[1].set_title("Entropy Distribution Overlay")
    axes[1].set_xlabel("Entropy (bits)")
    axes[1].set_ylabel("Count")
    axes[1].legend()

    plt.tight_layout()
    save_figure(fig, NAME)

    return {
        cls: {
            "mean": float(np.mean(entropies[cls])),
            "std":  float(np.std(entropies[cls])),
            "min":  float(np.min(entropies[cls])),
            "max":  float(np.max(entropies[cls])),
            "n":    len(entropies[cls]),
        }
        for cls in CLASSES
    }
