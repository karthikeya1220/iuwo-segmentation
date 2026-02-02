"""
Phase 4 — Generate Uncertainty Artifacts

This script computes epistemic uncertainty for all patients using
Monte Carlo Dropout and saves uncertainty artifacts.

UNCERTAINTY IS A SIGNAL, NOT A DECISION RULE.

This phase does NOT include:
- Slice selection
- Budget constraints
- Optimization
- Impact estimation

Author: Research Prototype
Date: 2026-02-02
"""

import sys
import numpy as np
from pathlib import Path
import argparse

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from models.backbone.frozen_model import load_frozen_model
from models.uncertainty.compute_uncertainty import compute_uncertainty_for_patient


def generate_uncertainty_for_dataset(
    phase2_data_dir: str,
    output_dir: str,
    model_path: str = None,
    device: str = "cpu",
    num_samples: int = 20,
    seed: int = 42,
    max_patients: int = None
) -> None:
    """
    Generate uncertainty artifacts for all patients.
    
    Args:
        phase2_data_dir: Directory containing Phase 2 .npy files
        output_dir: Directory to save uncertainty .npy files
        model_path: Path to pretrained model (optional)
        device: Device for inference ('cpu' or 'cuda')
        num_samples: Number of MC dropout samples (T)
        seed: Random seed for reproducibility
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
    print(f"Phase 4 — Generate Epistemic Uncertainty")
    print(f"{'='*60}")
    print(f"Phase 2 data directory: {phase2_data_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Patients to process: {len(patient_files)}")
    print(f"Device: {device}")
    print(f"MC samples (T): {num_samples}")
    print(f"Random seed: {seed}")
    print(f"{'='*60}\n")
    
    # Load frozen model
    print("Loading frozen segmentation model...")
    model = load_frozen_model(model_path=model_path, device=device, use_nnunet=False)
    print()
    
    # Process each patient
    for i, patient_file in enumerate(patient_files):
        print(f"\n[{i+1}/{len(patient_files)}] Processing: {patient_file.name}")
        
        # Compute uncertainty
        uncertainties = compute_uncertainty_for_patient(
            patient_data_path=str(patient_file),
            model=model,
            num_samples=num_samples,
            seed=seed,
            verbose=True
        )
        
        # Save uncertainties
        patient_id = uncertainties["patient_id"]
        output_file = output_path / f"{patient_id}.npy"
        np.save(output_file, uncertainties, allow_pickle=True)
        
        print(f"   💾 Saved to: {output_file.name}")
    
    print(f"\n{'='*60}")
    print(f"✅ Uncertainty generation complete!")
    print(f"   Processed: {len(patient_files)} patients")
    print(f"   Output directory: {output_dir}")
    print(f"{'='*60}\n")


def verify_uncertainty(
    uncertainty_dir: str,
    phase2_data_dir: str
) -> None:
    """
    Verify uncertainty alignment with Phase 2 data.
    
    Args:
        uncertainty_dir: Directory containing uncertainty .npy files
        phase2_data_dir: Directory containing Phase 2 .npy files
    """
    uncertainty_path = Path(uncertainty_dir)
    phase2_path = Path(phase2_data_dir)
    
    uncertainty_files = sorted(uncertainty_path.glob("*.npy"))
    
    if len(uncertainty_files) == 0:
        print(f"❌ No uncertainty files found in: {uncertainty_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"Verifying Uncertainty Artifacts")
    print(f"{'='*60}\n")
    
    for uncertainty_file in uncertainty_files:
        patient_id = uncertainty_file.stem
        phase2_file = phase2_path / f"{patient_id}.npy"
        
        if not phase2_file.exists():
            print(f"⚠️  Phase 2 file not found for: {patient_id}")
            continue
        
        # Load data
        uncertainties = np.load(uncertainty_file, allow_pickle=True).item()
        phase2_data = np.load(phase2_file, allow_pickle=True).item()
        
        # Verify structure
        assert "patient_id" in uncertainties, "Missing patient_id"
        assert "slices" in uncertainties, "Missing slices"
        assert uncertainties["patient_id"] == patient_id, "Patient ID mismatch"
        
        # Verify slice alignment
        uncertainty_slices = uncertainties["slices"]
        phase2_slices = phase2_data["slices"]
        
        assert len(uncertainty_slices) == len(phase2_slices), \
            f"Slice count mismatch: {len(uncertainty_slices)} vs {len(phase2_slices)}"
        
        # Verify each slice
        for unc_slice, phase2_slice in zip(uncertainty_slices, phase2_slices):
            assert unc_slice["slice_id"] == phase2_slice["slice_id"], \
                "Slice ID mismatch"
            
            assert "uncertainty_map" in unc_slice, "Missing uncertainty_map"
            assert "slice_uncertainty" in unc_slice, "Missing slice_uncertainty"
            
            uncertainty_map = unc_slice["uncertainty_map"]
            slice_uncertainty = unc_slice["slice_uncertainty"]
            image = phase2_slice["image"]
            
            # Verify shapes
            assert uncertainty_map.shape == image.shape, "Shape mismatch: uncertainty_map"
            
            # Verify dtypes
            assert uncertainty_map.dtype == np.float32, f"Wrong dtype: {uncertainty_map.dtype}"
            assert isinstance(slice_uncertainty, (float, np.floating)), \
                f"slice_uncertainty must be scalar, got {type(slice_uncertainty)}"
            
            # Verify ranges
            assert 0 <= uncertainty_map.min() <= uncertainty_map.max() <= 1, \
                f"uncertainty_map out of range: [{uncertainty_map.min()}, {uncertainty_map.max()}]"
            assert 0 <= slice_uncertainty <= 1, \
                f"slice_uncertainty out of range: {slice_uncertainty}"
        
        # Compute statistics
        slice_uncertainties = [s["slice_uncertainty"] for s in uncertainty_slices]
        print(f"✅ {patient_id}: {len(uncertainty_slices)} slices")
        print(f"   Mean uncertainty: {np.mean(slice_uncertainties):.4f}")
        print(f"   Std uncertainty: {np.std(slice_uncertainties):.4f}")
    
    print(f"\n{'='*60}")
    print(f"✅ All uncertainty artifacts verified successfully!")
    print(f"{'='*60}\n")


def main():
    """
    Command-line interface for uncertainty generation.
    
    Usage:
        python generate_uncertainty.py --phase2_dir ./processed --output_dir ./uncertainty
        python generate_uncertainty.py --verify --uncertainty_dir ./uncertainty --phase2_dir ./processed
    """
    parser = argparse.ArgumentParser(
        description="Phase 4 — Generate Epistemic Uncertainty"
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
        default="./uncertainty",
        help="Directory to save uncertainty .npy files"
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
        "--num_samples",
        type=int,
        default=20,
        help="Number of MC dropout samples (T)"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility"
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
        help="Verify uncertainty artifacts instead of generating"
    )
    
    parser.add_argument(
        "--uncertainty_dir",
        type=str,
        default="./uncertainty",
        help="Directory containing uncertainty artifacts for verification"
    )
    
    args = parser.parse_args()
    
    if args.verify:
        # Verification mode
        verify_uncertainty(
            uncertainty_dir=args.uncertainty_dir,
            phase2_data_dir=args.phase2_dir
        )
    else:
        # Generation mode
        generate_uncertainty_for_dataset(
            phase2_data_dir=args.phase2_dir,
            output_dir=args.output_dir,
            model_path=args.model_path,
            device=args.device,
            num_samples=args.num_samples,
            seed=args.seed,
            max_patients=args.max_patients
        )


if __name__ == "__main__":
    main()
