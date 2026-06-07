# Installation & Testing Guide

## ✅ Phase 1 Complete - Now Let's Test It!

---

## 📋 Pre-Installation Checklist

- [ ] Python 3.8 or higher installed
- [ ] pip package manager available
- [ ] At least 5GB free disk space
- [ ] Internet connection for package downloads

Check Python version:
```bash
python --version
```

---

## 🔧 Installation Steps

### Step 1: Install Required Packages

**Option A: Install all at once (Recommended)**
```bash
pip install -r requirements.txt
```

**Option B: Install individually (if option A fails)**
```bash
pip install tensorflow>=2.13.0
pip install numpy>=1.24.0
pip install pandas>=2.0.0
pip install pillow>=10.0.0
pip install opencv-python>=4.8.0
pip install albumentations>=1.3.0
pip install matplotlib>=3.7.0
pip install seaborn>=0.12.0
pip install scikit-learn>=1.3.0
pip install tqdm>=4.65.0
```

### Step 2: Verify Installation

Run this command to check if packages are installed:
```bash
python -c "import tensorflow, numpy, cv2, albumentations, sklearn; print('All packages installed successfully!')"
```

Expected output:
```
All packages installed successfully!
```

### Step 3: Verify Project Structure

Run the quick start script:
```bash
python quick_start.py
```

This will check if all directories are created and display setup instructions.

---

## 📥 Dataset Setup

### Download Dataset

1. **Go to Kaggle:**
   https://www.kaggle.com/datasets/sartajbhuvaji/brain-tumor-classification-mri

2. **Download the dataset** (requires Kaggle account)

3. **Extract to the correct location:**
   ```
   mri/data/raw/
   ```

4. **Verify structure:**
   ```
   data/raw/
   ├── glioma/
   │   ├── image1.jpg
   │   ├── image2.jpg
   │   └── ...
   ├── meningioma/
   │   ├── image1.jpg
   │   └── ...
   ├── pituitary/
   │   ├── image1.jpg
   │   └── ...
   └── notumor/
       ├── image1.jpg
       └── ...
   ```

### Alternative: Use Sample Data (for testing)

If you want to test the pipeline without downloading the full dataset:

```bash
# Create sample data structure
cd data/raw
mkdir glioma meningioma pituitary notumor
```

Then add a few test images to each folder.

---

## 🧪 Testing the Pipeline

### Test 1: Individual Module Tests

**Test Preprocessing Module:**
```bash
cd src
python -c "from data_preprocessing import DataPreprocessor; print('Preprocessing module OK')"
```

**Test Augmentation Module:**
```bash
python -c "from data_augmentation import DataAugmentor; print('Augmentation module OK')"
```

**Test Splitting Module:**
```bash
python -c "from dataset_split import DatasetSplitter; print('Splitting module OK')"
```

**Test Pipeline Module:**
```bash
python -c "from data_pipeline import DataPipeline; print('Pipeline module OK')"
```

### Test 2: Run Complete Pipeline

**With full dataset:**
```bash
cd src
python data_pipeline.py
```

**Expected output:**
```
======================================================================
BRAIN TUMOR MRI - DATA PREPARATION PIPELINE
======================================================================

Configuration:
{
  "paths": { ... },
  ...
}

============================================================
STEP 1: DATA PREPROCESSING
============================================================

Processing class: glioma
Processing glioma: 100%|███████████| XXX/XXX [XX:XX<00:00, X.XXit/s]

Processing class: meningioma
Processing meningioma: 100%|████████| XXX/XXX [XX:XX<00:00, X.XXit/s]

...

============================================================
STEP 2: DATASET SPLITTING
============================================================

Dataset Statistics:
Total samples: XXXX
Number of classes: 4
Classes: ['glioma', 'meningioma', 'notumor', 'pituitary']

Train set: XXXX samples (70.0%)
Val set:   XXX samples (15.0%)
Test set:  XXX samples (15.0%)

============================================================
DATA PIPELINE COMPLETED SUCCESSFULLY!
============================================================
```

### Test 3: Verify Output

Check that files were created:

**Preprocessed data:**
```bash
# Windows
dir data\processed /s

# Should show folders: glioma, meningioma, pituitary, notumor
# Each containing .npy files
```

**Split information:**
```bash
# Windows
type data\splits\split_info.json

# Should show JSON with train/val/test splits
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'xxx'"

**Solution:**
```bash
pip install xxx
```

Or reinstall all requirements:
```bash
pip install --upgrade -r requirements.txt
```

### Issue: "No space left on device"

**Solution:**
- Free up disk space (need ~5GB)
- Or reduce dataset size for testing

### Issue: "Permission denied"

**Solution:**
```bash
# Run as administrator (Windows)
# Or use: sudo (Linux/Mac)
```

### Issue: TensorFlow installation fails

**Solution:**
```bash
# For CPU-only version (smaller, easier to install)
pip install tensorflow-cpu

# For specific version
pip install tensorflow==2.13.0
```

### Issue: OpenCV import error

**Solution:**
```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

### Issue: "Dataset not found"

**Solution:**
- Verify dataset is in `data/raw/`
- Check folder names match exactly: glioma, meningioma, pituitary, notumor
- Use absolute paths if relative paths fail

---

## ✅ Success Criteria

Your installation is successful if:

- [x] All packages import without errors
- [x] Quick start script runs without errors
- [x] Pipeline creates preprocessed data
- [x] Split information JSON is created
- [x] No error messages in console

---

## 📊 Performance Benchmarks

**Expected processing times:**
- Small dataset (100 images): ~1-2 minutes
- Medium dataset (1000 images): ~10-15 minutes
- Full dataset (7000+ images): ~45-60 minutes

*Times vary based on CPU/GPU and disk speed*

---

## 🎯 Next Steps After Successful Installation

1. ✅ Installation complete
2. ✅ Pipeline tested and working
3. ✅ Data preprocessed
4. ✅ Splits created

**Ready for Phase 2!**

Phase 2 will involve:
- Loading ResNet50 model
- Building custom classifier
- Training the model
- Evaluating performance

---

## 💡 Pro Tips

1. **Use a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

2. **Test with small dataset first** before processing full dataset

3. **Keep split_info.json safe** - it ensures reproducibility

4. **Monitor disk space** during preprocessing

5. **Use GPU if available** for faster processing (TensorFlow will auto-detect)

---

## 📞 Getting Help

If you encounter issues:

1. Check `PHASE1_COMPLETE.md` for detailed documentation
2. Review error messages carefully
3. Check Python version compatibility
4. Verify dataset structure matches expected format
5. Try testing individual modules first

---

## ✨ Installation Complete!

If you've reached this point without errors:

**🎉 Congratulations! Phase 1 setup is complete and tested!**

You're now ready to:
- Preprocess your full dataset
- Create train/val/test splits
- Move on to Phase 2: Model Development

---

**Happy Training! 🚀**
