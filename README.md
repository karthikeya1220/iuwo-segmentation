# Impact-Weighted Optimization for Expert-in-the-Loop Brain Tumor Segmentation

Research Prototype — PhD-Level Medical Image Analysis

---

## Project Overview

This project formalizes expert-in-the-loop brain tumor segmentation as a **budget-constrained decision problem**, where the goal is to optimally allocate limited expert corrections to maximize final segmentation quality.

### Core Framing

- ✅ The segmentation model is **frozen** (no retraining)
- ✅ Expert interaction is **simulated and perfect**
- ✅ Expert effort is modeled **ONLY as the number of axial slices corrected**
- ✅ Slice selection is a **decision problem**, separate from prediction
- ❌ NO active learning, NO UI, NO real-time interaction

---

## Project Structure

```text
iuwo-segmentation/
├── experiments/
│   ├── phase1_problem_formulation.md    # Mathematical formulation
│   └── problem-formulation.md           # (deprecated, use phase1_*)
├── data/
│   └── load_brats_axial.py              # BraTS dataset loader (Phase 2)
├── requirements.txt                      # Python dependencies
└── README.md                             # This file
```

---

## Phase Status

| Phase | Status | Description |
| --- | --- | --- |
| **Phase 1** | ✅ **Complete** | Problem Formulation |
| **Phase 2** | ✅ **Complete** | BraTS Loading + Axial Slicing |
| **Phase 3** | ⏸️ Not Started | Baseline Slice Selection Strategies |
| **Phase 4** | ⏸️ Not Started | Impact-Weighted Optimization |
| **Phase 5** | ⏸️ Not Started | Evaluation & Comparison |

---

## Phase 1: Problem Formulation

**Deliverable:** `experiments/phase1_problem_formulation.md`

### Key Contributions

1. Formalizes expert-in-the-loop segmentation as a constrained optimization problem
2. Defines expert effort as a hard budget $B$ on the number of slices
3. Separates prediction, decision-making, correction, and evaluation
4. Explicitly states what existing literature does NOT model

### Mathematical Formulation

Given:

- 3D MRI volume $V \in \mathbb{R}^{H \times W \times D}$
- Ground truth $Y \in \{0,1\}^{H \times W \times D}$
- Frozen model prediction $\hat{Y} = f_\theta(V)$

Objective:
$$
\begin{aligned}
\max_{\mathcal{B}} \quad & \text{Dice}(\tilde{Y}(\mathcal{B}), Y) \\
\text{subject to} \quad & |\mathcal{B}| \le B
\end{aligned}
$$

where $\mathcal{B}$ is the set of slice indices selected for expert correction.

---

## Phase 2: BraTS Loading & Axial Slicing

**Deliverable:** `data/load_brats_axial.py`

### Implementation Details

- ✅ Loads BraTS NIfTI files (`.nii.gz`)
- ✅ Uses **ONLY FLAIR modality**
- ✅ Slices **strictly along axial axis**
- ✅ Preserves **all slices** (no empty slice removal)
- ✅ **No normalization** across patients
- ✅ **No resampling, resizing, or augmentation**
- ✅ Outputs one `.npy` file per patient

### Data Format

Each patient is saved as:

```python
{
  "patient_id": str,
  "slices": [
    {
      "slice_id": int,        # 0-indexed, stable
      "image": np.ndarray,    # (H, W), float32
      "mask": np.ndarray      # (H, W), uint8
    },
    ...
  ]
}
```

### Usage

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Process BraTS Dataset

```bash
python data/load_brats_axial.py \
  --brats_dir /path/to/BraTS2021 \
  --output_dir ./processed \
  --max_patients 10
```

**Expected BraTS directory structure:**

```text
BraTS2021/
├── BraTS2021_00000/
│   ├── BraTS2021_00000_flair.nii.gz
│   └── BraTS2021_00000_seg.nii.gz
├── BraTS2021_00001/
│   ├── BraTS2021_00001_flair.nii.gz
│   └── BraTS2021_00001_seg.nii.gz
└── ...
```

#### 3. Verify Processed Data

```bash
python data/load_brats_axial.py \
  --verify \
  --output_dir ./processed
```

#### 4. Load Processed Data in Python

```python
import numpy as np

# Load patient data
data = np.load("processed/BraTS2021_00000.npy", allow_pickle=True).item()

# Access patient information
patient_id = data["patient_id"]
slices = data["slices"]

# Access individual slice
slice_0 = slices[0]
image = slice_0["image"]  # (H, W) float32
mask = slice_0["mask"]    # (H, W) uint8
slice_id = slice_0["slice_id"]  # int

print(f"Patient: {patient_id}")
print(f"Number of slices: {len(slices)}")
print(f"Slice shape: {image.shape}")
```

---

## Design Principles

### 1. Separation of Concerns

| Component | Responsibility | Implementation Status |
| --- | --- | --- |
| **Prediction** | Generate $\hat{Y}$ from $V$ | Phase 3 (not started) |
| **Decision** | Select $\mathcal{B}$ under budget $B$ | Phase 3-4 (not started) |
| **Correction** | Replace $\hat{Y}_i$ with $Y_i$ | Simulated (perfect) |
| **Evaluation** | Compute Dice score | Phase 5 (not started) |

### 2. Research Rigor

- All assumptions are **explicitly stated**
- All design decisions are **justified**
- All exclusions are **documented**
- Suitable for **MICCAI / IEEE TMI** reviewers

### 3. Reproducibility

- Slice indices are **stable and deterministic**
- No random seeds required for Phase 1-2
- Data format is **self-contained**
- Processing is **idempotent**

---

## Scope and Limitations

### In Scope

✅ Budget-constrained slice selection  
✅ Frozen segmentation model  
✅ Simulated expert interaction  
✅ Axial slice decomposition  
✅ FLAIR modality only  

### Out of Scope

❌ Model retraining or fine-tuning  
❌ Active learning  
❌ Multi-modal fusion  
❌ User interface design  
❌ Real-time interaction  
❌ Clinical validation  

---

## Dependencies

### Phase 2 (Current)

- `numpy >= 1.21.0` — Array operations
- `nibabel >= 3.2.0` — NIfTI file handling

### Future Phases (Not Yet Required)

- `torch >= 2.0.0` — Model inference
- `scikit-learn >= 1.0.0` — Metrics
- `matplotlib >= 3.5.0` — Visualization
- `scipy >= 1.7.0` — Optimization

---

## Next Steps

### Phase 3: Baseline Slice Selection Strategies

DO NOT IMPLEMENT YET

Will include:

- Random selection
- Uncertainty-based selection (entropy, variance)
- Oracle selection (upper bound)

### Phase 4: Impact-Weighted Optimization

DO NOT IMPLEMENT YET

Will include:

- Impact estimation
- Weighted uncertainty scoring
- Optimization algorithm

### Phase 5: Evaluation & Comparison

DO NOT IMPLEMENT YET

Will include:

- Dice score computation
- Strategy comparison
- Statistical analysis

---

## Citation

If you use this code or formulation, please cite:

```bibtex
@misc{iuwo2026,
  title={Impact-Weighted Optimization for Expert-in-the-Loop Brain Tumor Segmentation},
  author={[Author Name]},
  year={2026},
  note={Research Prototype}
}
```

---

## License

Research Prototype — For Academic Use Only

---

## Contact

For questions or collaboration:

- **Project:** Impact-Weighted Optimization for Expert-in-the-Loop Segmentation
- **Status:** Phase 2 Complete
- **Date:** 2026-02-02

---

**⚠️ IMPORTANT:** This is a research prototype, not a production system. Do not proceed to Phase 3 or beyond without explicit approval.
