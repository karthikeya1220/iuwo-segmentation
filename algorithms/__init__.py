"""
Phase 6 — Impact-Weighted Uncertainty Optimization (IWUO)

DECISION-MAKING ONLY - No evaluation, no correction simulation.

This package implements budget-constrained slice selection using IWUO.

Available components:
- IWUOSelector: IWUO decision algorithm
- select_slices_for_patient: Patient-level selection

Author: Research Prototype
Date: 2026-02-02
"""

from algorithms.iwuo import (
    IWUOSelector,
    select_slices_for_patient
)

__all__ = [
    "IWUOSelector",
    "select_slices_for_patient",
]

__version__ = "6.0.0"  # Phase 6 complete
