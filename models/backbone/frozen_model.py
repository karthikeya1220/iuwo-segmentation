"""
Phase 3.1 — Frozen Segmentation Backbone

INFERENCE ONLY - NO TRAINING, NO GRADIENT COMPUTATION

This module provides a thin wrapper around a pretrained, frozen segmentation model.
The model is used ONLY for inference to generate slice-aligned predictions.

Design Constraints:
- Model parameters are FROZEN (no updates)
- No gradient computation
- No training code
- No loss functions
- No data augmentation
- Deterministic inference only

Author: Research Prototype
Date: 2026-02-02
"""

import numpy as np
import torch
import torch.nn as nn
from pathlib import Path
from typing import Tuple, Optional
import warnings


class FrozenSegmentationModel:
    """
    Wrapper for a pretrained, frozen segmentation model.
    
    INFERENCE ONLY - This class does NOT support training.
    
    The model is loaded in eval mode with gradients disabled.
    All parameters are frozen and cannot be updated.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        device: str = "cpu"
    ):
        """
        Initialize frozen segmentation model.
        
        Args:
            model_path: Path to pretrained model checkpoint (optional)
            device: Device to run inference on ('cpu' or 'cuda')
            
        Note:
            If model_path is None, uses a simple U-Net architecture.
            For production use, provide a pretrained nnU-Net checkpoint.
        """
        self.device = torch.device(device)
        
        # Load pretrained model
        if model_path is not None:
            self.model = self._load_pretrained_model(model_path)
        else:
            # Fallback: simple U-Net for prototyping
            warnings.warn(
                "No model_path provided. Using simple U-Net for prototyping. "
                "For production, use a pretrained nnU-Net model."
            )
            self.model = self._create_simple_unet()
        
        # FREEZE MODEL - Set to eval mode and disable gradients
        self.model.eval()
        self.model.to(self.device)
        
        # Freeze all parameters
        for param in self.model.parameters():
            param.requires_grad = False
        
        print(f"✅ Frozen segmentation model loaded (device: {self.device})")
        print(f"   Total parameters: {self._count_parameters():,}")
        print(f"   Trainable parameters: 0 (FROZEN)")
    
    def _load_pretrained_model(self, model_path: str) -> nn.Module:
        """
        Load a pretrained model from checkpoint.
        
        Args:
            model_path: Path to model checkpoint
            
        Returns:
            Loaded model
            
        Note:
            This is a placeholder for nnU-Net loading.
            In production, use nnU-Net's official loading mechanism.
        """
        # TODO: Replace with actual nnU-Net loading
        # from nnunet.inference.predict import load_model_and_checkpoint_files
        
        checkpoint = torch.load(model_path, map_location=self.device)
        model = self._create_simple_unet()  # Replace with nnU-Net architecture
        model.load_state_dict(checkpoint['state_dict'])
        
        return model
    
    def _create_simple_unet(self) -> nn.Module:
        """
        Create a simple U-Net for prototyping.
        
        Returns:
            Simple U-Net model
            
        Note:
            This is a PLACEHOLDER for prototyping only.
            In production, use a pretrained nnU-Net model.
        """
        from models.backbone.simple_unet import SimpleUNet
        return SimpleUNet(in_channels=1, out_channels=1)
    
    def _count_parameters(self) -> int:
        """Count total number of model parameters."""
        return sum(p.numel() for p in self.model.parameters())
    
    @torch.no_grad()  # CRITICAL: No gradient computation
    def predict_slice(
        self,
        image_slice: np.ndarray,
        threshold: float = 0.5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Run inference on a single 2D slice.
        
        INFERENCE ONLY - No gradients are computed.
        
        Args:
            image_slice: Input image (H, W), float32
            threshold: Threshold for binary mask (default: 0.5)
            
        Returns:
            prob_map: Probability map (H, W), float32, range [0, 1]
            pred_mask: Binary prediction (H, W), uint8, values {0, 1}
            
        Note:
            - Model is in eval mode
            - No gradient computation
            - Deterministic inference (no dropout)
        """
        # Validate input
        assert image_slice.ndim == 2, f"Expected 2D slice, got shape {image_slice.shape}"
        assert image_slice.dtype == np.float32, f"Expected float32, got {image_slice.dtype}"
        
        # Prepare input tensor
        # Shape: (1, 1, H, W) for batch_size=1, channels=1
        input_tensor = torch.from_numpy(image_slice).unsqueeze(0).unsqueeze(0)
        input_tensor = input_tensor.to(self.device)
        
        # INFERENCE ONLY - Run forward pass
        with torch.no_grad():  # Double-check no gradients
            logits = self.model(input_tensor)
            probs = torch.sigmoid(logits)
        
        # Convert to numpy
        prob_map = probs.squeeze().cpu().numpy().astype(np.float32)
        
        # Threshold to get binary mask
        pred_mask = (prob_map >= threshold).astype(np.uint8)
        
        # Validate output shapes
        assert prob_map.shape == image_slice.shape, \
            f"Output shape mismatch: {prob_map.shape} vs {image_slice.shape}"
        assert pred_mask.shape == image_slice.shape, \
            f"Mask shape mismatch: {pred_mask.shape} vs {image_slice.shape}"
        
        return prob_map, pred_mask
    
    def predict_volume(
        self,
        image_slices: list,
        threshold: float = 0.5,
        verbose: bool = True
    ) -> list:
        """
        Run inference on multiple slices (full volume).
        
        INFERENCE ONLY - No gradients are computed.
        
        Args:
            image_slices: List of 2D image slices
            threshold: Threshold for binary masks
            verbose: Print progress
            
        Returns:
            List of (prob_map, pred_mask) tuples
            
        Note:
            Processes slices sequentially to preserve slice alignment.
        """
        predictions = []
        
        for i, image_slice in enumerate(image_slices):
            if verbose and (i % 10 == 0 or i == len(image_slices) - 1):
                print(f"   Processing slice {i+1}/{len(image_slices)}")
            
            prob_map, pred_mask = self.predict_slice(image_slice, threshold)
            predictions.append((prob_map, pred_mask))
        
        return predictions


def load_frozen_model(
    model_path: Optional[str] = None,
    device: str = "cpu"
) -> FrozenSegmentationModel:
    """
    Load a frozen segmentation model for inference.
    
    Args:
        model_path: Path to pretrained checkpoint (optional)
        device: Device for inference ('cpu' or 'cuda')
        
    Returns:
        FrozenSegmentationModel instance
        
    Example:
        >>> model = load_frozen_model(device='cuda')
        >>> prob_map, pred_mask = model.predict_slice(image_slice)
    """
    return FrozenSegmentationModel(model_path=model_path, device=device)


if __name__ == "__main__":
    # Test frozen model
    print("Testing frozen segmentation model...")
    
    # Create dummy input
    dummy_slice = np.random.randn(256, 256).astype(np.float32)
    
    # Load model
    model = load_frozen_model(device='cpu')
    
    # Run inference
    prob_map, pred_mask = model.predict_slice(dummy_slice)
    
    print(f"\n✅ Inference successful!")
    print(f"   Input shape: {dummy_slice.shape}")
    print(f"   Probability map shape: {prob_map.shape}, dtype: {prob_map.dtype}")
    print(f"   Prediction mask shape: {pred_mask.shape}, dtype: {pred_mask.dtype}")
    print(f"   Probability range: [{prob_map.min():.3f}, {prob_map.max():.3f}]")
    print(f"   Mask values: {np.unique(pred_mask)}")
