"""
Phase 8 — Evaluation Package

This package implements evaluation logic for segmentation strategies.

Modules:
    dice: Dice score computation
    evaluate_strategies: Orchestration script for multi-strategy evaluation
    plots: Plotting utilities

Usage:
    from evaluation.dice import compute_volume_dice
    from evaluation.evaluate_strategies import evaluate_strategies
"""

from evaluation.dice import compute_dice, compute_volume_dice

__all__ = ["compute_dice", "compute_volume_dice"]
