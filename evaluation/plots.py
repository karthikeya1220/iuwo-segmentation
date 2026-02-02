"""
Phase 8 — Evaluation Plotting

This module generates plots for evaluation results.

EVALUATION ONLY.

Author: Research Prototype
Date: 2026-02-02
"""

import numpy as np
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
from typing import Dict


def plot_dice_vs_budget(
    results_path: str,
    output_path: str
):
    """
    Generate Dice vs Budget plot including ALL strategies.
    
    Args:
        results_path: Path to evaluation/results.npy
        output_path: Path to save plot (e.g., evaluation/dice_vs_budget.png)
    """
    results_path = Path(results_path)
    output_path = Path(output_path)
    
    if not results_path.exists():
        print(f"❌ Results file not found: {results_path}")
        return
    
    # Load results
    results = np.load(results_path, allow_pickle=True).item()
    
    budgets = results["budgets"]
    strategies = results["strategies"]
    aggregate = results["aggregate"]
    
    # Plot setup
    plt.figure(figsize=(10, 6))
    
    # Colors and markers
    styles = {
        "No Correction": {"color": "gray", "marker": "o", "linestyle": "--"},
        "Random": {"color": "brown", "marker": "^", "linestyle": ":"},
        "Uniform": {"color": "orange", "marker": "v", "linestyle": ":"},
        "Uncertainty-Only": {"color": "blue", "marker": "s", "linestyle": "-"},
        "Impact-Only": {"color": "green", "marker": "D", "linestyle": "-"},
        "IWUO": {"color": "red", "marker": "*", "linestyle": "-", "linewidth": 2}
    }
    
    # Convert budgets to percentages for x-axis
    x_values = [b * 100 for b in budgets]
    
    for strat in strategies:
        if strat not in aggregate:
            continue
        
        means = []
        stds = []
        
        for b in budgets:
            if b in aggregate[strat]:
                means.append(aggregate[strat][b]["mean"])
                stds.append(aggregate[strat][b]["std"])
            else:
                means.append(np.nan)
                stds.append(np.nan)
        
        style = styles.get(strat, {})
        
        plt.errorbar(
            x_values,
            means,
            yerr=stds,
            label=strat,
            capsize=4,
            alpha=0.8,
            **style
        )
    
    plt.title("Dice Score vs. Expert Budget", fontsize=14)
    plt.xlabel("Budget (% of slices)", fontsize=12)
    plt.ylabel("Dice Similarity Coefficient (DSC)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='best', fontsize=10)
    plt.tight_layout()
    
    # Save plot
    plt.savefig(output_path, dpi=300)
    print(f"✅ Plot saved to: {output_path}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Generate evaluation plots")
    parser.add_argument("--results_file", default="evaluation/results.npy", help="Input results file")
    parser.add_argument("--output_file", default="evaluation/dice_vs_budget.png", help="Output plot file")
    
    args = parser.parse_args()
    
    plot_dice_vs_budget(args.results_file, args.output_file)


if __name__ == "__main__":
    main()
