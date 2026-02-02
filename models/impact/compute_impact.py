"""
Phase 5 — Impact Estimation

This module computes the GLOBAL VOLUMETRIC IMPACT of correcting each slice.

IMPACT IS A SIGNAL, NOT A DECISION RULE.

Impact answers: "How much does correcting this slice matter for the final 3D segmentation?"

This phase does NOT include:
- Slice selection
- Ranking for decision-making
- Budget constraints
- Optimization logic
- Expert correction simulation
- Uncertainty combination

Design Rationale:
- Impact reflects volumetric contribution to global segmentation
- Impact is independent of uncertainty
- Impact provides a complementary signal to uncertainty

Author: Research Prototype
Date: 2026-02-02
"""

import numpy as np
from typing import Dict, List, Tuple
from pathlib import Path


class VolumetricImpactEstimator:
    """
    Volumetric impact estimation for slice-level corrections.
    
    This class computes the global volumetric importance of each slice
    based on its contribution to the total predicted tumor volume.
    
    Impact Formulation:
        Slice-wise contribution to total predicted tumor volume,
        weighted by spatial connectivity and geometric properties.
    
    Rationale:
        - Slices with larger tumor regions have higher impact
        - Slices in the tumor core have higher impact than periphery
        - Impact reflects potential influence on global segmentation
    
    Note:
        Impact is computed as a SIGNAL only.
        This phase does NOT use impact for decision-making.
    """
    
    def __init__(
        self,
        use_connectivity: bool = True,
        use_sqrt_transform: bool = True
    ):
        """
        Initialize volumetric impact estimator.
        
        Args:
            use_connectivity: Weight impact by 3D connectivity
            use_sqrt_transform: Apply sqrt stabilization to impact scores
            
        Note:
            Sqrt transform reduces dynamic range and stabilizes scores.
        """
        self.use_connectivity = use_connectivity
        self.use_sqrt_transform = use_sqrt_transform
        
        print(f"✅ Volumetric Impact Estimator initialized")
        print(f"   Connectivity weighting: {use_connectivity}")
        print(f"   Sqrt stabilization: {use_sqrt_transform}")
    
    def compute_impact(
        self,
        predictions: List[Dict],
        verbose: bool = False
    ) -> List[Dict]:
        """
        Compute volumetric impact for all slices in a volume.
        
        IMPACT IS A SIGNAL, NOT A DECISION RULE.
        
        Args:
            predictions: List of prediction dictionaries from Phase 3
                         Each dict must contain:
                         - "slice_id": int
                         - "pred_mask": np.ndarray (H, W), uint8
            verbose: Print progress
            
        Returns:
            List of impact dictionaries
            
        Algorithm:
            1. Compute voxel count per slice (tumor volume proxy)
            2. Weight by connectivity to adjacent slices
            3. Normalize to [0, 1] range
            4. Apply stabilization transform (optional)
            
        Note:
            - No ground truth is used
            - No expert corrections are simulated
            - Impact is independent of uncertainty
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"Computing volumetric impact...")
            print(f"{'='*60}")
        
        # Extract slice IDs and masks
        slice_ids = [p["slice_id"] for p in predictions]
        pred_masks = [p["pred_mask"] for p in predictions]
        
        num_slices = len(predictions)
        
        # Step 1: Compute raw voxel counts per slice
        voxel_counts = []
        for i, mask in enumerate(pred_masks):
            count = np.sum(mask > 0)  # Foreground voxels
            voxel_counts.append(count)
            
            if verbose and (i % 20 == 0 or i == num_slices - 1):
                print(f"   Slice {i+1}/{num_slices}: {count} foreground voxels")
        
        voxel_counts = np.array(voxel_counts, dtype=np.float32)
        
        # Step 2: Weight by connectivity (optional)
        if self.use_connectivity:
            connectivity_weights = self._compute_connectivity_weights(pred_masks)
            weighted_counts = voxel_counts * connectivity_weights
        else:
            weighted_counts = voxel_counts
        
        # Step 3: Normalize to [0, 1]
        if np.max(weighted_counts) > 0:
            normalized_impact = weighted_counts / np.max(weighted_counts)
        else:
            # All slices empty - uniform zero impact
            normalized_impact = np.zeros_like(weighted_counts)
        
        # Step 4: Apply stabilization transform (optional)
        if self.use_sqrt_transform:
            # Sqrt reduces dynamic range and stabilizes scores
            impact_scores = np.sqrt(normalized_impact)
        else:
            impact_scores = normalized_impact
        
        # Create impact dictionaries
        impact_results = []
        for slice_id, impact_score in zip(slice_ids, impact_scores):
            impact_results.append({
                "slice_id": int(slice_id),
                "impact_score": float(impact_score)
            })
        
        if verbose:
            print(f"\n✅ Impact computation complete")
            print(f"   Mean impact: {np.mean(impact_scores):.4f}")
            print(f"   Std impact: {np.std(impact_scores):.4f}")
            print(f"   Min impact: {np.min(impact_scores):.4f}")
            print(f"   Max impact: {np.max(impact_scores):.4f}")
        
        return impact_results
    
    def _compute_connectivity_weights(
        self,
        pred_masks: List[np.ndarray]
    ) -> np.ndarray:
        """
        Compute connectivity weights based on 3D spatial context.
        
        Args:
            pred_masks: List of predicted masks (H, W), uint8
            
        Returns:
            Connectivity weights (num_slices,), float32
            
        Rationale:
            Slices in the tumor core (surrounded by tumor slices)
            have higher impact than isolated peripheral slices.
            
        Algorithm:
            For each slice, count adjacent slices with foreground.
            Weight = (1 + num_adjacent_with_tumor) / 3
            
        Note:
            This is a simple 3D connectivity proxy.
            More sophisticated methods could use connected components.
        """
        num_slices = len(pred_masks)
        weights = np.ones(num_slices, dtype=np.float32)
        
        for i in range(num_slices):
            num_adjacent = 0
            
            # Check previous slice
            if i > 0 and np.sum(pred_masks[i-1] > 0) > 0:
                num_adjacent += 1
            
            # Check next slice
            if i < num_slices - 1 and np.sum(pred_masks[i+1] > 0) > 0:
                num_adjacent += 1
            
            # Weight: (1 + num_adjacent) / 3
            # Range: [1/3, 1] for [0, 2] adjacent slices
            weights[i] = (1.0 + num_adjacent) / 3.0
        
        return weights


def compute_impact_for_patient(
    predictions_path: str,
    use_connectivity: bool = True,
    use_sqrt_transform: bool = True,
    verbose: bool = True
) -> Dict:
    """
    Compute impact for a single patient.
    
    Args:
        predictions_path: Path to Phase 3 predictions .npy file
        use_connectivity: Weight impact by 3D connectivity
        use_sqrt_transform: Apply sqrt stabilization
        verbose: Print progress
        
    Returns:
        Dictionary with patient_id and slice impacts
        
    Format:
        {
          "patient_id": str,
          "slices": [
            {
              "slice_id": int,
              "impact_score": float
            },
            ...
          ]
        }
    """
    # Load Phase 3 predictions
    predictions_data = np.load(predictions_path, allow_pickle=True).item()
    patient_id = predictions_data["patient_id"]
    predictions = predictions_data["slices"]
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Computing impact for patient: {patient_id}")
        print(f"Number of slices: {len(predictions)}")
        print(f"{'='*60}")
    
    # Initialize impact estimator
    impact_estimator = VolumetricImpactEstimator(
        use_connectivity=use_connectivity,
        use_sqrt_transform=use_sqrt_transform
    )
    
    # Compute impact
    impact_slices = impact_estimator.compute_impact(
        predictions=predictions,
        verbose=verbose
    )
    
    # Verify slice_id alignment
    pred_slice_ids = [p["slice_id"] for p in predictions]
    impact_slice_ids = [s["slice_id"] for s in impact_slices]
    assert pred_slice_ids == impact_slice_ids, \
        "Slice ID mismatch between predictions and impact"
    
    if verbose:
        print(f"\n✅ Impact computed for {patient_id}")
        print(f"   Slices: {len(impact_slices)}")
    
    return {
        "patient_id": patient_id,
        "slices": impact_slices
    }


if __name__ == "__main__":
    # Test impact computation
    print("Testing Volumetric Impact Estimation...")
    
    # Create dummy predictions
    dummy_predictions = []
    for i in range(50):
        # Simulate varying tumor sizes
        if 10 <= i <= 40:
            # Tumor core: larger masks
            mask = (np.random.rand(64, 64) > 0.3).astype(np.uint8)
        else:
            # Periphery: smaller masks
            mask = (np.random.rand(64, 64) > 0.8).astype(np.uint8)
        
        dummy_predictions.append({
            "slice_id": i,
            "pred_mask": mask
        })
    
    # Compute impact
    estimator = VolumetricImpactEstimator(
        use_connectivity=True,
        use_sqrt_transform=True
    )
    
    impact_results = estimator.compute_impact(
        predictions=dummy_predictions,
        verbose=True
    )
    
    print(f"\n✅ Impact computation successful!")
    print(f"   Number of slices: {len(impact_results)}")
    
    # Show impact distribution
    impact_scores = [s["impact_score"] for s in impact_results]
    print(f"\n   Impact distribution:")
    print(f"   - Core slices (10-40): mean = {np.mean(impact_scores[10:41]):.4f}")
    print(f"   - Peripheral slices: mean = {np.mean(impact_scores[:10] + impact_scores[41:]):.4f}")
