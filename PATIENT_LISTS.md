# BraTS 2024 Patient Lists - Quick Reference

## Training Set (20 patients)

### Small Volume (6 patients)

```
BraTS-GLI-00005-100
BraTS-GLI-00005-101
BraTS-GLI-00006-100
BraTS-GLI-00006-101
BraTS-GLI-00020-100
BraTS-GLI-00020-101
```

### Medium Volume (8 patients)

```
BraTS-GLI-00027-100
BraTS-GLI-00027-101
BraTS-GLI-00033-100
BraTS-GLI-00033-101
BraTS-GLI-00046-100
BraTS-GLI-00046-101
BraTS-GLI-00060-100
BraTS-GLI-00060-101
```

### Large Volume (6 patients)

```
BraTS-GLI-00063-100
BraTS-GLI-00063-101
BraTS-GLI-00078-100
BraTS-GLI-00078-101
BraTS-GLI-00080-100
BraTS-GLI-00080-101
```

---

## Evaluation Set (3 patients)

```
BraTS-GLI-00008-103  # Medium volume, representative
BraTS-GLI-00009-100  # Small volume, sparse
BraTS-GLI-00085-100  # Large volume, dense
```

---

## All Patients (Combined List)

### Training (20)

```python
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
```

### Evaluation (3)

```python
EVALUATION_PATIENTS = [
    "BraTS-GLI-00008-103",
    "BraTS-GLI-00009-100",
    "BraTS-GLI-00085-100",
]
```

---

## Verification

**Total Patients:** 23  
**Training:** 20  
**Evaluation:** 3  
**Overlap:** None ✅

**Selection Method:** Deterministic (ground truth-based stratification)  
**Reproducibility:** Fully reproducible from patient IDs  
**Documentation:** See `PATIENT_SELECTION_STRATEGY.md`
