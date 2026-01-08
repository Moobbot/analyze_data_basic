import json
import os
from datetime import datetime


def convert_date_to_mm_dd_yyyy(date_str):
    """Convert YYYY-MM-DD to MM/DD/YYYY"""
    if not date_str or date_str == "":
        return date_str

    try:
        date_obj = datetime.strptime(str(date_str), "%Y-%m-%d")
        return date_obj.strftime("%m/%d/%Y")
    except:
        return date_str


def fix_remaining_files():
    """Fix the 2 remaining files with YYYY-MM-DD format"""

    files_to_fix = ["0379.json", "0392.json"]
    trade_dir = "datasets/labels/Trade_Confirmation"

    print("=" * 80)
    print("FIXING REMAINING FILES")
    print("=" * 80)
    print()

    for filename in files_to_fix:
        filepath = os.path.join(trade_dir, filename)

        if not os.path.exists(filepath):
            print(f"File not found: {filename}")
            continue

        try:
            # Read the file
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle both list and dict formats
            is_list = isinstance(data, list)
            records = data if is_list else [data]

            # Process each record
            for record in records:
                if isinstance(record, dict):
                    for key, value in list(record.items()):
                        if key.lower() == "trade date" and value:
                            old_value = value
                            new_value = convert_date_to_mm_dd_yyyy(value)
                            if old_value != new_value:
                                record[key] = new_value
                                print(
                                    f"{filename}: {key}: '{old_value}' -> '{new_value}'"
                                )

                        if key.lower() == "settlement date" and value:
                            old_value = value
                            new_value = convert_date_to_mm_dd_yyyy(value)
                            if old_value != new_value:
                                record[key] = new_value
                                print(
                                    f"{filename}: {key}: '{old_value}' -> '{new_value}'"
                                )

            # Write back
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4 if not is_list else 2, ensure_ascii=False)

            print(f"Fixed {filename}")
            print()

        except Exception as e:
            print(f"ERROR fixing {filename}: {e}")
            print()

    print("=" * 80)
    print("COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    fix_remaining_files()
