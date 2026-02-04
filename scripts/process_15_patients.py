#!/usr/bin/env python3
"""
Process 15-patient dataset for IUWO evaluation

This script processes the extracted BraTS patients from data/raw_subset/
and prepares them for evaluation using the existing IUWO pipeline.

Adapts to the BraTS-GLI naming convention:
- FLAIR modality: {patient_id}-t2f.nii
- Segmentation: {patient_id}-seg.nii
"""

import sys
from pathlib import Path

# Add parent directory to path to import existing module
sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))

from load_brats_axial import (
    load_nifti_volume,
    extract_axial_slices
)
import numpy as np


def process_brats_gli_patient(patient_dir: Path, output_dir: Path) -> None:
    """
    Process a single BraTS-GLI patient directory.
    
    Expected directory structure:
        patient_dir/
            ├── {patient_id}-t2f.nii      # T2-FLAIR modality
            └── {patient_id}-seg.nii      # Ground truth segmentation
    
    Args:
        patient_dir: Path to patient directory
        output_dir: Path to output directory for .npy files
        
    Output:
        Saves {patient_id}.npy to output_dir
    """
    patient_id = patient_dir.name
    
    # BraTS-GLI naming convention: {patient_id}-{modality}.nii
    flair_path = patient_dir / f"{patient_id}-t2f.nii"
    seg_path = patient_dir / f"{patient_id}-seg.nii"
    
    # Try .nii.gz if .nii doesn't exist
    if not flair_path.exists():
        flair_path = patient_dir / f"{patient_id}-t2f.nii.gz"
    if not seg_path.exists():
        seg_path = patient_dir / f"{patient_id}-seg.nii.gz"
    
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


def main():
    """Process all 15 patients from data/raw_subset/"""
    
    # Paths
    raw_subset_dir = Path("data/raw_subset")
    output_dir = Path("data/processed")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all patient directories
    patient_dirs = sorted([
        d for d in raw_subset_dir.iterdir() 
        if d.is_dir() and d.name.startswith('BraTS-')
    ])
    
    if len(patient_dirs) == 0:
        print(f"❌ No patient directories found in: {raw_subset_dir}")
        return 1
    
    print(f"{'='*60}")
    print(f"BraTS-GLI Dataset Processing — 15 Patients")
    print(f"{'='*60}")
    print(f"Input directory:  {raw_subset_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Patients found:   {len(patient_dirs)}")
    print(f"{'='*60}\n")
    
    # Process each patient
    for patient_dir in patient_dirs:
        try:
            process_brats_gli_patient(patient_dir, output_dir)
        except Exception as e:
            print(f"❌ Error processing {patient_dir.name}: {e}\n")
            continue
    
    print(f"{'='*60}")
    print(f"✅ Processing complete!")
    print(f"   Processed: {len(list(output_dir.glob('*.npy')))} patients")
    print(f"{'='*60}")
    
    return 0


if __name__ == "__main__":
    exit(main())
