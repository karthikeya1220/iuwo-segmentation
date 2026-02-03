# Quick Start Guide

## Impact-Weighted Optimization for Expert-in-the-Loop Brain Tumor Segmentation

### Prerequisites

1. **Python Environment:**

   ```bash
   python >= 3.11
   pip install -r requirements.txt
   ```

2. **Data:**
   - BraTS 2024 dataset archive at: `/Users/darshankarthikeya/Downloads/archive.zip`
   - Or update path in `scripts/prepare_nnunet_dataset.py`

3. **Disk Space:**
   - ~5GB for extracted data
   - ~2GB for preprocessed artifacts
   - ~500MB for results

### One-Command Execution

```bash
./scripts/train_and_evaluate.sh
```

**Runtime:** ~30-45 minutes (CPU-dependent)

### What Happens

1. **Data Preparation** (~2 min)
   - Extracts 25 BraTS patients
   - Formats for nnU-Net v2
   - Validates dataset integrity

2. **Preprocessing** (~3 min)
   - Generates nnU-Net plans
   - Creates 2D and 3D configurations
   - Preprocesses all volumes

3. **Inference** (~5-10 min)
   - Runs nnU-Net v2 prediction (CPU)
   - Generates probabilistic segmentations
   - Converts back to slice format

4. **Uncertainty Estimation** (~5 min)
   - Monte Carlo Dropout (5 samples)
   - Per-voxel variance computation

5. **Impact Estimation** (~1 min)
   - Potential Dice improvement calculation
   - Boundary complexity weighting

6. **Evaluation** (~2 min)
   - IWUO vs. Random vs. Uncertainty
   - Dice vs. Budget curves
   - Statistical analysis

### Output Files

```
evaluation/
├── results_frozen.npy          # Raw results (NumPy)
└── dice_vs_budget_frozen.png   # Performance plot
```

### Troubleshooting

**Error: "CUDA not available"**

- Expected behavior on macOS
- Pipeline automatically uses CPU
- No action needed

**Error: "Dataset not found"**

- Check BraTS archive path
- Verify `archive.zip` exists
- Update path in `prepare_nnunet_dataset.py`

**Error: "Out of memory"**

- Reduce `num_samples` in uncertainty generation
- Close other applications
- Use smaller batch size (edit plans)

**Slow execution**

- Normal on CPU
- Inference takes 5-10 minutes
- Consider reducing dataset size for testing

### Validation

After completion, verify:

```bash
# Check output exists
ls -lh evaluation/dice_vs_budget_frozen.png

# View results
python -c "import numpy as np; print(np.load('evaluation/results_frozen.npy', allow_pickle=True))"
```

### Documentation

- **Overview:** `README.md`
- **Development Log:** `PHASE3_COMPLETION.md`
- **Technical Details:** `TECHNICAL_POSTMORTEM.md`
- **Complete Summary:** `FINAL_SUMMARY.md`

### Support

For issues:

1. Check `TECHNICAL_POSTMORTEM.md` for known limitations
2. Review `pipeline_execution.log` for error details
3. Verify environment setup

### Citation

```bibtex
@misc{iwuo2026,
  title={Impact-Weighted Optimization for Expert-in-the-Loop Brain Tumor Segmentation},
  year={2026}
}
```

---

**Last Updated:** February 3, 2026  
**Status:** Production Ready
