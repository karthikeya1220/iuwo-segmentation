"""
Phase 8 — Evaluate Segmentation Strategies

This script evaluates expert correction strategies across multiple budgets.
It computes Dice scores for:
1. No Correction (Baseline)
2. Random Selection (Phase 3)
3. Uniform Selection (Phase 3)
4. Uncertainty-Only Selection (Phase 4)
5. Impact-Only Selection (Phase 5)
6. IWUO (Phase 6)

EVALUATION ONLY - No decision-making logic inside (uses existing modules).

Usage:
    python evaluation/evaluate_strategies.py \
        --predictions_dir predictions/predictions \
        --ground_truth_dir data/processed \
        --uncertainty_dir models/uncertainty \
        --impact_dir models/impact \
        --output_file evaluation/results.npy

Author: Research Prototype
Date: 2026-02-02
"""

import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from simulation.expert_correction import apply_expert_correction
from evaluation.dice import compute_volume_dice
from strategies.random_selection import RandomSelection
from strategies.uniform_selection import UniformSelection
from algorithms.iwuo import IWUOSelector


def get_patient_ids(directory: Path) -> List[str]:
    """Get list of patient IDs from .npy files in directory."""
    return sorted([f.stem for f in directory.glob("*.npy")])


def evaluate_strategies(
    predictions_dir: str,
    ground_truth_dir: str,
    uncertainty_dir: str,
    impact_dir: str,
    output_file: str,
    budgets: List[float] = [0.05, 0.10, 0.20, 0.30, 0.50],
    verbose: bool = True
):
    """
    Evaluate all strategies across budgets.
    
    Args:
        predictions_dir: Phase 3 predictions
        ground_truth_dir: Phase 2 ground truth
        uncertainty_dir: Phase 4 uncertainty artifacts
        impact_dir: Phase 5 impact artifacts
        output_file: Path to save results .npy
        budgets: List of budget percentages (0.0 to 1.0)
        verbose: Print progress
    """
    pred_path = Path(predictions_dir)
    gt_path = Path(ground_truth_dir)
    unc_path = Path(uncertainty_dir)
    imp_path = Path(impact_dir)
    output_path = Path(output_file)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get common patient IDs
    pred_ids = set(get_patient_ids(pred_path))
    gt_ids = set(get_patient_ids(gt_path))
    
    # Uncertainty/Impact IDs might be missing if not generated, handled gracefully
    unc_ids = set(get_patient_ids(unc_path))
    imp_ids = set(get_patient_ids(imp_path))
    
    # Intersect all required for advanced strategies
    # For baseline/random/uniform, only pred and gt needed
    # But for fair comparison, we only evaluate patients having ALL data
    patient_ids = sorted(list(pred_ids & gt_ids & unc_ids & imp_ids))
    
    if len(patient_ids) == 0:
        print("❌ No patients found with all required artifacts (predictions, GT, uncertainty, impact)")
        print(f"   Predictions: {len(pred_ids)}")
        print(f"   Ground Truth: {len(gt_ids)}")
        print(f"   Uncertainty: {len(unc_ids)}")
        print(f"   Impact: {len(imp_ids)}")
        # Fallback to just pred/gt for testing basics if advanced missing?
        # User requirement says "ALL strategies must be evaluated".
        # So we fail if artifacts missing.
        if verbose:
            print("   Available Pred IDs:", list(pred_ids)[:5])
            print("   Available Unc IDs:", list(unc_ids)[:5])
        return

    if verbose:
        print(f"\n{'='*60}")
        print(f"Evaluating Strategies")
        print(f"{'='*60}")
        print(f"Patients: {len(patient_ids)}")
        print(f"Budgets: {budgets}")
        print(f"{'='*60}\n")
    
    # Initialize strategies
    random_selector = RandomSelection(seed=42)
    uniform_selector = UniformSelection()
    iwuo_selector = IWUOSelector(alpha=0.5)
    uncertainty_selector = IWUOSelector(alpha=1.0)
    impact_selector = IWUOSelector(alpha=0.0)
    
    # Results structure
    results = {
        "budgets": budgets,
        "strategies": [
            "No Correction",
            "Random",
            "Uniform",
            "Uncertainty-Only",
            "Impact-Only",
            "IWUO"
        ],
        "per_patient": {}
    }
    
    for i, patient_id in enumerate(patient_ids, 1):
        if verbose:
            print(f"[{i}/{len(patient_ids)}] Processing {patient_id}...")
            
        results["per_patient"][patient_id] = {}
        for strat in results["strategies"]:
            results["per_patient"][patient_id][strat] = {}
        
        try:
            # Load data
            pred_data = np.load(pred_path / f"{patient_id}.npy", allow_pickle=True).item()
            gt_data = np.load(gt_path / f"{patient_id}.npy", allow_pickle=True).item()
            unc_data = np.load(unc_path / f"{patient_id}.npy", allow_pickle=True).item()
            imp_data = np.load(imp_path / f"{patient_id}.npy", allow_pickle=True).item()
            
            # Baseline (No Correction)
            baseline_result = compute_volume_dice(pred_data["slices"], gt_data["slices"])
            # Store baseline for all budgets (it's constant)
            for b_pct in budgets:
                results["per_patient"][patient_id]["No Correction"][b_pct] = baseline_result
            
            num_slices = len(pred_data["slices"])
            
            # Evaluate at each budget
            for b_pct in budgets:
                budget = int(round(num_slices * b_pct))
                
                if budget == 0:
                    # If budget rounds to 0, it's same as baseline
                    for strat in results["strategies"]:
                        if strat != "No Correction":
                            results["per_patient"][patient_id][strat][b_pct] = baseline_result
                    continue
                
                # 1. Random Selection
                rand_selected = random_selector.select(pred_data["slices"], budget)
                rand_corrected = apply_expert_correction(pred_data, gt_data, rand_selected)
                rand_dice = compute_volume_dice(rand_corrected["corrected_slices"], gt_data["slices"])
                results["per_patient"][patient_id]["Random"][b_pct] = rand_dice
                
                # 2. Uniform Selection
                uni_selected = uniform_selector.select(pred_data["slices"], budget)
                uni_corrected = apply_expert_correction(pred_data, gt_data, uni_selected)
                uni_dice = compute_volume_dice(uni_corrected["corrected_slices"], gt_data["slices"])
                results["per_patient"][patient_id]["Uniform"][b_pct] = uni_dice
                
                # 3. Uncertainty-Only (alpha=1.0)
                unc_selected = uncertainty_selector.select(unc_data, imp_data, budget)
                unc_corrected = apply_expert_correction(pred_data, gt_data, unc_selected)
                unc_dice = compute_volume_dice(unc_corrected["corrected_slices"], gt_data["slices"])
                results["per_patient"][patient_id]["Uncertainty-Only"][b_pct] = unc_dice
                
                # 4. Impact-Only (alpha=0.0)
                imp_selected = impact_selector.select(unc_data, imp_data, budget)
                imp_corrected = apply_expert_correction(pred_data, gt_data, imp_selected)
                imp_dice = compute_volume_dice(imp_corrected["corrected_slices"], gt_data["slices"])
                results["per_patient"][patient_id]["Impact-Only"][b_pct] = imp_dice
                
                # 5. IWUO (alpha=0.5)
                iwuo_selected = iwuo_selector.select(unc_data, imp_data, budget)
                iwuo_corrected = apply_expert_correction(pred_data, gt_data, iwuo_selected)
                iwuo_dice = compute_volume_dice(iwuo_corrected["corrected_slices"], gt_data["slices"])
                results["per_patient"][patient_id]["IWUO"][b_pct] = iwuo_dice
                
        except Exception as e:
            print(f"❌ Error processing {patient_id}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Compute aggregate stats
    if verbose:
        print("\nComputing aggregate statistics...")
        
    aggregate = {}
    for strat in results["strategies"]:
        aggregate[strat] = {}
        for b_pct in budgets:
            scores = []
            for pid in results["per_patient"]:
                if strat in results["per_patient"][pid] and b_pct in results["per_patient"][pid][strat]:
                    scores.append(results["per_patient"][pid][strat][b_pct])
            
            if scores:
                aggregate[strat][b_pct] = {
                    "mean": float(np.mean(scores)),
                    "std": float(np.std(scores)),
                    "count": len(scores)
                }
            else:
                aggregate[strat][b_pct] = {"mean": 0.0, "std": 0.0, "count": 0}
                
    results["aggregate"] = aggregate
    
    # Save results
    np.save(output_path, results)
    
    if verbose:
        print(f"\n✅ Evaluation complete!")
        print(f"   Results saved to: {output_path}")
        print("\nSummary (Mean Dice):")
        print(f"{'Strategy':<20} {'5%':<10} {'10%':<10} {'20%':<10} {'30%':<10} {'50%':<10}")
        print("-" * 70)
        
        for strat in results["strategies"]:
            row = f"{strat:<20} "
            for b_pct in budgets:
                if b_pct in aggregate[strat]:
                    # Format checking if budget exists in list to align with header
                    # The header assumes specific budgets, but robust code iterates budgets
                    pass
                
            # Assume budgets are standard for printing
            for b in [0.05, 0.10, 0.20, 0.30, 0.50]:
                if b in aggregate[strat]:
                    row += f"{aggregate[strat][b]['mean']:.4f}     "
                else:
                    row += "N/A        "
            print(row)


def main():
    parser = argparse.ArgumentParser(description="Evaluate segmentation strategies phase 8")
    parser.add_argument("--predictions_dir", default="predictions/predictions", help="Predictions directory")
    parser.add_argument("--ground_truth_dir", default="data/processed", help="Ground truth directory")
    parser.add_argument("--uncertainty_dir", default="models/uncertainty/artifacts", help="Uncertainty artifacts directory")
    parser.add_argument("--impact_dir", default="models/impact/artifacts", help="Impact artifacts directory")
    parser.add_argument("--output_file", default="evaluation/results.npy", help="Output results file")
    
    args = parser.parse_args()
    
    # Check if directories exist, if not try fallback defaults based on common issues
    # But user asked for specific flags
    
    evaluate_strategies(
        predictions_dir=args.predictions_dir,
        ground_truth_dir=args.ground_truth_dir,
        uncertainty_dir=args.uncertainty_dir,
        impact_dir=args.impact_dir,
        output_file=args.output_file
    )

if __name__ == "__main__":
    main()
