import json
import logging
from pathlib import Path
import config
import utils

# Setup Logger
logger = logging.getLogger("json_cleaner")
logger.setLevel(logging.INFO)
# Prevent duplicate handlers if module is reloaded
if not logger.handlers:
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(
        config.REVIEW_DIR / "json_validation_log.txt", encoding="utf-8", mode="w"
    )
    formatter = logging.Formatter("%(message)s")
    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

# Define validations
SCHEMA = {
    "Date": ("DATE", False),
    "Customer": ("STRING", False),
    "Supplier": ("STRING", False),
    "Currency": ("STRING", False),
    "text": ("STRING", False),
    "Amount (before tax)": ("FLOAT", True),
    "Tax amount": ("FLOAT", True),
    "Amount (after GST)": ("FLOAT", True),
    "Amount in SGD": ("FLOAT", True),
    "Tax amount in SGD": ("FLOAT", True),
    "Amount after tax in SGD": ("FLOAT", True),
    "Ex rate": ("FLOAT", True),
    "Ex rate to SGD": ("FLOAT", True),
}


def validate_and_clean_value(key, value, expected_type, auto_convert):
    if value is None:
        return True, value, False

    if expected_type == "DATE":
        if not isinstance(value, str):
            return False, value, False
        is_valid, _, _ = utils.validate_date(value)
        return is_valid, value, False

    elif expected_type == "STRING":
        if isinstance(value, str):
            return True, value, False
        return False, value, False

    elif expected_type == "FLOAT":
        if isinstance(value, (int, float)):
            return True, value, False

        if auto_convert and isinstance(value, str):
            clean_str = value.replace(",", "")
            try:
                new_val = float(clean_str)
                return True, new_val, True
            except ValueError:
                pass
        return False, value, False

    return True, value, False


def process_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.info(f"[ERROR] Reading {file_path}: {e}")
        return False

    modified = False
    errors = []

    if isinstance(data, dict):
        items_to_check = [data]
    elif isinstance(data, list):
        items_to_check = data
    else:
        items_to_check = []

    for item in items_to_check:
        if not isinstance(item, dict):
            continue

        for key, (expected_type, auto_convert) in SCHEMA.items():
            if key in item:
                val = item[key]
                is_valid, new_val, was_modified = validate_and_clean_value(
                    key, val, expected_type, auto_convert
                )

                if was_modified:
                    item[key] = new_val
                    modified = True

                if not is_valid:
                    errors.append(
                        f"  - Key '{key}' has invalid value: {repr(val)} (Expected {expected_type})"
                    )

    if errors:
        logger.info(f"[WARNING] Issues in {file_path}:")
        for err in errors:
            logger.info(err)

    if modified:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"[INFO] Fixed/Updated {file_path}")
            return True
        except Exception as e:
            logger.info(f"[ERROR] Writing {file_path}: {e}")
            return False

    return False


def clean_json_files():
    target_dir = config.LABEL_DIR

    if not target_dir.exists():
        logger.info(f"Directory not found: {target_dir}")
        return

    logger.info(f"Scanning directory: {target_dir}")

    count = 0
    updated_count = 0

    files = list(target_dir.rglob("*.json"))
    logger.info(f"Found {len(files)} JSON files.")

    for file_path in files:
        if process_file(file_path):
            updated_count += 1
        count += 1

    logger.info(f"Finished. Processed {count} files. Updated {updated_count} files.")
    logger.info(f"Log saved to json_validation_log.txt")


if __name__ == "__main__":
    clean_json_files()
