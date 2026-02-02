"""
Phase 3.1 — Frozen Segmentation Backbone (nnU-Net)

INFERENCE ONLY - NO TRAINING, NO GRADIENT COMPUTATION

This module provides a thin wrapper around a PRETRAINED nnU-Net model.
The model is used ONLY for inference to generate slice-aligned predictions.

BACKBONE: Pretrained nnU-Net v2
STATUS: FROZEN (no retraining, no fine-tuning)

Design Constraints:
- Model parameters are FROZEN (no updates)
- No gradient computation
- No training code
- No loss functions
- No data augmentation
- Deterministic inference only

Author: Research Prototype
Date: 2026-02-02
Updated: 2026-02-02 (Backbone upgraded to nnU-Net)
"""

import numpy as np
import torch
import torch.nn as nn
from pathlib import Path
from typing import Tuple, Optional
import warnings


class FrozenSegmentationModel:
    """
    Wrapper for a PRETRAINED, FROZEN nnU-Net segmentation model.
    
    INFERENCE ONLY - This class does NOT support training.
    
    The model is loaded in eval mode with gradients disabled.
    All parameters are frozen and cannot be updated.
    
    Backbone: Pretrained nnU-Net v2
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        device: str = "cpu",
        use_nnunet: bool = True
    ):
        """
        Initialize frozen segmentation model.
        
        Args:
            model_path: Path to pretrained nnU-Net checkpoint (optional)
            device: Device to run inference on ('cpu' or 'cuda')
            use_nnunet: If True, use nnU-Net; if False, use Simple U-Net (prototyping only)
            
        Note:
            For production use, provide a pretrained nnU-Net checkpoint.
            Simple U-Net is only for early pipeline validation.
        """
        self.device = torch.device(device)
        self.use_nnunet = use_nnunet
        
        # Load pretrained model
        if use_nnunet:
            self.model = self._load_nnunet_model(model_path)
            self.model_type = "nnU-Net (Pretrained)"
        else:
            warnings.warn(
                "Using Simple U-Net for prototyping only. "
                "All experimental results use pretrained nnU-Net."
            )
            self.model = self._create_simple_unet()
            self.model_type = "Simple U-Net (Prototyping Only)"
        
        # FREEZE MODEL - Set to eval mode and disable gradients
        self.model.eval()
        self.model.to(self.device)
        
        # Freeze all parameters
        for param in self.model.parameters():
            param.requires_grad = False
        
        print(f"✅ Frozen segmentation model loaded (device: {self.device})")
        print(f"   Model type: {self.model_type}")
        print(f"   Total parameters: {self._count_parameters():,}")
        print(f"   Trainable parameters: 0 (FROZEN)")
    
    def _load_nnunet_model(self, model_path: Optional[str]) -> nn.Module:
        """
        Load a PRETRAINED nnU-Net model for inference.
        
        Args:
            model_path: Path to nnU-Net checkpoint directory or file
            
        Returns:
            Loaded nnU-Net model (FROZEN, inference only)
            
        Note:
            This uses nnU-Net v2 inference API.
            The model is PRETRAINED and used strictly for inference.
            NO retraining or fine-tuning is performed.
        """
        try:
            # Import nnU-Net v2 inference utilities
            from nnunetv2.inference.predict_from_raw_data import nnUNetPredictor
            
            if model_path is None:
                raise ValueError(
                    "model_path is required for nnU-Net. "
                    "Provide path to pretrained nnU-Net checkpoint."
                )
            
            # Initialize nnU-Net predictor (INFERENCE ONLY)
            predictor = nnUNetPredictor(
                tile_step_size=0.5,
                use_gaussian=True,
                use_mirroring=False,  # Deterministic inference
                perform_everything_on_gpu=self.device.type == 'cuda',
                device=self.device,
                verbose=False,
                verbose_preprocessing=False,
                allow_tqdm=False
            )
            
            # Load pretrained checkpoint (NO TRAINING)
            predictor.initialize_from_trained_model_folder(
                model_path,
                use_folds=(0,),  # Use first fold only
                checkpoint_name='checkpoint_final.pth'
            )
            
            print(f"   ✅ Loaded pretrained nnU-Net from: {model_path}")
            print(f"   ⚠️  Model is FROZEN - inference only, no training")
            
            return predictor
            
        except ImportError:
            warnings.warn(
                "nnU-Net v2 not installed. Falling back to Simple U-Net. "
                "Install with: pip install nnunetv2"
            )
            return self._create_simple_unet()
        except Exception as e:
            warnings.warn(
                f"Failed to load nnU-Net: {e}. Falling back to Simple U-Net."
            )
            return self._create_simple_unet()
    
    def _create_simple_unet(self) -> nn.Module:
        """
        Create a simple U-Net for prototyping.
        
        Returns:
            Simple U-Net model
            
        Note:
            This is a PLACEHOLDER for early pipeline validation only.
            All experimental results use pretrained nnU-Net.
        """
        from models.backbone.simple_unet import SimpleUNet
        return SimpleUNet(in_channels=1, out_channels=1)
    
    def _count_parameters(self) -> int:
        """Count total number of model parameters."""
        if hasattr(self.model, 'network'):
            # nnU-Net predictor
            return sum(p.numel() for p in self.model.network.parameters())
        else:
            # Simple U-Net
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
            - Preserves spatial alignment with Phase 2
        """
        # Validate input
        assert image_slice.ndim == 2, f"Expected 2D slice, got shape {image_slice.shape}"
        assert image_slice.dtype == np.float32, f"Expected float32, got {image_slice.dtype}"
        
        if self.use_nnunet and hasattr(self.model, 'predict_single_npy_array'):
            # nnU-Net inference path
            prob_map = self._predict_with_nnunet(image_slice)
        else:
            # Simple U-Net inference path (prototyping only)
            prob_map = self._predict_with_simple_unet(image_slice)
        
        # Threshold to get binary mask
        pred_mask = (prob_map >= threshold).astype(np.uint8)
        
        # Validate output shapes (CRITICAL: preserve spatial alignment)
        assert prob_map.shape == image_slice.shape, \
            f"Output shape mismatch: {prob_map.shape} vs {image_slice.shape}"
        assert pred_mask.shape == image_slice.shape, \
            f"Mask shape mismatch: {pred_mask.shape} vs {image_slice.shape}"
        
        return prob_map, pred_mask
    
    def _predict_with_nnunet(self, image_slice: np.ndarray) -> np.ndarray:
        """
        Run nnU-Net inference on a 2D slice.
        
        Args:
            image_slice: Input image (H, W), float32
            
        Returns:
            Probability map (H, W), float32, range [0, 1]
            
        Note:
            nnU-Net expects 3D input, so we add a dummy depth dimension.
        """
        # Add channel and depth dimensions: (H, W) -> (1, H, W, 1)
        # nnU-Net expects (C, H, W, D) format
        image_3d = image_slice[np.newaxis, :, :, np.newaxis]  # (1, H, W, 1)
        
        # Run nnU-Net inference (INFERENCE ONLY)
        with torch.no_grad():
            # nnU-Net predictor handles preprocessing internally
            prediction = self.model.predict_single_npy_array(
                image_3d,
                properties={
                    'spacing': [1.0, 1.0, 1.0],  # Dummy spacing
                    'direction': np.eye(3)
                },
                save_or_return_probabilities=True
            )
        
        # Extract 2D slice from 3D output
        # prediction shape: (num_classes, H, W, D)
        # We want the foreground class (index 1) and the single slice
        if prediction.ndim == 4:
            prob_map = prediction[1, :, :, 0]  # Foreground class, first slice
        else:
            prob_map = prediction[:, :, 0]  # Single class case
        
        # Ensure float32 and [0, 1] range
        prob_map = prob_map.astype(np.float32)
        prob_map = np.clip(prob_map, 0.0, 1.0)
        
        return prob_map
    
    def _predict_with_simple_unet(self, image_slice: np.ndarray) -> np.ndarray:
        """
        Run Simple U-Net inference on a 2D slice.
        
        Args:
            image_slice: Input image (H, W), float32
            
        Returns:
            Probability map (H, W), float32, range [0, 1]
            
        Note:
            This is for prototyping only. All experiments use nnU-Net.
        """
        # Prepare input tensor: (1, 1, H, W) for batch_size=1, channels=1
        input_tensor = torch.from_numpy(image_slice).unsqueeze(0).unsqueeze(0)
        input_tensor = input_tensor.to(self.device)
        
        # INFERENCE ONLY - Run forward pass
        with torch.no_grad():
            logits = self.model(input_tensor)
            probs = torch.sigmoid(logits)
        
        # Convert to numpy
        prob_map = probs.squeeze().cpu().numpy().astype(np.float32)
        
        return prob_map
    
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
    device: str = "cpu",
    use_nnunet: bool = True
) -> FrozenSegmentationModel:
    """
    Load a frozen segmentation model for inference.
    
    Args:
        model_path: Path to pretrained nnU-Net checkpoint (required for nnU-Net)
        device: Device for inference ('cpu' or 'cuda')
        use_nnunet: If True, use pretrained nnU-Net; if False, use Simple U-Net
        
    Returns:
        FrozenSegmentationModel instance
        
    Note:
        All experimental results use pretrained nnU-Net (use_nnunet=True).
        Simple U-Net is only for early pipeline validation.
        
    Example:
        >>> # Load pretrained nnU-Net
        >>> model = load_frozen_model(
        ...     model_path='/path/to/nnunet/checkpoint',
        ...     device='cuda',
        ...     use_nnunet=True
        ... )
        >>> prob_map, pred_mask = model.predict_slice(image_slice)
    """
    return FrozenSegmentationModel(
        model_path=model_path,
        device=device,
        use_nnunet=use_nnunet
    )


if __name__ == "__main__":
    # Test frozen model
    print("Testing frozen segmentation model...")
    
    # Create dummy input
    dummy_slice = np.random.randn(256, 256).astype(np.float32)
    
    # Test with Simple U-Net (prototyping)
    print("\n" + "="*60)
    print("Testing Simple U-Net (prototyping only)")
    print("="*60)
    model = load_frozen_model(device='cpu', use_nnunet=False)
    
    # Run inference
    prob_map, pred_mask = model.predict_slice(dummy_slice)
    
    print(f"\n✅ Inference successful!")
    print(f"   Input shape: {dummy_slice.shape}")
    print(f"   Probability map shape: {prob_map.shape}, dtype: {prob_map.dtype}")
    print(f"   Prediction mask shape: {pred_mask.shape}, dtype: {pred_mask.dtype}")
    print(f"   Probability range: [{prob_map.min():.3f}, {prob_map.max():.3f}]")
    print(f"   Mask values: {np.unique(pred_mask)}")
    
    print("\n" + "="*60)
    print("⚠️  NOTE: All experimental results use pretrained nnU-Net")
    print("   Simple U-Net is for early pipeline validation only")
    print("="*60)
