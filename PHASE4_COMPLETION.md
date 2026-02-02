# Phase 4 — Completion Report

**Impact-Weighted Optimization for Expert-in-the-Loop Brain Tumor Segmentation**

**Phase:** 4 (Epistemic Uncertainty Estimation)  
**Status:** ✅ Complete  
**Date:** 2026-02-02

> **Note:** Uncertainty is computed as a SIGNAL ONLY.  
> This phase does NOT include decision-making, selection, or optimization.

---

## Executive Summary

Phase 4 implements **epistemic uncertainty estimation** using Monte Carlo Dropout to quantify model confidence in slice-level predictions.

**CRITICAL FRAMING:** Uncertainty is a SIGNAL, not a decision rule.

This phase does NOT include:

- Slice selection
- Budget constraints
- Optimization logic
- Impact estimation
- Expert correction
- Active learning

These features are intentionally excluded and will be addressed in future phases.

---

## Deliverables

### Phase 4.1 — Monte Carlo Dropout Uncertainty

✅ **File:** `models/uncertainty/compute_uncertainty.py`

**Description:** Epistemic uncertainty estimation using Monte Carlo Dropout.

**Key Features:**

- Monte Carlo Dropout with T=20 stochastic forward passes
- Voxel-wise entropy computation
- Slice-level uncertainty aggregation
- No gradient computation (model remains frozen)
- Deterministic given fixed seed

**Implementation:**

- `MonteCarloDropoutUncertainty` class
- Dropout enabled at test time
- Entropy-based uncertainty measure
- Foreground-relevant pixel aggregation

**Usage:**

```python
from models.uncertainty import MonteCarloDropoutUncertainty

estimator = MonteCarloDropoutUncertainty(
    model=model,
    num_samples=20,
    seed=42
)

uncertainty_map, slice_uncertainty = estimator.compute_uncertainty(image_slice)
```

---

✅ **File:** `models/uncertainty/generate_uncertainty.py`

**Description:** Batch script to generate uncertainty artifacts for all patients.

**Key Features:**

- Processes all patients in Phase 2 dataset
- Preserves slice alignment with Phase 2
- Saves uncertainty artifacts in required format
- Includes verification utilities

**Usage:**

```bash
# Generate uncertainty
python models/uncertainty/generate_uncertainty.py \
  --phase2_dir ./processed \
  --output_dir ./uncertainty \
  --device cuda \
  --num_samples 20

# Verify uncertainty
python models/uncertainty/generate_uncertainty.py \
  --verify \
  --uncertainty_dir ./uncertainty \
  --phase2_dir ./processed
```

---

✅ **File:** `models/uncertainty/README.md`

**Description:** Comprehensive documentation for uncertainty estimation.

**Contents:**

- Why epistemic uncertainty is used
- Why Monte Carlo Dropout is chosen
- Why uncertainty is NOT a decision rule
- Limitations of uncertainty-only approaches
- Mathematical formulation
- Usage examples
- Design rationale

**Key Statements:**

1. "Uncertainty is a SIGNAL, not a decision rule"
2. "High uncertainty ≠ high improvement potential"
3. "Uncertainty must be combined with impact estimation"

---

✅ **File:** `models/uncertainty/__init__.py`

**Description:** Package initialization for uncertainty module.

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
- **`slice_uncertainty`:** Mean entropy over foreground-relevant pixels, float

### Alignment Guarantees

- ✅ Slice IDs match Phase 2 exactly
- ✅ Spatial dimensions match Phase 2
- ✅ Slice ordering matches Phase 2
- ✅ Verified with assertions

---

## File Structure

```
iuwo-segmentation/
├── models/
│   ├── uncertainty/
│   │   ├── __init__.py                  # Package initialization
│   │   ├── compute_uncertainty.py       # MC Dropout implementation
│   │   ├── generate_uncertainty.py      # Batch generation script
│   │   └── README.md                    # Uncertainty documentation
│   └── [Phase 3 files unchanged]
├── [Phase 1 & 2 files unchanged]
└── PHASE4_COMPLETION.md                 # This file
```

---

## Design Principles

### 1. Uncertainty as a Signal

**Principle:** Uncertainty provides information, not decisions.

**Implementation:**

- No slice selection logic
- No budget constraints
- No optimization
- Pure signal computation

### 2. Epistemic Uncertainty

**Principle:** Capture model uncertainty, not data noise.

**Method:** Monte Carlo Dropout

- Approximates Bayesian inference
- Works with frozen models
- Well-established in literature

### 3. Slice-Level Granularity

**Principle:** Match decision granularity (slice selection).

**Implementation:**

- Voxel-wise uncertainty computed
- Aggregated to slice-level scalar
- Comparable across slices

### 4. Model Remains Frozen

**Principle:** No retraining or fine-tuning.

**Implementation:**

- Gradients disabled during MC sampling
- Parameters unchanged
- Dropout enabled only for sampling

---

## Scope Limitations

### Phase 4 Does NOT Include

❌ **Slice Selection**

- No ranking of slices
- No budget constraints
- No selection strategies
- (Reserved for Phase 5)

❌ **Impact Estimation**

- No Dice improvement prediction
- No correction impact modeling
- No weighted scoring
- (Reserved for Phase 5)

❌ **Optimization**

- No optimization algorithms
- No hyperparameter tuning
- No adaptive selection
- (Reserved for Phase 5)

❌ **Expert Correction**

- No simulated corrections
- No ground truth replacement
- No corrected volume generation
- (Reserved for Phase 5)

❌ **Evaluation**

- No strategy comparison
- No statistical analysis
- No Dice score computation
- (Reserved for Phase 5)

---

## Method: Monte Carlo Dropout

### Algorithm

For each slice:

1. **Enable Dropout:** Activate dropout layers at test time
2. **Stochastic Sampling:** Perform T forward passes (T=20)
3. **Aggregate Predictions:** Compute mean probability map
4. **Compute Uncertainty:** Calculate entropy as uncertainty measure
5. **Slice-Level Aggregation:** Average entropy over foreground pixels

### Mathematical Formulation

**Predictive Distribution:**
$$p(y|x) \approx \frac{1}{T} \sum_{t=1}^T f(x; \omega_t)$$

**Epistemic Uncertainty (Entropy):**
$$H(p) = -p \log(p) - (1-p) \log(1-p)$$

**Slice-Level Uncertainty:**
$$U_{\text{slice}} = \frac{1}{|F|} \sum_{i \in F} H(p_i)$$

where $F$ is the set of foreground-relevant pixels.

### Configuration

- **Number of samples (T):** 20 (default)
- **Dropout rate:** 0.1 (default)
- **Aggregation threshold:** 0.1 (foreground pixels)
- **Random seed:** 42 (reproducibility)

---

## Why Uncertainty is NOT a Decision Rule

### Common Misconception

**WRONG:** "Select slices with highest uncertainty for expert review."

**Why Wrong:**

1. Uncertainty alone ignores impact of corrections
2. High uncertainty ≠ high improvement potential
3. Ignores spatial context and tumor characteristics
4. May select uninformative slices

### Correct Framing

**RIGHT:** "Uncertainty is ONE signal for decision-making."

**Phase 4 Scope:**

- ✅ Compute uncertainty as a signal
- ✅ Store uncertainty artifacts
- ❌ Do NOT use uncertainty for selection

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

Uncertainty-only selection would choose Slice A (suboptimal).

### 2. No Spatial Context

Uncertainty is computed per-slice, ignoring 3D context.

### 3. Calibration Issues

Uncertainty scores may not be perfectly calibrated across patients.

### 4. Ignores Expert Preferences

Experts may prefer certain anatomical regions regardless of uncertainty.

---

## Testing

All components include built-in tests:

```bash
# Test MC Dropout uncertainty
python models/uncertainty/compute_uncertainty.py
```

---

## Usage Examples

### Generate Uncertainty

```bash
# Generate uncertainty for all patients
python models/uncertainty/generate_uncertainty.py \
  --phase2_dir ./processed \
  --output_dir ./uncertainty \
  --device cuda \
  --num_samples 20 \
  --seed 42 \
  --max_patients 10
```

### Load Uncertainty

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

## Success Criteria

Phase 4 is successful if:

1. ✅ Uncertainty maps are computed per slice
2. ✅ Slice-level uncertainty scores exist
3. ✅ Outputs are aligned with Phase 2 & 3 slices
4. ✅ No decision-making logic exists
5. ✅ No optimization exists
6. ✅ Uncertainty is clearly framed as a signal only
7. ✅ Documentation explains limitations
8. ✅ Model remains frozen (no retraining)
9. ✅ Deterministic given fixed seed
10. ✅ All tests pass

**Status: All criteria met ✅**

---

## Next Steps (Phase 5 - NOT IMPLEMENTED)

Phase 5 will include:

- Impact estimation (Dice improvement prediction)
- Uncertainty + Impact combined signal
- Impact-weighted slice selection
- Evaluation against baselines

**DO NOT proceed to Phase 5 without explicit approval.**

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

3. **Limitations**
   - Uncertainty alone is insufficient for optimal selection
   - Must be combined with impact estimation (Phase 5)
   - Calibration may not be perfect

4. **Alignment**
   - Uncertainty artifacts match Phase 2 exactly
   - Same slice_ids, same shapes
   - Verified with assertions

---

## Verification Checklist

- [x] MC Dropout uncertainty implemented
- [x] Uncertainty maps computed per slice
- [x] Slice-level uncertainty scores exist
- [x] Outputs aligned with Phase 2
- [x] No decision-making logic
- [x] No optimization logic
- [x] Model remains frozen
- [x] Gradients disabled
- [x] Deterministic given seed
- [x] Documentation complete
- [x] Limitations explained
- [x] Tests pass

---

**Phase 4 Status: ✅ COMPLETE**

**Ready for:** User review and Phase 5 approval

**Date:** 2026-02-02

---

**END OF PHASE 4 COMPLETION REPORT**
