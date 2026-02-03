#!/usr/bin/env python3
"""
Script để convert tất cả JSON ground truth labels thành CSV format
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any

# Đường dẫn
BASE_DIR = Path(__file__).parent
# LABELS_DIR = BASE_DIR / "datasets" / "test-set-100" / "labels"
# OUTPUT_CSV = BASE_DIR / "test-set-100-ground-truth.csv"
LABELS_DIR = BASE_DIR / "datasets" / "test-set-100-multipage" / "labels"
OUTPUT_CSV = BASE_DIR / "test-set-100-multipage-ground-truth.csv"

# CSV columns matching the model output format
CSV_COLUMNS = [
    "invoice_name",
    "Type",
    "No",
    "Date",
    "Customer",
    "Supplier",
    "Currency",
    "Ex rate",
    "Ex rate to SGD",
    "Project code",
    "Tax type",
    "Description",
    "Amount (before tax)",
    "Tax amount",
    "Amount (after GST)",
    "Amount in SGD",
    "Tax amount in SGD",
    "Amount after tax in SGD",
    "created_at",
    "updated_at",
]


def convert_json_to_csv_rows(json_file: Path, json_data: Any) -> List[Dict]:
    """Convert một JSON file thành nhiều CSV rows (mỗi line item là 1 row)"""
    rows = []

    # Handle array format (multipage PDFs with multiple invoices)
    if isinstance(json_data, list):
        for idx, invoice_data in enumerate(json_data):
            if not isinstance(invoice_data, dict):
                continue
            # For array format, append index to invoice name
            invoice_name = f"{json_file.stem}[{idx}].pdf"
            rows.extend(process_single_invoice(invoice_name, invoice_data))
        return rows

    # Handle object format (single invoice)
    if isinstance(json_data, dict):
        invoice_name = json_file.stem + ".pdf"
        return process_single_invoice(invoice_name, json_data)

    # Invalid format
    print(f"  ⚠ Skipping {json_file.name}: invalid format (not dict or list)")
    return rows


def process_single_invoice(invoice_name: str, invoice_data: Dict) -> List[Dict]:
    """Process a single invoice dict and return CSV rows"""
    rows = []

    # Get Description items
    descriptions = invoice_data.get("Description", [])
    if not isinstance(descriptions, list):
        descriptions = [descriptions] if descriptions else []

    # If no description items, create one row with header info only
    if not descriptions:
        descriptions = [{}]

    # Create a row for each line item
    for desc_item in descriptions:
        row = {
            "invoice_name": invoice_name,
            "Type": invoice_data.get("Type", ""),
            "No": invoice_data.get("No", ""),
            "Date": invoice_data.get("Date", ""),
            "Customer": invoice_data.get("Customer", ""),
            "Supplier": invoice_data.get("Supplier", ""),
            "Currency": invoice_data.get("Currency", ""),
            "Ex rate": invoice_data.get("Ex rate", ""),
            "Ex rate to SGD": invoice_data.get("Ex rate to SGD", ""),
            "Project code": (
                desc_item.get("Project code", "") if isinstance(desc_item, dict) else ""
            ),
            "Tax type": (
                desc_item.get("Tax type", "") if isinstance(desc_item, dict) else ""
            ),
            "Description": (
                desc_item.get("text", "") if isinstance(desc_item, dict) else ""
            ),
            "Amount (before tax)": (
                desc_item.get("Amount (before tax)", "")
                if isinstance(desc_item, dict)
                else ""
            ),
            "Tax amount": (
                desc_item.get("Tax amount", "") if isinstance(desc_item, dict) else ""
            ),
            "Amount (after GST)": (
                desc_item.get("Amount (after GST)", "")
                if isinstance(desc_item, dict)
                else ""
            ),
            "Amount in SGD": (
                desc_item.get("Amount in SGD", "")
                if isinstance(desc_item, dict)
                else ""
            ),
            "Tax amount in SGD": (
                desc_item.get("Tax amount in SGD", "")
                if isinstance(desc_item, dict)
                else ""
            ),
            "Amount after tax in SGD": (
                desc_item.get("Amount after tax in SGD", "")
                if isinstance(desc_item, dict)
                else ""
            ),
            "created_at": "",
            "updated_at": "",
        }
        rows.append(row)

    return rows


def main():
    print("=" * 80)
    print("JSON TO CSV CONVERTER")
    print("=" * 80)

    all_rows = []
    processed = 0
    skipped = 0

    print(f"\nProcessing JSON files from: {LABELS_DIR}")

    # Iterate through all supplier directories
    for supplier_dir in sorted(LABELS_DIR.iterdir()):
        if not supplier_dir.is_dir():
            continue

        print(f"\n📁 Processing {supplier_dir.name}...")

        for json_file in sorted(supplier_dir.glob("*.json")):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                rows = convert_json_to_csv_rows(json_file, data)
                if rows:
                    all_rows.extend(rows)
                    processed += 1
                else:
                    skipped += 1

            except Exception as e:
                print(f"  ❌ Error processing {json_file.name}: {e}")
                skipped += 1

    # Write to CSV
    print(f"\n{'=' * 80}")
    print(f"Writing {len(all_rows)} rows to CSV...")

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\n✓ Conversion completed!")
    print(f"  - Processed: {processed} files")
    print(f"  - Skipped: {skipped} files")
    print(f"  - Total rows: {len(all_rows)}")
    print(f"  - Output: {OUTPUT_CSV}")
    print("=" * 80)


if __name__ == "__main__":
    main()
