import json
import os
import re
from datetime import datetime
import shutil
import sys

# Assuming script is run from project root or analyze_data_broker directory
# We need to find the root where common_lib is located.
# common_lib is at d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\common_lib
# convert_date_format.py is at analyze_data_broker\scripts

current_dir = os.path.dirname(os.path.abspath(__file__))
# Should go up three levels from scripts/conversion to get to analyze_data_basic root
# Layout:
# analyze_data_basic/
#   analyze_data_broker/
#     scripts/
#       conversion/
#         convert_date_format.py
#   common_lib/
#     date_utils.py

# Go up from scripts/conversion -> scripts -> analyze_data_broker -> analyze_data_basic
root_dir = os.path.abspath(os.path.join(current_dir, "../../../"))

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from common_lib import date_utils
except ImportError:
    # If standard import fails, try direct path adjust just in case
    # common_lib might be a namespace package or something else
    sys.path.append(os.path.abspath(os.path.join(current_dir, "../../../")))
    try:
        from common_lib import date_utils
    except ImportError:
        print(f"Error: Could not import common_lib.date_utils. sys.path: {sys.path}")
        raise


def convert_date_to_mm_dd_yyyy(date_str):
    """Convert date string to MM/DD/YYYY format using common_lib"""
    if date_str is None or str(date_str).strip() == "":
        return date_str

    date_str = str(date_str).strip()

    # Check if already in MM/DD/YYYY format
    if re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", date_str):
        return date_str

    # Use common_lib.date_utils calling validate_date
    is_valid, parsed_date, fmt = date_utils.validate_date(date_str)

    if is_valid and parsed_date:
        return parsed_date.strftime("%m/%d/%Y")

    # If format is unknown, return as is
    print(f"  Warning: Unknown date format '{date_str}', keeping as is")
    return date_str


def convert_dates_in_json_files(directory_path, backup=True):
    """Convert all date formats in JSON files to MM/DD/YYYY"""

    # Create backup directory if requested
    if backup:
        backup_dir = os.path.join(
            os.path.dirname(directory_path), "Trade_Confirmation_backup"
        )
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            print(f"Created backup directory: {backup_dir}")

    # Statistics
    total_files = 0
    modified_files = 0
    total_dates_converted = 0

    # Get all JSON files
    json_files = [f for f in os.listdir(directory_path) if f.endswith(".json")]

    print("=" * 80)
    print("CONVERTING DATE FORMATS TO MM/DD/YYYY")
    print("=" * 80)
    print(f"\nTotal files to process: {len(json_files)}\n")

    for filename in sorted(json_files):
        filepath = os.path.join(directory_path, filename)
        total_files += 1

        try:
            # Read the JSON file
            with open(filepath, "r", encoding="utf-8") as f:
                json_content = json.load(f)

            # Handle list vs dict
            if isinstance(json_content, list):
                if not json_content:
                    print(f"Skipping empty list file: {filename}")
                    continue
                data = json_content[0]
            else:
                data = json_content

            # Track if this file was modified
            file_modified = False
            dates_converted_in_file = 0

            # Helper to find key case-insensitively and return (actual_key, value)
            def get_key_value_case_insensitive(data, search_key):
                if not isinstance(data, dict):
                    return None, None
                for k, v in data.items():
                    if k.lower() == search_key.lower():
                        return k, v
                return None, None

            # Convert Trade Date
            trade_key, trade_val = get_key_value_case_insensitive(data, "Trade date")
            if trade_key and trade_val is not None:
                original = trade_val
                converted = convert_date_to_mm_dd_yyyy(original)
                if original != converted:
                    data[trade_key] = converted
                    file_modified = True
                    dates_converted_in_file += 1
                    print(f"{filename}: Trade Date: '{original}' -> '{converted}'")

            # Convert Settlement Date
            settlement_key, settlement_val = get_key_value_case_insensitive(
                data, "Settlement date"
            )
            if settlement_key and settlement_val is not None:
                original = settlement_val
                converted = convert_date_to_mm_dd_yyyy(original)
                if original != converted:
                    data[settlement_key] = converted
                    file_modified = True
                    dates_converted_in_file += 1
                    print(f"{filename}: Settlement Date: '{original}' -> '{converted}'")

            # Save the file if it was modified
            if file_modified:
                # Create backup
                if backup:
                    backup_filepath = os.path.join(backup_dir, filename)
                    shutil.copy2(filepath, backup_filepath)

                # Write the modified data back
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(json_content, f, indent=4, ensure_ascii=False)

                modified_files += 1
                total_dates_converted += dates_converted_in_file

        except Exception as e:
            print(f"ERROR processing {filename}: {e}")

    # Print summary
    print("\n" + "=" * 80)
    print("CONVERSION SUMMARY")
    print("=" * 80)
    print(f"Total files processed: {total_files}")
    print(f"Files modified: {modified_files}")
    print(f"Files unchanged: {total_files - modified_files}")
    print(f"Total dates converted: {total_dates_converted}")

    if backup and modified_files > 0:
        print(f"\nBackup created in: {backup_dir}")

    print("=" * 80)

    return {
        "total_files": total_files,
        "modified_files": modified_files,
        "total_dates_converted": total_dates_converted,
    }


if __name__ == "__main__":
    # Path to Trade_Confirmation labels directory
    trade_confirmation_dir = "datasets/labels/Contact_Note"

    if os.path.exists(trade_confirmation_dir):
        # Ask for confirmation
        print("\nThis script will convert all date formats to MM/DD/YYYY")
        print(f"Directory: {trade_confirmation_dir}")
        print("\nA backup will be created automatically.")

        response = input("\nDo you want to proceed? (yes/no): ").strip().lower()

        if response in ["yes", "y"]:
            convert_dates_in_json_files(trade_confirmation_dir, backup=True)
        else:
            print("\nOperation cancelled.")
    else:
        print(f"Directory not found: {trade_confirmation_dir}")
