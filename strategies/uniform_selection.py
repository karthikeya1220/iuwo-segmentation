"""
Phase 3.3 — Uniform Slice Selection Strategy

Selects B slices at fixed intervals across the volume depth.

This is a NON-OPTIMIZED baseline strategy.

Design Rationale:
- Provides spatial coverage across the volume
- Deterministic (no randomness)
- Simple and interpretable
- Common baseline in medical imaging

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


class UniformSelection(SliceSelectionStrategy):
    """
    Uniform slice selection strategy.
    
    Selects B slices at evenly-spaced intervals across the volume depth.
    
    Properties:
    - Deterministic (same input always produces same output)
    - Spatial coverage across depth
    - No domain knowledge
    - Common baseline in medical imaging
    
    Algorithm:
        Given D total slices and budget B:
        - Divide depth into B+1 intervals
        - Select slice at the center of each interval
        - Ensures even coverage from top to bottom
    
    Usage:
        >>> strategy = UniformSelection()
        >>> selected_ids = strategy.select(slices, budget=10)
    """
    
    def __init__(self, seed: int = 42):
        """
        Initialize uniform selection strategy.
        
        Args:
            seed: Random seed (not used, but kept for interface consistency)
        """
        super().__init__(name="Uniform Selection", seed=seed)
    
    def select(
        self,
        slices: List[Dict],
        budget: int
    ) -> List[int]:
        """
        Select B slices at evenly-spaced intervals.
        
        Args:
            slices: List of slice metadata dictionaries
            budget: Maximum number of slices to select (B)
            
        Returns:
            List of uniformly-spaced slice_ids
            
        Algorithm:
            1. Extract all slice_ids (sorted)
            2. Compute interval size: D / (B + 1)
            3. Select slices at positions: interval, 2*interval, ..., B*interval
            4. Round to nearest integer indices
            
        Example:
            D = 100 slices, B = 5
            Interval = 100 / 6 ≈ 16.67
            Selected indices: [16, 33, 50, 67, 83]
            
        Note:
            - Deterministic (no randomness)
            - Ensures coverage across entire depth
            - Avoids first and last slices (often empty in brain MRI)
        """
        # Extract and sort slice IDs
        slice_ids = sorted([s["slice_id"] for s in slices])
        D = len(slice_ids)
        
        # Ensure budget does not exceed number of slices
        actual_budget = min(budget, D)
        
        if actual_budget == D:
            # Select all slices
            selected_ids = slice_ids
        else:
            # Compute evenly-spaced indices
            # Divide depth into (B+1) intervals and select center of each
            interval = D / (actual_budget + 1)
            
            selected_indices = []
            for i in range(1, actual_budget + 1):
                # Position in continuous space
                position = i * interval
                # Round to nearest integer index
                index = int(np.round(position)) - 1  # -1 for 0-indexing
                # Clamp to valid range
                index = max(0, min(index, D - 1))
                selected_indices.append(index)
            
            # Convert indices to slice_ids
            selected_ids = [slice_ids[idx] for idx in selected_indices]
        
        # Validate selection
        self.validate_selection(selected_ids, slice_ids, budget)
        
        return selected_ids


if __name__ == "__main__":
    # Test uniform selection
    print("Testing Uniform Selection Strategy...")
    
    # Test 1: Basic functionality
    print("\nTest 1: Basic functionality")
    dummy_slices = [
        {"slice_id": i, "data": np.random.randn(10, 10)}
        for i in range(100)
    ]
    
    strategy = UniformSelection()
    budget = 5
    selected = strategy.select(dummy_slices, budget)
    
    print(f"Total slices: {len(dummy_slices)}")
    print(f"Budget: {budget}")
    print(f"Selected slice_ids: {sorted(selected)}")
    print(f"Number selected: {len(selected)}")
    
    assert len(selected) == budget
    assert len(selected) == len(set(selected))
    print("✅ Basic functionality verified")
    
    # Test 2: Determinism
    print("\nTest 2: Determinism")
    strategy2 = UniformSelection()
    selected2 = strategy2.select(dummy_slices, budget)
    
    assert selected == selected2, "Should produce same selection"
    print("✅ Determinism verified")
    
    # Test 3: Spatial coverage
    print("\nTest 3: Spatial coverage")
    budget = 10
    selected = strategy.select(dummy_slices, budget)
    selected_sorted = sorted(selected)
    
    print(f"Selected (sorted): {selected_sorted}")
    
    # Check that slices are spread across depth
    min_id = min(selected_sorted)
    max_id = max(selected_sorted)
    span = max_id - min_id
    
    print(f"Span: {min_id} to {max_id} (range: {span})")
    assert span > len(dummy_slices) * 0.7, "Should cover most of the depth"
    print("✅ Spatial coverage verified")
    
    # Test 4: Budget constraint
    print("\nTest 4: Budget constraint")
    large_budget = 200
    selected_large = strategy.select(dummy_slices, large_budget)
    
    print(f"Budget: {large_budget}, Available: {len(dummy_slices)}, Selected: {len(selected_large)}")
    assert len(selected_large) == len(dummy_slices), "Should select all available slices"
    print("✅ Budget constraint verified")
    
    # Test 5: Small budget
    print("\nTest 5: Small budget")
    small_budget = 1
    selected_small = strategy.select(dummy_slices, small_budget)
    
    print(f"Budget: {small_budget}, Selected: {selected_small}")
    assert len(selected_small) == small_budget
    # Should select middle slice
    expected_middle = len(dummy_slices) // 2
    assert abs(selected_small[0] - expected_middle) < 5, "Should select near middle"
    print("✅ Small budget verified")
    
    # Test 6: Edge case - 2 slices
    print("\nTest 6: Edge case - 2 total slices")
    tiny_slices = [{"slice_id": i} for i in range(2)]
    selected_tiny = strategy.select(tiny_slices, budget=1)
    
    print(f"Total: 2, Budget: 1, Selected: {selected_tiny}")
    assert len(selected_tiny) == 1
    print("✅ Edge case verified")
    
    print("\n" + "="*60)
    print("✅ All tests passed!")
    print("="*60)
