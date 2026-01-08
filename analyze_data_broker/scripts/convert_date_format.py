import json
import os
import re
from datetime import datetime
import shutil


def convert_date_to_mm_dd_yyyy(date_str):
    """Convert date string to MM/DD/YYYY format"""
    if date_str is None or date_str == "":
        return date_str

    date_str = str(date_str).strip()

    # Check if already in MM/DD/YYYY format
    if re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", date_str):
        return date_str

    # Month map
    month_map = {
        "jan": "01",
        "feb": "02",
        "mar": "03",
        "apr": "04",
        "may": "05",
        "jun": "06",
        "jul": "07",
        "aug": "08",
        "sep": "09",
        "oct": "10",
        "nov": "11",
        "dec": "12",
    }

    # Convert from DD.MM.YYYY format (e.g. 10.03.2025)
    if re.match(r"^\d{1,2}\.\d{1,2}\.\d{4}$", date_str):
        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y")
            return date_obj.strftime("%m/%d/%Y")
        except ValueError as e:
            print(f"  Warning: Could not parse date '{date_str}': {e}")
            return date_str

    # Convert from DD-MMM-YYYY format (e.g. 25-Apr-2025)
    match_dmy = re.match(r"^(\d{1,2})-([A-Za-z]{3})-(\d{4})$", date_str)
    if match_dmy:
        day, month_str, year = match_dmy.groups()
        month = month_map.get(month_str.lower())
        if month:
            try:
                # Create a date object to validate
                date_obj = datetime(int(year), int(month), int(day))
                return date_obj.strftime("%m/%d/%Y")
            except ValueError:
                pass

    # Convert from DD-MMM-YY format (e.g. 26-May-25)
    match_dmy_short = re.match(r"^(\d{1,2})-([A-Za-z]{3})-(\d{2})$", date_str)
    if match_dmy_short:
        day, month_str, year_short = match_dmy_short.groups()
        month = month_map.get(month_str.lower())
        if month:
            year = int(year_short)
            # Assume 20xx for year <= 50, 19xx for year > 50
            full_year = 2000 + year if year <= 50 else 1900 + year
            try:
                date_obj = datetime(full_year, int(month), int(day))
                return date_obj.strftime("%m/%d/%Y")
            except ValueError:
                pass

    # Convert from YYYY-MM-DD format
    if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%m/%d/%Y")
        except ValueError as e:
            print(f"  Warning: Could not parse date '{date_str}': {e}")
            return date_str

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
                data = json.load(f)

            # Track if this file was modified
            file_modified = False
            dates_converted_in_file = 0

            # Helper to find key case-insensitively and return (actual_key, value)
            def get_key_value_case_insensitive(data, search_key):
                for k, v in data.items():
                    if k.lower() == search_key.lower():
                        return k, v
                return None, None

            # Convert Trade Date
            trade_key, trade_val = get_key_value_case_insensitive(data, "Trade Date")
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
                data, "Settlement Date"
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
                    json.dump(data, f, indent=4, ensure_ascii=False)

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
    trade_confirmation_dir = "datasets/labels/Trade_Confirmation"

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
