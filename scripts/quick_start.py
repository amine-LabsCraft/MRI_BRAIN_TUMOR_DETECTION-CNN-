"""
Quick Start Script - Phase 1 Data Preparation
Run this script to quickly set up and test the data pipeline
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'src'))

print("="*70)
print("BRAIN TUMOR MRI - PHASE 1: DATA PREPARATION")
print("="*70)

print("\n📋 Checking project structure...")

# Check if directories exist
directories = ['data/raw', 'data/processed', 'data/splits', 'src', 'notebooks', 'models']
for directory in directories:
    path = Path(directory)
    if path.exists():
        print(f"✓ {directory}")
    else:
        print(f"✗ {directory} - Creating...")
        path.mkdir(parents=True, exist_ok=True)

print("\n📦 Required packages:")
packages = [
    'tensorflow',
    'numpy',
    'pandas',
    'opencv-python (cv2)',
    'albumentations',
    'matplotlib',
    'scikit-learn',
    'tqdm',
    'pillow'
]

for package in packages:
    print(f"  • {package}")

print("\n📥 To install all dependencies, run:")
print("  pip install -r requirements.txt")

print("\n📂 Dataset Setup:")
print("  1. Download the dataset from:")
print("     https://www.kaggle.com/datasets/sartajbhuvaji/brain-tumor-classification-mri")
print("  2. Extract to: data/raw/")
print("  3. Expected structure:")
print("     data/raw/")
print("       ├── glioma/")
print("       ├── meningioma/")
print("       ├── pituitary/")
print("       └── notumor/")

print("\n🚀 To run the complete pipeline:")
print("  cd src")
print("  python data_pipeline.py")

print("\n📖 For detailed documentation, see:")
print("  • README.md - Project overview")
print("  • PHASE1_COMPLETE.md - Complete Phase 1 guide")
print("  • file.txt - Full project plan")

print("\n" + "="*70)
print("Phase 1 Implementation: COMPLETE ✅")
print("="*70)

print("\nNext Steps:")
print("1. Install dependencies (if not already done)")
print("2. Download and place dataset in data/raw/")
print("3. Run: python src/data_pipeline.py")
print("4. Proceed to Phase 2: Model Development")

print("\n💡 Tip: Read PHASE1_COMPLETE.md for detailed usage examples!")
