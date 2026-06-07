"""
Main Training Script for Brain Tumor MRI Classification
Phase 2: Complete Training Pipeline with CLI Support
"""

import argparse
import json
from pathlib import Path
import sys

from model_trainer import TwoStageTrainer, get_default_config


def load_config(config_path):
    """Load configuration from JSON file."""
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config


def save_config(config, config_path):
    """Save configuration to JSON file."""
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuration saved to: {config_path}")


def update_config_from_args(config, args):
    """Update configuration with command-line arguments."""
    if args.batch_size:
        config['data']['batch_size'] = args.batch_size
    
    if args.stage1_epochs:
        config['training']['stage1']['epochs'] = args.stage1_epochs
    
    if args.stage2_epochs:
        config['training']['stage2']['epochs'] = args.stage2_epochs
    
    if args.stage1_lr:
        config['training']['stage1']['learning_rate'] = args.stage1_lr
    
    if args.stage2_lr:
        config['training']['stage2']['learning_rate'] = args.stage2_lr
    
    if args.dense_units:
        config['model']['dense_units'] = args.dense_units
    
    if args.dropout:
        config['model']['dropout_rate'] = args.dropout
    
    if args.unfreeze_layers:
        config['training']['stage2']['unfreeze_layers'] = args.unfreeze_layers
    
    if args.skip_stage1:
        config['training']['run_stage1'] = False
    
    if args.skip_stage2:
        config['training']['run_stage2'] = False
    
    if args.no_tensorboard:
        config['training']['use_tensorboard'] = False
    
    if args.no_class_weights:
        config['training']['use_class_weights'] = False
    
    return config


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(
        description='Train Brain Tumor MRI Classification Model (ResNet50)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train with default configuration
  python train_model.py

  # Train with custom config
  python train_model.py --config my_config.json

  # Quick training (fewer epochs)
  python train_model.py --stage1-epochs 5 --stage2-epochs 10

  # Custom hyperparameters
  python train_model.py --batch-size 64 --dense-units 1024 --dropout 0.5

  # Skip stages
  python train_model.py --skip-stage1  # Only fine-tuning
  python train_model.py --skip-stage2  # Only train head

  # Save default config
  python train_model.py --save-config training_config.json --no-train
        """
    )
    
    # Configuration
    parser.add_argument('--config', type=str, default=None,
                       help='Path to configuration JSON file')
    parser.add_argument('--save-config', type=str, default=None,
                       help='Save configuration to specified path')
    parser.add_argument('--no-train', action='store_true',
                       help='Do not run training (useful with --save-config)')
    
    # Data parameters
    parser.add_argument('--batch-size', type=int, default=None,
                       help='Batch size for training (default: 32)')
    
    # Model parameters
    parser.add_argument('--dense-units', type=int, default=None,
                       help='Number of units in dense layer (default: 512)')
    parser.add_argument('--dropout', type=float, default=None,
                       help='Dropout rate (default: 0.4)')
    
    # Training parameters - Stage 1
    parser.add_argument('--stage1-epochs', type=int, default=None,
                       help='Number of epochs for Stage 1 (default: 20)')
    parser.add_argument('--stage1-lr', type=float, default=None,
                       help='Learning rate for Stage 1 (default: 1e-4)')
    
    # Training parameters - Stage 2
    parser.add_argument('--stage2-epochs', type=int, default=None,
                       help='Number of epochs for Stage 2 (default: 30)')
    parser.add_argument('--stage2-lr', type=float, default=None,
                       help='Learning rate for Stage 2 (default: 1e-5)')
    parser.add_argument('--unfreeze-layers', type=int, default=None,
                       help='Number of layers to unfreeze in Stage 2 (default: 30)')
    
    # Training control
    parser.add_argument('--skip-stage1', action='store_true',
                       help='Skip Stage 1 (train head)')
    parser.add_argument('--skip-stage2', action='store_true',
                       help='Skip Stage 2 (fine-tuning)')
    parser.add_argument('--no-tensorboard', action='store_true',
                       help='Disable TensorBoard logging')
    parser.add_argument('--no-class-weights', action='store_true',
                       help='Do not use class weights for imbalanced data')
    
    args = parser.parse_args()
    
    # Load or create configuration
    if args.config:
        print(f"Loading configuration from: {args.config}")
        config = load_config(args.config)
    else:
        print("Using default configuration")
        config = get_default_config()
    
    # Update config with command-line arguments
    config = update_config_from_args(config, args)
    
    # Save configuration if requested
    if args.save_config:
        save_config(config, args.save_config)
        if args.no_train:
            print("\nConfiguration saved. Exiting without training.")
            return
    
    # Display configuration
    print("\n" + "="*70)
    print("TRAINING CONFIGURATION")
    print("="*70)
    print(json.dumps(config, indent=2))
    
    # Verify data exists
    split_info_path = Path(config['data']['split_info_path'])
    if not split_info_path.exists():
        print("\n" + "="*70)
        print("ERROR: Split information not found!")
        print("="*70)
        print(f"Expected file: {split_info_path}")
        print("\nPlease run the data preparation pipeline first:")
        print("  cd src")
        print("  python data_pipeline.py")
        sys.exit(1)
    
    # Create trainer
    print("\n" + "="*70)
    print("Initializing Trainer")
    print("="*70)
    trainer = TwoStageTrainer(config)
    
    # Run training
    try:
        results = trainer.train_full_pipeline()
        
        print("\n" + "="*70)
        print("🎉 TRAINING COMPLETED SUCCESSFULLY! 🎉")
        print("="*70)
        print(f"\nFinal Test Accuracy: {results[1]:.2%}")
        print(f"Final Test Loss: {results[0]:.4f}")
        
        print("\n📁 Output Files:")
        print(f"  Models: {config['paths']['models']}/")
        print(f"  Logs: {config['paths']['logs']}/")
        
        print("\n🔜 Next Steps:")
        print("  1. Visualize training history")
        print("  2. Generate confusion matrix")
        print("  3. Create Grad-CAM visualizations")
        print("  4. Proceed to Phase 3: Evaluation")
        
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during training: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
