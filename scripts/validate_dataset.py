#!/usr/bin/env python3
"""
BraTS Dataset Validation Script

Validates extracted BraTS patient data for completeness and integrity.
Produces machine-readable validation reports suitable for CI/CD and thesis appendices.

Usage:
    python validate_dataset.py --data-dir data/raw_subset --expected-n 15
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib


@dataclass
class FileValidation:
    """Validation result for a single file."""
    path: str
    exists: bool
    size_bytes: int
    is_valid_nifti: bool
    error: Optional[str] = None


@dataclass
class PatientValidation:
    """Validation result for a single patient."""
    patient_id: str
    folder_exists: bool
    required_files_present: bool
    file_count: int
    expected_file_count: int
    files: Dict[str, FileValidation]
    is_valid: bool
    errors: List[str]


@dataclass
class DatasetValidation:
    """Complete dataset validation result."""
    data_dir: str
    timestamp: str
    expected_patient_count: int
    actual_patient_count: int
    valid_patient_count: int
    patients: List[PatientValidation]
    is_valid: bool
    summary: Dict[str, any]


class BraTSValidator:
    """Validates BraTS dataset structure and integrity."""
    
    # Required modalities for BraTS
    REQUIRED_MODALITIES = ['t1c', 't1n', 't2f', 't2w', 'seg']
    
    # Minimum expected file size (in bytes) - BraTS volumes are typically ~28MB
    MIN_FILE_SIZE = 1_000_000  # 1 MB (conservative lower bound)
    MAX_FILE_SIZE = 100_000_000  # 100 MB (conservative upper bound)
    
    def __init__(self, data_dir: Path):
        """
        Initialize validator.
        
        Args:
            data_dir: Path to dataset directory
        """
        self.data_dir = data_dir
        
    def discover_patients(self) -> List[str]:
        """
        Discover all patient folders in data directory.
        
        Returns:
            Sorted list of patient IDs
        """
        if not self.data_dir.exists():
            return []
        
        # Find all directories that match BraTS naming pattern
        patient_dirs = [
            d.name for d in self.data_dir.iterdir() 
            if d.is_dir() and d.name.startswith('BraTS-')
        ]
        
        return sorted(patient_dirs)
    
    def validate_nifti_header(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Validate NIfTI file header without loading full volume.
        
        Args:
            file_path: Path to NIfTI file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # NIfTI-1 header is 348 bytes
            # Check magic bytes at offset 344-348
            with open(file_path, 'rb') as f:
                # Read first 352 bytes (header + magic)
                header = f.read(352)
                
                if len(header) < 348:
                    return False, "File too small to be valid NIfTI"
                
                # Check for NIfTI magic bytes
                # NIfTI-1: "n+1\0" or "ni1\0" at offset 344
                magic = header[344:348]
                
                valid_magic = [
                    b'n+1\x00',  # NIfTI-1 single file
                    b'ni1\x00',  # NIfTI-1 header/image pair
                ]
                
                if magic not in valid_magic:
                    return False, f"Invalid NIfTI magic bytes: {magic}"
                
                return True, None
                
        except Exception as e:
            return False, f"Header validation error: {str(e)}"
    
    def validate_file(self, file_path: Path) -> FileValidation:
        """
        Validate a single file.
        
        Args:
            file_path: Path to file
            
        Returns:
            FileValidation object
        """
        if not file_path.exists():
            return FileValidation(
                path=str(file_path),
                exists=False,
                size_bytes=0,
                is_valid_nifti=False,
                error="File does not exist"
            )
        
        size = file_path.stat().st_size
        
        # Check file size bounds
        if size < self.MIN_FILE_SIZE:
            return FileValidation(
                path=str(file_path),
                exists=True,
                size_bytes=size,
                is_valid_nifti=False,
                error=f"File too small ({size} bytes < {self.MIN_FILE_SIZE})"
            )
        
        if size > self.MAX_FILE_SIZE:
            return FileValidation(
                path=str(file_path),
                exists=True,
                size_bytes=size,
                is_valid_nifti=False,
                error=f"File too large ({size} bytes > {self.MAX_FILE_SIZE})"
            )
        
        # Validate NIfTI header
        is_valid_nifti, error = self.validate_nifti_header(file_path)
        
        return FileValidation(
            path=str(file_path),
            exists=True,
            size_bytes=size,
            is_valid_nifti=is_valid_nifti,
            error=error
        )
    
    def validate_patient(self, patient_id: str) -> PatientValidation:
        """
        Validate a single patient folder.
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            PatientValidation object
        """
        patient_dir = self.data_dir / patient_id
        
        if not patient_dir.exists():
            return PatientValidation(
                patient_id=patient_id,
                folder_exists=False,
                required_files_present=False,
                file_count=0,
                expected_file_count=len(self.REQUIRED_MODALITIES),
                files={},
                is_valid=False,
                errors=[f"Patient folder does not exist: {patient_dir}"]
            )
        
        # Validate each required modality
        file_validations = {}
        errors = []
        
        for modality in self.REQUIRED_MODALITIES:
            # BraTS naming: {patient_id}-{modality}.nii or .nii.gz
            file_name = f"{patient_id}-{modality}.nii"
            file_path = patient_dir / file_name
            
            # Try .nii.gz if .nii doesn't exist
            if not file_path.exists():
                file_name = f"{patient_id}-{modality}.nii.gz"
                file_path = patient_dir / file_name
            
            validation = self.validate_file(file_path)
            file_validations[modality] = validation
            
            if not validation.exists:
                errors.append(f"Missing {modality} modality")
            elif validation.error:
                errors.append(f"{modality}: {validation.error}")
        
        # Check for unexpected files
        expected_files = {f"{patient_id}-{mod}.nii" for mod in self.REQUIRED_MODALITIES}
        expected_files.update({f"{patient_id}-{mod}.nii.gz" for mod in self.REQUIRED_MODALITIES})
        
        actual_files = {f.name for f in patient_dir.iterdir() if f.is_file()}
        unexpected = actual_files - expected_files
        
        if unexpected:
            errors.append(f"Unexpected files: {', '.join(unexpected)}")
        
        # Determine validity
        required_files_present = all(v.exists for v in file_validations.values())
        all_files_valid = all(v.is_valid_nifti for v in file_validations.values())
        is_valid = required_files_present and all_files_valid and len(errors) == 0
        
        return PatientValidation(
            patient_id=patient_id,
            folder_exists=True,
            required_files_present=required_files_present,
            file_count=len([v for v in file_validations.values() if v.exists]),
            expected_file_count=len(self.REQUIRED_MODALITIES),
            files=file_validations,
            is_valid=is_valid,
            errors=errors
        )
    
    def validate_dataset(self, expected_n: int) -> DatasetValidation:
        """
        Validate entire dataset.
        
        Args:
            expected_n: Expected number of patients
            
        Returns:
            DatasetValidation object
        """
        # Discover patients
        patient_ids = self.discover_patients()
        
        # Validate each patient
        patient_validations = [
            self.validate_patient(pid) for pid in patient_ids
        ]
        
        # Count valid patients
        valid_count = sum(1 for p in patient_validations if p.is_valid)
        
        # Generate summary statistics
        summary = {
            'total_patients': len(patient_ids),
            'valid_patients': valid_count,
            'invalid_patients': len(patient_ids) - valid_count,
            'expected_patients': expected_n,
            'patient_count_match': len(patient_ids) == expected_n,
            'total_files': sum(p.file_count for p in patient_validations),
            'expected_total_files': expected_n * len(self.REQUIRED_MODALITIES),
            'missing_files': sum(
                p.expected_file_count - p.file_count 
                for p in patient_validations
            ),
        }
        
        # Overall validity
        is_valid = (
            len(patient_ids) == expected_n and
            valid_count == expected_n
        )
        
        return DatasetValidation(
            data_dir=str(self.data_dir),
            timestamp=datetime.now().isoformat(),
            expected_patient_count=expected_n,
            actual_patient_count=len(patient_ids),
            valid_patient_count=valid_count,
            patients=patient_validations,
            is_valid=is_valid,
            summary=summary
        )
    
    def write_json_report(self, validation: DatasetValidation, output_path: Path):
        """
        Write machine-readable JSON validation report.
        
        Args:
            validation: DatasetValidation object
            output_path: Path to output JSON file
        """
        # Convert dataclasses to dict
        report = {
            'data_dir': validation.data_dir,
            'timestamp': validation.timestamp,
            'expected_patient_count': validation.expected_patient_count,
            'actual_patient_count': validation.actual_patient_count,
            'valid_patient_count': validation.valid_patient_count,
            'is_valid': validation.is_valid,
            'summary': validation.summary,
            'patients': [
                {
                    'patient_id': p.patient_id,
                    'folder_exists': p.folder_exists,
                    'required_files_present': p.required_files_present,
                    'file_count': p.file_count,
                    'expected_file_count': p.expected_file_count,
                    'is_valid': p.is_valid,
                    'errors': p.errors,
                    'files': {
                        modality: {
                            'path': f.path,
                            'exists': f.exists,
                            'size_bytes': f.size_bytes,
                            'is_valid_nifti': f.is_valid_nifti,
                            'error': f.error
                        }
                        for modality, f in p.files.items()
                    }
                }
                for p in validation.patients
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
    
    def write_text_report(self, validation: DatasetValidation, output_path: Path):
        """
        Write human-readable text validation report.
        
        Args:
            validation: DatasetValidation object
            output_path: Path to output text file
        """
        with open(output_path, 'w') as f:
            f.write("BraTS Dataset Validation Report\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"Timestamp: {validation.timestamp}\n")
            f.write(f"Data Directory: {validation.data_dir}\n\n")
            
            f.write("Summary\n")
            f.write("-" * 70 + "\n")
            f.write(f"Expected Patients: {validation.expected_patient_count}\n")
            f.write(f"Actual Patients:   {validation.actual_patient_count}\n")
            f.write(f"Valid Patients:    {validation.valid_patient_count}\n")
            f.write(f"Invalid Patients:  {validation.summary['invalid_patients']}\n")
            f.write(f"Total Files:       {validation.summary['total_files']}\n")
            f.write(f"Missing Files:     {validation.summary['missing_files']}\n\n")
            
            # Overall status
            status = "✓ PASS" if validation.is_valid else "✗ FAIL"
            f.write(f"Overall Status: {status}\n\n")
            
            # Patient details
            f.write("Patient Validation Details\n")
            f.write("-" * 70 + "\n\n")
            
            for patient in validation.patients:
                status_icon = "✓" if patient.is_valid else "✗"
                f.write(f"{status_icon} {patient.patient_id}\n")
                f.write(f"   Files: {patient.file_count}/{patient.expected_file_count}\n")
                
                if patient.errors:
                    f.write(f"   Errors:\n")
                    for error in patient.errors:
                        f.write(f"      - {error}\n")
                
                f.write("\n")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Validate BraTS dataset extraction'
    )
    parser.add_argument(
        '--data-dir',
        type=Path,
        required=True,
        help='Path to dataset directory'
    )
    parser.add_argument(
        '--expected-n',
        type=int,
        required=True,
        help='Expected number of patients'
    )
    parser.add_argument(
        '--output-json',
        type=Path,
        default=None,
        help='Path to JSON validation report (default: {data-dir}/validation.json)'
    )
    parser.add_argument(
        '--output-text',
        type=Path,
        default=None,
        help='Path to text validation report (default: {data-dir}/validation.txt)'
    )
    
    args = parser.parse_args()
    
    # Set default output paths
    if args.output_json is None:
        args.output_json = args.data_dir / 'validation.json'
    if args.output_text is None:
        args.output_text = args.data_dir / 'validation.txt'
    
    # Initialize validator
    validator = BraTSValidator(args.data_dir)
    
    # Run validation
    print(f"Validating dataset: {args.data_dir}")
    print(f"Expected patients: {args.expected_n}")
    print()
    
    validation = validator.validate_dataset(args.expected_n)
    
    # Write reports
    validator.write_json_report(validation, args.output_json)
    validator.write_text_report(validation, args.output_text)
    
    print(f"JSON report written to: {args.output_json}")
    print(f"Text report written to: {args.output_text}")
    print()
    
    # Print summary
    print("Validation Summary")
    print("-" * 50)
    print(f"Expected Patients: {validation.expected_patient_count}")
    print(f"Actual Patients:   {validation.actual_patient_count}")
    print(f"Valid Patients:    {validation.valid_patient_count}")
    print(f"Invalid Patients:  {validation.summary['invalid_patients']}")
    print(f"Total Files:       {validation.summary['total_files']}")
    print(f"Missing Files:     {validation.summary['missing_files']}")
    print()
    
    # Exit with appropriate code
    if validation.is_valid:
        print("✓ Dataset validation PASSED")
        sys.exit(0)
    else:
        print("✗ Dataset validation FAILED")
        sys.exit(1)


if __name__ == '__main__':
    main()
