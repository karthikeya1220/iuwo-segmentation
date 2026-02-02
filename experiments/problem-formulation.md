# Phase 1 — Problem Formulation & Research Scope

## 1. Motivation

Deep learning–based brain tumor segmentation models achieve strong average accuracy but remain unreliable in localized regions. In clinical workflows, these failures are typically corrected by human experts, whose time and attention constitute a scarce resource.  

Most existing interactive segmentation systems focus on *how* experts provide corrections (e.g., clicks, scribbles, refinement loops), but do not explicitly model *where* expert effort should be allocated when only a limited fraction of the volume can be reviewed.

This project formulates expert-in-the-loop segmentation as a **budget-constrained decision problem**, where the goal is to optimally allocate limited expert corrections to maximize final segmentation quality.

---

## 2. Task Definition

Let a 3D medical image volume and its corresponding ground truth be defined as:

$$V \in \mathbb{R}^{H \times W \times D}$$
$$Y \in \{0,1\}^{H \times W \times D}$$

A pretrained and frozen segmentation model produces an automatic prediction:

$$\hat{Y} = f_\theta(V)$$

where $f_\theta$ is not updated during expert interaction.

---

## 3. Slice-Level Decomposition

The volume is decomposed into axial slices:

$$V = \{V_1, V_2, \dots, V_D\}$$

For each slice $i \in \{1,\dots,D\}$, we define the slice-wise predicted and ground truth masks:

$$\hat{Y}_i, \quad Y_i$$

All expert interactions occur at the **slice level**, not voxel or volume level.

---

## 4. Expert Effort as a Budgeted Resource

Expert effort is modeled as a **hard budget constraint** on the number of slices that can be reviewed and corrected. Let $\mathcal{B}$ denote the set of indices selected for review:

$$\mathcal{B} \subseteq \{1,\dots,D\}, \quad \text{subject to} \quad |\mathcal{B}| \le B$$

where $B$ is the maximum number of slices the expert is allowed to review. This formulation treats expert effort as a **finite, discrete resource**.

---

## 5. Correction Operator

Expert correction is modeled as a perfect replacement of the model prediction with ground truth on selected slices:

$$\tilde{Y}_i = \begin{cases} Y_i & \text{if } i \in \mathcal{B} \\ \hat{Y}_i & \text{otherwise} \end{cases}$$

The resulting corrected 3D segmentation volume is:

$$\tilde{Y}(\mathcal{B}) = \{\tilde{Y}_1, \tilde{Y}_2, \dots, \tilde{Y}_D\}$$

---

## 6. Optimization Objective

The goal is to select a subset of slices $\mathcal{B}$ that maximizes the final segmentation quality under the budget constraint:

$$\begin{aligned}
\max_{\mathcal{B}} \quad & \text{Dice}(\tilde{Y}(\mathcal{B}), Y) \\
\text{s.t.} \quad & |\mathcal{B}| \le B
\end{aligned}$$

Key properties:
- Optimization variables are **slice indices**, not model parameters.
- The segmentation model remains fixed.

---

## 7. Relationship to Prior Work

Existing interactive and uncertainty-guided segmentation methods typically identify uncertain regions and enable corrections, but they generally do **not**:

- Model expert effort as an explicit constrained resource.
- Formalize slice selection as a budgeted optimization problem.
- Decouple *where* to intervene from *how* corrections are applied.

---

## 8. Success Criteria for Phase 1

Phase 1 is successful if:
1. Segmentation is expressed as a **well-defined constrained optimization problem**.
2. Expert interaction is represented as a **decision variable**.
3. The formulation enables **fair, reproducible comparison** of selection strategies.

---

## 9. Scope and Assumptions

To ensure analytical clarity, we assume:
- Expert corrections are perfect.
- Corrections are applied independently per slice.
- Human factors (fatigue, time) are abstracted into the discrete slice budget $B$.
