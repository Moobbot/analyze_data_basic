import json
import argparse
import sys
import os
from collections import OrderedDict

# Define the target order of keys
# This specific order is for "Trade Types" and "Contract Types" (e.g., Trade Confirmation, Contract Note).
TARGET_ORDER = [
    "Client name",
    "Account no.",
    "Name/ Security",
    "Securities ID",
    "Currency",
    "Transaction Type",
    "Trade Date",
    "Settlement Date",
    "Quantity",
    "Foreign Unit Price",
    "Foreign Gross Consideration",
    "Accrued Interest",
    "Foreign Net Consideration",
    "Net Consideration",
    "Exec Commission",
    "Research Commission",
    "Total Commission",
    "Local Fee",
    "Local Tax",
    "Stamp Duty",
    "Foreign GST",
    "GST Equivalent",
    "GST ON (SR)",
]


def reorder_json(input_path, output_path=None):
    # Check if input is a directory
    if os.path.isdir(input_path):
        process_directory(input_path, output_path)
    elif os.path.isfile(input_path):
        process_file(input_path, output_path)
    else:
        print(f"Error: {input_path} is not a valid file or directory.")


def process_directory(input_dir, output_dir=None):
    print(f"Processing directory: {input_dir}")
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except OSError as e:
            print(f"Error creating output directory {output_dir}: {e}")
            return

    # Walk through directory
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(".json"):
                file_path = os.path.join(root, file)

                if output_dir:
                    # Calculate relative path to maintain structure
                    rel_path = os.path.relpath(file_path, input_dir)
                    save_path = os.path.join(output_dir, rel_path)

                    # Ensure destination directory exists
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                else:
                    save_path = None  # Will imply overwrite in process_file

                print(f"Processing file: {file_path}")
                process_file(file_path, save_path)


def process_file(input_path, output_path=None):
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return

    # If the input is a list, process each item
    if isinstance(data, list):
        processed_data = [process_single_item(item) for item in data]
    else:
        processed_data = process_single_item(data)

    if output_path:
        save_path = output_path
    else:
        save_path = input_path  # Overwrite if no output path specified

    try:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(processed_data, f, indent=4, ensure_ascii=False)
        print(f"Successfully processed and saved to {save_path}")
    except Exception as e:
        print(f"Error writing to {save_path}: {e}")


def process_single_item(item):
    if not isinstance(item, dict):
        return item

    ordered_item = OrderedDict()

    # Group all entries by their lowercase key handle case-insensitivity consistency
    # key_lower -> list of (original_key, value)
    candidates = {}
    for k, v in item.items():
        k_lower = k.lower()
        if k_lower not in candidates:
            candidates[k_lower] = []
        candidates[k_lower].append((k, v))

    used_keys = set()

    # Add keys in target order
    for target_key in TARGET_ORDER:
        target_key_lower = target_key.lower()

        final_value = None

        if target_key_lower in candidates:
            # We found matches (one or more)
            # Iterate through them and pick the first non-None value if available
            # Also mark all corresponding original keys as used so they don't appear in leftovers

            found_valid = False
            for orig_k, val in candidates[target_key_lower]:
                used_keys.add(orig_k)
                if val is not None and not found_valid:
                    final_value = val
                    found_valid = True  # Stop looking for values, but continue marking keys as used

            ordered_item[target_key] = final_value
        else:
            # Key completely missing
            ordered_item[target_key] = None

    # Add any remaining keys that were in the original item but not in target order
    for key, value in item.items():
        if key not in used_keys:
            ordered_item[key] = value

    return ordered_item


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reorder JSON keys.")
    parser.add_argument("input_path", help="Path to input JSON file or directory")
    parser.add_argument(
        "output_path",
        nargs="?",
        help="Path to output JSON file or directory (optional)",
    )

    args = parser.parse_args()

    reorder_json(args.input_path, args.output_path)
