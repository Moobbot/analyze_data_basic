#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scan_currency_format.py
Quét và kiểm tra định dạng tiền tệ trong các file JSON
"""

import json
from pathlib import Path
from datetime import datetime

# Config
# Config
SCRIPT_DIR = Path(__file__).parent.resolve()
BASE_DIR = SCRIPT_DIR.parent
LABELS_DIR = BASE_DIR / "datasets" / "data-muti-page" / "labels"

# Các cột tiền tệ cần kiểm tra
CURRENCY_FIELDS = [
    "Amount (before tax)",
    "Amount (after GST)",
    "Amount in SGD",
    "Amount after tax in SGD",
    "Tax amount",
    "Tax amount in SGD",
]


def check_amount_format(value):
    """Kiểm tra định dạng của một giá trị tiền tệ"""
    if value is None:
        return {"type": "null", "value": value, "status": "ok"}

    if isinstance(value, (int, float)):
        return {"type": "number", "value": value, "status": "ok"}

    if isinstance(value, str):
        # Kiểm tra string có chứa dấu phẩy hay không
        if "," in value:
            return {"type": "string_with_comma", "value": value, "status": "warning"}
        try:
            float(value)
            return {"type": "string_number", "value": value, "status": "ok"}
        except ValueError:
            return {"type": "string_invalid", "value": value, "status": "error"}

    return {"type": "unknown", "value": value, "status": "error"}


def scan_json_file(file_path):
    """Quét một file JSON"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        issues = []
        stats = {"total_amounts": 0, "warnings": 0, "errors": 0}

        # Kiểm tra Description array
        if not isinstance(data, dict) or "Description" not in data:
            return {
                "file": str(file_path.name),
                "status": "ok",
                "stats": stats,
                "issues": issues,
            }

        descriptions = data["Description"]
        if not isinstance(descriptions, list):
            return {
                "file": str(file_path.name),
                "status": "ok",
                "stats": stats,
                "issues": issues,
            }

        for idx, item in enumerate(descriptions):
            if not isinstance(item, dict):
                continue
            for field in CURRENCY_FIELDS:
                if field not in item:
                    continue
                stats["total_amounts"] += 1
                result = check_amount_format(item[field])

                if result["status"] == "warning":
                    stats["warnings"] += 1
                    issues.append(
                        {
                            "type": "warning",
                            "description_idx": idx,
                            "field": field,
                            "value": result["value"],
                            "format": result["type"],
                        }
                    )
                elif result["status"] == "error":
                    stats["errors"] += 1
                    issues.append(
                        {
                            "type": "error",
                            "description_idx": idx,
                            "field": field,
                            "value": result["value"],
                            "format": result["type"],
                        }
                    )

        return {
            "file": str(file_path.name),
            "status": "ok" if stats["errors"] == 0 else "error",
            "stats": stats,
            "issues": issues,
        }

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
    print("[SCAN] QUÉT ĐỊNH DẠNG TIỀN TỆ - ANALYZE_DATA_INVOICE")
    print("=" * 80)

    if not LABELS_DIR.exists():
        print(f"[ERROR] Thư mục không tồn tại: {LABELS_DIR}")
        return

    # Tìm tất cả file JSON
    json_files = list(LABELS_DIR.rglob("*.json"))
    print(f"\n[OK] Tìm thấy {len(json_files)} file JSON\n")

    # Quét từng file
    results = []
    warnings_count = 0
    errors_count = 0

    for i, json_file in enumerate(json_files, 1):
        result = scan_json_file(json_file)
        results.append(result)

        if result["status"] == "error" and "stats" in result:
            if result["stats"]["warnings"] > 0:
                warnings_count += result["stats"]["warnings"]
            if result["stats"]["errors"] > 0:
                errors_count += result["stats"]["errors"]

        if i % 100 == 0:
            print(f"   [PROGRESS] Quét {i}/{len(json_files)} files")

    # Tóm tắt
    print(f"\n{'=' * 80}")
    print("[SUMMARY] TÓM TẮT")
    print(f"{'=' * 80}")

    files_with_warnings = [
        r
        for r in results
        if r.get("status") == "ok" and r.get("stats", {}).get("warnings", 0) > 0
    ]
    files_with_errors = [
        r
        for r in results
        if r.get("status") == "ok" and r.get("stats", {}).get("errors", 0) > 0
    ]

    print(f"\n[OK] Tổng file JSON: {len(json_files)}")
    print(
        f"[OK] File bình thường: {len(results) - len(files_with_warnings) - len(files_with_errors)}"
    )
    print(
        f"[WARNING] File có cảnh báo (string với dấu phẩy): {len(files_with_warnings)}"
    )
    print(f"[ERROR] File có lỗi: {len(files_with_errors)}")

    total_warnings = sum(
        r.get("stats", {}).get("warnings", 0) for r in files_with_warnings
    )
    total_errors = sum(r.get("stats", {}).get("errors", 0) for r in files_with_errors)

    print(f"\n   Tổng cảnh báo: {total_warnings}")
    print(f"   Tổng lỗi: {total_errors}")

    # Chi tiết các file có cảnh báo
    if files_with_warnings:
        print(f"\n{'=' * 80}")
        print("[WARNING] CÁC FILE CÓ CẢNH BÁO (String với dấu phẩy)")
        print(f"{'=' * 80}")
        for result in sorted(
            files_with_warnings, key=lambda x: x["stats"]["warnings"], reverse=True
        )[:20]:
            print(f"\n[FILE] {result['file']}")
            print(f"   [WARNING] {result['stats']['warnings']} trường có dấu phẩy")
            for issue in result["issues"][:3]:  # Hiển thị 3 issue đầu tiên
                print(
                    f"      * {issue['field']} (Item {issue['description_idx']}): {issue['value']}"
                )

    # Chi tiết các file có lỗi
    if files_with_errors:
        print(f"\n{'=' * 80}")
        print("[ERROR] CÁC FILE CÓ LỖI")
        print(f"{'=' * 80}")
        for result in sorted(
            files_with_errors, key=lambda x: x["stats"]["errors"], reverse=True
        )[:20]:
            print(f"\n[FILE] {result['file']}")
            print(f"   [ERROR] {result['stats']['errors']} trường có lỗi")
            for issue in result["issues"][:3]:  # Hiển thị 3 issue đầu tiên
                print(
                    f"      * {issue['field']} (Item {issue['description_idx']}): {issue['value']}"
                )

    # Lưu báng cáo
    output_file = (
        BASE_DIR / "output_analyze" / "data-muti-page" / "currency_format_scan.txt"
    )
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("QUÉT ĐỊNH DẠNG TIỀN TỆ - ANALYZE_DATA_INVOICE\n")
        f.write(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")

        f.write("TÓM TẮT\n")
        f.write("─" * 80 + "\n")
        f.write(f"Tổng file JSON: {len(json_files)}\n")
        f.write(
            f"File bình thường: {len(results) - len(files_with_warnings) - len(files_with_errors)}\n"
        )
        f.write(
            f"File có cảnh báo: {len(files_with_warnings)} (tổng {total_warnings} trường)\n"
        )
        f.write(
            f"File có lỗi: {len(files_with_errors)} (tổng {total_errors} trường)\n\n"
        )

        if files_with_warnings:
            f.write("CÁC FILE CÓ CẢNH BÁO\n")
            f.write("─" * 80 + "\n")
            for result in sorted(
                files_with_warnings, key=lambda x: x["stats"]["warnings"], reverse=True
            ):
                f.write(f"\n{result['file']}: {result['stats']['warnings']} cảnh báo\n")
                for issue in result["issues"]:
                    f.write(
                        f"  • Item {issue['description_idx']}, {issue['field']}: {issue['value']}\n"
                    )

        if files_with_errors:
            f.write("\n\nCÁC FILE CÓ LỖI\n")
            f.write("─" * 80 + "\n")
            for result in sorted(
                files_with_errors, key=lambda x: x["stats"]["errors"], reverse=True
            ):
                f.write(f"\n{result['file']}: {result['stats']['errors']} lỗi\n")
                for issue in result["issues"]:
                    f.write(
                        f"  • Item {issue['description_idx']}, {issue['field']}: {issue['value']}\n"
                    )

    print(f"\n[OK] Báng cáo lưu tại: {output_file}")

    # Khuyến nghị
    print(f"\n{'=' * 80}")
    print("[INFO] KHUYẾN NGHỊ")
    print(f"{'=' * 80}")
    if total_warnings > 0:
        print(
            f"\n[WARNING] Phát hiện {total_warnings} trường tiền tệ dạng string với dấu phẩy"
        )
        print("   Cần chạy script FIX để chuyển đổi sang số hoặc string không dấu phẩy")
        print("   Chạy: python fix_currency_format.py")

    if total_errors == 0 and total_warnings == 0:
        print("\n[OK] TẤT CẢ DỮ LIỆU TIỀN TỆ ĐỀU BÌNH THƯỜNG")
        print("   Không cần chạy script sửa")

    print()


if __name__ == "__main__":
    main()
