#!/usr/bin/env python3
"""
Analyze over-extraction cases where Model has more rows than Ground Truth
Supports multiple broker document types
"""

import pandas as pd
import importlib.util
from pathlib import Path
import sys
from collections import defaultdict

# Add parent directory to path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Configuration for each document type
DOC_TYPES = [
    {"name": "Contract Note", "script": "calculate_accuracy_contract_note.py"},
    {"name": "Dividend Advice", "script": "calculate_accuracy_dividend.py"},
    {"name": "FX Trade", "script": "calculate_accuracy_fx_trade.py"},
    {"name": "Interest Payment", "script": "calculate_accuracy_interest.py"},
    {"name": "Trade Confirmation", "script": "calculate_accuracy_trade_conf.py"},
]

OUTPUT_FILE = (
    BASE_DIR / "danh_gia_ket_qua" / "2026_02_04" / "broker_over_extraction_analysis.md"
)


def load_module(script_name):
    """Dynamically load module from file path"""
    file_path = BASE_DIR / script_name
    spec = importlib.util.spec_from_file_location("module", file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["module"] = module
    spec.loader.exec_module(module)
    return module


def analyze_over_extraction(doc_type, gt_df, model_df):
    """Analyze cases where model has more rows than GT"""
    results = []

    # Get all filenames
    all_files = set(gt_df["_filename_normalized"].unique()) | set(
        model_df["_filename_normalized"].unique()
    )

    for filename in sorted(all_files):
        gt_rows = gt_df[gt_df["_filename_normalized"] == filename]
        model_rows = model_df[model_df["_filename_normalized"] == filename]

        gt_count = len(gt_rows)
        model_count = len(model_rows)

        if model_count > gt_count:
            # Over-extraction
            over_count = model_count - gt_count

            # Try to get some ID or description to identify the extra rows
            extra_details = []
            if model_count > 0:
                for i in range(gt_count, model_count):
                    if i < len(model_rows):
                        # Try common identifying fields
                        row = model_rows.iloc[i]
                        detail = ""
                        for field in [
                            "Description",
                            "Security Name",
                            "Name/ Security",
                            "Transaction type",
                            "Amount",
                        ]:
                            if field in row and pd.notna(row[field]):
                                detail += f"{field}: {row[field]} | "
                        extra_details.append(detail.strip(" | "))

            results.append(
                {
                    "doc_type": doc_type,
                    "filename": filename,
                    "gt_rows": gt_count,
                    "model_rows": model_count,
                    "over_count": over_count,
                    "extra_details": extra_details,
                }
            )

    return results


def generate_report(all_results):
    """Generate markdown report"""
    report = []
    report.append("# Broker Over-Extraction Analysis Report")
    report.append("")
    report.append("**Cập nhật:** 2026-02-04")
    report.append("")
    report.append("---")
    report.append("")

    total_over = sum(len(r) for r in all_results.values())
    total_rows = sum(
        sum(item["over_count"] for item in r) for r in all_results.values()
    )

    report.append("## 1. Tổng Quan")
    report.append("")
    report.append(f"- **Tổng số documents bị over-extract:** {total_over}")
    report.append(f"- **Tổng số rows thừa:** {total_rows}")
    report.append("")

    # Per Doc Type Stats
    report.append("## 2. Thống Kê Theo Loại Document")
    report.append("")
    report.append("| Document Type | Documents Count | Extra Rows | Avg Extra/Doc |")
    report.append("| :--- | :--- | :--- | :--- |")

    for doc_type, results in all_results.items():
        count = len(results)
        extra = sum(r["over_count"] for r in results)
        avg = extra / count if count > 0 else 0
        report.append(f"| {doc_type} | {count} | {extra} | {avg:.1f} |")

    report.append("")
    report.append("---")
    report.append("")

    # Details
    report.append("## 3. Chi Tiết Các Trường Hợp")
    report.append("")

    for doc_type, results in all_results.items():
        if not results:
            continue

        report.append(f"### {doc_type}")
        report.append("")

        # Sort by over_count descending
        sorted_res = sorted(results, key=lambda x: x["over_count"], reverse=True)

        for r in sorted_res[:10]:  # Top 10 per type
            report.append(f"#### {r['filename']}")
            report.append(
                f"- **GT Rows:** {r['gt_rows']} | **Model Rows:** {r['model_rows']} (**+{r['over_count']}**)"
            )
            if r["extra_details"]:
                report.append(f"- Extra Info: {', '.join(r['extra_details'][:3])}")
                if len(r["extra_details"]) > 3:
                    report.append(f"  ...and {len(r['extra_details'])-3} more")
            report.append("")

        if len(sorted_res) > 10:
            report.append(f"*... và {len(sorted_res) - 10} trường hợp khác*")

        report.append("---")
        report.append("")

    return "\n".join(report)


def main():
    print("STARTING OVER-EXTRACTION ANALYSIS...")

    all_results = defaultdict(list)

    for doc_config in DOC_TYPES:
        name = doc_config["name"]
        script = doc_config["script"]

        try:
            print(f"\nLoading module: {script}")
            module = load_module(script)

            # Helper to find load function
            def get_data(module):
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

            results = analyze_over_extraction(name, gt_df, model_df)
            if results:
                all_results[name] = results
                print(f"  Found {len(results)} over-extraction cases")
            else:
                print(f"  No over-extraction found")

        except Exception as e:
            print(f"Failed to analyze {name}: {e}")
            import traceback

            traceback.print_exc()

    # Generate Report
    if all_results:
        report = generate_report(all_results)
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\nReport saved to: {OUTPUT_FILE}")
    else:
        print("\nNo over-extraction cases found across all document types.")


if __name__ == "__main__":
    main()
