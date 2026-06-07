"""22 — Per-class confusion focus (4 mini bar charts)."""
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from core import (
    CLASS_COLORS, CLASS_INDEX, CLASS_LABELS,
    save_figure, test_results_csv,
)

NAME        = "22_class_focus_confusion"
TITLE       = "Per-class confusion focus"
DESCRIPTION = "4 mini horizontal bars showing each true class's predicted distribution"
CATEGORY    = "errors"
REQUIRES    = ["results"]
ORDER       = 22


def run() -> dict:
    df = pd.read_csv(test_results_csv())
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))

    focus = {}
    for ax, (idx, cls) in zip(axes, CLASS_INDEX.items()):
        sub = df[df["True_Label"] == idx]
        counts = sub["Predicted_Label"].value_counts().sort_index()
        full = pd.Series([0] * 4, index=range(4))
        full.update(counts)

        labels = [CLASS_LABELS[CLASS_INDEX[i]] for i in range(4)]
        colors = [CLASS_COLORS[CLASS_INDEX[i]] for i in range(4)]

        bars = ax.barh(labels, full.values, color=colors, edgecolor="white")
        ax.set_title(f"True = {CLASS_LABELS[cls]} (n={len(sub)})",
                     color=CLASS_COLORS[cls], fontweight="bold")
        ax.set_xlabel("Predictions")
        max_val = max(full.values) if max(full.values) > 0 else 1
        for bar, v in zip(bars, full.values):
            if v > 0:
                ax.text(v + max_val * 0.01,
                        bar.get_y() + bar.get_height() / 2,
                        str(v), va="center", fontsize=9, fontweight="bold")
        ax.grid(axis="y", visible=False)

        focus[cls] = {CLASS_INDEX[i]: int(full.iloc[i]) for i in range(4)}

    plt.suptitle("Per-Class Confusion Focus", fontweight="bold", y=1.02)
    plt.tight_layout()
    save_figure(fig, NAME)
    return focus
