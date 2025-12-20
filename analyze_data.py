import os
import csv
from collections import Counter, defaultdict
import config
import utils


def analyze_directories(
    output_csv=config.DEFAULT_OUTPUT_CSV, output_report=config.DEFAULT_OUTPUT_REPORT
):
    all_files = []
    report_lines = []

    report_lines.append("BÁO CÁO THỐNG KÊ DỮ LIỆU CHI TIẾT")
    report_lines.append("=" * 60)

    for category, path in config.DIRECTORIES.items():
        if not os.path.exists(path):
            print(f"Error: Directory not found: {path}")
            continue

        report_lines.append(f"\n[{category}]")
        report_lines.append("-" * 40)

        file_list = []
        sizes = []
        non_pdf_files = []
        basename_map = defaultdict(list)

        try:
            for f in os.listdir(path):
                full_path = os.path.join(path, f)
                if os.path.isfile(full_path):
                    file_list.append(f)
                    size = os.path.getsize(full_path)
                    sizes.append(size)

                    ext = os.path.splitext(f)[1].lower()

                    # Track non-PDFs (specifically for Dataset, but good general info)
                    if category == "Dataset" and ext != ".pdf":
                        non_pdf_files.append(f)

                    # Group by basename for duplicate check
                    basename = os.path.splitext(f)[0]
                    basename_map[basename].append(f)

                    all_files.append(
                        {
                            "Category": category,
                            "FileName": f,
                            "Extension": ext,
                            "SizeBytes": size,
                            "ReadableSize": utils.format_size(size),
                        }
                    )
        except Exception as e:
            print(f"Error reading {category}: {e}")
            continue

        # 1. Quantity & Types
        total_count = len(file_list)
        extensions = [os.path.splitext(f)[1].lower() for f in file_list]
        type_counts = Counter(extensions)

        report_lines.append(f"1. Số lượng & Định dạng:")
        report_lines.append(f"   - Tổng số file: {total_count}")
        for ext, count in type_counts.items():
            report_lines.append(f"   - {ext}: {count}")

        # 2. Size Statistics
        if sizes:
            min_size = min(sizes)
            max_size = max(sizes)
            avg_size = sum(sizes) / len(sizes)
            report_lines.append(f"\n2. Thống kê kích thước file:")
            report_lines.append(f"   - Nhỏ nhất: {utils.format_size(min_size)}")
            report_lines.append(f"   - Lớn nhất: {utils.format_size(max_size)}")
            report_lines.append(f"   - Trung bình: {utils.format_size(avg_size)}")
            report_lines.append(
                f"   - Khoảng kích thước: {utils.format_size(min_size)} - {utils.format_size(max_size)}"
            )

        # 3. Non-PDF Files (Dataset Only)
        if category == "Dataset":
            report_lines.append(
                f"\n3. Danh sách file KHÔNG PHẢI PDF ({len(non_pdf_files)} file):"
            )
            if non_pdf_files:
                for npf in non_pdf_files:
                    report_lines.append(f"   - {npf}")
            else:
                report_lines.append("   (Không có)")

        # 4. Duplicate Names (Same basename, different extensions)
        duplicates = {k: v for k, v in basename_map.items() if len(v) > 1}
        report_lines.append(
            f"\n4. Các file trùng tên (khác đuôi mở rộng): {len(duplicates)} nhóm"
        )
        if duplicates:
            for base, files in duplicates.items():
                report_lines.append(f"   - {base}: {', '.join(files)}")
        else:
            report_lines.append("   (Không có)")

    # Write CSV
    try:
        with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "Category",
                "FileName",
                "Extension",
                "SizeBytes",
                "ReadableSize",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for data in all_files:
                writer.writerow(data)
        print(f"Detailed statistics saved to {os.path.abspath(output_csv)}")
    except Exception as e:
        print(f"Error writing CSV: {e}")

    # Write Report
    try:
        with open(output_report, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
        print(f"Summary report saved to {os.path.abspath(output_report)}")
    except Exception as e:
        print(f"Error writing Report: {e}")


if __name__ == "__main__":
    analyze_directories()
