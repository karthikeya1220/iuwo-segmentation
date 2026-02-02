# Phase 8 — Evaluation

## Overview

Phase 8 evaluates segmentation quality improvement under limited expert effort.
It computes **Dice Similarity Coefficient (DSC)** for corrected volumes across multiple strategies and budgets.

**Scope:** EVALUATION ONLY  
**Phase 8 does NOT include:**

- Decision-making (uses existing strategies)
- Learning or retraining
- Hyperparameter tuning

---

## Evaluation Protocol

### 1. Strategies Evaluated

| Strategy | Description | Phase |
|----------|-------------|-------|
| **No Correction** | Baseline nnU-Net prediction (Budget = 0%) | Phase 3 |
| **Random** | Select B slices uniformly at random | Phase 3 |
| **Uniform** | Select B slices with uniform spacing | Phase 3 |
| **Uncertainty-Only** | Select top-B slices by epistemic uncertainty | Phase 4 |
| **Impact-Only** | Select top-B slices by estimated impact | Phase 5 |
| **IWUO (Proposed)** | Select top-B slices by Impact-Weighted Uncertainty | Phase 6 |

### 2. Budgets

We evaluate at fixed percentages of total slices per volume:
$B \in \{5\%, 10\%, 20\%, 30\%, 50\%\}$

### 3. Metric

**Dice Similarity Coefficient (DSC):**
$$DSC = \frac{2 |P \cap G|}{|P| + |G|}$$

- Computed on the **full 3D corrected volume**
- Correction simulation (Phase 7) is applied before evaluation
- Ground truth is identical for all strategies

---

## Artifact Structure

### Results File

`evaluation/results.npy`

Structure:

```python
{
  "budgets": [0.05, 0.10, ...],
  "strategies": ["No Correction", "Random", ...],
  "per_patient": {
      "<patient_id>": {
          "<strategy>": {
              "<budget>": dice_score
          }
      }
  },
  "aggregate": {
      "<strategy>": {
          "<budget>": {
              "mean": float,
              "std": float
          }
      }
  }
}
```

### Plots

`evaluation/dice_vs_budget.png`: Mean Dice ± Std Dev vs Budget %

---

## Why Improvement Over Baseline Matters?

The baseline (No Correction) represents the fully automated performance.
Improvement over baseline ($\Delta DSC$) quantifies the value of expert intervention.

- **Efficiency:** How fast does Dice improve per slice corrected?
- **Effectiveness:** What is the maximum achievable Dice given the budget?

IWUO aims to maximize $\Delta DSC$ for a fixed budget $B$ compared to other strategies.

---

## Fairness

To ensure fair evaluation:

1. **Identical Budget:** All strategies select exactly $B$ slices (unless volume exhausted).
2. **Identical Correction:** All selected slices are corrected perfectly (Phase 7 simulation).
3. **Identical Evaluation:** Same ground truth and metric implementation used for all.

---

## Usage

### Run Evaluation

```bash
python evaluation/evaluate_strategies.py \
    --predictions_dir predictions/predictions \
    --ground_truth_dir data/processed \
    --uncertainty_dir models/uncertainty \
    --impact_dir models/impact \
    --output_file evaluation/results.npy
```

### Generate Plots

```bash
python evaluation/plots.py \
    --results_file evaluation/results.npy \
    --output_file evaluation/dice_vs_budget.png
```

---

## Limitations

- **Perfect Correction Assumption:** Results represent an upper bound (see Phase 7).
- **No User Variability:** Does not account for expert fatigue or error.
- **Fixed Alpha:** IWUO uses $\alpha=0.5$ without per-patient tuning.

---

**Phase 8 Status:** Implementation Complete  
**Next Phase:** NONE (Project ends at Phase 8/Evaluation as requested)
