"""
Phase 3.3 — Base Slice Selection Strategy

This module defines the interface for all slice selection strategies.

All strategies must implement the same interface to enable fair comparison.

Design Constraints:
- No optimization logic (Phase 3 only)
- No uncertainty estimation (Phase 3 only)
- No impact estimation (Phase 3 only)
- No expert correction (simulated in later phases)

Author: Research Prototype
Date: 2026-02-02
"""

from abc import ABC, abstractmethod
from typing import List, Dict
import numpy as np


class SliceSelectionStrategy(ABC):
    """
    Abstract base class for slice selection strategies.
    
    All strategies must implement the select() method.
    
    This interface enables fair comparison of different selection approaches
    under the same budget constraint.
    """
    
    def __init__(self, name: str, seed: int = 42):
        """
        Initialize strategy.
        
        Args:
            name: Human-readable strategy name
            seed: Random seed for reproducibility (if applicable)
        """
        self.name = name
        self.seed = seed
        np.random.seed(seed)
    
    @abstractmethod
    def select(
        self,
        slices: List[Dict],
        budget: int
    ) -> List[int]:
        """
        Select slices for expert review under budget constraint.
        
        Args:
            slices: List of slice metadata dictionaries
                    Each dict must contain at minimum:
                    - "slice_id": int
                    Additional fields depend on strategy
            budget: Maximum number of slices to select (B)
            
        Returns:
            List of selected slice_ids (length <= budget)
            
        Constraints:
            - Must return at most `budget` slice_ids
            - slice_ids must be valid (exist in input slices)
            - slice_ids must be unique (no duplicates)
            - Order of returned slice_ids does not matter
            
        Note:
            This is Phase 3 only. Strategies must NOT:
            - Compute uncertainty
            - Compute impact
            - Apply expert corrections
            - Optimize for Dice improvement
        """
        pass
    
    def validate_selection(
        self,
        selected_ids: List[int],
        all_slice_ids: List[int],
        budget: int
    ) -> None:
        """
        Validate that selection satisfies constraints.
        
        Args:
            selected_ids: Selected slice IDs
            all_slice_ids: All available slice IDs
            budget: Budget constraint
            
        Raises:
            AssertionError: If constraints are violated
        """
        # Check budget constraint
        assert len(selected_ids) <= budget, \
            f"Budget violated: selected {len(selected_ids)}, budget {budget}"
        
        # Check uniqueness
        assert len(selected_ids) == len(set(selected_ids)), \
            "Selected slice_ids contain duplicates"
        
        # Check validity
        for slice_id in selected_ids:
            assert slice_id in all_slice_ids, \
                f"Invalid slice_id: {slice_id} not in available slices"
    
    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(name='{self.name}', seed={self.seed})"


class DummyStrategy(SliceSelectionStrategy):
    """
    Dummy strategy for testing the interface.
    
    Selects the first B slices.
    """
    
    def __init__(self, seed: int = 42):
        super().__init__(name="Dummy (First B)", seed=seed)
    
    def select(self, slices: List[Dict], budget: int) -> List[int]:
        """Select first B slices."""
        slice_ids = [s["slice_id"] for s in slices]
        selected = slice_ids[:budget]
        
        # Validate
        self.validate_selection(selected, slice_ids, budget)
        
        return selected


if __name__ == "__main__":
    # Test base interface
    print("Testing SliceSelectionStrategy interface...")
    
    # Create dummy slices
    dummy_slices = [
        {"slice_id": i, "data": np.random.randn(10, 10)}
        for i in range(20)
    ]
    
    # Test dummy strategy
    strategy = DummyStrategy(seed=42)
    print(f"\nStrategy: {strategy}")
    
    budget = 5
    selected = strategy.select(dummy_slices, budget)
    
    print(f"Budget: {budget}")
    print(f"Selected slice_ids: {selected}")
    print(f"Number selected: {len(selected)}")
    
    assert len(selected) == budget
    assert len(selected) == len(set(selected))
    
    print("\n✅ Interface test passed!")
