#!/usr/bin/env python3
"""
Script to analyze error patterns in invoice extraction
"""

import pandas as pd
from pathlib import Path
from accuracy_common import (
    EVAL_FIELDS,
    normalize_invoice_name,
    are_values_equivalent,
    calculate_missing_fields,
)
from calculate_accuracy_test100 import load_ground_truth as load_gt_100
from calculate_accuracy_test100 import load_model_output as load_model_100
from calculate_accuracy_test100_multipage import load_ground_truth as load_gt_multi
from calculate_accuracy_test100_multipage import load_model_output as load_model_multi


def analyze_dataset(name, gt_df, model_df):
    print(f"\n{'='*20} ANALYZING: {name} {'='*20}")

    # Match invoices
    gt_invoices = set(gt_df["invoice_name_normalized"].unique())
    model_invoices = set(model_df["invoice_name_normalized"].unique())
    matched_invoices = sorted(list(gt_invoices & model_invoices))

    print(f"Total Matched Invoices: {len(matched_invoices)}")

    # Store errors
    field_errors = {
        field: {
            "total": 0,
            "cnt": 0,
            "model_empty": 0,
            "gt_empty": 0,
            "value_mismatch": 0,
        }
        for field in EVAL_FIELDS
    }
    error_examples = {field: [] for field in EVAL_FIELDS}

    for invoice_name in matched_invoices:
        gt_rows = gt_df[gt_df["invoice_name_normalized"] == invoice_name]
        model_rows = model_df[model_df["invoice_name_normalized"] == invoice_name]

        # We need to match rows. For now, simple assumption: 1-to-1 or max-to-max matching order
        # This is a simplification but useful for error analysis
        max_rows = max(len(gt_rows), len(model_rows))

        for i in range(max_rows):
            gt_row = gt_rows.iloc[i].to_dict() if i < len(gt_rows) else {}
            model_row = model_rows.iloc[i].to_dict() if i < len(model_rows) else {}

            # Apply calculator for missing GT fields
            calc_gt = calculate_missing_fields(gt_row) if gt_row else {}

            for field in EVAL_FIELDS:
                field_errors[field]["total"] += 1

                gt_val = gt_row.get(field) if gt_row else ""
                if field in calc_gt and (pd.isna(gt_val) or str(gt_val).strip() == ""):
                    gt_val = calc_gt[field]

                model_val = model_row.get(field) if model_row else ""

                is_match, match_type = are_values_equivalent(gt_val, model_val, field)

                if not is_match:
                    field_errors[field]["cnt"] += 1

                    gt_str = str(gt_val).strip() if pd.notna(gt_val) else ""
                    model_str = str(model_val).strip() if pd.notna(model_val) else ""

                    if model_str == "" and gt_str != "":
                        field_errors[field]["model_empty"] += 1
                    elif gt_str == "" and model_str != "":
                        field_errors[field]["gt_empty"] += 1
                    else:
                        field_errors[field]["value_mismatch"] += 1

                    # Save examples (max 5 per field)
                    if len(error_examples[field]) < 5:
                        error_examples[field].append(
                            {"invoice": invoice_name, "gt": gt_str, "model": model_str}
                        )

    # Print Report
    print(
        f"\n{'Field':<25} | {'Error %':<8} | {'Empty(Model)':<12} | {'Mismatch':<10} | {'Empty(GT)':<10}"
    )
    print("-" * 80)

    sorted_fields = sorted(
        field_errors.items(), key=lambda x: x[1]["cnt"], reverse=True
    )

    for field, stats in sorted_fields:
        if stats["total"] == 0:
            continue
        err_rate = (stats["cnt"] / stats["total"]) * 100
        print(
            f"{field:<25} | {err_rate:6.1f}% | {stats['model_empty']:<12} | {stats['value_mismatch']:<10} | {stats['gt_empty']:<10}"
        )

    print("\n--- TOP ERROR EXAMPLES ---")
    for field, stats in sorted_fields[:5]:  # Top 5 problematic fields
        if stats["cnt"] == 0:
            continue
        print(f"\n[ {field} ] Errors: {stats['cnt']}")
        for ex in error_examples[field]:
            print(f"  {ex['invoice']}: GT='{ex['gt']}' vs Model='{ex['model']}'")


def main():
    print("Loading data...")
    gt_100 = load_gt_100()
    model_100 = load_model_100()

    analyze_dataset("TEST-SET-100 (Single Page)", gt_100, model_100)

    # Uncomment to analyze multipage as well
    gt_multi = load_gt_multi()
    model_multi = load_model_multi()
    analyze_dataset("TEST-SET-100-MULTIPAGE", gt_multi, model_multi)


if __name__ == "__main__":
    main()
