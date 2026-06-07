"""09 — Precision / Recall / F1 per class."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from core import CLASS_INDEX, CLASS_LABELS, CLASSES, save_figure, test_results_csv

NAME        = "09_per_class_metrics"
TITLE       = "Per-class metrics"
DESCRIPTION = "Precision / Recall / F1 grouped bars"
CATEGORY    = "evaluation"
REQUIRES    = ["results"]
ORDER       = 9


def run() -> dict:
    df = pd.read_csv(test_results_csv())
    metrics = {}
    for idx, cls in CLASS_INDEX.items():
        tp = ((df["True_Label"] == idx) & (df["Predicted_Label"] == idx)).sum()
        fp = ((df["True_Label"] != idx) & (df["Predicted_Label"] == idx)).sum()
        fn = ((df["True_Label"] == idx) & (df["Predicted_Label"] != idx)).sum()
        prec   = tp / (tp + fp) if tp + fp else 0
        recall = tp / (tp + fn) if tp + fn else 0
        f1     = 2 * prec * recall / (prec + recall) if prec + recall else 0
        metrics[cls] = {
            "precision": float(prec),
            "recall":    float(recall),
            "f1":        float(f1),
            "support":   int((df["True_Label"] == idx).sum()),
        }

    fig, ax = plt.subplots(figsize=(12, 6))
    labels = [CLASS_LABELS[c] for c in CLASSES]
    x = np.arange(len(labels))
    w = 0.27

    prec_v = [metrics[c]["precision"] * 100 for c in CLASSES]
    rec_v  = [metrics[c]["recall"]    * 100 for c in CLASSES]
    f1_v   = [metrics[c]["f1"]        * 100 for c in CLASSES]

    b1 = ax.bar(x - w, prec_v, w, label="Precision", color="#3B82F6", edgecolor="white")
    b2 = ax.bar(x,     rec_v,  w, label="Recall",    color="#F59E0B", edgecolor="white")
    b3 = ax.bar(x + w, f1_v,   w, label="F1-Score",  color="#10B981", edgecolor="white")

    for bars in (b1, b2, b3):
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.3, f"{h:.1f}",
                    ha="center", fontsize=9, fontweight="bold")

    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("Score (%)")
    ax.set_title("Per-Class Performance Metrics")
    ax.set_ylim(94, 102)
    ax.legend(loc="lower right", framealpha=0.95)
    ax.grid(axis="x", visible=False)

    plt.tight_layout()
    save_figure(fig, NAME)

    return metrics
