import json
import os
from collections import Counter
import re


def identify_date_format(date_str):
    """Identify the format of a date string"""
    if date_str is None:
        return "null"

    date_str = str(date_str).strip()

    if not date_str:
        return "empty"

    # Common date patterns
    patterns = {
        r"^\d{1,2}/\d{1,2}/\d{4}$": "MM/DD/YYYY or DD/MM/YYYY",
        r"^\d{4}-\d{2}-\d{2}$": "YYYY-MM-DD",
        r"^\d{2}-\d{2}-\d{4}$": "DD-MM-YYYY or MM-DD-YYYY",
        r"^\d{1,2}\.\d{1,2}\.\d{4}$": "DD.MM.YYYY or MM.DD.YYYY",
        r"^\d{4}/\d{2}/\d{2}$": "YYYY/MM/DD",
        r"^\d{1,2}-\w{3}-\d{4}$": "DD-MMM-YYYY",
        r"^\w{3}\s+\d{1,2},\s+\d{4}$": "MMM DD, YYYY",
        # Additional Formats
        r"^\d{1,2}-\w{3}-\d{2}$": "DD-MMM-YY",
        r"^\d{4}\.\d{2}\.\d{2}$": "YYYY.MM.DD",
        r"^\d{1,2}/\d{1,2}/\d{2}$": "MM/DD/YY or DD/MM/YY",
        r"^\d{2}-\d{2}-\d{2}$": "DD-MM-YY",
        r"^\d{8}$": "YYYYMMDD",
        r"^\d{1,2}\s+[A-Za-z]+\s+\d{4}$": "DD MMM YYYY",
    }

    for pattern, format_name in patterns.items():
        if re.match(pattern, date_str):
            return format_name

    return f"unknown: {date_str}"


def analyze_date_formats(directory_path):
    """Analyze date formats in all JSON files in the directory"""

    trade_date_formats = Counter()
    settlement_date_formats = Counter()

    # Statistics
    total_files = 0
    files_with_trade_date = 0
    files_with_settlement_date = 0

    # Examples for each format
    trade_date_examples = {}
    settlement_date_examples = {}

    # Get all JSON files
    json_files = [f for f in os.listdir(directory_path) if f.endswith(".json")]

    for filename in sorted(json_files):
        filepath = os.path.join(directory_path, filename)
        total_files += 1

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Helper to find key case-insensitively
            def get_value_case_insensitive(data, key):
                for k, v in data.items():
                    if k.lower() == key.lower():
                        return v
                return None

            # Analyze Trade Date
            trade_date = get_value_case_insensitive(data, "Trade date")
            if trade_date:
                files_with_trade_date += 1
                format_type = identify_date_format(trade_date)
                trade_date_formats[format_type] += 1

                # Store example
                if format_type not in trade_date_examples:
                    trade_date_examples[format_type] = (filename, trade_date)

            # Analyze Settlement Date
            settlement_date = get_value_case_insensitive(data, "Settlement date")
            if settlement_date:
                files_with_settlement_date += 1
                format_type = identify_date_format(settlement_date)
                settlement_date_formats[format_type] += 1

                # Store example
                if format_type not in settlement_date_examples:
                    settlement_date_examples[format_type] = (filename, settlement_date)

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # Print results
    print("=" * 80)
    print("DATE FORMAT ANALYSIS - Trade Confirmation JSON Files")
    print("=" * 80)
    print(f"\nTotal files analyzed: {total_files}")
    print(f"Files with Trade Date: {files_with_trade_date}")
    print(f"Files with Settlement Date: {files_with_settlement_date}")

    print("\n" + "=" * 80)
    print("TRADE DATE FORMATS")
    print("=" * 80)
    for format_type, count in trade_date_formats.most_common():
        percentage = (count / total_files) * 100
        print(f"\n{format_type}:")
        print(f"  Count: {count} ({percentage:.2f}%)")
        if format_type in trade_date_examples:
            filename, example = trade_date_examples[format_type]
            print(f"  Example: '{example}' from {filename}")

    print("\n" + "=" * 80)
    print("SETTLEMENT DATE FORMATS")
    print("=" * 80)
    for format_type, count in settlement_date_formats.most_common():
        percentage = (count / total_files) * 100
        print(f"\n{format_type}:")
        print(f"  Count: {count} ({percentage:.2f}%)")
        if format_type in settlement_date_examples:
            filename, example = settlement_date_examples[format_type]
            print(f"  Example: '{example}' from {filename}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nTrade Date - Unique formats found: {len(trade_date_formats)}")
    print(f"Settlement Date - Unique formats found: {len(settlement_date_formats)}")

    # Export to CSV
    output_file = "date_format_analysis.csv"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("Date Field,Format Type,Count,Percentage,Example Value,Example File\n")

        for format_type, count in trade_date_formats.most_common():
            percentage = (count / total_files) * 100
            filename, example = trade_date_examples.get(format_type, ("", ""))
            f.write(
                f"Trade Date,{format_type},{count},{percentage:.2f}%,{example},{filename}\n"
            )

        for format_type, count in settlement_date_formats.most_common():
            percentage = (count / total_files) * 100
            filename, example = settlement_date_examples.get(format_type, ("", ""))
            f.write(
                f"Settlement Date,{format_type},{count},{percentage:.2f}%,{example},{filename}\n"
            )

    print(f"\nResults exported to: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    # Path to Trade_Confirmation labels directory
    trade_confirmation_dir = "datasets/labels/Contact_Note"

    if os.path.exists(trade_confirmation_dir):
        analyze_date_formats(trade_confirmation_dir)
    else:
        print(f"Directory not found: {trade_confirmation_dir}")
