# Phase 5 — Impact Estimation

**IMPACT IS A SIGNAL, NOT A DECISION RULE**

This module computes the global volumetric impact of correcting each slice.

Impact answers: **"How much does correcting this slice matter for the final 3D segmentation?"**

---

## ⚠️ CRITICAL FRAMING

**Impact in Phase 5 is a SIGNAL ONLY.**

This phase does NOT include:

- ❌ Slice selection
- ❌ Ranking for decision-making
- ❌ Budget constraints
- ❌ Optimization logic
- ❌ Expert correction simulation
- ❌ Uncertainty combination
- ❌ Dice evaluation

Impact provides information about volumetric importance, but it is NOT used to make decisions in this phase.

---

## Impact Definition

### What is Impact?

**Definition:** The global volumetric importance of correcting a slice, measured by its contribution to the total 3D segmentation.

**Interpretation:** High impact indicates slices where corrections would have large influence on the final volumetric segmentation.

**Formulation:** Slice-wise contribution to total predicted tumor volume, weighted by 3D spatial connectivity.

### Why Impact ≠ Uncertainty?

Impact and uncertainty are **complementary but distinct** signals:

| Aspect | Uncertainty | Impact |
|--------|-------------|--------|
| **What it measures** | Model confidence | Volumetric importance |
| **High value means** | Model is uncertain | Slice is volumetrically important |
| **Low value means** | Model is confident | Slice has low volumetric contribution |
| **Independent of** | Tumor size | Model confidence |
| **Example** | Small tumor, high uncertainty | Large tumor, low uncertainty |

**Key Insight:** A slice can have:

- High uncertainty, low impact (small uncertain region)
- Low uncertainty, high impact (large confident tumor)
- High uncertainty, high impact (large uncertain tumor) ← **Most important**
- Low uncertainty, low impact (small confident region)

### Why Impact is Needed in Addition to Uncertainty?

**Problem with Uncertainty Alone:**
Uncertainty-only selection ignores volumetric importance.

**Example:**

- **Slice A:** High uncertainty (entropy = 0.9), small tumor (10 voxels)
- **Slice B:** Medium uncertainty (entropy = 0.6), large tumor (1000 voxels)

**Uncertainty-only selection:** Choose Slice A (higher uncertainty)  
**Impact-aware selection:** Choose Slice B (higher global influence)

**Solution:**
Combine uncertainty and impact to identify slices that are both:

1. Uncertain (model needs help)
2. Important (corrections matter globally)

---

## Impact Formulation

### Chosen Formulation

**Slice-wise contribution to total predicted tumor volume, weighted by 3D spatial connectivity.**

### Mathematical Definition

For slice $i$:

**Raw Volumetric Contribution:**
$$V_i = \sum_{x,y} M_i(x,y)$$

where $M_i$ is the predicted binary mask for slice $i$.

**Connectivity Weight:**
$$w_i = \frac{1 + n_{\text{adjacent}}}{3}$$

where $n_{\text{adjacent}} \in \{0, 1, 2\}$ is the number of adjacent slices with foreground.

**Weighted Impact:**
$$I_i^{\text{raw}} = V_i \cdot w_i$$

**Normalized Impact:**
$$I_i^{\text{norm}} = \frac{I_i^{\text{raw}}}{\max_j I_j^{\text{raw}}}$$

**Stabilized Impact (Final):**
$$I_i = \sqrt{I_i^{\text{norm}}}$$

### Rationale for Each Component

1. **Volumetric Contribution ($V_i$):**
   - Larger tumor regions have higher impact
   - Reflects potential influence on global segmentation
   - Directly measurable from predictions

2. **Connectivity Weighting ($w_i$):**
   - Slices in tumor core (surrounded by tumor) have higher impact
   - Peripheral slices have lower impact
   - Captures 3D spatial context

3. **Normalization:**
   - Makes impact scores comparable across patients
   - Range: [0, 1]

4. **Sqrt Stabilization:**
   - Reduces dynamic range
   - Prevents extreme values from dominating
   - Standard transform in medical imaging

### Why This Formulation?

**Advantages:**

- ✅ Computable from predictions only (no ground truth needed)
- ✅ Reflects volumetric importance
- ✅ Incorporates 3D spatial context
- ✅ Monotonic with respect to tumor size
- ✅ Normalized and stable

**Alternatives Considered:**

- **Dice improvement:** Requires ground truth (forbidden)
- **Gradient-based importance:** Requires model gradients (complex)
- **Shapley values:** Computationally expensive

---

## Limitations of the Chosen Impact Proxy

### 1. Prediction-Based (Not Ground Truth)

**Limitation:** Impact is computed from model predictions, not ground truth.

**Implication:** If predictions are very wrong, impact estimates may be misleading.

**Mitigation:** Use pretrained nnU-Net (high quality predictions).

### 2. Volume-Centric

**Limitation:** Impact focuses on volumetric contribution, not boundary accuracy.

**Implication:** May undervalue slices with small but critical structures.

**Example:** A slice with a small but critical tumor boundary may have low impact.

### 3. No Semantic Context

**Limitation:** Impact does not consider anatomical or clinical importance.

**Implication:** All tumor voxels are treated equally.

**Example:** Tumor near critical structures may be clinically more important.

### 4. 3D Connectivity is Simplified

**Limitation:** Connectivity weight uses simple adjacent slice counting.

**Implication:** More sophisticated 3D connected component analysis could improve accuracy.

**Alternative:** Use full 3D connected components (more complex).

### 5. No Correction Simulation

**Limitation:** Impact does not simulate actual expert corrections.

**Implication:** Assumes corrections proportional to volume (may not hold).

**Note:** Correction simulation is out of scope for Phase 5.

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

## Usage

### Generate Impact Artifacts

```bash
# Generate impact for all patients
python models/impact/generate_impact.py \
  --predictions_dir ./predictions \
  --output_dir ./impact \
  --use_connectivity \
  --use_sqrt_transform \
  --max_patients 10

# Verify impact artifacts
python models/impact/generate_impact.py \
  --verify \
  --impact_dir ./impact \
  --predictions_dir ./predictions
```

### Load Impact in Python

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

---

## Configuration

### Connectivity Weighting

**Default:** Enabled

**Rationale:**

- Incorporates 3D spatial context
- Slices in tumor core have higher impact
- Reflects global volumetric importance

**Disable with:** `--no_connectivity`

### Sqrt Stabilization

**Default:** Enabled

**Rationale:**

- Reduces dynamic range
- Prevents extreme values
- Standard transform in medical imaging

**Formula:** $I_i = \sqrt{I_i^{\text{norm}}}$

**Effect:**

- Large values compressed more than small values
- Example: 0.01 → 0.1, 0.25 → 0.5, 1.0 → 1.0

**Disable with:** `--no_sqrt_transform`

---

## Design Rationale

### Why Volumetric Impact?

**Rationale:** Volume is the primary clinical metric for tumor segmentation.

**Alternatives:**

- Boundary-based impact: More complex, less interpretable
- Dice-based impact: Requires ground truth (forbidden)

### Why Connectivity Weighting?

**Rationale:** 3D context matters for global segmentation quality.

**Example:**

- Isolated peripheral slice: Low connectivity, lower impact
- Core slice surrounded by tumor: High connectivity, higher impact

### Why Sqrt Transform?

**Rationale:** Stabilizes scores and reduces outlier influence.

**Mathematical Property:**

- Sqrt is a concave function
- Compresses large values more than small values
- Preserves monotonicity

---

## Verification

All impact artifacts are verified to ensure:

- [x] Slice IDs match Phase 3 predictions
- [x] Impact scores are scalars, range [0, 1]
- [x] No NaN or Inf values
- [x] Deterministic (same predictions → same impact)
- [x] Monotonic with respect to tumor volume

---

## File Structure

```
models/impact/
├── compute_impact.py         # Volumetric impact implementation
├── generate_impact.py        # Batch generation script
├── README.md                 # This file
└── <patient_id>.npy          # Impact artifacts (generated)
```

---

## Dependencies

```bash
pip install numpy>=1.21.0
```

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

## Combining Impact and Uncertainty (Future Work)

**Phase 5 Scope:** Compute impact only (NO combination)

**Future Phases:** Combine impact and uncertainty for optimized selection

**Combination Strategy (NOT IMPLEMENTED):**

- Multiplicative: $S_i = U_i \times I_i$ (both high → high score)
- Additive: $S_i = \alpha U_i + (1-\alpha) I_i$ (weighted sum)
- Rank-based: Combine rankings instead of raw scores

**Note:** Combination is OUT OF SCOPE for Phase 5.

---

## References

1. **Kohl, S., et al. (2018).** A probabilistic U-Net for segmentation of ambiguous images. *NeurIPS*.

2. **Jungo, A., et al. (2020).** Analyzing the quality and challenges of uncertainty estimations for brain tumor segmentation. *Frontiers in Neuroscience*.

3. **Settles, B. (2009).** Active learning literature survey. *University of Wisconsin-Madison*.

---

**Last Updated:** 2026-02-02  
**Phase:** 5 (Impact Estimation)  
**Status:** Complete ✅
