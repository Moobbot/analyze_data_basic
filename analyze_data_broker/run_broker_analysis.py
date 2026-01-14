#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
run_broker_analysis.py
Chạy kiểm tra dữ liệu cho các datasets của analyze_data_broker
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Add paths
BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR.parent))

# Config cho từng dataset
DATASETS = {
    "Account_Statements": {
        "name": "Tuyên bố tài khoản",
        "files_dir": "datasets/files/Account_Statements",
        "labels_dir": "datasets/labels/Account_Statements",
    },
    "Dividend": {
        "name": "Cổ tức",
        "files_dir": "datasets/files/Dividend",
        "labels_dir": "datasets/labels/Dividend",
    },
    "FX-FT": {
        "name": "Ngoại tệ - Chuyển tiền",
        "files_dir": "datasets/files/FX-FT",
        "labels_dir": "datasets/labels/FX-FT",
    },
    "Others_Template": {
        "name": "Mẫu khác",
        "files_dir": "datasets/files/Others_Template",
        "labels_dir": "datasets/labels/Others_Template",
    },
}


def analyze_dataset(dataset_key, dataset_info):
    """Phân tích một dataset"""
    print(f"\n{'=' * 80}")
    print(f"📊 KIỂM TRA DATASET: {dataset_key} ({dataset_info['name']})")
    print(f"{'=' * 80}")

    files_dir = BASE_DIR / dataset_info["files_dir"]
    labels_dir = BASE_DIR / dataset_info["labels_dir"]
    output_dir = BASE_DIR / "output_analyze" / dataset_key

    # Tạo output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Khởi tạo thống kê
    stats = {
        "dataset": dataset_key,
        "timestamp": datetime.now().isoformat(),
        "files_count": 0,
        "labels_count": 0,
        "pdf_files": [],
        "json_files": [],
        "file_size_info": [],
        "page_info": [],
        "errors": [],
    }

    # 1. Kiểm tra và đếm files
    print(f"\n>>> [BƯỚC 1] KIỂM TRA CẤU TRÚC THƯ MỤC")
    if not files_dir.exists():
        print(f"❌ Thư mục files không tồn tại: {files_dir}")
        stats["errors"].append(f"Files directory not found: {files_dir}")
        return stats

    if not labels_dir.exists():
        print(f"⚠️  Thư mục labels không tồn tại: {labels_dir}")
        stats["errors"].append(f"Labels directory not found: {labels_dir}")

    # Đếm PDF files (bao gồm subfolder)
    pdf_files = list(files_dir.rglob("*.pdf"))
    stats["files_count"] = len(pdf_files)
    print(f"✅ Tìm thấy {stats['files_count']} file PDF")

    # Kiểm tra subfolders
    subfolders = [d for d in files_dir.iterdir() if d.is_dir()]
    if subfolders:
        print(f"✅ Tìm thấy {len(subfolders)} subfolder:")
        for sf in subfolders:
            sf_files = list(sf.glob("*.pdf"))
            stats["subfolders"] = []
            stats["subfolders"].append({"name": sf.name, "count": len(sf_files)})
            print(f"   • {sf.name}: {len(sf_files)} files")

    # Đếm JSON labels (bao gồm subfolder)
    if labels_dir.exists():
        json_files = list(labels_dir.rglob("*.json"))
        stats["labels_count"] = len(json_files)
        print(f"✅ Tìm thấy {stats['labels_count']} file JSON nhãn")

    # 2. Phân tích PDF
    print(f"\n>>> [BƯỚC 2] PHÂN TÍCH CHI TIẾT PDF")
    try:
        import fitz  # PyMuPDF

        for i, pdf_path in enumerate(pdf_files, 1):
            try:
                with fitz.open(pdf_path) as doc:
                    pages = len(doc)
                    text_content = ""
                    for page in doc:
                        text_content += page.get_text() + "\n"

                    file_size_kb = pdf_path.stat().st_size / 1024
                    is_encrypted = doc.is_encrypted
                    is_empty = len(text_content.strip()) == 0

                    # Kiểm tra nhãn tương ứng
                    json_name = pdf_path.stem + ".json"
                    json_path = labels_dir / json_name if labels_dir.exists() else None
                    has_label = json_path.exists() if json_path else False

                    info = {
                        "filename": pdf_path.name,
                        "pages": pages,
                        "text_length": len(text_content.strip()),
                        "is_empty": is_empty,
                        "is_encrypted": is_encrypted,
                        "file_size_kb": round(file_size_kb, 2),
                        "has_label": has_label,
                        "status": "success",
                    }
                    stats["page_info"].append(info)

                    if (i) % 50 == 0:
                        print(f"   ✓ Xử lý {i}/{stats['files_count']} files")

            except Exception as e:
                error_info = {
                    "filename": pdf_path.name,
                    "error": str(e)[:100],
                }
                stats["errors"].append(error_info)
                print(f"   ⚠️  Lỗi khi xử lý {pdf_path.name}: {str(e)[:50]}")

        print(f"✅ Hoàn thành phân tích {stats['files_count']} file PDF")

    except ImportError:
        print("❌ PyMuPDF (fitz) chưa được cài đặt")
        stats["errors"].append("PyMuPDF not installed")

    # 3. Tạo báng cáo CSV
    print(f"\n>>> [BƯỚC 3] TẠO BÁ NG CÁO")

    csv_file = output_dir / "pdf_page_info.csv"
    try:
        with open(csv_file, "w", encoding="utf-8") as f:
            f.write(
                "Filename,Pages,TextLength,IsEmpty,IsEncrypted,FileSizeKB,HasLabel,Status\n"
            )
            for info in stats["page_info"]:
                f.write(
                    f"{info['filename']},{info['pages']},{info['text_length']},{info['is_empty']},{info['is_encrypted']},{info['file_size_kb']},{info['has_label']},\"{info['status']}\"\n"
                )
        print(f"✅ Báng cáo PDF lưu tại: {csv_file}")
    except Exception as e:
        print(f"❌ Lỗi khi tạo báng cáo: {e}")
        stats["errors"].append(f"CSV report error: {str(e)}")

    # 4. Tạo báng cáo text tóm tắt
    summary_file = output_dir / "analysis_summary.txt"
    try:
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(f"{'=' * 80}\n")
            f.write(f"KIỂM TRA DATASET: {dataset_key}\n")
            f.write(f"Tên: {dataset_info['name']}\n")
            f.write(f"Thời gian: {stats['timestamp']}\n")
            f.write(f"{'=' * 80}\n\n")

            f.write(f"THỐNG KÊ CƠ BẢN:\n")
            f.write(f"  • Tổng PDF: {stats['files_count']}\n")
            f.write(f"  • Tổng nhãn: {stats['labels_count']}\n")

            if stats["page_info"]:
                has_text = sum(1 for p in stats["page_info"] if not p["is_empty"])
                is_empty = sum(1 for p in stats["page_info"] if p["is_empty"])
                is_encrypted = sum(1 for p in stats["page_info"] if p["is_encrypted"])

                f.write(
                    f"  • File có text: {has_text} ({100*has_text/len(stats['page_info']):.1f}%)\n"
                )
                f.write(
                    f"  • File rỗng/scan: {is_empty} ({100*is_empty/len(stats['page_info']):.1f}%)\n"
                )
                f.write(f"  • File bị mã hóa: {is_encrypted}\n")

                total_pages = sum(
                    p["pages"]
                    for p in stats["page_info"]
                    if isinstance(p["pages"], int)
                )
                avg_pages = (
                    total_pages / len(stats["page_info"]) if stats["page_info"] else 0
                )
                total_size = sum(p["file_size_kb"] for p in stats["page_info"])
                avg_size = (
                    total_size / len(stats["page_info"]) if stats["page_info"] else 0
                )

                f.write(f"  • Tổng trang: {total_pages}\n")
                f.write(f"  • Trung bình trang: {avg_pages:.1f}\n")
                f.write(f"  • Tổng kích thước: {total_size:.1f} KB\n")
                f.write(f"  • Trung bình kích thước: {avg_size:.1f} KB\n")

            if stats["errors"]:
                f.write(f"\nLỖI:\n")
                for error in stats["errors"]:
                    if isinstance(error, dict):
                        f.write(
                            f"  • {error.get('filename', 'Unknown')}: {error.get('error', 'Unknown')}\n"
                        )
                    else:
                        f.write(f"  • {error}\n")

        print(f"✅ Báng cáo tóm tắt lưu tại: {summary_file}")
    except Exception as e:
        print(f"❌ Lỗi khi tạo báng cáo tóm tắt: {e}")

    return stats


def main():
    """Hàm chính"""
    print("\n" + "=" * 80)
    print("🔍 KIỂM TRA DỮ LIỆU - ANALYZE_DATA_BROKER")
    print("=" * 80)

    # Chạy phân tích cho từng dataset
    results = {}
    for dataset_key, dataset_info in DATASETS.items():
        stats = analyze_dataset(dataset_key, dataset_info)
        results[dataset_key] = stats

    # Tạo báng cáo tổng hợp
    print(f"\n>>> [BƯỚC CUỐI] TẠO BÁ NG CÁO TỔNG HỢP")

    summary_file = BASE_DIR / "output_analyze" / "BROKER_ANALYSIS_SUMMARY.txt"
    summary_file.parent.mkdir(parents=True, exist_ok=True)

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(f"{'=' * 80}\n")
        f.write(f"KIỂM TRA DỮ LIỆU - ANALYZE_DATA_BROKER\n")
        f.write(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'=' * 80}\n\n")

        for dataset_key, stats in results.items():
            dataset_info = DATASETS[dataset_key]
            f.write(f"\n{'─' * 80}\n")
            f.write(f"📊 {dataset_key} - {dataset_info['name']}\n")
            f.write(f"{'─' * 80}\n")
            f.write(f"PDF: {stats['files_count']} | Nhãn: {stats['labels_count']}\n")

            if stats["page_info"]:
                has_text = sum(1 for p in stats["page_info"] if not p["is_empty"])
                is_empty = sum(1 for p in stats["page_info"] if p["is_empty"])
                f.write(f"Có text: {has_text} | Rỗng: {is_empty}\n")

            if stats["errors"]:
                f.write(f"Lỗi: {len(stats['errors'])} ⚠️ \n")

    print(f"✅ Báng cáo tổng hợp lưu tại: {summary_file}")

    print(f"\n{'=' * 80}")
    print("✅ HOÀN THÀNH KIỂM TRA DỮ LIỆU")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    main()
