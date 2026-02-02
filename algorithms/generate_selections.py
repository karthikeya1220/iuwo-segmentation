"""
Phase 6 — Generate IWUO Selection Artifacts

This script generates slice selections using IWUO for all patients.

DECISION-MAKING ONLY - No evaluation, no correction simulation.

Author: Research Prototype
Date: 2026-02-02
"""

import sys
import numpy as np
from pathlib import Path
import argparse

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from algorithms.iwuo import select_slices_for_patient


def generate_selections_for_dataset(
    uncertainty_dir: str,
    impact_dir: str,
    output_dir: str,
    budget: int,
    alpha: float = 0.5,
    max_patients: int = None
) -> None:
    """
    Generate IWUO selections for all patients.
    
    Args:
        uncertainty_dir: Directory containing Phase 4 uncertainty .npy files
        impact_dir: Directory containing Phase 5 impact .npy files
        output_dir: Directory to save selection .npy files
        budget: Maximum number of slices to select per patient
        alpha: Weighting parameter (default: 0.5)
        max_patients: Maximum number of patients to process (optional)
    """
    uncertainty_path = Path(uncertainty_dir)
    impact_path = Path(impact_dir)
    output_path = Path(output_dir)
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all uncertainty files
    uncertainty_files = sorted(uncertainty_path.glob("*.npy"))
    
    if len(uncertainty_files) == 0:
        print(f"❌ No .npy files found in: {uncertainty_dir}")
        return
    
    # Limit number of patients if specified
    if max_patients is not None:
        uncertainty_files = uncertainty_files[:max_patients]
    
    print(f"\n{'='*60}")
    print(f"Phase 6 — Generate IWUO Selections")
    print(f"{'='*60}")
    print(f"Uncertainty directory: {uncertainty_dir}")
    print(f"Impact directory: {impact_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Patients to process: {len(uncertainty_files)}")
    print(f"Budget: {budget}")
    print(f"Alpha: {alpha}")
    print(f"{'='*60}\n")
    
    # Process each patient
    for i, uncertainty_file in enumerate(uncertainty_files):
        patient_id = uncertainty_file.stem
        impact_file = impact_path / f"{patient_id}.npy"
        
        if not impact_file.exists():
            print(f"⚠️  Impact file not found for: {patient_id}")
            continue
        
        print(f"\n[{i+1}/{len(uncertainty_files)}] Processing: {patient_id}")
        
        # Generate selection
        selection_data = select_slices_for_patient(
            uncertainty_path=str(uncertainty_file),
            impact_path=str(impact_file),
            budget=budget,
            alpha=alpha,
            verbose=True
        )
        
        # Save selection
        output_file = output_path / f"{patient_id}.npy"
        np.save(output_file, selection_data, allow_pickle=True)
        
        print(f"   💾 Saved to: {output_file.name}")
    
    print(f"\n{'='*60}")
    print(f"✅ Selection generation complete!")
    print(f"   Processed: {len(uncertainty_files)} patients")
    print(f"   Output directory: {output_dir}")
    print(f"{'='*60}\n")


def verify_selections(
    selection_dir: str,
    uncertainty_dir: str,
    impact_dir: str
) -> None:
    """
    Verify selection artifacts.
    
    Args:
        selection_dir: Directory containing selection .npy files
        uncertainty_dir: Directory containing Phase 4 uncertainty .npy files
        impact_dir: Directory containing Phase 5 impact .npy files
    """
    selection_path = Path(selection_dir)
    uncertainty_path = Path(uncertainty_dir)
    impact_path = Path(impact_dir)
    
    selection_files = sorted(selection_path.glob("*.npy"))
    
    if len(selection_files) == 0:
        print(f"❌ No selection files found in: {selection_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"Verifying IWUO Selection Artifacts")
    print(f"{'='*60}\n")
    
    for selection_file in selection_files:
        patient_id = selection_file.stem
        uncertainty_file = uncertainty_path / f"{patient_id}.npy"
        impact_file = impact_path / f"{patient_id}.npy"
        
        if not uncertainty_file.exists() or not impact_file.exists():
            print(f"⚠️  Missing uncertainty or impact file for: {patient_id}")
            continue
        
        # Load data
        selection_data = np.load(selection_file, allow_pickle=True).item()
        uncertainty_data = np.load(uncertainty_file, allow_pickle=True).item()
        impact_data = np.load(impact_file, allow_pickle=True).item()
        
        # Verify structure
        assert "patient_id" in selection_data, "Missing patient_id"
        assert "budget" in selection_data, "Missing budget"
        assert "alpha" in selection_data, "Missing alpha"
        assert "selected_slices" in selection_data, "Missing selected_slices"
        
        assert selection_data["patient_id"] == patient_id, "Patient ID mismatch"
        
        # Verify selection
        selected_slices = selection_data["selected_slices"]
        budget = selection_data["budget"]
        alpha = selection_data["alpha"]
        
        # Verify budget constraint
        assert len(selected_slices) <= budget, \
            f"Selection exceeds budget: {len(selected_slices)} > {budget}"
        
        # Verify alpha range
        assert 0.0 <= alpha <= 1.0, f"Alpha out of range: {alpha}"
        
        # Verify selected slices are valid
        all_slice_ids = [s["slice_id"] for s in uncertainty_data["slices"]]
        for slice_id in selected_slices:
            assert slice_id in all_slice_ids, \
                f"Invalid slice_id: {slice_id}"
        
        # Verify no duplicates
        assert len(selected_slices) == len(set(selected_slices)), \
            "Duplicate slice_ids in selection"
        
        print(f"✅ {patient_id}:")
        print(f"   Budget: {budget}")
        print(f"   Alpha: {alpha:.2f}")
        print(f"   Selected: {len(selected_slices)} slices")
        print(f"   Slice IDs: {sorted(selected_slices)[:10]}{'...' if len(selected_slices) > 10 else ''}")
    
    print(f"\n{'='*60}")
    print(f"✅ All selection artifacts verified successfully!")
    print(f"{'='*60}\n")


def main():
    """
    Command-line interface for IWUO selection generation.
    
    Usage:
        python generate_selections.py --uncertainty_dir ./uncertainty --impact_dir ./impact --output_dir ./selections --budget 10
        python generate_selections.py --verify --selection_dir ./selections --uncertainty_dir ./uncertainty --impact_dir ./impact
    """
    parser = argparse.ArgumentParser(
        description="Phase 6 — Generate IWUO Selections"
    )
    
    parser.add_argument(
        "--uncertainty_dir",
        type=str,
        default="./uncertainty",
        help="Directory containing Phase 4 uncertainty .npy files"
    )
    
    parser.add_argument(
        "--impact_dir",
        type=str,
        default="./impact",
        help="Directory containing Phase 5 impact .npy files"
    )
    
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./selections",
        help="Directory to save selection .npy files"
    )
    
    parser.add_argument(
        "--budget",
        type=int,
        default=10,
        help="Maximum number of slices to select per patient"
    )
    
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.5,
        help="Weighting parameter (0=impact-only, 0.5=equal, 1=uncertainty-only)"
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
        help="Verify selection artifacts instead of generating"
    )
    
    parser.add_argument(
        "--selection_dir",
        type=str,
        default="./selections",
        help="Directory containing selection artifacts for verification"
    )
    
    args = parser.parse_args()
    
    if args.verify:
        # Verification mode
        verify_selections(
            selection_dir=args.selection_dir,
            uncertainty_dir=args.uncertainty_dir,
            impact_dir=args.impact_dir
        )
    else:
        # Generation mode
        generate_selections_for_dataset(
            uncertainty_dir=args.uncertainty_dir,
            impact_dir=args.impact_dir,
            output_dir=args.output_dir,
            budget=args.budget,
            alpha=args.alpha,
            max_patients=args.max_patients
        )


if __name__ == "__main__":
    main()
