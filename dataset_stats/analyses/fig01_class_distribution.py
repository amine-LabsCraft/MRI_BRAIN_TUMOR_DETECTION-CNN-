"""01 — Class distribution: bar + pie chart of total samples per class."""
from __future__ import annotations

import matplotlib.pyplot as plt

from core import (
    CLASSES, CLASS_COLORS, CLASS_LABELS,
    list_class_files, save_figure,
)

NAME        = "01_class_distribution"
TITLE       = "Class distribution"
DESCRIPTION = "Total samples per class — bar + pie chart"
CATEGORY    = "overview"
REQUIRES    = ["data"]
ORDER       = 1


def run() -> dict:
    counts = {cls: len(list_class_files(cls)) for cls in CLASSES}
    total  = sum(counts.values())

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    labels = [CLASS_LABELS[c] for c in CLASSES]
    values = [counts[c] for c in CLASSES]
    colors = [CLASS_COLORS[c] for c in CLASSES]

    bars = axes[0].bar(labels, values, color=colors, edgecolor="white", linewidth=2)
    axes[0].set_title("Class Distribution — Total Samples")
    axes[0].set_ylabel("Number of samples")
    axes[0].grid(axis="x", visible=False)
    for bar, v in zip(bars, values):
        axes[0].text(bar.get_x() + bar.get_width() / 2, v + total * 0.01,
                     f"{v:,}\n({v/total*100:.1f}%)", ha="center",
                     fontweight="bold", fontsize=10)
    axes[0].set_ylim(0, max(values) * 1.18)

    wedges, texts, autotexts = axes[1].pie(
        values, labels=labels, colors=colors,
        autopct="%1.1f%%", startangle=90,
        wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),
        textprops=dict(fontsize=11, fontweight="bold"),
    )
    for at in autotexts:
        at.set_color("white"); at.set_fontsize(12)
    axes[1].set_title(f"Class Proportions — Total: {total:,} images")

    plt.tight_layout()
    save_figure(fig, NAME)

    return {"counts": counts, "total": total}
