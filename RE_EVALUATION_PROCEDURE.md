# Re-Evaluation Procedure: Dataset Expansion

## **CONTEXT**

- **Current state**: IUWO prototype evaluated on 2 patients
- **New state**: Dataset expanded to 15 patients
- **Constraint**: No algorithmic changes, hyperparameters, or retraining allowed
- **Goal**: Re-run evaluation while preserving comparability

---

## **PROCEDURE OVERVIEW**

### **Phase 1: Preserve Existing Results**

Migrate existing 2-patient results to versioned structure.

### **Phase 2: Prepare New Dataset**

Verify 15-patient dataset is ready for evaluation.

### **Phase 3: Re-run Evaluation**

Execute identical evaluation pipeline on new dataset.

### **Phase 4: Cross-Dataset Comparison**

Compare results across dataset sizes.

---

## **PHASE 1: PRESERVE EXISTING RESULTS**

### **Step 1.1: Migrate Legacy Results**

```bash
# Create results directory structure
mkdir -p results

# Migrate existing 2-patient results
python scripts/migrate_results.py \
    --legacy-results evaluation/results.npy \
    --dataset-version n02_patients \
    --output-dir results/n02_patients
```

**Expected output**:

```
results/n02_patients/
├── metadata.json
├── patient_ids.txt
├── no_correction/
│   ├── dice_scores.csv
│   └── summary.json
├── random/
│   ├── dice_scores.csv
│   └── summary.json
├── uniform/
│   ├── dice_scores.csv
│   └── summary.json
├── uncertainty_only/
│   ├── dice_scores.csv
│   └── summary.json
├── impact_only/
│   ├── dice_scores.csv
│   └── summary.json
├── iwuo/
│   ├── dice_scores.csv
│   └── summary.json
└── comparison.csv
```

### **Step 1.2: Verify Migration**

```bash
# Check patient count
cat results/n02_patients/metadata.json | grep "num_patients"
# Expected: "num_patients": 2

# Check patient IDs
cat results/n02_patients/patient_ids.txt
# Expected: 2 patient IDs

# Check strategies
ls results/n02_patients/
# Expected: 6 strategy directories + metadata files
```

### **Step 1.3: Archive Legacy Results**

```bash
# Create archive directory
mkdir -p evaluation/legacy

# Move legacy files (keep as backup)
cp evaluation/results.npy evaluation/legacy/results_n02.npy
cp evaluation/results_backbone.npy evaluation/legacy/results_backbone_n02.npy

# Add README
cat > evaluation/legacy/README.md << 'EOF'
# Legacy Results Archive

This directory contains original evaluation results in .npy format.

These have been migrated to the versioned structure in `results/`.

**Do not delete** - kept for reproducibility verification.
EOF
```

---

## **PHASE 2: PREPARE NEW DATASET**

### **Step 2.1: Verify Dataset Extraction**

```bash
# Verify 15 patients extracted
python scripts/validate_dataset.py \
    --data-dir data/raw_subset \
    --expected-n 15

# Expected: ✓ Dataset validation PASSED
```

### **Step 2.2: Document Patient IDs**

```bash
# Create results directory for new evaluation
mkdir -p results/n15_patients

# Extract patient IDs
ls data/raw_subset/ | grep "BraTS-" | sort > results/n15_patients/patient_ids.txt

# Verify count
wc -l results/n15_patients/patient_ids.txt
# Expected: 15
```

### **Step 2.3: Create Metadata Template**

```bash
cat > results/n15_patients/metadata.json << 'EOF'
{
  "dataset_version": "n15_patients",
  "num_patients": 15,
  "patient_ids": [],
  "data_source": "data/raw_subset",
  "extraction_date": "2026-02-04T18:31:33",
  "evaluation_date": null,
  "model_checkpoint": "models/nnunet_brats_fold0.pth",
  "budgets_evaluated": [0.05, 0.10, 0.20, 0.30, 0.50],
  "random_seed": null,
  "notes": "Dataset expansion from 2 to 15 patients. No algorithmic changes."
}
EOF

# Populate patient_ids from file
python -c "
import json
with open('results/n15_patients/patient_ids.txt') as f:
    patient_ids = [line.strip() for line in f]
with open('results/n15_patients/metadata.json') as f:
    metadata = json.load(f)
metadata['patient_ids'] = patient_ids
with open('results/n15_patients/metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)
"
```

---

## **PHASE 3: RE-RUN EVALUATION**

### **Step 3.1: Verify Evaluation Code Unchanged**

```bash
# Check git status of evaluation code
git log --oneline -1 evaluation/evaluate_strategies.py

# Verify no uncommitted changes
git diff evaluation/evaluate_strategies.py
# Expected: no output (no changes)
```

### **Step 3.2: Run Evaluation Pipeline**

**CRITICAL**: Use identical parameters as original evaluation.

```bash
# Run evaluation on 15 patients
python evaluation/evaluate_strategies.py \
    --predictions_dir predictions/predictions \
    --ground_truth_dir data/raw_subset \
    --uncertainty_dir models/uncertainty \
    --impact_dir models/impact \
    --output_file results/n15_patients/results_raw.npy
```

**Expected duration**: ~5-10 minutes for 15 patients

### **Step 3.3: Convert to Versioned Format**

```bash
# Migrate new results to structured format
python scripts/migrate_results.py \
    --legacy-results results/n15_patients/results_raw.npy \
    --dataset-version n15_patients \
    --output-dir results/n15_patients
```

### **Step 3.4: Verify Result Structure**

```bash
# Check directory structure
ls results/n15_patients/

# Expected output:
# metadata.json
# patient_ids.txt
# no_correction/
# random/
# uniform/
# uncertainty_only/
# impact_only/
# iwuo/
# comparison.csv
# results_raw.npy (legacy format, kept for backup)
```

---

## **PHASE 4: CROSS-DATASET COMPARISON**

### **Step 4.1: Generate Cross-Dataset Comparison**

```bash
python scripts/compare_datasets.py \
    --dataset-dirs results/n02_patients results/n15_patients \
    --output results/cross_dataset_comparison.csv
```

**Note**: This script needs to be created. Template below.

### **Step 4.2: Verify Comparability**

Check that:

1. Strategy names match across datasets
2. Budget values match across datasets
3. File structures are identical

```bash
# Compare strategy names
diff <(ls results/n02_patients/ | grep -v ".csv" | grep -v ".json" | grep -v ".txt" | grep -v ".npy") \
     <(ls results/n15_patients/ | grep -v ".csv" | grep -v ".json" | grep -v ".txt" | grep -v ".npy")

# Expected: no output (identical)

# Compare budgets
diff <(jq -r '.budgets_evaluated[]' results/n02_patients/metadata.json) \
     <(jq -r '.budgets_evaluated[]' results/n15_patients/metadata.json)

# Expected: no output (identical)
```

### **Step 4.3: Statistical Comparison**

```bash
# Generate statistical comparison report
python scripts/statistical_comparison.py \
    --baseline results/n02_patients \
    --expanded results/n15_patients \
    --output results/statistical_comparison.md
```

**Note**: This script needs to be created.

---

## **VERIFICATION CHECKLIST**

Before considering re-evaluation complete:

- [ ] Legacy results migrated to `results/n02_patients/`
- [ ] New dataset validated (15 patients, all files present)
- [ ] Patient IDs documented in `results/n15_patients/patient_ids.txt`
- [ ] Metadata created with correct parameters
- [ ] Evaluation code unchanged (verified via git)
- [ ] Evaluation completed successfully
- [ ] Results migrated to structured format
- [ ] Directory structures match between n02 and n15
- [ ] Strategy names match between n02 and n15
- [ ] Budget values match between n02 and n15
- [ ] Cross-dataset comparison generated
- [ ] All results committed to git

---

## **GIT COMMIT PROCEDURE**

### **Commit 1: Migrate Legacy Results**

```bash
git add results/n02_patients/
git add evaluation/legacy/
git commit -m "Migrate legacy evaluation results to versioned structure

- Created results/n02_patients/ with structured format
- Archived original results.npy in evaluation/legacy/
- No changes to evaluation code or algorithms
"
```

### **Commit 2: New Evaluation Results**

```bash
git add results/n15_patients/
git add results/cross_dataset_comparison.csv
git commit -m "Evaluation results: N=15 patients

Dataset version: n15_patients
Patient count: 15
Strategies evaluated: no_correction, random, uniform, uncertainty_only, impact_only, iwuo
Budgets: [0.05, 0.10, 0.20, 0.30, 0.50]
Model checkpoint: models/nnunet_brats_fold0.pth
Evaluation date: $(date -Iseconds)

Changes from previous evaluation:
- Dataset expanded from 2 to 15 patients
- No algorithmic changes
- No hyperparameter changes
- Identical evaluation protocol
"
```

---

## **ANTI-GRAVITY COMPLIANCE**

### **Constraints Verified**

✓ **No hyperparameter changes**

- Budgets: [0.05, 0.10, 0.20, 0.30, 0.50] (unchanged)
- IWUO alpha: 0.5 (unchanged)
- MC Dropout samples: unchanged

✓ **No retraining**

- Model checkpoint: `models/nnunet_brats_fold0.pth` (unchanged)
- No gradient updates
- No fine-tuning

✓ **No cherry-picking**

- All 15 patients in `data/raw_subset/` evaluated
- Deterministic patient selection (alphabetical)
- No patient exclusions

✓ **Reproducibility**

- Patient IDs documented
- Evaluation date timestamped
- Git commits with full context
- Identical evaluation code (verified via git)

✓ **Comparability**

- Identical directory structure
- Identical file formats
- Identical strategy names
- Identical budget values
- Cross-dataset comparison generated

---

## **EXPECTED OUTCOMES**

### **What Should Change**

- **Mean Dice scores**: May change due to different patient mix
- **Standard deviations**: Should decrease (more patients → more stable estimates)
- **Strategy rankings**: Should remain consistent if IUWO is robust

### **What Should NOT Change**

- **Evaluation code**: Identical
- **Model checkpoint**: Identical
- **Budgets**: Identical
- **Strategy definitions**: Identical
- **Metric computation**: Identical

### **Red Flags**

If any of the following occur, STOP and investigate:

- Strategy rankings reverse (e.g., IUWO becomes worse than random)
- Dice scores change by >0.2 (suggests data or code issue)
- File structures don't match between n02 and n15
- Evaluation code has uncommitted changes

---

## **TROUBLESHOOTING**

### **Issue: Evaluation fails on new patients**

**Possible causes**:

- Missing preprocessing artifacts
- Incompatible data format
- Insufficient disk space

**Solution**:

1. Verify all patients have required files (use `validate_dataset.py`)
2. Check preprocessing pipeline completed successfully
3. Verify disk space available

### **Issue: Results differ dramatically from n02**

**Possible causes**:

- Different patient difficulty distribution
- Code changes (unintended)
- Data corruption

**Solution**:

1. Verify evaluation code unchanged: `git diff evaluation/`
2. Verify model checkpoint unchanged: `md5sum models/nnunet_brats_fold0.pth`
3. Check patient IDs are correct
4. Re-run validation on dataset

### **Issue: Directory structures don't match**

**Possible causes**:

- Migration script error
- Manual file modifications

**Solution**:

1. Re-run migration script
2. Compare directory trees: `diff <(tree results/n02_patients) <(tree results/n15_patients)`
3. Verify all strategy directories exist

---

## **NEXT STEPS AFTER RE-EVALUATION**

1. **Update documentation**: Revise `BASELINE_DESCRIPTION.MD` with new patient count
2. **Update plots**: Regenerate Dice vs Budget plots with n15 data
3. **Statistical analysis**: Run significance tests comparing strategies
4. **Thesis integration**: Include cross-dataset comparison in results section

---

**Procedure Status**: READY FOR EXECUTION  
**Estimated Time**: 30-60 minutes  
**Risk Level**: LOW (all changes are additive, no deletions)
