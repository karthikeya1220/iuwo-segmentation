"""
Phase 5 — Impact Estimation

IMPACT IS A SIGNAL, NOT A DECISION RULE.

This package computes global volumetric impact of correcting each slice.

Available components:
- VolumetricImpactEstimator: Impact estimator
- compute_impact_for_patient: Patient-level impact computation

Author: Research Prototype
Date: 2026-02-02
"""

from models.impact.compute_impact import (
    VolumetricImpactEstimator,
    compute_impact_for_patient
)

__all__ = [
    "VolumetricImpactEstimator",
    "compute_impact_for_patient",
]

__version__ = "5.0.0"  # Phase 5 complete
