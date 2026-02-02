"""
Phase 3.3 — Random Slice Selection Strategy

Selects B slices uniformly at random from all available slices.

This is a NON-OPTIMIZED baseline strategy.

Design Rationale:
- Provides a lower bound for comparison
- No domain knowledge required
- Stochastic (requires random seed for reproducibility)

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


class RandomSelection(SliceSelectionStrategy):
    """
    Random slice selection strategy.
    
    Selects B slices uniformly at random from all available slices.
    
    Properties:
    - Stochastic (different runs produce different selections)
    - No domain knowledge
    - Treats all slices equally
    - Lower bound baseline
    
    Usage:
        >>> strategy = RandomSelection(seed=42)
        >>> selected_ids = strategy.select(slices, budget=10)
    """
    
    def __init__(self, seed: int = 42):
        """
        Initialize random selection strategy.
        
        Args:
            seed: Random seed for reproducibility
        """
        super().__init__(name="Random Selection", seed=seed)
    
    def select(
        self,
        slices: List[Dict],
        budget: int
    ) -> List[int]:
        """
        Select B slices uniformly at random.
        
        Args:
            slices: List of slice metadata dictionaries
            budget: Maximum number of slices to select (B)
            
        Returns:
            List of randomly selected slice_ids
            
        Algorithm:
            1. Extract all slice_ids
            2. Randomly shuffle slice_ids
            3. Select first B slice_ids
            
        Note:
            - Uses numpy.random with fixed seed for reproducibility
            - All slices have equal probability of selection
            - No domain knowledge is used
        """
        # Extract slice IDs
        slice_ids = [s["slice_id"] for s in slices]
        
        # Ensure budget does not exceed number of slices
        actual_budget = min(budget, len(slice_ids))
        
        # Random selection without replacement
        # Set seed for reproducibility
        rng = np.random.RandomState(self.seed)
        selected_ids = rng.choice(
            slice_ids,
            size=actual_budget,
            replace=False  # No duplicates
        ).tolist()
        
        # Validate selection
        self.validate_selection(selected_ids, slice_ids, budget)
        
        return selected_ids


if __name__ == "__main__":
    # Test random selection
    print("Testing Random Selection Strategy...")
    
    # Create dummy slices
    dummy_slices = [
        {"slice_id": i, "data": np.random.randn(10, 10)}
        for i in range(50)
    ]
    
    # Test with different seeds
    print("\nTest 1: Same seed produces same selection")
    strategy1 = RandomSelection(seed=42)
    strategy2 = RandomSelection(seed=42)
    
    budget = 10
    selected1 = strategy1.select(dummy_slices, budget)
    selected2 = strategy2.select(dummy_slices, budget)
    
    print(f"Strategy 1 selected: {sorted(selected1)}")
    print(f"Strategy 2 selected: {sorted(selected2)}")
    assert selected1 == selected2, "Same seed should produce same selection"
    print("✅ Reproducibility verified")
    
    # Test with different seeds
    print("\nTest 2: Different seeds produce different selections")
    strategy3 = RandomSelection(seed=123)
    selected3 = strategy3.select(dummy_slices, budget)
    
    print(f"Strategy 3 selected: {sorted(selected3)}")
    assert selected1 != selected3, "Different seeds should produce different selections"
    print("✅ Randomness verified")
    
    # Test budget constraint
    print("\nTest 3: Budget constraint")
    large_budget = 100
    selected_large = strategy1.select(dummy_slices, large_budget)
    print(f"Budget: {large_budget}, Available: {len(dummy_slices)}, Selected: {len(selected_large)}")
    assert len(selected_large) == len(dummy_slices), "Should select all available slices"
    print("✅ Budget constraint verified")
    
    # Test uniqueness
    print("\nTest 4: Uniqueness")
    assert len(selected1) == len(set(selected1)), "Selected IDs should be unique"
    print("✅ Uniqueness verified")
    
    print("\n" + "="*60)
    print("✅ All tests passed!")
    print("="*60)
