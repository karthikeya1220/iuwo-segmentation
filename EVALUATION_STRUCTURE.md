# Evaluation Directory Structure

## Overview

This document defines the directory layout and file naming conventions for storing evaluation results across different dataset sizes.

## Principles

1. **Isolation**: Each dataset size gets its own result directory
2. **Versioning**: Results are versioned by dataset size (N patients)
3. **Reproducibility**: Patient IDs are explicitly documented
4. **Comparability**: Identical evaluation code and metrics across versions

---

## Directory Layout

```
results/
├── n02_patients/                    # Original 2-patient results
│   ├── metadata.json                # Dataset metadata
│   ├── patient_ids.txt              # List of patient IDs used
│   ├── baseline/                    # Baseline (no interaction) results
│   │   ├── dice_scores.csv          # Per-patient Dice scores
│   │   └── summary.json             # Aggregate statistics
│   ├── random/                      # Random slice selection
│   │   ├── dice_scores.csv
│   │   └── summary.json
│   ├── uncertainty/                 # Uncertainty-only selection
│   │   ├── dice_scores.csv
│   │   └── summary.json
│   ├── impact/                      # Impact-only selection
│   │   ├── dice_scores.csv
│   │   └── summary.json
│   ├── iuwo/                        # IUWO (impact-weighted) selection
│   │   ├── dice_scores.csv
│   │   └── summary.json
│   └── comparison.csv               # Cross-strategy comparison
│
├── n15_patients/                    # New 15-patient results
│   ├── metadata.json
│   ├── patient_ids.txt
│   ├── baseline/
│   │   ├── dice_scores.csv
│   │   └── summary.json
│   ├── random/
│   │   ├── dice_scores.csv
│   │   └── summary.json
│   ├── uncertainty/
│   │   ├── dice_scores.csv
│   │   └── summary.json
│   ├── impact/
│   │   ├── dice_scores.csv
│   │   └── summary.json
│   ├── iuwo/
│   │   ├── dice_scores.csv
│   │   └── summary.json
│   └── comparison.csv
│
└── cross_dataset_comparison.csv     # Compare n02 vs n15 results
```

---

## File Naming Conventions

### 1. Result Directories

**Format**: `n{NN}_patients/`

- `NN`: Zero-padded patient count (e.g., `02`, `15`, `50`)
- Examples: `n02_patients/`, `n15_patients/`, `n100_patients/`

**Rationale**: Alphabetical sorting preserves chronological order

### 2. Strategy Subdirectories

**Fixed names** (must match original implementation):

- `baseline/` - No expert interaction
- `random/` - Random slice selection
- `uncertainty/` - Uncertainty-only selection
- `impact/` - Impact-only selection
- `iuwo/` - Impact-Weighted Uncertainty Optimization

**CRITICAL**: Do not rename or add new strategies without documentation

### 3. Per-Patient Dice Scores

**File**: `dice_scores.csv`

**Format**:

```csv
patient_id,budget,dice_score,num_slices_corrected
BraTS-GLI-00005-100,0,0.7234,0
BraTS-GLI-00005-100,5,0.8123,5
BraTS-GLI-00005-100,10,0.8456,10
BraTS-GLI-00005-101,0,0.6891,0
...
```

**Columns**:

- `patient_id`: BraTS patient identifier
- `budget`: Number of slices corrected (0 = baseline)
- `dice_score`: Final 3D Dice score after correction
- `num_slices_corrected`: Actual number of slices corrected (for validation)

### 4. Summary Statistics

**File**: `summary.json`

**Format**:

```json
{
  "strategy": "iuwo",
  "dataset_version": "n15_patients",
  "num_patients": 15,
  "budgets": [0, 5, 10, 15, 20],
  "mean_dice_by_budget": {
    "0": 0.7123,
    "5": 0.8234,
    "10": 0.8567,
    "15": 0.8789,
    "20": 0.8901
  },
  "std_dice_by_budget": {
    "0": 0.0456,
    "5": 0.0389,
    "10": 0.0312,
    "15": 0.0278,
    "20": 0.0245
  },
  "median_dice_by_budget": {...},
  "min_dice_by_budget": {...},
  "max_dice_by_budget": {...}
}
```

### 5. Metadata

**File**: `metadata.json`

**Format**:

```json
{
  "dataset_version": "n15_patients",
  "num_patients": 15,
  "patient_ids": [
    "BraTS-GLI-00005-100",
    "BraTS-GLI-00005-101",
    ...
  ],
  "data_source": "data/raw_subset",
  "extraction_date": "2026-02-04T18:31:33",
  "evaluation_date": "2026-02-04T19:00:00",
  "model_checkpoint": "models/nnunet_brats_fold0.pth",
  "budgets_evaluated": [0, 5, 10, 15, 20],
  "random_seed": null,
  "notes": "Dataset expansion from 2 to 15 patients. No algorithmic changes."
}
```

### 6. Patient ID List

**File**: `patient_ids.txt`

**Format** (one patient ID per line, sorted):

```
BraTS-GLI-00005-100
BraTS-GLI-00005-101
BraTS-GLI-00006-100
...
```

**Rationale**: Human-readable, git-friendly, easy to diff

### 7. Cross-Strategy Comparison

**File**: `comparison.csv`

**Format**:

```csv
strategy,budget,mean_dice,std_dice,median_dice,min_dice,max_dice
baseline,0,0.7123,0.0456,0.7234,0.6234,0.8123
random,5,0.7456,0.0423,0.7512,0.6456,0.8234
random,10,0.7789,0.0398,0.7845,0.6678,0.8456
uncertainty,5,0.7834,0.0412,0.7901,0.6789,0.8567
uncertainty,10,0.8123,0.0378,0.8189,0.7012,0.8789
impact,5,0.7912,0.0401,0.7978,0.6823,0.8612
impact,10,0.8234,0.0367,0.8301,0.7123,0.8901
iuwo,5,0.8012,0.0389,0.8078,0.6912,0.8678
iuwo,10,0.8345,0.0356,0.8412,0.7234,0.9012
```

---

## Versioning Rules

### When to Create a New Result Directory

Create a new `nXX_patients/` directory when:

1. Dataset size changes (e.g., 2 → 15 patients)
2. Patient set changes (even if size is the same)
3. Data preprocessing changes (e.g., different slicing axis)

### When NOT to Create a New Directory

Do NOT create a new directory when:

1. Re-running evaluation with identical data (overwrite existing)
2. Fixing bugs in evaluation code (update existing + document)
3. Adding new budgets to existing evaluation (append to existing)

### Backward Compatibility

**CRITICAL**: Never delete or modify old result directories.

If old results are invalid:

1. Create new directory with corrected results
2. Add `DEPRECATED.txt` to old directory explaining why
3. Update cross-dataset comparison to exclude deprecated results

---

## Cross-Dataset Comparison

**File**: `results/cross_dataset_comparison.csv`

**Format**:

```csv
dataset_version,strategy,budget,num_patients,mean_dice,std_dice
n02_patients,baseline,0,2,0.6234,0.0123
n02_patients,iuwo,10,2,0.7456,0.0234
n15_patients,baseline,0,15,0.7123,0.0456
n15_patients,iuwo,10,15,0.8345,0.0356
```

**Purpose**: Compare performance across dataset sizes to assess:

- Statistical stability (does ranking change with more data?)
- Effect size consistency (does IUWO advantage hold?)
- Variance reduction (does std decrease with more patients?)

---

## Reproducibility Checklist

Before running evaluation on new dataset:

- [ ] Create new `nXX_patients/` directory
- [ ] Copy patient IDs to `patient_ids.txt`
- [ ] Create `metadata.json` with dataset details
- [ ] Verify model checkpoint path is identical
- [ ] Verify budget list is identical
- [ ] Verify evaluation code is unchanged (git commit hash)
- [ ] Run all strategies with identical budgets
- [ ] Generate per-patient and summary results
- [ ] Update cross-dataset comparison
- [ ] Commit results to git with descriptive message

---

## Git Commit Message Template

```
Evaluation results: N={num_patients} patients

Dataset version: nXX_patients
Patient count: {num_patients}
Strategies evaluated: baseline, random, uncertainty, impact, iuwo
Budgets: {budget_list}
Model checkpoint: {checkpoint_path}
Evaluation date: {date}

Changes from previous evaluation:
- Dataset expanded from {old_n} to {new_n} patients
- No algorithmic changes
- No hyperparameter changes
```

---

## Example: Migrating from 2 to 15 Patients

### Step 1: Preserve Old Results

```bash
# Verify old results exist
ls results/n02_patients/

# Expected output:
# metadata.json
# patient_ids.txt
# baseline/
# random/
# uncertainty/
# impact/
# iuwo/
# comparison.csv
```

### Step 2: Create New Result Directory

```bash
mkdir -p results/n15_patients/{baseline,random,uncertainty,impact,iuwo}
```

### Step 3: Document Patient IDs

```bash
# Extract patient IDs from dataset
ls data/raw_subset/ | grep "BraTS-" | sort > results/n15_patients/patient_ids.txt
```

### Step 4: Create Metadata

```json
{
  "dataset_version": "n15_patients",
  "num_patients": 15,
  "patient_ids": [...],
  "data_source": "data/raw_subset",
  "extraction_date": "2026-02-04T18:31:33",
  "evaluation_date": "2026-02-04T19:00:00",
  "model_checkpoint": "models/nnunet_brats_fold0.pth",
  "budgets_evaluated": [0, 5, 10, 15, 20],
  "random_seed": null,
  "notes": "Dataset expansion from 2 to 15 patients. No algorithmic changes."
}
```

### Step 5: Run Evaluation

```bash
# Run evaluation script (to be created)
python scripts/run_evaluation.py \
  --data-dir data/raw_subset \
  --output-dir results/n15_patients \
  --budgets 0 5 10 15 20
```

### Step 6: Verify Comparability

```bash
# Compare file structures
diff <(ls results/n02_patients/) <(ls results/n15_patients/)

# Should show only metadata differences, not structural changes
```

---

## Anti-Gravity Compliance

✓ **No hyperparameter changes** (budgets, thresholds identical)  
✓ **No retraining** (same model checkpoint)  
✓ **No cherry-picking** (all patients in dataset evaluated)  
✓ **Reproducibility** (patient IDs, metadata, git commits)  
✓ **Comparability** (identical directory structure and file formats)  
✓ **Versioning** (isolated result directories, no overwriting)
