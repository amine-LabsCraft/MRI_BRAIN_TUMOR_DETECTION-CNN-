"""
Model Evaluation Script for Brain Tumor Classification
PyTorch Implementation with GPU Support
"""

import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from pathlib import Path
import sys
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))

from model_architecture import ResNet50Classifier
from data_loaders import create_data_loaders


def evaluate_model(model, data_loader, device, class_names):
    """
    Evaluate model on test set.
    
    Args:
        model: PyTorch model
        data_loader: Test data loader
        device: Device to run on
        class_names: List of class names
        
    Returns:
        dict: Evaluation metrics
    """
    model.eval()
    
    all_preds = []
    all_labels = []
    all_probs = []
    
    print("\nEvaluating model on test set...")
    
    with torch.no_grad():
        for inputs, labels in data_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            
            # Forward pass
            outputs = model(inputs)
            probs = torch.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
    
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_probs = np.array(all_probs)
    
    # Calculate accuracy
    accuracy = np.mean(all_preds == all_labels)
    
    # Classification report
    report = classification_report(
        all_labels, 
        all_preds, 
        target_names=class_names[:4],  # Only first 4 classes
        output_dict=True
    )
    
    # Confusion matrix
    cm = confusion_matrix(all_labels, all_preds)
    
    return {
        'accuracy': accuracy,
        'predictions': all_preds,
        'labels': all_labels,
        'probabilities': all_probs,
        'classification_report': report,
        'confusion_matrix': cm
    }


def plot_confusion_matrix(cm, class_names, save_path):
    """Plot and save confusion matrix."""
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm, 
        annot=True, 
        fmt='d', 
        cmap='Blues',
        xticklabels=class_names[:4],
        yticklabels=class_names[:4]
    )
    plt.title('Confusion Matrix', fontsize=16, fontweight='bold')
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Confusion matrix saved to: {save_path}")


def plot_class_performance(report, class_names, save_path):
    """Plot per-class performance metrics."""
    metrics = ['precision', 'recall', 'f1-score']
    classes = class_names[:4]
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for idx, metric in enumerate(metrics):
        values = [report[cls][metric] for cls in classes]
        axes[idx].bar(classes, values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        axes[idx].set_ylim([0, 1])
        axes[idx].set_title(metric.capitalize(), fontsize=14, fontweight='bold')
        axes[idx].set_ylabel('Score', fontsize=12)
        axes[idx].grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for i, v in enumerate(values):
            axes[idx].text(i, v + 0.02, f'{v:.3f}', ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Class performance plot saved to: {save_path}")


def main():
    """Main evaluation function."""
    print("\n" + "="*70)
    print("MODEL EVALUATION - PyTorch")
    print("="*70)
    
    # Setup paths
    base_dir = Path(__file__).parent
    models_dir = base_dir / 'models'
    results_dir = base_dir / 'results'
    results_dir.mkdir(exist_ok=True)
    
    # Find the latest model
    model_files = list(models_dir.glob('best_model_stage2.pth'))
    if not model_files:
        model_files = list(models_dir.glob('final_model_*.pth'))
    
    if not model_files:
        print("\n❌ No trained model found!")
        print("Please train the model first with: python train_pytorch.py")
        return
    
    model_path = sorted(model_files)[-1]
    print(f"\n✓ Loading model: {model_path.name}")
    
    # Check GPU
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"✓ Device: {device}")
    if torch.cuda.is_available():
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
    
    # Load data
    print("\n" + "="*70)
    print("LOADING TEST DATA")
    print("="*70)
    
    split_info_path = base_dir / 'data' / 'splits' / 'split_info.json'
    data_loaders, class_names = create_data_loaders(
        split_info_path=split_info_path,
        batch_size=32,
        image_size=(224, 224),
        num_workers=4
    )
    
    test_loader = data_loaders['test']
    
    # Load model
    print("\n" + "="*70)
    print("LOADING MODEL")
    print("="*70)
    
    model = ResNet50Classifier(
        num_classes=4,
        pretrained=False,
        dense_units=512,
        dropout_rate=0.4
    )
    
    # Load weights
    checkpoint = torch.load(model_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    
    print(f"✓ Model loaded successfully")
    if 'val_acc' in checkpoint:
        print(f"  Validation accuracy: {checkpoint['val_acc']:.4f}")
    
    # Evaluate
    print("\n" + "="*70)
    print("EVALUATING MODEL")
    print("="*70)
    
    results = evaluate_model(model, test_loader, device, class_names)
    
    # Print results
    print("\n" + "="*70)
    print("TEST SET RESULTS")
    print("="*70)
    print(f"\n✓ Overall Accuracy: {results['accuracy']:.4f} ({results['accuracy']*100:.2f}%)")
    
    print("\n" + "-"*70)
    print("Per-Class Performance:")
    print("-"*70)
    
    report = results['classification_report']
    for cls in class_names[:4]:
        metrics = report[cls]
        print(f"\n{cls.upper()}")
        print(f"  Precision: {metrics['precision']:.4f}")
        print(f"  Recall:    {metrics['recall']:.4f}")
        print(f"  F1-Score:  {metrics['f1-score']:.4f}")
        print(f"  Support:   {int(metrics['support'])}")
    
    print("\n" + "-"*70)
    print("Overall Metrics:")
    print("-"*70)
    print(f"Macro Avg Precision:  {report['macro avg']['precision']:.4f}")
    print(f"Macro Avg Recall:     {report['macro avg']['recall']:.4f}")
    print(f"Macro Avg F1-Score:   {report['macro avg']['f1-score']:.4f}")
    
    # Save visualizations
    print("\n" + "="*70)
    print("GENERATING VISUALIZATIONS")
    print("="*70)
    
    # Confusion matrix
    cm_path = results_dir / 'confusion_matrix.png'
    plot_confusion_matrix(results['confusion_matrix'], class_names, cm_path)
    
    # Class performance
    perf_path = results_dir / 'class_performance.png'
    plot_class_performance(report, class_names, perf_path)
    
    # Save results to CSV
    results_csv = results_dir / 'test_results.csv'
    df_results = pd.DataFrame({
        'True_Label': results['labels'],
        'Predicted_Label': results['predictions'],
        'Correct': results['labels'] == results['predictions']
    })
    
    # Add probability columns
    for i, cls in enumerate(class_names[:4]):
        df_results[f'Prob_{cls}'] = results['probabilities'][:, i]
    
    df_results.to_csv(results_csv, index=False)
    print(f"\n✓ Detailed results saved to: {results_csv}")
    
    # Save summary
    summary_path = results_dir / 'evaluation_summary.txt'
    with open(summary_path, 'w') as f:
        f.write("="*70 + "\n")
        f.write("MODEL EVALUATION SUMMARY\n")
        f.write("="*70 + "\n\n")
        f.write(f"Model: {model_path.name}\n")
        f.write(f"Test Samples: {len(results['labels'])}\n")
        f.write(f"Overall Accuracy: {results['accuracy']:.4f} ({results['accuracy']*100:.2f}%)\n\n")
        
        f.write("-"*70 + "\n")
        f.write("Per-Class Performance:\n")
        f.write("-"*70 + "\n\n")
        
        for cls in class_names[:4]:
            metrics = report[cls]
            f.write(f"{cls.upper()}\n")
            f.write(f"  Precision: {metrics['precision']:.4f}\n")
            f.write(f"  Recall:    {metrics['recall']:.4f}\n")
            f.write(f"  F1-Score:  {metrics['f1-score']:.4f}\n")
            f.write(f"  Support:   {int(metrics['support'])}\n\n")
        
        f.write("-"*70 + "\n")
        f.write("Confusion Matrix:\n")
        f.write("-"*70 + "\n\n")
        f.write(str(results['confusion_matrix']))
    
    print(f"✓ Summary saved to: {summary_path}")
    
    print("\n" + "="*70)
    print("✓ EVALUATION COMPLETED!")
    print("="*70)
    print(f"\nResults saved in: {results_dir}")
    print("\nGenerated files:")
    print(f"  1. {cm_path.name} - Confusion matrix heatmap")
    print(f"  2. {perf_path.name} - Per-class performance metrics")
    print(f"  3. {results_csv.name} - Detailed predictions")
    print(f"  4. {summary_path.name} - Text summary")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nEvaluation interrupted by user.")
    except Exception as e:
        print(f"\n\nError during evaluation: {e}")
        import traceback
        traceback.print_exc()
