"""15 — Precision-Recall curves per class."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, precision_recall_curve

from core import (
    CLASS_COLORS, CLASS_INDEX, CLASS_LABELS,
    save_figure, test_results_csv,
)

NAME        = "15_pr_curves"
TITLE       = "Precision-Recall curves"
DESCRIPTION = "Per-class PR curves with average precision (AP)"
CATEGORY    = "evaluation"
REQUIRES    = ["results"]
ORDER       = 15


def run() -> dict:
    df = pd.read_csv(test_results_csv())

    fig, ax = plt.subplots(figsize=(9, 7))
    aps = {}

    for idx, cls in CLASS_INDEX.items():
        y_true  = (df["True_Label"] == idx).astype(int)
        y_score = df[f"Prob_{cls}"]
        precision, recall, _ = precision_recall_curve(y_true, y_score)
        ap = average_precision_score(y_true, y_score)
        aps[cls] = float(ap)
        ax.plot(recall, precision, color=CLASS_COLORS[cls], lw=2.4,
                label=f"{CLASS_LABELS[cls]} (AP = {ap:.4f})")

    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title("Precision-Recall Curves — Per Class")
    ax.legend(loc="lower left")
    ax.grid(alpha=0.3)
    ax.set_xlim(-0.01, 1.01)
    ax.set_ylim(-0.01, 1.05)

    plt.tight_layout()
    save_figure(fig, NAME)

    return {
        "ap_per_class": aps,
        "macro_ap":     float(np.mean(list(aps.values()))),
    }
