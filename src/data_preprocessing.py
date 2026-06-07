"""
Data Preprocessing Module for Brain Tumor MRI Classification
Phase 1.2 - 1.3: Data Cleaning and Preprocessing
"""

import os
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from tqdm import tqdm


class DataPreprocessor:
    """Handles data cleaning and preprocessing for MRI images."""
    
    def __init__(self, target_size=256, crop_size=224):
        """
        Initialize preprocessor with image size parameters.
        
        Args:
            target_size (int): Initial resize dimension (256x256)
            crop_size (int): Final center crop dimension (224x224)
        """
        self.target_size = target_size
        self.crop_size = crop_size
        
        # ImageNet normalization parameters
        self.mean = np.array([0.485, 0.456, 0.406])
        self.std = np.array([0.229, 0.224, 0.225])
    
    def is_valid_image(self, image_path):
        """
        Check if image is valid and can be loaded.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            bool: True if image is valid, False otherwise
        """
        try:
            img = Image.open(image_path)
            img.verify()
            return True
        except Exception as e:
            print(f"Invalid image {image_path}: {e}")
            return False
    
    def convert_to_rgb(self, image):
        """
        Convert image to RGB format.
        
        Args:
            image (PIL.Image or numpy.ndarray): Input image
            
        Returns:
            numpy.ndarray: RGB image
        """
        if isinstance(image, Image.Image):
            # Convert PIL Image to RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return np.array(image)
        elif isinstance(image, np.ndarray):
            # Convert numpy array to RGB
            if len(image.shape) == 2:  # Grayscale
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 4:  # RGBA
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            return image
        else:
            raise ValueError("Image must be PIL Image or numpy array")
    
    def resize_image(self, image):
        """
        Resize image to target size.
        
        Args:
            image (numpy.ndarray): Input image
            
        Returns:
            numpy.ndarray: Resized image
        """
        return cv2.resize(image, (self.target_size, self.target_size), 
                         interpolation=cv2.INTER_LINEAR)
    
    def center_crop(self, image):
        """
        Apply center crop to image.
        
        Args:
            image (numpy.ndarray): Input image
            
        Returns:
            numpy.ndarray: Center-cropped image
        """
        h, w = image.shape[:2]
        start_h = (h - self.crop_size) // 2
        start_w = (w - self.crop_size) // 2
        
        return image[start_h:start_h + self.crop_size, 
                    start_w:start_w + self.crop_size]
    
    def normalize_pixel_values(self, image):
        """
        Normalize pixel values to [0, 1] range.
        
        Args:
            image (numpy.ndarray): Input image (0-255)
            
        Returns:
            numpy.ndarray: Normalized image (0-1)
        """
        return image.astype(np.float32) / 255.0
    
    def apply_imagenet_normalization(self, image):
        """
        Apply ImageNet mean-std normalization.
        
        Args:
            image (numpy.ndarray): Normalized image (0-1)
            
        Returns:
            numpy.ndarray: Normalized image with ImageNet statistics
        """
        return (image - self.mean) / self.std
    
    def preprocess_image(self, image_path, apply_normalization=True):
        """
        Complete preprocessing pipeline for a single image.
        
        Args:
            image_path (str): Path to the image
            apply_normalization (bool): Whether to apply ImageNet normalization
            
        Returns:
            numpy.ndarray or None: Preprocessed image or None if invalid
        """
        try:
            # Load image
            image = Image.open(image_path)
            
            # Convert to RGB
            image = self.convert_to_rgb(image)
            
            # Resize
            image = self.resize_image(image)
            
            # Center crop
            image = self.center_crop(image)
            
            # Normalize pixel values
            image = self.normalize_pixel_values(image)
            
            # Apply ImageNet normalization (optional)
            if apply_normalization:
                image = self.apply_imagenet_normalization(image)
            
            return image
            
        except Exception as e:
            print(f"Error preprocessing {image_path}: {e}")
            return None
    
    def preprocess_dataset(self, input_dir, output_dir, apply_normalization=True):
        """
        Preprocess entire dataset directory.
        
        Args:
            input_dir (str): Input directory containing class folders or Training/Testing folders
            output_dir (str): Output directory for preprocessed images
            apply_normalization (bool): Whether to apply ImageNet normalization
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Check if we have Training/Testing structure
        subfolders = [f.name.lower() for f in input_path.iterdir() if f.is_dir()]
        if 'training' in subfolders or 'traning' in subfolders or 'testing' in subfolders:
            # Dataset has Training/Testing structure - process both
            print("\nDetected Training/Testing folder structure")
            class_folders = []
            for split_folder in input_path.iterdir():
                if split_folder.is_dir():
                    # Get class folders inside Training/Testing
                    class_folders.extend([f for f in split_folder.iterdir() if f.is_dir()])
        else:
            # Direct class folders
            class_folders = [f for f in input_path.iterdir() if f.is_dir()]
        
        total_processed = 0
        total_failed = 0
        
        for class_folder in class_folders:
            class_name = class_folder.name
            print(f"\nProcessing class: {class_name}")
            
            # Create output class folder
            output_class_folder = output_path / class_name
            output_class_folder.mkdir(parents=True, exist_ok=True)
            
            # Get all images in class folder
            image_files = list(class_folder.glob('*.jpg')) + \
                         list(class_folder.glob('*.jpeg')) + \
                         list(class_folder.glob('*.png'))
            
            for image_file in tqdm(image_files, desc=f"Processing {class_name}"):
                # Check if valid image
                if not self.is_valid_image(image_file):
                    total_failed += 1
                    continue
                
                # Preprocess image
                preprocessed = self.preprocess_image(image_file, apply_normalization)
                
                if preprocessed is not None:
                    # Save preprocessed image as .npy file
                    output_file = output_class_folder / f"{image_file.stem}.npy"
                    np.save(output_file, preprocessed)
                    total_processed += 1
                else:
                    total_failed += 1
        
        print(f"\n{'='*50}")
        print(f"Preprocessing Complete!")
        print(f"Total processed: {total_processed}")
        print(f"Total failed: {total_failed}")
        print(f"{'='*50}")


if __name__ == "__main__":
    # Example usage
    preprocessor = DataPreprocessor(target_size=256, crop_size=224)
    
    # Define paths
    input_dir = "../data/raw"  # Modify this to your raw data path
    output_dir = "../data/processed"
    
    print("Starting data preprocessing...")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    
    # Preprocess dataset
    preprocessor.preprocess_dataset(input_dir, output_dir, apply_normalization=False)
    
    print("\nPreprocessing completed!")
