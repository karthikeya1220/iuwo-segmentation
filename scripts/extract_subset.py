#!/usr/bin/env python3
"""
Selective BraTS Patient Extraction from ZIP Archive

This script extracts exactly N patients from a BraTS ZIP archive
WITHOUT unzipping the entire archive to disk.

Hard Constraints:
- No full archive extraction
- Deterministic patient selection
- Preserves original folder structure
- Validates extraction completeness

Usage:
    python extract_subset.py --archive brats_dataset.zip --n 10 --output data/raw_subset/
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Set, Dict
from zipfile import ZipFile, BadZipFile
from collections import defaultdict


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('extraction.log')
    ]
)
logger = logging.getLogger(__name__)


class BraTSExtractor:
    """Handles selective extraction of BraTS patients from ZIP archives."""
    
    def __init__(self, archive_path: Path, output_dir: Path):
        """
        Initialize extractor.
        
        Args:
            archive_path: Path to BraTS ZIP archive
            output_dir: Target directory for extracted patients
        """
        self.archive_path = archive_path
        self.output_dir = output_dir
        self.patient_files: Dict[str, List[str]] = defaultdict(list)
        
    def validate_archive(self) -> bool:
        """
        Validate ZIP archive integrity.
        
        Returns:
            True if archive is valid, False otherwise
        """
        try:
            with ZipFile(self.archive_path, 'r') as zf:
                # Test archive integrity
                corrupt = zf.testzip()
                if corrupt:
                    logger.error(f"Corrupt file detected: {corrupt}")
                    return False
            logger.info(f"Archive validation passed: {self.archive_path}")
            return True
        except BadZipFile:
            logger.error(f"Invalid ZIP archive: {self.archive_path}")
            return False
        except FileNotFoundError:
            logger.error(f"Archive not found: {self.archive_path}")
            return False
    
    def discover_patients(self) -> List[str]:
        """
        Discover all patient IDs in the archive.
        
        BraTS archives typically have structure:
            BraTS-GLI-00000-000/
                BraTS-GLI-00000-000-t1c.nii.gz
                BraTS-GLI-00000-000-t1n.nii.gz
                ...
        
        Returns:
            Sorted list of unique patient IDs
        """
        logger.info("Discovering patients in archive...")
        
        with ZipFile(self.archive_path, 'r') as zf:
            all_paths = zf.namelist()
            
            # Extract patient IDs from paths
            patient_ids: Set[str] = set()
            
            for path in all_paths:
                # Skip directory entries and hidden files
                if path.endswith('/') or '/__MACOSX' in path or '/._' in path:
                    continue
                
                # Parse patient ID from path
                # Expected format: <patient_id>/<patient_id>-<modality>.nii.gz
                parts = Path(path).parts
                if len(parts) >= 2:
                    patient_id = parts[0]
                    patient_ids.add(patient_id)
                    self.patient_files[patient_id].append(path)
        
        # Sort for deterministic selection
        sorted_patients = sorted(patient_ids)
        logger.info(f"Discovered {len(sorted_patients)} patients")
        
        return sorted_patients
    
    def select_patients(self, all_patients: List[str], n: int) -> List[str]:
        """
        Select exactly N patients deterministically.
        
        Args:
            all_patients: List of all available patient IDs
            n: Number of patients to select
        
        Returns:
            List of selected patient IDs
        
        Raises:
            ValueError: If N exceeds available patients
        """
        if n > len(all_patients):
            raise ValueError(
                f"Requested {n} patients but only {len(all_patients)} available"
            )
        
        # Deterministic selection: first N patients (alphabetically sorted)
        selected = all_patients[:n]
        logger.info(f"Selected {len(selected)} patients: {selected[:5]}...")
        
        return selected
    
    def extract_patients(self, patient_ids: List[str]) -> Dict[str, int]:
        """
        Extract selected patients from archive.
        
        Args:
            patient_ids: List of patient IDs to extract
        
        Returns:
            Dictionary mapping patient_id -> number of files extracted
        """
        logger.info(f"Extracting {len(patient_ids)} patients to {self.output_dir}")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        extraction_summary = {}
        
        with ZipFile(self.archive_path, 'r') as zf:
            for patient_id in patient_ids:
                patient_files = self.patient_files[patient_id]
                
                if not patient_files:
                    logger.warning(f"No files found for patient: {patient_id}")
                    extraction_summary[patient_id] = 0
                    continue
                
                # Extract all files for this patient
                extracted_count = 0
                for file_path in patient_files:
                    try:
                        zf.extract(file_path, self.output_dir)
                        extracted_count += 1
                    except Exception as e:
                        logger.error(f"Failed to extract {file_path}: {e}")
                
                extraction_summary[patient_id] = extracted_count
                logger.info(f"Extracted {patient_id}: {extracted_count} files")
        
        return extraction_summary
    
    def validate_extraction(
        self, 
        patient_ids: List[str], 
        extraction_summary: Dict[str, int]
    ) -> bool:
        """
        Validate that all patients were extracted completely.
        
        Args:
            patient_ids: List of patient IDs that should be extracted
            extraction_summary: Dictionary of extraction results
        
        Returns:
            True if all patients extracted successfully
        """
        logger.info("Validating extraction completeness...")
        
        all_valid = True
        
        for patient_id in patient_ids:
            expected_files = len(self.patient_files[patient_id])
            extracted_files = extraction_summary.get(patient_id, 0)
            
            if extracted_files == 0:
                logger.error(f"FAILED: {patient_id} - no files extracted")
                all_valid = False
            elif extracted_files < expected_files:
                logger.warning(
                    f"INCOMPLETE: {patient_id} - "
                    f"{extracted_files}/{expected_files} files"
                )
                all_valid = False
            else:
                logger.info(f"VALID: {patient_id} - {extracted_files} files")
        
        return all_valid
    
    def write_extraction_log(
        self, 
        patient_ids: List[str], 
        extraction_summary: Dict[str, int]
    ) -> None:
        """
        Write extraction log to output directory.
        
        Args:
            patient_ids: List of extracted patient IDs
            extraction_summary: Dictionary of extraction results
        """
        log_path = self.output_dir / 'EXTRACTION_LOG.txt'
        
        with open(log_path, 'w') as f:
            f.write("BraTS Subset Extraction Log\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Archive: {self.archive_path}\n")
            f.write(f"Output Directory: {self.output_dir}\n")
            f.write(f"Total Patients Extracted: {len(patient_ids)}\n\n")
            f.write("Patient IDs:\n")
            f.write("-" * 50 + "\n")
            
            for patient_id in patient_ids:
                file_count = extraction_summary.get(patient_id, 0)
                f.write(f"{patient_id}: {file_count} files\n")
        
        logger.info(f"Extraction log written to {log_path}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Extract N patients from BraTS ZIP archive'
    )
    parser.add_argument(
        '--archive',
        type=Path,
        required=True,
        help='Path to BraTS ZIP archive'
    )
    parser.add_argument(
        '--n',
        type=int,
        required=True,
        help='Number of patients to extract'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('data/raw_subset'),
        help='Output directory for extracted patients'
    )
    
    args = parser.parse_args()
    
    # Initialize extractor
    extractor = BraTSExtractor(args.archive, args.output)
    
    # Step 1: Validate archive
    if not extractor.validate_archive():
        logger.error("Archive validation failed. Aborting.")
        sys.exit(1)
    
    # Step 2: Discover patients
    all_patients = extractor.discover_patients()
    
    if not all_patients:
        logger.error("No patients found in archive. Aborting.")
        sys.exit(1)
    
    # Step 3: Select N patients
    try:
        selected_patients = extractor.select_patients(all_patients, args.n)
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)
    
    # Step 4: Extract patients
    extraction_summary = extractor.extract_patients(selected_patients)
    
    # Step 5: Validate extraction
    is_valid = extractor.validate_extraction(selected_patients, extraction_summary)
    
    # Step 6: Write log
    extractor.write_extraction_log(selected_patients, extraction_summary)
    
    # Final status
    if is_valid:
        logger.info("✓ Extraction completed successfully")
        sys.exit(0)
    else:
        logger.error("✗ Extraction completed with errors")
        sys.exit(1)


if __name__ == '__main__':
    main()
