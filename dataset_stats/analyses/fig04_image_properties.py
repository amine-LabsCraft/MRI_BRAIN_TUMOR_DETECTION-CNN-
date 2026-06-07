"""04 — Image properties summary (info card)."""
from __future__ import annotations

import matplotlib.pyplot as plt

from core import save_figure

NAME        = "04_image_properties"
TITLE       = "Image properties"
DESCRIPTION = "Shape / dtype / preprocessing pipeline summary"
CATEGORY    = "image"
REQUIRES    = []
ORDER       = 4


def run() -> dict:
    info = {
        "Standard size":     "224 × 224",
        "Channels":          "3 (RGB)",
        "Dtype":             "float32 (normalized 0-1)",
        "Storage":           ".npy (NumPy)",
        "Original formats":  "JPG / PNG (Kaggle)",
        "Pre-processing":    "Resize 256 → CenterCrop 224 → ImageNet norm",
    }

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis("off")
    ax.text(0.5, 0.95, "Image Properties — All Classes",
            fontsize=16, fontweight="bold", ha="center", transform=ax.transAxes)
    ax.text(0.5, 0.88, "Every sample is pre-resized & ImageNet-normalized for ResNet50",
            fontsize=10, ha="center", style="italic", color="#64748B",
            transform=ax.transAxes)

    y_start, line_h = 0.78, 0.10
    for i, (k, v) in enumerate(info.items()):
        y = y_start - i * line_h
        ax.text(0.15, y, k, fontweight="bold", fontsize=12, transform=ax.transAxes)
        ax.text(0.55, y, v, fontsize=12, transform=ax.transAxes,
                family="monospace", color="#0F3460")
        ax.plot([0.12, 0.88], [y - 0.025, y - 0.025],
                color="#E2E8F0", lw=1, transform=ax.transAxes)

    diag_y = 0.06
    boxes = [("256×256", "#94A3B8"), ("→", None),
             ("224×224", "#3B82F6"), ("→", None),
             ("Norm",    "#10B981")]
    x = 0.15
    for txt, color in boxes:
        if color:
            ax.add_patch(plt.Rectangle((x, diag_y), 0.13, 0.07,
                         facecolor=color, alpha=0.8, transform=ax.transAxes))
            ax.text(x + 0.065, diag_y + 0.035, txt, fontsize=11,
                    fontweight="bold", color="white", ha="center",
                    va="center", transform=ax.transAxes)
            x += 0.155
        else:
            ax.text(x, diag_y + 0.035, txt, fontsize=20, ha="center",
                    va="center", transform=ax.transAxes, color="#475569")
            x += 0.05

    save_figure(fig, NAME)
    return info
