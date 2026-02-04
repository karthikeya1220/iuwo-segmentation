# IUWO Prototype CURRENT Baseline Summary

Based on my analysis of your project documentation, here is the factual baseline of your system:

## Dataset Size

* 2 patients from BraTS 2024 Glioma dataset (proof-of-concept)
* FLAIR modality only
* ~300 total axial slices across both patients
* Ground truth segmentation masks used for validation
* No train/test split (both patients used for demonstration)

## Strategies Compared

Six strategies evaluated across the same dataset:

* **No Correction**: baseline - no expert intervention
* **Random Selection**: random slice selection
* **Uniform Selection**: evenly distributed slices
* **Uncertainty-Only**: MC Dropout entropy-based ranking
* **Impact-Only**: volumetric impact proxy ranking
* **IWUO**: proposed method: α·Uncertainty + (1-α)·Impact

## Evaluation Metric

* **Primary metric**: Dice coefficient vs. annotation budget
* **Budget points tested**: 5%, 10%, 20%, 30%, 50% of total slices
* **Comparison method**: Relative performance curves (Dice improvement per unit expert effort)
* **Simulation**: Perfect expert correction (ground truth replacement on selected slices)

## Known Assumptions

* Segmentation model is frozen (nnU-Net v2, pretrained/default weights, inference-only)
* Expert corrections are simulated as perfect (upper-bound analysis)
* Expert effort modeled as hard budget on number of axial slices
* Slice independence: Corrections do not propagate between slices
* CPU-only execution (no GPU training or fine-tuning)
* Single modality (FLAIR only, not multi-modal fusion)

## Known Limitations

* **Dataset size**: 2 patients insufficient for statistical significance testing
* **Simulation vs. reality**: Expert corrections are perfect; real experts have variability and fatigue
* **No retraining**: Model weights never updated (not active learning)
* **Platform constraint**: macOS CPU-only PyTorch (no CUDA support)
* **No clinical validation**: Simulated workflow, not tested with real radiologists
* **Modality specificity**: FLAIR-only, not validated on T1/T2/T1ce
* **No GUI**: Command-line pipeline only, no interactive annotation interface
* **Generalization**: Not tested on other anatomies or imaging tasks
