"""
Script to standardize "Transaction Type" field in JSON files.
Handles both JSON objects and arrays of objects.
"""

import os
import json
import argparse
import sys

# Add parent directory to path (2 levels up from scripts/cleaning/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from lib.validation_config import TRANSACTION_KEYWORDS


def standardize_transaction_type(transaction_value):
    """Standardize transaction type to BUY or SELL based on keywords."""
    if not transaction_value or not isinstance(transaction_value, str):
        return transaction_value

    # Check against BUY keywords
    for keyword in TRANSACTION_KEYWORDS["BUY"]:
        if keyword.lower() in transaction_value.lower():
            return "BUY"

    # Check against SELL keywords
    for keyword in TRANSACTION_KEYWORDS["SELL"]:
        if keyword.lower() in transaction_value.lower():
            return "SELL"

    return transaction_value


def process_item(item):
    """Process a single JSON object to standardize transaction type."""
    if not isinstance(item, dict):
        return False

    # Check for transaction type field
    field_name = None
    if "Transaction Type" in item:
        field_name = "Transaction Type"
    elif "Transaction type" in item:
        field_name = "Transaction type"

    if field_name is None:
        return False

    old_value = item[field_name]
    new_value = standardize_transaction_type(old_value)

    # Check if anything needs to change
    if (old_value != new_value) or (field_name != "Transaction Type"):
        # Remove old field if lowercase
        if field_name == "Transaction type":
            del item[field_name]

        # Set with correct capitalization
        item["Transaction Type"] = new_value
        return True

    return False


def process_json_file(input_path, output_path=None):
    """Process a single JSON file."""
    if output_path is None:
        output_path = input_path

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Handle both object and array formats
        changed = False
        if isinstance(data, list):
            for item in data:
                if process_item(item):
                    changed = True
        elif isinstance(data, dict):
            changed = process_item(data)

        if changed:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✓ Updated: {input_path}")
        else:
            print(f"○ No change: {input_path}")

        return (True, changed, None, None)

    except json.JSONDecodeError as e:
        print(f"✗ JSON Error in {input_path}: {e}")
        return (False, False, None, None)
    except Exception as e:
        print(f"✗ Error processing {input_path}: {e}")
        return (False, False, None, None)


def process_folder(input_folder, output_folder=None):
    """Process all JSON files in a folder recursively."""
    stats = {"total": 0, "changed": 0, "unchanged": 0, "errors": 0}

    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if filename.lower().endswith(".json"):
                input_path = os.path.join(root, filename)

                if output_folder:
                    rel_path = os.path.relpath(input_path, input_folder)
                    output_path = os.path.join(output_folder, rel_path)
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                else:
                    output_path = None

                success, changed, _, _ = process_json_file(input_path, output_path)

                stats["total"] += 1
                if success:
                    if changed:
                        stats["changed"] += 1
                    else:
                        stats["unchanged"] += 1
                else:
                    stats["errors"] += 1

    return stats


def main():
    parser = argparse.ArgumentParser(description="Standardize Transaction Type field")
    parser.add_argument("input", help="Input JSON file or folder")
    parser.add_argument("--output", "-o", help="Output folder", default=None)
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input path not found: {args.input}")
        return

    if os.path.isfile(args.input):
        process_json_file(args.input, args.output)
    elif os.path.isdir(args.input):
        print(f"Processing folder: {args.input}")
        print("Note: Overwriting input files\n")

        stats = process_folder(args.input, args.output)

        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  Total: {stats['total']}")
        print(f"  ✓ Changed: {stats['changed']}")
        print(f"  ○ Unchanged: {stats['unchanged']}")
        print(f"  ✗ Errors: {stats['errors']}")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
