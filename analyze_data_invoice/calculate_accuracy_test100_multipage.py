#!/usr/bin/env python3
"""
Script để đánh giá độ chính xác cho TEST-SET-100-MULTIPAGE
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
TEST_DIR = BASE_DIR / "test-2026-02-03"
GROUND_TRUTH_CSV = BASE_DIR / "test-set-100-multipage-ground-truth.csv"
MODEL_OUTPUT_CSV = TEST_DIR / "test-set-100-multipage-all.csv"
OUTPUT_FILE = BASE_DIR / "accuracy_report_test-set-100-multipage.xlsx"


def load_ground_truth():
    """Load ground truth CSV"""
    if not GROUND_TRUTH_CSV.exists():
        print(f"  ERROR: Ground truth not found: {GROUND_TRUTH_CSV}")
        return pd.DataFrame()

    df = pd.read_csv(GROUND_TRUTH_CSV, encoding="utf-8")
    df["invoice_name_normalized"] = df["invoice_name"].apply(normalize_invoice_name)
    return df


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
    print("TEST-SET-100-MULTIPAGE ACCURACY EVALUATION")
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

    print(f"\n  Unique GT invoices: {len(gt_invoices)}")
    print(f"  Unique Model invoices: {len(model_invoices)}")
    print(f"  Matched invoices: {len(matched_invoices)}")
    print(f"  Missing in Model: {len(gt_invoices - model_invoices)}")

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
    print("✓ TEST-SET-100-MULTIPAGE Accuracy report completed!")
    print(f"  Output: {OUTPUT_FILE}")
    print("\n  OVERALL METRICS:")
    print(f"    Accuracy:  {overall_accuracy:.2f}%")
    print(f"    Precision: {overall_precision:.2f}%")
    print(f"    Recall:    {overall_recall:.2f}%")
    print(f"    F1-Score:  {overall_f1:.2f}%")
    print("=" * 80)


if __name__ == "__main__":
    main()
