# Migration Verification Report

**Date**: 2026-02-04T18:47:11  
**Source**: `evaluation/results.npy`  
**Destination**: `results/n02_patients/`  
**Status**: ✓ COMPLETE

---

## Migration Summary

### Patients Migrated

- **Count**: 2
- **IDs**:
  - BraTS-GLI-00008-103
  - BraTS-GLI-00009-100

### Strategies Migrated

1. No Correction (baseline)
2. Random
3. Uniform
4. Uncertainty-Only
5. Impact-Only
6. IWUO

### Budgets Evaluated

- 0.05 (5%)
- 0.10 (10%)
- 0.20 (20%)
- 0.30 (30%)
- 0.50 (50%)

---

## Directory Structure Verification

✓ `results/n02_patients/metadata.json` - Created  
✓ `results/n02_patients/patient_ids.txt` - Created  
✓ `results/n02_patients/comparison.csv` - Created  
✓ `results/n02_patients/no_correction/` - Created  
✓ `results/n02_patients/random/` - Created  
✓ `results/n02_patients/uniform/` - Created  
✓ `results/n02_patients/uncertainty_only/` - Created  
✓ `results/n02_patients/impact_only/` - Created  
✓ `results/n02_patients/iwuo/` - Created  

### Per-Strategy Files

Each strategy directory contains:

- `dice_scores.csv` - Per-patient Dice scores
- `summary.json` - Aggregate statistics

---

## Sample Data Verification

### IWUO Strategy (Budget = 0.05)

**Patient**: BraTS-GLI-00008-103  
**Dice Score**: 0.0655  
**Slices Corrected**: 7  

**Patient**: BraTS-GLI-00009-100  
**Dice Score**: 0.2178  
**Slices Corrected**: 7  

**Mean**: 0.1416  
**Std**: 0.0762  

✓ Values match legacy results

---

## Legacy Archive

Original results archived to:

- `evaluation/legacy/results_n02.npy`
- `evaluation/legacy/results_backbone_n02.npy`
- `evaluation/legacy/README.md`

---

## Next Steps

1. ✓ Migration complete
2. ⏳ Prepare new dataset (15 patients)
3. ⏳ Re-run evaluation pipeline
4. ⏳ Generate cross-dataset comparison

---

**Migration Status**: VERIFIED AND COMPLETE
