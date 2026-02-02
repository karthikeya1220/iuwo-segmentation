# Phase 7 — Expert Correction Simulation

## Overview

This module simulates **PERFECT EXPERT CORRECTION** on slices selected by a decision algorithm (IWUO or baselines).

**Scope:** SIMULATION ONLY  
**Phase 7 does NOT include:**

- Dice score computation
- Performance evaluation
- Baseline comparison
- Uncertainty or impact computation
- Slice selection logic
- Optimization
- Learning or retraining

---

## Correction Model

### Perfect Expert Assumption

We simulate a **perfect expert** who corrects selected slices with **ground truth**.

**Correction Rule:**

For each selected slice $i \in \mathcal{B}$:
$$\hat{Y}_i^{\text{corrected}} = Y_i \quad \text{(ground truth)}$$

For each unselected slice $j \notin \mathcal{B}$:
$$\hat{Y}_j^{\text{corrected}} = \hat{Y}_j \quad \text{(original prediction)}$$

**Properties:**

- **Deterministic:** Same inputs → same outputs
- **Perfect:** No noise, no errors, no partial corrections
- **Binary:** Slice is either fully corrected or unchanged

---

## Why Perfect Correction?

### 1. **Upper Bound on Performance**

Perfect correction establishes an **upper bound** on what can be achieved with expert-in-the-loop segmentation under a given budget.

- Real experts may make errors or provide partial corrections
- Perfect correction shows the **best-case scenario**
- Provides a **performance ceiling** for comparison

### 2. **Isolates Decision Quality**

By assuming perfect correction, we isolate the quality of the **slice selection decision** from the quality of the correction itself.

- Differences in performance are due to **which slices were selected**, not **how they were corrected**
- Enables fair comparison between selection strategies (IWUO vs baselines)

### 3. **Reproducibility**

Perfect correction is **deterministic and reproducible**.

- No human variability
- No annotation noise
- Results can be exactly replicated

---

## Why Simulation Instead of Human Experts?

### 1. **Scalability**

Simulating expert correction allows us to:

- Test on the **entire dataset** (hundreds of patients)
- Evaluate **multiple budgets** (B = 5, 10, 15, 20, ...)
- Compare **multiple strategies** (IWUO, Random, Uncertainty-Only, Impact-Only)

Human annotation at this scale would be:

- **Prohibitively expensive** (hundreds of hours of expert time)
- **Time-consuming** (weeks or months)
- **Infeasible** for a research prototype

### 2. **Controlled Experiments**

Simulation provides:

- **Perfect control** over correction quality
- **No confounding factors** (fatigue, inter-annotator variability)
- **Exact reproducibility** for validation

### 3. **Ground Truth Availability**

The BraTS dataset provides **expert-annotated ground truth** for all slices.

- We can use this ground truth to **simulate** what would happen if an expert corrected a slice
- This is a **valid proxy** for expert correction in a controlled research setting

---

## Limitations of Perfect Correction Assumption

### 1. **Overestimates Real-World Performance**

Real experts:

- May make **errors** or **miss small regions**
- May provide **partial corrections** (e.g., only correcting obvious errors)
- May have **inter-annotator variability**

Perfect correction assumes **none of these issues**, so:

- **Absolute performance** will be **higher** than in real deployment
- **Relative comparisons** between strategies remain valid

### 2. **Does Not Model Expert Effort**

Perfect correction assumes:

- All corrections take **equal time**
- Experts can correct **any slice** perfectly

In reality:

- Some slices may be **harder to correct** than others
- Expert effort may vary based on **slice complexity**

This limitation does **not affect** the validity of comparing selection strategies under a **fixed budget**.

### 3. **Binary Correction Model**

Our model assumes:

- Slices are either **fully corrected** (ground truth) or **unchanged** (prediction)

In reality:

- Experts may provide **partial corrections**
- Corrections may be **iterative** (multiple rounds)

This simplification is **acceptable** for:

- Establishing an **upper bound** on performance
- Comparing **slice selection strategies** under a hard budget

---

## When is Perfect Correction Valid?

Perfect correction is a **valid assumption** when:

1. **Goal is to compare selection strategies**, not to predict absolute real-world performance
2. **Ground truth is available** (as in BraTS)
3. **Budget constraint is hard** (expert can only review B slices)
4. **Focus is on decision-making**, not on the correction process itself

Perfect correction is **not valid** when:

- Modeling **real expert behavior** is required
- Estimating **absolute real-world performance** is the goal
- Studying **expert-model interaction dynamics**

---

## Artifact Format

For each patient, we create:

```
simulation/corrected/<patient_id>.npy
```

**Structure:**

```python
{
  "patient_id": str,
  "selected_slices": [int, int, ...],  # From Phase 6
  "corrected_slices": [
    {
      "slice_id": int,
      "mask": np.ndarray (H, W)  # Corrected or original
    },
    ...
  ]
}
```

**Invariants:**

- `len(corrected_slices)` equals total number of slices in volume
- `corrected_slices` is ordered by `slice_id`
- For `slice_id` in `selected_slices`: `mask` is ground truth
- For `slice_id` not in `selected_slices`: `mask` is original prediction

---

## Usage

### Apply Correction for a Single Patient

```python
from simulation.expert_correction import apply_correction_for_patient

corrected_data = apply_correction_for_patient(
    predictions_path="predictions/predictions/<patient_id>.npy",
    ground_truth_path="data/processed/<patient_id>.npy",
    selection_path="algorithms/selection/<patient_id>.npy",
    verbose=True
)

# Save corrected volume
np.save(f"simulation/corrected/{patient_id}.npy", corrected_data)
```

### Apply Correction Programmatically

```python
from simulation.expert_correction import apply_expert_correction

corrected_data = apply_expert_correction(
    predictions_data=predictions_data,
    ground_truth_data=ground_truth_data,
    selected_slices=[5, 10, 15, 20],
    verbose=True
)
```

---

## Verification

The expert correction simulator includes **strict verification**:

1. **Slice alignment:** Predictions and ground truth must have matching slice IDs
2. **Spatial dimensions:** All masks must have identical (H, W) dimensions
3. **Patient ID matching:** Predictions, ground truth, and selections must be for the same patient
4. **Valid selections:** All selected slice IDs must exist in the volume

---

## Next Steps

After Phase 7 is complete:

- **Phase 8:** Evaluation (compute Dice scores on corrected volumes)
- **Phase 9:** Baseline comparison (compare IWUO vs Random, Uncertainty-Only, etc.)

**Phase 7 does NOT perform evaluation.**  
Evaluation is strictly deferred to Phase 8.

---

## Design Rationale

### Why Separate Correction from Evaluation?

1. **Modularity:** Correction simulation is independent of evaluation metrics
2. **Reusability:** Corrected volumes can be evaluated with different metrics
3. **Clarity:** Separation enforces that Phase 7 is SIMULATION ONLY

### Why Use Ground Truth for Correction?

1. **Perfect expert assumption:** Ground truth represents what a perfect expert would produce
2. **Upper bound:** Establishes best-case performance under budget constraint
3. **Reproducibility:** Deterministic, no human variability

### Why Store Full Corrected Volumes?

1. **Evaluation flexibility:** Phase 8 can compute any metric on corrected volumes
2. **Visualization:** Corrected volumes can be visualized for qualitative analysis
3. **Debugging:** Full volumes enable verification of correction logic

---

## References

- **Phase 2:** Ground truth slicing (`data/processed/`)
- **Phase 3:** Frozen model predictions (`predictions/predictions/`)
- **Phase 6:** IWUO slice selection (`algorithms/selection/`)

---

**Phase 7 Status:** Implementation Complete  
**Next Phase:** Phase 8 (Evaluation)
