# BraTS Subset Extraction Usage Guide

## Basic Usage

```bash
python scripts/extract_subset.py \
    --archive /path/to/brats_dataset.zip \
    --n 10 \
    --output data/raw_subset/
```

## Arguments

- `--archive`: Path to BraTS ZIP archive (required)
- `--n`: Number of patients to extract (required)
- `--output`: Target directory (default: `data/raw_subset/`)

## Example: Extract 5 Patients

```bash
python scripts/extract_subset.py \
    --archive data/ASNR-MICCAI-BraTS2023-GLI-Challenge-TrainingData.zip \
    --n 5 \
    --output data/raw_subset/
```

## Output Structure

```
data/raw_subset/
├── BraTS-GLI-00000-000/
│   ├── BraTS-GLI-00000-000-t1c.nii.gz
│   ├── BraTS-GLI-00000-000-t1n.nii.gz
│   ├── BraTS-GLI-00000-000-t2f.nii.gz
│   ├── BraTS-GLI-00000-000-t2w.nii.gz
│   └── BraTS-GLI-00000-000-seg.nii.gz
├── BraTS-GLI-00001-000/
│   └── ...
├── EXTRACTION_LOG.txt
└── extraction.log
```

## Logs

1. **EXTRACTION_LOG.txt**: Summary of extracted patients
2. **extraction.log**: Detailed extraction process log

## Validation

The script automatically validates:

- ZIP archive integrity (before extraction)
- File completeness per patient (after extraction)
- Exit code 0 = success, 1 = failure

## Determinism

Patient selection is deterministic (alphabetical order).
Running the script multiple times with the same `--n` produces identical results.

## Memory Efficiency

- Does NOT load entire ZIP into memory
- Streams files on-demand
- Suitable for large archives (>100GB)

## Error Handling

- Corrupt archive → abort before extraction
- Missing patient files → log warning, continue
- Incomplete extraction → report in validation
- N exceeds available → clear error message
