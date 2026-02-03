#!/usr/bin/env python3
"""
Common utilities for invoice accuracy evaluation
"""

import pandas as pd
import re
from openpyxl.styles import Font, PatternFill


# Fields to evaluate
EVAL_FIELDS = [
    "Type",
    "No",
    "Date",
    "Customer",
    "Supplier",
    "Currency",
    "Ex rate",
    "Ex rate to SGD",
    "Tax type",
    "Description",
    "Amount (before tax)",
    "Tax amount",
    "Amount (after GST)",
    "Amount in SGD",
    "Tax amount in SGD",
    "Amount after tax in SGD",
]


def normalize_invoice_name(name):
    """Normalize invoice name for matching"""
    if pd.isna(name):
        return ""
    name = str(name).strip()

    # Remove .pdf extension if present
    if name.lower().endswith(".pdf"):
        name = name[:-4]

    # Remove [0], [1], [2] etc. suffixes
    name = re.sub(r"\[\d+\]$", "", name)

    return name.strip()


def normalize_value(value):
    """Normalize value for comparison"""
    if pd.isna(value):
        return ""

    value = str(value).strip()
    value = value.replace(",", "")
    value = value.lower()

    return value


def calculate_field_accuracy(gt_df, model_df, field):
    """Calculate accuracy metrics for a specific field"""

    # Get matched invoices only
    gt_invoices = set(gt_df["invoice_name_normalized"].unique())
    model_invoices = set(model_df["invoice_name_normalized"].unique())
    matched_invoices = gt_invoices & model_invoices

    # Filter to matched invoices
    gt_matched = gt_df[gt_df["invoice_name_normalized"].isin(matched_invoices)]
    model_matched = model_df[model_df["invoice_name_normalized"].isin(matched_invoices)]

    # Count matches
    total_gt = 0
    total_model = 0
    correct = 0

    for invoice_name in matched_invoices:
        gt_rows = gt_matched[gt_matched["invoice_name_normalized"] == invoice_name]
        model_rows = model_matched[
            model_matched["invoice_name_normalized"] == invoice_name
        ]

        gt_values = gt_rows[field].apply(normalize_value).tolist()
        model_values = model_rows[field].apply(normalize_value).tolist()

        total_gt += len(gt_values)
        total_model += len(model_values)

        for i in range(min(len(gt_values), len(model_values))):
            if gt_values[i] == model_values[i]:
                correct += 1

    # Calculate metrics
    accuracy = (correct / total_gt * 100) if total_gt > 0 else 0
    precision = (correct / total_model * 100) if total_model > 0 else 0
    recall = (correct / total_gt * 100) if total_gt > 0 else 0
    f1_score = (
        (2 * precision * recall / (precision + recall))
        if (precision + recall) > 0
        else 0
    )

    return {
        "field": field,
        "total_gt": total_gt,
        "total_model": total_model,
        "correct": correct,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
    }


def create_excel_report(wb, gt_df, model_df, results, matched_invoices):
    """Create Excel sheets with accuracy summary and field comparison"""

    # Remove default sheet
    if "Sheet" in wb.sheetnames:
        wb.remove(wb["Sheet"])

    # Styling
    header_fill = PatternFill(
        start_color="4472C4", end_color="4472C4", fill_type="solid"
    )
    header_font = Font(color="FFFFFF", bold=True)
    match_fill = PatternFill(
        start_color="C6EFCE", end_color="C6EFCE", fill_type="solid"
    )
    mismatch_fill = PatternFill(
        start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"
    )

    # Sheet 1: Accuracy Summary
    ws_summary = wb.create_sheet("Accuracy Summary")

    headers = [
        "Field",
        "Total GT",
        "Total Model",
        "Correct",
        "Accuracy (%)",
        "Precision (%)",
        "Recall (%)",
        "F1-Score (%)",
    ]
    for col, header in enumerate(headers, start=1):
        cell = ws_summary.cell(1, col, header)
        cell.fill = header_fill
        cell.font = header_font

    # Data rows
    for row_idx, result in enumerate(results, start=2):
        ws_summary.cell(row_idx, 1, result["field"])
        ws_summary.cell(row_idx, 2, result["total_gt"])
        ws_summary.cell(row_idx, 3, result["total_model"])
        ws_summary.cell(row_idx, 4, result["correct"])
        ws_summary.cell(row_idx, 5, f"{result['accuracy']:.2f}")
        ws_summary.cell(row_idx, 6, f"{result['precision']:.2f}")
        ws_summary.cell(row_idx, 7, f"{result['recall']:.2f}")
        ws_summary.cell(row_idx, 8, f"{result['f1_score']:.2f}")

    # Add summary row
    summary_row = len(results) + 3
    ws_summary.cell(summary_row, 1, "OVERALL SUMMARY").font = Font(bold=True)

    total_gt = sum(r["total_gt"] for r in results)
    total_model = sum(r["total_model"] for r in results)
    total_correct = sum(r["correct"] for r in results)

    overall_accuracy = (total_correct / total_gt * 100) if total_gt > 0 else 0
    overall_precision = (total_correct / total_model * 100) if total_model > 0 else 0
    overall_recall = (total_correct / total_gt * 100) if total_gt > 0 else 0
    overall_f1 = (
        (2 * overall_precision * overall_recall / (overall_precision + overall_recall))
        if (overall_precision + overall_recall) > 0
        else 0
    )

    ws_summary.cell(summary_row, 2, total_gt)
    ws_summary.cell(summary_row, 3, total_model)
    ws_summary.cell(summary_row, 4, total_correct)
    ws_summary.cell(summary_row, 5, f"{overall_accuracy:.2f}")
    ws_summary.cell(summary_row, 6, f"{overall_precision:.2f}")
    ws_summary.cell(summary_row, 7, f"{overall_recall:.2f}")
    ws_summary.cell(summary_row, 8, f"{overall_f1:.2f}")

    # Adjust column widths
    ws_summary.column_dimensions["A"].width = 25
    for col in ["B", "C", "D", "E", "F", "G", "H"]:
        ws_summary.column_dimensions[col].width = 15

    # Sheet 2: Detailed Comparison
    ws_compare = wb.create_sheet("Field Comparison")

    # Headers for comparison
    col = 1
    ws_compare.cell(1, col, "Invoice Name").fill = header_fill
    ws_compare.cell(1, col, "Invoice Name").font = header_font
    col += 1

    for field in EVAL_FIELDS:
        ws_compare.cell(1, col, f"GT_{field}").fill = header_fill
        ws_compare.cell(1, col, f"GT_{field}").font = header_font
        ws_compare.cell(1, col + 1, f"Model_{field}").fill = header_fill
        ws_compare.cell(1, col + 1, f"Model_{field}").font = header_font
        ws_compare.cell(1, col + 2, "Match").fill = header_fill
        ws_compare.cell(1, col + 2, "Match").font = header_font
        col += 3

    # Data rows - compare matched invoices
    row = 2
    for invoice_name in sorted(matched_invoices):
        gt_rows = gt_df[gt_df["invoice_name_normalized"] == invoice_name]
        model_rows = model_df[model_df["invoice_name_normalized"] == invoice_name]

        max_rows = max(len(gt_rows), len(model_rows))

        for i in range(max_rows):
            col = 1

            # Invoice name
            ws_compare.cell(row, col, invoice_name)
            col += 1

            # Compare each field
            for field in EVAL_FIELDS:
                gt_val = gt_rows.iloc[i][field] if i < len(gt_rows) else ""
                model_val = model_rows.iloc[i][field] if i < len(model_rows) else ""

                gt_str = str(gt_val) if pd.notna(gt_val) else ""
                model_str = str(model_val) if pd.notna(model_val) else ""

                # Write values
                ws_compare.cell(row, col, gt_str)
                ws_compare.cell(row, col + 1, model_str)

                # Match indicator
                match = normalize_value(gt_val) == normalize_value(model_val)
                ws_compare.cell(row, col + 2, "✓" if match else "✗")

                if match:
                    ws_compare.cell(row, col + 2).fill = match_fill
                else:
                    ws_compare.cell(row, col + 2).fill = mismatch_fill

                col += 3

            row += 1

    # Adjust column widths for comparison sheet
    ws_compare.column_dimensions["A"].width = 40
    for col_idx in range(2, len(EVAL_FIELDS) * 3 + 2):
        col_letter = ws_compare.cell(1, col_idx).column_letter
        ws_compare.column_dimensions[col_letter].width = 20

    return overall_accuracy, overall_precision, overall_recall, overall_f1
