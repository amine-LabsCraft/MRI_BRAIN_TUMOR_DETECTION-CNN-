"""16 — Calibration / reliability diagram + Expected Calibration Error (ECE)."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from core import save_figure, test_results_csv

NAME        = "16_calibration"
TITLE       = "Calibration diagram"
DESCRIPTION = "Reliability diagram + Expected Calibration Error (ECE)"
CATEGORY    = "evaluation"
REQUIRES    = ["results"]
ORDER       = 16

N_BINS = 15


def run() -> dict:
    df = pd.read_csv(test_results_csv())
    df["max_prob"] = df[["Prob_glioma", "Prob_meningioma",
                         "Prob_notumor", "Prob_pituitary"]].max(axis=1)

    bin_edges   = np.linspace(0, 1, N_BINS + 1)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    bin_acc, bin_conf, bin_count = [], [], []
    ece = 0.0
    n   = len(df)

    for i in range(N_BINS):
        if i == N_BINS - 1:
            mask = (df["max_prob"] >= bin_edges[i]) & (df["max_prob"] <= bin_edges[i + 1])
        else:
            mask = (df["max_prob"] >= bin_edges[i]) & (df["max_prob"] <  bin_edges[i + 1])
        count = int(mask.sum())
        if count > 0:
            acc  = float(df.loc[mask, "Correct"].mean())
            conf = float(df.loc[mask, "max_prob"].mean())
            bin_acc.append(acc); bin_conf.append(conf); bin_count.append(count)
            ece += (count / n) * abs(acc - conf)
        else:
            bin_acc.append(0.0); bin_conf.append(bin_centers[i]); bin_count.append(0)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Reliability bars
    width = 1 / N_BINS * 0.95
    axes[0].bar(bin_centers, bin_acc, width=width, color="#3B82F6",
                alpha=0.8, edgecolor="white", label="Empirical accuracy")
    axes[0].plot([0, 1], [0, 1], "k--", lw=1.5, alpha=0.6, label="Perfect calibration")
    axes[0].set_xlabel("Confidence")
    axes[0].set_ylabel("Accuracy")
    axes[0].set_title(f"Reliability Diagram — ECE = {ece:.4f}")
    axes[0].legend(loc="upper left")
    axes[0].set_xlim(0, 1); axes[0].set_ylim(0, 1.05)
    axes[0].grid(alpha=0.3)

    # Confidence histogram
    axes[1].hist(df["max_prob"], bins=30, color="#10B981",
                 edgecolor="white", alpha=0.85)
    axes[1].axvline(df["max_prob"].mean(), color="#EF4444", ls="--",
                    label=f"Mean conf: {df['max_prob'].mean():.4f}")
    axes[1].set_xlabel("Max softmax probability")
    axes[1].set_ylabel("Count")
    axes[1].set_title("Confidence Histogram")
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    save_figure(fig, NAME)

    return {
        "ece":             float(ece),
        "n_bins":          N_BINS,
        "mean_confidence": float(df["max_prob"].mean()),
        "mean_accuracy":   float(df["Correct"].mean()),
    }
