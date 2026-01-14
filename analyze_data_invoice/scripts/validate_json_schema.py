#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
validate_json_schema.py
Kiểm tra schema của các file JSON invoice
Hỗ trợ xử lý dữ liệu và báng cáo chi tiết
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add project root to path to allow importing from lib
sys.path.append(str(Path(__file__).parent.parent))

from lib.label_schema import INVOICE_SCHEMA


def validate_field(value, rules, field_path):
    """Kiểm tra một trường dữ liệu"""
    errors = []

    # Check Required/Null
    if value is None:
        if not rules.get("nullable", False) and rules.get("required", True):
            return [f"{field_path}: Value cannot be null"]
        return []  # Null is allowed

    # Check Type
    expected_type = rules.get("type")
    if expected_type and not isinstance(value, expected_type):
        # Allow int for float fields
        if expected_type is float and isinstance(value, int):
            return errors
        # Allow tuple of types (e.g. (int, float))
        if isinstance(expected_type, tuple):
            return errors
        errors.append(
            f"{field_path}: Expected type {expected_type.__name__}, got {type(value).__name__}"
        )

    # Check Pattern (Regex) for strings
    pattern = rules.get("pattern")
    if pattern and isinstance(value, str):
        if not re.match(pattern, value):
            desc = rules.get("description", f"Must match pattern {pattern}")
            errors.append(f"{field_path}: {desc} (Value: '{value}')")

    return errors


def validate_object(data, schema, path_prefix=""):
    """Kiểm tra một object JSON (recursive)"""
    errors = []

    for field, rules in schema.items():
        if field == "item_schema":
            continue  # Skip internal meta-field

        field_path = f"{path_prefix}.{field}" if path_prefix else field

        # Check existence
        if field not in data:
            if rules.get("required", True):
                errors.append(f"{field_path}: Missing required field")
            continue

        value = data[field]

        # Recursive check for list of objects
        if (
            rules.get("type") is list
            and "item_schema" in rules
            and isinstance(value, list)
        ):
            for idx, item in enumerate(value):
                item_errors = validate_object(
                    item, rules["item_schema"], f"{field_path}[{idx}]"
                )
                errors.extend(item_errors)

        # Standard field validation
        errors.extend(validate_field(value, rules, field_path))

    return errors


def validate_json_schema(directory_path, dataset_name=""):
    """Kiểm tra schema cho tất cả JSON files trong thư mục"""

    print("=" * 80)
    print(f"📋 KIỂM TRA SCHEMA JSON - {dataset_name}")
    print("=" * 80)
    print(f"Thư mục: {directory_path}\n")

    valid_count = 0
    invalid_count = 0
    total_files = 0
    errors_by_type = defaultdict(int)
    invalid_files = []

    report_lines = []

    directory = Path(directory_path)
    if not directory.exists():
        print(f"❌ Thư mục không tồn tại: {directory}")
        return {"total": 0, "valid": 0, "invalid": 0, "errors": {}}

    json_files = list(directory.rglob("*.json"))
    print(f"✅ Tìm thấy {len(json_files)} file JSON\n")

    for i, file_path in enumerate(json_files, 1):
        total_files += 1
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            errors = validate_object(data, INVOICE_SCHEMA)

            if errors:
                invalid_count += 1
                invalid_files.append(file_path.name)
                report_lines.append(f"❌ {file_path.name}")
                for err in errors:
                    report_lines.append(f"   • {err}")
                    # Phân loại lỗi
                    if "Missing required field" in err:
                        errors_by_type["Missing field"] += 1
                    elif "Expected type" in err:
                        errors_by_type["Type mismatch"] += 1
                    elif "Must match pattern" in err:
                        errors_by_type["Pattern mismatch"] += 1
                    else:
                        errors_by_type["Other"] += 1
            else:
                valid_count += 1

        except json.JSONDecodeError as e:
            invalid_count += 1
            invalid_files.append(file_path.name)
            errors_by_type["JSON syntax error"] += 1
            report_lines.append(f"❌ {file_path.name}")
            report_lines.append(f"   • JSON Syntax Error: {str(e)}")

        except Exception as e:
            invalid_count += 1
            invalid_files.append(file_path.name)
            errors_by_type["File read error"] += 1
            report_lines.append(f"❌ {file_path.name}")
            report_lines.append(f"   • Error: {str(e)}")

        if i % 100 == 0:
            print(f"   ✓ Kiểm tra {i}/{len(json_files)} files")

    # Summary
    print(f"\n{'=' * 80}")
    print("📊 KẾT QUẢ")
    print(f"{'=' * 80}\n")

    print(f"✅ Tổng file: {total_files}")
    print(f"✅ File hợp lệ: {valid_count} ({100*valid_count/total_files:.1f}%)")
    print(
        f"❌ File không hợp lệ: {invalid_count} ({100*invalid_count/total_files:.1f}%)"
    )

    if errors_by_type:
        print(f"\n📋 Phân loại lỗi:")
        for error_type, count in sorted(
            errors_by_type.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"   • {error_type}: {count}")

    # Save report
    output_dir = directory.parent.parent / "output_analyze" / directory.parent.name
    output_dir.mkdir(parents=True, exist_ok=True)

    report_file = output_dir / "schema_validation_report.txt"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write(f"KIỂM TRA SCHEMA JSON - {dataset_name}\n")
        f.write(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")

        f.write("TÓM TẮT\n")
        f.write("─" * 80 + "\n")
        f.write(f"Tổng file: {total_files}\n")
        f.write(f"File hợp lệ: {valid_count} ({100*valid_count/total_files:.1f}%)\n")
        f.write(
            f"File không hợp lệ: {invalid_count} ({100*invalid_count/total_files:.1f}%)\n\n"
        )

        if errors_by_type:
            f.write("PHÂN LOẠI LỖI\n")
            f.write("─" * 80 + "\n")
            for error_type, count in sorted(
                errors_by_type.items(), key=lambda x: x[1], reverse=True
            ):
                f.write(f"{error_type}: {count}\n")
            f.write("\n")

        if invalid_count > 0:
            f.write("CHI TIẾT CÁC FILE LỖI\n")
            f.write("─" * 80 + "\n")
            f.write("\n".join(report_lines))
        else:
            f.write("✅ TẤT CẢ FILE ĐỀU HỢP LỆ!")

    print(f"\n✅ Báng cáo lưu tại: {report_file}")

    if invalid_count == 0:
        print(f"✅ TẤT CẢ FILE KIỂM TRA BÌNH THƯỜNG!")
    else:
        print(f"\n⚠️  Có {invalid_count} file cần sửa")
        print(f"   Chi tiết xem trong báng cáo: {report_file.name}")

    return {
        "total": total_files,
        "valid": valid_count,
        "invalid": invalid_count,
        "errors": dict(errors_by_type),
        "invalid_files": invalid_files,
        "report_file": str(report_file),
    }


def main():
    """Hàm chính"""
    # Target data-muti-page
    target_dir = Path(__file__).parent.parent / "datasets" / "data-muti-page" / "labels"

    if not target_dir.exists():
        target_dir = Path(
            r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\analyze_data_invoice\datasets\data-muti-page\labels"
        )

    validate_json_schema(target_dir, "DATA-MUTI-PAGE")


if __name__ == "__main__":
    main()
