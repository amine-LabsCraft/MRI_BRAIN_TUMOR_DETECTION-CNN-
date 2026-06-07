"""08 — Confusion matrix: counts + normalized recall."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from core import CLASSES, CLASS_LABELS, save_figure, test_results_csv

NAME        = "08_confusion_matrix"
TITLE       = "Confusion matrix"
DESCRIPTION = "Test-set confusion matrix — counts + normalized recall"
CATEGORY    = "evaluation"
REQUIRES    = ["results"]
ORDER       = 8


def run() -> dict:
    csv = test_results_csv()
    df = pd.read_csv(csv)
    cm = np.zeros((4, 4), dtype=int)
    for _, row in df.iterrows():
        cm[int(row["True_Label"]), int(row["Predicted_Label"])] += 1

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    labels = [CLASS_LABELS[c] for c in CLASSES]

    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels, yticklabels=labels,
                cbar_kws={"label": "Count"}, ax=axes[0],
                linewidths=0.5, linecolor="white")
    axes[0].set_title("Confusion Matrix — Counts")
    axes[0].set_xlabel("Predicted"); axes[0].set_ylabel("True")

    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True) * 100
    sns.heatmap(cm_norm, annot=True, fmt=".1f", cmap="Greens",
                xticklabels=labels, yticklabels=labels,
                cbar_kws={"label": "Recall (%)"}, ax=axes[1],
                vmin=0, vmax=100, linewidths=0.5, linecolor="white")
    axes[1].set_title("Confusion Matrix — Normalized (% recall)")
    axes[1].set_xlabel("Predicted"); axes[1].set_ylabel("True")

    plt.tight_layout()
    save_figure(fig, NAME)

    return {
        "matrix":   cm.tolist(),
        "total":    int(cm.sum()),
        "correct":  int(cm.trace()),
        "accuracy": float(cm.trace() / cm.sum()),
    }
