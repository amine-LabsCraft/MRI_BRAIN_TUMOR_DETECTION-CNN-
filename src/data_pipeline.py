"""
Complete Data Pipeline for Brain Tumor MRI Classification
Phase 1: Complete End-to-End Data Preparation Pipeline
"""

import os
import argparse
import json
from pathlib import Path
from data_preprocessing import DataPreprocessor
from data_augmentation import DataAugmentor
from dataset_split import DatasetSplitter, verify_split_balance


class DataPipeline:
    """Complete data preparation pipeline for the project."""
    
    def __init__(self, config):
        """
        Initialize data pipeline with configuration.
        
        Args:
            config (dict): Configuration dictionary
        """
        self.config = config
        
        # Initialize components
        self.preprocessor = DataPreprocessor(
            target_size=config['preprocessing']['target_size'],
            crop_size=config['preprocessing']['crop_size']
        )
        
        self.augmentor = DataAugmentor(
            image_size=config['preprocessing']['crop_size']
        )
        
        self.splitter = DatasetSplitter(
            train_ratio=config['split']['train_ratio'],
            val_ratio=config['split']['val_ratio'],
            test_ratio=config['split']['test_ratio'],
            random_state=config['split']['random_state']
        )
    
    def run_preprocessing(self):
        """Run data preprocessing step."""
        print("\n" + "="*60)
        print("STEP 1: DATA PREPROCESSING")
        print("="*60)
        
        input_dir = self.config['paths']['raw_data']
        output_dir = self.config['paths']['processed_data']
        
        self.preprocessor.preprocess_dataset(
            input_dir=input_dir,
            output_dir=output_dir,
            apply_normalization=self.config['preprocessing']['apply_imagenet_norm']
        )
    
    def run_splitting(self):
        """Run dataset splitting step."""
        print("\n" + "="*60)
        print("STEP 2: DATASET SPLITTING")
        print("="*60)
        
        data_dir = self.config['paths']['processed_data']
        output_dir = self.config['paths']['split_data']
        
        split_info = self.splitter.split_dataset(
            data_dir=data_dir,
            output_dir=output_dir
        )
        
        # Verify balance
        verify_split_balance(split_info)
        
        # Optionally organize into folders
        if self.config['split'].get('organize_folders', False):
            self.splitter.organize_split_folders(split_info, output_dir)
        
        return split_info
    
    def run_full_pipeline(self):
        """Run the complete data preparation pipeline."""
        print("\n" + "="*60)
        print("BRAIN TUMOR MRI - DATA PREPARATION PIPELINE")
        print("="*60)
        print("\nConfiguration:")
        print(json.dumps(self.config, indent=2))
        
        # Step 1: Preprocessing
        if self.config.get('run_preprocessing', True):
            self.run_preprocessing()
        else:
            print("\nSkipping preprocessing (already done)")
        
        # Step 2: Splitting
        if self.config.get('run_splitting', True):
            split_info = self.run_splitting()
        else:
            print("\nSkipping splitting (already done)")
            split_info = None
        
        # Summary
        print("\n" + "="*60)
        print("DATA PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nNext Steps:")
        print("1. Verify the processed data in:", self.config['paths']['processed_data'])
        print("2. Check split information in:", self.config['paths']['split_data'])
        print("3. Ready to proceed to Phase 2: Model Development")
        
        return split_info


def get_default_config():
    """Get default configuration for data pipeline."""
    # Get absolute paths
    project_root = Path(__file__).parent.parent
    
    return {
        'paths': {
            'raw_data': str(project_root / 'data' / 'raw'),
            'processed_data': str(project_root / 'data' / 'processed'),
            'split_data': str(project_root / 'data' / 'splits')
        },
        'preprocessing': {
            'target_size': 256,
            'crop_size': 224,
            'apply_imagenet_norm': False  # Set True if training from scratch
        },
        'augmentation': {
            'enabled': True,
            'horizontal_flip': True,
            'vertical_flip': True,
            'rotation_range': 15,
            'zoom_range': 0.2,
            'brightness_range': 0.2,
            'contrast_range': 0.2,
            'gaussian_noise': True
        },
        'split': {
            'train_ratio': 0.70,
            'val_ratio': 0.15,
            'test_ratio': 0.15,
            'random_state': 42,
            'organize_folders': False  # Set True to organize into train/val/test folders
        },
        'run_preprocessing': True,
        'run_splitting': True
    }


def save_config(config, output_path):
    """Save configuration to JSON file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuration saved to: {output_path}")


def load_config(config_path):
    """Load configuration from JSON file."""
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config


def main():
    """Main function to run the data pipeline."""
    parser = argparse.ArgumentParser(
        description='Brain Tumor MRI Data Preparation Pipeline'
    )
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to configuration JSON file'
    )
    parser.add_argument(
        '--save-config',
        type=str,
        default=None,
        help='Save default configuration to specified path'
    )
    parser.add_argument(
        '--skip-preprocessing',
        action='store_true',
        help='Skip preprocessing step'
    )
    parser.add_argument(
        '--skip-splitting',
        action='store_true',
        help='Skip splitting step'
    )
    
    args = parser.parse_args()
    
    # Load or create configuration
    if args.config:
        print(f"Loading configuration from: {args.config}")
        config = load_config(args.config)
    else:
        print("Using default configuration")
        config = get_default_config()
    
    # Save configuration if requested
    if args.save_config:
        save_config(config, args.save_config)
        return
    
    # Update config based on arguments
    if args.skip_preprocessing:
        config['run_preprocessing'] = False
    if args.skip_splitting:
        config['run_splitting'] = False
    
    # Create and run pipeline
    pipeline = DataPipeline(config)
    pipeline.run_full_pipeline()


if __name__ == "__main__":
    # Check if running as script or imported
    import sys
    
    if len(sys.argv) > 1:
        # Run with command-line arguments
        main()
    else:
        # Run with default configuration
        print("Running with default configuration...")
        print("Use --help to see available options\n")
        
        config = get_default_config()
        
        # Save default config for reference
        config_path = Path('../data/pipeline_config.json')
        save_config(config, config_path)
        
        # Run pipeline
        pipeline = DataPipeline(config)
        pipeline.run_full_pipeline()
