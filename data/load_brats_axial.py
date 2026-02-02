"""
Phase 2 — BraTS Dataset Loading & Axial Slicing

This module loads BraTS NIfTI files, extracts FLAIR modality and ground-truth
segmentation masks, and slices volumes strictly along the axial axis.

Design Constraints:
- Use ONLY FLAIR modality
- Slice STRICTLY along axial axis (axis=2 in NIfTI convention)
- Do NOT remove empty slices
- Do NOT normalize across patients
- Do NOT resample, resize, or augment
- Do NOT compute Dice, uncertainty, or features
- Do NOT introduce model inference

Output Format:
Each patient is saved as a single .npy file with structure:
{
  "patient_id": str,
  "slices": [
    {
      "slice_id": int,
      "image": np.ndarray (H, W),
      "mask": np.ndarray (H, W)
    },
    ...
  ]
}

Author: Research Prototype
Date: 2026-02-02
"""

import os
import numpy as np
import nibabel as nib
from pathlib import Path
from typing import Dict, List, Tuple
import argparse


def load_nifti_volume(filepath: str) -> np.ndarray:
    """
    Load a NIfTI file and return the volume as a numpy array.
    
    Args:
        filepath: Path to .nii or .nii.gz file
        
    Returns:
        Volume as numpy array with shape (H, W, D)
        
    Note:
        NIfTI files are loaded in their native orientation.
        No resampling or reorientation is performed.
    """
    nifti_img = nib.load(filepath)
    volume = nifti_img.get_fdata()
    return np.array(volume)


def extract_axial_slices(
    image_volume: np.ndarray,
    mask_volume: np.ndarray,
    patient_id: str
) -> Dict:
    """
    Extract axial slices from 3D volumes.
    
    Args:
        image_volume: FLAIR image volume (H, W, D)
        mask_volume: Segmentation mask volume (H, W, D)
        patient_id: Unique patient identifier
        
    Returns:
        Dictionary containing patient_id and list of slice dictionaries
        
    Design decisions:
        - Slices are extracted along axis 2 (axial plane)
        - Slice indices are 0-indexed and stable
        - Empty slices are NOT removed
        - Image and mask are perfectly aligned by construction
    """
    # Verify volumes have the same shape
    assert image_volume.shape == mask_volume.shape, \
        f"Image and mask shapes must match: {image_volume.shape} vs {mask_volume.shape}"
    
    H, W, D = image_volume.shape
    
    # Extract slices along axial axis (axis=2)
    slices = []
    for slice_idx in range(D):
        slice_dict = {
            "slice_id": slice_idx,  # 0-indexed, stable identifier
            "image": image_volume[:, :, slice_idx].astype(np.float32),
            "mask": mask_volume[:, :, slice_idx].astype(np.uint8)
        }
        slices.append(slice_dict)
    
    patient_data = {
        "patient_id": patient_id,
        "slices": slices
    }
    
    return patient_data


def process_brats_patient(
    patient_dir: Path,
    output_dir: Path
) -> None:
    """
    Process a single BraTS patient directory.
    
    Expected directory structure:
        patient_dir/
            ├── {patient_id}_flair.nii.gz      # FLAIR modality
            └── {patient_id}_seg.nii.gz        # Ground truth segmentation
    
    Args:
        patient_dir: Path to patient directory
        output_dir: Path to output directory for .npy files
        
    Output:
        Saves {patient_id}.npy to output_dir
    """
    patient_id = patient_dir.name
    
    # Construct file paths
    # BraTS naming convention: {patient_id}_{modality}.nii.gz
    flair_path = patient_dir / f"{patient_id}_flair.nii.gz"
    seg_path = patient_dir / f"{patient_id}_seg.nii.gz"
    
    # Verify files exist
    if not flair_path.exists():
        print(f"⚠️  FLAIR file not found: {flair_path}")
        return
    
    if not seg_path.exists():
        print(f"⚠️  Segmentation file not found: {seg_path}")
        return
    
    print(f"📂 Processing patient: {patient_id}")
    
    # Load volumes
    print(f"   Loading FLAIR from: {flair_path.name}")
    flair_volume = load_nifti_volume(str(flair_path))
    
    print(f"   Loading segmentation from: {seg_path.name}")
    seg_volume = load_nifti_volume(str(seg_path))
    
    # Extract axial slices
    print(f"   Extracting axial slices (shape: {flair_volume.shape})")
    patient_data = extract_axial_slices(
        image_volume=flair_volume,
        mask_volume=seg_volume,
        patient_id=patient_id
    )
    
    # Save to .npy file
    output_path = output_dir / f"{patient_id}.npy"
    np.save(output_path, patient_data, allow_pickle=True)
    
    num_slices = len(patient_data["slices"])
    print(f"   ✅ Saved {num_slices} slices to: {output_path.name}\n")


def process_brats_dataset(
    brats_dir: str,
    output_dir: str,
    max_patients: int = 10
) -> None:
    """
    Process BraTS dataset and extract axial slices for multiple patients.
    
    Args:
        brats_dir: Path to BraTS dataset root directory
        output_dir: Path to output directory for processed .npy files
        max_patients: Maximum number of patients to process (for prototyping)
        
    Directory structure:
        brats_dir/
            ├── BraTS2021_00000/
            │   ├── BraTS2021_00000_flair.nii.gz
            │   └── BraTS2021_00000_seg.nii.gz
            ├── BraTS2021_00001/
            │   ├── BraTS2021_00001_flair.nii.gz
            │   └── BraTS2021_00001_seg.nii.gz
            └── ...
    
    Output:
        output_dir/
            ├── BraTS2021_00000.npy
            ├── BraTS2021_00001.npy
            └── ...
    """
    brats_path = Path(brats_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all patient directories
    patient_dirs = sorted([d for d in brats_path.iterdir() if d.is_dir()])
    
    if len(patient_dirs) == 0:
        print(f"❌ No patient directories found in: {brats_dir}")
        return
    
    # Limit to max_patients for prototyping
    patient_dirs = patient_dirs[:max_patients]
    
    print(f"{'='*60}")
    print(f"BraTS Axial Slice Extraction — Phase 2")
    print(f"{'='*60}")
    print(f"Dataset directory: {brats_dir}")
    print(f"Output directory:  {output_dir}")
    print(f"Patients to process: {len(patient_dirs)}")
    print(f"{'='*60}\n")
    
    # Process each patient
    for patient_dir in patient_dirs:
        process_brats_patient(patient_dir, output_path)
    
    print(f"{'='*60}")
    print(f"✅ Processing complete!")
    print(f"{'='*60}")


def load_processed_patient(filepath: str) -> Dict:
    """
    Load a processed patient .npy file.
    
    Args:
        filepath: Path to .npy file
        
    Returns:
        Dictionary with patient_id and slices
        
    Example usage:
        >>> data = load_processed_patient("output/BraTS2021_00000.npy")
        >>> print(data["patient_id"])
        >>> print(len(data["slices"]))
        >>> slice_0 = data["slices"][0]
        >>> print(slice_0["slice_id"])
        >>> print(slice_0["image"].shape)
        >>> print(slice_0["mask"].shape)
    """
    data = np.load(filepath, allow_pickle=True).item()
    return data


def verify_processed_data(output_dir: str) -> None:
    """
    Verify the integrity of processed data.
    
    Args:
        output_dir: Path to directory containing .npy files
        
    Checks:
        - All files can be loaded
        - Image and mask shapes match
        - Slice IDs are sequential
        - Data types are correct
    """
    output_path = Path(output_dir)
    npy_files = sorted(output_path.glob("*.npy"))
    
    if len(npy_files) == 0:
        print(f"❌ No .npy files found in: {output_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"Data Verification")
    print(f"{'='*60}\n")
    
    for npy_file in npy_files:
        print(f"Verifying: {npy_file.name}")
        
        # Load data
        data = load_processed_patient(str(npy_file))
        
        patient_id = data["patient_id"]
        slices = data["slices"]
        
        # Check slice count
        num_slices = len(slices)
        print(f"  Patient ID: {patient_id}")
        print(f"  Number of slices: {num_slices}")
        
        # Verify first and last slice
        first_slice = slices[0]
        last_slice = slices[-1]
        
        # Check slice IDs are sequential
        assert first_slice["slice_id"] == 0, "First slice ID should be 0"
        assert last_slice["slice_id"] == num_slices - 1, \
            f"Last slice ID should be {num_slices - 1}"
        
        # Check shapes
        img_shape = first_slice["image"].shape
        mask_shape = first_slice["mask"].shape
        assert img_shape == mask_shape, "Image and mask shapes must match"
        print(f"  Slice shape: {img_shape}")
        
        # Check data types
        assert first_slice["image"].dtype == np.float32, "Image should be float32"
        assert first_slice["mask"].dtype == np.uint8, "Mask should be uint8"
        
        # Check for NaN or Inf
        has_nan = np.any(np.isnan(first_slice["image"]))
        has_inf = np.any(np.isinf(first_slice["image"]))
        assert not has_nan, "Image contains NaN values"
        assert not has_inf, "Image contains Inf values"
        
        print(f"  ✅ Verification passed\n")
    
    print(f"{'='*60}")
    print(f"✅ All files verified successfully!")
    print(f"{'='*60}\n")


def main():
    """
    Command-line interface for BraTS axial slice extraction.
    
    Usage:
        python load_brats_axial.py --brats_dir /path/to/brats --output_dir ./processed
        python load_brats_axial.py --brats_dir /path/to/brats --output_dir ./processed --max_patients 5
        python load_brats_axial.py --verify --output_dir ./processed
    """
    parser = argparse.ArgumentParser(
        description="BraTS Axial Slice Extraction — Phase 2"
    )
    
    parser.add_argument(
        "--brats_dir",
        type=str,
        help="Path to BraTS dataset root directory"
    )
    
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./processed",
        help="Path to output directory for .npy files (default: ./processed)"
    )
    
    parser.add_argument(
        "--max_patients",
        type=int,
        default=10,
        help="Maximum number of patients to process (default: 10)"
    )
    
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify processed data integrity"
    )
    
    args = parser.parse_args()
    
    if args.verify:
        # Verification mode
        verify_processed_data(args.output_dir)
    else:
        # Processing mode
        if args.brats_dir is None:
            parser.error("--brats_dir is required when not in --verify mode")
        
        process_brats_dataset(
            brats_dir=args.brats_dir,
            output_dir=args.output_dir,
            max_patients=args.max_patients
        )


if __name__ == "__main__":
    main()
