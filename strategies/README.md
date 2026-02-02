# Phase 3.3 — Baseline Slice Selection Strategies

**NON-OPTIMIZED baseline strategies for slice selection.**

This module implements simple, interpretable baseline strategies that do NOT use optimization, uncertainty estimation, or impact estimation.

---

## Available Strategies

### 1. Random Selection

**File:** `random_selection.py`

**Description:** Selects B slices uniformly at random.

**Properties:**

- Stochastic (requires random seed)
- No domain knowledge
- Lower bound baseline
- All slices have equal probability

**Usage:**

```python
from strategies.random_selection import RandomSelection

strategy = RandomSelection(seed=42)
selected_ids = strategy.select(slices, budget=10)
```

---

### 2. Uniform Selection

**File:** `uniform_selection.py`

**Description:** Selects B slices at evenly-spaced intervals across volume depth.

**Properties:**

- Deterministic
- Spatial coverage across depth
- No domain knowledge
- Common medical imaging baseline

**Usage:**

```python
from strategies.uniform_selection import UniformSelection

strategy = UniformSelection()
selected_ids = strategy.select(slices, budget=10)
```

---

### 3. Oracle Selection (UPPER BOUND ONLY)

**File:** `oracle_selection.py`

**Description:** Selects B slices with highest ground truth error.

⚠️ **WARNING: This is NOT a real method!** ⚠️

**Properties:**

- Uses ground truth (NOT available in practice)
- Deterministic (given predictions and GT)
- Upper bound on achievable performance
- **Must be labeled as "UPPER BOUND" in all results**

**Usage:**

```python
from strategies.oracle_selection import OracleSelection

# UPPER BOUND ONLY - requires ground truth
strategy = OracleSelection()
selected_ids = strategy.select(slices, budget=10)
```

**Important:** Never treat oracle selection as a real method. It is used ONLY to establish an upper bound for comparison.

---

## Strategy Interface

All strategies implement the same interface defined in `base_strategy.py`:

```python
class SliceSelectionStrategy(ABC):
    def select(
        self,
        slices: List[Dict],
        budget: int
    ) -> List[int]:
        """
        Select slices for expert review under budget constraint.
        
        Args:
            slices: List of slice metadata dictionaries
            budget: Maximum number of slices to select (B)
            
        Returns:
            List of selected slice_ids (length <= budget)
        """
        pass
```

### Input Format

Each slice dictionary must contain at minimum:

```python
{
    "slice_id": int,  # Required for all strategies
    # Additional fields depend on strategy
}
```

For oracle selection, also required:

```python
{
    "slice_id": int,
    "pred_mask": np.ndarray,  # (H, W), uint8
    "gt_mask": np.ndarray     # (H, W), uint8
}
```

### Output Format

List of selected slice IDs:

```python
[3, 7, 12, 18, 25]  # Example with budget=5
```

### Constraints

All strategies must satisfy:

- Return at most `budget` slice_ids
- slice_ids must be valid (exist in input)
- slice_ids must be unique (no duplicates)
- Order does not matter

---

## Scope Limitations (Phase 3 Only)

These strategies are **NON-OPTIMIZED baselines**. They do NOT include:

❌ Uncertainty estimation  
❌ Impact estimation  
❌ Expert correction  
❌ Dice improvement optimization  
❌ Active learning  
❌ Model retraining  

These features are out of scope for Phase 3.

---

## Comparison Framework

To compare strategies fairly:

1. **Same Budget:** Use identical budget B across all strategies
2. **Same Patients:** Test on same patient set
3. **Same Model:** Use same frozen segmentation model
4. **Same Metrics:** Evaluate with same Dice computation
5. **Multiple Seeds:** For stochastic strategies (random), test with multiple seeds

Example comparison:

```python
strategies = [
    RandomSelection(seed=42),
    UniformSelection(),
    OracleSelection()  # UPPER BOUND
]

for strategy in strategies:
    selected = strategy.select(slices, budget=10)
    # Evaluate performance (Phase 5)
```

---

## Testing

Each strategy includes built-in tests. Run with:

```bash
# Test random selection
python strategies/random_selection.py

# Test uniform selection
python strategies/uniform_selection.py

# Test oracle selection
python strategies/oracle_selection.py
```

---

## Adding New Strategies

To add a new strategy:

1. **Inherit from `SliceSelectionStrategy`:**

   ```python
   from strategies.base_strategy import SliceSelectionStrategy
   
   class MyStrategy(SliceSelectionStrategy):
       def __init__(self, seed=42):
           super().__init__(name="My Strategy", seed=seed)
       
       def select(self, slices, budget):
           # Implementation
           pass
   ```

2. **Implement `select()` method**
3. **Validate selection** using `self.validate_selection()`
4. **Add tests** in `if __name__ == "__main__"` block
5. **Document** assumptions and limitations

---

## File Structure

```
strategies/
├── base_strategy.py         # Abstract base class
├── random_selection.py      # Random baseline
├── uniform_selection.py     # Uniform baseline
├── oracle_selection.py      # Oracle upper bound
└── README.md                # This file
```

---

## Design Rationale

### Why These Baselines?

1. **Random Selection**
   - Simplest possible approach
   - No assumptions about data
   - Lower bound for comparison

2. **Uniform Selection**
   - Common medical imaging practice
   - Ensures spatial coverage
   - Deterministic and interpretable

3. **Oracle Selection**
   - Upper bound on performance
   - Shows maximum achievable improvement
   - Guides expectations for optimized methods

### Why No Uncertainty-Based Selection?

Uncertainty-based selection (e.g., entropy, variance) is NOT included in Phase 3 because:

- It requires uncertainty estimation (Phase 4)
- It is an optimized method, not a baseline
- It conflates prediction quality with selection strategy

Phase 3 focuses on **NON-OPTIMIZED** baselines only.

---

## Important Notes

1. **Phase 3 Scope**
   - These are baseline strategies only
   - No optimization logic
   - No uncertainty or impact estimation

2. **Oracle is NOT a Real Method**
   - Uses ground truth (unavailable in practice)
   - Upper bound only
   - Must be clearly labeled in results

3. **Fair Comparison**
   - All strategies use same interface
   - Same budget constraint
   - Same evaluation metrics

4. **Reproducibility**
   - Random strategies use fixed seeds
   - Deterministic strategies always produce same output
   - All strategies are tested

---

**Last Updated:** 2026-02-02  
**Phase:** 3.3 (Baseline Slice Selection Strategies)  
**Status:** Complete
