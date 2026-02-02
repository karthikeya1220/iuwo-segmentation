# Phase 4 — Epistemic Uncertainty Estimation

**UNCERTAINTY IS A SIGNAL, NOT A DECISION RULE**

This module computes predictive uncertainty for slice-level segmentation predictions using Monte Carlo Dropout.

---

## ⚠️ CRITICAL FRAMING

**Uncertainty in Phase 4 is a SIGNAL ONLY.**

This phase does NOT include:

- ❌ Slice selection
- ❌ Budget constraints
- ❌ Optimization logic
- ❌ Impact estimation
- ❌ Expert correction
- ❌ Active learning
- ❌ Decision-making

Uncertainty provides information about model confidence, but it is NOT used to make decisions in this phase.

---

## Uncertainty Definition

### Epistemic Uncertainty

**Definition:** Model uncertainty arising from limited training data or model capacity.

**Interpretation:** High epistemic uncertainty indicates regions where the model is uncertain about its predictions due to lack of knowledge.

**Method:** Monte Carlo Dropout (Gal & Ghahramani, 2016)

### Why Epistemic Uncertainty?

1. **Model-Derived:** Captures uncertainty in the frozen nnU-Net model
2. **No Retraining Required:** Works with frozen, pretrained models
3. **Well-Established:** Standard method in medical imaging literature
4. **Interpretable:** Reflects model confidence in predictions

### Why NOT Aleatoric Uncertainty?

Aleatoric uncertainty (data uncertainty) is OUT OF SCOPE for Phase 4 because:

- Requires modeling data noise explicitly
- Less relevant for frozen model evaluation
- Adds complexity without clear benefit for slice selection

---

## Method: Monte Carlo Dropout

### Overview

Monte Carlo Dropout estimates epistemic uncertainty by performing multiple stochastic forward passes with dropout ENABLED at test time.

**Key Idea:** Dropout at test time approximates Bayesian inference over model weights.

### Algorithm

For each slice:

1. **Enable Dropout:** Activate dropout layers at test time
2. **Stochastic Sampling:** Perform T forward passes (T=20 by default)
3. **Aggregate Predictions:** Compute mean probability map across samples
4. **Compute Uncertainty:** Calculate entropy as uncertainty measure
5. **Slice-Level Aggregation:** Average entropy over foreground-relevant pixels

### Mathematical Formulation

Given input slice $x$, model $f$, and dropout mask $\omega$:

**Predictive Distribution:**
$$p(y|x) \approx \frac{1}{T} \sum_{t=1}^T f(x; \omega_t)$$

**Epistemic Uncertainty (Entropy):**
$$H(p) = -p \log(p) - (1-p) \log(1-p)$$

where $p$ is the mean predictive probability.

**Slice-Level Uncertainty:**
$$U_{\text{slice}} = \frac{1}{|F|} \sum_{i \in F} H(p_i)$$

where $F$ is the set of foreground-relevant pixels.

---

## Why Monte Carlo Dropout?

### Advantages

1. **No Retraining:** Works with frozen, pretrained models
2. **Computationally Efficient:** Only requires multiple forward passes
3. **Theoretically Grounded:** Approximates Bayesian inference
4. **Widely Used:** Standard method in medical imaging

### Limitations

1. **Requires Dropout Layers:** Model must have dropout for stochastic sampling
2. **Computational Cost:** T forward passes per slice (T=20)
3. **Approximation:** Not exact Bayesian inference
4. **Calibration:** Uncertainty scores may not be perfectly calibrated

---

## Why Uncertainty is NOT a Decision Rule

### Common Misconception

**WRONG:** "Select slices with highest uncertainty for expert review."

**Why Wrong:**

- Uncertainty alone ignores impact of corrections
- High uncertainty ≠ high improvement potential
- Ignores spatial context and tumor characteristics
- May select uninformative slices

### Correct Framing

**RIGHT:** "Uncertainty is ONE signal among many for decision-making."

**Phase 4 Scope:**

- Compute uncertainty as a signal
- Store uncertainty artifacts
- Do NOT use uncertainty for selection

**Future Phases:**

- Combine uncertainty with impact estimation (Phase 5)
- Use combined signal for optimized selection (Phase 5)

---

## Limitations of Uncertainty-Only Approaches

### 1. Ignores Impact

Uncertainty measures model confidence, not correction impact.

**Example:**

- Slice A: High uncertainty, small tumor → Low impact
- Slice B: Medium uncertainty, large tumor → High impact

Uncertainty-only selection would choose Slice A, which is suboptimal.

### 2. No Spatial Context

Uncertainty is computed per-slice, ignoring 3D context.

**Issue:** Adjacent slices may have correlated uncertainties.

### 3. Calibration Issues

Uncertainty scores may not be perfectly calibrated.

**Issue:** Absolute values may not be comparable across patients.

### 4. Ignores Expert Preferences

Experts may prefer to review certain anatomical regions regardless of uncertainty.

**Issue:** Uncertainty-only selection ignores domain knowledge.

---

## Output Format

### Per-Patient Artifact

**File:** `models/uncertainty/<patient_id>.npy`

**Structure:**

```python
{
  "patient_id": str,
  "slices": [
    {
      "slice_id": int,
      "uncertainty_map": np.ndarray (H, W),  # float32, [0, 1]
      "slice_uncertainty": float             # scalar, [0, 1]
    },
    ...
  ]
}
```

### Fields

- **`uncertainty_map`:** Voxel-wise entropy (H, W), float32, range [0, 1]
- **`slice_uncertainty`:** Mean entropy over foreground-relevant pixels, float, range [0, 1]

### Alignment Guarantees

- ✅ Slice IDs match Phase 2 exactly
- ✅ Spatial dimensions match Phase 2
- ✅ Slice ordering matches Phase 2
- ✅ Verified with assertions

---

## Usage

### Generate Uncertainty Artifacts

```bash
# Generate uncertainty for all patients
python models/uncertainty/generate_uncertainty.py \
  --phase2_dir ./processed \
  --output_dir ./uncertainty \
  --device cuda \
  --num_samples 20 \
  --seed 42 \
  --max_patients 10

# Verify uncertainty artifacts
python models/uncertainty/generate_uncertainty.py \
  --verify \
  --uncertainty_dir ./uncertainty \
  --phase2_dir ./processed
```

### Load Uncertainty in Python

```python
import numpy as np

# Load uncertainty for a patient
uncertainties = np.load("uncertainty/BraTS2021_00000.npy", allow_pickle=True).item()

patient_id = uncertainties["patient_id"]
slices = uncertainties["slices"]

# Access slice-level uncertainty
for slice_data in slices:
    slice_id = slice_data["slice_id"]
    uncertainty_map = slice_data["uncertainty_map"]  # (H, W)
    slice_uncertainty = slice_data["slice_uncertainty"]  # scalar
    
    print(f"Slice {slice_id}: uncertainty = {slice_uncertainty:.4f}")
```

---

## Configuration

### Number of MC Samples (T)

**Default:** T = 20

**Rationale:**

- Balances accuracy and computational cost
- Standard in literature (Gal & Ghahramani, 2016)
- Sufficient for stable uncertainty estimates

**Tuning:**

- Increase T for more stable estimates (slower)
- Decrease T for faster computation (less stable)

### Dropout Rate

**Default:** p = 0.1

**Rationale:**

- Standard dropout rate for inference
- Provides sufficient stochasticity without degrading predictions

### Aggregation Threshold

**Default:** threshold = 0.1

**Rationale:**

- Focuses on foreground-relevant pixels
- Ignores background pixels (low information)

---

## Design Rationale

### Why Slice-Level Uncertainty?

**Rationale:** Matches the decision granularity (slice selection).

**Alternative:** Voxel-level selection is out of scope.

### Why Mean Entropy?

**Rationale:**

- Simple and interpretable
- Comparable across slices
- Standard aggregation method

**Alternatives:**

- Max entropy: Too sensitive to outliers
- Median entropy: Less interpretable

### Why Foreground-Relevant Pixels?

**Rationale:**

- Focuses on tumor regions
- Ignores uninformative background
- Provides more meaningful scores

**Alternative:** Mean over all pixels includes background noise.

---

## Verification

All uncertainty artifacts are verified to ensure:

- [x] Slice IDs match Phase 2
- [x] Spatial dimensions match Phase 2
- [x] Uncertainty maps are float32, range [0, 1]
- [x] Slice uncertainties are scalars, range [0, 1]
- [x] No NaN or Inf values
- [x] Deterministic given fixed seed

---

## File Structure

```
models/uncertainty/
├── compute_uncertainty.py       # MC Dropout implementation
├── generate_uncertainty.py      # Batch generation script
├── README.md                    # This file
└── <patient_id>.npy             # Uncertainty artifacts (generated)
```

---

## Dependencies

```bash
pip install torch>=2.0.0 numpy>=1.21.0
```

---

## Important Notes

1. **Uncertainty is a Signal**
   - NOT a decision rule
   - NOT used for selection in Phase 4
   - Provides information for future phases

2. **Model Remains Frozen**
   - No retraining or fine-tuning
   - Gradients disabled during MC sampling
   - Parameters unchanged

3. **Deterministic**
   - Fixed random seed ensures reproducibility
   - Same input → same uncertainty

4. **Limitations**
   - Uncertainty alone is insufficient for optimal selection
   - Must be combined with impact estimation (Phase 5)
   - Calibration may not be perfect

---

## References

1. **Gal, Y., & Ghahramani, Z. (2016).** Dropout as a Bayesian approximation: Representing model uncertainty in deep learning. *ICML*.

2. **Kendall, A., & Gal, Y. (2017).** What uncertainties do we need in Bayesian deep learning for computer vision? *NeurIPS*.

3. **Nair, T., et al. (2020).** Exploring uncertainty measures in deep networks for multiple sclerosis lesion detection and segmentation. *Medical Image Analysis*.

---

**Last Updated:** 2026-02-02  
**Phase:** 4 (Epistemic Uncertainty Estimation)  
**Status:** Complete ✅
