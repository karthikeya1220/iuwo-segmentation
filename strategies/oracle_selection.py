"""
Phase 3.3 — Oracle Slice Selection Strategy

Selects B slices with highest ground truth error (upper bound).

⚠️ THIS IS AN UPPER BOUND ONLY - NOT A REAL METHOD ⚠️

This strategy uses ground truth to select slices with the worst predictions.
It represents the BEST POSSIBLE selection if we had perfect knowledge.

Design Rationale:
- Provides an upper bound for comparison
- Shows maximum achievable improvement
- NOT a real method (uses ground truth)
- Must be clearly labeled in all results

Author: Research Prototype
Date: 2026-02-02
"""

import sys
from pathlib import Path
import numpy as np
from typing import List, Dict

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from strategies.base_strategy import SliceSelectionStrategy


class OracleSelection(SliceSelectionStrategy):
    """
    Oracle slice selection strategy (UPPER BOUND ONLY).
    
    ⚠️ WARNING: This is NOT a real method! ⚠️
    
    Selects B slices with the highest prediction error (lowest Dice score).
    Requires ground truth masks, which are NOT available in real scenarios.
    
    Purpose:
    - Provides an upper bound on achievable performance
    - Shows maximum possible improvement with perfect knowledge
    - Used for comparison only, never as a real method
    
    Properties:
    - Uses ground truth (NOT available in practice)
    - Deterministic (given predictions and ground truth)
    - Represents best-case scenario
    - Must be labeled as "UPPER BOUND" in all results
    
    Usage:
        >>> strategy = OracleSelection()
        >>> # Requires both predictions and ground truth
        >>> selected_ids = strategy.select(slices, budget=10)
    """
    
    def __init__(self, seed: int = 42):
        """
        Initialize oracle selection strategy.
        
        Args:
            seed: Random seed (not used, but kept for interface consistency)
        """
        super().__init__(name="Oracle Selection (UPPER BOUND)", seed=seed)
    
    def compute_slice_dice(
        self,
        pred_mask: np.ndarray,
        gt_mask: np.ndarray
    ) -> float:
        """
        Compute Dice coefficient for a single slice.
        
        Args:
            pred_mask: Predicted binary mask (H, W), uint8
            gt_mask: Ground truth binary mask (H, W), uint8
            
        Returns:
            Dice coefficient in [0, 1]
            
        Formula:
            Dice = 2 * |pred ∩ gt| / (|pred| + |gt|)
        """
        assert pred_mask.shape == gt_mask.shape, "Shape mismatch"
        assert pred_mask.dtype == np.uint8, "pred_mask must be uint8"
        assert gt_mask.dtype == np.uint8, "gt_mask must be uint8"
        
        intersection = np.sum(pred_mask * gt_mask)
        union = np.sum(pred_mask) + np.sum(gt_mask)
        
        if union == 0:
            # Both empty - perfect match
            return 1.0
        
        dice = 2.0 * intersection / union
        return float(dice)
    
    def select(
        self,
        slices: List[Dict],
        budget: int
    ) -> List[int]:
        """
        Select B slices with lowest Dice scores (highest error).
        
        ⚠️ WARNING: Uses ground truth - NOT a real method! ⚠️
        
        Args:
            slices: List of slice metadata dictionaries
                    Each dict must contain:
                    - "slice_id": int
                    - "pred_mask": np.ndarray (H, W), uint8
                    - "gt_mask": np.ndarray (H, W), uint8
            budget: Maximum number of slices to select (B)
            
        Returns:
            List of slice_ids with lowest Dice scores
            
        Algorithm:
            1. Compute Dice score for each slice
            2. Sort slices by Dice score (ascending)
            3. Select B slices with lowest Dice scores
            
        Note:
            - This uses GROUND TRUTH, which is NOT available in practice
            - This is an UPPER BOUND on achievable performance
            - Must be labeled as "UPPER BOUND" in all results
            - Never treat this as a real method
        """
        # Extract slice IDs
        slice_ids = [s["slice_id"] for s in slices]
        
        # Ensure budget does not exceed number of slices
        actual_budget = min(budget, len(slice_ids))
        
        # Compute Dice score for each slice
        dice_scores = []
        for s in slices:
            # Verify required fields
            assert "slice_id" in s, "Missing slice_id"
            assert "pred_mask" in s, "Missing pred_mask (oracle requires predictions)"
            assert "gt_mask" in s, "Missing gt_mask (oracle requires ground truth)"
            
            pred_mask = s["pred_mask"]
            gt_mask = s["gt_mask"]
            
            dice = self.compute_slice_dice(pred_mask, gt_mask)
            dice_scores.append((s["slice_id"], dice))
        
        # Sort by Dice score (ascending) - lowest Dice = highest error
        dice_scores.sort(key=lambda x: x[1])
        
        # Select B slices with lowest Dice scores
        selected_ids = [slice_id for slice_id, dice in dice_scores[:actual_budget]]
        
        # Validate selection
        self.validate_selection(selected_ids, slice_ids, budget)
        
        return selected_ids


if __name__ == "__main__":
    # Test oracle selection
    print("Testing Oracle Selection Strategy...")
    print("\n⚠️  WARNING: This is an UPPER BOUND only, NOT a real method! ⚠️\n")
    
    # Create dummy slices with predictions and ground truth
    np.random.seed(42)
    
    dummy_slices = []
    for i in range(20):
        # Create random prediction and ground truth
        pred_mask = (np.random.rand(64, 64) > 0.5).astype(np.uint8)
        gt_mask = (np.random.rand(64, 64) > 0.5).astype(np.uint8)
        
        dummy_slices.append({
            "slice_id": i,
            "pred_mask": pred_mask,
            "gt_mask": gt_mask
        })
    
    # Test oracle selection
    strategy = OracleSelection()
    budget = 5
    selected = strategy.select(dummy_slices, budget)
    
    print(f"Strategy: {strategy}")
    print(f"Budget: {budget}")
    print(f"Selected slice_ids: {sorted(selected)}")
    print(f"Number selected: {len(selected)}")
    
    # Verify that selected slices have low Dice scores
    print("\nVerifying selection quality...")
    for s in dummy_slices:
        dice = strategy.compute_slice_dice(s["pred_mask"], s["gt_mask"])
        is_selected = s["slice_id"] in selected
        marker = "✓" if is_selected else " "
        print(f"  [{marker}] Slice {s['slice_id']:2d}: Dice = {dice:.3f}")
    
    # Compute average Dice for selected vs non-selected
    selected_dice = []
    nonselected_dice = []
    
    for s in dummy_slices:
        dice = strategy.compute_slice_dice(s["pred_mask"], s["gt_mask"])
        if s["slice_id"] in selected:
            selected_dice.append(dice)
        else:
            nonselected_dice.append(dice)
    
    print(f"\nAverage Dice (selected): {np.mean(selected_dice):.3f}")
    print(f"Average Dice (non-selected): {np.mean(nonselected_dice):.3f}")
    
    # Selected slices should have lower average Dice
    assert np.mean(selected_dice) <= np.mean(nonselected_dice) + 0.01, \
        "Oracle should select slices with lower Dice scores"
    
    print("\n✅ Oracle selection verified!")
    print("\n⚠️  Remember: This is an UPPER BOUND only!")
    print("   Never use this as a real method in practice.")
