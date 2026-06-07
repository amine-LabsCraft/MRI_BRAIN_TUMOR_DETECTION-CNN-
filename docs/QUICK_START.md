# 🚀 Quick Start Guide - Brain Tumor Detection AI

## 1️⃣ Launch Web App (Easiest!)

### Option A: Start Application
```powershell
streamlit run app.py
```

### Option B: Or use this shortcut
```powershell
cd c:\Users\Avi\Desktop\mri
.\venv\Scripts\Activate.ps1
streamlit run app.py
```

**App opens automatically at: http://localhost:8501**

---

## 2️⃣ Using the Web Interface

### Upload Image
1. Click **"Browse files"** button
2. Select brain MRI image
3. Supported formats: PNG, JPG, JPEG, NPY

### Try Demo Images
Use test images from: `data/processed/Testing/` or:
- **Glioma**: `data/processed/glioma/Te-gl_0010.npy`
- **Meningioma**: `data/processed/meningioma/Te-me_0001.npy`
- **No Tumor**: `data/processed/notumor/Te-no_0001.npy`
- **Pituitary**: `data/processed/pituitary/Te-pi_0001.npy`

### Read Results
- **Green Box** ✅ = No tumor detected
- **Red Box** ⚠️ = Tumor detected
- **Confidence %** = How certain the AI is
- **All Probabilities** = Scores for all 4 classes

---

## 3️⃣ Other Commands

### Train New Model
```powershell
python train_pytorch.py
```

### Evaluate Model
```powershell
python evaluate_pytorch.py
```

### Visualize Training
```powershell
python visualize_training.py
```

### Predict Single Image
```powershell
python predict.py --image path/to/image.jpg
```

---

## 🎯 What You Get

**Upload MRI → Get Results:**
- ✅ Tumor present or not?
- 🔍 If yes, which type?
- 📊 Confidence percentage
- 💡 Medical description
- ⚠️ Severity level
- 📝 Recommendations

**Model Accuracy: 98.96%** 🎯

---

## ⚠️ Important Notes

1. **Educational Purpose Only** - Not for clinical diagnosis
2. **Always Consult Doctors** - This is an AI demonstration
3. **GPU Accelerated** - Uses NVIDIA RTX 2050 for speed
4. **Real-time Results** - Predictions in less than 1 second

---

## 🆘 Need Help?

**GPU not working?**
```powershell
python test_pytorch_gpu.py
```

**App not starting?**
```powershell
pip install --upgrade streamlit
streamlit run app.py
```

**Model not found?**
- Ensure `models/final_model_20251106_142153.pth` exists
- Or train new model: `python train_pytorch.py`

---

**Full documentation in [README.md](README.md)**

**Last Updated**: November 6, 2025
