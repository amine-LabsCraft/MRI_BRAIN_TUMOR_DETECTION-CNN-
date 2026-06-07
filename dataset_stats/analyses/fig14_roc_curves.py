"""14 — ROC curves (one-vs-rest) per class."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import auc, roc_curve

from core import (
    CLASS_COLORS, CLASS_INDEX, CLASS_LABELS,
    save_figure, test_results_csv,
)

NAME        = "14_roc_curves"
TITLE       = "ROC curves"
DESCRIPTION = "ROC curves (one-vs-rest) per class with AUC scores"
CATEGORY    = "evaluation"
REQUIRES    = ["results"]
ORDER       = 14


def run() -> dict:
    df = pd.read_csv(test_results_csv())

    fig, ax = plt.subplots(figsize=(9, 7))
    aucs = {}

    for idx, cls in CLASS_INDEX.items():
        y_true  = (df["True_Label"] == idx).astype(int)
        y_score = df[f"Prob_{cls}"]
        fpr, tpr, _ = roc_curve(y_true, y_score)
        roc_auc = auc(fpr, tpr)
        aucs[cls] = float(roc_auc)
        ax.plot(fpr, tpr, color=CLASS_COLORS[cls], lw=2.4,
                label=f"{CLASS_LABELS[cls]} (AUC = {roc_auc:.4f})")

    ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5, label="Random")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves — One-vs-Rest")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)
    ax.set_xlim(-0.01, 1.01)
    ax.set_ylim(-0.01, 1.01)

    plt.tight_layout()
    save_figure(fig, NAME)

    return {
        "auc_per_class": aucs,
        "macro_auc":     float(np.mean(list(aucs.values()))),
    }
