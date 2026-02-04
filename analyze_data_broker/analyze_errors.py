#!/usr/bin/env python3
"""
Detailed error analysis for Broker Extraction
Comparisons are made row-by-row on raw data
Generates Markdown report
"""

import pandas as pd
import importlib.util
from pathlib import Path
import sys

# Add parent directory to path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from broker_accuracy_common import (
    are_values_equivalent,
    CONTRACT_NOTE_FIELDS,
    DIVIDEND_FIELDS,
    FX_TRADE_FIELDS,
    INTEREST_PAYMENT_FIELDS,
    TRADE_CONFIRMATION_FIELDS,
)

# Output Path
OUTPUT_FILE = BASE_DIR / "danh_gia_ket_qua" / "2026_02_04" / "broker_error_report.md"

# Configuration for each document type
DOC_TYPES = [
    {
        "name": "Contract Note",
        "script": "calculate_accuracy_contract_note.py",
        "fields": CONTRACT_NOTE_FIELDS,
    },
    {
        "name": "Dividend Advice",
        "script": "calculate_accuracy_dividend.py",
        "fields": DIVIDEND_FIELDS,
    },
    {
        "name": "FX Trade",
        "script": "calculate_accuracy_fx_trade.py",
        "fields": FX_TRADE_FIELDS,
    },
    {
        "name": "Interest Payment",
        "script": "calculate_accuracy_interest.py",
        "fields": INTEREST_PAYMENT_FIELDS,
    },
    {
        "name": "Trade Confirmation",
        "script": "calculate_accuracy_trade_conf.py",
        "fields": TRADE_CONFIRMATION_FIELDS,
    },
]


def load_module(script_name):
    """Dynamically load module from file path"""
    file_path = BASE_DIR / script_name
    spec = importlib.util.spec_from_file_location("module", file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["module"] = module
    spec.loader.exec_module(module)
    return module


def analyze_dataset(name, gt_df, model_df, fields):
    """Analyze dataset and return report lines"""
    report = []
    report.append(f"## {name}")
    report.append("")

    # Match documents
    gt_files = set(gt_df["_filename_normalized"].unique())
    model_files = set(model_df["_filename_normalized"].unique())
    matched_files = sorted(list(gt_files & model_files))

    report.append(f"- **Total Matched Files:** {len(matched_files)}")
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
        for field in fields
    }
    error_examples = {field: [] for field in fields}

    for filename in matched_files:
        gt_rows = gt_df[gt_df["_filename_normalized"] == filename]
        model_rows = model_df[model_df["_filename_normalized"] == filename]

        max_rows = max(len(gt_rows), len(model_rows))

        for i in range(max_rows):
            gt_row = gt_rows.iloc[i].to_dict() if i < len(gt_rows) else {}
            model_row = model_rows.iloc[i].to_dict() if i < len(model_rows) else {}

            for field in fields:
                field_errors[field]["total"] += 1

                gt_val = gt_row.get(field) if gt_row else ""
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
                            {"file": filename, "gt": gt_str, "model": model_str}
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

            report.append(f"- **{ex['file']}**")
            report.append(f"  - GT: `{gt_disp}`")
            report.append(f"  - Model: `{model_disp}`")
        report.append("")

    report.append("---")
    report.append("")

    return report


def main():
    print("STARTING DETAILED ERROR ANALYSIS...")

    report_lines = []
    report_lines.append("# Broker Error Analysis Report")
    report_lines.append("")
    report_lines.append("**Cập nhật:** 2026-02-04")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    for doc_config in DOC_TYPES:
        name = doc_config["name"]
        script = doc_config["script"]
        fields = doc_config["fields"]

        try:
            print(f"\nLoading module: {script}")
            module = load_module(script)

            # Helper to find load function
            def get_data(module):
                # Try generic names
                if hasattr(module, "load_ground_truth"):
                    gt = module.load_ground_truth()
                elif hasattr(module, "load_gt"):
                    gt = module.load_gt()
                else:
                    raise AttributeError("Cannot find load_ground_truth function")

                if hasattr(module, "load_model_output"):
                    model = module.load_model_output()
                elif hasattr(module, "load_model"):
                    model = module.load_model()
                else:
                    raise AttributeError("Cannot find load_model_output function")
                return gt, model

            gt_df, model_df = get_data(module)

            if gt_df.empty or model_df.empty:
                print(f"Skipping {name} due to empty data")
                continue

            # Apply column mapping if needed (Contract Note has different column names)
            if name == "Contract Note":
                column_mapping = {
                    "Transaction Type": "Transaction type",
                    "Trade Date": "Trade date",
                    "Settlement Date": "Settlement date",
                }
                model_df = model_df.rename(columns=column_mapping)

            report_lines.extend(analyze_dataset(name, gt_df, model_df, fields))

        except Exception as e:
            print(f"Failed to analyze {name}: {e}")
            import traceback

            traceback.print_exc()

    # Write to file
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\n✓ Report saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
