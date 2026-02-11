#!/usr/bin/env python3
"""
index_validator.py - Knowledge Index Validator

Validates that knowledge_index.json exists, all referenced files exist,
and SHA256 hashes match the actual files.

Exit codes:
    0 - All validations passed
    1 - Warnings or mismatches found
    2 - Critical error (missing index file)
"""

import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

# Configuration
SCRIPT_DIR = Path(__file__).parent.absolute()
INDEX_FILE = SCRIPT_DIR / "knowledge_index.json"
KNOWLEDGE_DIR = SCRIPT_DIR / "knowledge"


def log(level: str, message: str) -> None:
    """Log a message with level."""
    prefix = {
        "INFO": "✓",
        "WARN": "⚠",
        "ERROR": "✗"
    }.get(level, "•")
    print(f"{prefix} [{level}] {message}")


def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def load_index() -> Dict:
    """Load and parse knowledge_index.json."""
    if not INDEX_FILE.exists():
        log("ERROR", f"Index file not found: {INDEX_FILE}")
        log("ERROR", "Please run boot.sh or boot_preload.py to generate the index")
        sys.exit(2)
    
    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            index_data = json.load(f)
        log("INFO", f"Loaded index: {INDEX_FILE}")
        return index_data
    except json.JSONDecodeError as e:
        log("ERROR", f"Invalid JSON in index file: {e}")
        sys.exit(2)
    except Exception as e:
        log("ERROR", f"Failed to load index: {e}")
        sys.exit(2)


def validate_index_structure(index_data: Dict) -> List[str]:
    """Validate the structure of the index data."""
    warnings = []
    
    required_fields = ["version", "generated_at", "total_files", "files"]
    for field in required_fields:
        if field not in index_data:
            warnings.append(f"Missing required field in index: {field}")
    
    if "files" in index_data and not isinstance(index_data["files"], list):
        warnings.append("'files' field is not a list")
    
    return warnings


def validate_file_entries(files: List[Dict]) -> Tuple[List[str], List[str]]:
    """
    Validate file entries in the index.
    Returns (warnings, errors) lists.
    """
    warnings = []
    errors = []
    
    for i, entry in enumerate(files):
        # Check required fields
        required_fields = ["path", "original", "size", "sha256", "loaded_at"]
        missing_fields = [f for f in required_fields if f not in entry]
        if missing_fields:
            warnings.append(f"File entry {i} missing fields: {missing_fields}")
            continue
        
        file_path = KNOWLEDGE_DIR / entry["path"]
        
        # Check if file exists
        if not file_path.exists():
            errors.append(f"File not found: {entry['path']}")
            continue
        
        # Check file size
        actual_size = file_path.stat().st_size
        expected_size = entry["size"]
        if actual_size != expected_size:
            warnings.append(
                f"Size mismatch for {entry['path']}: "
                f"expected {expected_size}, got {actual_size}"
            )
        
        # Check SHA256 hash
        try:
            actual_hash = compute_sha256(file_path)
            expected_hash = entry["sha256"]
            if actual_hash != expected_hash:
                errors.append(
                    f"Hash mismatch for {entry['path']}: "
                    f"expected {expected_hash[:16]}..., got {actual_hash[:16]}..."
                )
        except Exception as e:
            errors.append(f"Failed to compute hash for {entry['path']}: {e}")
    
    return warnings, errors


def validate_knowledge_directory(files: List[Dict]) -> List[str]:
    """Check for files in knowledge/ that are not in the index."""
    warnings = []
    
    if not KNOWLEDGE_DIR.exists():
        warnings.append(f"Knowledge directory does not exist: {KNOWLEDGE_DIR}")
        return warnings
    
    # Get all files in knowledge directory
    actual_files = set()
    for file_path in KNOWLEDGE_DIR.rglob("*"):
        if file_path.is_file():
            rel_path = file_path.relative_to(KNOWLEDGE_DIR)
            actual_files.add(str(rel_path.as_posix()))
    
    # Get indexed files
    indexed_files = {entry["path"] for entry in files if "path" in entry}
    
    # Find unindexed files
    unindexed = actual_files - indexed_files
    if unindexed:
        warnings.append(f"Found {len(unindexed)} file(s) in knowledge/ not in index:")
        for f in sorted(unindexed)[:5]:  # Show first 5
            warnings.append(f"  - {f}")
        if len(unindexed) > 5:
            warnings.append(f"  ... and {len(unindexed) - 5} more")
    
    return warnings


def main() -> int:
    """Main validation logic."""
    print("=" * 70)
    print("Knowledge Index Validator")
    print("=" * 70)
    print()
    
    # Load index
    index_data = load_index()
    
    # Validate structure
    structure_warnings = validate_index_structure(index_data)
    
    # Get files list
    files = index_data.get("files", [])
    log("INFO", f"Index contains {len(files)} file entries")
    
    # Validate file entries
    file_warnings, file_errors = validate_file_entries(files)
    
    # Check for unindexed files
    dir_warnings = validate_knowledge_directory(files)
    
    # Combine all warnings and errors
    all_warnings = structure_warnings + file_warnings + dir_warnings
    all_errors = file_errors
    
    # Print summary
    print()
    print("=" * 70)
    print("Validation Summary")
    print("=" * 70)
    
    if all_warnings:
        log("WARN", f"Found {len(all_warnings)} warning(s):")
        for warning in all_warnings:
            print(f"  ⚠ {warning}")
        print()
    
    if all_errors:
        log("ERROR", f"Found {len(all_errors)} error(s):")
        for error in all_errors:
            print(f"  ✗ {error}")
        print()
    
    # Determine exit code
    if all_errors:
        log("ERROR", "Validation FAILED with errors")
        return 1
    elif all_warnings:
        log("WARN", "Validation completed with warnings")
        return 1
    else:
        log("INFO", "Validation PASSED - all checks successful!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
