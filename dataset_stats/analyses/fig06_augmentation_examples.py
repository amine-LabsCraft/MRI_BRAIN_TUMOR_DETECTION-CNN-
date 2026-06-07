"""06 — Augmentation examples (albumentations preferred, fallback otherwise)."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from core import list_class_files, load_npy, save_figure
from core.config import RANDOM_SEED

NAME        = "06_augmentation_examples"
TITLE       = "Augmentation examples"
DESCRIPTION = "Original vs typical augmentations applied during training"
CATEGORY    = "image"
REQUIRES    = ["data"]
ORDER       = 6


def run() -> dict:
    rng = np.random.default_rng(0)
    files = list_class_files("glioma")
    arr = load_npy(rng.choice(files))

    augmentations: list[tuple[str, np.ndarray]] = []
    used = "fallback"

    try:
        import albumentations as A  # type: ignore
        import cv2

        augmentations = [
            ("Original",            arr),
            ("Horizontal Flip",     A.HorizontalFlip(p=1)(image=arr)["image"]),
            ("Rotate ±15°",         A.Rotate(limit=15, p=1, border_mode=cv2.BORDER_CONSTANT)(image=arr)["image"]),
            ("Random Scale",        A.Compose([
                                        A.RandomScale(scale_limit=0.2, p=1),
                                        A.PadIfNeeded(224, 224, border_mode=cv2.BORDER_CONSTANT),
                                        A.RandomCrop(224, 224)])(image=arr)["image"]),
            ("Brightness/Contrast", A.RandomBrightnessContrast(p=1)(image=arr)["image"]),
            ("Gaussian Noise",      A.GaussNoise(var_limit=(50.0, 100.0), p=1)(image=arr)["image"]),
            ("Elastic Transform",   A.ElasticTransform(alpha=1, sigma=50, alpha_affine=50, p=1)(image=arr)["image"]),
            ("Grid Distortion",     A.GridDistortion(p=1)(image=arr)["image"]),
        ]
        used = "albumentations"
    except Exception as e:  # noqa: BLE001
        print(f"  (albumentations unavailable: {e}) — fallback")
        augmentations = [
            ("Original",     arr),
            ("Flipped (H)",  arr[:, ::-1]),
            ("Flipped (V)",  arr[::-1, :]),
            ("Brightness +", np.clip(arr.astype(np.int16) + 40, 0, 255).astype(np.uint8)),
            ("Brightness -", np.clip(arr.astype(np.int16) - 40, 0, 255).astype(np.uint8)),
            ("Noise",        np.clip(arr.astype(np.int16) + rng.integers(-30, 30, arr.shape), 0, 255).astype(np.uint8)),
        ]

    n = len(augmentations)
    cols = 4
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 3, rows * 3))
    axes = axes.flatten() if hasattr(axes, "flatten") else [axes]

    for i, (name, img) in enumerate(augmentations):
        axes[i].imshow(img)
        axes[i].set_title(name, fontsize=11, fontweight="bold")
        axes[i].axis("off")
    for i in range(len(augmentations), len(axes)):
        axes[i].axis("off")

    plt.suptitle("Data Augmentation Examples — Glioma sample",
                 fontsize=15, fontweight="bold", y=1.00)
    plt.tight_layout()
    save_figure(fig, NAME)

    return {"backend": used, "n_examples": len(augmentations)}
