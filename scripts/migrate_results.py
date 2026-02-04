#!/usr/bin/env python3
"""
Migrate Evaluation Results to Versioned Structure

This script migrates existing evaluation results from the legacy format
(evaluation/results.npy) to the new versioned directory structure.

Usage:
    python scripts/migrate_results.py \
        --legacy-results evaluation/results.npy \
        --dataset-version n02_patients \
        --output-dir results/n02_patients
"""

import argparse
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


def load_legacy_results(results_path: Path) -> Dict[str, Any]:
    """
    Load legacy .npy results file.
    
    Args:
        results_path: Path to results.npy
        
    Returns:
        Dictionary containing results
    """
    results = np.load(results_path, allow_pickle=True).item()
    return results


def extract_patient_ids(results: Dict[str, Any]) -> list:
    """
    Extract patient IDs from results.
    
    Args:
        results: Legacy results dictionary
        
    Returns:
        Sorted list of patient IDs
    """
    if 'per_patient' in results:
        return sorted(results['per_patient'].keys())
    return []


def create_metadata(
    dataset_version: str,
    patient_ids: list,
    results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create metadata.json content.
    
    Args:
        dataset_version: Version identifier (e.g., "n02_patients")
        patient_ids: List of patient IDs
        results: Legacy results dictionary
        
    Returns:
        Metadata dictionary
    """
    budgets = results.get('budgets', [])
    
    return {
        "dataset_version": dataset_version,
        "num_patients": len(patient_ids),
        "patient_ids": patient_ids,
        "data_source": "data/processed",
        "extraction_date": "unknown",
        "evaluation_date": datetime.now().isoformat(),
        "model_checkpoint": "models/nnunet_brats_fold0.pth",
        "budgets_evaluated": [float(b) for b in budgets],
        "random_seed": None,
        "notes": "Migrated from legacy results.npy format"
    }


def create_dice_scores_csv(
    patient_ids: list,
    strategy: str,
    results: Dict[str, Any],
    output_path: Path
):
    """
    Create dice_scores.csv for a strategy.
    
    Args:
        patient_ids: List of patient IDs
        strategy: Strategy name
        results: Legacy results dictionary
        output_path: Path to output CSV
    """
    rows = []
    
    budgets = results.get('budgets', [])
    per_patient = results.get('per_patient', {})
    
    for patient_id in patient_ids:
        patient_data = per_patient.get(patient_id, {})
        strategy_data = patient_data.get(strategy, {})
        
        for budget in budgets:
            dice_score = strategy_data.get(budget, None)
            
            if dice_score is not None:
                # Convert budget percentage to number of slices
                # Assuming ~155 slices per volume (BraTS standard)
                num_slices = int(budget * 155)
                
                rows.append({
                    'patient_id': patient_id,
                    'budget': budget,
                    'dice_score': float(dice_score),
                    'num_slices_corrected': num_slices
                })
    
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)


def create_summary_json(
    strategy: str,
    dataset_version: str,
    num_patients: int,
    results: Dict[str, Any],
    output_path: Path
):
    """
    Create summary.json for a strategy.
    
    Args:
        strategy: Strategy name
        dataset_version: Version identifier
        num_patients: Number of patients
        results: Legacy results dictionary
        output_path: Path to output JSON
    """
    budgets = results.get('budgets', [])
    aggregate = results.get('aggregate', {})
    strategy_agg = aggregate.get(strategy, {})
    
    mean_dice_by_budget = {}
    std_dice_by_budget = {}
    
    for budget in budgets:
        budget_stats = strategy_agg.get(budget, {})
        mean_dice_by_budget[str(budget)] = float(budget_stats.get('mean', 0.0))
        std_dice_by_budget[str(budget)] = float(budget_stats.get('std', 0.0))
    
    summary = {
        "strategy": strategy,
        "dataset_version": dataset_version,
        "num_patients": num_patients,
        "budgets": [float(b) for b in budgets],
        "mean_dice_by_budget": mean_dice_by_budget,
        "std_dice_by_budget": std_dice_by_budget
    }
    
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)


def create_comparison_csv(
    results: Dict[str, Any],
    output_path: Path
):
    """
    Create comparison.csv across all strategies.
    
    Args:
        results: Legacy results dictionary
        output_path: Path to output CSV
    """
    rows = []
    
    budgets = results.get('budgets', [])
    strategies = results.get('strategies', [])
    aggregate = results.get('aggregate', {})
    
    for strategy in strategies:
        strategy_agg = aggregate.get(strategy, {})
        
        for budget in budgets:
            budget_stats = strategy_agg.get(budget, {})
            
            rows.append({
                'strategy': strategy,
                'budget': float(budget),
                'mean_dice': float(budget_stats.get('mean', 0.0)),
                'std_dice': float(budget_stats.get('std', 0.0))
            })
    
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)


def migrate_results(
    legacy_results_path: Path,
    dataset_version: str,
    output_dir: Path
):
    """
    Migrate legacy results to new structure.
    
    Args:
        legacy_results_path: Path to legacy results.npy
        dataset_version: Version identifier (e.g., "n02_patients")
        output_dir: Output directory for migrated results
    """
    print(f"Loading legacy results from {legacy_results_path}...")
    results = load_legacy_results(legacy_results_path)
    
    # Extract patient IDs
    patient_ids = extract_patient_ids(results)
    print(f"Found {len(patient_ids)} patients")
    
    # Create output directory structure
    output_dir.mkdir(parents=True, exist_ok=True)
    
    strategies = results.get('strategies', [])
    for strategy in strategies:
        strategy_dir = output_dir / strategy.lower().replace(' ', '_').replace('-', '_')
        strategy_dir.mkdir(exist_ok=True)
    
    # Create metadata.json
    print("Creating metadata.json...")
    metadata = create_metadata(dataset_version, patient_ids, results)
    with open(output_dir / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Create patient_ids.txt
    print("Creating patient_ids.txt...")
    with open(output_dir / 'patient_ids.txt', 'w') as f:
        for patient_id in patient_ids:
            f.write(f"{patient_id}\n")
    
    # Create per-strategy files
    for strategy in strategies:
        strategy_name = strategy.lower().replace(' ', '_').replace('-', '_')
        strategy_dir = output_dir / strategy_name
        
        print(f"Creating files for strategy: {strategy}...")
        
        # dice_scores.csv
        create_dice_scores_csv(
            patient_ids,
            strategy,
            results,
            strategy_dir / 'dice_scores.csv'
        )
        
        # summary.json
        create_summary_json(
            strategy,
            dataset_version,
            len(patient_ids),
            results,
            strategy_dir / 'summary.json'
        )
    
    # Create comparison.csv
    print("Creating comparison.csv...")
    create_comparison_csv(results, output_dir / 'comparison.csv')
    
    print(f"\n✓ Migration complete: {output_dir}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Migrate legacy evaluation results to versioned structure'
    )
    parser.add_argument(
        '--legacy-results',
        type=Path,
        required=True,
        help='Path to legacy results.npy file'
    )
    parser.add_argument(
        '--dataset-version',
        type=str,
        required=True,
        help='Dataset version identifier (e.g., n02_patients)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        required=True,
        help='Output directory for migrated results'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.legacy_results.exists():
        print(f"Error: Legacy results file not found: {args.legacy_results}")
        return 1
    
    # Run migration
    migrate_results(
        args.legacy_results,
        args.dataset_version,
        args.output_dir
    )
    
    return 0


if __name__ == '__main__':
    exit(main())
