#!/bin/bash
set -e
set -x

# ==============================================================================
# FINALIZED PIPELINE: INFERENCE-ONLY nnU-Net v2 BACKBONE
# ==============================================================================
# Objective: Run the Expert-in-the-Loop simulation using nnU-Net v2 inference.
# Note: No training is performed. nnU-Net v2 will use default initialization
#       for inference, which is sufficient to validate pipeline mechanics.
# ==============================================================================

# 1. FORCE CPU EXECUTION (Resolve CUDA/MPS Conflicts)
export CUDA_VISIBLE_DEVICES=""
export CUDA_DEVICE_ORDER="PCI_BUS_ID"

# 2. SETUP ENVIRONMENT (Absolute Paths)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT_DIR:$PYTHONPATH"

export nnUNet_raw="$ROOT_DIR/nnunet_env/nnUNet_raw"
export nnUNet_preprocessed="$ROOT_DIR/nnunet_env/nnUNet_preprocessed"
export nnUNet_results="$ROOT_DIR/nnunet_env/nnUNet_results"

mkdir -p "$nnUNet_raw" "$nnUNet_preprocessed" "$nnUNet_results"

echo "=================================================="
echo "PHASE 1: DATA PREPARATION & PLANNING"
echo "=================================================="

echo "[1.1] Extracting Subset from BraTS Archive..."
cd "$ROOT_DIR"
python scripts/prepare_nnunet_dataset.py

echo "[1.2] Planning & Preprocessing (dataset integrity verification)..."
# Dataset ID 1 -> 'Dataset001_BraTS'
nnUNetv2_plan_and_preprocess -d 1 --verify_dataset_integrity

echo "=================================================="
echo "PHASE 2: INFERENCE PIPELINE"
echo "=================================================="

echo "[2.1] Adapter: Preparing Inference Input..."
# Converts Phase 2 slices (Validation Set) to nnU-Net NIfTI format
python scripts/slices_to_nnunet_volume.py \
    --input_dir data/processed \
    --output_dir nnunet_input/imagesTs

echo "[2.2] Executing nnU-Net v2 Prediction (CPU, default weights)..."
mkdir -p nnunet_output
# Note: nnU-Net v2 will initialize the model automatically during prediction
# We use fold 'all' to avoid needing a specific checkpoint
nnUNetv2_predict \
    -i nnunet_input/imagesTs \
    -o nnunet_output \
    -d 1 \
    -c 3d_fullres \
    -f all \
    --disable_tta \
    -device cpu

echo "[2.3] Adapter: Converting Predictions back to Slices..."
mkdir -p predictions/predictions
python scripts/nnunet_volume_to_slices.py \
    --input_dir nnunet_output \
    --output_dir predictions/predictions

echo "=================================================="
echo "PHASE 3: DOWNSTREAM SIMULATION (UNCHANGED)"
echo "=================================================="

echo "[3.1] Generating Uncertainty Map..."
# Using Bayesian dropout approximation (fast)
python models/uncertainty/generate_uncertainty.py \
    --phase2_dir data/processed \
    --output_dir models/uncertainty/artifacts \
    --num_samples 5 \
    --device cpu

echo "[3.2] Estimating Impact Scores (IWUO)..."
python models/impact/generate_impact.py \
    --predictions_dir predictions/predictions \
    --output_dir models/impact/artifacts

echo "[3.3] Running Evaluation & Plotting..."
python evaluation/evaluate_strategies.py \
    --predictions_dir predictions/predictions \
    --ground_truth_dir data/processed \
    --uncertainty_dir models/uncertainty/artifacts \
    --impact_dir models/impact/artifacts \
    --output_file evaluation/results_frozen.npy

python evaluation/plots.py \
    --results_file evaluation/results_frozen.npy \
    --output_file evaluation/dice_vs_budget_frozen.png

echo "=================================================="
echo "✅ PIPELINE FINALIZATION COMPLETE."
echo "   Artifacts generated in: evaluation/"
echo "=================================================="