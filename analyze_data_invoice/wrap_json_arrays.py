#!/usr/bin/env python3
"""
Script để wrap JSON objects thành arrays cho invoice data
Chuyển từ {} sang [] format để support multipage invoices
"""

import sys
from pathlib import Path

# Add parent directory to path to import common_lib
sys.path.insert(0, str(Path(__file__).parent.parent))

from common_lib.wrap_json_arrays import wrap_json_in_folders

# Đường dẫn đến datasets
BASE_DIR = Path(__file__).parent
DATASETS = [
    BASE_DIR / "datasets" / "test-set-100" / "labels",
    BASE_DIR / "datasets" / "test-set-100-muti-page" / "labels",
]


def main():
    print("=" * 80)
    print("JSON ARRAY WRAPPER FOR INVOICE DATA")
    print("=" * 80)
    print("\nThis script will wrap all JSON objects {} into arrays []")
    print("to support multipage invoice format.\n")

    # Process datasets
    results = wrap_json_in_folders(DATASETS, recursive=True, verbose=True)

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Folders processed: {results['folders_processed']}")
    print(f"Total fixed:       {results['total_fixed']}")
    print(f"Already arrays:    {results['total_already']}")
    print(f"Total errors:      {results['total_errors']}")
    print("=" * 80)
    print("✓ Wrapping completed!")
    print("=" * 80)


if __name__ == "__main__":
    # Confirm before running
    print("⚠️  WARNING: This will modify JSON files in place!")
    print("   Make sure you have a backup before proceeding.\n")

    response = input("Do you want to continue? (yes/no): ").strip().lower()
    if response in ["yes", "y"]:
        main()
    else:
        print("❌ Operation cancelled.")
