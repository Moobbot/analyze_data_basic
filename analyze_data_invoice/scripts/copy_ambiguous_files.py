#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
copy_ambiguous_files.py
Copy files flagged with ambiguous dates for review
"""

import shutil
import sys
import re
from pathlib import Path

# Add project root to path
try:
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
except NameError:
    pass

import config


def copy_ambiguous_files(audit_report_path):
    """Copy files marked ambiguous for review"""
    report_path = Path(audit_report_path)
    if not report_path.exists():
        print(f"❌ Audit report không tồn tại: {report_path}")
        return

    # Destination directory
    review_dir = config.REVIEW_DIR / "ambiguous_review"

    # Cleanup destination
    if review_dir.exists():
        try:
            shutil.rmtree(review_dir, ignore_errors=True)
        except Exception as e:
            print(f"⚠️  Cảnh báo: Không thể xóa review directory: {e}")

    review_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 80}")
    print("📋 SAO CHÉP FILE AMBIGUOUS")
    print(f"{'=' * 80}")
    print(f"Báng cáo: {report_path}")
    print(f"Thư mục đích: {review_dir}\n")

    count = 0
    missing_files = 0

    with open(report_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        match = re.match(r"^\[(\?|OK)\]\s+(.*?\.json):", line)
        if not match:
            continue

        status = "check" if match.group(1) == "?" else "verified"
        json_filename = match.group(2)

        # Find JSON file
        found_json = list(config.LABEL_DIR.rglob(json_filename))
        if not found_json:
            print(f"⚠️  Cảnh báo: Không tìm thấy JSON: {json_filename}")
            missing_files += 1
            continue

        json_path = found_json[0]
        file_stem = json_path.stem

        # Find PDF file
        found_pdf = list(config.DATASET_DIR.rglob(f"{file_stem}.*"))
        pdf_path = None
        for p in found_pdf:
            if p.suffix.lower() in [".pdf", ".jpg", ".png", ".jpeg"]:
                pdf_path = p
                break

        # Find TXT file
        found_txt = list(config.EXTRACTED_TEXT_DIR.rglob(f"{file_stem}.txt"))
        txt_path = found_txt[0] if found_txt else None

        # Prepare destination folder
        safe_stem = file_stem.strip()
        dest_folder = review_dir / status / safe_stem

        try:
            dest_folder.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"❌ Lỗi tạo thư mục cho {safe_stem}: {e}")
            continue

        # Copy files
        try:
            # Copy JSON
            shutil.copy2(json_path, dest_folder / json_path.name)

            # Copy PDF
            if pdf_path:
                shutil.copy2(pdf_path, dest_folder / pdf_path.name)
            else:
                with open(dest_folder / "MISSING_PDF.txt", "w") as mf:
                    mf.write(f"PDF not found for {json_filename}")

            # Copy TXT
            if txt_path:
                shutil.copy2(txt_path, dest_folder / txt_path.name)
            else:
                with open(dest_folder / "MISSING_TXT.txt", "w") as mf:
                    mf.write(f"TXT not found for {json_filename}")

            count += 1

        except Exception as e:
            print(f"❌ Lỗi sao chép {json_filename}: {e}")

    print(f"\n{'=' * 80}")
    print("📊 KẾT QUẢ")
    print(f"{'=' * 80}")
    print(f"✅ Tổng file được sao chép: {count}")
    print(f"❌ File bị thiếu: {missing_files}")
    print(f"📁 Thư mục review: {review_dir}")


if __name__ == "__main__":
    report_file = Path("ambiguous_dates_audit.txt")
    if not report_file.exists():
        report_file = Path(__file__).parent.parent / "ambiguous_dates_audit.txt"

    copy_ambiguous_files(report_file)
