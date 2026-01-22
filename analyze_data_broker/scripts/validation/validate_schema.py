# validate_schema.py
"""
Standalone utility for schema validation testing.
Validates JSON files against their detected schemas and generates reports.
"""

import os
import sys
import csv
import argparse
from pathlib import Path

# Add parent directory to path (2 levels up from scripts/validation/)
parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)

from lib import schema_validator


def process_folder(input_folder: str, output_csv: str):
    """
    Process all JSON files in a folder and validate against schemas.

    Args:
        input_folder: Path to folder containing JSON files
        output_csv: Path to output CSV file
    """
    print(f"Processing folder: {input_folder}")

    # Find all JSON files
    files = []
    for root, dirs, filenames in os.walk(input_folder):
        for f in filenames:
            if f.lower().endswith(".json"):
                files.append(os.path.join(root, f))

    print(f"Found {len(files)} JSON files")

    # Validate each file
    results = []
    for i, json_file in enumerate(files):
        result = schema_validator.validate_file(json_file)
        results.append(result)

        if (i + 1) % 10 == 0:
            print(f"Processed {i+1}/{len(files)}")

    # Write results to CSV
    if results:
        fieldnames = ["file", "schema_detected", "is_valid", "errors"]

        try:
            # Ensure output directory exists
            out_dir = os.path.dirname(output_csv)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)

            with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for result in results:
                    # Format errors as string
                    row = {
                        "file": result["file"],
                        "schema_detected": result["schema_detected"] or "",
                        "is_valid": result["is_valid"],
                        "errors": (
                            "; ".join(result["errors"]) if result["errors"] else ""
                        ),
                    }
                    writer.writerow(row)

            print(f"\nSuccessfully wrote results to {output_csv}")
        except Exception as e:
            print(f"Error writing CSV: {e}")

    # Generate summary
    generate_summary(results, output_csv)


def generate_summary(results, csv_path):
    """Generate and print summary statistics."""
    total = len(results)
    valid = sum(1 for r in results if r["is_valid"])
    invalid = total - valid

    # Count by schema type
    schema_counts = {}
    for r in results:
        schema = r["schema_detected"] or "Unknown"
        schema_counts[schema] = schema_counts.get(schema, 0) + 1

    # Print summary
    print("\n" + "=" * 60)
    print("SCHEMA VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total Files:     {total}")
    print(f"Valid:           {valid}")
    print(f"Invalid:         {invalid}")
    print(f"Success Rate:    {(valid/total*100):.1f}%" if total > 0 else "N/A")
    print("\nSchema Detection:")
    for schema, count in sorted(schema_counts.items()):
        print(f"  {schema:30s}: {count}")

    # Write summary to text file
    summary_path = csv_path.replace(".csv", "_summary.txt")
    try:
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("SCHEMA VALIDATION SUMMARY\n")
            f.write("=" * 60 + "\n")
            f.write(f"Total Files:     {total}\n")
            f.write(f"Valid:           {valid}\n")
            f.write(f"Invalid:         {invalid}\n")
            f.write(
                f"Success Rate:    {(valid/total*100):.1f}%\n" if total > 0 else "N/A\n"
            )
            f.write("\nSchema Detection:\n")
            for schema, count in sorted(schema_counts.items()):
                f.write(f"  {schema:30s}: {count}\n")

            # List invalid files
            invalid_files = [r for r in results if not r["is_valid"]]
            if invalid_files:
                f.write("\n" + "=" * 60 + "\n")
                f.write("INVALID FILES\n")
                f.write("=" * 60 + "\n")
                for r in invalid_files:
                    f.write(f"\nFile: {r['file']}\n")
                    f.write(f"Schema: {r['schema_detected'] or 'Unknown'}\n")
                    f.write(f"Errors:\n")
                    for error in r["errors"]:
                        f.write(f"  - {error}\n")

        print(f"\nSummary written to {summary_path}")
    except Exception as e:
        print(f"Error writing summary: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate JSON files against broker transaction schemas"
    )
    parser.add_argument(
        "--input", required=True, help="Input folder containing JSON files"
    )
    parser.add_argument("--output", required=True, help="Output CSV file path")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input folder does not exist: {args.input}")
        sys.exit(1)

    process_folder(args.input, args.output)


if __name__ == "__main__":
    main()
