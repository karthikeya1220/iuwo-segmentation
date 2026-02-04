# Legacy Results Archive

This directory contains original evaluation results in `.npy` format.

## Files

- `results_n02.npy`: Original evaluation results for 2 patients
- `results_backbone_n02.npy`: Backbone-only evaluation results for 2 patients

## Migration

These results have been migrated to the versioned structure in `results/n02_patients/`.

The migration was performed on 2026-02-04 using `scripts/migrate_results.py`.

## Purpose

**Do not delete** - kept for reproducibility verification and backward compatibility.

If you need to verify the migration was correct, you can:

1. Load the legacy `.npy` file
2. Compare with the structured CSV/JSON files in `results/n02_patients/`
3. Verify patient IDs, budgets, and Dice scores match

## Format

Legacy format (Python pickle):

```python
{
  "budgets": [0.05, 0.10, ...],
  "strategies": ["No Correction", "Random", ...],
  "per_patient": {
      "<patient_id>": {
          "<strategy>": {
              "<budget>": dice_score
          }
      }
  },
  "aggregate": {
      "<strategy>": {
          "<budget>": {
              "mean": float,
              "std": float
          }
      }
  }
}
```

New format: See `results/n02_patients/` for CSV and JSON files.
