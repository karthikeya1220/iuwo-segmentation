# Frozen Segmentation Backbone

**Model Type:** Segmentation Model (Inference Only)

**Status:** FROZEN - No Training, No Fine-tuning

---

## Model Information

### Current Implementation (Prototyping)

- **Architecture:** Simple U-Net
- **Purpose:** Prototyping and pipeline testing
- **Training:** Random initialization (not trained)
- **Use Case:** Development and testing only

### Production Recommendation

For production use, replace with:

- **Model:** nnU-Net (pretrained)
- **Source:** [nnU-Net GitHub](https://github.com/MIC-DKFZ/nnUNet)
- **Training Dataset:** BraTS 2020/2021 (or equivalent)
- **License:** Apache 2.0
- **Citation:**

  ```
  Isensee, F., Jaeger, P. F., Kohl, S. A., Petersen, J., & Maier-Hein, K. H. (2021).
  nnU-Net: a self-configuring method for deep learning-based biomedical image segmentation.
  Nature methods, 18(2), 203-211.
  ```

---

## Usage

### INFERENCE ONLY

**This model is used for inference only. No retraining is performed.**

```python
from models.backbone.frozen_model import load_frozen_model

# Load frozen model
model = load_frozen_model(device='cuda')

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

---

## Model Architecture

### Simple U-Net (Prototyping)

```
Input (1, 256, 256)
    ↓
Encoder (4 blocks, max pooling)
    ↓
Bottleneck (1024 channels)
    ↓
Decoder (4 blocks, upsampling + skip connections)
    ↓
Output (1, 256, 256)
```

**Parameters:** ~31M (approximate)

---

## Replacing with nnU-Net

To use a pretrained nnU-Net model:

1. **Download pretrained weights:**

   ```bash
   # Download from nnU-Net model zoo
   # Or train on BraTS dataset following nnU-Net instructions
   ```

2. **Update `frozen_model.py`:**

   ```python
   def _load_pretrained_model(self, model_path: str) -> nn.Module:
       from nnunet.inference.predict import load_model_and_checkpoint_files
       model = load_model_and_checkpoint_files(model_path)
       return model
   ```

3. **Load model:**

   ```python
   model = load_frozen_model(
       model_path='/path/to/nnunet/checkpoint',
       device='cuda'
   )
   ```

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

nnU-Net is recommended for production because:

- State-of-the-art performance on medical image segmentation
- Well-documented and widely used
- Pretrained models available for BraTS
- Robust and reliable

---

## File Structure

```
models/backbone/
├── frozen_model.py       # Main wrapper (INFERENCE ONLY)
├── simple_unet.py        # Placeholder architecture (prototyping)
└── README.md             # This file
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

---

## License

- **Simple U-Net:** MIT License (prototyping code)
- **nnU-Net (recommended):** Apache 2.0 License

---

**Last Updated:** 2026-02-02  
**Phase:** 3.1 (Frozen Segmentation Backbone)  
**Status:** Complete
