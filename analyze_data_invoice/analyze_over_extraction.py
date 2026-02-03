#!/usr/bin/env python3
"""
Script to analyze over-extraction cases where Model has more rows than Ground Truth
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict

# Import common utilities
from accuracy_common import normalize_invoice_name

# Paths
BASE_DIR = Path(__file__).parent
TEST_DIR = BASE_DIR / "test-2026-02-03"
LABELS_DIR = BASE_DIR / "datasets" / "test-set-100" / "labels"
MODEL_OUTPUT_CSV = TEST_DIR / "test-set-100.csv"
OUTPUT_FILE = BASE_DIR / "over_extraction_analysis.md"


def load_ground_truth():
    """Load ground truth from JSON files"""
    import json

    rows = []
    json_files = list(LABELS_DIR.glob("**/*.json"))

    for json_file in json_files:
        try:
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

    descriptions = data.get("Description", [])
    if not isinstance(descriptions, list):
        descriptions = []

    for desc_item in descriptions:
        if not isinstance(desc_item, dict):
            continue

        row = {
            "invoice_name": invoice_name + ".pdf",
            "invoice_type": invoice_type,
            "Type": data.get("Type"),
            "No": data.get("No"),
            "Description": desc_item.get("text"),
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


def analyze_over_extraction(gt_df, model_df):
    """Analyze cases where model has more rows than GT"""

    results = []

    # Get all invoices
    all_invoices = set(gt_df["invoice_name_normalized"].unique()) | set(
        model_df["invoice_name_normalized"].unique()
    )

    for invoice_name in sorted(all_invoices):
        gt_rows = gt_df[gt_df["invoice_name_normalized"] == invoice_name]
        model_rows = model_df[model_df["invoice_name_normalized"] == invoice_name]

        gt_count = len(gt_rows)
        model_count = len(model_rows)

        if model_count > gt_count:
            # Over-extraction case
            over_count = model_count - gt_count

            # Get invoice details
            invoice_type = (
                gt_rows.iloc[0]["invoice_type"] if not gt_rows.empty else "Unknown"
            )
            invoice_no = gt_rows.iloc[0]["No"] if not gt_rows.empty else "N/A"

            # Get the extra rows
            extra_descriptions = []
            if model_count > 0:
                for i in range(gt_count, model_count):
                    if i < len(model_rows):
                        desc = model_rows.iloc[i].get("Description", "")
                        extra_descriptions.append(desc)

            results.append(
                {
                    "invoice_name": invoice_name,
                    "invoice_type": invoice_type,
                    "invoice_no": invoice_no,
                    "gt_rows": gt_count,
                    "model_rows": model_count,
                    "over_count": over_count,
                    "extra_descriptions": extra_descriptions,
                }
            )

    return results


def generate_report(results, gt_df, model_df):
    """Generate markdown report"""

    total_over_cases = len(results)
    total_extra_rows = sum(r["over_count"] for r in results)

    # Calculate what-if accuracy (if no over-extraction)
    total_gt_rows = len(gt_df)
    total_model_rows = len(model_df)

    # Current metrics
    current_precision_denominator = total_model_rows
    # If we remove extra rows
    corrected_model_rows = total_model_rows - total_extra_rows

    # Estimate impact on accuracy
    # Assuming 16 fields per row
    num_fields = 16
    current_total_comparisons = total_model_rows * num_fields
    corrected_total_comparisons = corrected_model_rows * num_fields

    report = []
    report.append("# Over-Extraction Analysis Report")
    report.append("")
    report.append(
        "**Phân tích các trường hợp Model trích xuất thừa (nhiều rows hơn Ground Truth)**"
    )
    report.append("")
    report.append("---")
    report.append("")

    # Summary
    report.append("## 1. Tổng Quan")
    report.append("")
    report.append(f"- **Tổng số invoices bị over-extract:** {total_over_cases}")
    report.append(f"- **Tổng số rows thừa:** {total_extra_rows}")
    report.append(
        f"- **Trung bình rows thừa/invoice:** {total_extra_rows/total_over_cases:.2f}"
        if total_over_cases > 0
        else "- **Trung bình rows thừa/invoice:** 0"
    )
    report.append("")
    report.append("### Số Liệu")
    report.append("")
    report.append(f"- **Total GT rows:** {total_gt_rows}")
    report.append(f"- **Total Model rows (current):** {total_model_rows}")
    report.append(
        f"- **Total Model rows (if no over-extraction):** {corrected_model_rows}"
    )
    report.append(
        f"- **Reduction:** {total_extra_rows} rows ({total_extra_rows/total_model_rows*100:.2f}%)"
    )
    report.append("")

    # Impact on metrics
    report.append("### Impact on Metrics")
    report.append("")
    report.append("Over-extraction làm giảm **Precision** vì:")
    report.append("- Model output có nhiều rows hơn → Total Model tăng")
    report.append("- Các rows thừa không match với GT → Correct không tăng")
    report.append("- Precision = Correct / Total Model → giảm")
    report.append("")
    report.append("**Ước tính impact:**")
    report.append("")
    report.append(f"- Current: {current_total_comparisons:,} field comparisons")
    report.append(f"- If corrected: {corrected_total_comparisons:,} field comparisons")
    report.append(
        f"- Reduction: {current_total_comparisons - corrected_total_comparisons:,} comparisons ({(current_total_comparisons - corrected_total_comparisons)/current_total_comparisons*100:.2f}%)"
    )
    report.append("")
    report.append(
        "> **Note:** Nếu loại bỏ over-extraction, Precision sẽ tăng vì denominator giảm."
    )
    report.append("> Accuracy có thể tăng nhẹ nếu các rows thừa chứa nhiều errors.")
    report.append("")
    report.append("---")
    report.append("")

    # Group by invoice type
    report.append("## 2. Phân Tích Theo Loại Invoice")
    report.append("")

    type_stats = defaultdict(lambda: {"count": 0, "total_extra": 0})
    for r in results:
        inv_type = r["invoice_type"]
        type_stats[inv_type]["count"] += 1
        type_stats[inv_type]["total_extra"] += r["over_count"]

    report.append(
        "| Invoice Type | Số Invoice Bị Over-Extract | Tổng Rows Thừa | Trung Bình |"
    )
    report.append(
        "| :----------- | :------------------------- | :------------- | :--------- |"
    )

    for inv_type in sorted(type_stats.keys()):
        stats = type_stats[inv_type]
        avg = stats["total_extra"] / stats["count"]
        report.append(
            f"| {inv_type} | {stats['count']} | {stats['total_extra']} | {avg:.2f} |"
        )

    report.append("")
    report.append("---")
    report.append("")

    # Detailed cases
    report.append("## 3. Chi Tiết Các Trường Hợp")
    report.append("")

    # Sort by over_count descending
    results_sorted = sorted(results, key=lambda x: x["over_count"], reverse=True)

    for idx, r in enumerate(results_sorted[:20], 1):  # Top 20
        report.append(f"### {idx}. {r['invoice_name']}")
        report.append("")
        report.append(f"- **Invoice Type:** {r['invoice_type']}")
        report.append(f"- **Invoice No:** {r['invoice_no']}")
        report.append(f"- **GT Rows:** {r['gt_rows']}")
        report.append(f"- **Model Rows:** {r['model_rows']}")
        report.append(f"- **Over-extracted:** {r['over_count']} rows")
        report.append("")

        if r["extra_descriptions"]:
            report.append("**Extra Descriptions (Model extracted but not in GT):**")
            report.append("")
            for i, desc in enumerate(r["extra_descriptions"], 1):
                desc_str = (
                    str(desc)[:100] + "..." if len(str(desc)) > 100 else str(desc)
                )
                report.append(f"{i}. `{desc_str}`")
            report.append("")

        report.append("---")
        report.append("")

    if len(results_sorted) > 20:
        report.append(f"*... và {len(results_sorted) - 20} trường hợp khác*")
        report.append("")

    # Recommendations
    report.append("## 4. Khuyến Nghị")
    report.append("")
    report.append("### Nguyên nhân có thể:")
    report.append("")
    report.append(
        "1. **Model extract header/footer rows** - Các dòng tiêu đề hoặc tổng cộng không nên được extract"
    )
    report.append("2. **Model split 1 row thành nhiều rows** - Parsing error")
    report.append("3. **Model extract duplicate rows** - Lỗi logic")
    report.append("4. **Ground Truth thiếu rows** - Cần review lại GT")
    report.append("")
    report.append("### Hành động:")
    report.append("")
    report.append("- Review các extra descriptions để identify pattern")
    report.append("- Kiểm tra xem có phải header/footer/total rows không")
    report.append("- Validate Ground Truth có đầy đủ không")
    report.append("- Cải thiện prompt để tránh extract thừa")
    report.append("")

    return "\n".join(report)


def main():
    """Main function"""
    print("=" * 80)
    print("OVER-EXTRACTION ANALYSIS")
    print("=" * 80)

    print("\n[1/3] Loading data...")
    gt_df = load_ground_truth()
    model_df = load_model_output()

    if gt_df.empty or model_df.empty:
        print("  ERROR: Cannot load data")
        return

    print(f"  Ground truth rows: {len(gt_df)}")
    print(f"  Model output rows: {len(model_df)}")

    print("\n[2/3] Analyzing over-extraction cases...")
    results = analyze_over_extraction(gt_df, model_df)

    print(f"  Found {len(results)} over-extraction cases")
    print(f"  Total extra rows: {sum(r['over_count'] for r in results)}")

    print("\n[3/3] Generating report...")
    report = generate_report(results, gt_df, model_df)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✓ Report saved to: {OUTPUT_FILE}")
    print("=" * 80)


if __name__ == "__main__":
    main()
