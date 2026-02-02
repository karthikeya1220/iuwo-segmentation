"""
Phase 5 — Generate Impact Artifacts

This script computes volumetric impact for all patients and saves impact artifacts.

IMPACT IS A SIGNAL, NOT A DECISION RULE.

This phase does NOT include:
- Slice selection
- Ranking for decision-making
- Budget constraints
- Optimization
- Uncertainty combination

Author: Research Prototype
Date: 2026-02-02
"""

import sys
import numpy as np
from pathlib import Path
import argparse

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from models.impact.compute_impact import compute_impact_for_patient


def generate_impact_for_dataset(
    predictions_dir: str,
    output_dir: str,
    use_connectivity: bool = True,
    use_sqrt_transform: bool = True,
    max_patients: int = None
) -> None:
    """
    Generate impact artifacts for all patients.
    
    Args:
        predictions_dir: Directory containing Phase 3 prediction .npy files
        output_dir: Directory to save impact .npy files
        use_connectivity: Weight impact by 3D connectivity
        use_sqrt_transform: Apply sqrt stabilization
        max_patients: Maximum number of patients to process (optional)
    """
    predictions_path = Path(predictions_dir)
    output_path = Path(output_dir)
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all Phase 3 prediction files
    prediction_files = sorted(predictions_path.glob("*.npy"))
    
    if len(prediction_files) == 0:
        print(f"❌ No .npy files found in: {predictions_dir}")
        return
    
    # Limit number of patients if specified
    if max_patients is not None:
        prediction_files = prediction_files[:max_patients]
    
    print(f"\n{'='*60}")
    print(f"Phase 5 — Generate Volumetric Impact")
    print(f"{'='*60}")
    print(f"Predictions directory: {predictions_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Patients to process: {len(prediction_files)}")
    print(f"Connectivity weighting: {use_connectivity}")
    print(f"Sqrt stabilization: {use_sqrt_transform}")
    print(f"{'='*60}\n")
    
    # Process each patient
    for i, prediction_file in enumerate(prediction_files):
        print(f"\n[{i+1}/{len(prediction_files)}] Processing: {prediction_file.name}")
        
        # Compute impact
        impact_data = compute_impact_for_patient(
            predictions_path=str(prediction_file),
            use_connectivity=use_connectivity,
            use_sqrt_transform=use_sqrt_transform,
            verbose=True
        )
        
        # Save impact
        patient_id = impact_data["patient_id"]
        output_file = output_path / f"{patient_id}.npy"
        np.save(output_file, impact_data, allow_pickle=True)
        
        print(f"   💾 Saved to: {output_file.name}")
    
    print(f"\n{'='*60}")
    print(f"✅ Impact generation complete!")
    print(f"   Processed: {len(prediction_files)} patients")
    print(f"   Output directory: {output_dir}")
    print(f"{'='*60}\n")


def verify_impact(
    impact_dir: str,
    predictions_dir: str
) -> None:
    """
    Verify impact alignment with Phase 3 predictions.
    
    Args:
        impact_dir: Directory containing impact .npy files
        predictions_dir: Directory containing Phase 3 prediction .npy files
    """
    impact_path = Path(impact_dir)
    predictions_path = Path(predictions_dir)
    
    impact_files = sorted(impact_path.glob("*.npy"))
    
    if len(impact_files) == 0:
        print(f"❌ No impact files found in: {impact_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"Verifying Impact Artifacts")
    print(f"{'='*60}\n")
    
    for impact_file in impact_files:
        patient_id = impact_file.stem
        predictions_file = predictions_path / f"{patient_id}.npy"
        
        if not predictions_file.exists():
            print(f"⚠️  Predictions file not found for: {patient_id}")
            continue
        
        # Load data
        impact_data = np.load(impact_file, allow_pickle=True).item()
        predictions_data = np.load(predictions_file, allow_pickle=True).item()
        
        # Verify structure
        assert "patient_id" in impact_data, "Missing patient_id"
        assert "slices" in impact_data, "Missing slices"
        assert impact_data["patient_id"] == patient_id, "Patient ID mismatch"
        
        # Verify slice alignment
        impact_slices = impact_data["slices"]
        prediction_slices = predictions_data["slices"]
        
        assert len(impact_slices) == len(prediction_slices), \
            f"Slice count mismatch: {len(impact_slices)} vs {len(prediction_slices)}"
        
        # Verify each slice
        for impact_slice, pred_slice in zip(impact_slices, prediction_slices):
            assert impact_slice["slice_id"] == pred_slice["slice_id"], \
                "Slice ID mismatch"
            
            assert "impact_score" in impact_slice, "Missing impact_score"
            
            impact_score = impact_slice["impact_score"]
            
            # Verify type and range
            assert isinstance(impact_score, (float, np.floating)), \
                f"impact_score must be scalar, got {type(impact_score)}"
            assert 0 <= impact_score <= 1, \
                f"impact_score out of range: {impact_score}"
        
        # Compute statistics
        impact_scores = [s["impact_score"] for s in impact_slices]
        print(f"✅ {patient_id}: {len(impact_slices)} slices")
        print(f"   Mean impact: {np.mean(impact_scores):.4f}")
        print(f"   Std impact: {np.std(impact_scores):.4f}")
        print(f"   Max impact: {np.max(impact_scores):.4f}")
    
    print(f"\n{'='*60}")
    print(f"✅ All impact artifacts verified successfully!")
    print(f"{'='*60}\n")


def main():
    """
    Command-line interface for impact generation.
    
    Usage:
        python generate_impact.py --predictions_dir ./predictions --output_dir ./impact
        python generate_impact.py --verify --impact_dir ./impact --predictions_dir ./predictions
    """
    parser = argparse.ArgumentParser(
        description="Phase 5 — Generate Volumetric Impact"
    )
    
    parser.add_argument(
        "--predictions_dir",
        type=str,
        default="./predictions",
        help="Directory containing Phase 3 prediction .npy files"
    )
    
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./impact",
        help="Directory to save impact .npy files"
    )
    
    parser.add_argument(
        "--use_connectivity",
        action="store_true",
        default=True,
        help="Weight impact by 3D connectivity"
    )
    
    parser.add_argument(
        "--no_connectivity",
        action="store_false",
        dest="use_connectivity",
        help="Disable connectivity weighting"
    )
    
    parser.add_argument(
        "--use_sqrt_transform",
        action="store_true",
        default=True,
        help="Apply sqrt stabilization to impact scores"
    )
    
    parser.add_argument(
        "--no_sqrt_transform",
        action="store_false",
        dest="use_sqrt_transform",
        help="Disable sqrt stabilization"
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
        help="Verify impact artifacts instead of generating"
    )
    
    parser.add_argument(
        "--impact_dir",
        type=str,
        default="./impact",
        help="Directory containing impact artifacts for verification"
    )
    
    args = parser.parse_args()
    
    if args.verify:
        # Verification mode
        verify_impact(
            impact_dir=args.impact_dir,
            predictions_dir=args.predictions_dir
        )
    else:
        # Generation mode
        generate_impact_for_dataset(
            predictions_dir=args.predictions_dir,
            output_dir=args.output_dir,
            use_connectivity=args.use_connectivity,
            use_sqrt_transform=args.use_sqrt_transform,
            max_patients=args.max_patients
        )


if __name__ == "__main__":
    main()
