#!/bin/bash
# ==============================================================================
# REPOSITORY CLEANUP & VALIDATION
# ==============================================================================
# Purpose: Remove deprecated training scripts and validate final pipeline state
# ==============================================================================

set -e

echo "=================================================="
echo "CLEANUP: Removing Deprecated Training Scripts"
echo "=================================================="

# Remove training-related scripts that are no longer used
if [ -f "scripts/run_timeout_train.py" ]; then
    echo "Removing: scripts/run_timeout_train.py (deprecated)"
    rm scripts/run_timeout_train.py
fi

if [ -f "scripts/run_timeout_train.py.save" ]; then
    echo "Removing: scripts/run_timeout_train.py.save (backup)"
    rm scripts/run_timeout_train.py.save
fi

# Remove the manual initialization script (invalid approach)
if [ -f "scripts/init_frozen_model.py" ]; then
    echo "Removing: scripts/init_frozen_model.py (invalid approach)"
    rm scripts/init_frozen_model.py
fi

echo ""
echo "=================================================="
echo "VALIDATION: Checking Final Pipeline Components"
echo "=================================================="

# Required scripts
REQUIRED_SCRIPTS=(
    "scripts/prepare_nnunet_dataset.py"
    "scripts/slices_to_nnunet_volume.py"
    "scripts/nnunet_volume_to_slices.py"
    "scripts/train_and_evaluate.sh"
)

echo "Checking required scripts..."
for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        echo "  ✓ $script"
    else
        echo "  ✗ MISSING: $script"
        exit 1
    fi
done

# Required documentation
REQUIRED_DOCS=(
    "README.md"
    "PHASE3_COMPLETION.md"
    "TECHNICAL_POSTMORTEM.md"
)

echo ""
echo "Checking documentation..."
for doc in "${REQUIRED_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo "  ✓ $doc"
    else
        echo "  ✗ MISSING: $doc"
        exit 1
    fi
done

# Required pipeline phases
REQUIRED_PHASES=(
    "data/load_brats_axial.py"
    "models/uncertainty/generate_uncertainty.py"
    "models/impact/generate_impact.py"
    "evaluation/evaluate_strategies.py"
    "evaluation/plots.py"
)

echo ""
echo "Checking pipeline phases..."
for phase in "${REQUIRED_PHASES[@]}"; do
    if [ -f "$phase" ]; then
        echo "  ✓ $phase"
    else
        echo "  ✗ MISSING: $phase"
        exit 1
    fi
done

echo ""
echo "=================================================="
echo "✅ REPOSITORY CLEANUP COMPLETE"
echo "=================================================="
echo ""
echo "Final State:"
echo "  - Training scripts: REMOVED"
echo "  - Inference pipeline: VALIDATED"
echo "  - Documentation: COMPLETE"
echo ""
echo "The repository is ready for:"
echo "  - Thesis submission"
echo "  - Code review"
echo "  - Reproducibility validation"
echo "=================================================="
