"""02 — Stratified 70/15/15 split visualization."""
from __future__ import annotations

import matplotlib.pyplot as plt

from core import CLASSES, CLASS_LABELS, list_class_files, save_figure

NAME        = "02_split_distribution"
TITLE       = "Train/Val/Test split"
DESCRIPTION = "Stratified 70/15/15 split per class + totals"
CATEGORY    = "overview"
REQUIRES    = ["data"]
ORDER       = 2


def run() -> dict:
    class_counts = {cls: len(list_class_files(cls)) for cls in CLASSES}
    splits = {"train": 0.70, "val": 0.15, "test": 0.15}
    split_data = {cls: {s: int(round(class_counts[cls] * r))
                        for s, r in splits.items()} for cls in CLASSES}

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    labels     = [CLASS_LABELS[c] for c in CLASSES]
    train_vals = [split_data[c]["train"] for c in CLASSES]
    val_vals   = [split_data[c]["val"]   for c in CLASSES]
    test_vals  = [split_data[c]["test"]  for c in CLASSES]

    axes[0].barh(labels, train_vals, color="#3B82F6", label="Train (70 %)", edgecolor="white")
    axes[0].barh(labels, val_vals, left=train_vals, color="#F59E0B",
                 label="Validation (15 %)", edgecolor="white")
    axes[0].barh(labels, test_vals,
                 left=[t + v for t, v in zip(train_vals, val_vals)],
                 color="#10B981", label="Test (15 %)", edgecolor="white")
    axes[0].set_title("Stratified 70/15/15 Split per Class")
    axes[0].set_xlabel("Number of samples")
    axes[0].legend(loc="lower right", framealpha=0.95)
    axes[0].grid(axis="y", visible=False)

    totals = {
        "Train":      sum(train_vals),
        "Validation": sum(val_vals),
        "Test":       sum(test_vals),
    }
    bars = axes[1].bar(totals.keys(), totals.values(),
                       color=["#3B82F6", "#F59E0B", "#10B981"],
                       edgecolor="white", linewidth=2)
    axes[1].set_title("Total Samples per Split")
    axes[1].set_ylabel("Number of samples")
    axes[1].grid(axis="x", visible=False)
    grand = sum(totals.values())
    for bar, v in zip(bars, totals.values()):
        axes[1].text(bar.get_x() + bar.get_width() / 2, v + grand * 0.01,
                     f"{v:,}\n({v/grand*100:.1f}%)", ha="center",
                     fontweight="bold", fontsize=11)
    axes[1].set_ylim(0, max(totals.values()) * 1.2)

    plt.tight_layout()
    save_figure(fig, NAME)

    return {"per_class": split_data, "totals": totals}
