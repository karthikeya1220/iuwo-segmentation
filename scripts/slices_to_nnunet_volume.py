import numpy as np
import nibabel as nib
from pathlib import Path
import os
import argparse

def convert_slices_to_volume(input_dir, output_dir):
    """
    Convert Phase 2 slice artifacts (.npy) to 3D NIfTI volumes for nnU-Net.
    
    Format:
        Input: .npy dictionary with 'slices' list
        Output: Case_Identifier_0000.nii.gz
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    files = sorted(input_path.glob("*.npy"))
    print(f"Found {len(files)} processed patients.")
    
    for f in files:
        data = np.load(f, allow_pickle=True).item()
        patient_id = data["patient_id"]
        slices = data["slices"]
        
        # Sort slices by ID just in case (Phase 2 guarantees sorting, but valid to check)
        slices.sort(key=lambda x: x["slice_id"])
        
        # Stack images
        # slices[i]["image"] is (H, W) -> Stack to (H, W, D)
        volume_data = np.stack([s["image"] for s in slices], axis=2)
        
        # Create NIfTI with Identity affine
        # Note: We assume 1x1x1 mm spacing or disregard geometry as Phase 3 
        # is purely slice-based validation. nnU-Net might resample internally
        # but we convert back in Step 3 effectively undoing/ignoring it if we map voxel-to-voxel.
        # Ideally we should use original affine, but Phase 2 abstraction discarded it.
        affine = np.eye(4)
        nifti_img = nib.Nifti1Image(volume_data, affine)
        
        # Save as _0000.nii.gz for nnU-Net
        out_name = f"{patient_id}_0000.nii.gz"
        nib.save(nifti_img, output_path / out_name)
        print(f"Saved {out_name} (Shape: {volume_data.shape})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", required=True, help="Phase 2 processed dir")
    parser.add_argument("--output_dir", required=True, help="nnU-Net input dir (imagesTs)")
    args = parser.parse_args()
    convert_slices_to_volume(args.input_dir, args.output_dir)
