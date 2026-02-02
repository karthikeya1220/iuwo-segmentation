# Project Rules and Guardrails

These rules are non-negotiable. Any implementation or modification that violates them invalidates the research premise.

## 1. Segmentation Model Rules

- The segmentation model MUST be pretrained and frozen.
- No retraining, fine-tuning, or online updates are allowed.
- No gradients, loss backpropagation, or learning loops.

## 2. Interaction Rules

- Expert interaction is simulated, not human-in-the-loop.
- Corrections are assumed to be perfect replacements.
- Interaction occurs ONLY at the slice level.
- No clicks, scribbles, bounding boxes, or UI abstractions.

## 3. Budget Rules

- Expert effort is modeled ONLY as the number of axial slices corrected.
- The budget is a hard constraint (|ℬ| ≤ B).
- Time, fatigue, or cognitive load are not modeled.

## 4. Scope Control Rules

- Do NOT introduce uncertainty-aware training losses.
- Do NOT introduce active learning, self-training, or pseudo-labeling.
- Do NOT mix training and evaluation data.
- Do NOT remove empty slices during preprocessing.

## 5. Evaluation Rules

- All slice selection strategies must be evaluated under identical budgets.
- Corrections must be applied using the same correction operator.
- Dice score is the primary evaluation metric.
- No qualitative claims without quantitative backing.

## 6. Reproducibility Rules

- All randomness must be controlled or eliminated.
- Slice indices must be stable and reproducible.
- Dataset preprocessing must be deterministic.
- Results must be reproducible from saved artifacts.

## 7. Research Integrity Rules

- Prediction quality and decision quality must remain separated.
- Improvements must be attributable to slice selection, not model changes.
- All assumptions must be stated explicitly.
- All limitations must be acknowledged in failure analysis.

Violation of any rule must be treated as a bug, not a design choice.
