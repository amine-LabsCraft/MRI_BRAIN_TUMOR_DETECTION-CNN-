"""19 — Per-channel pixel statistics (R, G, B)."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from core import (
    CLASS_LABELS, CLASSES,
    list_class_files, load_npy, save_figure,
)
from core.config import RANDOM_SEED

NAME        = "19_channel_stats"
TITLE       = "Per-channel statistics"
DESCRIPTION = "Mean R/G/B intensity per class (verifies grayscale-ness)"
CATEGORY    = "image"
REQUIRES    = ["data"]
ORDER       = 19

N_SAMPLE = 100


def run() -> dict:
    rng   = np.random.default_rng(RANDOM_SEED)
    stats = {}

    for cls in CLASSES:
        files = list_class_files(cls)
        if len(files) > N_SAMPLE:
            files = list(rng.choice(files, N_SAMPLE, replace=False))
        rs, gs, bs = [], [], []
        for f in tqdm(files, desc=f"  {cls}", ncols=70, leave=False):
            arr = load_npy(f)
            rs.append(arr[..., 0].mean())
            gs.append(arr[..., 1].mean())
            bs.append(arr[..., 2].mean())
        stats[cls] = {
            "R_mean": float(np.mean(rs)),
            "G_mean": float(np.mean(gs)),
            "B_mean": float(np.mean(bs)),
            "R_std":  float(np.std(rs)),
            "G_std":  float(np.std(gs)),
            "B_std":  float(np.std(bs)),
        }

    fig, ax = plt.subplots(figsize=(12, 5))
    x = np.arange(len(CLASSES))
    w = 0.27

    rs_v = [stats[c]["R_mean"] for c in CLASSES]
    gs_v = [stats[c]["G_mean"] for c in CLASSES]
    bs_v = [stats[c]["B_mean"] for c in CLASSES]

    ax.bar(x - w, rs_v, w, label="Red",   color="#EF4444", edgecolor="white")
    ax.bar(x,     gs_v, w, label="Green", color="#10B981", edgecolor="white")
    ax.bar(x + w, bs_v, w, label="Blue",  color="#3B82F6", edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels([CLASS_LABELS[c] for c in CLASSES])
    ax.set_ylabel("Mean intensity (0-255)")
    ax.set_title("Per-Channel Mean Intensity per Class")
    ax.legend()
    ax.grid(axis="x", visible=False)

    plt.tight_layout()
    save_figure(fig, NAME)

    return stats
