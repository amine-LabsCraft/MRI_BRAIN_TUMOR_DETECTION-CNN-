"""07 — Training history: loss + accuracy curves over 50 epochs."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from core import latest_training_csv, save_figure

NAME        = "07_training_history"
TITLE       = "Training history"
DESCRIPTION = "Loss + accuracy curves with Stage-1/Stage-2 shading"
CATEGORY    = "training"
REQUIRES    = ["logs"]
ORDER       = 7


def run() -> dict:
    csv = latest_training_csv()
    if csv is None:
        return {}

    df = pd.read_csv(csv)
    epochs = np.arange(1, len(df) + 1)
    stage_split = 20

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].plot(epochs, df["train_loss"], color="#3B82F6", lw=2.2, label="Train Loss")
    axes[0].plot(epochs, df["val_loss"],   color="#EF4444", lw=2.2, label="Val Loss")
    axes[0].axvspan(0, stage_split, alpha=0.12, color="#94A3B8", label="Stage 1 (frozen)")
    axes[0].axvspan(stage_split, len(df), alpha=0.12, color="#10B981", label="Stage 2 (fine-tune)")
    axes[0].axvline(stage_split, color="#0F172A", ls="--", lw=1, alpha=0.6)
    axes[0].set_title("Loss Over Epochs")
    axes[0].set_xlabel("Epoch"); axes[0].set_ylabel("Loss")
    axes[0].legend(loc="upper right"); axes[0].grid(alpha=0.3)

    axes[1].plot(epochs, df["train_acc"] * 100, color="#3B82F6", lw=2.2, label="Train Acc")
    axes[1].plot(epochs, df["val_acc"]   * 100, color="#EF4444", lw=2.2, label="Val Acc")
    axes[1].axvspan(0, stage_split, alpha=0.12, color="#94A3B8")
    axes[1].axvspan(stage_split, len(df), alpha=0.12, color="#10B981")
    axes[1].axvline(stage_split, color="#0F172A", ls="--", lw=1, alpha=0.6)
    axes[1].axhline(98.96, color="#10B981", ls=":", lw=1.2, alpha=0.7,
                    label="Final test acc (98.96%)")
    axes[1].set_title("Accuracy Over Epochs")
    axes[1].set_xlabel("Epoch"); axes[1].set_ylabel("Accuracy (%)")
    axes[1].legend(loc="lower right"); axes[1].grid(alpha=0.3)
    axes[1].set_ylim(75, 101)

    plt.tight_layout()
    save_figure(fig, NAME)

    return {
        "n_epochs":         len(df),
        "best_val_loss":    float(df["val_loss"].min()),
        "best_val_acc":     float(df["val_acc"].max() * 100),
        "final_train_acc":  float(df["train_acc"].iloc[-1] * 100),
        "final_val_acc":    float(df["val_acc"].iloc[-1] * 100),
        "source":           csv.name,
    }
