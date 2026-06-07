"""
Model Architecture for Brain Tumor MRI Classification
Phase 2.1 - 2.2: ResNet50 Base Model + Custom Classifier Head
PyTorch Implementation with GPU Support
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models
import json
from pathlib import Path


class ResNet50Classifier(nn.Module):
    """ResNet50-based classifier for brain tumor detection."""
    
    def __init__(self, num_classes=4, pretrained=True, dense_units=512, dropout_rate=0.4):
        """
        Initialize ResNet50 classifier.
        
        Args:
            num_classes (int): Number of output classes
            pretrained (bool): Use pretrained ResNet50 weights
            dense_units (int): Number of units in dense layer
            dropout_rate (float): Dropout rate
        """
        super(ResNet50Classifier, self).__init__()
        
        self.num_classes = num_classes
        self.pretrained = pretrained
        self.dense_units = dense_units
        self.dropout_rate = dropout_rate
        
        # Load pretrained ResNet50
        weights = models.ResNet50_Weights.IMAGENET1K_V1 if pretrained else None
        self.base_model = models.resnet50(weights=weights)
        
        # Get the number of input features for the classifier
        num_features = self.base_model.fc.in_features
        
        # Replace the final fully connected layer with custom head
        self.base_model.fc = nn.Identity()  # Remove original classifier
        
        # Custom classifier head
        self.classifier = nn.Sequential(
            nn.Linear(num_features, dense_units),
            nn.ReLU(),
            nn.BatchNorm1d(dense_units),
            nn.Dropout(dropout_rate),
            nn.Linear(dense_units, num_classes)
        )
        
        print("\n" + "="*60)
        print("ResNet50 Classifier Initialized (PyTorch)")
        print("="*60)
        print(f"Num classes: {num_classes}")
        print(f"Pretrained: {pretrained}")
        print(f"Dense units: {dense_units}")
        print(f"Dropout rate: {dropout_rate}")
    
    def forward(self, x):
        """Forward pass through the network."""
        x = self.base_model(x)
        x = self.classifier(x)
        return x
    
    def freeze_base_layers(self):
        """Freeze all ResNet50 base layers (Stage 1 training)."""
        print("\nFreezing ResNet50 base layers...")
        for name, param in self.base_model.named_parameters():
            param.requires_grad = False
        
        # Classifier head remains trainable
        trainable_params = sum(p.numel() for p in self.classifier.parameters() if p.requires_grad)
        frozen_params = sum(p.numel() for p in self.base_model.parameters())
        
        print(f"Frozen parameters: {frozen_params:,}")
        print(f"Trainable parameters: {trainable_params:,}")
    
    def unfreeze_base_layers(self, num_layers=30):
        """
        Unfreeze last N layers of base model for fine-tuning (Stage 2).
        
        Args:
            num_layers (int): Number of layers to unfreeze from the end
        """
        print(f"\nUnfreezing last {num_layers} layers for fine-tuning...")
        
        # Get all base model parameters
        base_params = list(self.base_model.parameters())
        total_params = len(base_params)
        
        # Unfreeze last N layers
        for param in base_params[-num_layers:]:
            param.requires_grad = True
        
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        total = sum(p.numel() for p in self.parameters())
        
        print(f"Total parameters: {total:,}")
        print(f"Trainable parameters: {trainable_params:,}")
        print(f"Frozen parameters: {total - trainable_params:,}")
    
    def get_model_summary(self):
        """Print model summary."""
        print("\n" + "="*60)
        print("Model Summary")
        print("="*60)
        
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        
        print(f"Total parameters: {total_params:,}")
        print(f"Trainable parameters: {trainable_params:,}")
        print(f"Non-trainable parameters: {total_params - trainable_params:,}")
        print("\nModel architecture:")
        print(self)
    
    def save_model(self, filepath):
        """
        Save model weights.
        
        Args:
            filepath (str): Path to save the model
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        torch.save({
            'model_state_dict': self.state_dict(),
            'num_classes': self.num_classes,
            'dense_units': self.dense_units,
            'dropout_rate': self.dropout_rate
        }, filepath)
        
        print(f"\nModel saved to: {filepath}")
    
    def load_model(self, filepath, device='cuda'):
        """
        Load model weights.
        
        Args:
            filepath (str): Path to load the model from
            device (str): Device to load model to ('cuda' or 'cpu')
        """
        checkpoint = torch.load(filepath, map_location=device)
        self.load_state_dict(checkpoint['model_state_dict'])
        
        print(f"\nModel loaded from: {filepath}")
        print(f"Device: {device}")


def create_model(num_classes=4, pretrained=True, dense_units=512, dropout_rate=0.4, freeze_base=True):
    """
    Create and configure ResNet50 classifier.
    
    Args:
        num_classes (int): Number of output classes
        pretrained (bool): Use pretrained weights
        dense_units (int): Number of units in dense layer
        dropout_rate (float): Dropout rate
        freeze_base (bool): Whether to freeze base layers initially
        
    Returns:
        ResNet50Classifier: Configured model
    """
    model = ResNet50Classifier(
        num_classes=num_classes,
        pretrained=pretrained,
        dense_units=dense_units,
        dropout_rate=dropout_rate
    )
    
    if freeze_base:
        model.freeze_base_layers()
    
    return model


def get_optimizer_and_loss(model, learning_rate=1e-4, weight_decay=1e-4):
    """
    Create optimizer and loss function.
    
    Args:
        model (nn.Module): Model to optimize
        learning_rate (float): Learning rate
        weight_decay (float): Weight decay for regularization
        
    Returns:
        tuple: (optimizer, criterion)
    """
    # Only optimize trainable parameters
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    
    optimizer = optim.Adam(trainable_params, lr=learning_rate, weight_decay=weight_decay)
    criterion = nn.CrossEntropyLoss()
    
    print("\n" + "="*60)
    print("Optimizer and Loss Function")
    print("="*60)
    print(f"Optimizer: Adam")
    print(f"  Learning rate: {learning_rate}")
    print(f"  Weight decay: {weight_decay}")
    print(f"  Trainable parameters: {len(trainable_params)}")
    print(f"Loss function: CrossEntropyLoss")
    
    return optimizer, criterion


if __name__ == "__main__":
    # Test model creation
    print("\nTesting ResNet50Classifier...")
    
    # Check GPU availability
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\nDevice: {device}")
    
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    
    # Create model
    model = create_model(num_classes=4, freeze_base=True)
    model = model.to(device)
    
    # Print summary
    model.get_model_summary()
    
    # Test forward pass
    dummy_input = torch.randn(2, 3, 224, 224).to(device)
    output = model(dummy_input)
    print(f"\nTest forward pass:")
    print(f"  Input shape: {dummy_input.shape}")
    print(f"  Output shape: {output.shape}")
    print(f"  Output device: {output.device}")
    
    print("\n✓ Model test completed successfully!")
