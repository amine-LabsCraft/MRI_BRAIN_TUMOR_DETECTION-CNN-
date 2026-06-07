"""
Model Trainer for Brain Tumor MRI Classification
PyTorch Implementation with GPU Support and Two-Stage Training
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import json


class PyTorchTrainer:
    """Two-stage trainer for brain tumor classification."""
    
    def __init__(self, model, data_loaders, config, device='cuda'):
        """
        Initialize trainer.
        
        Args:
            model (nn.Module): PyTorch model
            data_loaders (dict): Dict with 'train', 'val', 'test' DataLoaders
            config (dict): Training configuration
            device (str): Device to train on ('cuda' or 'cpu')
        """
        self.model = model
        self.data_loaders = data_loaders
        self.config = config
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        
        # Move model to device
        self.model = self.model.to(self.device)
        
        # Training history
        self.history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': []
        }
        
        # Best model tracking
        self.best_val_loss = float('inf')
        self.best_model_path = None
        
        print("\n" + "="*60)
        print("PyTorch Trainer Initialized")
        print("="*60)
        print(f"Device: {self.device}")
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        print(f"Batch size: {config['batch_size']}")
    
    def train_epoch(self, optimizer, criterion, epoch, num_epochs):
        """Train for one epoch."""
        self.model.train()
        
        running_loss = 0.0
        running_corrects = 0
        total_samples = 0
        
        train_loader = self.data_loaders['train']
        
        # Progress bar
        pbar = tqdm(train_loader, desc=f'Epoch {epoch}/{num_epochs} [Train]')
        
        for batch_idx, (inputs, labels) in enumerate(pbar):
            # Move to device
            inputs = inputs.to(self.device)
            labels = labels.to(self.device)
            
            # Zero gradients
            optimizer.zero_grad()
            
            # Forward pass
            outputs = self.model(inputs)
            loss = criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            # Statistics
            _, preds = torch.max(outputs, 1)
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)
            total_samples += inputs.size(0)
            
            # Update progress bar
            current_loss = running_loss / total_samples
            current_acc = running_corrects.double() / total_samples
            pbar.set_postfix({
                'loss': f'{current_loss:.4f}',
                'acc': f'{current_acc:.4f}'
            })
        
        epoch_loss = running_loss / total_samples
        epoch_acc = running_corrects.double() / total_samples
        
        return epoch_loss, epoch_acc.item()
    
    def validate_epoch(self, criterion, epoch, num_epochs):
        """Validate for one epoch."""
        self.model.eval()
        
        running_loss = 0.0
        running_corrects = 0
        total_samples = 0
        
        val_loader = self.data_loaders['val']
        
        # Progress bar
        pbar = tqdm(val_loader, desc=f'Epoch {epoch}/{num_epochs} [Val]')
        
        with torch.no_grad():
            for inputs, labels in pbar:
                # Move to device
                inputs = inputs.to(self.device)
                labels = labels.to(self.device)
                
                # Forward pass
                outputs = self.model(inputs)
                loss = criterion(outputs, labels)
                
                # Statistics
                _, preds = torch.max(outputs, 1)
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)
                total_samples += inputs.size(0)
                
                # Update progress bar
                current_loss = running_loss / total_samples
                current_acc = running_corrects.double() / total_samples
                pbar.set_postfix({
                    'loss': f'{current_loss:.4f}',
                    'acc': f'{current_acc:.4f}'
                })
        
        epoch_loss = running_loss / total_samples
        epoch_acc = running_corrects.double() / total_samples
        
        return epoch_loss, epoch_acc.item()
    
    def train_stage(self, stage_num, num_epochs, learning_rate, weight_decay=1e-4):
        """
        Train a single stage.
        
        Args:
            stage_num (int): Stage number (1 or 2)
            num_epochs (int): Number of epochs
            learning_rate (float): Learning rate
            weight_decay (float): Weight decay for regularization
        """
        print("\n" + "="*70)
        print(f"STAGE {stage_num} TRAINING")
        print("="*70)
        
        # Setup optimizer and criterion
        trainable_params = [p for p in self.model.parameters() if p.requires_grad]
        optimizer = optim.Adam(trainable_params, lr=learning_rate, weight_decay=weight_decay)
        criterion = nn.CrossEntropyLoss()
        
        # Learning rate scheduler (PyTorch ReduceLROnPlateau doesn't have verbose parameter)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=3
        )
        
        print(f"Optimizer: Adam (lr={learning_rate}, weight_decay={weight_decay})")
        print(f"Trainable parameters: {sum(p.numel() for p in trainable_params):,}")
        print(f"Training for {num_epochs} epochs...")
        
        # Training loop
        for epoch in range(1, num_epochs + 1):
            # Train
            train_loss, train_acc = self.train_epoch(optimizer, criterion, epoch, num_epochs)
            
            # Validate
            val_loss, val_acc = self.validate_epoch(criterion, epoch, num_epochs)
            
            # Update learning rate
            scheduler.step(val_loss)
            
            # Save history
            self.history['train_loss'].append(train_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_loss'].append(val_loss)
            self.history['val_acc'].append(val_acc)
            
            # Print epoch summary
            print(f"\nEpoch {epoch}/{num_epochs}:")
            print(f"  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f}")
            print(f"  Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.4f}")
            
            # Save best model
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                self.save_checkpoint(f'best_model_stage{stage_num}.pth', epoch, val_loss, val_acc)
                print(f"  ✓ Best model saved (val_loss: {val_loss:.4f})")
        
        print(f"\n✓ Stage {stage_num} training complete!")
    
    def train_two_stages(self):
        """Execute two-stage training strategy."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("\n" + "="*70)
        print("TWO-STAGE TRAINING STRATEGY")
        print("="*70)
        print("Stage 1: Train classifier head with frozen base model")
        print("Stage 2: Fine-tune entire network with lower learning rate")
        print("="*70)
        
        # STAGE 1: Frozen base model
        print("\nPreparing Stage 1...")
        self.model.freeze_base_layers()
        
        stage1_epochs = self.config.get('stage1_epochs', 20)
        stage1_lr = self.config.get('stage1_lr', 1e-3)
        
        self.train_stage(
            stage_num=1,
            num_epochs=stage1_epochs,
            learning_rate=stage1_lr,
            weight_decay=1e-4
        )
        
        # STAGE 2: Unfreeze and fine-tune
        if self.config.get('stage2_epochs', 30) > 0:
            print("\nPreparing Stage 2...")
            num_layers_unfreeze = self.config.get('unfreeze_layers', 30)
            self.model.unfreeze_base_layers(num_layers=num_layers_unfreeze)
            
            stage2_epochs = self.config.get('stage2_epochs', 30)
            stage2_lr = self.config.get('stage2_lr', 1e-4)
            
            self.train_stage(
                stage_num=2,
                num_epochs=stage2_epochs,
                learning_rate=stage2_lr,
                weight_decay=1e-4
            )
        
        # Save final model
        final_model_path = self.config['models_dir'] / f'final_model_{timestamp}.pth'
        self.save_checkpoint(final_model_path, stage2_epochs, self.history['val_loss'][-1], 
                           self.history['val_acc'][-1])
        
        # Save training history
        self.save_history(timestamp)
        
        print("\n" + "="*70)
        print("✓ TWO-STAGE TRAINING COMPLETED!")
        print("="*70)
        print(f"Best validation loss: {self.best_val_loss:.4f}")
        print(f"Best model: {self.best_model_path}")
        print(f"Final model: {final_model_path}")
    
    def save_checkpoint(self, filename, epoch, val_loss, val_acc):
        """Save model checkpoint."""
        filepath = self.config['models_dir'] / filename
        self.config['models_dir'].mkdir(parents=True, exist_ok=True)
        
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'val_loss': val_loss,
            'val_acc': val_acc,
            'config': self.config
        }, filepath)
        
        self.best_model_path = filepath
    
    def save_history(self, timestamp):
        """Save training history to CSV."""
        logs_dir = self.config['logs_dir']
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        history_df = pd.DataFrame(self.history)
        history_path = logs_dir / f'training_history_{timestamp}.csv'
        history_df.to_csv(history_path, index=False)
        
        print(f"\nTraining history saved to: {history_path}")


def get_default_config():
    """Get default training configuration."""
    base_dir = Path(__file__).parent.parent
    
    config = {
        # Paths
        'data_dir': base_dir / 'data',
        'models_dir': base_dir / 'models',
        'logs_dir': base_dir / 'logs',
        'split_info_path': base_dir / 'data' / 'splits' / 'split_info.json',
        
        # Training parameters
        'batch_size': 24,
        'image_size': (224, 224),
        'num_classes': 4,
        'num_workers': 4,
        
        # Stage 1: Frozen base
        'stage1_epochs': 20,
        'stage1_lr': 1e-3,
        
        # Stage 2: Fine-tuning
        'stage2_epochs': 30,
        'stage2_lr': 1e-4,
        'unfreeze_layers': 30,
        
        # Model architecture
        'pretrained': True,
        'dense_units': 512,
        'dropout_rate': 0.4,
    }
    
    return config


if __name__ == "__main__":
    print("\nTesting PyTorch Trainer...")
    
    # Import required modules
    from model_architecture import create_model
    from data_loaders import create_data_loaders
    
    # Get configuration
    config = get_default_config()
    
    # Create data loaders
    print("\nCreating data loaders...")
    data_loaders, class_names = create_data_loaders(
        split_info_path=config['split_info_path'],
        batch_size=config['batch_size'],
        image_size=config['image_size'],
        num_workers=config['num_workers']
    )
    
    # Create model
    print("\nCreating model...")
    model = create_model(
        num_classes=config['num_classes'],
        pretrained=config['pretrained'],
        dense_units=config['dense_units'],
        dropout_rate=config['dropout_rate'],
        freeze_base=True
    )
    
    # Create trainer
    print("\nCreating trainer...")
    trainer = PyTorchTrainer(
        model=model,
        data_loaders=data_loaders,
        config=config,
        device='cuda'
    )
    
    # Test single epoch
    print("\nTesting single training epoch...")
    config['stage1_epochs'] = 1
    config['stage2_epochs'] = 0
    
    trainer.train_two_stages()
    
    print("\n✓ Trainer test completed successfully!")
