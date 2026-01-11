import json
import re
import sys
from pathlib import Path

# Add project root to path to allow importing from lib
sys.path.append(str(Path(__file__).parent.parent))

from lib.label_schema import INVOICE_SCHEMA


def validate_field(value, rules, field_path):
    errors = []

    # Check Required/Null
    if value is None:
        if not rules.get("nullable", False) and rules.get("required", True):
            return [f"{field_path}: Value cannot be null"]
        return []  # Null is allowed

    # Check Type
    expected_type = rules.get("type")
    if expected_type:
        if not isinstance(value, expected_type):
            # Special case: float/int confusion.
            # If expecting float but got int, that's usually fine in Python/JSON.
            # But specific check:
            if isinstance(expected_type, tuple):
                # e.g. (int, float)
                pass
            elif expected_type is float and isinstance(value, int):
                pass  # Allow int for float
            else:
                errors.append(
                    f"{field_path}: Expected type {expected_type}, got {type(value).__name__}"
                )

    # Check Pattern (Regex) for strings
    pattern = rules.get("pattern")
    if pattern and isinstance(value, str):
        if not re.match(pattern, value):
            desc = rules.get("description", f"Must match pattern {pattern}")
            errors.append(f"{field_path}: {desc} (Value: '{value}')")

    return errors


def validate_object(data, schema, path_prefix=""):
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
        if rules.get("type") is list and "item_schema" in rules:
            if isinstance(value, list):
                for idx, item in enumerate(value):
                    item_errors = validate_object(
                        item, rules["item_schema"], f"{field_path}[{idx}]"
                    )
                    errors.extend(item_errors)
            # Type error for list itself is handled by validate_field below

        # Standard field validation
        errors.extend(validate_field(value, rules, field_path))

    return errors


def check_json_schema(directory_path):
    print(f"Validating JSON files in: {directory_path} against schema...")

    valid_count = 0
    invalid_count = 0
    total_files = 0

    report_lines = []

    directory = Path(directory_path)
    if not directory.exists():
        print(f"Directory not found: {directory}")
        return

    for file_path in directory.rglob("*.json"):
        total_files += 1
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            errors = validate_object(data, INVOICE_SCHEMA)

            if errors:
                invalid_count += 1
                report_lines.append(f"File: {file_path.name}")
                for err in errors:
                    report_lines.append(f"  - {err}")
                report_lines.append("")
            else:
                valid_count += 1

        except json.JSONDecodeError:
            invalid_count += 1
            report_lines.append(f"File: {file_path.name}")
            report_lines.append("  - Invalid JSON syntax")
            report_lines.append("")
        except Exception as e:
            invalid_count += 1
            report_lines.append(f"File: {file_path.name}")
            report_lines.append(f"  - Error reading file: {str(e)}")
            report_lines.append("")

    # Summary
    print(f"\nProcessing complete.")
    print(f"Total files: {total_files}")
    print(f"Valid: {valid_count}")
    print(f"Invalid: {invalid_count}")

    if invalid_count > 0:
        report_file = Path("schema_validation_report.txt")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(f"Schema Validation Report\n")
            f.write(
                f"Total: {total_files}, Valid: {valid_count}, Invalid: {invalid_count}\n"
            )
            f.write("=" * 50 + "\n\n")
            f.write("\n".join(report_lines))
        print(f"Detailed report saved to: {report_file.absolute()}")
    else:
        print("All files matched the schema correctly!")


if __name__ == "__main__":
    target_dir = Path(__file__).parent.parent / "datasets" / "data-all" / "labels"

    if not target_dir.exists():
        target_dir = Path(
            r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\analyze_data_invoice\datasets\data-all\labels"
        )

    check_json_schema(target_dir)
