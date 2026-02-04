#!/usr/bin/env python3
"""
Script to analyze error patterns in invoice extraction
Generates markdown report
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

# Paths
BASE_DIR = Path(__file__).parent
OUTPUT_FILE = BASE_DIR / "danh_gia_ket_qua" / "2026_02_04" / "report_analysis_error.md"


def analyze_dataset(name, gt_df, model_df):
    """Analyze dataset and return report lines"""
    report = []
    report.append(f"## {name}")
    report.append("")

    # Match invoices
    gt_invoices = set(gt_df["invoice_name_normalized"].unique())
    model_invoices = set(model_df["invoice_name_normalized"].unique())
    matched_invoices = sorted(list(gt_invoices & model_invoices))

    report.append(f"- **Total Matched Invoices:** {len(matched_invoices)}")
    report.append("")

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

    # Generate Tables
    report.append("| Field | Error % | Empty(Model) | Mismatch | Empty(GT) |")
    report.append("| :--- | :--- | :--- | :--- | :--- |")

    sorted_fields = sorted(
        field_errors.items(), key=lambda x: x[1]["cnt"], reverse=True
    )

    for field, stats in sorted_fields:
        if stats["total"] == 0:
            continue
        err_rate = (stats["cnt"] / stats["total"]) * 100
        report.append(
            f"| {field} | {err_rate:.1f}% | {stats['model_empty']} | {stats['value_mismatch']} | {stats['gt_empty']} |"
        )

    report.append("")
    report.append("### Top Error Examples")
    report.append("")

    for field, stats in sorted_fields[:5]:  # Top 5 problematic fields
        if stats["cnt"] == 0:
            continue
        report.append(f"#### {field} (Errors: {stats['cnt']})")

        for ex in error_examples[field]:
            # Format nicely
            gt_disp = ex["gt"].replace("\n", " ").strip()
            model_disp = ex["model"].replace("\n", " ").strip()
            if len(gt_disp) > 50:
                gt_disp = gt_disp[:47] + "..."
            if len(model_disp) > 50:
                model_disp = model_disp[:47] + "..."

            report.append(f"- **{ex['invoice']}**")
            report.append(f"  - GT: `{gt_disp}`")
            report.append(f"  - Model: `{model_disp}`")
        report.append("")

    return report


def main():
    print("Loading data...")
    gt_100 = load_gt_100()
    model_100 = load_model_100()
    gt_multi = load_gt_multi()
    model_multi = load_model_multi()

    print("Analyzing and generating report...")

    report_lines = []
    report_lines.append("# Invoice Error Analysis Report")
    report_lines.append("")
    report_lines.append("**Cập nhật:** 2026-02-04")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Analyze Single Page
    report_lines.extend(
        analyze_dataset("TEST-SET-100 (Single Page)", gt_100, model_100)
    )

    report_lines.append("---")
    report_lines.append("")

    # Analyze Multipage
    report_lines.extend(
        analyze_dataset("TEST-SET-100-MULTIPAGE", gt_multi, model_multi)
    )

    # Write to file
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"✓ Report saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
