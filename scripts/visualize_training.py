"""
Training History Visualization
Visualize loss and accuracy curves from training
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (15, 10)


def plot_training_history(history_path, save_dir):
    """
    Plot training history with loss and accuracy curves.
    
    Args:
        history_path: Path to training history CSV
        save_dir: Directory to save plots
    """
    # Load history
    df = pd.read_csv(history_path)
    
    print(f"\n✓ Loaded training history: {len(df)} epochs")
    print(f"  Columns: {list(df.columns)}")
    
    # Create figure with 2x2 subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    epochs = np.arange(1, len(df) + 1)
    
    # Stage boundaries (assuming 20 epochs stage 1, rest stage 2)
    stage1_end = 20 if len(df) > 20 else len(df)
    
    # Plot 1: Training & Validation Loss
    ax1 = axes[0, 0]
    ax1.plot(epochs, df['train_loss'], 'b-', linewidth=2, label='Training Loss', marker='o', markersize=4)
    ax1.plot(epochs, df['val_loss'], 'r-', linewidth=2, label='Validation Loss', marker='s', markersize=4)
    ax1.axvline(x=stage1_end, color='gray', linestyle='--', linewidth=1.5, alpha=0.7, label='Stage 1/2 Boundary')
    ax1.set_xlabel('Epoch', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Loss', fontsize=12, fontweight='bold')
    ax1.set_title('Training and Validation Loss', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Training & Validation Accuracy
    ax2 = axes[0, 1]
    ax2.plot(epochs, df['train_acc'], 'b-', linewidth=2, label='Training Accuracy', marker='o', markersize=4)
    ax2.plot(epochs, df['val_acc'], 'r-', linewidth=2, label='Validation Accuracy', marker='s', markersize=4)
    ax2.axvline(x=stage1_end, color='gray', linestyle='--', linewidth=1.5, alpha=0.7, label='Stage 1/2 Boundary')
    ax2.set_xlabel('Epoch', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Accuracy', fontsize=12, fontweight='bold')
    ax2.set_title('Training and Validation Accuracy', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([0, 1.05])
    
    # Plot 3: Loss Comparison (Train vs Val)
    ax3 = axes[1, 0]
    ax3.scatter(df['train_loss'], df['val_loss'], c=epochs, cmap='viridis', s=100, alpha=0.6)
    ax3.plot([df['train_loss'].min(), df['train_loss'].max()], 
             [df['train_loss'].min(), df['train_loss'].max()], 
             'k--', linewidth=1, alpha=0.5, label='Perfect Fit')
    ax3.set_xlabel('Training Loss', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Validation Loss', fontsize=12, fontweight='bold')
    ax3.set_title('Training vs Validation Loss', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    cbar = plt.colorbar(ax3.collections[0], ax=ax3)
    cbar.set_label('Epoch', fontsize=10)
    
    # Plot 4: Accuracy Comparison (Train vs Val)
    ax4 = axes[1, 1]
    ax4.scatter(df['train_acc'], df['val_acc'], c=epochs, cmap='viridis', s=100, alpha=0.6)
    ax4.plot([df['train_acc'].min(), 1], [df['train_acc'].min(), 1], 
             'k--', linewidth=1, alpha=0.5, label='Perfect Fit')
    ax4.set_xlabel('Training Accuracy', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Validation Accuracy', fontsize=12, fontweight='bold')
    ax4.set_title('Training vs Validation Accuracy', fontsize=14, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)
    cbar = plt.colorbar(ax4.collections[0], ax=ax4)
    cbar.set_label('Epoch', fontsize=10)
    
    plt.tight_layout()
    
    # Save plot
    plot_path = save_dir / 'training_history.png'
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Training history plot saved to: {plot_path}")
    plt.close()
    
    # Create summary statistics
    print("\n" + "="*70)
    print("TRAINING SUMMARY")
    print("="*70)
    
    print(f"\nStage 1 (Epochs 1-{stage1_end}):")
    stage1_df = df.iloc[:stage1_end]
    print(f"  Best Val Loss: {stage1_df['val_loss'].min():.4f} (Epoch {stage1_df['val_loss'].idxmin() + 1})")
    print(f"  Best Val Acc:  {stage1_df['val_acc'].max():.4f} (Epoch {stage1_df['val_acc'].idxmax() + 1})")
    print(f"  Final Val Acc: {stage1_df['val_acc'].iloc[-1]:.4f}")
    
    if len(df) > stage1_end:
        print(f"\nStage 2 (Epochs {stage1_end + 1}-{len(df)}):")
        stage2_df = df.iloc[stage1_end:]
        print(f"  Best Val Loss: {stage2_df['val_loss'].min():.4f} (Epoch {stage2_df['val_loss'].idxmin() + stage1_end + 1})")
        print(f"  Best Val Acc:  {stage2_df['val_acc'].max():.4f} (Epoch {stage2_df['val_acc'].idxmax() + stage1_end + 1})")
        print(f"  Final Val Acc: {stage2_df['val_acc'].iloc[-1]:.4f}")
    
    print(f"\nOverall:")
    print(f"  Best Val Loss: {df['val_loss'].min():.4f} (Epoch {df['val_loss'].idxmin() + 1})")
    print(f"  Best Val Acc:  {df['val_acc'].max():.4f} (Epoch {df['val_acc'].idxmax() + 1})")
    print(f"  Final Val Acc: {df['val_acc'].iloc[-1]:.4f}")
    print(f"  Improvement:   {(df['val_acc'].iloc[-1] - df['val_acc'].iloc[0]) * 100:.2f}%")


def main():
    """Main function."""
    print("\n" + "="*70)
    print("TRAINING HISTORY VISUALIZATION")
    print("="*70)
    
    # Setup paths (resolved relative to project root)
    base_dir = Path(__file__).resolve().parent.parent
    logs_dir = base_dir / 'logs'
    results_dir = base_dir / 'results'
    results_dir.mkdir(exist_ok=True)
    
    # Find latest training history
    history_files = list(logs_dir.glob('training_history_*.csv'))
    
    if not history_files:
        print("\n❌ No training history found!")
        print("Please train the model first with: python scripts/train.py")
        return
    
    history_path = sorted(history_files)[-1]
    print(f"\n✓ Found training history: {history_path.name}")
    
    # Plot
    plot_training_history(history_path, results_dir)
    
    print("\n" + "="*70)
    print("✓ VISUALIZATION COMPLETED!")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nVisualization interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
