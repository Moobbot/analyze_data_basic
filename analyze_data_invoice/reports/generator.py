import os
import config


def read_lines(path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return [l.strip() for l in f.readlines()]
    return []


def count_lines_in_csv(path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return sum(1 for line in f) - 1  # Subtract header
    return 0


def generate_reports():
    print("Generating Final Reports...")

    # Output Paths
    report_overview = config.REVIEW_DIR / "General_Overview_Report.md"
    report_errors = config.REVIEW_DIR / "Detailed_Error_Report.md"

    # Gather Data
    # 1. File Stats
    summary_txt = ""
    summary_path = config.REVIEW_DIR / "data_summary_report.txt"
    if summary_path.exists():
        with open(summary_path, "r", encoding="utf-8") as f:
            summary_txt = f.read()

    # 2. PDF Issues
    pdf_errors = read_lines(config.ERROR_PDF_REPORT)
    pdf_images = read_lines(config.IMAGE_PDF_REPORT)

    count_pdf_errors = max(0, len(pdf_errors) - 3)
    count_pdf_images = max(0, len(pdf_images) - 3)

    # 3. Label Verification
    missing_csv = (
        config.OUTPUT_FILTER_MISSING
    )  # Actually this file isn't created by verify_labels yet, relying on VERIFY_REPORT_CSV mostly.
    # But wait, original code referenced "label_verification_missing.csv".
    # My refactored verify_labels didn't explicitly create it yet, only the main CSV.
    # To be safe, I should update verification to output split CSVs or just use the main one here.
    # For now, I'll rely on the main stats or skipping if not present.
    # Actually, verify_labels currently only outputs verify_report.csv.
    # I should add splitting logic to verification later or just report from main csv stats.

    verify_txt = ""
    if config.VERIFY_REPORT_TXT.exists():
        with open(config.VERIFY_REPORT_TXT, "r", encoding="utf-8") as f:
            verify_txt = f.read()

    # --- 1. GENERAL OVERVIEW REPORT ---
    with open(report_overview, "w", encoding="utf-8") as f:
        f.write("# BÁO CÁO TỔNG QUAN HỆ THỐNG XỬ LÝ DỮ LIỆU\n\n")

        f.write("## 1. Tình trạng dữ liệu gốc (Files)\n")
        f.write("Dựa trên kết quả phân tích file ban đầu:\n")
        f.write("```\n")
        f.write(summary_txt)
        f.write("\n```\n\n")

        f.write("## 2. Kết quả trích xuất PDF (Extraction)\n")
        f.write(f"- Thư viện sử dụng: **PyMuPDF (fitz)**\n")
        f.write(f"- Tổng số file lỗi (Không đọc được): **{count_pdf_errors}**\n")
        f.write(
            f"- Tổng số file dạng ảnh/scan (Không có text): **{count_pdf_images}**\n\n"
        )

        f.write("## 3. Kết quả đối soát nhãn (Label Verification)\n")
        f.write("So sánh dữ liệu file JSON (Label) với Text trích xuất:\n")
        # f.write(f"- Số trường MISSING (Không tìm thấy): **{count_missing_fields}**\n")
        # f.write(f"- Số trường SIMILAR (Tương đồng > 80%): **{count_similar_fields}**\n")
        f.write("- Chi tiết thống kê:\n")
        f.write("```\n")
        f.write(verify_txt)
        f.write("\n```\n")

    print(f"Created: {report_overview}")

    # --- 2. DETAILED ERROR REPORT ---
    with open(report_errors, "w", encoding="utf-8") as f:
        f.write("# BÁO CÁO CHI TIẾT LỖI & VẤN ĐỀ\n\n")

        f.write("## 1. Các file PDF bị lỗi (Corrupt/Error)\n")
        f.write(f"Tổng số: {count_pdf_errors}\n")
        if count_pdf_errors > 0:
            f.write("| Tên File | Lỗi |\n|---|---|\n")
            for line in pdf_errors[2:]:
                if "|" in line:
                    parts = line.split("|", 1)
                    f.write(f"| {parts[0].strip()} | {parts[1].strip()} |\n")
                elif line.strip():
                    f.write(f"| {line.strip()} | - |\n")
        else:
            f.write("> Không có file lỗi.\n")

        f.write("\n## 2. Các file PDF dạng ảnh/Scan (Cần OCR)\n")
        f.write(f"Tổng số: {count_pdf_images}\n")
        if count_pdf_images > 0:
            f.write("```\n")
            for line in pdf_images[2:]:
                f.write(line + "\n")
            f.write("```\n")
        else:
            f.write("> Không có file dạng ảnh.\n")

        f.write("\n## 3. Vấn đề đối soát dữ liệu (Verification Issues)\n")
        f.write("### A. Dữ liệu KHÔNG tìm thấy (Missing)\n")
        f.write(f"- Xem chi tiết file: {config.VERIFY_REPORT_CSV}\n")
        f.write("- Các trường hợp phổ biến cần kiểm tra:\n")
        f.write("  - Lỗi format ngày tháng (dd/mm/yyyy vs mm/dd/yyyy).\n")
        f.write("  - Lỗi format số tiền (dấu phẩy/chấm).\n")
        f.write("  - OCR đọc sai ký tự (O vs 0, I vs 1).\n")
        f.write("  - Key trong JSON không tồn tại trong văn bản.\n")

    print(f"Created: {report_errors}")


if __name__ == "__main__":
    generate_reports()
