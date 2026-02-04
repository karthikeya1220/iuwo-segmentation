#!/usr/bin/env python3
"""
Complete Evaluation Pipeline for 15 Patients

This script runs the complete IUWO evaluation pipeline:
1. Phase 3: Generate predictions (frozen model inference)
2. Phase 4: Compute uncertainty (MC Dropout)
3. Phase 5: Compute impact (impact estimation)
4. Phase 8: Evaluate all strategies

This is a streamlined version that processes all patients sequentially.

Usage:
    python scripts/run_full_pipeline.py --patients 15
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """
    Run a command and report status.
    
    Args:
        cmd: Command as list of strings
        description: Description of what the command does
        
    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=False,
            text=True
        )
        print(f"\n✅ {description} - COMPLETE\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} - FAILED")
        print(f"Error: {e}\n")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Run complete IUWO evaluation pipeline"
    )
    parser.add_argument(
        "--patients",
        type=int,
        default=15,
        help="Number of patients to process"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=["cpu", "cuda"],
        help="Device for inference"
    )
    parser.add_argument(
        "--skip-predictions",
        action="store_true",
        help="Skip prediction generation (if already done)"
    )
    parser.add_argument(
        "--skip-uncertainty",
        action="store_true",
        help="Skip uncertainty computation (if already done)"
    )
    parser.add_argument(
        "--skip-impact",
        action="store_true",
        help="Skip impact computation (if already done)"
    )
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"IUWO Evaluation Pipeline — {args.patients} Patients")
    print(f"{'='*60}\n")
    
    # Phase 3: Generate Predictions
    if not args.skip_predictions:
        success = run_command(
            [
                "python", "models/backbone/generate_predictions.py",
                "--phase2_dir", "data/processed",
                "--output_dir", "predictions/predictions",
                "--device", args.device,
                "--max_patients", str(args.patients)
            ],
            "Phase 3: Generate Predictions"
        )
        if not success:
            print("❌ Pipeline failed at Phase 3")
            return 1
    else:
        print("\n⏭️  Skipping Phase 3 (predictions)")
    
    # Phase 4: Compute Uncertainty
    if not args.skip_uncertainty:
        success = run_command(
            [
                "python", "models/uncertainty/generate_uncertainty.py",
                "--phase2_dir", "data/processed",
                "--output_dir", "models/uncertainty/artifacts",
                "--device", args.device,
                "--num_samples", "20",
                "--max_patients", str(args.patients)
            ],
            "Phase 4: Compute Uncertainty"
        )
        if not success:
            print("❌ Pipeline failed at Phase 4")
            return 1
    else:
        print("\n⏭️  Skipping Phase 4 (uncertainty)")
    
    # Phase 5: Compute Impact
    if not args.skip_impact:
        success = run_command(
            [
                "python", "models/impact/generate_impact.py",
                "--predictions_dir", "predictions/predictions",
                "--ground_truth_dir", "data/processed",
                "--output_dir", "models/impact/artifacts",
                "--max_patients", str(args.patients)
            ],
            "Phase 5: Compute Impact"
        )
        if not success:
            print("❌ Pipeline failed at Phase 5")
            return 1
    else:
        print("\n⏭️  Skipping Phase 5 (impact)")
    
    # Phase 8: Evaluate Strategies
    success = run_command(
        [
            "python", "evaluation/evaluate_strategies.py",
            "--predictions_dir", "predictions/predictions",
            "--ground_truth_dir", "data/processed",
            "--uncertainty_dir", "models/uncertainty/artifacts",
            "--impact_dir", "models/impact/artifacts",
            "--output_file", "results/n15_patients/results_raw.npy"
        ],
        "Phase 8: Evaluate Strategies"
    )
    if not success:
        print("❌ Pipeline failed at Phase 8")
        return 1
    
    # Migrate results to structured format
    success = run_command(
        [
            "python", "scripts/migrate_results.py",
            "--legacy-results", "results/n15_patients/results_raw.npy",
            "--dataset-version", "n15_patients",
            "--output-dir", "results/n15_patients"
        ],
        "Migrate Results to Structured Format"
    )
    if not success:
        print("❌ Pipeline failed at result migration")
        return 1
    
    print(f"\n{'='*60}")
    print(f"✅ COMPLETE PIPELINE SUCCESS!")
    print(f"{'='*60}")
    print(f"\nResults saved to: results/n15_patients/")
    print(f"\nNext steps:")
    print(f"  1. Review results: cat results/n15_patients/comparison.csv")
    print(f"  2. Compare with n02: diff results/n02_patients/comparison.csv results/n15_patients/comparison.csv")
    print(f"  3. Generate plots: python evaluation/plots.py --results_file results/n15_patients/results_raw.npy")
    print(f"\n{'='*60}\n")
    
    return 0


if __name__ == "__main__":
    exit(main())
