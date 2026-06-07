"""03 — Pixel statistics per class (mean / std)."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from core import CLASSES, CLASS_COLORS, CLASS_LABELS, list_class_files, load_npy, save_figure
from core.config import DEFAULT_PIXEL_SAMPLE, RANDOM_SEED

NAME        = "03_pixel_statistics"
TITLE       = "Pixel statistics"
DESCRIPTION = "Mean intensity & std per class (sampled)"
CATEGORY    = "image"
REQUIRES    = ["data"]
ORDER       = 3


def run() -> dict:
    rng = np.random.default_rng(RANDOM_SEED)
    stats = {}
    for cls in CLASSES:
        files = list_class_files(cls)
        if len(files) > DEFAULT_PIXEL_SAMPLE:
            files = list(rng.choice(files, DEFAULT_PIXEL_SAMPLE, replace=False))
        means, stds, mins, maxs = [], [], [], []
        for f in tqdm(files, desc=f"  {cls}", ncols=70, leave=False):
            arr = load_npy(f)
            means.append(arr.mean()); stds.append(arr.std())
            mins.append(arr.min());   maxs.append(arr.max())
        stats[cls] = {
            "mean":      float(np.mean(means)),
            "mean_std":  float(np.std(means)),
            "std":       float(np.mean(stds)),
            "min":       float(np.mean(mins)),
            "max":       float(np.mean(maxs)),
            "n_sampled": len(files),
        }

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    labels = [CLASS_LABELS[c] for c in CLASSES]
    colors = [CLASS_COLORS[c]  for c in CLASSES]

    means = [stats[c]["mean"] for c in CLASSES]
    bars  = axes[0].bar(labels, means, color=colors,
                        yerr=[stats[c]["mean_std"] for c in CLASSES],
                        edgecolor="white", linewidth=2, capsize=8)
    axes[0].set_title("Mean Pixel Intensity per Class")
    axes[0].set_ylabel("Mean intensity (0-255)")
    axes[0].grid(axis="x", visible=False)
    for bar, v in zip(bars, means):
        axes[0].text(bar.get_x() + bar.get_width() / 2, v + 5,
                     f"{v:.1f}", ha="center", fontweight="bold")

    stds = [stats[c]["std"] for c in CLASSES]
    bars = axes[1].bar(labels, stds, color=colors, edgecolor="white", linewidth=2)
    axes[1].set_title("Pixel Standard Deviation per Class")
    axes[1].set_ylabel("Std (texture diversity)")
    axes[1].grid(axis="x", visible=False)
    for bar, v in zip(bars, stds):
        axes[1].text(bar.get_x() + bar.get_width() / 2, v + 1,
                     f"{v:.1f}", ha="center", fontweight="bold")

    plt.tight_layout()
    save_figure(fig, NAME)

    return stats
