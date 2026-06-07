"""11 — Prediction confidence distribution (correct vs wrong + per-class boxplot)."""
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from core import CLASS_COLORS, CLASS_INDEX, CLASS_LABELS, CLASSES, save_figure, test_results_csv

NAME        = "11_confidence_distribution"
TITLE       = "Confidence distribution"
DESCRIPTION = "Confidence on correct vs misclassified + per-class boxplot"
CATEGORY    = "errors"
REQUIRES    = ["results"]
ORDER       = 11


def run() -> dict:
    df = pd.read_csv(test_results_csv())
    df["max_prob"] = df[["Prob_glioma", "Prob_meningioma", "Prob_notumor", "Prob_pituitary"]].max(axis=1)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    correct = df[df["Correct"]].max_prob
    wrong   = df[~df["Correct"]].max_prob
    axes[0].hist(correct, bins=40, color="#10B981", alpha=0.7,
                 label=f"Correct ({len(correct)})", edgecolor="white")
    axes[0].hist(wrong,   bins=40, color="#EF4444", alpha=0.85,
                 label=f"Misclassified ({len(wrong)})", edgecolor="white")
    axes[0].set_title("Prediction Confidence — Correct vs Incorrect")
    axes[0].set_xlabel("Max softmax probability")
    axes[0].set_ylabel("Count (log scale)")
    axes[0].set_yscale("log")
    axes[0].legend(loc="upper left")
    axes[0].set_xlim(0, 1.02)

    box_data = []
    for idx, cls in CLASS_INDEX.items():
        sub = df[df["True_Label"] == idx]
        box_data.append(sub[f"Prob_{cls}"].values * 100)
    bp = axes[1].boxplot(box_data, labels=[CLASS_LABELS[c] for c in CLASSES],
                         patch_artist=True, widths=0.55,
                         medianprops=dict(color="white", lw=2))
    for patch, cls in zip(bp["boxes"], CLASSES):
        patch.set_facecolor(CLASS_COLORS[cls])
        patch.set_alpha(0.85)
        patch.set_edgecolor("white")
    axes[1].set_title("Confidence on True-Class Probability")
    axes[1].set_ylabel("True-class probability (%)")
    axes[1].set_ylim(0, 105)
    axes[1].grid(axis="x", visible=False)

    plt.tight_layout()
    save_figure(fig, NAME)

    return {
        "correct":      int(len(correct)),
        "misclassified":int(len(wrong)),
        "mean_conf_correct": float(correct.mean()),
        "mean_conf_wrong":   float(wrong.mean()) if len(wrong) else None,
    }
