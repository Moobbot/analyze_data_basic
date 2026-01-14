import os
import config

from datetime import datetime


def merge(
    report_path=config.DEFAULT_OUTPUT_REPORT,
    diff_path=config.DEFAULT_OUTPUT_DIFF,
    output_path=config.DEFAULT_OUTPUT_FINAL,
):
    report_content = ""
    if report_path.exists():
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()

    diff_content = ""
    if diff_path.exists():
        with open(diff_path, "r", encoding="utf-8") as f:
            diff_content = f.read()

    final_lines = []
    final_lines.append("BÁO CÁO TỔNG HỢP DỮ LIỆU (DATA REPORT)")
    final_lines.append("=" * 80)
    final_lines.append(f"Thời gian tạo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    final_lines.append("=" * 80)

    final_lines.append("\nI. THỐNG KÊ CHI TIẾT (STATISTICS)")
    final_lines.append("-" * 80)
    final_lines.append(report_content)

    final_lines.append("\n\n" + "=" * 80)
    final_lines.append("II. SO SÁNH & KHÁC BIỆT FILE (FILE DIFFERENCES)")
    final_lines.append("-" * 80)
    final_lines.append(diff_content)

    final_lines.append("\n\n" + "=" * 80)
    final_lines.append("KẾT THÚC BÁO CÁO")

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(final_lines))
        print(f"Final summary created successfully at:\n{output_path}")
    except Exception as e:
        print(f"Error writing final summary: {e}")


if __name__ == "__main__":
    merge()
