"""
Phase 3.2 — Generate Slice-Aligned Predictions

This script runs the frozen segmentation model on Phase 2 data
and produces slice-aligned predictions in the required format.

INFERENCE ONLY - No training, no gradient computation.

Design Constraints:
- Slice IDs must match Phase 2 exactly
- Spatial alignment must be preserved
- No aggregation across slices
- No post-processing beyond thresholding

Author: Research Prototype
Date: 2026-02-02
"""

import sys
import numpy as np
from pathlib import Path
from typing import Dict, List
import argparse

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from models.backbone.frozen_model import load_frozen_model


def generate_predictions_for_patient(
    patient_data_path: str,
    model,
    threshold: float = 0.5,
    verbose: bool = True
) -> Dict:
    """
    Generate predictions for a single patient.
    
    Args:
        patient_data_path: Path to Phase 2 patient .npy file
        model: Frozen segmentation model
        threshold: Threshold for binary masks
        verbose: Print progress
        
    Returns:
        Dictionary with patient_id and slice predictions
        
    Format:
        {
          "patient_id": str,
          "slices": [
            {
              "slice_id": int,
              "prob_map": np.ndarray (H, W), float32, [0,1]
              "pred_mask": np.ndarray (H, W), uint8
            },
            ...
          ]
        }
    """
    # Load Phase 2 data
    patient_data = np.load(patient_data_path, allow_pickle=True).item()
    patient_id = patient_data["patient_id"]
    phase2_slices = patient_data["slices"]
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Processing patient: {patient_id}")
        print(f"Number of slices: {len(phase2_slices)}")
        print(f"{'='*60}")
    
    # Generate predictions for each slice
    prediction_slices = []
    
    for slice_data in phase2_slices:
        slice_id = slice_data["slice_id"]
        image = slice_data["image"]  # (H, W), float32
        
        # CRITICAL: Preserve slice_id alignment with Phase 2
        assert isinstance(slice_id, (int, np.integer)), \
            f"slice_id must be int, got {type(slice_id)}"
        
        # Run inference (INFERENCE ONLY - no gradients)
        prob_map, pred_mask = model.predict_slice(image, threshold=threshold)
        
        # Verify spatial alignment
        assert prob_map.shape == image.shape, \
            f"Spatial alignment error: {prob_map.shape} vs {image.shape}"
        assert pred_mask.shape == image.shape, \
            f"Spatial alignment error: {pred_mask.shape} vs {image.shape}"
        
        # Store prediction
        prediction_slice = {
            "slice_id": int(slice_id),  # Ensure int type
            "prob_map": prob_map.astype(np.float32),
            "pred_mask": pred_mask.astype(np.uint8)
        }
        
        prediction_slices.append(prediction_slice)
        
        if verbose and (slice_id % 20 == 0 or slice_id == len(phase2_slices) - 1):
            print(f"   Processed slice {slice_id + 1}/{len(phase2_slices)}")
    
    # Verify slice_id alignment
    phase2_slice_ids = [s["slice_id"] for s in phase2_slices]
    pred_slice_ids = [s["slice_id"] for s in prediction_slices]
    assert phase2_slice_ids == pred_slice_ids, \
        "Slice ID mismatch between Phase 2 and predictions"
    
    if verbose:
        print(f"✅ Predictions generated for {patient_id}")
        print(f"   Slices: {len(prediction_slices)}")
        print(f"   Slice IDs: [{pred_slice_ids[0]}, ..., {pred_slice_ids[-1]}]")
    
    return {
        "patient_id": patient_id,
        "slices": prediction_slices
    }


def generate_predictions_for_dataset(
    phase2_data_dir: str,
    output_dir: str,
    model_path: str = None,
    device: str = "cpu",
    threshold: float = 0.5,
    max_patients: int = None
) -> None:
    """
    Generate predictions for all patients in Phase 2 dataset.
    
    Args:
        phase2_data_dir: Directory containing Phase 2 .npy files
        output_dir: Directory to save prediction .npy files
        model_path: Path to pretrained model (optional)
        device: Device for inference ('cpu' or 'cuda')
        threshold: Threshold for binary masks
        max_patients: Maximum number of patients to process (optional)
    """
    phase2_path = Path(phase2_data_dir)
    output_path = Path(output_dir)
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all Phase 2 patient files
    patient_files = sorted(phase2_path.glob("*.npy"))
    
    if len(patient_files) == 0:
        print(f"❌ No .npy files found in: {phase2_data_dir}")
        return
    
    # Limit number of patients if specified
    if max_patients is not None:
        patient_files = patient_files[:max_patients]
    
    print(f"\n{'='*60}")
    print(f"Phase 3.2 — Generate Slice-Aligned Predictions")
    print(f"{'='*60}")
    print(f"Phase 2 data directory: {phase2_data_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Patients to process: {len(patient_files)}")
    print(f"Device: {device}")
    print(f"Threshold: {threshold}")
    print(f"{'='*60}\n")
    
    # Load frozen model (INFERENCE ONLY)
    print("Loading frozen segmentation model...")
    model = load_frozen_model(model_path=model_path, device=device)
    print()
    
    # Process each patient
    for i, patient_file in enumerate(patient_files):
        print(f"\n[{i+1}/{len(patient_files)}] Processing: {patient_file.name}")
        
        # Generate predictions
        predictions = generate_predictions_for_patient(
            patient_data_path=str(patient_file),
            model=model,
            threshold=threshold,
            verbose=True
        )
        
        # Save predictions
        patient_id = predictions["patient_id"]
        output_file = output_path / f"{patient_id}.npy"
        np.save(output_file, predictions, allow_pickle=True)
        
        print(f"   💾 Saved to: {output_file.name}")
    
    print(f"\n{'='*60}")
    print(f"✅ Prediction generation complete!")
    print(f"   Processed: {len(patient_files)} patients")
    print(f"   Output directory: {output_dir}")
    print(f"{'='*60}\n")


def verify_predictions(
    predictions_dir: str,
    phase2_data_dir: str
) -> None:
    """
    Verify prediction alignment with Phase 2 data.
    
    Args:
        predictions_dir: Directory containing prediction .npy files
        phase2_data_dir: Directory containing Phase 2 .npy files
    """
    pred_path = Path(predictions_dir)
    phase2_path = Path(phase2_data_dir)
    
    pred_files = sorted(pred_path.glob("*.npy"))
    
    if len(pred_files) == 0:
        print(f"❌ No prediction files found in: {predictions_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"Verifying Predictions")
    print(f"{'='*60}\n")
    
    for pred_file in pred_files:
        patient_id = pred_file.stem
        phase2_file = phase2_path / f"{patient_id}.npy"
        
        if not phase2_file.exists():
            print(f"⚠️  Phase 2 file not found for: {patient_id}")
            continue
        
        # Load data
        predictions = np.load(pred_file, allow_pickle=True).item()
        phase2_data = np.load(phase2_file, allow_pickle=True).item()
        
        # Verify structure
        assert "patient_id" in predictions, "Missing patient_id"
        assert "slices" in predictions, "Missing slices"
        assert predictions["patient_id"] == patient_id, "Patient ID mismatch"
        
        # Verify slice alignment
        pred_slices = predictions["slices"]
        phase2_slices = phase2_data["slices"]
        
        assert len(pred_slices) == len(phase2_slices), \
            f"Slice count mismatch: {len(pred_slices)} vs {len(phase2_slices)}"
        
        # Verify each slice
        for pred_slice, phase2_slice in zip(pred_slices, phase2_slices):
            assert pred_slice["slice_id"] == phase2_slice["slice_id"], \
                "Slice ID mismatch"
            
            assert "prob_map" in pred_slice, "Missing prob_map"
            assert "pred_mask" in pred_slice, "Missing pred_mask"
            
            prob_map = pred_slice["prob_map"]
            pred_mask = pred_slice["pred_mask"]
            image = phase2_slice["image"]
            
            # Verify shapes
            assert prob_map.shape == image.shape, "Shape mismatch: prob_map"
            assert pred_mask.shape == image.shape, "Shape mismatch: pred_mask"
            
            # Verify dtypes
            assert prob_map.dtype == np.float32, f"Wrong dtype: {prob_map.dtype}"
            assert pred_mask.dtype == np.uint8, f"Wrong dtype: {pred_mask.dtype}"
            
            # Verify ranges
            assert 0 <= prob_map.min() <= prob_map.max() <= 1, \
                f"prob_map out of range: [{prob_map.min()}, {prob_map.max()}]"
            assert set(np.unique(pred_mask)).issubset({0, 1}), \
                f"pred_mask has invalid values: {np.unique(pred_mask)}"
        
        print(f"✅ {patient_id}: {len(pred_slices)} slices verified")
    
    print(f"\n{'='*60}")
    print(f"✅ All predictions verified successfully!")
    print(f"{'='*60}\n")


def main():
    """
    Command-line interface for prediction generation.
    
    Usage:
        python generate_predictions.py --phase2_dir ./processed --output_dir ./predictions
        python generate_predictions.py --verify --predictions_dir ./predictions --phase2_dir ./processed
    """
    parser = argparse.ArgumentParser(
        description="Phase 3.2 — Generate Slice-Aligned Predictions"
    )
    
    parser.add_argument(
        "--phase2_dir",
        type=str,
        default="./processed",
        help="Directory containing Phase 2 .npy files"
    )
    
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./predictions",
        help="Directory to save prediction .npy files"
    )
    
    parser.add_argument(
        "--model_path",
        type=str,
        default=None,
        help="Path to pretrained model checkpoint (optional)"
    )
    
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=["cpu", "cuda"],
        help="Device for inference"
    )
    
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Threshold for binary masks"
    )
    
    parser.add_argument(
        "--max_patients",
        type=int,
        default=None,
        help="Maximum number of patients to process"
    )
    
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify predictions instead of generating"
    )
    
    parser.add_argument(
        "--predictions_dir",
        type=str,
        default="./predictions",
        help="Directory containing predictions for verification"
    )
    
    args = parser.parse_args()
    
    if args.verify:
        # Verification mode
        verify_predictions(
            predictions_dir=args.predictions_dir,
            phase2_data_dir=args.phase2_dir
        )
    else:
        # Generation mode
        generate_predictions_for_dataset(
            phase2_data_dir=args.phase2_dir,
            output_dir=args.output_dir,
            model_path=args.model_path,
            device=args.device,
            threshold=args.threshold,
            max_patients=args.max_patients
        )


if __name__ == "__main__":
    main()
