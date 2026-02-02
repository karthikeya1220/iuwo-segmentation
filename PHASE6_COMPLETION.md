# Phase 6 — Completion Report

**Impact-Weighted Uncertainty Optimization for Expert-in-the-Loop Brain Tumor Segmentation**

**Phase:** 6 (IWUO Decision Algorithm)  
**Status:** ✅ Complete  
**Date:** 2026-02-02

> **Note:** IWUO performs DECISION-MAKING ONLY.  
> This phase does NOT include evaluation or correction simulation.

---

## Executive Summary

Phase 6 implements **Impact-Weighted Uncertainty Optimization (IWUO)**, a deterministic budget-constrained slice selection algorithm.

**IWUO answers:** "Given limited expert effort, which slices should be corrected?"

**CRITICAL FRAMING:** IWUO is DECISION-MAKING ONLY.

This phase does NOT include:

- Expert correction simulation
- Dice score computation
- Performance evaluation
- Learning or retraining
- Uncertainty computation
- Impact computation
- Hyperparameter tuning

These features are intentionally excluded and will be addressed in future phases.

---

## Deliverables

### Phase 6.1 — IWUO Selector

✅ **File:** `algorithms/iwuo.py`

**Description:** IWUO decision algorithm for budget-constrained slice selection.

**Key Features:**

- Joint priority scoring: $S_i = \alpha \cdot U_i + (1 - \alpha) \cdot I_i$
- Top-B greedy selection
- Deterministic and reproducible
- Budget constraint enforcement
- Slice alignment verification

**Implementation:**

- `IWUOSelector` class
- Linear combination of uncertainty and impact
- Greedy top-B selection
- No internal signal computation

**Usage:**

```python
from algorithms.iwuo import IWUOSelector

selector = IWUOSelector(alpha=0.5)

selected = selector.select(
    uncertainty_data=uncertainty_data,
    impact_data=impact_data,
    budget=10
)
```

---

✅ **File:** `algorithms/generate_selections.py`

**Description:** Batch script to generate IWUO selections for all patients.

**Key Features:**

- Processes all patients with uncertainty and impact data
- Saves selection artifacts in required format
- Includes verification utilities
- Command-line interface

**Usage:**

```bash
# Generate selections
python algorithms/generate_selections.py \
  --uncertainty_dir ./uncertainty \
  --impact_dir ./impact \
  --output_dir ./selections \
  --budget 10 \
  --alpha 0.5

# Verify selections
python algorithms/generate_selections.py \
  --verify \
  --selection_dir ./selections \
  --uncertainty_dir ./uncertainty \
  --impact_dir ./impact
```

---

✅ **File:** `algorithms/README.md`

**Description:** Comprehensive documentation for IWUO.

**Contents:**

- The IWUO decision rule
- Why both uncertainty and impact are required
- Why the problem is budget-constrained
- Why this is a decision problem, not learning
- Limitations of linear weighting
- Mathematical formulation
- Usage examples

**Key Statements:**

1. "IWUO is decision-making only"
2. "Both uncertainty AND impact are required"
3. "Alpha is a hyperparameter, not learned"
4. "Linear weighting has limitations"

---

✅ **File:** `algorithms/__init__.py`

**Description:** Package initialization for algorithms module.

---

## IWUO Definition

### Decision Problem

**Given:**

- Slice-level uncertainty scores $U_i \in [0,1]$ (Phase 4)
- Slice-level impact scores $I_i \in [0,1]$ (Phase 5)
- Expert budget $B$ (number of slices)

**Find:**

- A set of slice IDs $\mathcal{B}$ such that $|\mathcal{B}| \leq B$

**Objective:**

- Maximize expected segmentation improvement under expert budget

### IWUO Algorithm

**Joint Priority Score:**
$$S_i = \alpha \cdot U_i + (1 - \alpha) \cdot I_i$$

where:

- $U_i$: normalized uncertainty score
- $I_i$: normalized impact score
- $\alpha \in [0, 1]$: weighting parameter (default: 0.5)

**Selection Rule:**

1. Compute $S_i$ for all slices
2. Sort slices by $S_i$ (descending)
3. Select top-$B$ slices
4. Return $\mathcal{B}$

### Properties

- ✅ Deterministic
- ✅ Reproducible
- ✅ Order-invariant
- ✅ Budget-constrained

---

## Output Format

### Per-Patient Selection

**File:** `algorithms/selection/<patient_id>.npy`

**Structure:**

```python
{
  "patient_id": str,
  "budget": int,
  "alpha": float,
  "selected_slices": [int, int, ...]
}
```

### Fields

- **`patient_id`:** Patient identifier
- **`budget`:** Maximum number of slices (B)
- **`alpha`:** Weighting parameter
- **`selected_slices`:** List of selected slice IDs (length ≤ budget)

---

## File Structure

```
iuwo-segmentation/
├── algorithms/
│   ├── __init__.py                      # Package initialization
│   ├── iwuo.py                          # IWUO selector
│   ├── generate_selections.py           # Batch selection script
│   ├── README.md                        # IWUO documentation
│   └── selection/                       # Selection artifacts (generated)
│       └── <patient_id>.npy
├── [Phase 1-5 files unchanged]
└── PHASE6_COMPLETION.md                 # This file
```

---

## Design Principles

### 1. Decision-Making Only

**Principle:** IWUO performs slice selection, not evaluation.

**Implementation:**

- No Dice computation
- No correction simulation
- No performance metrics
- Pure decision rule

### 2. Budget-Constrained

**Principle:** Expert effort is limited.

**Constraint:** $|\mathcal{B}| \leq B$

**Implementation:**

- Hard budget constraint
- Greedy top-B selection
- No soft constraints

### 3. Combines Uncertainty and Impact

**Principle:** Both signals are required for optimal selection.

**Rationale:**

- Uncertainty alone ignores volumetric importance
- Impact alone ignores model confidence
- Combined signal balances both

**Implementation:**

- Linear combination: $S_i = \alpha \cdot U_i + (1 - \alpha) \cdot I_i$

### 4. Deterministic

**Principle:** Reproducibility and transparency.

**Property:** Same inputs → same outputs

**Implementation:**

- No randomness
- Greedy selection
- Fixed $\alpha$

---

## Why Both Uncertainty AND Impact are Required

### Problem with Uncertainty Alone

**Example:**

- **Slice A:** High uncertainty (0.9), small tumor (10 voxels)
- **Slice B:** Medium uncertainty (0.6), large tumor (1000 voxels)

**Uncertainty-only ($\alpha = 1.0$):** Selects Slice A  
**Problem:** Minimal global impact

### Problem with Impact Alone

**Example:**

- **Slice C:** Low uncertainty (0.2), large tumor (1000 voxels)
- **Slice D:** High uncertainty (0.9), medium tumor (500 voxels)

**Impact-only ($\alpha = 0.0$):** Selects Slice C  
**Problem:** Model already confident

### Solution: IWUO

**IWUO ($\alpha = 0.5$):** Balances both signals

**Optimal slices:**

1. High uncertainty (model needs help)
2. High impact (corrections matter globally)

---

## Why the Problem is Budget-Constrained

### Expert Effort is Limited

**Reality:** Expert radiologists have limited time.

**Constraint:** Cannot review all slices.

**Budget:** Maximum number of slices expert can correct (e.g., $B = 10$).

### Hard Budget Constraint

**Definition:** $|\mathcal{B}| \leq B$ (strict inequality)

**Implication:** Must prioritize slices carefully.

**Trade-off:** Select slices with highest expected improvement.

---

## Why This is a Decision Problem, Not Learning

### Decision Problem

**Definition:** Given fixed signals, select slices.

**Characteristics:**

- No training data
- No model updates
- No parameter learning
- Deterministic rule

**IWUO is a decision problem.**

### NOT a Learning Problem

**Learning would involve:**

- Training a selection policy
- Optimizing $\alpha$ based on outcomes
- Adapting to expert feedback
- Updating model parameters

**IWUO does NOT do any of this.**

### Hyperparameter vs Learned Parameter

**Hyperparameter ($\alpha$):**

- Fixed before selection
- Not optimized during selection
- Chosen by designer (default: 0.5)

**$\alpha$ is a HYPERPARAMETER, not learned.**

---

## Limitations of Linear Weighting

### 1. Assumes Independence

**Limitation:** Linear combination assumes uncertainty and impact are independent.

**Reality:** They may be correlated.

### 2. Fixed Weighting

**Limitation:** $\alpha$ is fixed for all slices.

**Reality:** Optimal weighting may vary per slice.

### 3. No Nonlinear Interactions

**Limitation:** Ignores nonlinear synergies.

**Alternative:** Multiplicative $S_i = U_i \times I_i$

### 4. Ignores Spatial Context

**Limitation:** Selects slices independently.

**Reality:** Adjacent slices may have correlated errors.

### 5. No Diversity Constraint

**Limitation:** May select clustered slices.

**Reality:** Diverse selection may be beneficial.

---

## Why Linear Weighting is Used

Despite limitations:

1. **Interpretability:** Easy to understand
2. **Simplicity:** Minimal hyperparameters
3. **Efficiency:** Fast computation
4. **Baseline:** Establishes simple baseline
5. **Transparency:** Clear decision rule

---

## Scope Limitations

### Phase 6 Does NOT Include

❌ **Expert Correction**

- No simulated corrections
- No ground truth replacement
- (Reserved for Phase 7+)

❌ **Evaluation**

- No Dice computation
- No strategy comparison
- No statistical analysis
- (Reserved for Phase 7+)

❌ **Hyperparameter Tuning**

- No $\alpha$ optimization
- No budget optimization
- (Reserved for Phase 7+)

❌ **Learning**

- No policy training
- No adaptive selection
- No model updates
- (Out of scope)

---

## Testing

All components include built-in tests:

```bash
# Test IWUO selector
python algorithms/iwuo.py
```

---

## Usage Examples

### Generate Selections

```bash
# Generate IWUO selections for all patients
python algorithms/generate_selections.py \
  --uncertainty_dir ./uncertainty \
  --impact_dir ./impact \
  --output_dir ./selections \
  --budget 10 \
  --alpha 0.5 \
  --max_patients 10
```

### Load Selections

```python
import numpy as np

# Load selection for a patient
selection_data = np.load("selections/BraTS2021_00000.npy", allow_pickle=True).item()

patient_id = selection_data["patient_id"]
budget = selection_data["budget"]
alpha = selection_data["alpha"]
selected_slices = selection_data["selected_slices"]

print(f"Patient: {patient_id}")
print(f"Selected {len(selected_slices)} slices: {sorted(selected_slices)}")
```

---

## Success Criteria

Phase 6 is successful if:

1. ✅ Slice selection obeys budget constraints
2. ✅ Selection is deterministic
3. ✅ Uses BOTH uncertainty and impact
4. ✅ Does not compute signals internally
5. ✅ Does not perform evaluation
6. ✅ Implements IWUO exactly as defined
7. ✅ Documentation clearly explains decision logic
8. ✅ No correction simulation
9. ✅ No Dice computation
10. ✅ All tests pass

**Status: All criteria met ✅**

---

## Next Steps (Phase 7+ - NOT IMPLEMENTED)

Future phases will include:

- Expert correction simulation
- Dice score evaluation
- Strategy comparison (IWUO vs baselines)
- Statistical analysis

**DO NOT proceed to Phase 7 without explicit approval.**

---

## Important Notes

1. **Decision-Making Only**
   - NO evaluation
   - NO correction simulation
   - NO Dice computation
   - Pure slice selection

2. **Uses Pre-Computed Signals**
   - Uncertainty from Phase 4
   - Impact from Phase 5
   - Does NOT compute signals internally

3. **Budget-Constrained**
   - Hard budget constraint
   - $|\mathcal{B}| \leq B$
   - Greedy top-B selection

4. **Hyperparameter**
   - $\alpha$ is a hyperparameter
   - NOT tuned or optimized here
   - Default: 0.5 (equal weighting)

5. **Limitations**
   - Linear weighting (no interactions)
   - Fixed $\alpha$ (no adaptation)
   - Independent selection (no spatial context)
   - No diversity constraint

---

## Verification Checklist

- [x] IWUO selector implemented
- [x] Budget constraint enforced
- [x] Selection is deterministic
- [x] Uses both uncertainty and impact
- [x] Does not compute signals internally
- [x] Does not perform evaluation
- [x] Documentation complete
- [x] Limitations explained
- [x] Tests pass

---

**Phase 6 Status: ✅ COMPLETE**

**Ready for:** User review and Phase 7 approval

**Date:** 2026-02-02

---

**END OF PHASE 6 COMPLETION REPORT**
