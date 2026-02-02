# Frozen Segmentation Backbone

**Model Type:** Segmentation Model (Inference Only)

**Status:** FROZEN - No Training, No Fine-tuning

**Backbone:** Pretrained nnU-Net v2

---

## ⚠️ IMPORTANT STATEMENTS

1. **All experimental results use a pretrained nnU-Net backbone.**
2. **The model is used strictly for inference; no retraining or fine-tuning is performed.**
3. **Simple U-Net was used only for early pipeline validation and is not used in experiments.**

---

## Model Information

### Production Implementation (Current)

- **Architecture:** nnU-Net v2 (Pretrained)
- **Source:** [nnU-Net GitHub](https://github.com/MIC-DKFZ/nnUNet)
- **Training Dataset:** BraTS 2020/2021 (or equivalent medical segmentation dataset)
- **Status:** PRETRAINED and FROZEN
- **Use Case:** All experimental results and production inference
- **License:** Apache 2.0

**Citation:**

```bibtex
@article{isensee2021nnunet,
  title={nnU-Net: a self-configuring method for deep learning-based biomedical image segmentation},
  author={Isensee, Fabian and Jaeger, Paul F and Kohl, Simon AA and Petersen, Jens and Maier-Hein, Klaus H},
  journal={Nature methods},
  volume={18},
  number={2},
  pages={203--211},
  year={2021},
  publisher={Nature Publishing Group}
}
```

### Prototyping Implementation (Deprecated)

- **Architecture:** Simple U-Net
- **Purpose:** Early pipeline validation only
- **Training:** Random initialization (not trained)
- **Use Case:** Development and testing only (NOT used in experiments)
- **Status:** Deprecated - replaced by nnU-Net

---

## Usage

### INFERENCE ONLY

**This model is used for inference only. No retraining is performed.**

```python
from models.backbone.frozen_model import load_frozen_model

# Load pretrained nnU-Net (for experiments)
model = load_frozen_model(
    model_path='/path/to/nnunet/checkpoint',
    device='cuda',
    use_nnunet=True
)

# Run inference on a single slice
prob_map, pred_mask = model.predict_slice(image_slice)
```

### Key Constraints

- ✅ Model parameters are FROZEN
- ✅ No gradient computation
- ✅ No training code
- ✅ No loss functions
- ✅ No data augmentation
- ✅ Deterministic inference
- ✅ Pretrained weights only

---

## Model Architecture

### nnU-Net v2 (Production)

**Architecture:** Self-configuring U-Net with:

- Automatic architecture adaptation
- Automatic preprocessing
- Automatic augmentation (disabled for inference)
- Ensemble predictions (optional)

**Inference Mode:**

- Eval mode (no dropout, no batch norm updates)
- No gradients
- Deterministic (no test-time augmentation)
- Slice-by-slice processing for 2D compatibility

**Parameters:** ~30-50M (varies by configuration)

### Simple U-Net (Deprecated)

**Architecture:** Basic U-Net with:

- 4 encoder blocks
- 4 decoder blocks
- Skip connections

**Status:** Used only for early pipeline validation. NOT used in experiments.

**Parameters:** ~31M

---

## Loading Pretrained nnU-Net

### Option 1: Use Pretrained BraTS Model

```bash
# Download pretrained nnU-Net model for BraTS
# (Follow nnU-Net documentation for model zoo)

# Example structure:
# /path/to/nnunet/
#   ├── fold_0/
#   │   └── checkpoint_final.pth
#   ├── plans.json
#   └── dataset.json
```

### Option 2: Train Your Own (NOT RECOMMENDED)

If you must train your own nnU-Net:

```bash
# This is OUT OF SCOPE for this project
# The project uses FROZEN, PRETRAINED models only
# Training is NOT part of the research prototype
```

**Note:** This project does NOT include training code. Use pretrained models only.

---

## Loading the Model

```python
from models.backbone.frozen_model import load_frozen_model

# Production: Load pretrained nnU-Net
model = load_frozen_model(
    model_path='/path/to/nnunet/checkpoint',
    device='cuda',
    use_nnunet=True
)

# Prototyping: Load Simple U-Net (NOT for experiments)
model = load_frozen_model(
    device='cpu',
    use_nnunet=False
)
```

---

## Inference API

The public API is identical for both backends:

```python
# Single slice inference
prob_map, pred_mask = model.predict_slice(
    image_slice,  # (H, W), float32
    threshold=0.5
)

# Volume inference
predictions = model.predict_volume(
    image_slices,  # List of (H, W) arrays
    threshold=0.5,
    verbose=True
)
```

**Output Format:**

- `prob_map`: (H, W), float32, range [0, 1]
- `pred_mask`: (H, W), uint8, values {0, 1}

**Guarantees:**

- Spatial alignment preserved (same H, W as input)
- Slice ordering preserved
- Deterministic (same input → same output)

---

## Design Rationale

### Why Frozen?

This project focuses on **slice selection optimization**, not model training.

The segmentation model is treated as a **black box** that:

- Produces predictions
- Has fixed parameters
- Is not updated based on expert feedback

This separation allows us to:

- Compare slice selection strategies independently
- Avoid conflating model quality with selection strategy quality
- Maintain reproducibility across experiments

### Why nnU-Net?

nnU-Net is the production backbone because:

- ✅ State-of-the-art performance on medical image segmentation
- ✅ Well-documented and widely used
- ✅ Pretrained models available for BraTS
- ✅ Robust and reliable
- ✅ Self-configuring (minimal hyperparameter tuning)

### Why Keep Simple U-Net?

Simple U-Net is retained for:

- Early pipeline validation
- Testing without nnU-Net dependencies
- Rapid prototyping

**It is NOT used in any experimental results.**

---

## File Structure

```
models/backbone/
├── frozen_model.py       # Main wrapper (supports both nnU-Net and Simple U-Net)
├── simple_unet.py        # Placeholder architecture (prototyping only)
├── __init__.py           # Package initialization
└── README.md             # This file
```

---

## Dependencies

### For nnU-Net (Production)

```bash
pip install nnunetv2
```

### For Simple U-Net (Prototyping)

```bash
pip install torch>=2.0.0
```

---

## Important Notes

1. **No Training Code**
   - This module contains NO training code
   - All parameters are frozen
   - Gradients are explicitly disabled

2. **Inference Only**
   - Use `@torch.no_grad()` decorator
   - Model is always in eval mode
   - No dropout or batch normalization updates

3. **Deterministic Behavior**
   - Inference is deterministic (no stochastic operations)
   - Same input always produces same output
   - Reproducible across runs

4. **Scope Limitation**
   - This is Phase 3.1 only
   - Does NOT include uncertainty estimation
   - Does NOT include impact estimation
   - Does NOT include expert correction

5. **Experimental Results**
   - **All experimental results use pretrained nnU-Net**
   - Simple U-Net is for validation only
   - Results are NOT comparable between backends

---

## Backbone Upgrade History

- **2026-02-02 (Initial):** Simple U-Net for prototyping
- **2026-02-02 (Upgrade):** Pretrained nnU-Net v2 for production
- **Status:** Phase 3 remains complete and valid after upgrade

---

## Troubleshooting

### nnU-Net Not Found

If nnU-Net is not installed:

```bash
pip install nnunetv2
```

The model will automatically fall back to Simple U-Net with a warning.

### Checkpoint Not Found

Ensure the checkpoint path points to a valid nnU-Net model folder:

```
/path/to/checkpoint/
├── fold_0/
│   └── checkpoint_final.pth
├── plans.json
└── dataset.json
```

### GPU Memory Issues

If running out of GPU memory:

```python
# Use CPU instead
model = load_frozen_model(device='cpu', use_nnunet=True)

# Or process slices in smaller batches
```

---

## License

- **nnU-Net:** Apache 2.0 License
- **Simple U-Net:** MIT License (prototyping code)

---

**Last Updated:** 2026-02-02  
**Phase:** 3.1 (Frozen Segmentation Backbone)  
**Backbone:** Pretrained nnU-Net v2  
**Status:** Complete ✅
