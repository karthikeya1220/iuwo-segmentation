#!/usr/bin/env python3
"""
Selective BraTS 2024 Patient Extraction
========================================
Extracts a predefined subset of patients from archive.zip without
unpacking the entire archive (disk-space efficient).

Usage:
    python scripts/extract_brats_subset.py [--dry-run]

Output:
    data/brats_subset/BraTS-GLI-XXXXX-YYY/
"""

import os
import sys
import zipfile
from pathlib import Path
from typing import List, Set

# ============================================================================
# CONFIGURATION
# ============================================================================

ARCHIVE_PATH = "/Users/darshankarthikeya/Downloads/archive.zip"
OUTPUT_DIR = "data/brats_subset"

# Training patients (20)
TRAINING_PATIENTS = [
    "BraTS-GLI-00005-100", "BraTS-GLI-00005-101",
    "BraTS-GLI-00006-100", "BraTS-GLI-00006-101",
    "BraTS-GLI-00020-100", "BraTS-GLI-00020-101",
    "BraTS-GLI-00027-100", "BraTS-GLI-00027-101",
    "BraTS-GLI-00033-100", "BraTS-GLI-00033-101",
    "BraTS-GLI-00046-100", "BraTS-GLI-00046-101",
    "BraTS-GLI-00060-100", "BraTS-GLI-00060-101",
    "BraTS-GLI-00063-100", "BraTS-GLI-00063-101",
    "BraTS-GLI-00078-100", "BraTS-GLI-00078-101",
    "BraTS-GLI-00080-100", "BraTS-GLI-00080-101",
]

# Evaluation patients (3)
EVALUATION_PATIENTS = [
    "BraTS-GLI-00008-103",
    "BraTS-GLI-00009-100",
    "BraTS-GLI-00085-100",
]

# All patients to extract
ALL_PATIENTS = TRAINING_PATIENTS + EVALUATION_PATIENTS

# Valid file extensions
VALID_EXTENSIONS = {".nii", ".nii.gz"}

# ============================================================================
# EXTRACTION LOGIC
# ============================================================================

def verify_no_overlap() -> bool:
    """Verify training and evaluation sets don't overlap."""
    train_set = set(TRAINING_PATIENTS)
    eval_set = set(EVALUATION_PATIENTS)
    overlap = train_set & eval_set
    
    if overlap:
        print(f"❌ ERROR: Training/Evaluation overlap detected: {overlap}")
        return False
    
    print(f"✅ No overlap: {len(train_set)} training, {len(eval_set)} evaluation")
    return True


def extract_patients(dry_run: bool = False) -> None:
    """
    Extract specified patients from archive.zip.
    
    Args:
        dry_run: If True, only print what would be extracted
    """
    # Verify archive exists
    if not os.path.exists(ARCHIVE_PATH):
        print(f"❌ Archive not found: {ARCHIVE_PATH}")
        sys.exit(1)
    
    # Verify no overlap
    if not verify_no_overlap():
        sys.exit(1)
    
    # Create output directory
    output_path = Path(OUTPUT_DIR)
    if not dry_run:
        output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*70}")
    print(f"BraTS 2024 Selective Extraction")
    print(f"{'='*70}")
    print(f"Archive: {ARCHIVE_PATH}")
    print(f"Output:  {OUTPUT_DIR}")
    print(f"Mode:    {'DRY RUN' if dry_run else 'EXTRACTION'}")
    print(f"Patients: {len(ALL_PATIENTS)} total")
    print(f"{'='*70}\n")
    
    # Track statistics
    stats = {
        "patients_found": 0,
        "patients_missing": [],
        "files_extracted": 0,
        "total_bytes": 0,
        "per_patient": {}
    }
    
    # Open archive
    with zipfile.ZipFile(ARCHIVE_PATH, 'r') as zf:
        # Get all file paths in archive
        all_files = zf.namelist()
        
        # Process each patient
        for patient_id in ALL_PATIENTS:
            print(f"Processing: {patient_id}...", end=" ")
            
            # Find files for this patient
            patient_files = [
                f for f in all_files
                if patient_id in f and any(f.endswith(ext) for ext in VALID_EXTENSIONS)
            ]
            
            if not patient_files:
                print(f"❌ NOT FOUND")
                stats["patients_missing"].append(patient_id)
                continue
            
            # Extract files
            patient_count = 0
            patient_bytes = 0
            
            for file_path in patient_files:
                # Get file info
                file_info = zf.getinfo(file_path)
                
                # Construct output path
                # Handle various archive structures (e.g., BraTS-GLI-00005-100/file.nii)
                parts = Path(file_path).parts
                
                # Find patient directory in path
                patient_dir_idx = None
                for i, part in enumerate(parts):
                    if patient_id in part:
                        patient_dir_idx = i
                        break
                
                if patient_dir_idx is None:
                    continue
                
                # Reconstruct relative path from patient directory
                relative_path = Path(*parts[patient_dir_idx:])
                output_file = output_path / relative_path
                
                if dry_run:
                    print(f"\n  [DRY] {file_path} -> {output_file}")
                else:
                    # Create parent directory
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Extract file
                    with zf.open(file_path) as source, open(output_file, 'wb') as target:
                        target.write(source.read())
                
                patient_count += 1
                patient_bytes += file_info.file_size
            
            stats["patients_found"] += 1
            stats["files_extracted"] += patient_count
            stats["total_bytes"] += patient_bytes
            stats["per_patient"][patient_id] = {
                "files": patient_count,
                "bytes": patient_bytes
            }
            
            print(f"✅ {patient_count} files ({patient_bytes / 1024 / 1024:.1f} MB)")
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"EXTRACTION SUMMARY")
    print(f"{'='*70}")
    print(f"Patients found:    {stats['patients_found']}/{len(ALL_PATIENTS)}")
    print(f"Files extracted:   {stats['files_extracted']}")
    print(f"Total size:        {stats['total_bytes'] / 1024 / 1024:.1f} MB")
    
    if stats["patients_missing"]:
        print(f"\n⚠️  Missing patients ({len(stats['patients_missing'])}):")
        for patient in stats["patients_missing"]:
            print(f"  - {patient}")
    
    print(f"\n{'='*70}")
    print(f"Per-Patient Statistics:")
    print(f"{'='*70}")
    
    # Group by category
    for category, patients in [("Training", TRAINING_PATIENTS), ("Evaluation", EVALUATION_PATIENTS)]:
        print(f"\n{category} Set:")
        for patient in patients:
            if patient in stats["per_patient"]:
                info = stats["per_patient"][patient]
                print(f"  {patient}: {info['files']} files, {info['bytes'] / 1024 / 1024:.1f} MB")
            else:
                print(f"  {patient}: ❌ MISSING")
    
    print(f"\n{'='*70}")
    
    if not dry_run:
        print(f"✅ Extraction complete: {OUTPUT_DIR}")
    else:
        print(f"ℹ️  Dry run complete. Use without --dry-run to extract.")
    
    print(f"{'='*70}\n")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    
    try:
        extract_patients(dry_run=dry_run)
    except KeyboardInterrupt:
        print("\n\n⚠️  Extraction cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
