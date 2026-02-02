"""
Generate Expert Correction Artifacts for All Patients

This script applies expert correction simulation to all patients
using Phase 6 IWUO selections.

SIMULATION ONLY - No evaluation, no metrics.

Usage:
    python simulation/generate_corrections.py --budget 10 --alpha 0.5
    python simulation/generate_corrections.py --budget 10 --alpha 0.5 --verify

Author: Research Prototype
Date: 2026-02-02
"""

import numpy as np
import argparse
from pathlib import Path
from typing import List, Dict
from simulation.expert_correction import apply_correction_for_patient


def get_patient_ids(predictions_dir: Path) -> List[str]:
    """Get list of patient IDs from predictions directory."""
    patient_ids = []
    for pred_file in sorted(predictions_dir.glob("*.npy")):
        patient_id = pred_file.stem
        patient_ids.append(patient_id)
    return patient_ids


def generate_corrections(
    predictions_dir: str = "predictions/predictions",
    ground_truth_dir: str = "data/processed",
    selection_dir: str = "algorithms/selection",
    output_dir: str = "simulation/corrected",
    verbose: bool = True
):
    """
    Generate expert correction artifacts for all patients.
    
    Args:
        predictions_dir: Directory containing Phase 3 predictions
        ground_truth_dir: Directory containing Phase 2 ground truth
        selection_dir: Directory containing Phase 6 selections
        output_dir: Directory to save corrected volumes
        verbose: Print progress
    """
    predictions_dir = Path(predictions_dir)
    ground_truth_dir = Path(ground_truth_dir)
    selection_dir = Path(selection_dir)
    output_dir = Path(output_dir)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get patient IDs
    patient_ids = get_patient_ids(predictions_dir)
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Expert Correction Generation")
        print(f"{'='*60}")
        print(f"Predictions directory: {predictions_dir}")
        print(f"Ground truth directory: {ground_truth_dir}")
        print(f"Selection directory: {selection_dir}")
        print(f"Output directory: {output_dir}")
        print(f"Total patients: {len(patient_ids)}")
        print(f"{'='*60}\n")
    
    # Generate corrections for each patient
    for i, patient_id in enumerate(patient_ids, 1):
        if verbose:
            print(f"\n[{i}/{len(patient_ids)}] Processing {patient_id}...")
        
        # Define paths
        predictions_path = predictions_dir / f"{patient_id}.npy"
        ground_truth_path = ground_truth_dir / f"{patient_id}.npy"
        selection_path = selection_dir / f"{patient_id}.npy"
        output_path = output_dir / f"{patient_id}.npy"
        
        # Verify files exist
        if not predictions_path.exists():
            print(f"   ⚠️  Skipping {patient_id}: predictions not found")
            continue
        
        if not ground_truth_path.exists():
            print(f"   ⚠️  Skipping {patient_id}: ground truth not found")
            continue
        
        if not selection_path.exists():
            print(f"   ⚠️  Skipping {patient_id}: selection not found")
            continue
        
        # Apply correction
        try:
            corrected_data = apply_correction_for_patient(
                predictions_path=str(predictions_path),
                ground_truth_path=str(ground_truth_path),
                selection_path=str(selection_path),
                verbose=False
            )
            
            # Save corrected volume
            np.save(output_path, corrected_data)
            
            if verbose:
                num_selected = len(corrected_data["selected_slices"])
                num_total = len(corrected_data["corrected_slices"])
                print(f"   ✅ Correction complete")
                print(f"      Selected: {num_selected}/{num_total} slices")
                print(f"      Saved to: {output_path}")
        
        except Exception as e:
            print(f"   ❌ Error processing {patient_id}: {e}")
            continue
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"✅ Expert correction generation complete!")
        print(f"   Output directory: {output_dir}")
        print(f"{'='*60}\n")


def verify_corrections(
    corrected_dir: str = "simulation/corrected",
    predictions_dir: str = "predictions/predictions",
    ground_truth_dir: str = "data/processed",
    selection_dir: str = "algorithms/selection"
):
    """
    Verify expert correction artifacts.
    
    Checks:
    1. All corrected files exist
    2. Corrected slices match selected slices (ground truth)
    3. Uncorrected slices match predictions
    4. Slice alignment is preserved
    
    Args:
        corrected_dir: Directory containing corrected volumes
        predictions_dir: Directory containing Phase 3 predictions
        ground_truth_dir: Directory containing Phase 2 ground truth
        selection_dir: Directory containing Phase 6 selections
    """
    corrected_dir = Path(corrected_dir)
    predictions_dir = Path(predictions_dir)
    ground_truth_dir = Path(ground_truth_dir)
    selection_dir = Path(selection_dir)
    
    print(f"\n{'='*60}")
    print(f"Verifying Expert Correction Artifacts")
    print(f"{'='*60}\n")
    
    # Get patient IDs
    patient_ids = get_patient_ids(predictions_dir)
    
    num_verified = 0
    num_errors = 0
    
    for patient_id in patient_ids:
        corrected_path = corrected_dir / f"{patient_id}.npy"
        predictions_path = predictions_dir / f"{patient_id}.npy"
        ground_truth_path = ground_truth_dir / f"{patient_id}.npy"
        selection_path = selection_dir / f"{patient_id}.npy"
        
        # Check if corrected file exists
        if not corrected_path.exists():
            print(f"❌ {patient_id}: corrected file not found")
            num_errors += 1
            continue
        
        try:
            # Load data
            corrected_data = np.load(corrected_path, allow_pickle=True).item()
            predictions_data = np.load(predictions_path, allow_pickle=True).item()
            ground_truth_data = np.load(ground_truth_path, allow_pickle=True).item()
            selection_data = np.load(selection_path, allow_pickle=True).item()
            
            # Verify structure
            assert "patient_id" in corrected_data
            assert "selected_slices" in corrected_data
            assert "corrected_slices" in corrected_data
            
            # Verify patient_id
            assert corrected_data["patient_id"] == patient_id
            
            # Verify selected_slices match
            assert corrected_data["selected_slices"] == selection_data["selected_slices"]
            
            # Verify number of slices
            num_corrected_slices = len(corrected_data["corrected_slices"])
            num_pred_slices = len(predictions_data["slices"])
            assert num_corrected_slices == num_pred_slices
            
            # Verify correction logic
            selected_slices = set(corrected_data["selected_slices"])
            
            for i, corrected_slice in enumerate(corrected_data["corrected_slices"]):
                slice_id = corrected_slice["slice_id"]
                corrected_mask = corrected_slice["mask"]
                
                pred_mask = predictions_data["slices"][i]["pred_mask"]
                gt_mask = ground_truth_data["slices"][i]["mask"]
                
                if slice_id in selected_slices:
                    # Should be ground truth
                    assert np.array_equal(corrected_mask, gt_mask), \
                        f"Corrected slice {slice_id} does not match ground truth"
                else:
                    # Should be prediction
                    assert np.array_equal(corrected_mask, pred_mask), \
                        f"Uncorrected slice {slice_id} does not match prediction"
            
            print(f"✅ {patient_id}: verified ({num_corrected_slices} slices, {len(selected_slices)} corrected)")
            num_verified += 1
        
        except Exception as e:
            print(f"❌ {patient_id}: verification failed - {e}")
            num_errors += 1
    
    print(f"\n{'='*60}")
    print(f"Verification Summary")
    print(f"{'='*60}")
    print(f"Total patients: {len(patient_ids)}")
    print(f"Verified: {num_verified}")
    print(f"Errors: {num_errors}")
    
    if num_errors == 0:
        print(f"\n✅ All corrections verified successfully!")
    else:
        print(f"\n⚠️  {num_errors} corrections failed verification")
    
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate expert correction artifacts for all patients"
    )
    parser.add_argument(
        "--predictions-dir",
        type=str,
        default="predictions/predictions",
        help="Directory containing Phase 3 predictions"
    )
    parser.add_argument(
        "--ground-truth-dir",
        type=str,
        default="data/processed",
        help="Directory containing Phase 2 ground truth"
    )
    parser.add_argument(
        "--selection-dir",
        type=str,
        default="algorithms/selection",
        help="Directory containing Phase 6 selections"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="simulation/corrected",
        help="Directory to save corrected volumes"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify corrections after generation"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify existing corrections (do not generate)"
    )
    
    args = parser.parse_args()
    
    if args.verify_only:
        # Only verify
        verify_corrections(
            corrected_dir=args.output_dir,
            predictions_dir=args.predictions_dir,
            ground_truth_dir=args.ground_truth_dir,
            selection_dir=args.selection_dir
        )
    else:
        # Generate corrections
        generate_corrections(
            predictions_dir=args.predictions_dir,
            ground_truth_dir=args.ground_truth_dir,
            selection_dir=args.selection_dir,
            output_dir=args.output_dir,
            verbose=True
        )
        
        # Verify if requested
        if args.verify:
            verify_corrections(
                corrected_dir=args.output_dir,
                predictions_dir=args.predictions_dir,
                ground_truth_dir=args.ground_truth_dir,
                selection_dir=args.selection_dir
            )


if __name__ == "__main__":
    main()
