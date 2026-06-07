"""13 — Learning rate schedule visualization (Stage 1 + 2 + ReduceLROnPlateau)."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from core import save_figure

NAME        = "13_lr_schedule"
TITLE       = "Learning rate schedule"
DESCRIPTION = "Two-stage LR schedule + simulated ReduceLROnPlateau"
CATEGORY    = "training"
REQUIRES    = []
ORDER       = 13


def run() -> dict:
    epochs = np.arange(1, 51)
    lr = np.where(epochs <= 20, 1e-3, 1e-4)

    halvings = [28, 35, 42]
    for h in halvings:
        lr[epochs >= h] /= 2

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(epochs, lr, color="#3B82F6", lw=2.5, marker="o", markersize=4)
    ax.axvspan(0, 20, alpha=0.15, color="#94A3B8", label="Stage 1 (head only, lr=1e-3)")
    ax.axvspan(20, 50, alpha=0.15, color="#10B981", label="Stage 2 (fine-tune, lr=1e-4)")
    ax.axvline(20, color="#0F172A", ls="--", lw=1, alpha=0.6)
    for h in halvings:
        ax.axvline(h, color="#EF4444", ls=":", lw=1, alpha=0.5)
        ax.text(h, lr.max() * 0.6, "LR ÷ 2", rotation=90, color="#EF4444",
                fontsize=9, va="bottom")
    ax.set_yscale("log")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Learning rate (log scale)")
    ax.set_title("Learning Rate Schedule — Two-Stage Strategy + ReduceLROnPlateau")
    ax.legend(loc="upper right")
    ax.grid(alpha=0.3, which="both")

    plt.tight_layout()
    save_figure(fig, NAME)

    return {"halvings_at_epochs": halvings, "stage1_lr": 1e-3, "stage2_lr": 1e-4}
