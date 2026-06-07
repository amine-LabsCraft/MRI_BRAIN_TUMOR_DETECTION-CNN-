# GPU Configuration Guide

## 🚀 GPU Training Setup

Your Brain Tumor MRI Classification project is now configured to automatically use GPU for training and evaluation when available.

---

## ✅ Automatic GPU Detection

The system automatically:
- ✓ Detects available GPUs
- ✓ Enables memory growth (prevents OOM errors)
- ✓ Enables mixed precision training (faster on modern GPUs)
- ✓ Falls back to CPU if no GPU is found

---

## 🔧 GPU Requirements

### Hardware
- NVIDIA GPU with CUDA Compute Capability 3.5 or higher
- Recommended: 6GB+ VRAM for training
- Minimum: 4GB VRAM

### Software
1. **NVIDIA Driver**
   - Latest Game Ready or Studio Driver
   - Download: https://www.nvidia.com/download/index.aspx

2. **CUDA Toolkit**
   - CUDA 11.2 or later
   - Download: https://developer.nvidia.com/cuda-downloads

3. **cuDNN**
   - cuDNN 8.1 or later
   - Download: https://developer.nvidia.com/cudnn

4. **TensorFlow-GPU**
   ```bash
   pip install tensorflow[and-cuda]
   # or
   pip install tensorflow>=2.13.0
   ```

---

## 🔍 Verify GPU Setup

### Check GPU Availability
```python
import tensorflow as tf

# Check if GPU is available
print("GPU Available:", tf.config.list_physical_devices('GPU'))

# Check TensorFlow version
print("TensorFlow version:", tf.__version__)

# Test GPU
print("Built with CUDA:", tf.test.is_built_with_cuda())
```

### Check from Terminal
```bash
# Check NVIDIA GPU
nvidia-smi

# Check CUDA version
nvcc --version
```

---

## 🎯 GPU Features Enabled

### 1. Memory Growth
Prevents TensorFlow from allocating all GPU memory at startup.
```python
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)
```

### 2. Mixed Precision Training
Uses float16 for computation, float32 for variables.
- **Benefit**: 2-3x faster training on modern GPUs
- **Requirement**: GPU with Tensor Cores (RTX series, V100, A100, etc.)

```python
policy = tf.keras.mixed_precision.Policy('mixed_float16')
tf.keras.mixed_precision.set_global_policy(policy)
```

---

## 📊 Expected Performance

### Training Time (Full Dataset)

| Hardware | Stage 1 (20 epochs) | Stage 2 (30 epochs) | Total |
|----------|---------------------|---------------------|-------|
| CPU (i7) | ~4-6 hours | ~6-8 hours | ~10-14 hours |
| GPU (GTX 1660) | ~30-40 min | ~45-60 min | ~1.5-2 hours |
| GPU (RTX 3060) | ~15-20 min | ~25-30 min | ~40-50 min |
| GPU (RTX 4090) | ~8-10 min | ~12-15 min | ~20-25 min |

### Batch Size Recommendations

| GPU VRAM | Batch Size | Notes |
|----------|------------|-------|
| 4GB | 16-24 | Reduce if OOM errors occur |
| 6GB | 32-48 | Default: 32 |
| 8GB | 48-64 | Good performance |
| 12GB+ | 64-128 | Maximum throughput |

---

## 🐛 Troubleshooting

### Issue: "No GPU detected"

**Solution 1: Check CUDA Installation**
```bash
# Windows
nvidia-smi
nvcc --version

# Should show GPU info and CUDA version
```

**Solution 2: Reinstall TensorFlow**
```bash
pip uninstall tensorflow
pip install tensorflow>=2.13.0
```

**Solution 3: Check Driver Version**
- Update to latest NVIDIA driver
- Ensure driver supports your CUDA version

---

### Issue: "Out of Memory (OOM)"

**Solution 1: Reduce Batch Size**
```bash
python src/train_model.py --batch-size 16
```

**Solution 2: Enable Memory Growth** (Already enabled)
Memory growth is automatically enabled in the code.

**Solution 3: Close Other GPU Applications**
```bash
# Windows
nvidia-smi
# Kill processes using GPU memory
```

---

### Issue: "CUDA Error" or "cuDNN Error"

**Solution 1: Check Compatibility**
- TensorFlow 2.13+ requires CUDA 11.2+ and cuDNN 8.1+
- Verify versions match

**Solution 2: Reinstall CUDA and cuDNN**
- Uninstall old versions
- Install matching versions
- Add to PATH

**Solution 3: Set Environment Variables**
```bash
# Windows PowerShell
$env:CUDA_HOME = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2"
$env:PATH += ";$env:CUDA_HOME\bin"
```

---

### Issue: "Training is slow on GPU"

**Check 1: Verify GPU is Being Used**
```python
import tensorflow as tf
print(tf.config.list_physical_devices('GPU'))
# Should show your GPU
```

**Check 2: Monitor GPU Usage**
```bash
# Run in separate terminal while training
nvidia-smi -l 1
# Should show high GPU utilization (80-100%)
```

**Check 3: Increase Batch Size**
Larger batches utilize GPU better:
```bash
python src/train_model.py --batch-size 64
```

---

## 💡 Training Output with GPU

When training starts, you should see:

```
✓ GPU Configuration:
  • Found 1 GPU(s)
  • GPU 0: /physical_device:GPU:0
  • Mixed precision enabled: mixed_float16
  • Compute dtype: float16
  • Variable dtype: float32

======================================================================
BRAIN TUMOR MRI - TWO-STAGE TRAINING PIPELINE
======================================================================

🚀 GPU Training Enabled
  Training will utilize GPU acceleration for faster performance
```

---

## 📈 Monitoring GPU During Training

### Option 1: nvidia-smi
```bash
# Windows PowerShell
while($true) { cls; nvidia-smi; Start-Sleep -Seconds 2 }
```

### Option 2: Task Manager
- Open Task Manager (Ctrl + Shift + Esc)
- Go to Performance tab
- Select GPU
- Monitor utilization during training

### Option 3: GPU-Z
- Download from: https://www.techpowerup.com/gpuz/
- Shows detailed GPU metrics

---

## 🎓 Advanced GPU Configuration

### Limit GPU Memory Usage
If you need to share GPU with other applications:

```python
# Add to model_trainer.py before configure_gpu()
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    tf.config.set_logical_device_configuration(
        gpus[0],
        [tf.config.LogicalDeviceConfiguration(memory_limit=4096)]  # 4GB
    )
```

### Use Specific GPU (Multi-GPU Systems)
```python
# Use only GPU 1
tf.config.set_visible_devices(gpus[1], 'GPU')
```

### Disable GPU (Force CPU)
```bash
# Windows PowerShell
$env:CUDA_VISIBLE_DEVICES = "-1"
python src/train_model.py
```

---

## ✅ Quick Checklist

Before training with GPU:

- [ ] NVIDIA GPU installed
- [ ] Latest NVIDIA driver installed
- [ ] CUDA Toolkit installed
- [ ] cuDNN installed
- [ ] TensorFlow 2.13+ installed
- [ ] GPU detected: `nvidia-smi` works
- [ ] TensorFlow sees GPU: `tf.config.list_physical_devices('GPU')`

---

## 📚 Additional Resources

- **TensorFlow GPU Guide**: https://www.tensorflow.org/install/gpu
- **CUDA Installation**: https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/
- **cuDNN Installation**: https://docs.nvidia.com/deeplearning/cudnn/install-guide/
- **GPU Memory Management**: https://www.tensorflow.org/guide/gpu

---

## 🎉 Benefits of GPU Training

✓ **Faster Training**: 5-10x faster than CPU  
✓ **Larger Batches**: Better gradient estimates  
✓ **Mixed Precision**: Even faster on modern GPUs  
✓ **Real-time Monitoring**: See progress faster  
✓ **Experimentation**: Try more hyperparameters  

Your project is ready for high-performance GPU training!
