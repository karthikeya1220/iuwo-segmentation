"""
Phase 3.3 — Baseline Slice Selection Strategies

This package provides non-optimized baseline strategies for slice selection.

Available strategies:
- RandomSelection: Select B slices uniformly at random
- UniformSelection: Select B slices at evenly-spaced intervals
- OracleSelection: Select B slices with highest GT error (UPPER BOUND ONLY)

Author: Research Prototype
Date: 2026-02-02
"""

from strategies.base_strategy import SliceSelectionStrategy
from strategies.random_selection import RandomSelection
from strategies.uniform_selection import UniformSelection
from strategies.oracle_selection import OracleSelection

__all__ = [
    "SliceSelectionStrategy",
    "RandomSelection",
    "UniformSelection",
    "OracleSelection",
]

__version__ = "3.0.0"  # Phase 3 complete
