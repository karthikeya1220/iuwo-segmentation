"""
Phase 6 — Impact-Weighted Uncertainty Optimization (IWUO)

This module implements the IWUO slice selection algorithm under hard budget constraints.

IWUO answers: "Given limited expert effort, which slices should be corrected?"

This phase performs DECISION-MAKING ONLY.

This phase does NOT include:
- Expert correction simulation
- Dice score computation
- Performance evaluation
- Learning or retraining
- Uncertainty computation
- Impact computation
- Hyperparameter tuning

Design Rationale:
- Combines uncertainty (model confidence) and impact (volumetric importance)
- Deterministic budget-constrained selection
- Linear weighting for interpretability

Author: Research Prototype
Date: 2026-02-02
"""

import numpy as np
from typing import List, Dict, Tuple
from pathlib import Path


class IWUOSelector:
    """
    Impact-Weighted Uncertainty Optimization (IWUO) selector.
    
    This class implements a deterministic budget-constrained slice selection
    algorithm that combines uncertainty and impact signals.
    
    Decision Rule:
        For each slice i, compute joint priority score:
        S_i = α · U_i + (1 - α) · I_i
        
        Select top-B slices by S_i.
    
    Parameters:
        - α ∈ [0, 1]: weighting parameter (default: 0.5)
        - U_i: normalized uncertainty score (Phase 4)
        - I_i: normalized impact score (Phase 5)
        - B: expert budget (number of slices)
    
    Note:
        This is a DECISION-MAKING module only.
        It does NOT compute uncertainty or impact.
        It uses pre-computed artifacts from Phase 4 and Phase 5.
    """
    
    def __init__(self, alpha: float = 0.5):
        """
        Initialize IWUO selector.
        
        Args:
            alpha: Weighting parameter for uncertainty vs impact
                   α = 0.0: impact-only selection
                   α = 0.5: equal weighting (default)
                   α = 1.0: uncertainty-only selection
                   
        Note:
            Alpha is a HYPERPARAMETER, not tuned here.
            Default α = 0.5 gives equal weight to both signals.
        """
        assert 0.0 <= alpha <= 1.0, f"Alpha must be in [0, 1], got {alpha}"
        
        self.alpha = alpha
        
        print(f"✅ IWUO Selector initialized")
        print(f"   Alpha (uncertainty weight): {alpha:.2f}")
        print(f"   Impact weight: {1 - alpha:.2f}")
    
    def select(
        self,
        uncertainty_data: Dict,
        impact_data: Dict,
        budget: int,
        verbose: bool = False
    ) -> List[int]:
        """
        Select slices using IWUO under budget constraint.
        
        DECISION-MAKING ONLY - No evaluation, no correction simulation.
        
        Args:
            uncertainty_data: Phase 4 uncertainty artifacts
                              Must contain "slices" with "slice_id" and "slice_uncertainty"
            impact_data: Phase 5 impact artifacts
                         Must contain "slices" with "slice_id" and "impact_score"
            budget: Maximum number of slices to select (B)
            verbose: Print selection details
            
        Returns:
            List of selected slice_ids (length <= budget)
            
        Algorithm:
            1. Verify slice alignment between uncertainty and impact
            2. Extract uncertainty and impact scores
            3. Compute joint priority scores: S_i = α·U_i + (1-α)·I_i
            4. Sort slices by S_i (descending)
            5. Select top-B slices
            6. Return selected slice_ids
            
        Note:
            - Deterministic (same inputs → same outputs)
            - Reproducible
            - Order-invariant given identical inputs
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"IWUO Slice Selection")
            print(f"{'='*60}")
        
        # Verify data structure
        assert "slices" in uncertainty_data, "Missing 'slices' in uncertainty_data"
        assert "slices" in impact_data, "Missing 'slices' in impact_data"
        
        uncertainty_slices = uncertainty_data["slices"]
        impact_slices = impact_data["slices"]
        
        # Verify slice alignment
        assert len(uncertainty_slices) == len(impact_slices), \
            f"Slice count mismatch: {len(uncertainty_slices)} vs {len(impact_slices)}"
        
        unc_slice_ids = [s["slice_id"] for s in uncertainty_slices]
        imp_slice_ids = [s["slice_id"] for s in impact_slices]
        
        assert unc_slice_ids == imp_slice_ids, \
            "Slice ID mismatch between uncertainty and impact"
        
        # Verify budget validity
        num_slices = len(uncertainty_slices)
        assert budget > 0, f"Budget must be positive, got {budget}"
        
        actual_budget = min(budget, num_slices)
        
        if verbose:
            print(f"   Total slices: {num_slices}")
            print(f"   Requested budget: {budget}")
            print(f"   Actual budget: {actual_budget}")
            print(f"   Alpha: {self.alpha:.2f}")
        
        # Extract uncertainty and impact scores
        uncertainty_scores = np.array([
            s["slice_uncertainty"] for s in uncertainty_slices
        ], dtype=np.float32)
        
        impact_scores = np.array([
            s["impact_score"] for s in impact_slices
        ], dtype=np.float32)
        
        # Verify normalization (should already be [0, 1])
        assert np.all((0 <= uncertainty_scores) & (uncertainty_scores <= 1)), \
            "Uncertainty scores must be in [0, 1]"
        assert np.all((0 <= impact_scores) & (impact_scores <= 1)), \
            "Impact scores must be in [0, 1]"
        
        # Compute joint priority scores
        # S_i = α · U_i + (1 - α) · I_i
        joint_scores = (
            self.alpha * uncertainty_scores +
            (1 - self.alpha) * impact_scores
        )
        
        if verbose:
            print(f"\n   Joint score statistics:")
            print(f"   - Mean: {np.mean(joint_scores):.4f}")
            print(f"   - Std: {np.std(joint_scores):.4f}")
            print(f"   - Min: {np.min(joint_scores):.4f}")
            print(f"   - Max: {np.max(joint_scores):.4f}")
        
        # Sort slices by joint score (descending)
        sorted_indices = np.argsort(joint_scores)[::-1]
        
        # Select top-B slices
        selected_indices = sorted_indices[:actual_budget]
        
        # Get selected slice_ids
        selected_slice_ids = [unc_slice_ids[i] for i in selected_indices]
        
        if verbose:
            print(f"\n   Selected {len(selected_slice_ids)} slices:")
            for i, idx in enumerate(selected_indices[:10]):  # Show first 10
                slice_id = unc_slice_ids[idx]
                unc = uncertainty_scores[idx]
                imp = impact_scores[idx]
                joint = joint_scores[idx]
                print(f"   {i+1}. Slice {slice_id}: U={unc:.3f}, I={imp:.3f}, S={joint:.3f}")
            if len(selected_indices) > 10:
                print(f"   ... and {len(selected_indices) - 10} more")
        
        if verbose:
            print(f"\n{'='*60}")
        
        return selected_slice_ids
    
    def get_selection_details(
        self,
        uncertainty_data: Dict,
        impact_data: Dict,
        budget: int
    ) -> Dict:
        """
        Get detailed selection information (for analysis, not evaluation).
        
        Args:
            uncertainty_data: Phase 4 uncertainty artifacts
            impact_data: Phase 5 impact artifacts
            budget: Maximum number of slices to select
            
        Returns:
            Dictionary with selection details
            
        Format:
            {
              "selected_slice_ids": [int, ...],
              "joint_scores": np.ndarray,
              "uncertainty_scores": np.ndarray,
              "impact_scores": np.ndarray,
              "alpha": float,
              "budget": int
            }
        """
        # Extract data
        uncertainty_slices = uncertainty_data["slices"]
        impact_slices = impact_data["slices"]
        
        slice_ids = [s["slice_id"] for s in uncertainty_slices]
        
        uncertainty_scores = np.array([
            s["slice_uncertainty"] for s in uncertainty_slices
        ], dtype=np.float32)
        
        impact_scores = np.array([
            s["impact_score"] for s in impact_slices
        ], dtype=np.float32)
        
        # Compute joint scores
        joint_scores = (
            self.alpha * uncertainty_scores +
            (1 - self.alpha) * impact_scores
        )
        
        # Select slices
        selected_slice_ids = self.select(
            uncertainty_data,
            impact_data,
            budget,
            verbose=False
        )
        
        return {
            "selected_slice_ids": selected_slice_ids,
            "joint_scores": joint_scores,
            "uncertainty_scores": uncertainty_scores,
            "impact_scores": impact_scores,
            "slice_ids": slice_ids,
            "alpha": self.alpha,
            "budget": budget
        }


def select_slices_for_patient(
    uncertainty_path: str,
    impact_path: str,
    budget: int,
    alpha: float = 0.5,
    verbose: bool = True
) -> Dict:
    """
    Select slices for a single patient using IWUO.
    
    Args:
        uncertainty_path: Path to Phase 4 uncertainty .npy file
        impact_path: Path to Phase 5 impact .npy file
        budget: Maximum number of slices to select
        alpha: Weighting parameter (default: 0.5)
        verbose: Print selection details
        
    Returns:
        Dictionary with patient_id, budget, alpha, and selected_slices
        
    Format:
        {
          "patient_id": str,
          "budget": int,
          "alpha": float,
          "selected_slices": [int, int, ...]
        }
    """
    # Load uncertainty and impact data
    uncertainty_data = np.load(uncertainty_path, allow_pickle=True).item()
    impact_data = np.load(impact_path, allow_pickle=True).item()
    
    # Verify patient_id match
    assert uncertainty_data["patient_id"] == impact_data["patient_id"], \
        "Patient ID mismatch between uncertainty and impact"
    
    patient_id = uncertainty_data["patient_id"]
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"IWUO Selection for patient: {patient_id}")
        print(f"{'='*60}")
    
    # Initialize selector
    selector = IWUOSelector(alpha=alpha)
    
    # Select slices
    selected_slices = selector.select(
        uncertainty_data=uncertainty_data,
        impact_data=impact_data,
        budget=budget,
        verbose=verbose
    )
    
    if verbose:
        print(f"\n✅ Selection complete for {patient_id}")
        print(f"   Selected {len(selected_slices)} slices")
    
    return {
        "patient_id": patient_id,
        "budget": budget,
        "alpha": alpha,
        "selected_slices": selected_slices
    }


if __name__ == "__main__":
    # Test IWUO selector
    print("Testing IWUO Selector...")
    
    # Create dummy uncertainty and impact data
    num_slices = 50
    
    dummy_uncertainty = {
        "patient_id": "TEST_PATIENT",
        "slices": [
            {
                "slice_id": i,
                "slice_uncertainty": np.random.rand()
            }
            for i in range(num_slices)
        ]
    }
    
    dummy_impact = {
        "patient_id": "TEST_PATIENT",
        "slices": [
            {
                "slice_id": i,
                "impact_score": np.random.rand()
            }
            for i in range(num_slices)
        ]
    }
    
    # Test IWUO selection
    selector = IWUOSelector(alpha=0.5)
    budget = 10
    
    selected = selector.select(
        uncertainty_data=dummy_uncertainty,
        impact_data=dummy_impact,
        budget=budget,
        verbose=True
    )
    
    print(f"\n✅ IWUO selection successful!")
    print(f"   Budget: {budget}")
    print(f"   Selected: {len(selected)} slices")
    print(f"   Slice IDs: {sorted(selected)}")
    
    # Test determinism
    selected2 = selector.select(
        uncertainty_data=dummy_uncertainty,
        impact_data=dummy_impact,
        budget=budget,
        verbose=False
    )
    
    assert selected == selected2, "Selection must be deterministic"
    print(f"\n✅ Determinism verified!")
