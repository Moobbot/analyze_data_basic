#!/usr/bin/env python3
"""
Script để đánh giá độ chính xác cho TEST-SET-100 (single-page invoices)
"""

import pandas as pd
from pathlib import Path
from openpyxl import Workbook

# Import common utilities
from accuracy_common import (
    EVAL_FIELDS,
    normalize_invoice_name,
    calculate_field_accuracy,
    create_excel_report,
)

# Đường dẫn
BASE_DIR = Path(__file__).parent
TEST_DIR = BASE_DIR / "danh_gia_ket_qua" / "2026_02_04" / "test"
LABELS_DIR = BASE_DIR / "datasets" / "test-set-100" / "labels"
MODEL_OUTPUT_CSV = TEST_DIR / "test-set-100.csv"
OUTPUT_FILE = (
    BASE_DIR / "danh_gia_ket_qua" / "2026_02_04" / "accuracy_report_test-set-100.xlsx"
)


def load_ground_truth():
    """Convert JSON labels to DataFrame"""
    import json

    rows = []
    json_files = list(LABELS_DIR.glob("**/*.json"))

    for json_file in json_files:
        try:
            # Extract invoice type from parent folder name
            invoice_type = json_file.parent.name

            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle array format
            if isinstance(data, list):
                for idx, invoice_data in enumerate(data):
                    if not isinstance(invoice_data, dict):
                        continue
                    invoice_name = f"{json_file.stem}[{idx}]"
                    rows.extend(
                        process_invoice(invoice_name, invoice_data, invoice_type)
                    )
            # Handle object format
            elif isinstance(data, dict):
                invoice_name = json_file.stem
                rows.extend(process_invoice(invoice_name, invoice_data, invoice_type))

        except Exception as e:
            print(f"  Error processing {json_file.name}: {e}")

    df = pd.DataFrame(rows)
    df["invoice_name_normalized"] = df["invoice_name"].apply(normalize_invoice_name)
    return df


def process_invoice(invoice_name, data, invoice_type):
    """Process single invoice data"""
    rows = []

    # Get description items
    descriptions = data.get("Description", [])
    if not isinstance(descriptions, list):
        descriptions = []

    # Create row for each description item
    for desc_item in descriptions:
        if not isinstance(desc_item, dict):
            continue

        row = {
            "invoice_name": invoice_name + ".pdf",
            "invoice_type": invoice_type,
            "Type": data.get("Type"),
            "No": data.get("No"),
            "Date": data.get("Date"),
            "Customer": data.get("Customer"),
            "Supplier": data.get("Supplier"),
            "Currency": data.get("Currency"),
            "Ex rate": data.get("Ex rate"),
            "Ex rate to SGD": data.get("Ex rate to SGD"),
            "Tax type": desc_item.get("Tax type"),
            "Description": desc_item.get("text"),
            "Amount (before tax)": desc_item.get("Amount (before tax)"),
            "Tax amount": desc_item.get("Tax amount"),
            "Amount (after GST)": desc_item.get("Amount (after GST)"),
            "Amount in SGD": desc_item.get("Amount in SGD"),
            "Tax amount in SGD": desc_item.get("Tax amount in SGD"),
            "Amount after tax in SGD": desc_item.get("Amount after tax in SGD"),
        }
        rows.append(row)

    return rows


def load_model_output():
    """Load model output CSV"""
    if not MODEL_OUTPUT_CSV.exists():
        print(f"  ERROR: Model output not found: {MODEL_OUTPUT_CSV}")
        return pd.DataFrame()

    df = pd.read_csv(MODEL_OUTPUT_CSV, encoding="utf-8")
    df["invoice_name_normalized"] = df["invoice_name"].apply(normalize_invoice_name)
    return df


def main():
    """Main evaluation function"""
    print("=" * 80)
    print("TEST-SET-100 (SINGLE-PAGE) ACCURACY EVALUATION")
    print("=" * 80)

    # Load data
    print("\n[1/4] Loading data...")
    gt_df = load_ground_truth()
    model_df = load_model_output()

    if gt_df.empty or model_df.empty:
        print("  ERROR: Cannot load data")
        return

    print(f"  Ground truth rows: {len(gt_df)}")
    print(f"  Model output rows: {len(model_df)}")

    # Get matched invoices
    gt_invoices = set(gt_df["invoice_name_normalized"].unique())
    model_invoices = set(model_df["invoice_name_normalized"].unique())
    matched_invoices = gt_invoices & model_invoices
    missing_in_model = gt_invoices - model_invoices
    extra_in_model = model_invoices - gt_invoices

    print(f"\n  Unique GT invoices: {len(gt_invoices)}")
    print(f"  Unique Model invoices: {len(model_invoices)}")
    print(f"  Matched invoices: {len(matched_invoices)}")
    print(f"  Missing in Model: {len(missing_in_model)}")
    if missing_in_model:
        print(
            f"    → GT has but Model doesn't: {sorted(list(missing_in_model))[:5]}..."
            if len(missing_in_model) > 5
            else f"    → {sorted(list(missing_in_model))}"
        )
    print(f"  Extra in Model: {len(extra_in_model)}")
    if extra_in_model:
        print(
            f"    ⚠️  Model has but GT doesn't: {sorted(list(extra_in_model))[:5]}..."
            if len(extra_in_model) > 5
            else f"    ⚠️  {sorted(list(extra_in_model))}"
        )
        print(
            f"    ⚠️  WARNING: These invoices will be IGNORED in accuracy calculation!"
        )

    # Calculate accuracy for each field
    print("\n[2/4] Calculating accuracy metrics...")
    results = []

    for field in EVAL_FIELDS:
        print(f"  Evaluating: {field}")
        metrics = calculate_field_accuracy(gt_df, model_df, field)
        results.append(metrics)

    # Create Excel workbook
    print("\n[3/4] Creating comparison sheets...")
    wb = Workbook()

    overall_accuracy, overall_precision, overall_recall, overall_f1 = (
        create_excel_report(wb, gt_df, model_df, results, matched_invoices)
    )

    # Save
    print(f"\n[4/4] Saving to {OUTPUT_FILE}...")
    wb.save(OUTPUT_FILE)

    print("\n" + "=" * 80)
    print("✓ TEST-SET-100 Accuracy report completed!")
    print(f"  Output: {OUTPUT_FILE}")
    print("\n  OVERALL METRICS:")
    print(f"    Accuracy:  {overall_accuracy:.2f}%")
    print(f"    Precision: {overall_precision:.2f}%")
    print(f"    Recall:    {overall_recall:.2f}%")
    print(f"    F1-Score:  {overall_f1:.2f}%")
    print("=" * 80)


if __name__ == "__main__":
    main()
