"""12 — Misclassification analysis: top error patterns + error rate per class."""
from __future__ import annotations

from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd

from core import CLASS_COLORS, CLASS_INDEX, CLASS_LABELS, CLASSES, save_figure, test_results_csv

NAME        = "12_misclassification_analysis"
TITLE       = "Misclassification analysis"
DESCRIPTION = "Top confusion pairs + per-class error rate"
CATEGORY    = "errors"
REQUIRES    = ["results"]
ORDER       = 12


def run() -> dict:
    df = pd.read_csv(test_results_csv())
    wrong = df[~df["Correct"]]

    pairs = Counter()
    for _, row in wrong.iterrows():
        t = CLASS_INDEX[int(row["True_Label"])]
        p = CLASS_INDEX[int(row["Predicted_Label"])]
        pairs[(t, p)] += 1

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    top = pairs.most_common(8)
    if top:
        labels = [f"{CLASS_LABELS[t]} → {CLASS_LABELS[p]}" for (t, p), _ in top]
        counts = [c for _, c in top]
        colors = [CLASS_COLORS[t] for (t, _), _ in top]
        axes[0].barh(labels[::-1], counts[::-1], color=colors[::-1], edgecolor="white")
        axes[0].set_title(f"Top Misclassification Patterns (n={len(wrong)})")
        axes[0].set_xlabel("Count")
        for i, c in enumerate(counts[::-1]):
            axes[0].text(c + 0.05, i, str(c), va="center", fontweight="bold")
        axes[0].grid(axis="y", visible=False)

    err_rate = {}
    for idx, cls in CLASS_INDEX.items():
        sub = df[df["True_Label"] == idx]
        err_rate[cls] = float((1 - sub["Correct"].mean()) * 100)

    bars = axes[1].bar([CLASS_LABELS[c] for c in CLASSES],
                       [err_rate[c] for c in CLASSES],
                       color=[CLASS_COLORS[c] for c in CLASSES],
                       edgecolor="white", linewidth=2)
    axes[1].set_title("Error Rate per Class")
    axes[1].set_ylabel("Error rate (%)")
    axes[1].grid(axis="x", visible=False)
    if max(err_rate.values()) > 0:
        axes[1].set_ylim(0, max(err_rate.values()) * 1.3)
    for bar, c in zip(bars, CLASSES):
        v = err_rate[c]
        axes[1].text(bar.get_x() + bar.get_width() / 2, v + 0.05,
                     f"{v:.2f}%", ha="center", fontweight="bold")

    plt.tight_layout()
    save_figure(fig, NAME)

    return {
        "total_errors":         int(len(wrong)),
        "top_patterns":         {f"{t}->{p}": int(n) for (t, p), n in top},
        "error_rate_per_class": err_rate,
    }
