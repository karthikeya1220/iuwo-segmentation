"""
Phase 3.1 — Frozen Segmentation Backbone

INFERENCE ONLY - NO TRAINING

This package provides a frozen segmentation model wrapper for inference-only operation.

Author: Research Prototype
Date: 2026-02-02
"""

from models.backbone.frozen_model import FrozenSegmentationModel, load_frozen_model
from models.backbone.simple_unet import SimpleUNet

__all__ = [
    "FrozenSegmentationModel",
    "load_frozen_model",
    "SimpleUNet",
]

__version__ = "3.0.0"  # Phase 3 complete
