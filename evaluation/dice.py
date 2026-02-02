"""
Phase 8 — Dice Similarity Coefficient Computation

This module computes Dice scores for evaluating segmentation quality.

EVALUATION ONLY - No decision-making, no learning.

This phase does NOT include:
- Slice selection logic
- Uncertainty computation
- Impact computation
- Expert correction simulation
- Learning or retraining
- Hyperparameter tuning

Design Rationale:
- Dice measures overlap between prediction and ground truth
- Computed on FULL corrected volumes
- Handles empty-mask edge cases correctly

Author: Research Prototype
Date: 2026-02-02
"""

import numpy as np
from typing import Dict, List


def compute_dice(pred_mask: np.ndarray, gt_mask: np.ndarray) -> float:
    """
    Compute Dice Similarity Coefficient between prediction and ground truth.
    
    Dice = 2 * |P ∩ G| / (|P| + |G|)
    
    Args:
        pred_mask: Binary prediction mask (H, W) or (D, H, W)
        gt_mask: Binary ground truth mask (H, W) or (D, H, W)
        
    Returns:
        Dice score in [0, 1]
        
    Edge Cases:
        - Both masks empty: Dice = 1.0 (perfect agreement)
        - One mask empty: Dice = 0.0 (no overlap)
        
    Note:
        This is EVALUATION ONLY.
        Dice is NOT used for decision-making or optimization.
    """
    # Ensure binary masks
    pred_binary = (pred_mask > 0).astype(np.uint8)
    gt_binary = (gt_mask > 0).astype(np.uint8)
    
    # Flatten masks
    pred_flat = pred_binary.flatten()
    gt_flat = gt_binary.flatten()
    
    # Compute intersection and union
    intersection = np.sum(pred_flat * gt_flat)
    pred_sum = np.sum(pred_flat)
    gt_sum = np.sum(gt_flat)
    
    # Handle edge cases
    if pred_sum == 0 and gt_sum == 0:
        # Both masks empty → perfect agreement
        return 1.0
    
    if pred_sum == 0 or gt_sum == 0:
        # One mask empty → no overlap
        return 0.0
    
    # Compute Dice
    dice = (2.0 * intersection) / (pred_sum + gt_sum)
    
    return float(dice)


def compute_volume_dice(
    corrected_slices: List[Dict],
    ground_truth_slices: List[Dict]
) -> float:
    """
    Compute Dice on full 3D volume.
    
    Args:
        corrected_slices: List of corrected slice dictionaries
                          Each dict has "slice_id" and "mask"
        ground_truth_slices: List of ground truth slice dictionaries
                             Each dict has "slice_id" and "mask"
        
    Returns:
        Dice score for the full volume
        
    Note:
        Slices must be aligned (same slice_ids in same order).
    """
    # Verify slice alignment
    assert len(corrected_slices) == len(ground_truth_slices), \
        f"Slice count mismatch: {len(corrected_slices)} vs {len(ground_truth_slices)}"
    
    corrected_ids = [s["slice_id"] for s in corrected_slices]
    gt_ids = [s["slice_id"] for s in ground_truth_slices]
    
    assert corrected_ids == gt_ids, \
        "Slice ID mismatch between corrected and ground truth"
    
    # Stack slices into 3D volume
    corrected_volume = np.stack([s["mask"] for s in corrected_slices], axis=0)
    gt_volume = np.stack([s["mask"] for s in ground_truth_slices], axis=0)
    
    # Compute Dice on full volume
    dice = compute_dice(corrected_volume, gt_volume)
    
    return dice


def evaluate_corrected_volume(
    corrected_data: Dict,
    ground_truth_data: Dict,
    verbose: bool = False
) -> Dict:
    """
    Evaluate corrected volume against ground truth.
    
    EVALUATION ONLY - No decision-making.
    
    Args:
        corrected_data: Phase 7 corrected volume artifact
                        Must contain "patient_id" and "corrected_slices"
        ground_truth_data: Phase 2 ground truth slices
                           Must contain "patient_id" and "slices"
        verbose: Print evaluation details
        
    Returns:
        Dictionary with evaluation results
        
    Format:
        {
          "patient_id": str,
          "dice": float,
          "num_slices": int,
          "num_corrected": int
        }
    """
    # Verify patient_id match
    assert corrected_data["patient_id"] == ground_truth_data["patient_id"], \
        "Patient ID mismatch between corrected and ground truth"
    
    patient_id = corrected_data["patient_id"]
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Evaluating patient: {patient_id}")
        print(f"{'='*60}")
    
    # Get slices
    corrected_slices = corrected_data["corrected_slices"]
    gt_slices = ground_truth_data["slices"]
    
    # Compute Dice
    dice = compute_volume_dice(corrected_slices, gt_slices)
    
    # Get correction info
    num_slices = len(corrected_slices)
    num_corrected = len(corrected_data.get("selected_slices", []))
    
    if verbose:
        print(f"   Total slices: {num_slices}")
        print(f"   Corrected slices: {num_corrected}")
        print(f"   Dice score: {dice:.4f}")
        print(f"{'='*60}")
    
    return {
        "patient_id": patient_id,
        "dice": dice,
        "num_slices": num_slices,
        "num_corrected": num_corrected
    }


def evaluate_baseline_volume(
    predictions_data: Dict,
    ground_truth_data: Dict,
    verbose: bool = False
) -> Dict:
    """
    Evaluate baseline (uncorrected) predictions against ground truth.
    
    This is the "No Correction" baseline (Budget B = 0).
    
    Args:
        predictions_data: Phase 3 prediction artifacts
        ground_truth_data: Phase 2 ground truth slices
        verbose: Print evaluation details
        
    Returns:
        Dictionary with evaluation results
    """
    # Verify patient_id match
    assert predictions_data["patient_id"] == ground_truth_data["patient_id"], \
        "Patient ID mismatch between predictions and ground truth"
    
    patient_id = predictions_data["patient_id"]
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Evaluating baseline (no correction): {patient_id}")
        print(f"{'='*60}")
    
    # Get slices
    pred_slices = predictions_data["slices"]
    gt_slices = ground_truth_data["slices"]
    
    # Verify alignment
    assert len(pred_slices) == len(gt_slices), \
        f"Slice count mismatch: {len(pred_slices)} vs {len(gt_slices)}"
    
    pred_ids = [s["slice_id"] for s in pred_slices]
    gt_ids = [s["slice_id"] for s in gt_slices]
    
    assert pred_ids == gt_ids, \
        "Slice ID mismatch between predictions and ground truth"
    
    # Stack into volumes
    pred_volume = np.stack([s["pred_mask"] for s in pred_slices], axis=0)
    gt_volume = np.stack([s["mask"] for s in gt_slices], axis=0)
    
    # Compute Dice
    dice = compute_dice(pred_volume, gt_volume)
    
    num_slices = len(pred_slices)
    
    if verbose:
        print(f"   Total slices: {num_slices}")
        print(f"   Corrected slices: 0 (baseline)")
        print(f"   Dice score: {dice:.4f}")
        print(f"{'='*60}")
    
    return {
        "patient_id": patient_id,
        "dice": dice,
        "num_slices": num_slices,
        "num_corrected": 0
    }


if __name__ == "__main__":
    # Test Dice computation
    print("Testing Dice Computation...")
    
    # Test case 1: Perfect overlap
    mask1 = np.array([[1, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.uint8)
    mask2 = np.array([[1, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.uint8)
    dice = compute_dice(mask1, mask2)
    assert dice == 1.0, f"Perfect overlap should give Dice=1.0, got {dice}"
    print(f"✅ Test 1 passed: Perfect overlap → Dice = {dice:.4f}")
    
    # Test case 2: No overlap
    mask1 = np.array([[1, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.uint8)
    mask2 = np.array([[0, 0, 1], [0, 1, 1], [1, 1, 1]], dtype=np.uint8)
    dice = compute_dice(mask1, mask2)
    assert dice == 0.0, f"No overlap should give Dice=0.0, got {dice}"
    print(f"✅ Test 2 passed: No overlap → Dice = {dice:.4f}")
    
    # Test case 3: Partial overlap
    mask1 = np.array([[1, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.uint8)
    mask2 = np.array([[1, 0, 0], [1, 1, 0], [0, 0, 0]], dtype=np.uint8)
    dice = compute_dice(mask1, mask2)
    expected = (2 * 2) / (3 + 3)  # 2 intersection, 3+3 union
    assert abs(dice - expected) < 1e-6, f"Expected Dice={expected:.4f}, got {dice:.4f}"
    print(f"✅ Test 3 passed: Partial overlap → Dice = {dice:.4f}")
    
    # Test case 4: Both empty
    mask1 = np.zeros((3, 3), dtype=np.uint8)
    mask2 = np.zeros((3, 3), dtype=np.uint8)
    dice = compute_dice(mask1, mask2)
    assert dice == 1.0, f"Both empty should give Dice=1.0, got {dice}"
    print(f"✅ Test 4 passed: Both empty → Dice = {dice:.4f}")
    
    # Test case 5: One empty
    mask1 = np.array([[1, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.uint8)
    mask2 = np.zeros((3, 3), dtype=np.uint8)
    dice = compute_dice(mask1, mask2)
    assert dice == 0.0, f"One empty should give Dice=0.0, got {dice}"
    print(f"✅ Test 5 passed: One empty → Dice = {dice:.4f}")
    
    print(f"\n✅ All Dice computation tests passed!")
