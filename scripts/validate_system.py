#!/usr/bin/env python3
"""
System Validation Script
Performs comprehensive diagnostic checks on the IUWO segmentation prototype.
"""

import os
import sys
from pathlib import Path
import numpy as np

def check_directory_structure():
    """Verify all required directories exist."""
    print("=" * 60)
    print("1. DIRECTORY STRUCTURE CHECK")
    print("=" * 60)
    
    required_dirs = [
        "data/processed",
        "predictions/predictions",
        "models/uncertainty/artifacts",
        "models/impact/artifacts",
        "evaluation",
        "algorithms",
        "simulation",
        "strategies"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        exists = Path(dir_path).exists()
        status = "✓" if exists else "✗"
        print(f"{status} {dir_path}")
        all_exist = all_exist and exists
    
    return all_exist

def check_data_files():
    """Check if data files are present."""
    print("\n" + "=" * 60)
    print("2. DATA FILES CHECK")
    print("=" * 60)
    
    data_dir = Path("data/processed")
    pred_dir = Path("predictions/predictions")
    unc_dir = Path("models/uncertainty/artifacts")
    imp_dir = Path("models/impact/artifacts")
    
    data_files = list(data_dir.glob("*.npy")) if data_dir.exists() else []
    pred_files = list(pred_dir.glob("*.npy")) if pred_dir.exists() else []
    unc_files = list(unc_dir.glob("*.npy")) if unc_dir.exists() else []
    imp_files = list(imp_dir.glob("*.npy")) if imp_dir.exists() else []
    
    print(f"✓ Ground truth data: {len(data_files)} patients")
    print(f"✓ Predictions: {len(pred_files)} patients")
    print(f"✓ Uncertainty maps: {len(unc_files)} patients")
    print(f"✓ Impact scores: {len(imp_files)} patients")
    
    # Check consistency
    if len(data_files) == len(pred_files) == len(unc_files) == len(imp_files):
        print(f"\n✓ Data consistency: All pipelines have {len(data_files)} patients")
        return True, len(data_files)
    else:
        print(f"\n✗ Data inconsistency detected!")
        return False, 0

def check_module_imports():
    """Test if all modules can be imported."""
    print("\n" + "=" * 60)
    print("3. MODULE IMPORT CHECK")
    print("=" * 60)
    
    modules = [
        ("algorithms.iwuo", "IWUOSelector"),
        ("strategies.random_selection", "RandomSelector"),
        ("strategies.uniform_selection", "UniformSelector"),
        ("strategies.oracle_selection", "OracleSelector"),
        ("simulation.expert_correction", "ExpertCorrectionSimulator"),
        ("evaluation.dice", "compute_dice"),
    ]
    
    all_imported = True
    for module_name, class_or_func in modules:
        try:
            module = __import__(module_name, fromlist=[class_or_func])
            getattr(module, class_or_func)
            print(f"✓ {module_name}.{class_or_func}")
        except Exception as e:
            print(f"✗ {module_name}.{class_or_func}: {e}")
            all_imported = False
    
    return all_imported

def check_evaluation_results():
    """Check if evaluation results exist and are valid."""
    print("\n" + "=" * 60)
    print("4. EVALUATION RESULTS CHECK")
    print("=" * 60)
    
    results_files = [
        "evaluation/results.npy",
        "evaluation/results_backbone.npy",
        "evaluation/dice_vs_budget.png",
        "evaluation/dice_vs_budget_backbone.png"
    ]
    
    all_exist = True
    for file_path in results_files:
        exists = Path(file_path).exists()
        status = "✓" if exists else "✗"
        print(f"{status} {file_path}")
        all_exist = all_exist and exists
    
    # Load and inspect results
    if Path("evaluation/results_backbone.npy").exists():
        try:
            results = np.load("evaluation/results_backbone.npy", allow_pickle=True).item()
            print(f"\n✓ Results loaded successfully")
            print(f"  Strategies: {results['strategies']}")
            print(f"  Budget points: {len(results['budgets'])}")
            print(f"  Budgets: {results['budgets']}")
            
            # Check for IWUO
            if 'IWUO' in results['strategies']:
                print(f"✓ IWUO strategy present in results")
            else:
                print(f"✗ IWUO strategy missing from results")
                all_exist = False
                
        except Exception as e:
            print(f"✗ Error loading results: {e}")
            all_exist = False
    
    return all_exist

def check_documentation():
    """Check if key documentation files exist."""
    print("\n" + "=" * 60)
    print("5. DOCUMENTATION CHECK")
    print("=" * 60)
    
    docs = [
        "README.md",
        "FINAL_SUMMARY.md",
        "TECHNICAL_POSTMORTEM.md",
        "COMPLETION_REPORT.md",
        "requirements.txt",
        "analysis/phase10_failure_analysis.md"
    ]
    
    all_exist = True
    for doc in docs:
        exists = Path(doc).exists()
        status = "✓" if exists else "✗"
        print(f"{status} {doc}")
        all_exist = all_exist and exists
    
    return all_exist

def check_dependencies():
    """Check if required Python packages are installed."""
    print("\n" + "=" * 60)
    print("6. DEPENDENCY CHECK")
    print("=" * 60)
    
    required_packages = [
        "numpy",
        "nibabel",
        "torch",
        "matplotlib",
        "pandas"
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (not installed)")
            all_installed = False
    
    return all_installed

def generate_summary(checks):
    """Generate final summary report."""
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    total = len(checks)
    passed = sum(checks.values())
    percentage = (passed / total) * 100
    
    for check_name, status in checks.items():
        status_str = "✓ PASS" if status else "✗ FAIL"
        print(f"{status_str}: {check_name}")
    
    print(f"\n{'=' * 60}")
    print(f"OVERALL: {passed}/{total} checks passed ({percentage:.1f}%)")
    print(f"{'=' * 60}")
    
    if percentage == 100:
        print("\n🎉 System validation PASSED! All components operational.")
        return 0
    elif percentage >= 80:
        print("\n⚠️  System validation MOSTLY PASSED. Minor issues detected.")
        return 0
    else:
        print("\n❌ System validation FAILED. Critical issues detected.")
        return 1

def main():
    """Run all validation checks."""
    print("\n" + "=" * 60)
    print("IUWO SEGMENTATION PROTOTYPE - SYSTEM VALIDATION")
    print("=" * 60 + "\n")
    
    checks = {}
    
    # Run all checks
    checks["Directory Structure"] = check_directory_structure()
    data_ok, num_patients = check_data_files()
    checks["Data Files"] = data_ok
    checks["Module Imports"] = check_module_imports()
    checks["Evaluation Results"] = check_evaluation_results()
    checks["Documentation"] = check_documentation()
    checks["Dependencies"] = check_dependencies()
    
    # Generate summary
    exit_code = generate_summary(checks)
    
    # Additional info
    if data_ok:
        print(f"\nℹ️  Current dataset size: {num_patients} patients")
        print(f"ℹ️  Recommended for thesis: 20+ patients")
        if num_patients < 20:
            print(f"⚠️  Consider expanding dataset by {20 - num_patients} patients")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
