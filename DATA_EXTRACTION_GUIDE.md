# BraTS 2024 Subset Extraction Guide

## Overview

This directory contains scripts for **selective extraction** of a predefined patient subset from the BraTS 2024 archive without unpacking the entire dataset (disk-space efficient).

## Why Selective Extraction?

- **Disk Space:** BraTS 2024 full archive is ~50GB. We only need 23 patients (~2-3GB).
- **Speed:** Extracting specific patients is 10-20x faster than full extraction.
- **Reproducibility:** Ensures exact patient subset matches `PATIENT_SELECTION_STRATEGY.md`.

## Available Scripts

### 1. Python Script (Recommended)

**File:** `scripts/extract_brats_subset.py`

**Advantages:**

- Cross-platform (macOS, Linux, Windows)
- Detailed statistics and progress
- Better error handling
- Per-patient file count and size

**Usage:**

```bash
# Dry run (see what would be extracted)
python scripts/extract_brats_subset.py --dry-run

# Actual extraction
python scripts/extract_brats_subset.py
```

### 2. Bash Script (Alternative)

**File:** `scripts/extract_brats_subset.sh`

**Advantages:**

- No Python dependency
- Uses standard `unzip` command
- Simpler for shell scripting

**Usage:**

```bash
# Make executable
chmod +x scripts/extract_brats_subset.sh

# Dry run
./scripts/extract_brats_subset.sh --dry-run

# Actual extraction
./scripts/extract_brats_subset.sh
```

## Configuration

Both scripts extract the same patient subset:

**Training (20 patients):**

- Small volume: 6 patients (00005, 00006, 00020)
- Medium volume: 8 patients (00027, 00033, 00046, 00060)
- Large volume: 6 patients (00063, 00078, 00080)

**Evaluation (3 patients):**

- BraTS-GLI-00008-103 (medium, representative)
- BraTS-GLI-00009-100 (small, sparse)
- BraTS-GLI-00085-100 (large, dense)

**Total:** 23 patients

## Archive Location

Default: `/Users/darshankarthikeya/Downloads/archive.zip`

To change, edit the `ARCHIVE_PATH` variable in the scripts.

## Output Structure

```
data/brats_subset/
├── BraTS-GLI-00005-100/
│   ├── BraTS-GLI-00005-100-t1n.nii
│   ├── BraTS-GLI-00005-100-t1c.nii
│   ├── BraTS-GLI-00005-100-t2f.nii
│   ├── BraTS-GLI-00005-100-t2w.nii
│   └── BraTS-GLI-00005-100-seg.nii
├── BraTS-GLI-00005-101/
│   └── ...
└── ...
```

**Note:** Only `.nii` and `.nii.gz` files are extracted (metadata/README files are skipped).

## Safety Features

Both scripts include:

✅ **No-overlap verification:** Ensures training/evaluation sets don't overlap  
✅ **Missing patient detection:** Reports patients not found in archive  
✅ **Dry-run mode:** Preview extraction without writing files  
✅ **Progress tracking:** Shows per-patient extraction status  
✅ **Statistics:** File counts and total size

## Expected Output

```
======================================================================
BraTS 2024 Selective Extraction
======================================================================
Archive: /Users/darshankarthikeya/Downloads/archive.zip
Output:  data/brats_subset
Mode:    EXTRACTION
Patients: 23 total
======================================================================

✅ No overlap: 20 training, 3 evaluation

Processing: BraTS-GLI-00005-100... ✅ 5 files (45.2 MB)
Processing: BraTS-GLI-00005-101... ✅ 5 files (42.8 MB)
...

======================================================================
EXTRACTION SUMMARY
======================================================================
Patients found:    23/23
Files extracted:   115
Total size:        2.3 GB
======================================================================
```

## Troubleshooting

### Archive not found

```
❌ Archive not found: /Users/darshankarthikeya/Downloads/archive.zip
```

**Solution:** Update `ARCHIVE_PATH` in the script or move archive to expected location.

### Patient not found

```
Processing: BraTS-GLI-00085-100... ❌ NOT FOUND
```

**Possible causes:**

- Archive is incomplete
- Patient ID mismatch (check exact naming in archive)
- Archive structure differs from expected

**Solution:** Run `unzip -l archive.zip | grep BraTS-GLI-00085` to verify patient exists.

### Permission denied

```
PermissionError: [Errno 13] Permission denied: 'data/brats_subset'
```

**Solution:** Ensure you have write permissions in the project directory.

## For Google Colab Upload

After extraction, the `data/brats_subset/` directory is ready for upload to Colab:

```python
# In Colab
from google.colab import files
import zipfile

# Option 1: Upload zip of subset
# (Create zip locally first: zip -r brats_subset.zip data/brats_subset)
uploaded = files.upload()

# Option 2: Mount Google Drive and copy
from google.colab import drive
drive.mount('/content/drive')
!cp -r /content/drive/MyDrive/brats_subset data/
```

**Recommended:** Zip the subset locally, upload to Google Drive, then mount Drive in Colab (faster than direct upload).

## Verification

After extraction, verify the subset:

```bash
# Count patients
ls data/brats_subset | wc -l
# Expected: 23

# Count total files
find data/brats_subset -name "*.nii*" | wc -l
# Expected: ~115 (5 files per patient)

# Check total size
du -sh data/brats_subset
# Expected: ~2-3 GB
```

## Integration with Pipeline

The extraction scripts are designed to work seamlessly with:

1. `scripts/prepare_nnunet_dataset.py` - Formats subset for nnU-Net
2. `data/load_brats_axial.py` - Loads slices for pipeline
3. `scripts/train_and_evaluate.sh` - Main pipeline execution

**Workflow:**

```bash
# 1. Extract subset
python scripts/extract_brats_subset.py

# 2. Run pipeline (includes data preparation)
./scripts/train_and_evaluate.sh
```

## Documentation References

- **Patient Selection:** `PATIENT_SELECTION_STRATEGY.md`
- **Patient Lists:** `PATIENT_LISTS.md`
- **Pipeline Guide:** `QUICKSTART.md`

---

**Last Updated:** February 3, 2026  
**Status:** Production Ready
