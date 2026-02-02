"""
Phase 4 — Epistemic Uncertainty Estimation

UNCERTAINTY IS A SIGNAL, NOT A DECISION RULE.

This package computes predictive uncertainty using Monte Carlo Dropout.

Available components:
- MonteCarloDropoutUncertainty: Uncertainty estimator
- compute_uncertainty_for_patient: Patient-level uncertainty computation

Author: Research Prototype
Date: 2026-02-02
"""

from models.uncertainty.compute_uncertainty import (
    MonteCarloDropoutUncertainty,
    compute_uncertainty_for_patient
)

__all__ = [
    "MonteCarloDropoutUncertainty",
    "compute_uncertainty_for_patient",
]

__version__ = "4.0.0"  # Phase 4 complete
