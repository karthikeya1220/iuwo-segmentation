# Phase 6 — Impact-Weighted Uncertainty Optimization (IWUO)

**IWUO: Budget-Constrained Slice Selection**

This module implements the IWUO decision algorithm for expert-in-the-loop slice selection.

IWUO answers: **"Given limited expert effort, which slices should be corrected?"**

---

## ⚠️ CRITICAL FRAMING

**IWUO in Phase 6 is DECISION-MAKING ONLY.**

This phase does NOT include:

- ❌ Expert correction simulation
- ❌ Dice score computation
- ❌ Performance evaluation
- ❌ Learning or retraining
- ❌ Uncertainty computation
- ❌ Impact computation
- ❌ Hyperparameter tuning

IWUO performs **slice selection** under a **hard budget constraint**.

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

---

## IWUO Algorithm

### Joint Priority Score

For each slice $i$, compute:

$$S_i = \alpha \cdot U_i + (1 - \alpha) \cdot I_i$$

where:

- $U_i$: normalized uncertainty score (epistemic uncertainty)
- $I_i$: normalized impact score (volumetric importance)
- $\alpha \in [0, 1]$: weighting parameter (hyperparameter)

**Default:** $\alpha = 0.5$ (equal weighting)

### Selection Rule

1. **Compute** joint scores $S_i$ for all slices
2. **Sort** slices by $S_i$ in descending order
3. **Select** top-$B$ slices
4. **Return** selected slice IDs $\mathcal{B}$

### Properties

- ✅ **Deterministic:** Same inputs → same outputs
- ✅ **Reproducible:** No randomness
- ✅ **Order-invariant:** Given identical inputs
- ✅ **Budget-constrained:** $|\mathcal{B}| \leq B$

---

## Why Both Uncertainty AND Impact are Required

### Problem with Uncertainty Alone

**Uncertainty-only selection** ignores volumetric importance.

**Example:**

- **Slice A:** High uncertainty (0.9), small tumor (10 voxels)
- **Slice B:** Medium uncertainty (0.6), large tumor (1000 voxels)

**Uncertainty-only ($\alpha = 1.0$):** Selects Slice A  
**Result:** Correcting Slice A has minimal global impact

### Problem with Impact Alone

**Impact-only selection** ignores model confidence.

**Example:**

- **Slice C:** Low uncertainty (0.2), large tumor (1000 voxels)
- **Slice D:** High uncertainty (0.9), medium tumor (500 voxels)

**Impact-only ($\alpha = 0.0$):** Selects Slice C  
**Result:** Model is already confident on Slice C; correction may not help

### Solution: IWUO (Combined)

**IWUO ($\alpha = 0.5$):** Balances both signals

**Optimal slices have:**

1. **High uncertainty** (model needs help)
2. **High impact** (corrections matter globally)

**Example:**

- **Slice E:** High uncertainty (0.9), large tumor (1000 voxels)
- **Joint score:** $S_E = 0.5 \times 0.9 + 0.5 \times 1.0 = 0.95$

**Result:** Slice E is prioritized (both uncertain AND important)

---

## Why the Problem is Budget-Constrained

### Expert Effort is Limited

**Reality:** Expert radiologists have limited time.

**Constraint:** Cannot review all slices in a volume.

**Budget:** Maximum number of slices expert can correct (e.g., $B = 10$).

### Hard Budget Constraint

**Definition:** $|\mathcal{B}| \leq B$ (strict inequality)

**Implication:** Must prioritize slices carefully.

**Trade-off:** Select slices with highest expected improvement.

### Why Not Soft Constraints?

**Soft constraints** (e.g., probabilistic budgets) are out of scope.

**Rationale:**

- Hard budgets are easier to interpret
- Align with real-world expert workflows
- Deterministic decision-making

---

## Why This is a Decision Problem, Not Learning

### Decision Problem

**Definition:** Given fixed signals (uncertainty, impact), select slices.

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

**Learned parameter:**

- Optimized from data
- Updated during training
- Data-driven

**$\alpha$ is a HYPERPARAMETER, not learned.**

---

## Limitations of Linear Weighting

### 1. Assumes Independence

**Limitation:** Linear combination assumes uncertainty and impact are independent.

**Reality:** They may be correlated (e.g., uncertain regions often have high impact).

**Implication:** Linear weighting may not capture interactions.

### 2. Fixed Weighting

**Limitation:** $\alpha$ is fixed for all slices.

**Reality:** Optimal weighting may vary per slice or patient.

**Implication:** Adaptive weighting could improve performance.

### 3. No Nonlinear Interactions

**Limitation:** Linear combination ignores nonlinear synergies.

**Example:** Multiplicative combination $S_i = U_i \times I_i$ could prioritize slices with BOTH high uncertainty AND high impact.

**Trade-off:** Nonlinear methods are less interpretable.

### 4. Ignores Spatial Context

**Limitation:** IWUO selects slices independently.

**Reality:** Adjacent slices may have correlated errors.

**Implication:** Spatial context could improve selection.

### 5. No Diversity Constraint

**Limitation:** IWUO may select clustered slices.

**Reality:** Diverse slice selection may be beneficial.

**Implication:** Diversity constraints could improve coverage.

---

## Why Linear Weighting is Used

Despite limitations, linear weighting is chosen for:

1. **Interpretability:** Easy to understand and explain
2. **Simplicity:** Minimal hyperparameters ($\alpha$ only)
3. **Efficiency:** Fast computation (no optimization)
4. **Baseline:** Establishes a simple baseline for future methods
5. **Transparency:** Clear decision rule

**Future work** could explore nonlinear combinations, adaptive weighting, or spatial constraints.

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

## Usage

### Generate Selections

```bash
# Generate IWUO selections for all patients
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

### Load Selections in Python

```python
import numpy as np

# Load selection for a patient
selection_data = np.load("selections/BraTS2021_00000.npy", allow_pickle=True).item()

patient_id = selection_data["patient_id"]
budget = selection_data["budget"]
alpha = selection_data["alpha"]
selected_slices = selection_data["selected_slices"]

print(f"Patient: {patient_id}")
print(f"Budget: {budget}")
print(f"Alpha: {alpha}")
print(f"Selected {len(selected_slices)} slices: {sorted(selected_slices)}")
```

### Use IWUO Selector Directly

```python
from algorithms.iwuo import IWUOSelector
import numpy as np

# Load uncertainty and impact
uncertainty_data = np.load("uncertainty/patient.npy", allow_pickle=True).item()
impact_data = np.load("impact/patient.npy", allow_pickle=True).item()

# Initialize selector
selector = IWUOSelector(alpha=0.5)

# Select slices
selected = selector.select(
    uncertainty_data=uncertainty_data,
    impact_data=impact_data,
    budget=10,
    verbose=True
)

print(f"Selected slices: {sorted(selected)}")
```

---

## Configuration

### Alpha (α)

**Range:** $\alpha \in [0, 1]$

**Interpretation:**

- $\alpha = 0.0$: Impact-only selection (ignore uncertainty)
- $\alpha = 0.5$: Equal weighting (default)
- $\alpha = 1.0$: Uncertainty-only selection (ignore impact)

**Default:** $\alpha = 0.5$

**Rationale:** Equal weighting balances both signals.

**Note:** $\alpha$ is a HYPERPARAMETER, not tuned here.

### Budget (B)

**Range:** $B \in \{1, 2, \ldots, N\}$ where $N$ is the number of slices

**Interpretation:** Maximum number of slices expert can review.

**Typical values:**

- $B = 5$: Very limited expert effort
- $B = 10$: Moderate expert effort (default)
- $B = 20$: High expert effort

**Note:** Budget is a CONSTRAINT, not optimized.

---

## Design Rationale

### Why Linear Combination?

**Rationale:** Simplicity and interpretability.

**Formula:** $S_i = \alpha \cdot U_i + (1 - \alpha) \cdot I_i$

**Alternatives:**

- Multiplicative: $S_i = U_i \times I_i$ (requires both high)
- Rank-based: Combine rankings instead of scores
- Learned: Train a selection policy

**Choice:** Linear for baseline simplicity.

### Why Top-B Selection?

**Rationale:** Greedy selection is simple and effective.

**Algorithm:** Sort by $S_i$, select top-$B$.

**Alternatives:**

- Diverse selection (maximize coverage)
- Spatially-aware selection (avoid clustering)
- Submodular optimization (diminishing returns)

**Choice:** Top-$B$ for baseline simplicity.

### Why Deterministic?

**Rationale:** Reproducibility and transparency.

**Property:** Same inputs → same outputs.

**Alternatives:**

- Stochastic policies (sample from distribution)
- Adaptive policies (update based on feedback)

**Choice:** Deterministic for reproducibility.

---

## Verification

All selection artifacts are verified to ensure:

- [x] Budget constraint satisfied ($|\mathcal{B}| \leq B$)
- [x] Selected slices are valid (exist in uncertainty/impact data)
- [x] No duplicate slice IDs
- [x] Deterministic (same inputs → same outputs)
- [x] Alpha in valid range ([0, 1])

---

## File Structure

```
algorithms/
├── iwuo.py                      # IWUO selector implementation
├── generate_selections.py       # Batch selection script
└── selection/                   # Selection artifacts (generated)
    └── <patient_id>.npy
```

---

## Dependencies

```bash
pip install numpy>=1.21.0
```

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
   - Greedy top-$B$ selection

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

## References

1. **Settles, B. (2009).** Active learning literature survey. *University of Wisconsin-Madison*.

2. **Gal, Y., Islam, R., & Ghahramani, Z. (2017).** Deep Bayesian active learning with image data. *ICML*.

3. **Sener, O., & Savarese, S. (2018).** Active learning for convolutional neural networks: A core-set approach. *ICLR*.

---

**Last Updated:** 2026-02-02  
**Phase:** 6 (IWUO Decision Algorithm)  
**Status:** Complete ✅
