"""
Example Usage — Phase 2 Data Loader

This script demonstrates how to use the BraTS axial slice loader
and inspect the processed data.

Usage:
    python examples/example_usage.py --data_dir ./processed
"""

import sys
import numpy as np
from pathlib import Path
import argparse


def inspect_patient_data(filepath: str) -> None:
    """
    Load and inspect a single patient's processed data.
    
    Args:
        filepath: Path to .npy file
    """
    print(f"\n{'='*60}")
    print(f"Inspecting: {Path(filepath).name}")
    print(f"{'='*60}\n")
    
    # Load data
    data = np.load(filepath, allow_pickle=True).item()
    
    # Extract patient information
    patient_id = data["patient_id"]
    slices = data["slices"]
    num_slices = len(slices)
    
    print(f"Patient ID: {patient_id}")
    print(f"Number of slices: {num_slices}\n")
    
    # Inspect first slice
    first_slice = slices[0]
    print(f"First Slice (ID: {first_slice['slice_id']}):")
    print(f"  Image shape: {first_slice['image'].shape}")
    print(f"  Image dtype: {first_slice['image'].dtype}")
    print(f"  Image range: [{first_slice['image'].min():.2f}, {first_slice['image'].max():.2f}]")
    print(f"  Mask shape: {first_slice['mask'].shape}")
    print(f"  Mask dtype: {first_slice['mask'].dtype}")
    print(f"  Mask unique values: {np.unique(first_slice['mask'])}\n")
    
    # Inspect middle slice
    mid_idx = num_slices // 2
    mid_slice = slices[mid_idx]
    print(f"Middle Slice (ID: {mid_slice['slice_id']}):")
    print(f"  Image shape: {mid_slice['image'].shape}")
    print(f"  Tumor pixels: {np.sum(mid_slice['mask'] > 0)}")
    print(f"  Tumor percentage: {100 * np.sum(mid_slice['mask'] > 0) / mid_slice['mask'].size:.2f}%\n")
    
    # Inspect last slice
    last_slice = slices[-1]
    print(f"Last Slice (ID: {last_slice['slice_id']}):")
    print(f"  Image shape: {last_slice['image'].shape}")
    print(f"  Tumor pixels: {np.sum(last_slice['mask'] > 0)}")
    print(f"  Tumor percentage: {100 * np.sum(last_slice['mask'] > 0) / last_slice['mask'].size:.2f}%\n")
    
    # Compute slice-level statistics
    tumor_counts = [np.sum(s['mask'] > 0) for s in slices]
    slices_with_tumor = sum(1 for count in tumor_counts if count > 0)
    
    print(f"Dataset Statistics:")
    print(f"  Slices with tumor: {slices_with_tumor} / {num_slices} ({100*slices_with_tumor/num_slices:.1f}%)")
    print(f"  Empty slices: {num_slices - slices_with_tumor} / {num_slices} ({100*(num_slices-slices_with_tumor)/num_slices:.1f}%)")
    
    if slices_with_tumor > 0:
        tumor_slice_ids = [i for i, count in enumerate(tumor_counts) if count > 0]
        print(f"  Tumor slice range: [{min(tumor_slice_ids)}, {max(tumor_slice_ids)}]")
    
    print(f"\n{'='*60}\n")


def compare_multiple_patients(data_dir: str, max_patients: int = 5) -> None:
    """
    Compare statistics across multiple patients.
    
    Args:
        data_dir: Directory containing .npy files
        max_patients: Maximum number of patients to compare
    """
    data_path = Path(data_dir)
    npy_files = sorted(data_path.glob("*.npy"))[:max_patients]
    
    if len(npy_files) == 0:
        print(f"❌ No .npy files found in: {data_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"Comparing {len(npy_files)} Patients")
    print(f"{'='*60}\n")
    
    for npy_file in npy_files:
        data = np.load(str(npy_file), allow_pickle=True).item()
        patient_id = data["patient_id"]
        slices = data["slices"]
        
        # Compute statistics
        num_slices = len(slices)
        tumor_counts = [np.sum(s['mask'] > 0) for s in slices]
        slices_with_tumor = sum(1 for count in tumor_counts if count > 0)
        total_tumor_voxels = sum(tumor_counts)
        
        # Image shape
        img_shape = slices[0]['image'].shape
        
        print(f"{patient_id}:")
        print(f"  Slices: {num_slices}")
        print(f"  Shape: {img_shape}")
        print(f"  Tumor slices: {slices_with_tumor} ({100*slices_with_tumor/num_slices:.1f}%)")
        print(f"  Total tumor voxels: {total_tumor_voxels:,}\n")
    
    print(f"{'='*60}\n")


def demonstrate_slice_iteration(filepath: str) -> None:
    """
    Demonstrate how to iterate through slices for processing.
    
    Args:
        filepath: Path to .npy file
    """
    print(f"\n{'='*60}")
    print(f"Slice Iteration Example")
    print(f"{'='*60}\n")
    
    # Load data
    data = np.load(filepath, allow_pickle=True).item()
    patient_id = data["patient_id"]
    slices = data["slices"]
    
    print(f"Patient: {patient_id}")
    print(f"Processing {len(slices)} slices...\n")
    
    # Example: Find slices with tumor
    tumor_slices = []
    for slice_data in slices:
        slice_id = slice_data["slice_id"]
        mask = slice_data["mask"]
        
        # Check if slice contains tumor
        if np.sum(mask > 0) > 0:
            tumor_slices.append(slice_id)
    
    print(f"Found {len(tumor_slices)} slices with tumor:")
    print(f"  Slice IDs: {tumor_slices[:10]}{'...' if len(tumor_slices) > 10 else ''}")
    
    # Example: Access specific slice by ID
    target_slice_id = tumor_slices[0] if tumor_slices else 0
    target_slice = slices[target_slice_id]
    
    print(f"\nAccessing slice {target_slice_id}:")
    print(f"  Image shape: {target_slice['image'].shape}")
    print(f"  Mask shape: {target_slice['mask'].shape}")
    print(f"  Tumor pixels: {np.sum(target_slice['mask'] > 0)}")
    
    print(f"\n{'='*60}\n")


def main():
    """
    Main function for example usage script.
    """
    parser = argparse.ArgumentParser(
        description="Example usage of Phase 2 data loader"
    )
    
    parser.add_argument(
        "--data_dir",
        type=str,
        default="./processed",
        help="Directory containing processed .npy files"
    )
    
    parser.add_argument(
        "--patient_file",
        type=str,
        help="Specific patient .npy file to inspect"
    )
    
    args = parser.parse_args()
    
    if args.patient_file:
        # Inspect specific patient
        inspect_patient_data(args.patient_file)
        demonstrate_slice_iteration(args.patient_file)
    else:
        # Compare multiple patients
        data_path = Path(args.data_dir)
        npy_files = sorted(data_path.glob("*.npy"))
        
        if len(npy_files) == 0:
            print(f"❌ No .npy files found in: {args.data_dir}")
            print(f"\nPlease run the data loader first:")
            print(f"  python data/load_brats_axial.py --brats_dir /path/to/brats --output_dir {args.data_dir}")
            return
        
        # Inspect first patient in detail
        inspect_patient_data(str(npy_files[0]))
        demonstrate_slice_iteration(str(npy_files[0]))
        
        # Compare all patients
        compare_multiple_patients(args.data_dir)


if __name__ == "__main__":
    main()
