import json
import os
import re


def check_date_formats():
    """Check the date formats in converted files"""

    trade_dir = "datasets/labels/Trade_Confirmation"

    # Get all JSON files
    files = sorted([f for f in os.listdir(trade_dir) if f.endswith(".json")])

    print("=" * 80)
    print("DATE FORMAT VERIFICATION")
    print("=" * 80)
    print(f"\nTotal files: {len(files)}\n")

    # Statistics
    mm_dd_yyyy_count = 0
    other_format_count = 0
    no_date_count = 0
    error_count = 0

    # Details for non-MM/DD/YYYY formats
    other_formats = []

    # Sample of converted dates
    sample_conversions = []
    sample_count = 0
    max_samples = 10

    for filename in files:
        current_file = os.path.join(trade_dir, filename)

        try:
            with open(current_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle list (array) format
            if isinstance(data, list):
                if len(data) > 0 and isinstance(data[0], dict):
                    data = data[0]
                else:
                    no_date_count += 1
                    continue

            # Get dates (case-insensitive search)
            trade_date = None
            settlement_date = None

            for key, value in data.items():
                if key.lower() == "trade date":
                    trade_date = value
                elif key.lower() == "settlement date":
                    settlement_date = value

            # Check formats
            mm_dd_yyyy_pattern = r"^\d{1,2}/\d{1,2}/\d{4}$"

            dates_to_check = [
                ("Trade Date", trade_date),
                ("Settlement Date", settlement_date),
            ]

            file_has_mm_dd_yyyy = False
            file_has_other = False

            for date_name, date_value in dates_to_check:
                if date_value:
                    if re.match(mm_dd_yyyy_pattern, str(date_value)):
                        file_has_mm_dd_yyyy = True
                        if sample_count < max_samples:
                            sample_conversions.append(
                                f"{filename}: {date_name} = {date_value}"
                            )
                            sample_count += 1
                    else:
                        file_has_other = True
                        other_formats.append(f"{filename}: {date_name} = {date_value}")

            if file_has_mm_dd_yyyy:
                mm_dd_yyyy_count += 1
            elif file_has_other:
                other_format_count += 1
            else:
                no_date_count += 1

        except Exception as e:
            error_count += 1
            print(f"ERROR reading {filename}: {e}")

    # Print statistics
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files with MM/DD/YYYY format: {mm_dd_yyyy_count}")
    print(f"Files with other date formats: {other_format_count}")
    print(f"Files with no dates: {no_date_count}")
    print(f"Files with errors: {error_count}")

    if sample_conversions:
        print("\n" + "=" * 80)
        print("SAMPLE CONVERSIONS (MM/DD/YYYY)")
        print("=" * 80)
        for sample in sample_conversions:
            print(f"  {sample}")

    if other_formats:
        print("\n" + "=" * 80)
        print("FILES WITH NON-MM/DD/YYYY FORMATS")
        print("=" * 80)
        for other in other_formats[:20]:  # Show first 20
            print(f"  {other}")
        if len(other_formats) > 20:
            print(f"  ... and {len(other_formats) - 20} more")

    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    check_date_formats()
