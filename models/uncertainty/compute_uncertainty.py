"""
Phase 4 — Epistemic Uncertainty Estimation

This module computes PREDICTIVE UNCERTAINTY for slice-level segmentation
predictions using Monte Carlo Dropout.

UNCERTAINTY IS A SIGNAL, NOT A DECISION RULE.

This phase does NOT include:
- Slice selection
- Budget constraints
- Optimization logic
- Impact estimation
- Expert correction
- Active learning

Design Rationale:
- Epistemic uncertainty captures model uncertainty
- Monte Carlo Dropout is well-established for frozen networks
- Uncertainty provides a signal for future decision-making (Phase 5+)

Author: Research Prototype
Date: 2026-02-02
"""

import numpy as np
import torch
import torch.nn as nn
from pathlib import Path
from typing import Tuple, Dict, List
import warnings


class MonteCarloDropoutUncertainty:
    """
    Epistemic uncertainty estimation using Monte Carlo Dropout.
    
    This class computes predictive uncertainty by performing multiple
    stochastic forward passes with dropout ENABLED at test time.
    
    Method: Monte Carlo Dropout (Gal & Ghahramani, 2016)
    
    Key Properties:
    - Epistemic uncertainty (model uncertainty)
    - No retraining required
    - Works with frozen models
    - Deterministic given fixed seed
    
    Note:
        Uncertainty is computed as a SIGNAL only.
        This phase does NOT use uncertainty for decision-making.
    """
    
    def __init__(
        self,
        model,
        num_samples: int = 20,
        dropout_rate: float = 0.1,
        seed: int = 42
    ):
        """
        Initialize Monte Carlo Dropout uncertainty estimator.
        
        Args:
            model: Frozen segmentation model (with dropout layers)
            num_samples: Number of stochastic forward passes (T)
            dropout_rate: Dropout probability for MC sampling
            seed: Random seed for reproducibility
            
        Note:
            The model must have dropout layers for MC sampling to work.
            If no dropout exists, uncertainty will be zero (deterministic).
        """
        self.model = model
        self.num_samples = num_samples
        self.dropout_rate = dropout_rate
        self.seed = seed
        
        # Set random seed for reproducibility
        torch.manual_seed(seed)
        np.random.seed(seed)
        
        print(f"✅ Monte Carlo Dropout Uncertainty Estimator initialized")
        print(f"   Number of samples (T): {num_samples}")
        print(f"   Dropout rate: {dropout_rate}")
        print(f"   Random seed: {seed}")
    
    def _enable_dropout(self):
        """
        Enable dropout layers for stochastic inference.
        
        Note:
            This enables dropout at TEST TIME for Monte Carlo sampling.
            Model remains frozen (no gradient computation).
        """
        # Handle FrozenSegmentationModel wrapper
        target_model = self.model.model if hasattr(self.model, 'model') else self.model
        
        if not hasattr(target_model, 'modules'):
            warnings.warn("Model does not strictly look like a PyTorch module. Dropout enabling might fail.")
            return

        for module in target_model.modules():
            if isinstance(module, nn.Dropout) or isinstance(module, nn.Dropout2d):
                module.train()  # Enable dropout
    
    def _disable_dropout(self):
        """Disable dropout layers (return to deterministic inference)."""
        # Handle FrozenSegmentationModel wrapper
        target_model = self.model.model if hasattr(self.model, 'model') else self.model
        
        if not hasattr(target_model, 'modules'):
            return

        for module in target_model.modules():
            if isinstance(module, nn.Dropout) or isinstance(module, nn.Dropout2d):
                module.eval()  # Disable dropout
    
    @torch.no_grad()  # CRITICAL: No gradient computation
    def compute_uncertainty(
        self,
        image_slice: np.ndarray,
        verbose: bool = False
    ) -> Tuple[np.ndarray, float]:
        """
        Compute epistemic uncertainty for a single slice.
        
        UNCERTAINTY IS A SIGNAL, NOT A DECISION RULE.
        
        Args:
            image_slice: Input image (H, W), float32
            verbose: Print progress
            
        Returns:
            uncertainty_map: Voxel-wise uncertainty (H, W), float32
            slice_uncertainty: Scalar uncertainty score, float
            
        Algorithm:
            1. Perform T stochastic forward passes with dropout enabled
            2. Compute mean probability map across samples
            3. Compute entropy as uncertainty measure
            4. Aggregate to slice-level uncertainty
            
        Note:
            - No gradients are computed
            - Model parameters remain frozen
            - Dropout is enabled only during sampling
            - Deterministic given fixed seed
        """
        # Validate input
        assert image_slice.ndim == 2, f"Expected 2D slice, got shape {image_slice.shape}"
        assert image_slice.dtype == np.float32, f"Expected float32, got {image_slice.dtype}"
        
        H, W = image_slice.shape
        
        # Prepare input tensor
        input_tensor = torch.from_numpy(image_slice).unsqueeze(0).unsqueeze(0)
        
        # Handle device placement for wrapper or module
        device = getattr(self.model, 'device', None)
        if device is None and hasattr(self.model, 'model'):
             device = getattr(self.model.model, 'device', None)
        
        # Fallback to checking parameters if device is still unknown but it is a module
        if device is None and isinstance(self.model, nn.Module):
             try:
                 device = next(self.model.parameters()).device
             except StopIteration:
                 pass
        
        if device:
            input_tensor = input_tensor.to(device)
        
        # Enable dropout for stochastic inference
        self._enable_dropout()
        
        # Collect predictions from T stochastic forward passes
        predictions = []
        
        for t in range(self.num_samples):
            if verbose and (t % 5 == 0 or t == self.num_samples - 1):
                print(f"      MC sample {t+1}/{self.num_samples}")
            
            # Stochastic forward pass (dropout enabled)
            with torch.no_grad():
                if hasattr(self.model, 'model'):
                    # Simple U-Net path
                    logits = self.model.model(input_tensor)
                    probs = torch.sigmoid(logits)
                else:
                    # Direct model path
                    logits = self.model(input_tensor)
                    probs = torch.sigmoid(logits)
            
            # Convert to numpy
            prob_map = probs.squeeze().cpu().numpy().astype(np.float32)
            predictions.append(prob_map)
        
        # Disable dropout (return to deterministic mode)
        self._disable_dropout()
        
        # Stack predictions: (T, H, W)
        predictions = np.stack(predictions, axis=0)
        
        # Compute mean probability map
        mean_prob = np.mean(predictions, axis=0)  # (H, W)
        
        # Compute epistemic uncertainty using entropy
        # Entropy: H(p) = -p*log(p) - (1-p)*log(1-p)
        uncertainty_map = self._compute_entropy(mean_prob)
        
        # Aggregate to slice-level uncertainty
        slice_uncertainty = self._aggregate_uncertainty(uncertainty_map, mean_prob)
        
        # Validate output
        assert uncertainty_map.shape == image_slice.shape, \
            f"Uncertainty map shape mismatch: {uncertainty_map.shape} vs {image_slice.shape}"
        assert isinstance(slice_uncertainty, (float, np.floating)), \
            f"Slice uncertainty must be scalar, got {type(slice_uncertainty)}"
        
        return uncertainty_map, float(slice_uncertainty)
    
    def _compute_entropy(self, prob_map: np.ndarray) -> np.ndarray:
        """
        Compute voxel-wise entropy as uncertainty measure.
        
        Args:
            prob_map: Mean probability map (H, W), float32
            
        Returns:
            Entropy map (H, W), float32, range [0, 1]
            
        Formula:
            H(p) = -p*log(p) - (1-p)*log(1-p)
            
        Note:
            Entropy is maximized at p=0.5 (maximum uncertainty)
            Entropy is minimized at p=0 or p=1 (high confidence)
        """
        # Clip to avoid log(0)
        eps = 1e-10
        p = np.clip(prob_map, eps, 1 - eps)
        
        # Binary entropy
        entropy = -(p * np.log(p) + (1 - p) * np.log(1 - p))
        
        # Normalize to [0, 1] (max entropy = log(2))
        entropy = entropy / np.log(2)
        
        return entropy.astype(np.float32)
    
    def _aggregate_uncertainty(
        self,
        uncertainty_map: np.ndarray,
        prob_map: np.ndarray,
        threshold: float = 0.1
    ) -> float:
        """
        Aggregate voxel-wise uncertainty to slice-level scalar.
        
        Args:
            uncertainty_map: Voxel-wise uncertainty (H, W)
            prob_map: Mean probability map (H, W)
            threshold: Threshold for foreground pixels
            
        Returns:
            Scalar uncertainty score, float
            
        Aggregation Strategy:
            Compute mean entropy over foreground-relevant pixels
            (pixels with probability > threshold)
            
        Rationale:
            - Focuses on uncertain regions near decision boundary
            - Ignores background pixels (low information)
            - Provides comparable scores across slices
        """
        # Identify foreground-relevant pixels
        foreground_mask = prob_map > threshold
        
        if np.sum(foreground_mask) == 0:
            # No foreground pixels - return mean over all pixels
            return float(np.mean(uncertainty_map))
        
        # Mean uncertainty over foreground-relevant pixels
        slice_uncertainty = float(np.mean(uncertainty_map[foreground_mask]))
        
        return slice_uncertainty
    
    def compute_volume_uncertainty(
        self,
        image_slices: List[np.ndarray],
        verbose: bool = True
    ) -> List[Dict]:
        """
        Compute uncertainty for all slices in a volume.
        
        Args:
            image_slices: List of 2D image slices
            verbose: Print progress
            
        Returns:
            List of uncertainty dictionaries
            
        Note:
            Processes slices sequentially to preserve alignment.
        """
        uncertainties = []
        
        for i, image_slice in enumerate(image_slices):
            if verbose:
                print(f"   Processing slice {i+1}/{len(image_slices)}")
            
            uncertainty_map, slice_uncertainty = self.compute_uncertainty(
                image_slice,
                verbose=False
            )
            
            uncertainties.append({
                "slice_id": i,
                "uncertainty_map": uncertainty_map,
                "slice_uncertainty": slice_uncertainty
            })
        
        return uncertainties


def compute_uncertainty_for_patient(
    patient_data_path: str,
    model,
    num_samples: int = 20,
    seed: int = 42,
    verbose: bool = True
) -> Dict:
    """
    Compute uncertainty for a single patient.
    
    Args:
        patient_data_path: Path to Phase 2 patient .npy file
        model: Frozen segmentation model
        num_samples: Number of MC samples (T)
        seed: Random seed
        verbose: Print progress
        
    Returns:
        Dictionary with patient_id and slice uncertainties
        
    Format:
        {
          "patient_id": str,
          "slices": [
            {
              "slice_id": int,
              "uncertainty_map": np.ndarray (H, W), float32
              "slice_uncertainty": float
            },
            ...
          ]
        }
    """
    # Load Phase 2 data
    patient_data = np.load(patient_data_path, allow_pickle=True).item()
    patient_id = patient_data["patient_id"]
    phase2_slices = patient_data["slices"]
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Computing uncertainty for patient: {patient_id}")
        print(f"Number of slices: {len(phase2_slices)}")
        print(f"{'='*60}")
    
    # Initialize uncertainty estimator
    uncertainty_estimator = MonteCarloDropoutUncertainty(
        model=model,
        num_samples=num_samples,
        seed=seed
    )
    
    # Compute uncertainty for each slice
    uncertainty_slices = []
    
    for slice_data in phase2_slices:
        slice_id = slice_data["slice_id"]
        image = slice_data["image"]  # (H, W), float32
        
        if verbose:
            print(f"\n   Slice {slice_id}:")
        
        # Compute uncertainty
        uncertainty_map, slice_uncertainty = uncertainty_estimator.compute_uncertainty(
            image,
            verbose=verbose
        )
        
        # Store uncertainty
        uncertainty_slice = {
            "slice_id": int(slice_id),
            "uncertainty_map": uncertainty_map.astype(np.float32),
            "slice_uncertainty": float(slice_uncertainty)
        }
        
        uncertainty_slices.append(uncertainty_slice)
        
        if verbose:
            print(f"   Slice uncertainty: {slice_uncertainty:.4f}")
    
    # Verify slice_id alignment
    phase2_slice_ids = [s["slice_id"] for s in phase2_slices]
    uncertainty_slice_ids = [s["slice_id"] for s in uncertainty_slices]
    assert phase2_slice_ids == uncertainty_slice_ids, \
        "Slice ID mismatch between Phase 2 and uncertainty"
    
    if verbose:
        print(f"\n✅ Uncertainty computed for {patient_id}")
        print(f"   Slices: {len(uncertainty_slices)}")
        uncertainties = [s["slice_uncertainty"] for s in uncertainty_slices]
        print(f"   Mean uncertainty: {np.mean(uncertainties):.4f}")
        print(f"   Std uncertainty: {np.std(uncertainties):.4f}")
        print(f"   Min uncertainty: {np.min(uncertainties):.4f}")
        print(f"   Max uncertainty: {np.max(uncertainties):.4f}")
    
    return {
        "patient_id": patient_id,
        "slices": uncertainty_slices
    }


if __name__ == "__main__":
    # Test uncertainty computation
    print("Testing Monte Carlo Dropout Uncertainty...")
    
    # Create dummy model with dropout
    class DummyModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv1 = nn.Conv2d(1, 16, 3, padding=1)
            self.dropout = nn.Dropout2d(p=0.1)
            self.conv2 = nn.Conv2d(16, 1, 3, padding=1)
            self.device = torch.device('cpu')
        
        def forward(self, x):
            x = self.conv1(x)
            x = self.dropout(x)
            x = self.conv2(x)
            return x
    
    # Create dummy input
    dummy_slice = np.random.randn(64, 64).astype(np.float32)
    
    # Create model
    model = DummyModel()
    model.eval()
    
    # Compute uncertainty
    estimator = MonteCarloDropoutUncertainty(
        model=model,
        num_samples=10,
        seed=42
    )
    
    uncertainty_map, slice_uncertainty = estimator.compute_uncertainty(dummy_slice)
    
    print(f"\n✅ Uncertainty computation successful!")
    print(f"   Input shape: {dummy_slice.shape}")
    print(f"   Uncertainty map shape: {uncertainty_map.shape}")
    print(f"   Slice uncertainty: {slice_uncertainty:.4f}")
    print(f"   Uncertainty range: [{uncertainty_map.min():.4f}, {uncertainty_map.max():.4f}]")
