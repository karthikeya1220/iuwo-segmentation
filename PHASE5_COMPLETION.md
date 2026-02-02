# Phase 5 — Completion Report

**Impact-Weighted Optimization for Expert-in-the-Loop Brain Tumor Segmentation**

**Phase:** 5 (Impact Estimation)  
**Status:** ✅ Complete  
**Date:** 2026-02-02

> **Note:** Impact is computed as a SIGNAL ONLY.  
> This phase does NOT include decision-making, selection, or optimization.

---

## Executive Summary

Phase 5 implements **volumetric impact estimation** to quantify the global importance of correcting each slice.

**Impact answers:** "How much does correcting this slice matter for the final 3D segmentation?"

**CRITICAL FRAMING:** Impact is a SIGNAL, not a decision rule.

This phase does NOT include:

- Slice selection
- Ranking for decision-making
- Budget constraints
- Optimization logic
- Expert correction simulation
- Uncertainty combination

These features are intentionally excluded and will be addressed in future phases.

---

## Deliverables

### Phase 5.1 — Volumetric Impact Estimation

✅ **File:** `models/impact/compute_impact.py`

**Description:** Volumetric impact estimation based on tumor volume contribution and 3D connectivity.

**Key Features:**

- Slice-wise volumetric contribution computation
- 3D spatial connectivity weighting
- Sqrt stabilization transform
- Normalized impact scores [0, 1]
- No ground truth required

**Implementation:**

- `VolumetricImpactEstimator` class
- Connectivity-weighted volume computation
- Foreground voxel counting
- Stabilization and normalization

**Usage:**

```python
from models.impact import VolumetricImpactEstimator

estimator = VolumetricImpactEstimator(
    use_connectivity=True,
    use_sqrt_transform=True
)

impact_results = estimator.compute_impact(predictions)
```

---

✅ **File:** `models/impact/generate_impact.py`

**Description:** Batch script to generate impact artifacts for all patients.

**Key Features:**

- Processes all patients in Phase 3 predictions
- Preserves slice alignment with Phase 2–4
- Saves impact artifacts in required format
- Includes verification utilities

**Usage:**

```bash
# Generate impact
python models/impact/generate_impact.py \
  --predictions_dir ./predictions \
  --output_dir ./impact \
  --use_connectivity \
  --use_sqrt_transform

# Verify impact
python models/impact/generate_impact.py \
  --verify \
  --impact_dir ./impact \
  --predictions_dir ./predictions
```

---

✅ **File:** `models/impact/README.md`

**Description:** Comprehensive documentation for impact estimation.

**Contents:**

- What impact represents conceptually
- Why impact ≠ uncertainty
- Why impact is needed in addition to uncertainty
- Limitations of the chosen impact proxy
- Mathematical formulation
- Usage examples
- Design rationale

**Key Statements:**

1. "Impact is a SIGNAL, not a decision rule"
2. "Impact ≠ Uncertainty (complementary signals)"
3. "High uncertainty + high impact = most important slices"

---

✅ **File:** `models/impact/__init__.py`

**Description:** Package initialization for impact module.

---

## Output Format

### Per-Patient Artifact

**File:** `models/impact/<patient_id>.npy`

**Structure:**

```python
{
  "patient_id": str,
  "slices": [
    {
      "slice_id": int,
      "impact_score": float  # range [0, 1]
    },
    ...
  ]
}
```

### Fields

- **`impact_score`:** Normalized, stabilized volumetric impact, float, range [0, 1]

### Alignment Guarantees

- ✅ Slice IDs match Phase 2–4 exactly
- ✅ Slice ordering matches Phase 2–4
- ✅ Verified with assertions

---

## File Structure

```
iuwo-segmentation/
├── models/
│   ├── impact/
│   │   ├── __init__.py                  # Package initialization
│   │   ├── compute_impact.py            # Volumetric impact implementation
│   │   ├── generate_impact.py           # Batch generation script
│   │   └── README.md                    # Impact documentation
│   └── [Phase 3 & 4 files unchanged]
├── [Phase 1 & 2 files unchanged]
└── PHASE5_COMPLETION.md                 # This file
```

---

## Design Principles

### 1. Impact as a Signal

**Principle:** Impact provides information, not decisions.

**Implementation:**

- No slice selection logic
- No ranking for decision-making
- No budget constraints
- Pure signal computation

### 2. Volumetric Importance

**Principle:** Impact reflects global volumetric contribution.

**Formulation:** Slice-wise tumor volume weighted by 3D connectivity

**Rationale:**

- Larger tumor regions have higher impact
- Core slices have higher impact than periphery
- Reflects potential influence on global segmentation

### 3. Independent of Uncertainty

**Principle:** Impact is computed independently of uncertainty.

**Rationale:**

- Impact and uncertainty are complementary signals
- Both needed for optimal selection
- Will be combined in future phases

### 4. No Ground Truth Required

**Principle:** Impact computed from predictions only.

**Implementation:**

- Uses Phase 3 predictions
- No Dice improvements
- No expert corrections simulated
- No ground truth leakage

---

## Impact Formulation

### Mathematical Definition

For slice $i$:

**Raw Volumetric Contribution:**
$$V_i = \sum_{x,y} M_i(x,y)$$

**Connectivity Weight:**
$$w_i = \frac{1 + n_{\text{adjacent}}}{3}$$

**Weighted Impact:**
$$I_i^{\text{raw}} = V_i \cdot w_i$$

**Normalized Impact:**
$$I_i^{\text{norm}} = \frac{I_i^{\text{raw}}}{\max_j I_j^{\text{raw}}}$$

**Stabilized Impact (Final):**
$$I_i = \sqrt{I_i^{\text{norm}}}$$

### Configuration

- **Connectivity weighting:** Enabled (default)
- **Sqrt stabilization:** Enabled (default)
- **Normalization range:** [0, 1]

---

## Why Impact ≠ Uncertainty

Impact and uncertainty are **complementary but distinct** signals:

| Aspect | Uncertainty | Impact |
|--------|-------------|--------|
| **What it measures** | Model confidence | Volumetric importance |
| **High value means** | Model is uncertain | Slice is volumetrically important |
| **Low value means** | Model is confident | Slice has low volumetric contribution |
| **Independent of** | Tumor size | Model confidence |

**Key Insight:** Optimal slices have BOTH high uncertainty AND high impact.

---

## Why Impact is Needed in Addition to Uncertainty

**Problem with Uncertainty Alone:**
Uncertainty-only selection ignores volumetric importance.

**Example:**

- **Slice A:** High uncertainty (0.9), small tumor (10 voxels)
- **Slice B:** Medium uncertainty (0.6), large tumor (1000 voxels)

**Uncertainty-only:** Choose Slice A (suboptimal)  
**Impact-aware:** Choose Slice B (better global influence)

**Solution:** Combine uncertainty and impact (future phases).

---

## Limitations of the Chosen Impact Proxy

### 1. Prediction-Based (Not Ground Truth)

**Limitation:** Impact computed from model predictions, not ground truth.

**Implication:** If predictions are very wrong, impact may be misleading.

**Mitigation:** Use pretrained nnU-Net (high quality predictions).

### 2. Volume-Centric

**Limitation:** Focuses on volumetric contribution, not boundary accuracy.

**Implication:** May undervalue slices with small but critical structures.

### 3. No Semantic Context

**Limitation:** Does not consider anatomical or clinical importance.

**Implication:** All tumor voxels treated equally.

### 4. Simplified 3D Connectivity

**Limitation:** Uses simple adjacent slice counting.

**Alternative:** Full 3D connected component analysis (more complex).

### 5. No Correction Simulation

**Limitation:** Does not simulate actual expert corrections.

**Note:** Correction simulation is out of scope for Phase 5.

---

## Scope Limitations

### Phase 5 Does NOT Include

❌ **Slice Selection**

- No ranking of slices
- No budget constraints
- No selection strategies
- (Reserved for Phase 6+)

❌ **Uncertainty Combination**

- No combined uncertainty + impact scores
- No weighted combinations
- No rank-based fusion
- (Reserved for Phase 6+)

❌ **Optimization**

- No optimization algorithms
- No hyperparameter tuning
- No adaptive selection
- (Reserved for Phase 6+)

❌ **Expert Correction**

- No simulated corrections
- No ground truth replacement
- No corrected volume generation
- (Reserved for Phase 6+)

❌ **Evaluation**

- No strategy comparison
- No statistical analysis
- No Dice score computation
- (Reserved for Phase 6+)

---

## Testing

All components include built-in tests:

```bash
# Test volumetric impact
python models/impact/compute_impact.py
```

---

## Usage Examples

### Generate Impact

```bash
# Generate impact for all patients
python models/impact/generate_impact.py \
  --predictions_dir ./predictions \
  --output_dir ./impact \
  --use_connectivity \
  --use_sqrt_transform \
  --max_patients 10
```

### Load Impact

```python
import numpy as np

# Load impact for a patient
impact_data = np.load("impact/BraTS2021_00000.npy", allow_pickle=True).item()

patient_id = impact_data["patient_id"]
slices = impact_data["slices"]

# Access slice-level impact
for slice_data in slices:
    slice_id = slice_data["slice_id"]
    impact_score = slice_data["impact_score"]
    
    print(f"Slice {slice_id}: impact = {impact_score:.4f}")
```

### Combine with Uncertainty (Future)

```python
# NOT IMPLEMENTED IN PHASE 5
# This is for future phases only

import numpy as np

# Load uncertainty and impact
uncertainty_data = np.load("uncertainty/patient.npy", allow_pickle=True).item()
impact_data = np.load("impact/patient.npy", allow_pickle=True).item()

# Combine signals (example - NOT implemented)
for unc_slice, imp_slice in zip(uncertainty_data["slices"], impact_data["slices"]):
    uncertainty = unc_slice["slice_uncertainty"]
    impact = imp_slice["impact_score"]
    
    # Combined score (example)
    combined_score = uncertainty * impact
    
    print(f"Slice {unc_slice['slice_id']}: combined = {combined_score:.4f}")
```

---

## Success Criteria

Phase 5 is successful if:

1. ✅ Impact scores are computed per slice
2. ✅ Impact reflects volumetric importance
3. ✅ Impact is independent of uncertainty
4. ✅ Outputs are slice-aligned across phases
5. ✅ No decision or optimization logic exists
6. ✅ Documentation explains design and limitations
7. ✅ No ground truth is used
8. ✅ Deterministic (same predictions → same impact)
9. ✅ All tests pass
10. ✅ Impact framed as signal only

**Status: All criteria met ✅**

---

## Next Steps (Phase 6+ - NOT IMPLEMENTED)

Future phases will include:

- Combining uncertainty and impact signals
- Impact-weighted slice selection strategies
- Evaluation against baselines
- Statistical analysis

**DO NOT proceed to Phase 6 without explicit approval.**

---

## Important Notes

1. **Impact is a Signal**
   - NOT a decision rule
   - NOT used for selection in Phase 5
   - Provides information for future phases

2. **Impact ≠ Uncertainty**
   - Complementary signals
   - Both needed for optimal selection
   - Will be combined in future phases

3. **No Ground Truth Used**
   - Impact computed from predictions only
   - No Dice improvements
   - No expert corrections simulated

4. **Limitations**
   - Prediction-based (not ground truth)
   - Volume-centric (ignores boundaries)
   - Simplified 3D connectivity
   - No semantic context

---

## Verification Checklist

- [x] Impact scores computed per slice
- [x] Impact reflects volumetric importance
- [x] Impact independent of uncertainty
- [x] Outputs aligned with Phase 2–4
- [x] No decision-making logic
- [x] No optimization logic
- [x] No ground truth used
- [x] Deterministic computation
- [x] Documentation complete
- [x] Limitations explained
- [x] Tests pass

---

**Phase 5 Status: ✅ COMPLETE**

**Ready for:** User review and Phase 6 approval

**Date:** 2026-02-02

---

**END OF PHASE 5 COMPLETION REPORT**
