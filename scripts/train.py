"""
Quick Training Script for Brain Tumor Classification
PyTorch Implementation with GPU Support
"""

import torch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))

from model_architecture import create_model
from data_loaders import create_data_loaders
from model_trainer import PyTorchTrainer, get_default_config


def main():
    """Main training function."""
    print("\n" + "="*70)
    print("BRAIN TUMOR CLASSIFICATION - PyTorch Training")
    print("="*70)
    
    # Check GPU
    if torch.cuda.is_available():
        print(f"\n✓ GPU Available: {torch.cuda.get_device_name(0)}")
        print(f"  CUDA Version: {torch.version.cuda}")
        print(f"  GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    else:
        print("\n⚠ No GPU detected. Training will use CPU (much slower).")
        response = input("Continue with CPU training? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Get configuration
    config = get_default_config()
    
    # Allow user to modify epochs
    print(f"\nDefault configuration:")
    print(f"  Stage 1 epochs: {config['stage1_epochs']} (frozen base)")
    print(f"  Stage 2 epochs: {config['stage2_epochs']} (fine-tuning)")
    print(f"  Batch size: {config['batch_size']}")
    
    modify = input("\nUse default configuration? (y/n): ")
    if modify.lower() == 'n':
        try:
            stage1 = int(input("Stage 1 epochs: "))
            stage2 = int(input("Stage 2 epochs: "))
            batch_size = int(input("Batch size: "))
            config['stage1_epochs'] = stage1
            config['stage2_epochs'] = stage2
            config['batch_size'] = batch_size
        except ValueError:
            print("Invalid input. Using defaults.")
    
    # Create data loaders
    print("\n" + "="*70)
    print("STEP 1: Loading Data")
    print("="*70)
    data_loaders, class_names = create_data_loaders(
        split_info_path=config['split_info_path'],
        batch_size=config['batch_size'],
        image_size=config['image_size'],
        num_workers=config['num_workers']
    )
    
    # Create model
    print("\n" + "="*70)
    print("STEP 2: Building Model")
    print("="*70)
    model = create_model(
        num_classes=config['num_classes'],
        pretrained=config['pretrained'],
        dense_units=config['dense_units'],
        dropout_rate=config['dropout_rate'],
        freeze_base=True
    )
    
    model.get_model_summary()
    
    # Create trainer
    print("\n" + "="*70)
    print("STEP 3: Training")
    print("="*70)
    trainer = PyTorchTrainer(
        model=model,
        data_loaders=data_loaders,
        config=config,
        device='cuda' if torch.cuda.is_available() else 'cpu'
    )
    
    # Start training
    trainer.train_two_stages()
    
    print("\n" + "="*70)
    print("✓ TRAINING COMPLETED SUCCESSFULLY!")
    print("="*70)
    print(f"\nBest model saved to: {trainer.best_model_path}")
    print(f"Training history saved to: {config['logs_dir']}")
    print("\nNext steps:")
    print("  1. Evaluate model: python evaluate.py")
    print("  2. View results in logs/ directory")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user.")
    except Exception as e:
        print(f"\n\nError during training: {e}")
        import traceback
        traceback.print_exc()
