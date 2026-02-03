# Phase 10 — Failure Analysis and Limitations

**Date:** 2026-02-03  
**Status:** Limitations Analysis of Research Prototype  

---

## Overview

This analysis systematically characterizes the limitations, failure modes, and validity boundaries of the Impact-Weighted Uncertainty Optimization (IWUO) framework. By explicitly identifying when and why the method underperforms, we define its precise research contribution and differentiate it from a clinically deployable product.

---

## 1. Failure Modes: Mechanistic Analysis

We identify four primary scenarios where IWUO may yield suboptimal slice selections compared to simpler heuristics or oracle selection.

### 1.1 High-Confidence Correctness Errors (The "Silent Failure")

- **Mechanism:** The model predicts a structure with high confidence (low uncertainty) but is factually incorrect (e.g., misclassifying a tumor sub-region or hallucinating tissue).
- **IWUO Behavior:** Since $U_i \approx 0$, the prioritization score $S_i = \alpha U_i + (1-\alpha) I_i$ is driven entirely by the impact term. If the predicted impact is also low (e.g., a false negative near the skull base), the slice receives a low score.
- **Result:** IWUO will likely ignore this slice, favoring slices with higher uncertainty, even if those are ultimately correct. This highlights IWUO's dependency on the correlation between uncertainty and error.

### 1.2 The "Noisy Edge" Trap

- **Mechanism:** A slice contains complex anatomical boundaries resulting in high epistemic uncertainty along edges, but the volumetric error (Dice delta) is negligible because the boundaries are substantially correct.
- **IWUO Behavior:** Such slices yield high $U_i$. Even with impact weighting, a sufficiently high $U_i$ can push the slice into the selection set.
- **Result:** The budget is spent "refining" 1-2 pixel boundaries that yield minimal Dice improvement, reducing overall efficiency compared to correcting gross anatomical errors. This is a failure of the linear combination proxy to perfectly capture Dice gain.

### 1.3 Volumetric Overshadowing

- **Mechanism:** A slice contains a massive tumor prediction (high impact potential) with moderate uncertainty.
- **IWUO Behavior:** The large impact term $(1-\alpha) I_i$ dominates the score.
- **Result:** IWUO prioritizes this slice. If the prediction is actually correct (True Positive), the correction yields zero gain ("wasted click"). While Phase 5 uses proxy impact, it cannot distinguish large TP from large FP/FN without ground truth. This is an inherent limitation of unsupervised selection.

### 1.4 Saturation Instability

- **Mechanism:** In high-budget regimes ($B > 30\%$), the pool of "obvious" high-priority slices is exhausted.
- **IWUO Behavior:** The algorithm begins selecting slices with marginal scores driven by noise in the uncertainty estimation or impact proxies.
- **Result:** Selection quality degrades to random-equivalent performance. This is not a failure of logic but a boundary condition: IWUO is designed for *constrained* selection, not exhaustive verification.

---

## 2. Assumptions and Consequences

The validity of our findings rests on several simplifying assumptions.

### 2.1 Perfect Expert Correction

- **Assumption:** The expert always provides the ground truth mask for a selected slice.
- **Consequence:** This establishes an *upper bound* on performance. In reality, experts suffer from fatigue, inter-rater variability, and localized errors.
- **Limitation:** IWUO assumes correction cost is uniform. If complex slices (high $U_i$) take longer to correct, the "efficiency" (Dice gain per minute) would be lower than observed in our simulation (Dice gain per slice).

### 2.2 Slice-Level Independence

- **Assumption:** Corrections on slice $i$ do not propagate information to slice $i+1$.
- **Consequence:** This ignores the 3D nature of volumetric segmentation. In a real tool, correcting one slice could propagate constraints to neighbors.
- **Limitation:** Our evaluation likely *underestimates* the potential benefit of expert interaction if propagation were enabled, but *overestimates* the necessity of correcting adjacent slices independently.

### 2.3 Linear Combination Proxy ($\alpha U + (1-\alpha)I$)

- **Assumption:** Usefulness is a linear combination of uncertainty and impact.
- **Consequence:** This is a heuristic approximation of $\mathbb{E}[\Delta \text{Dice}]$. It assumes calibration between the two signals.
- **Limitation:** The optimal relationship is likely non-linear and patient-specific. The expected gain from a highly uncertain small region might be exponentially different from a certain large region depending on the metric (Dice vs. Hausdorff).

### 2.4 Fixed $\alpha$ Across Cohort

- **Assumption:** A single weighting parameter ($\alpha=0.5$) works for all patients.
- **Consequence:** We ignore inter-patient variability. Some patients might have confident-but-wrong models (needing high $\alpha$), while others have erratic-but-safe predictions.
- **Limitation:** Performance is suboptimal for outlier patients who deviate from the population mean characteristics.

---

## 3. Sensitivity and Design Choices

While strict tuning was out of scope, the method's behavior is conceptually sensitive to several choices.

- **Sensitivity to $\alpha$:** The balance is critical. As $\alpha \to 1$, IWUO collapses to uncertainty sampling (prone to low-impact noise). As $\alpha \to 0$, it collapses to volume-weighted sampling (prone to false-positive dominance). The stability of $\alpha=0.5$ suggests the signals are somewhat complementary, but this is empirically derived, not theoretically guaranteed.
- **Uncertainty Estimator:** We used MC Dropout ($T=20$). Using Deep Ensembles or Evidential Deep Learning would likely yield different calibration properties, potentially altering the selection ranking significantly.
- **Impact Proxy:** We used predicted volume as a proxy for impact. This relies on the model *detecting* the object. It inherently undervalues "missed targets" (False Negatives where prediction volume $\approx 0$).

---

## 4. Clinical and Practical Limitations

### 4.1 "Human-in-the-Loop" Reality Gap

Our simulation treats the expert as a function call: `ApplyCorrection(Slice)`. In clinical practice, experts do not "select slices" from a list; they scroll through volumes.

- **Limitation:** The cognitive load of "context switching" to specific slices suggested by an algorithm is not modeled.
- **Scope Boundary:** IWUO is valid for *triage* or *QA* workflows (identifying slices for review) rather than real-time interactive segmentation drawing.

### 4.2 Time vs. Clicks

We measure budget in *slices*. Real budgets are measured in *time*.

- **Limitation:** Correcting a complex tumor boundary takes longer than rejecting a false positive. IWUO treats both "costs" as identical (1 slice).
- **Scope Boundary:** Our results apply to *slice-based* budgeting, not *time-based* budgeting.

### 4.3 Generalizability

We validated on BraTS (Brain Tumor).

- **Limitation:** Brain tumors are singular, connected large objects. In tasks with many small objects (e.g., metastasis detection or cell counting), the "Impact" term might dominate or behave differently. The method's utility for multi-class or small-object segmentation remains to be proven.

---

## 5. Scope of Validity

Based on the analysis, IWUO is valid and recommended under the following specific conditions:

1. **Low-Budget Regimes:** Budget is constrained to $\le 10-20\%$ of slices.
2. **QA / Review Workflows:** The goal is to maximize quality improvement given a fixed review capacity.
3. **Large-Structure Segmentation:** The objects of interest (e.g., tumors, organs) have significant volumetric impact, making Dice a suitable target metric.

IWUO is **NOT** recommended when:

- **Full Verification is Required:** If every slice must be checked, random sequential review is more cognitively natural.
- **High-Precision Boundary is Critical:** If 1-pixel errors matter (e.g., radiotherapy planning), Hausdorff-based or strictly uncertainty-based methods might be superior.

---

## 6. Relationship to Prior Work (Critical Positioning)

IWUO addresses a specific gap in the literature: **decision-making under constrained expert effort**.

- **Contrast with Uncertainty Estimation:** Most work focuses on *quantifying* uncertainty (calibration, visualization). IWUO focuses on *using* it for resource allocation.
- **Contrast with Active Learning (AL):** AL selects samples to *retrain* the model. IWUO selects samples to *correct* the specific instance (inference-time intervention). The goals are distinct (future performance vs. current performance).
- **Contrast with Interactive Segmentation:** Deep-IGeS and similar tools focus on *how* to correct (clicks, scribbles). IWUO focuses on *where* to correct.

IWUO contributes a **selection policy** for inference-time quality assurance, offering a pragmatically motivated heuristic for the "triage" problem in AI-assisted radiology.

---

**Last Updated:** 2026-02-03  
**Status:** Limitations Defined and Scope Bounded
