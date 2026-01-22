# convert_string_to_number.py
"""
Convert string numeric values to actual numbers in JSON files.
Handles fields like Foreign GST, GST Equivalent, etc.
"""

import os
import json
import sys
from pathlib import Path

# Fields that should be converted from string to number
NUMERIC_FIELDS = [
    "Foreign GST",
    "GST Equivalent",
    "GST ON (SR)",
    "GST equivalent in SGD",
    "Research Commission",
    "Result Commission",
    "Total Commission",
    "Local Fee",
    "Local Tax",
    "Stamp Duty",
    "Accrued Interest",
    "Foreign Unit Price",
    "Foreign Gross Consideration",
    "Foreign Net Consideration",
    "Net Consideration",
    "Exec Commission",
    "Quantity",
]


def convert_string_to_number(value):
    """
    Convert string value to number.
    Returns None if value is null, empty, or cannot be converted.
    """
    if value is None or value == "":
        return None

    if isinstance(value, (int, float)):
        return value

    if isinstance(value, str):
        # Remove whitespace
        value = value.strip()

        if value == "" or value.lower() == "null":
            return None

        # Remove commas for thousands separator
        value = value.replace(",", "")

        # Try to convert to float
        try:
            num = float(value)
            # If it's a whole number, convert to int
            if num.is_integer():
                return int(num)
            return num
        except ValueError:
            print(f"Warning: Cannot convert '{value}' to number")
            return value  # Return original if conversion fails

    return value


def process_json_file(file_path, dry_run=False):
    """
    Process a single JSON file and convert string numbers to actual numbers.

    Args:
        file_path: Path to JSON file
        dry_run: If True, only show what would be changed without saving

    Returns:
        Dictionary with conversion statistics
    """
    stats = {"file": os.path.basename(file_path), "converted_fields": 0, "errors": []}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Handle both single objects and arrays
        items = data if isinstance(data, list) else [data]

        for item_idx, item in enumerate(items):
            if not isinstance(item, dict):
                continue

            for field in NUMERIC_FIELDS:
                if field in item:
                    original_value = item[field]
                    converted_value = convert_string_to_number(original_value)

                    if original_value != converted_value:
                        if dry_run:
                            print(
                                f"  [{os.path.basename(file_path)}] {field}: '{original_value}' -> {converted_value}"
                            )
                        else:
                            item[field] = converted_value
                        stats["converted_fields"] += 1

        # Save the file if not dry run
        if not dry_run and stats["converted_fields"] > 0:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    except Exception as e:
        stats["errors"].append(str(e))
        print(f"Error processing {file_path}: {e}")

    return stats


def process_folder(folder_path, dry_run=False):
    """
    Process all JSON files in a folder recursively.

    Args:
        folder_path: Path to folder containing JSON files
        dry_run: If True, only show what would be changed

    Returns:
        Overall statistics
    """
    total_files = 0
    total_conversions = 0
    files_with_errors = 0

    print(f"{'[DRY RUN] ' if dry_run else ''}Processing folder: {folder_path}\n")

    # Find all JSON files
    json_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))

    print(f"Found {len(json_files)} JSON files\n")

    for file_path in json_files:
        stats = process_json_file(file_path, dry_run)
        total_files += 1
        total_conversions += stats["converted_fields"]

        if stats["errors"]:
            files_with_errors += 1

        if stats["converted_fields"] > 0:
            print(f"✓ {stats['file']}: {stats['converted_fields']} fields converted")

    print("\n" + "=" * 80)
    print("CONVERSION SUMMARY")
    print("=" * 80)
    print(f"Total Files Processed: {total_files}")
    print(f"Total Conversions: {total_conversions}")
    print(f"Files with Errors: {files_with_errors}")

    if dry_run:
        print("\n⚠️  This was a DRY RUN - no files were modified")
        print("Run without --dry-run flag to apply changes")
    else:
        print("\n✓ Files have been updated")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert string numeric values to actual numbers in JSON files"
    )
    parser.add_argument("input_folder", help="Folder containing JSON files to process")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )

    args = parser.parse_args()

    if not os.path.exists(args.input_folder):
        print(f"Error: Folder not found: {args.input_folder}")
        sys.exit(1)

    process_folder(args.input_folder, args.dry_run)
