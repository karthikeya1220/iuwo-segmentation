# Research Workflow

This document defines the strict execution order of the project.
No phase may skip ahead or absorb responsibilities from another phase.

---

## Phase 1 — Problem Formulation

Objective:

- Formalize expert-in-the-loop segmentation as a budget-constrained optimization problem.

Deliverables:

- Mathematical problem definition
- Explicit decision variables and constraints
- Clear separation of prediction vs decision-making

No code beyond definitions.

---

## Phase 2 — Dataset Loading & Axial Slicing

Objective:

- Convert BraTS volumes into slice-level decision units.

Tasks:

- Load NIfTI volumes
- Use a single modality (FLAIR)
- Slice strictly along the axial axis
- Preserve all slices, including empty ones

Deliverables:

- One `.npy` file per patient
- Stable slice indexing
- Image–mask alignment verification

No models, no metrics.

---

## Phase 3 — Frozen Segmentation Inference

Objective:

- Generate baseline predictions using a pretrained model.

Tasks:

- Run inference only
- Store probability maps and binary masks
- Preserve spatial correspondence with slices

Deliverables:

- Slice-aligned prediction artifacts
- Baseline Dice scores (no interaction)

No retraining.

---

## Phase 4 — Predictive Uncertainty Estimation

Objective:

- Estimate epistemic uncertainty per slice.

Tasks:

- Use MC Dropout at inference
- Compute voxel-wise entropy
- Aggregate to slice-level uncertainty scores

Deliverables:

- Slice uncertainty distributions
- Visual sanity checks

No decision logic yet.

---

## Phase 5 — Correction Impact Estimation

Objective:

- Estimate how much correcting a slice influences global outcome.

Tasks:

- Approximate volumetric contribution per slice
- Normalize and stabilize impact scores

Deliverables:

- Slice impact scores
- Impact distribution analysis

---

## Phase 6 — Slice Selection Algorithm

Objective:

- Combine uncertainty and impact under a budget constraint.

Tasks:

- Define deterministic ranking function
- Select top-B slices
- Verify ranking stability

Deliverables:

- Slice rankings
- Selected slice sets per budget

---

## Phase 7 — Expert Correction Simulation

Objective:

- Apply corrections without human bias.

Tasks:

- Replace predictions with ground truth on selected slices
- Leave remaining slices unchanged

Deliverables:

- Corrected segmentation volumes

---

## Phase 8 — Baseline Strategies

Objective:

- Establish non-triviality of the proposed method.

Tasks:

- Implement random, uniform, uncertainty-only, impact-only baselines
- Apply identical correction simulation

Deliverables:

- Baseline comparison tables

---

## Phase 9 — Evaluation & Trade-off Analysis

Objective:

- Quantify effort vs accuracy behavior.

Tasks:

- Evaluate multiple budgets
- Plot Dice vs effort curves
- Analyze low-budget regimes

Deliverables:

- Trade-off plots
- Quantitative comparisons

---

## Phase 10 — Failure Analysis & Discussion

Objective:

- Demonstrate research maturity.

Tasks:

- Identify failure modes
- Analyze assumptions and limitations
- Propose future extensions

Deliverables:

- Failure taxonomy
- Limitations section

---

## Workflow Rule

Each phase must:

- Produce its own artifacts
- Avoid leaking responsibilities into other phases
- Be justifiable independently to a reviewer
