"""
Phase 7 — Expert Correction Simulation

This package simulates PERFECT EXPERT CORRECTION on selected slices.

SIMULATION ONLY - No evaluation, no decision-making.

Modules:
    expert_correction: Core correction simulation logic

Usage:
    from simulation.expert_correction import apply_expert_correction
    
    corrected_data = apply_expert_correction(
        predictions_data=predictions_data,
        ground_truth_data=ground_truth_data,
        selected_slices=selected_slices
    )
"""

from simulation.expert_correction import (
    ExpertCorrectionSimulator,
    apply_expert_correction,
    apply_correction_for_patient
)

__all__ = [
    "ExpertCorrectionSimulator",
    "apply_expert_correction",
    "apply_correction_for_patient"
]
