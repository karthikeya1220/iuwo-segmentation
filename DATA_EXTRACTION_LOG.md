# Data Extraction Log

**Source:** `/Users/darshankarthikeya/Downloads/archive.zip`
**Destination:** `/Users/darshankarthikeya/brats_subset`
**Date:** 2026-02-03

## Commands Used

### 1. List Contents
```bash
unzip -l /Users/darshankarthikeya/Downloads/archive.zip | head -n 50
```

### 2. Extract Subset (2 Patients)
```bash
unzip -o /Users/darshankarthikeya/Downloads/archive.zip \
  "BraTS-GLI-00008-103/*seg.nii" \
  "BraTS-GLI-00008-103/*t2f.nii" \
  "BraTS-GLI-00009-100/*seg.nii" \
  "BraTS-GLI-00009-100/*t2f.nii" \
  -d /Users/darshankarthikeya/brats_subset
```

### 3. Post-Processing (Gzip & Rename)
```bash
# Compress
find /Users/darshankarthikeya/brats_subset -name "*.nii" -exec gzip {} \;

# Rename t2f -> flair (hyphen to underscore)
python3 -c "import os, glob; [os.rename(f, f.replace('t2f', 'flair').replace('-flair', '_flair').replace('-seg', '_seg')) for f in glob.glob('/Users/darshankarthikeya/brats_subset/*/*t2f.nii.gz') + glob.glob('/Users/darshankarthikeya/brats_subset/*/*seg.nii.gz')]"
```

### 4. Verification
```bash
ls -R /Users/darshankarthikeya/brats_subset
```

## Next Step: Bind to Phase 2 (Completed ✅)

Data successfully processed into Phase 2 artifacts:

```bash
python data/load_brats_axial.py \
  --brats_dir /Users/darshankarthikeya/brats_subset \
  --output_dir data/processed
```
