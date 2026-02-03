#!/bin/bash
# ============================================================================
# BraTS 2024 Selective Extraction (Bash Version)
# ============================================================================
# Extracts predefined patient subset from archive.zip without full extraction
#
# Usage:
#   ./scripts/extract_brats_subset.sh [--dry-run]
#
# Requirements:
#   - unzip (standard on macOS/Linux)
# ============================================================================

set -e

# Configuration
ARCHIVE="/Users/darshankarthikeya/Downloads/archive.zip"
OUTPUT_DIR="data/brats_subset"
DRY_RUN=false

# Parse arguments
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
fi

# Patient lists
TRAINING_PATIENTS=(
    "BraTS-GLI-00005-100" "BraTS-GLI-00005-101"
    "BraTS-GLI-00006-100" "BraTS-GLI-00006-101"
    "BraTS-GLI-00020-100" "BraTS-GLI-00020-101"
    "BraTS-GLI-00027-100" "BraTS-GLI-00027-101"
    "BraTS-GLI-00033-100" "BraTS-GLI-00033-101"
    "BraTS-GLI-00046-100" "BraTS-GLI-00046-101"
    "BraTS-GLI-00060-100" "BraTS-GLI-00060-101"
    "BraTS-GLI-00063-100" "BraTS-GLI-00063-101"
    "BraTS-GLI-00078-100" "BraTS-GLI-00078-101"
    "BraTS-GLI-00080-100" "BraTS-GLI-00080-101"
)

EVALUATION_PATIENTS=(
    "BraTS-GLI-00008-103"
    "BraTS-GLI-00009-100"
    "BraTS-GLI-00085-100"
)

# Combine all patients
ALL_PATIENTS=("${TRAINING_PATIENTS[@]}" "${EVALUATION_PATIENTS[@]}")

# ============================================================================
# Functions
# ============================================================================

print_header() {
    echo "======================================================================"
    echo "$1"
    echo "======================================================================"
}

# ============================================================================
# Main
# ============================================================================

print_header "BraTS 2024 Selective Extraction (Bash)"

# Verify archive exists
if [[ ! -f "$ARCHIVE" ]]; then
    echo "❌ Archive not found: $ARCHIVE"
    exit 1
fi

echo "Archive: $ARCHIVE"
echo "Output:  $OUTPUT_DIR"
echo "Mode:    $([ "$DRY_RUN" = true ] && echo "DRY RUN" || echo "EXTRACTION")"
echo "Patients: ${#ALL_PATIENTS[@]} total"
echo ""

# Create output directory
if [[ "$DRY_RUN" = false ]]; then
    mkdir -p "$OUTPUT_DIR"
fi

# Statistics
PATIENTS_FOUND=0
FILES_EXTRACTED=0

# Process each patient
for PATIENT in "${ALL_PATIENTS[@]}"; do
    echo -n "Processing: $PATIENT... "
    
    # List files for this patient in archive
    # Use unzip -Z1 to list files (quiet mode)
    PATIENT_FILES=$(unzip -Z1 "$ARCHIVE" "*${PATIENT}*.nii*" 2>/dev/null || true)
    
    if [[ -z "$PATIENT_FILES" ]]; then
        echo "❌ NOT FOUND"
        continue
    fi
    
    # Count files
    FILE_COUNT=$(echo "$PATIENT_FILES" | wc -l | tr -d ' ')
    
    if [[ "$DRY_RUN" = true ]]; then
        echo "✅ $FILE_COUNT files (dry run)"
        echo "$PATIENT_FILES" | sed 's/^/  [DRY] /'
    else
        # Extract files
        # Use -j to junk paths, then reconstruct manually
        # Or use -d to specify output directory
        
        # Create patient directory
        mkdir -p "$OUTPUT_DIR/$PATIENT"
        
        # Extract each file
        echo "$PATIENT_FILES" | while read -r FILE; do
            # Extract to patient directory
            unzip -q -j "$ARCHIVE" "$FILE" -d "$OUTPUT_DIR/$PATIENT" 2>/dev/null || true
        done
        
        echo "✅ $FILE_COUNT files"
    fi
    
    PATIENTS_FOUND=$((PATIENTS_FOUND + 1))
    FILES_EXTRACTED=$((FILES_EXTRACTED + FILE_COUNT))
done

# Summary
echo ""
print_header "EXTRACTION SUMMARY"
echo "Patients found:    $PATIENTS_FOUND/${#ALL_PATIENTS[@]}"
echo "Files extracted:   $FILES_EXTRACTED"

if [[ "$DRY_RUN" = false ]]; then
    # Calculate total size
    TOTAL_SIZE=$(du -sh "$OUTPUT_DIR" 2>/dev/null | cut -f1 || echo "N/A")
    echo "Total size:        $TOTAL_SIZE"
    echo ""
    echo "✅ Extraction complete: $OUTPUT_DIR"
else
    echo ""
    echo "ℹ️  Dry run complete. Run without --dry-run to extract."
fi

echo "======================================================================"
