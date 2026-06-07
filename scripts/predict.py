"""
Single Image Prediction Script
Test the model on individual MRI images
"""

import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import numpy as np
from pathlib import Path
import sys
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))

from model_architecture import ResNet50Classifier


def load_model(model_path, device):
    """Load trained model."""
    model = ResNet50Classifier(
        num_classes=4,
        pretrained=False,
        dense_units=512,
        dropout_rate=0.4
    )
    
    checkpoint = torch.load(model_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    
    return model


def preprocess_image(image_path, image_size=(224, 224)):
    """Preprocess image for prediction."""
    # Load image
    if str(image_path).endswith('.npy'):
        # Load numpy file
        img_array = np.load(image_path)
        if img_array.dtype != np.float32:
            img_array = img_array.astype(np.float32)
        if img_array.max() > 1.0:
            img_array = img_array / 255.0
        img_array = (img_array * 255).astype(np.uint8)
        img = Image.fromarray(img_array)
    else:
        img = Image.open(image_path).convert('RGB')
    
    # Define transforms
    transform = transforms.Compose([
        transforms.Resize(image_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    img_tensor = transform(img).unsqueeze(0)  # Add batch dimension
    
    return img_tensor, img


def predict(model, image_tensor, device, class_names):
    """Make prediction on image."""
    image_tensor = image_tensor.to(device)
    
    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = F.softmax(outputs, dim=1)
        confidence, predicted_class = torch.max(probabilities, 1)
    
    predicted_class = predicted_class.item()
    confidence = confidence.item()
    probs = probabilities[0].cpu().numpy()
    
    return {
        'predicted_class': predicted_class,
        'predicted_label': class_names[predicted_class],
        'confidence': confidence,
        'all_probabilities': {class_names[i]: float(probs[i]) for i in range(len(class_names))}
    }


def print_prediction(result):
    """Pretty print prediction results."""
    print("\n" + "="*70)
    print("PREDICTION RESULTS")
    print("="*70)
    
    print(f"\n🎯 Predicted Class: {result['predicted_label'].upper()}")
    print(f"📊 Confidence: {result['confidence']*100:.2f}%")
    
    print("\n" + "-"*70)
    print("All Class Probabilities:")
    print("-"*70)
    
    # Sort by probability
    sorted_probs = sorted(result['all_probabilities'].items(), 
                         key=lambda x: x[1], reverse=True)
    
    for cls, prob in sorted_probs:
        bar_length = int(prob * 50)
        bar = '█' * bar_length + '░' * (50 - bar_length)
        print(f"{cls:15s} [{bar}] {prob*100:5.2f}%")


def main():
    """Main prediction function."""
    print("\n" + "="*70)
    print("BRAIN TUMOR MRI PREDICTION")
    print("="*70)
    
    # Setup
    base_dir = Path(__file__).parent
    models_dir = base_dir / 'models'
    
    # Load class names
    split_info_path = base_dir / 'data' / 'splits' / 'split_info.json'
    with open(split_info_path, 'r') as f:
        split_info = json.load(f)
    class_names = split_info['class_names'][:4]  # Only first 4
    
    # Find model
    model_files = list(models_dir.glob('best_model_stage2.pth'))
    if not model_files:
        model_files = list(models_dir.glob('final_model_*.pth'))
    
    if not model_files:
        print("\n❌ No trained model found!")
        print("Please train the model first with: python train_pytorch.py")
        return
    
    model_path = sorted(model_files)[-1]
    
    # Check GPU
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n✓ Device: {device}")
    if torch.cuda.is_available():
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
    
    # Load model
    print(f"✓ Loading model: {model_path.name}")
    model = load_model(model_path, device)
    print("✓ Model loaded successfully")
    
    # Get image path
    if len(sys.argv) > 1:
        image_path = Path(sys.argv[1])
    else:
        # Interactive mode
        print("\n" + "="*70)
        print("Enter image path (or 'q' to quit):")
        print("Example: data/processed/glioma/Te-gl_0010.npy")
        print("="*70)
        
        image_path_str = input("\nImage path: ").strip()
        
        if image_path_str.lower() == 'q':
            return
        
        image_path = Path(image_path_str)
    
    if not image_path.exists():
        print(f"\n❌ Image not found: {image_path}")
        return
    
    print(f"\n✓ Loading image: {image_path}")
    
    # Preprocess
    image_tensor, original_image = preprocess_image(image_path)
    print(f"✓ Image preprocessed: {image_tensor.shape}")
    
    # Predict
    print("✓ Making prediction...")
    result = predict(model, image_tensor, device, class_names)
    
    # Display results
    print_prediction(result)
    
    # Option to save visualization
    save = input("\n💾 Save prediction visualization? (y/n): ").strip().lower()
    
    if save == 'y':
        try:
            import matplotlib.pyplot as plt
            
            results_dir = base_dir / 'results'
            results_dir.mkdir(exist_ok=True)
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # Show image
            ax1.imshow(original_image)
            ax1.axis('off')
            ax1.set_title(f'Input Image\n{image_path.name}', fontsize=12, fontweight='bold')
            
            # Show probabilities
            probs = result['all_probabilities']
            classes = list(probs.keys())
            values = list(probs.values())
            colors = ['#2ecc71' if i == result['predicted_class'] else '#3498db' 
                     for i in range(len(classes))]
            
            bars = ax2.barh(classes, values, color=colors)
            ax2.set_xlabel('Probability', fontsize=12, fontweight='bold')
            ax2.set_xlim([0, 1])
            ax2.set_title(f'Prediction: {result["predicted_label"].upper()}\n'
                         f'Confidence: {result["confidence"]*100:.1f}%', 
                         fontsize=12, fontweight='bold')
            ax2.grid(axis='x', alpha=0.3)
            
            # Add value labels
            for bar, val in zip(bars, values):
                ax2.text(val + 0.02, bar.get_y() + bar.get_height()/2, 
                        f'{val*100:.1f}%', va='center', fontsize=10)
            
            plt.tight_layout()
            
            save_path = results_dir / f'prediction_{image_path.stem}.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"\n✓ Visualization saved to: {save_path}")
            
        except Exception as e:
            print(f"\n❌ Failed to save visualization: {e}")
    
    print("\n" + "="*70)
    print("✓ PREDICTION COMPLETED!")
    print("="*70)
    
    # Ask for another prediction
    if len(sys.argv) <= 1:
        another = input("\n🔄 Predict another image? (y/n): ").strip().lower()
        if another == 'y':
            print("\n" * 2)
            main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrediction interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
