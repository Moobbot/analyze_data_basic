"""
Analyze Label Statistics

This script generates comprehensive statistics for label datasets located in `datasets/labels`.
It handles different schemas for each label type (subdirectory) and provides insights into:
- Field coverage (how often a field appears)
- Value distribution (top values for categorical fields)
- Numeric statistics (min, max, average)
- Missing/Null value counts

Usage:
    python scripts/analysis/analyze_label_statistics.py
"""

import os
import json
import argparse
import sys
from collections import defaultdict, Counter
import statistics

# Add parent directory to path (3 levels up from scripts/analysis)
# scripts/analysis -> scripts -> analyze_data_broker -> analyze_data_basic
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

try:
    import config
except ImportError:
    # Fallback if config is not found or not in path
    config = None


def is_number(s):
    """Check if value is a number (int or float)."""
    if isinstance(s, (int, float)) and not isinstance(s, bool):
        return True
    return False


def get_labels_dir():
    """Get the labels directory path."""
    if config and hasattr(config, "LABEL_DIR"):
        return config.LABEL_DIR

    # Fallback to relative path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Assumes scripts/analysis/ -> ... -> datasets/labels
    # Up 2 levels to analyze_data_broker, then into datasets/labels
    base_dir = os.path.dirname(os.path.dirname(current_dir))
    return os.path.join(base_dir, "datasets", "labels")


def analyze_folder(folder_path, label_type):
    """Analyze a single label folder (Schema Type)."""
    print(f"Analyzing {label_type}...")

    stats = {
        "file_count": 0,
        "record_count": 0,
        "fields": defaultdict(
            lambda: {
                "count": 0,
                "null_count": 0,
                "types": Counter(),
                "values": Counter(),
                "numeric_values": [],
            }
        ),
    }

    files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    stats["file_count"] = len(files)

    for filename in files:
        filepath = os.path.join(folder_path, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Normalize to list of records
            records = []
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                records = [data]

            stats["record_count"] += len(records)

            for record in records:
                if not isinstance(record, dict):
                    continue

                # Analyze each field in the record
                for key, value in record.items():
                    field_stats = stats["fields"][key]
                    field_stats["count"] += 1

                    if value is None or value == "":
                        field_stats["null_count"] += 1

                    # Type tracking
                    val_type = type(value).__name__
                    if value is None:
                        val_type = "None"
                    field_stats["types"][val_type] += 1

                    # Value tracking
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        # For strings, truncate if too long/unique to avoid huge memory usage?
                        # For now, keep all for accurate Counter, but maybe limit in report separate logic
                        if not isinstance(value, (dict, list)):
                            # Convert to string for Counter consistency
                            field_stats["values"][str(value)] += 1

                    # Numeric stats collection
                    if is_number(value):
                        field_stats["numeric_values"].append(value)
                    elif isinstance(value, str):
                        # Try to parse string number
                        try:
                            val_clean = value.replace(",", "").strip()
                            if val_clean:
                                float_val = float(val_clean)
                                field_stats["numeric_values"].append(float_val)
                        except ValueError:
                            pass

        except Exception as e:
            print(f"Error reading {filename}: {e}")

    return stats


def generate_report_for_schema(label_type, stats, output_dir):
    """Generate a readable text report for a specific schema."""
    output_path = os.path.join(output_dir, f"statistics_{label_type}.txt")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write(f"STATISTICS REPORT: {label_type}\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Total Files:   {stats['file_count']}\n")
        f.write(f"Total Records: {stats['record_count']}\n")

        if stats["record_count"] == 0:
            f.write("\n  (No records found)\n\n")
            return

        f.write("\nFIELD STATISTICS:\n")

        # Sort fields alphabetically
        sorted_fields = sorted(stats["fields"].items())

        for field, f_stats in sorted_fields:
            f.write(f"\n" + "-" * 40 + "\n")
            f.write(f"FIELD: [{field}]\n")
            f.write("-" * 40 + "\n")

            # Presence
            completeness = (f_stats["count"] / stats["record_count"]) * 100
            f.write(
                f"Presence: {f_stats['count']}/{stats['record_count']} ({completeness:.1f}%)\n"
            )

            # Nulls
            if f_stats["null_count"] > 0:
                null_pct = (
                    (f_stats["null_count"] / f_stats["count"]) * 100
                    if f_stats["count"] > 0
                    else 0
                )
                f.write(f"Null/Empty: {f_stats['null_count']} ({null_pct:.1f}%)\n")

            # Types
            types_str = ", ".join(
                [f"{t}({c})" for t, c in f_stats["types"].most_common()]
            )
            f.write(f"Types: {types_str}\n")

            # Numeric Stats
            numeric_vals = f_stats["numeric_values"]
            if len(numeric_vals) > 0:
                # Check if the field is predominantly numeric (>50% of non-null values are numeric)
                non_null_count = f_stats["count"] - f_stats["null_count"]
                if non_null_count > 0 and (len(numeric_vals) / non_null_count > 0.5):
                    try:
                        f.write(f"Numeric Stats:\n")
                        f.write(f"  Min: {min(numeric_vals)}\n")
                        f.write(f"  Max: {max(numeric_vals)}\n")
                        f.write(f"  Avg: {statistics.mean(numeric_vals):.4f}\n")
                    except Exception:
                        pass

            # Value Distribution
            f.write(f"Value Distribution:\n")
            unique_val_count = len(f_stats["values"])

            # Show top 50 values (increased from 5 based on user request "Theo giá trị của trường")
            limit = 50
            for val, count in f_stats["values"].most_common(limit):
                pct = (count / f_stats["count"]) * 100 if f_stats["count"] > 0 else 0
                f.write(f"  * {val}: {count} ({pct:.1f}%)\n")

            if unique_val_count > limit:
                f.write(f"  ... and {unique_val_count - limit} more unique values\n")

    print(f"Created report: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Analyze Label Statistics")
    parser.add_argument("--output-dir", help="Directory to save reports", default=None)
    args = parser.parse_args()

    labels_dir = get_labels_dir()
    if not os.path.exists(labels_dir):
        print(f"Error: Labels directory not found at {labels_dir}")
        return

    print(f"Scanning labels in: {labels_dir}")

    if args.output_dir:
        output_dir = args.output_dir
    else:
        # Default to the labels directory itself or parent?
        # User requested per file, maybe putting them in a reports folder is cleaner.
        # process: datasets/statistics_reports/
        base_dir = os.path.dirname(labels_dir)
        output_dir = os.path.join(base_dir, "statistics_reports")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # Iterate through subdirectories (Schema Types)
    for entry in os.listdir(labels_dir):
        full_path = os.path.join(labels_dir, entry)
        if os.path.isdir(full_path):
            stats = analyze_folder(full_path, entry)
            generate_report_for_schema(entry, stats, output_dir)

    print(f"\nAll reports saved to: {output_dir}")


if __name__ == "__main__":
    main()
