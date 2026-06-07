"""
Script to fix the model by removing problematic pathlib objects
"""
import torch
import sys
import os
import pickle
import io

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
from model_architecture import ResNet50Classifier

# Create custom unpickler class
class PathedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        # Handle pathlib._local
        if module == 'pathlib._local':
            module = 'pathlib'
            name = 'Path'
        return super().find_class(module, name)
    
    def persistent_load(self, pid):
        # Handle persistent IDs - return them as strings if they are strings
        if isinstance(pid, str):
            return pid
        return None

model_path = 'models/final_model_20251106_142153.pth'
output_path = 'models/final_model_fixed.pth'

print("Loading model from " + model_path + "...")

try:
    # Use the custom unpickler by reading the file
    with open(model_path, 'rb') as f:
        checkpoint = PathedUnpickler(f).load()
    
    print("[+] Loaded checkpoint")
    
    # Extract just the model state dict
    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
        state_dict = checkpoint['model_state_dict']
        print("[+] Extracted model_state_dict with " + str(len(state_dict)) + " parameters")
    else:
        state_dict = checkpoint
        print("[+] Using checkpoint as state_dict")
    
    # Create a new checkpoint with only the state_dict (no config with Path objects)
    new_checkpoint = {
        'model_state_dict': state_dict,
        'num_classes': 4
    }
    
    # Save the fixed model
    torch.save(new_checkpoint, output_path)
    print("[+] Saved fixed model to " + output_path)
    
    # Verify it loads
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = ResNet50Classifier(num_classes=4)
    test_checkpoint = torch.load(output_path, map_location=device)
    model.load_state_dict(test_checkpoint['model_state_dict'])
    print("[+] Verified fixed model loads successfully!")
    
    # Update the original model path
    os.remove(model_path)
    os.rename(output_path, model_path)
    print("[+] Replaced original model with fixed version")
    print("[+] SUCCESS: Model file has been fixed!")
    
except Exception as e:
    print("[!] Error: " + str(e))
    import traceback
    traceback.print_exc()



