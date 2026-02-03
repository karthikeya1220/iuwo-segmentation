import numpy as np
import nibabel as nib
from pathlib import Path
import os
import argparse

def convert_volume_to_slices(input_dir, output_dir):
    """
    Convert 3D nnU-Net predictions back to Phase 3 slice artifacts.
    
    Input: nnU-Net output NIfTI (binary or integer masks)
    Output: Phase 3 .npy artifacts (slice_id, prob_map, pred_mask)
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    files = sorted(input_path.glob("*.nii.gz"))
    if len(files) == 0:
        print(f"❌ No NIfTI files found in {input_dir}")
        return

    print(f"Found {len(files)} nnU-Net predictions.")
    
    for f in files:
        filename = f.name
        # Handle filenames: nnU-Net typically outputs Case_Identifier.nii.gz
        # Our input was Case_Identifier_0000.nii.gz
        patient_id = filename.replace(".nii.gz", "")
        # Remove _0000 if it persisted (unlikely but safe)
        if patient_id.endswith("_0000"):
            patient_id = patient_id[:-5]
            
        print(f"Processing {patient_id} from {filename}...")
             
        # Load NIfTI
        try:
            img = nib.load(f)
            volume = img.get_fdata() # (H, W, D)
        except Exception as e:
            print(f"Failed to load {f}: {e}")
            continue

        # Convert to binary mask (Whole Tumor)
        # Any non-zero label is considered tumor for this binary pipeline
        pred_mask = (volume > 0).astype(np.uint8)
        
        # Create Probability Map
        # Since we ran inference without probabilities (hard output), 
        # we treat the binary mask as the probability map (0.0 or 1.0).
        prob_map = pred_mask.astype(np.float32)
        
        slices = []
        D = volume.shape[2]
        
        for i in range(D):
             slice_dict = {
                 "slice_id": i,
                 # Ensure strict float32 and dimensions
                 "prob_map": prob_map[:, :, i].astype(np.float32),
                 "pred_mask": pred_mask[:, :, i].astype(np.uint8)
             }
             slices.append(slice_dict)
             
        # Save Phase 3 artifact
        out_name = f"{patient_id}.npy"
        np.save(output_path / out_name, {"patient_id": patient_id, "slices": slices})
        print(f"   Saved {out_name} (Slices: {len(slices)})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", required=True, help="nnU-Net output dir")
    parser.add_argument("--output_dir", required=True, help="Phase 3 predictions dir")
    args = parser.parse_args()
    convert_volume_to_slices(args.input_dir, args.output_dir)
