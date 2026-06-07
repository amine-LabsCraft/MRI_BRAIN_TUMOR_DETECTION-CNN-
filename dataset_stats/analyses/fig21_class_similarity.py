"""21 — Inter-class similarity matrix (cosine similarity of mean images)."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from tqdm import tqdm

from core import (
    CLASS_LABELS, CLASSES,
    list_class_files, load_npy, save_figure,
)
from core.config import RANDOM_SEED

NAME        = "21_class_similarity"
TITLE       = "Inter-class similarity"
DESCRIPTION = "Cosine similarity matrix between mean class images"
CATEGORY    = "image"
REQUIRES    = ["data"]
ORDER       = 21

N_SAMPLE = 100


def run() -> dict:
    rng          = np.random.default_rng(RANDOM_SEED)
    mean_vectors = {}

    for cls in CLASSES:
        files = list_class_files(cls)
        if len(files) > N_SAMPLE:
            files = list(rng.choice(files, N_SAMPLE, replace=False))
        accumulator = np.zeros(224 * 224 * 3, dtype=np.float64)
        for f in tqdm(files, desc=f"  {cls}", ncols=70, leave=False):
            accumulator += load_npy(f).flatten().astype(np.float64)
        mean_vectors[cls] = accumulator / len(files)

    n   = len(CLASSES)
    sim = np.zeros((n, n))
    for i, cls_i in enumerate(CLASSES):
        for j, cls_j in enumerate(CLASSES):
            v_i, v_j = mean_vectors[cls_i], mean_vectors[cls_j]
            sim[i, j] = float(np.dot(v_i, v_j) / (np.linalg.norm(v_i) * np.linalg.norm(v_j)))

    off_diag_min = float(sim[~np.eye(n, dtype=bool)].min())

    fig, ax = plt.subplots(figsize=(8, 7))
    labels = [CLASS_LABELS[c] for c in CLASSES]
    sns.heatmap(
        sim, annot=True, fmt=".4f", cmap="RdYlGn",
        xticklabels=labels, yticklabels=labels,
        cbar_kws={"label": "Cosine similarity"}, ax=ax,
        vmin=off_diag_min, vmax=1.0,
        linewidths=0.5, linecolor="white",
    )
    ax.set_title("Inter-class Similarity (cosine on mean images)")

    plt.tight_layout()
    save_figure(fig, NAME)

    return {
        f"{a}-{b}": float(sim[i, j])
        for i, a in enumerate(CLASSES)
        for j, b in enumerate(CLASSES) if i < j
    }
