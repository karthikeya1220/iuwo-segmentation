# Data Management Guide

## Overview

This project uses large medical imaging datasets (BraTS 2024) that are **NOT stored in Git** due to their size (2+ GB). Dataset files are managed separately to keep the repository lightweight and fast.

## Why Data Files Are Not in Git

- **Size**: Medical imaging files (.nii, .npy) are very large (20-60 MB each)
- **Performance**: Large binary files slow down Git operations (clone, pull, push)
- **Best Practice**: Git is designed for code, not large binary data
- **Collaboration**: Faster cloning and syncing for collaborators

## Excluded File Types

The following file types are excluded via `.gitignore`:

- `.nii` - NIfTI medical imaging format
- `.nii.gz` - Compressed NIfTI files
- `.npy` - NumPy array files (preprocessed data)
- `.npz` - Compressed NumPy archives
- `.h5`, `.hdf5` - HDF5 data files

## Directory Structure

```
data/
├── raw/                  # Original BraTS archive (not in Git)
├── raw_subset/           # Extracted patient subset (not in Git)
├── brats_subset/         # Alternative extraction location (not in Git)
└── processed/            # Preprocessed .npy files (not in Git)
```

## How to Obtain the Dataset

### Option 1: Extract from BraTS Archive

If you have the BraTS 2024 archive:

```bash
# Extract the specific patients used in this project
python scripts/extract_subset.py

# This will create data/raw_subset/ with 15 patients
```

See `PATIENT_LISTS.md` for the specific patient IDs used.

### Option 2: Download from External Storage

For collaborators, the dataset can be shared via:

- Google Drive
- Institutional file sharing
- Cloud storage (AWS S3, etc.)

**Note**: Due to data licensing, the BraTS dataset cannot be publicly redistributed. You must obtain it from the official BraTS challenge.

## Preprocessing

After obtaining the raw data:

```bash
# Preprocess the dataset
python scripts/process_15_patients.py

# This creates data/processed/*.npy files
```

## Verification

To verify your dataset is correctly set up:

```bash
# Check that all required patients are present
python scripts/validate_dataset.py
```

## For Reproducibility

The exact patient IDs and extraction process are documented in:

- `PATIENT_LISTS.md` - List of patient IDs
- `DATA_EXTRACTION_GUIDE.md` - Extraction instructions
- `EXTRACTION_SUMMARY.txt` - Extraction log

## Git LFS Alternative (Future)

For future work, consider using Git LFS (Large File Storage) for dataset versioning:

```bash
# Install Git LFS
brew install git-lfs  # macOS
# or: sudo apt-get install git-lfs  # Linux

# Initialize Git LFS
git lfs install

# Track large files
git lfs track "*.nii"
git lfs track "*.npy"

# Commit .gitattributes
git add .gitattributes
git commit -m "Configure Git LFS"
```

## Important Notes

1. **Never commit data files to Git** - They are excluded for good reason
2. **Data files are local only** - Each user maintains their own copy
3. **Reproducibility is maintained** through documented patient IDs and extraction scripts
4. **For thesis/publication** - Dataset availability should be mentioned in the methods section

## Questions?

If you need access to the dataset or have questions about data management, please refer to:

- `DATA_EXTRACTION_GUIDE.md` for detailed extraction instructions
- `PATIENT_SELECTION_STRATEGY.md` for patient selection rationale
