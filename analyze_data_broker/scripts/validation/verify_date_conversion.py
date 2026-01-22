import json
import os
import re


def check_date_formats():
    """Check the date formats in converted files"""

    trade_dir = "datasets/labels"

    # Get all JSON files recursively
    files = []
    for root, dirs, filenames in os.walk(trade_dir):
        for filename in filenames:
            if filename.endswith(".json"):
                files.append(os.path.join(root, filename))

    files.sort()

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

    # Keys to look for (lowercase)
    date_keys_to_check = {
        "trade date",
        "settlement date",
        "date",
        "value date",
        "ex-date",
        "payment date",
    }

    for current_file in files:
        try:
            with open(current_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Normalize to list of dicts for uniform processing
            items_to_check = []
            if isinstance(data, list):
                items_to_check = [item for item in data if isinstance(item, dict)]
            elif isinstance(data, dict):
                items_to_check = [data]

            if not items_to_check:
                no_date_count += 1
                continue

            file_has_mm_dd_yyyy = False
            file_has_other = False
            found_any_date_value = False

            mm_dd_yyyy_pattern = r"^\d{1,2}/\d{1,2}/\d{4}$"

            # Display name for the file (relative to trade_dir)
            rel_filename = os.path.relpath(current_file, trade_dir)

            for item in items_to_check:
                for key, value in item.items():
                    if key.lower() in date_keys_to_check and value:
                        found_any_date_value = True
                        if re.match(mm_dd_yyyy_pattern, str(value)):
                            file_has_mm_dd_yyyy = True
                            if sample_count < max_samples:
                                sample_conversions.append(
                                    f"{rel_filename}: {key} = {value}"
                                )
                                sample_count += 1
                        else:
                            file_has_other = True
                            other_formats.append(f"{rel_filename}: {key} = {value}")

            if file_has_other:
                # If ANY date is bad, count as bad (even if some are good)
                other_format_count += 1
            elif file_has_mm_dd_yyyy:
                mm_dd_yyyy_count += 1
            else:
                # No dates found (or all null)
                no_date_count += 1

        except Exception as e:
            error_count += 1
            print(f"ERROR reading {current_file}: {e}")

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
