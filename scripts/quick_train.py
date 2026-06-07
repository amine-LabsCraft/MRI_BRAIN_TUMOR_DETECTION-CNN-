"""
Quick Training Script - Start Training Immediately
Phase 2: Model Training Quick Start
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'src'))

print("="*70)
print("BRAIN TUMOR MRI - PHASE 2: MODEL TRAINING")
print("="*70)

print("\n📋 Pre-Training Checklist:")
print("  1. Data preprocessed? (Phase 1 complete)")
print("  2. Dependencies installed? (pip install -r requirements.txt)")
print("  3. GPU available? (Optional, but recommended)")

# Check if split info exists
split_info_path = Path('data/splits/split_info.json')
if split_info_path.exists():
    print("\n✅ Data is ready (split_info.json found)")
else:
    print("\n❌ Data not ready (split_info.json not found)")
    print("\nPlease run Phase 1 first:")
    print("  python src/data_pipeline.py")
    sys.exit(1)

print("\n" + "="*70)
print("TRAINING OPTIONS")
print("="*70)

print("\n1️⃣  Quick Test (Fast)")
print("   Command: python src/train_model.py --stage1-epochs 3 --stage2-epochs 5")
print("   Time: ~15-30 minutes")
print("   Purpose: Test that everything works")

print("\n2️⃣  Default Training (Recommended)")
print("   Command: python src/train_model.py")
print("   Time: ~2-4 hours")
print("   Purpose: Full training with good results")

print("\n3️⃣  Extended Training (Best Results)")
print("   Command: python src/train_model.py --stage1-epochs 30 --stage2-epochs 50")
print("   Time: ~4-8 hours")
print("   Purpose: Maximum accuracy")

print("\n4️⃣  Custom Configuration")
print("   Command: python src/train_model.py --batch-size 64 --dense-units 1024")
print("   Purpose: Experiment with hyperparameters")

print("\n" + "="*70)
print("USEFUL COMMANDS")
print("="*70)

print("\n# View all options:")
print("  python src/train_model.py --help")

print("\n# Monitor training with TensorBoard:")
print("  tensorboard --logdir=logs")

print("\n# Save configuration for later:")
print("  python src/train_model.py --save-config my_config.json --no-train")

print("\n# Train with saved config:")
print("  python src/train_model.py --config my_config.json")

print("\n" + "="*70)
print("RECOMMENDED: Start with Quick Test")
print("="*70)

print("\nRun this command to start:")
print("  cd src")
print("  python train_model.py --stage1-epochs 3 --stage2-epochs 5")

print("\n💡 Tip: Open another terminal and run 'tensorboard --logdir=logs' to monitor!")

print("\n" + "="*70)
print("Phase 2 Implementation: COMPLETE ✅")
print("="*70)

print("\nWhat's included:")
print("  ✓ ResNet50 architecture with custom head")
print("  ✓ Two-stage training strategy")
print("  ✓ Complete callback system")
print("  ✓ Data loading with augmentation")
print("  ✓ CLI interface")
print("  ✓ TensorBoard logging")
print("  ✓ Model checkpointing")
print("  ✓ Training history tracking")

print("\n🚀 Ready to train! Good luck!")
