# Impact-Weighted Optimization for Expert-in-the-Loop Brain Tumor Segmentation

**Research Prototype — PhD-Level Medical Image Analysis**

---

## Project Overview

This project formalizes expert-in-the-loop brain tumor segmentation as a **budget-constrained decision problem**. It introduces **Impact-Weighted Uncertainty Optimization (IWUO)**, a decision algorithm that optimally allocates limited expert corrections to slices where they will maximize final volumetric segmentation accuracy (Dice score).

### Core Hypothesis

Selecting slices for expert correction based on **uncertainty alone is insufficient** because it ignores failure magnitude. By combining epistemic uncertainty (probability of error) with volumetric impact estimation (cost of error), we can maximize the return on expert effort.

### Scope & Assumptions

- ✅ The segmentation model is **frozen** (no retraining).
- ✅ Expert interaction is **simulated and perfect** (upper bound analysis).
- ✅ Expert effort is modeled as a hard budget on the **number of axial slices**.
- ❌ NO active learning, NO GUI, NO real-time user interaction.

---

## Phase Status Summary

| Phase | Status | Deliverable |
| :--- | :--- | :--- |
| **1. Formulation** | ✅ Complete | Formalized budget-constrained optimization problem |
| **2. Data** | ✅ Complete | BraTS loading & axial slicing pipeline |
| **3. Baseline** | ✅ Complete | Pretrained nnU-Net inference & Random/Uniform baselines |
| **4. Uncertainty** | ✅ Complete | MC Dropout based epistemic uncertainty estimation |
| **5. Impact** | ✅ Complete | Volumetric impact proxy estimation |
| **6. IWUO** | ✅ Complete | Impact-Weighted Uncertainty Optimization algorithm |
| **7. Simulation** | ✅ Complete | Perfect expert correction simulator |
| **8. Evaluation** | ✅ Complete | Multi-strategy, multi-budget Dice evaluation |
| **9. Analysis** | ✅ Complete | Effort-accuracy trade-off interpretation |
| **10. Limitations** | ✅ Complete | Failure mode analysis & scope bounding |

---

## Technical Architecture

The project is structured as a modular research pipeline:

1. **Prediction (Phase 3):** Generate initial segmentations using a frozen nnU-Net.
2. **Signal Extraction (Phase 4-5):** Compute two selection signals per slice:
    - $U_i$: Epistemic uncertainty (Entropy via MC Dropout)
    - $I_i$: Impact proxy (Predicted tumor volume)
3. **Decision Making (Phase 6):** Select top-$B$ slices maximizing $S_i = \alpha U_i + (1-\alpha) I_i$.
4. **Simulation (Phase 7):** Replace predictions with ground truth for selected slices.
5. **Evaluation (Phase 8):** Compute Dice on the corrected volumes.

---

## Key Results

Analysis of the experimental results reveals:

1. **Low-Budget Dominance:** IWUO outperforms Random, Uniform, and Uncertainty-only strategies in low-budget regimes ($<10\%$ of slices).
2. **Efficiency:** IWUO achieves the steepest initial gain in Dice score per unit of expert effort.
3. **Failure Modes:** Pure uncertainty selection wastes budget on complex boundaries of small/irrelevant structures. Pure impact selection wastes budget on large, confident correct predictions. IWUO balances these risks.

---

## Repository Structure

```text
iuwo-segmentation/
├── algorithms/           # IWUO decision logic (Phase 6)
├── analysis/             # Interpretative reports (Phase 9-10)
├── data/                 # BraTS processing pipeline (Phase 2)
├── evaluation/           # Metrics and plots (Phase 8)
├── experiments/          # Theoretical formulation (Phase 1)
├── models/               # nnU-Net, Uncertainty, Impact (Phase 3-5)
├── simulation/           # Expert correction logic (Phase 7)
├── strategies/           # Baseline selectors (Random, Uniform) (Phase 3)
└── requirements.txt      # Dependencies
```

---

## Usage Instructions

### 1. Setup

```bash
pip install -r requirements.txt
```

### 2. Run Pipeline (Example)

The pipeline assumes artifacts are generated sequentially. To run evaluation assuming artifacts exist:

```bash
python evaluation/evaluate_strategies.py \
  --predictions_dir predictions/predictions \
  --ground_truth_dir data/processed \
  --uncertainty_dir models/uncertainty/artifacts \
  --impact_dir models/impact/artifacts \
  --output_file evaluation/results.npy
```

### 3. Visualize Results

```bash
python evaluation/plots.py \
  --results_file evaluation/results.npy \
  --output_file evaluation/dice_vs_budget.png
```

---

## Citation & Authorship

**Author:** Research Prototype  
**Date:** February 2026  
**Context:** Advanced Agentic Coding - Deepmind
