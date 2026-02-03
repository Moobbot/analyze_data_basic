#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fix_currency_format.py
Sửa định dạng tiền tệ trong các file JSON
Chuyển đổi string với dấu phẩy thành số
"""

import json
from pathlib import Path
from datetime import datetime

# Config
# Config
SCRIPT_DIR = Path(__file__).parent.resolve()
BASE_DIR = SCRIPT_DIR.parent
LABELS_DIR = BASE_DIR / "datasets" / "data-muti-page" / "labels"

# Các cột tiền tệ cần sửa
CURRENCY_FIELDS = [
    "Amount (before tax)",
    "Amount (after GST)",
    "Amount in SGD",
    "Amount after tax in SGD",
    "Tax amount",
    "Tax amount in SGD",
]


def fix_amount_value(value):
    """Sửa giá trị tiền tệ - chuyển string với dấu phẩy thành float"""
    if value is None:
        return value

    if isinstance(value, (int, float)):
        return value

    if isinstance(value, str):
        # Xóa dấu phẩy và chuyển thành float
        try:
            return float(value.replace(",", ""))
        except ValueError:
            # Nếu không thể chuyển đổi, giữ nguyên string
            return value

    return value


def fix_json_file(file_path):
    """Sửa một file JSON"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        fixed_count = 0

        # Determine items to process
        items_to_process = []
        if isinstance(data, list):
            items_to_process = data
        elif isinstance(data, dict):
            items_to_process = [data]
        else:
            return {"file": str(file_path.name), "fixed": 0, "status": "no_change"}

        for doc in items_to_process:
            # Sửa Description array
            if not isinstance(doc, dict) or "Description" not in doc:
                continue

            descriptions = doc["Description"]
            if not isinstance(descriptions, list):
                continue

            for item in descriptions:
                if not isinstance(item, dict):
                    continue
                for field in CURRENCY_FIELDS:
                    if field not in item:
                        continue
                    original = item[field]
                    item[field] = fix_amount_value(item[field])
                    if original != item[field]:
                        fixed_count += 1

        # Lưu file nếu có thay đổi
        if fixed_count > 0:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return {
                "file": str(file_path.name),
                "fixed": fixed_count,
                "status": "success",
            }
        return {"file": str(file_path.name), "fixed": 0, "status": "no_change"}

    except json.JSONDecodeError as e:
        return {
            "file": str(file_path.name),
            "status": "error",
            "error": f"JSON syntax error: {str(e)}",
        }
    except Exception as e:
        return {"file": str(file_path.name), "status": "error", "error": str(e)}


def main():
    """Hàm chính"""
    print("=" * 80)
    print("[FIX] SỬA ĐỊNH DẠNG TIỀN TỆ - ANALYZE_DATA_INVOICE")
    print("=" * 80)

    if not LABELS_DIR.exists():
        print(f"[ERROR] Thư mục không tồn tại: {LABELS_DIR}")
        return

    # Tìm tất cả file JSON
    json_files = list(LABELS_DIR.rglob("*.json"))
    print(f"\n[OK] Tìm thấy {len(json_files)} file JSON\n")

    # Sửa từng file
    results = []
    total_fixed = 0

    for i, json_file in enumerate(json_files, 1):
        result = fix_json_file(json_file)
        results.append(result)

        if result["status"] == "success" and result.get("fixed", 0) > 0:
            total_fixed += result.get("fixed", 0)

        if i % 100 == 0:
            print(f"   [PROGRESS] Xử lý {i}/{len(json_files)} files")

    # Tóm tắt
    print(f"\n{'=' * 80}")
    print("[SUMMARY] TÓM TẮT")
    print(f"{'=' * 80}\n")

    success_count = len(
        [r for r in results if r["status"] == "success" and r.get("fixed", 0) > 0]
    )
    no_change_count = len([r for r in results if r["status"] == "no_change"])
    error_count = len([r for r in results if r["status"] == "error"])

    print(f"[OK] Tổng file: {len(json_files)}")
    print(f"[OK] File được sửa: {success_count}")
    print(f"[OK] File không cần sửa: {no_change_count}")
    print(f"[ERROR] File lỗi: {error_count}")
    print(f"\n[STAT] Tổng trường được sửa: {total_fixed}")

    # Lưu báng cáo
    output_file = (
        BASE_DIR / "output_analyze" / "data-muti-page" / "currency_format_fix.txt"
    )
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("SỬA ĐỊNH DẠNG TIỀN TỆ - ANALYZE_DATA_INVOICE\n")
        f.write(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")

        f.write("TÓM TẮT\n")
        f.write("─" * 80 + "\n")
        f.write(f"Tổng file JSON: {len(json_files)}\n")
        f.write(f"File được sửa: {success_count}\n")
        f.write(f"File không cần sửa: {no_change_count}\n")
        f.write(f"File lỗi: {error_count}\n")
        f.write(f"Tổng trường được sửa: {total_fixed}\n\n")

        # Chi tiết các file được sửa
        fixed_results = [
            r for r in results if r["status"] == "success" and r.get("fixed", 0) > 0
        ]
        if fixed_results:
            f.write("CÁC FILE ĐƯỢC SỬA\n")
            f.write("─" * 80 + "\n")
            for result in sorted(
                fixed_results, key=lambda x: x.get("fixed", 0), reverse=True
            ):
                f.write(f"{result['file']}: {result['fixed']} trường\n")

    print(f"\n[OK] Báng cáo lưu tại: {output_file}")

    # Kết quả
    print(f"\n{'=' * 80}")
    print("[RESULT] KẾT QUẢ")
    print(f"{'=' * 80}")

    if success_count > 0:
        print(f"\n[OK] ĐÃ SỬA THÀNH CÔNG {total_fixed} TRƯỜNG TIỀN TỀ")
        print(f"   * Chuyển đổi string với dấu phẩy thành số (float)")
        print(f"   * Sửa {success_count} file")
        print(f"\n[INFO] Lưu ý: Các giá trị tiền tệ giờ là SỐ (float)")
        print(f"   * Dễ hơn cho so sánh và tính toán")
        print(f"   * Tự động định dạng lại khi cần hiển thị")
    else:
        print(f"\n[OK] TẤT CẢ DỮ LIỆU ĐÃ BÌNH THƯỜNG")

    print()


if __name__ == "__main__":
    main()
