# Phase 1: Data Preparation - Complete Guide

## ✅ Phase 1 Status: COMPLETED

All components for Phase 1 (Data Preparation) have been implemented successfully!

---

## 📋 What Was Created

### 1. Project Structure
```
mri/
├── data/
│   ├── raw/              # Place your downloaded dataset here
│   ├── processed/        # Preprocessed images will be saved here
│   └── splits/           # Train/val/test split info
├── src/
│   ├── data_preprocessing.py    # Image cleaning & preprocessing
│   ├── data_augmentation.py     # Data augmentation pipeline
│   ├── dataset_split.py         # Stratified dataset splitting
│   └── data_pipeline.py         # Complete end-to-end pipeline
├── notebooks/            # For Jupyter notebooks
├── models/              # For saved models
├── requirements.txt     # Python dependencies
└── README.md           # Project documentation
```

### 2. Key Features Implemented

#### 📁 data_preprocessing.py
- ✅ Image validation and loading
- ✅ RGB conversion (handles grayscale images)
- ✅ Resize to 256×256
- ✅ Center crop to 224×224
- ✅ Pixel normalization (0-255 → 0-1)
- ✅ ImageNet mean-std normalization
- ✅ Batch processing for entire datasets

#### 🔄 data_augmentation.py
- ✅ Random horizontal/vertical flip
- ✅ Random rotation (±15°)
- ✅ Random zoom (0.2)
- ✅ Random brightness/contrast adjustment
- ✅ Gaussian noise
- ✅ Elastic transform
- ✅ Grid distortion
- ✅ Optical distortion
- ✅ Both Albumentations and TensorFlow implementations
- ✅ Visualization utilities

#### 📊 dataset_split.py
- ✅ Stratified splitting (70/15/15)
- ✅ Class balance maintenance
- ✅ Split verification
- ✅ JSON export of split info
- ✅ Optional folder organization

#### 🔗 data_pipeline.py
- ✅ End-to-end pipeline integration
- ✅ Configuration management
- ✅ Command-line interface
- ✅ Progress tracking
- ✅ Flexible execution (can skip steps)

---

## 🚀 Quick Start Guide

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Download Dataset
1. Go to: https://www.kaggle.com/datasets/sartajbhuvaji/brain-tumor-classification-mri
2. Download and extract to `data/raw/` folder
3. Expected structure:
   ```
   data/raw/
   ├── glioma/
   ├── meningioma/
   ├── pituitary/
   └── notumor/
   ```

### Step 3: Run the Complete Pipeline
```bash
cd src
python data_pipeline.py
```

### Step 4: Optional - Run Individual Steps

**Preprocessing only:**
```bash
python data_preprocessing.py
```

**Splitting only:**
```bash
python dataset_split.py
```

**Custom configuration:**
```bash
python data_pipeline.py --config custom_config.json
```

---

## 📖 Usage Examples

### Example 1: Basic Pipeline Run
```python
from data_pipeline import DataPipeline, get_default_config

# Get default configuration
config = get_default_config()

# Create and run pipeline
pipeline = DataPipeline(config)
pipeline.run_full_pipeline()
```

### Example 2: Custom Configuration
```python
config = {
    'paths': {
        'raw_data': './data/raw',
        'processed_data': './data/processed',
        'split_data': './data/splits'
    },
    'preprocessing': {
        'target_size': 256,
        'crop_size': 224,
        'apply_imagenet_norm': False
    },
    'split': {
        'train_ratio': 0.70,
        'val_ratio': 0.15,
        'test_ratio': 0.15,
        'random_state': 42
    }
}

pipeline = DataPipeline(config)
pipeline.run_full_pipeline()
```

### Example 3: Individual Preprocessing
```python
from data_preprocessing import DataPreprocessor

preprocessor = DataPreprocessor(target_size=256, crop_size=224)
preprocessor.preprocess_dataset(
    input_dir='data/raw',
    output_dir='data/processed'
)
```

### Example 4: Data Augmentation Testing
```python
from data_augmentation import DataAugmentor
import numpy as np

# Create augmentor
augmentor = DataAugmentor(image_size=224)

# Load and augment image
image = np.random.rand(224, 224, 3)
augmented = augmentor.augment_image(image, mode='train')

# Visualize augmentations
augmentor.visualize_augmentations(image, num_augmentations=5)
```

---

## 🎯 Configuration Options

### Pipeline Configuration
```json
{
  "paths": {
    "raw_data": "../data/raw",
    "processed_data": "../data/processed",
    "split_data": "../data/splits"
  },
  "preprocessing": {
    "target_size": 256,
    "crop_size": 224,
    "apply_imagenet_norm": false
  },
  "augmentation": {
    "enabled": true,
    "horizontal_flip": true,
    "vertical_flip": true,
    "rotation_range": 15,
    "zoom_range": 0.2,
    "brightness_range": 0.2,
    "contrast_range": 0.2,
    "gaussian_noise": true
  },
  "split": {
    "train_ratio": 0.70,
    "val_ratio": 0.15,
    "test_ratio": 0.15,
    "random_state": 42,
    "organize_folders": false
  }
}
```

---

## ✅ Phase 1 Checklist

- [x] **1.1 Dataset Collection**
  - Dataset source identified (Kaggle)
  - Instructions provided

- [x] **1.2 Data Cleaning**
  - RGB conversion implemented
  - Corrupted image detection
  - File structure standardization

- [x] **1.3 Data Preprocessing**
  - Resize to 256×256 ✓
  - Center crop to 224×224 ✓
  - Pixel normalization ✓
  - ImageNet normalization ✓

- [x] **1.4 Data Augmentation**
  - RandomFlip (horizontal/vertical) ✓
  - RandomRotation (±15°) ✓
  - RandomZoom (0.2) ✓
  - RandomBrightness/Contrast ✓
  - Gaussian noise ✓
  - Multiple implementation options ✓

- [x] **1.5 Dataset Splitting**
  - Stratified split (70/15/15) ✓
  - Class balance maintained ✓
  - Split verification ✓

---

## 📊 Expected Output

After running the pipeline, you should see:
```
Dataset Statistics:
Total samples: XXXX
Number of classes: 4
Classes: ['glioma', 'meningioma', 'notumor', 'pituitary']

Train set: XXXX samples (70.0%)
Val set:   XXX samples (15.0%)
Test set:  XXX samples (15.0%)

Train set distribution:
  glioma: XXX (XX.X%)
  meningioma: XXX (XX.X%)
  notumor: XXX (XX.X%)
  pituitary: XXX (XX.X%)
```

---

## 🔜 Next Steps: Phase 2

Phase 1 is complete! Ready to move to Phase 2: Model Development

Phase 2 will include:
1. Loading pretrained ResNet50
2. Adding custom classifier head
3. Setting up training callbacks
4. Implementing fine-tuning strategy
5. Training the model

---

## 🐛 Troubleshooting

### Import Errors
If you get import errors:
```bash
pip install --upgrade -r requirements.txt
```

### Memory Issues
If preprocessing runs out of memory:
- Process one class at a time
- Reduce batch size in pipeline
- Use generator-based loading

### File Not Found
Make sure your directory structure matches:
```
data/raw/
├── glioma/
├── meningioma/
├── pituitary/
└── notumor/
```

---

## 📝 Notes

- All images are saved as `.npy` files for faster loading
- Split information is saved in `split_info.json`
- ImageNet normalization can be toggled in config
- Random seed ensures reproducibility

---

**Phase 1 Status: ✅ COMPLETE**

Ready to proceed to Phase 2: Model Development!
