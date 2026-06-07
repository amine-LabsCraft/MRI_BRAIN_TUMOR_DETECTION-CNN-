"""
Dataset Splitting Module for Brain Tumor MRI Classification
Phase 1.5: Dataset Splitting with Stratification
"""

import os
import numpy as np
import json
from pathlib import Path
from sklearn.model_selection import train_test_split
from collections import Counter
import shutil
from tqdm import tqdm


class DatasetSplitter:
    """Handles stratified splitting of dataset into train/val/test sets."""
    
    def __init__(self, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, random_state=42):
        """
        Initialize dataset splitter.
        
        Args:
            train_ratio (float): Proportion of training data (default: 0.70)
            val_ratio (float): Proportion of validation data (default: 0.15)
            test_ratio (float): Proportion of test data (default: 0.15)
            random_state (int): Random seed for reproducibility
        """
        # Validate ratios
        total = train_ratio + val_ratio + test_ratio
        assert abs(total - 1.0) < 1e-6, f"Ratios must sum to 1.0, got {total}"
        
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        self.random_state = random_state
    
    def get_file_paths_and_labels(self, data_dir):
        """
        Get all file paths and their corresponding labels.
        
        Args:
            data_dir (str): Directory containing class folders
            
        Returns:
            tuple: (file_paths, labels, class_names)
        """
        data_path = Path(data_dir)
        file_paths = []
        labels = []
        class_names = []
        
        # Get all class folders
        class_folders = sorted([f for f in data_path.iterdir() if f.is_dir()])
        
        for class_idx, class_folder in enumerate(class_folders):
            class_name = class_folder.name
            class_names.append(class_name)
            
            # Get all image files in this class
            image_files = list(class_folder.glob('*.npy')) + \
                         list(class_folder.glob('*.jpg')) + \
                         list(class_folder.glob('*.jpeg')) + \
                         list(class_folder.glob('*.png'))
            
            for image_file in image_files:
                file_paths.append(str(image_file))
                labels.append(class_idx)
        
        return file_paths, labels, class_names
    
    def split_dataset(self, data_dir, output_dir=None):
        """
        Split dataset into train, validation, and test sets with stratification.
        
        Args:
            data_dir (str): Input directory containing class folders
            output_dir (str, optional): Output directory for split data
            
        Returns:
            dict: Dictionary containing split information
        """
        print("Loading dataset...")
        file_paths, labels, class_names = self.get_file_paths_and_labels(data_dir)
        
        print(f"\nDataset Statistics:")
        print(f"Total samples: {len(file_paths)}")
        print(f"Number of classes: {len(class_names)}")
        print(f"Classes: {class_names}")
        
        # Count samples per class
        label_counts = Counter(labels)
        print("\nSamples per class:")
        for idx, class_name in enumerate(class_names):
            print(f"  {class_name}: {label_counts[idx]}")
        
        # Convert to numpy arrays for easier manipulation
        file_paths = np.array(file_paths)
        labels = np.array(labels)
        
        # First split: separate test set
        train_val_paths, test_paths, train_val_labels, test_labels = train_test_split(
            file_paths, labels,
            test_size=self.test_ratio,
            stratify=labels,
            random_state=self.random_state
        )
        
        # Second split: separate train and validation sets
        val_size_adjusted = self.val_ratio / (self.train_ratio + self.val_ratio)
        train_paths, val_paths, train_labels, val_labels = train_test_split(
            train_val_paths, train_val_labels,
            test_size=val_size_adjusted,
            stratify=train_val_labels,
            random_state=self.random_state
        )
        
        # Create split information dictionary
        split_info = {
            'train': {
                'paths': train_paths.tolist(),
                'labels': train_labels.tolist(),
                'size': len(train_paths)
            },
            'val': {
                'paths': val_paths.tolist(),
                'labels': val_labels.tolist(),
                'size': len(val_paths)
            },
            'test': {
                'paths': test_paths.tolist(),
                'labels': test_labels.tolist(),
                'size': len(test_paths)
            },
            'class_names': class_names,
            'num_classes': len(class_names)
        }
        
        # Print split statistics
        print("\n" + "="*50)
        print("Dataset Split Complete!")
        print("="*50)
        print(f"\nTrain set: {len(train_paths)} samples ({self.train_ratio*100:.1f}%)")
        print(f"Val set:   {len(val_paths)} samples ({self.val_ratio*100:.1f}%)")
        print(f"Test set:  {len(test_paths)} samples ({self.test_ratio*100:.1f}%)")
        
        # Print class distribution for each split
        for split_name, split_data in [('Train', train_labels), 
                                       ('Val', val_labels), 
                                       ('Test', test_labels)]:
            print(f"\n{split_name} set distribution:")
            split_counts = Counter(split_data)
            for idx, class_name in enumerate(class_names):
                count = split_counts[idx]
                percentage = (count / len(split_data)) * 100
                print(f"  {class_name}: {count} ({percentage:.1f}%)")
        
        # Save split information to JSON
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            split_info_path = output_path / 'split_info.json'
            with open(split_info_path, 'w') as f:
                json.dump(split_info, f, indent=2)
            print(f"\nSplit information saved to: {split_info_path}")
        
        return split_info
    
    def organize_split_folders(self, split_info, output_dir):
        """
        Organize files into train/val/test folder structure.
        
        Args:
            split_info (dict): Split information from split_dataset()
            output_dir (str): Output directory for organized data
        """
        output_path = Path(output_dir)
        class_names = split_info['class_names']
        
        print("\nOrganizing files into train/val/test folders...")
        
        for split_name in ['train', 'val', 'test']:
            print(f"\nProcessing {split_name} set...")
            
            split_data = split_info[split_name]
            paths = split_data['paths']
            labels = split_data['labels']
            
            # Create split folder with class subfolders
            for class_name in class_names:
                split_class_dir = output_path / split_name / class_name
                split_class_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy files to appropriate folders
            for file_path, label in tqdm(zip(paths, labels), 
                                        total=len(paths),
                                        desc=f"Copying {split_name}"):
                class_name = class_names[label]
                dest_dir = output_path / split_name / class_name
                
                # Get filename
                filename = Path(file_path).name
                dest_path = dest_dir / filename
                
                # Copy file
                shutil.copy2(file_path, dest_path)
        
        print("\n" + "="*50)
        print("Files organized successfully!")
        print(f"Output directory: {output_dir}")
        print("="*50)
    
    def load_split_info(self, split_info_path):
        """
        Load split information from JSON file.
        
        Args:
            split_info_path (str): Path to split_info.json
            
        Returns:
            dict: Split information dictionary
        """
        with open(split_info_path, 'r') as f:
            split_info = json.load(f)
        return split_info


def verify_split_balance(split_info):
    """
    Verify that the split maintains class balance.
    
    Args:
        split_info (dict): Split information dictionary
    """
    print("\nVerifying split balance...")
    class_names = split_info['class_names']
    
    for split_name in ['train', 'val', 'test']:
        labels = split_info[split_name]['labels']
        total = len(labels)
        
        print(f"\n{split_name.upper()} SET:")
        label_counts = Counter(labels)
        
        for idx, class_name in enumerate(class_names):
            count = label_counts[idx]
            percentage = (count / total) * 100
            print(f"  {class_name}: {count}/{total} ({percentage:.2f}%)")


if __name__ == "__main__":
    print("Dataset Splitting Module")
    print("=" * 50)
    
    # Example usage
    splitter = DatasetSplitter(
        train_ratio=0.70,
        val_ratio=0.15,
        test_ratio=0.15,
        random_state=42
    )
    
    # Define paths
    data_dir = "../data/processed"  # Directory with preprocessed images
    output_dir = "../data/splits"
    
    # Split dataset
    split_info = splitter.split_dataset(data_dir, output_dir)
    
    # Verify balance
    verify_split_balance(split_info)
    
    # Optionally organize into folders (uncomment if needed)
    # splitter.organize_split_folders(split_info, output_dir)
    
    print("\nDataset splitting completed successfully!")
