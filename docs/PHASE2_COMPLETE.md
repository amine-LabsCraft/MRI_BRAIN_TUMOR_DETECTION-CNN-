# Phase 2: Model Development - Complete Guide

## ✅ Phase 2 Status: COMPLETED

All components for Phase 2 (Model Development) have been implemented successfully!

---

## 📋 What Was Created

### 1. New Python Modules

#### 📦 model_architecture.py (300+ lines)
Complete ResNet50-based classifier implementation:
- ✅ ResNet50 base model loading with ImageNet weights
- ✅ Custom classifier head (GlobalAvgPool → Dense → BatchNorm → Dropout → Output)
- ✅ Layer freezing/unfreezing functionality
- ✅ Model compilation with configurable optimizer
- ✅ Model save/load utilities
- ✅ Architecture export to JSON
- ✅ Parameter counting and summary

#### 🔄 training_callbacks.py (300+ lines)
Comprehensive callback system:
- ✅ EarlyStopping (patience=5, restore best weights)
- ✅ ReduceLROnPlateau (factor=0.5, patience=3)
- ✅ ModelCheckpoint (save best model)
- ✅ TensorBoard logging
- ✅ CSV logger for metrics
- ✅ Custom TrainingMonitor callback
- ✅ Learning rate logger
- ✅ Stage-specific callback configurations

#### 📊 data_loaders.py (280+ lines)
TensorFlow data pipeline:
- ✅ Dataset loading from split_info.json
- ✅ Image preprocessing and normalization
- ✅ Data augmentation integration
- ✅ Batch creation with prefetching
- ✅ Class weight computation for imbalanced data
- ✅ Train/val/test dataset generators
- ✅ Simple data loader for quick prototyping

#### 🎯 model_trainer.py (300+ lines)
Two-stage training orchestration:
- ✅ Complete training pipeline
- ✅ Stage 1: Train custom head (frozen base)
- ✅ Stage 2: Fine-tune with unfrozen layers
- ✅ Automatic data setup
- ✅ Model evaluation on test set
- ✅ Training history tracking
- ✅ Model and history saving

#### 🚀 train_model.py (200+ lines)
Main training script with CLI:
- ✅ Command-line argument parsing
- ✅ Configuration management
- ✅ Flexible hyperparameter control
- ✅ Stage skipping options
- ✅ Error handling
- ✅ Progress reporting

---

## 🏗️ Model Architecture

### ResNet50 Base + Custom Head

```
Input (224, 224, 3)
    ↓
ResNet50 Base (ImageNet weights)
    ↓
GlobalAveragePooling2D
    ↓
Dense(512, relu)
    ↓
BatchNormalization
    ↓
Dropout(0.4)
    ↓
Dense(4, softmax) → [Glioma, Meningioma, Pituitary, No Tumor]
```

### Model Statistics
- **Total Parameters**: ~24M
- **Trainable (Stage 1)**: ~1.5M (custom head only)
- **Trainable (Stage 2)**: ~15M (head + last 30 layers)

---

## 🎓 Two-Stage Training Strategy

### Stage 1: Train Custom Head (Frozen Base)
```
Epochs: 20
Learning Rate: 1e-4
Optimizer: Adam
Trainable: Custom head only (~1.5M params)
Goal: Learn task-specific features
```

### Stage 2: Fine-Tuning (Unfrozen Layers)
```
Epochs: 30
Learning Rate: 1e-5 (10x lower)
Optimizer: Adam
Trainable: Head + last 30 ResNet50 layers (~15M params)
Goal: Adapt pretrained features to MRI images
```

---

## 🚀 Quick Start Guide

### Step 1: Verify Data is Ready
```bash
# Ensure Phase 1 is complete
python src/data_pipeline.py
```

### Step 2: Train with Default Settings
```bash
cd src
python train_model.py
```

### Step 3: Monitor Training
```bash
# In another terminal, launch TensorBoard
tensorboard --logdir=../logs
```

---

## 📖 Usage Examples

### Example 1: Default Training
```bash
python train_model.py
```

### Example 2: Quick Training (Test Run)
```bash
python train_model.py --stage1-epochs 3 --stage2-epochs 5
```

### Example 3: Custom Hyperparameters
```bash
python train_model.py \
  --batch-size 64 \
  --dense-units 1024 \
  --dropout 0.5 \
  --stage1-lr 2e-4 \
  --stage2-lr 2e-5
```

### Example 4: Only Train Head (Skip Fine-Tuning)
```bash
python train_model.py --skip-stage2
```

### Example 5: Only Fine-Tune (Skip Head Training)
```bash
python train_model.py --skip-stage1
```

### Example 6: Use Custom Config
```bash
python train_model.py --config my_config.json
```

### Example 7: Save Configuration
```bash
python train_model.py --save-config training_config.json --no-train
```

---

## ⚙️ Configuration Options

### Complete Configuration Structure
```json
{
  "data": {
    "split_info_path": "../data/splits/split_info.json",
    "batch_size": 32,
    "image_size": [224, 224]
  },
  "model": {
    "num_classes": 4,
    "input_shape": [224, 224, 3],
    "weights": "imagenet",
    "dense_units": 512,
    "dropout_rate": 0.4
  },
  "training": {
    "loss": "categorical_crossentropy",
    "metrics": ["accuracy"],
    "use_class_weights": true,
    "use_tensorboard": true,
    "run_stage1": true,
    "run_stage2": true,
    "stage1": {
      "epochs": 20,
      "learning_rate": 0.0001
    },
    "stage2": {
      "epochs": 30,
      "learning_rate": 0.00001,
      "unfreeze_layers": 30
    }
  },
  "paths": {
    "models": "../models",
    "logs": "../logs"
  }
}
```

---

## 📊 Training Callbacks

### Automatic Callbacks (Stage 1 & 2)

1. **EarlyStopping**
   - Monitor: val_loss
   - Patience: 5 epochs (Stage 1), 7 epochs (Stage 2)
   - Restores best weights

2. **ReduceLROnPlateau**
   - Monitor: val_loss
   - Factor: 0.5 (halve LR)
   - Patience: 3 epochs
   - Min LR: 1e-7

3. **ModelCheckpoint**
   - Monitor: val_accuracy
   - Save best only: True
   - Format: .h5

4. **TensorBoard**
   - Histogram frequency: 1
   - Write graph: True
   - Update frequency: epoch

5. **CSVLogger**
   - Logs all metrics to CSV
   - Useful for analysis

6. **TrainingMonitor** (Custom)
   - Epoch timing
   - Metrics tracking
   - Training summary

7. **LearningRateLogger** (Custom)
   - Logs LR at each epoch
   - Useful for debugging

---

## 📈 Expected Training Output

```
======================================================================
BRAIN TUMOR MRI - TWO-STAGE TRAINING PIPELINE
======================================================================

Setting Up Data
======================================================================
DataLoader initialized:
  Classes: ['glioma', 'meningioma', 'notumor', 'pituitary']
  Batch size: 32
  Image size: (224, 224)
  Augmentation: True

Creating train dataset:
  Samples: 4916
Creating val dataset:
  Samples: 1054
Creating test dataset:
  Samples: 1053

✓ Data setup complete!

Setting Up Model
======================================================================
Building ResNet50 Classifier
...
✓ Model setup complete!

======================================================================
STAGE 1: TRAINING CUSTOM HEAD (Frozen Base)
======================================================================

Training Started
...
Epoch 1/20
154/154 [==============================] - 45s 290ms/step
  Loss: 0.8523
  Accuracy: 0.6234
  Val Loss: 0.5421
  Val Accuracy: 0.7856

...

✓ Stage 1 training complete!

======================================================================
STAGE 2: FINE-TUNING (Unfrozen Layers)
======================================================================

Unfreezing last 30 layers of base model...
...
Epoch 1/30
154/154 [==============================] - 78s 505ms/step
  Loss: 0.3421
  Accuracy: 0.8756
  Val Loss: 0.2845
  Val Accuracy: 0.9012

...

✓ Stage 2 training complete!

Evaluating Model on Test Set
...
Test Results:
  Loss: 0.2534
  Accuracy: 0.9156

🎉 TRAINING COMPLETED SUCCESSFULLY! 🎉
Final Test Accuracy: 91.56%
```

---

## 📁 Output Files

### Models Directory
```
models/
├── best_model_stage1_20251106_143022.h5
├── best_model_stage2_20251106_144533.h5
├── final_model_20251106_145612.h5
├── final_model_20251106_145612/  (SavedModel format)
└── architecture_20251106_145612.json
```

### Logs Directory
```
logs/
├── training_log_stage1_20251106_143022.csv
├── training_log_stage2_20251106_144533.csv
├── training_history_20251106_145612.json
├── metrics_history_20251106_145612.json
└── stage1_20251106_143022/  (TensorBoard logs)
    └── stage2_20251106_144533/
```

---

## 🔍 Monitoring Training

### Using TensorBoard
```bash
# Start TensorBoard
tensorboard --logdir=logs/

# Open browser
# Navigate to: http://localhost:6006
```

### View Metrics in TensorBoard
- Training/validation loss curves
- Training/validation accuracy curves
- Learning rate schedule
- Model graph
- Histograms (weights, gradients)

---

## 🐛 Troubleshooting

### Issue: "Out of Memory" Error

**Solution:**
```bash
# Reduce batch size
python train_model.py --batch-size 16

# Or even smaller
python train_model.py --batch-size 8
```

### Issue: Training Too Slow

**Solution:**
```bash
# Reduce epochs for testing
python train_model.py --stage1-epochs 5 --stage2-epochs 10

# Disable TensorBoard
python train_model.py --no-tensorboard
```

### Issue: Model Overfitting

**Solution:**
```bash
# Increase dropout
python train_model.py --dropout 0.6

# Use class weights
python train_model.py  # (enabled by default)
```

### Issue: Low Accuracy

**Solutions:**
1. Train longer: `--stage1-epochs 30 --stage2-epochs 50`
2. Unfreeze more layers: `--unfreeze-layers 50`
3. Increase model capacity: `--dense-units 1024`
4. Check data quality and preprocessing

---

## ✅ Phase 2 Checklist

- [x] **2.1 Base Model** - ResNet50 with ImageNet weights ✓
- [x] **2.2 Custom Classifier** - Dense + BatchNorm + Dropout ✓
- [x] **2.3 Compilation** - Adam optimizer, categorical crossentropy ✓
- [x] **2.4 Training Strategy** - Two-stage (frozen → fine-tune) ✓
- [x] **Callbacks** - EarlyStopping, ReduceLROnPlateau, ModelCheckpoint ✓
- [x] **Data Pipeline** - TensorFlow datasets with augmentation ✓
- [x] **CLI Interface** - Complete command-line control ✓

---

## 🎯 Key Features

### Production-Ready
- ✓ Comprehensive error handling
- ✓ Progress tracking and logging
- ✓ Model checkpointing
- ✓ Reproducible with config files
- ✓ CLI for easy experimentation

### Flexible & Modular
- ✓ Skip stages as needed
- ✓ Custom configurations
- ✓ Adjustable hyperparameters
- ✓ Multiple save formats

### Well-Documented
- ✓ Detailed docstrings
- ✓ Usage examples
- ✓ Troubleshooting guide
- ✓ Configuration reference

---

## 🔜 Next Steps: Phase 3

Phase 2 is complete! Ready to move to Phase 3: Model Evaluation

**Phase 3 will include:**
1. Quantitative metrics (Precision, Recall, F1-score)
2. Confusion matrix visualization
3. ROC-AUC curves
4. Grad-CAM visualizations
5. Sample predictions
6. Model analysis and interpretation

---

## 💡 Tips for Best Results

1. **Start with default settings** to establish baseline
2. **Monitor TensorBoard** to track training progress
3. **Use class weights** for imbalanced datasets
4. **Save configurations** for reproducibility
5. **Experiment with hyperparameters** systematically
6. **Train for sufficient epochs** (don't stop too early)
7. **Check for overfitting** (val_loss vs train_loss)

---

**Phase 2 Status: ✅ COMPLETE**

All training components are implemented and ready to use!
