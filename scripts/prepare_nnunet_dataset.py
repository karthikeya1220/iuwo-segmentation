import os
import subprocess
import shutil
from pathlib import Path
import json
import numpy as np
import nibabel as nib

def preparation():
    zip_path = "/Users/darshankarthikeya/Downloads/archive.zip"
    raw_base = Path("nnunet_env/nnUNet_raw/Dataset001_BraTS")
    imagesTr = raw_base / "imagesTr"
    labelsTr = raw_base / "labelsTr"
    
    imagesTr.mkdir(parents=True, exist_ok=True)
    labelsTr.mkdir(parents=True, exist_ok=True)
    
    print("Scanning zip file...")
    # List zip content to identify patients
    cmd = ["unzip", "-l", zip_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    lines = result.stdout.splitlines()
    
    patient_ids = set()
    for line in lines:
        parts = line.split()
        if len(parts) >= 4:
            path = parts[3]
            # Structure: BraTS-GLI-XXXXX-YYY/filename
            if "BraTS-GLI-" in path and "/" in path:
                pid = path.split("/")[0]
                patient_ids.add(pid)
                
    # Filter and Select
    eval_ids = {"BraTS-GLI-00008-103", "BraTS-GLI-00009-100"}
    # Exclude eval ids from candidate pool
    candidates = sorted(list(patient_ids - eval_ids))
    
    # Select 25 patients
    train_ids = candidates[:25]
    
    print(f"Selected {len(train_ids)} patients for training.")
    print(f"Verified exclusion of evaluation patients: {eval_ids.intersection(set(train_ids)) == set()}")
    
    # Extract
    temp_dir = Path("temp_extract")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(exist_ok=True)
    
    success_count = 0
    
    for pid in train_ids:
        # Check specific filenames (hyphens based on previous knowledge)
        # Archive filename format: {pid}/{pid}-t2f.nii
        files_to_extract = [f"{pid}/{pid}-t2f.nii", f"{pid}/{pid}-seg.nii"]
        
        # Unzip
        subprocess.run(["unzip", "-o", "-j", zip_path, *files_to_extract, "-d", str(temp_dir)], check=False, stdout=subprocess.DEVNULL)
        
        flair_src = temp_dir / f"{pid}-t2f.nii"
        seg_src = temp_dir / f"{pid}-seg.nii"
        
        if flair_src.exists() and seg_src.exists():
            # Process FLAIR
            # Save as {pid}_0000.nii.gz
            img = nib.load(flair_src)
            nib.save(img, imagesTr / f"{pid}_0000.nii.gz")
            
            # Process Seg
            # Binarize > 0 -> 1
            seg = nib.load(seg_src)
            seg_data = seg.get_fdata()
            seg_bin = (seg_data > 0).astype(np.uint8)
            new_seg = nib.Nifti1Image(seg_bin, seg.affine, seg.header)
            nib.save(new_seg, labelsTr / f"{pid}.nii.gz")
            
            success_count += 1
            print(f"   Processed {pid}")
            
        # Clean temp
        for f in temp_dir.glob("*"):
            f.unlink()
            
    temp_dir.rmdir()
    print(f"Successfully prepared {success_count} training pairs.")
    
    # Create dataset.json
    meta = {
        "channel_names": {"0": "FLAIR"},
        "labels": {"background": 0, "tumor": 1},
        "numTraining": success_count,
        "file_ending": ".nii.gz",
        "name": "BraTS_Binary",
        "reference": "BraTS2024",
        "release": "1.0",
        "description": "Binary Whole Tumor Segmentation",
        "tensorImageSize": "3D", 
        "modality": {"0": "MRI"}
    }
    
    with open(raw_base / "dataset.json", "w") as f:
        json.dump(meta, f, indent=4)
        
    print("dataset.json created.")

if __name__ == "__main__":
    preparation()
