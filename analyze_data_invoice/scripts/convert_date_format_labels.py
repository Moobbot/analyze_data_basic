import json
import os
import sys
from pathlib import Path

# Add project root (analyze_data_basic) to sys.path to allow importing common_lib
# Current script: .../analyze_data_basic/analyze_data_invoice/scripts/convert_date_format_labels.py
# Root: .../analyze_data_basic
try:
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
except NameError:
    # Fallback if __file__ is not defined (e.g. interactive mode)
    pass

try:
    from common_lib.date_utils import validate_date
except ImportError:
    # Fallback for when running in an environment where common_lib setup is tricky
    # But user specifically asked to use it, so we should try hard.
    print(
        "Warning: Could not import common_lib.date_utils. Ensure PYTHONPATH is set correctly."
    )
    validate_date = None


def convert_date_format(date_str):
    """
    Converts date to MM/DD/YYYY using common_lib.validate_date.
    Skips conversion if date is numeric and both day and month are < 13 (ambiguous).
    """
    if not isinstance(date_str, str):
        return None

    date_str = date_str.strip()

    # Check for ambiguity (Day and Month < 13) BEFORE validating/converting
    # We check if the string contains only numbers and separators / or -
    # and if both parts are < 13.
    import re

    # split by / or - or .
    parts = re.split(r"[/\-\.]", date_str)
    if len(parts) == 3:
        p1, p2, p3 = parts
        # If parts are numeric
        if p1.isdigit() and p2.isdigit():
            v1, v2 = int(p1), int(p2)
            # If both are valid months (1-12), it's ambiguous which is day/month.
            # User rule: if both < 13, do not convert.
            if 0 < v1 < 13 and 0 < v2 < 13:
                return date_str  # Ambiguous, do not convert

    if validate_date:
        is_valid, dt, fmt_name = validate_date(date_str)
        if is_valid and dt:
            # Re-format to MM/DD/YYYY
            return dt.strftime("%m/%d/%Y")

    # Fallback to simple parsing if import failed
    return date_str


def process_directory(directory_path):
    count = 0
    errors = 0

    directory = Path(directory_path)
    if not directory.exists():
        print(f"Directory not found: {directory}")
        return

    print(f"Scanning directory: {directory}")

    for file_path in directory.rglob("*.json"):
        try:
            changed = False
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON: {file_path}")
                    errors += 1
                    continue

            if isinstance(data, dict):
                if "Date" in data and data["Date"]:
                    original_date = data["Date"]
                    new_date = convert_date_format(original_date)

                    if new_date and new_date != original_date:
                        data["Date"] = new_date
                        changed = True
                        print(
                            f"Updated {file_path.name}: {original_date} -> {new_date}"
                        )

            if changed:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                count += 1

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            errors += 1

    print(f"\nProcessing complete.")
    print(f"Files updated: {count}")
    print(f"Errors encountered: {errors}")


if __name__ == "__main__":
    target_dir = Path(__file__).parent.parent / "datasets" / "data-all" / "labels"

    if not target_dir.exists():
        target_dir = Path(
            r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\analyze_data_invoice\datasets\data-all\labels"
        )

    process_directory(target_dir)
