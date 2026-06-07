"""18 — Top-confidence correct vs wrong predictions gallery."""
from __future__ import annotations

import json

import matplotlib.pyplot as plt
import pandas as pd

from core import (
    CLASS_INDEX, CLASS_LABELS,
    load_npy, save_figure, test_results_csv,
)
from core.config import BASE_DIR

NAME        = "18_top_predictions"
TITLE       = "Top-K predictions"
DESCRIPTION = "Top-K correct + top-K misclassified samples (by confidence)"
CATEGORY    = "errors"
REQUIRES    = ["results", "data"]
ORDER       = 18

K = 5


def run() -> dict:
    split_path = BASE_DIR / "data" / "splits" / "split_info.json"
    if not split_path.exists():
        return {"skipped": "split_info.json missing"}

    with open(split_path, "r", encoding="utf-8") as f:
        split = json.load(f)

    # split_info.json uses "paths"; older versions used "files"
    test_node = split.get("test", {})
    test_files = test_node.get("paths") or test_node.get("files") or []
    df = pd.read_csv(test_results_csv())

    if len(df) != len(test_files):
        return {
            "skipped": f"Length mismatch: csv={len(df)}, split={len(test_files)}",
        }

    df["file_path"] = test_files
    df["max_prob"]  = df[["Prob_glioma", "Prob_meningioma",
                          "Prob_notumor", "Prob_pituitary"]].max(axis=1)

    correct = df[df["Correct"]].nlargest(K, "max_prob")
    wrong   = df[~df["Correct"]].nlargest(K, "max_prob")

    fig, axes = plt.subplots(2, K, figsize=(K * 2.8, 5.8))

    # Top-K correct (row 0)
    for i, (_, row) in enumerate(correct.iterrows()):
        try:
            arr = load_npy(BASE_DIR / row["file_path"])
            axes[0, i].imshow(arr)
        except Exception:
            axes[0, i].text(0.5, 0.5, "(load fail)", ha="center", va="center")
        true_cls = CLASS_LABELS[CLASS_INDEX[int(row["True_Label"])]]
        axes[0, i].set_title(f"{true_cls}\n{row['max_prob']*100:.2f}%",
                             fontsize=9, color="#10B981", fontweight="bold")
        axes[0, i].axis("off")

    # Top-K wrong (row 1)
    for i, (_, row) in enumerate(wrong.iterrows()):
        if i >= K:
            break
        try:
            arr = load_npy(BASE_DIR / row["file_path"])
            axes[1, i].imshow(arr)
        except Exception:
            axes[1, i].text(0.5, 0.5, "(load fail)", ha="center", va="center")
        true_cls = CLASS_LABELS[CLASS_INDEX[int(row["True_Label"])]]
        pred_cls = CLASS_LABELS[CLASS_INDEX[int(row["Predicted_Label"])]]
        axes[1, i].set_title(f"True: {true_cls}\nPred: {pred_cls} ({row['max_prob']*100:.1f}%)",
                             fontsize=8, color="#EF4444", fontweight="bold")
        axes[1, i].axis("off")

    for i in range(len(wrong), K):
        axes[1, i].axis("off")

    fig.text(0.5, 0.97, f"Top-{K} Correct Predictions (highest confidence)",
             ha="center", fontsize=12, fontweight="bold", color="#10B981")
    fig.text(0.5, 0.485, f"Top-{K} Misclassifications (highest confidence)",
             ha="center", fontsize=12, fontweight="bold", color="#EF4444")

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    save_figure(fig, NAME)

    return {
        "top_correct_n":  len(correct),
        "top_wrong_n":    len(wrong),
        "max_correct_conf": float(correct["max_prob"].max()) if len(correct) else 0.0,
        "max_wrong_conf":   float(wrong["max_prob"].max())   if len(wrong)   else 0.0,
    }
