# Phase 1 — Problem Formulation

Impact-Weighted Optimization for Expert-in-the-Loop Brain Tumor Segmentation

---

## 1. Motivation

Deep learning–based brain tumor segmentation models achieve strong average accuracy but remain unreliable in localized regions. In clinical workflows, these failures are typically corrected by human experts, whose time and attention constitute a scarce resource.

Most existing interactive segmentation systems focus on *how* experts provide corrections (e.g., clicks, scribbles, refinement loops), but do not explicitly model *where* expert effort should be allocated when only a limited fraction of the volume can be reviewed.

This project formulates expert-in-the-loop segmentation as a **budget-constrained decision problem**, where the goal is to optimally allocate limited expert corrections to maximize final segmentation quality.

---

## 2. Mathematical Formulation

### 2.1 Volume and Ground Truth

Let a 3D MRI volume and its corresponding ground-truth segmentation mask be defined as:

$$
V \in \mathbb{R}^{H \times W \times D}
$$

$$
Y \in \{0,1\}^{H \times W \times D}
$$

where:

- $H, W$ are the spatial dimensions (height and width)
- $D$ is the number of axial slices
- $Y$ represents the binary segmentation mask (tumor vs. background)

### 2.2 Frozen Segmentation Model

A pretrained and frozen segmentation model $f_\theta$ produces an automatic prediction:

$$
\hat{Y} = f_\theta(V) \in \{0,1\}^{H \times W \times D}
$$

**Critical assumption:** The model parameters $\theta$ are **fixed** throughout the expert-in-the-loop process. There is no retraining, fine-tuning, or active learning.

---

## 3. Axial Slice Decomposition

The volume is decomposed into $D$ axial slices:

$$
V = \{V_1, V_2, \dots, V_D\}, \quad V_i \in \mathbb{R}^{H \times W}
$$

For each slice $i \in \{1, 2, \dots, D\}$, we define the corresponding 2D predicted and ground-truth masks:

$$
\hat{Y}_i \in \{0,1\}^{H \times W}, \quad Y_i \in \{0,1\}^{H \times W}
$$

**Design decision:** All expert interactions occur at the **slice level**, not at the voxel or volume level. This reflects clinical practice where radiologists review images slice-by-slice.

---

## 4. Expert Effort as a Hard Budget

Expert effort is modeled as a **hard budget constraint** on the number of slices that can be reviewed and corrected.

Let $\mathcal{B} \subseteq \{1, 2, \dots, D\}$ denote the set of slice indices selected for expert review. The budget constraint is:

$$
|\mathcal{B}| \le B
$$

where $B \in \mathbb{Z}^+$ is the maximum number of slices the expert is allowed to review.

**Interpretation:**

- $B$ abstracts human factors (time, fatigue, attention) into a discrete, countable resource.
- Expert effort is treated as **finite and non-renewable** within a single case.
- The slice index is the fundamental decision unit.

---

## 5. Correction Operator

Expert correction is modeled as a **perfect replacement** of the model prediction with ground truth on selected slices:

$$
\tilde{Y}_i =
\begin{cases}
Y_i & \text{if } i \in \mathcal{B} \\
\hat{Y}_i & \text{otherwise}
\end{cases}
$$

The resulting corrected 3D segmentation volume is:

$$
\tilde{Y}(\mathcal{B}) = \{\tilde{Y}_1, \tilde{Y}_2, \dots, \tilde{Y}_D\}
$$

**Assumptions:**

- Expert corrections are **perfect** (no human error).
- Corrections are applied **independently** per slice (no inter-slice dependencies).
- Correction is **instantaneous** (no time modeling beyond slice count).

---

## 6. Optimization Objective

The goal is to select a subset of slices $\mathcal{B}$ that maximizes the final 3D segmentation quality under the budget constraint:

$$
\begin{aligned}
\max_{\mathcal{B}} \quad & \text{Dice}(\tilde{Y}(\mathcal{B}), Y) \\
\text{subject to} \quad & |\mathcal{B}| \le B \\
& \mathcal{B} \subseteq \{1, 2, \dots, D\}
\end{aligned}
$$

where $\text{Dice}(\cdot, \cdot)$ is the Sørensen–Dice coefficient computed over the entire 3D volume.

**Key properties:**

- The optimization variables are **slice indices**, not model parameters.
- The segmentation model $f_\theta$ remains **fixed**.
- The objective is **deterministic** given $V$, $Y$, and $\hat{Y}$.

---

## 7. Separation of Concerns

This formulation explicitly separates four distinct components:

| Component | Description | Scope |
| --- | --- | --- |
| **Prediction** | Generating $\hat{Y}$ from $V$ using $f_\theta$ | Model inference (frozen) |
| **Decision-making** | Selecting $\mathcal{B}$ under budget $B$ | Slice selection algorithm |
| **Correction** | Replacing $\hat{Y}_i$ with $Y_i$ for $i \in \mathcal{B}$ | Expert interaction (simulated) |
| **Evaluation** | Computing $\text{Dice}(\tilde{Y}(\mathcal{B}), Y)$ | Performance measurement |

**Implication:** Different slice selection strategies can be compared **independently** of the segmentation model architecture.

---

## 8. Relationship to Prior Work

Existing interactive and uncertainty-guided segmentation methods typically identify uncertain regions and enable corrections, but they generally do **not**:

1. **Model expert effort as an explicit constrained resource.**
   - Most methods assume unlimited expert availability or use heuristic stopping criteria.

2. **Formalize slice selection as a budgeted optimization problem.**
   - Uncertainty sampling is often greedy and does not optimize for final segmentation quality.

3. **Decouple *where* to intervene from *how* corrections are applied.**
   - Many methods conflate the selection strategy with the correction mechanism (e.g., click-based refinement).

4. **Separate prediction from decision-making.**
   - Active learning methods often retrain the model, mixing prediction and selection.

**This work:** Treats slice selection as a **standalone decision problem** with a well-defined objective and constraints, enabling rigorous comparison of selection strategies.

---

## 9. Success Criteria for Phase 1

Phase 1 is considered successful if:

1. ✅ Segmentation is expressed as a **well-defined constrained optimization problem**.
2. ✅ Expert interaction is represented as a **decision variable** ($\mathcal{B}$).
3. ✅ The formulation enables **fair, reproducible comparison** of selection strategies.
4. ✅ All assumptions are **explicitly stated** and justified.
5. ✅ The problem is **decoupled** from implementation details.

---

## 10. Scope and Assumptions

To ensure analytical clarity and reproducibility, we assume:

| Assumption | Justification |
| --- | --- |
| Expert corrections are **perfect** | Isolates the slice selection problem from human error modeling |
| Corrections are applied **independently per slice** | Simplifies the decision space; reflects 2D review workflows |
| Human factors are abstracted into **discrete slice budget $B$** | Avoids modeling fatigue, time, or attention explicitly |
| The segmentation model is **frozen** | Separates prediction from decision-making; no active learning |
| Only **axial slices** are considered | Matches clinical practice; simplifies implementation |
| Only **FLAIR modality** is used | Reduces data complexity; FLAIR is standard for tumor visualization |

**Exclusions (out of scope for this research prototype):**

- Model retraining or fine-tuning
- Multi-modal fusion
- User interface design
- Real-time interaction
- Clinical validation

---

## 11. Next Steps (Not Part of Phase 1)

Phase 1 establishes the **problem formulation**. Subsequent phases will:

- **Phase 2:** Load BraTS dataset and extract axial slices
- **Phase 3:** Implement baseline slice selection strategies
- **Phase 4:** Develop impact-weighted optimization
- **Phase 5:** Evaluate and compare strategies

**Phase 1 does not include:**

- Experiments
- Implementation details
- Dataset loading
- Model inference
- Uncertainty computation
- Optimization algorithms

---

## 12. Summary

This document formalizes expert-in-the-loop brain tumor segmentation as a **budget-constrained optimization problem** where:

- The segmentation model is **frozen**
- Expert interaction is **simulated and perfect**
- Expert effort is modeled **only as the number of axial slices corrected**
- Slice selection is a **decision problem**, separate from prediction

The formulation enables rigorous, reproducible comparison of slice selection strategies under a well-defined objective and constraints.
