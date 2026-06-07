"""
Data Loaders for Brain Tumor MRI Classification
PyTorch Implementation with GPU Support
"""

import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import numpy as np
import json
from pathlib import Path
from PIL import Image
from sklearn.utils.class_weight import compute_class_weight


class BrainTumorDataset(Dataset):
    """PyTorch Dataset for brain tumor MRI images."""
    
    def __init__(self, file_paths, labels, transform=None, image_size=(224, 224)):
        """
        Initialize dataset.
        
        Args:
            file_paths (list): List of image file paths
            labels (list): List of integer labels
            transform (callable): Optional transform to apply
            image_size (tuple): Target image size
        """
        self.file_paths = file_paths
        self.labels = labels
        self.transform = transform
        self.image_size = image_size
    
    def __len__(self):
        return len(self.file_paths)
    
    def __getitem__(self, idx):
        """Get a single sample."""
        # Load image
        img_path = self.file_paths[idx]
        
        if img_path.endswith('.npy'):
            # Load .npy file
            img = np.load(img_path)
            # Ensure it's float32 and in range [0, 1]
            if img.dtype != np.float32:
                img = img.astype(np.float32)
            if img.max() > 1.0:
                img = img / 255.0
            # Convert to PIL Image
            img = (img * 255).astype(np.uint8)
            img = Image.fromarray(img)
        else:
            # Load regular image file
            img = Image.open(img_path).convert('RGB')
        
        # Apply transforms
        if self.transform:
            img = self.transform(img)
        
        # Get label
        label = torch.tensor(self.labels[idx], dtype=torch.long)
        
        return img, label


def get_transforms(augment=True, image_size=(224, 224)):
    """
    Get image transforms for training/validation.
    
    Args:
        augment (bool): Whether to apply augmentation
        image_size (tuple): Target image size
        
    Returns:
        torchvision.transforms.Compose: Composed transforms
    """
    if augment:
        # Training transforms with augmentation
        transform = transforms.Compose([
            transforms.Resize(image_size),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.5),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    else:
        # Validation/test transforms without augmentation
        transform = transforms.Compose([
            transforms.Resize(image_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    return transform


def create_data_loaders(split_info_path, batch_size=32, image_size=(224, 224), 
                       num_workers=4, pin_memory=True):
    """
    Create PyTorch DataLoaders for train/val/test splits.
    
    Args:
        split_info_path (str): Path to split_info.json
        batch_size (int): Batch size
        image_size (tuple): Target image size
        num_workers (int): Number of workers for data loading
        pin_memory (bool): Whether to pin memory (True for GPU)
        
    Returns:
        dict: Dictionary containing 'train', 'val', 'test' DataLoaders
    """
    # Load split information
    with open(split_info_path, 'r') as f:
        split_info = json.load(f)
    
    class_names = split_info['class_names']
    
    print("\n" + "="*60)
    print("Creating PyTorch DataLoaders")
    print("="*60)
    print(f"Classes: {class_names}")
    print(f"Batch size: {batch_size}")
    print(f"Image size: {image_size}")
    print(f"Num workers: {num_workers}")
    print(f"Pin memory: {pin_memory}")
    
    data_loaders = {}
    
    for split in ['train', 'val', 'test']:
        split_data = split_info[split]
        file_paths = split_data['paths']
        labels = split_data['labels']
        
        # Get appropriate transforms
        augment = (split == 'train')
        transform = get_transforms(augment=augment, image_size=image_size)
        
        # Create dataset
        dataset = BrainTumorDataset(
            file_paths=file_paths,
            labels=labels,
            transform=transform,
            image_size=image_size
        )
        
        # Create data loader
        loader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=(split == 'train'),
            num_workers=num_workers,
            pin_memory=pin_memory,
            drop_last=(split == 'train')  # Drop last incomplete batch for training
        )
        
        data_loaders[split] = loader
        
        print(f"\n{split.capitalize()} set:")
        print(f"  Samples: {len(dataset)}")
        print(f"  Batches: {len(loader)}")
        print(f"  Augmentation: {augment}")
    
    return data_loaders, class_names


def compute_class_weights(split_info_path, num_classes=4):
    """
    Compute class weights for imbalanced datasets.
    
    Args:
        split_info_path (str): Path to split_info.json
        num_classes (int): Number of classes
        
    Returns:
        torch.Tensor: Class weights
    """
    # Load split information
    with open(split_info_path, 'r') as f:
        split_info = json.load(f)
    
    # Get training labels
    train_labels = np.array(split_info['train']['labels'])
    
    # Compute class weights
    class_weights = compute_class_weight(
        class_weight='balanced',
        classes=np.arange(num_classes),
        y=train_labels
    )
    
    class_weights = torch.tensor(class_weights, dtype=torch.float32)
    
    print("\n" + "="*60)
    print("Class Weights (for imbalanced data)")
    print("="*60)
    for i, (class_name, weight) in enumerate(zip(split_info['class_names'], class_weights)):
        count = np.sum(train_labels == i)
        print(f"{class_name:15s}: weight={weight:.4f}, samples={count}")
    
    return class_weights


if __name__ == "__main__":
    # Test data loaders
    print("\nTesting PyTorch DataLoaders...")
    
    # Paths
    base_dir = Path(__file__).parent.parent
    split_info_path = base_dir / "data" / "splits" / "split_info.json"
    
    # Create data loaders
    data_loaders, class_names = create_data_loaders(
        split_info_path=split_info_path,
        batch_size=8,
        image_size=(224, 224),
        num_workers=2
    )
    
    # Test loading a batch
    print("\n" + "="*60)
    print("Testing batch loading...")
    print("="*60)
    
    train_loader = data_loaders['train']
    images, labels = next(iter(train_loader))
    
    print(f"\nBatch loaded successfully!")
    print(f"  Images shape: {images.shape}")
    print(f"  Images dtype: {images.dtype}")
    print(f"  Images range: [{images.min():.3f}, {images.max():.3f}]")
    print(f"  Labels shape: {labels.shape}")
    print(f"  Labels dtype: {labels.dtype}")
    print(f"  Label values: {labels.tolist()}")
    
    # Test GPU transfer
    if torch.cuda.is_available():
        device = torch.device('cuda')
        images_gpu = images.to(device)
        labels_gpu = labels.to(device)
        print(f"\n✓ GPU transfer successful!")
        print(f"  Images device: {images_gpu.device}")
        print(f"  Labels device: {labels_gpu.device}")
    
    # Compute class weights
    class_weights = compute_class_weights(split_info_path)
    
    print("\n✓ DataLoader test completed successfully!")
