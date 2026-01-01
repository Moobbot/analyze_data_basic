import json
import os
from pathlib import Path
import config
import utils
import logging

# Setup Logger
LOG_FILE = "json_validation_log.txt"

# Create a custom logger
logger = logging.getLogger("json_cleaner")
logger.setLevel(logging.INFO)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(LOG_FILE, encoding="utf-8", mode="w")

# Create formatters and add it to handlers
formatter = logging.Formatter("%(message)s")
c_handler.setFormatter(formatter)
f_handler.setFormatter(formatter)

# Add handlers to the logger
if not logger.handlers:
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)


# Define validations
# KEY: (Expected Type, Auto-Convert?)
# Types: "DATE", "STRING", "FLOAT"
SCHEMA = {
    # Date validation
    "Date": ("DATE", False),
    # String validation
    "Customer": ("STRING", False),
    "Supplier": ("STRING", False),
    "Currency": ("STRING", False),
    "text": ("STRING", False),
    # Numeric cleaning (Float conversion)
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
    """
    Validates and optionally cleans a value based on type.
    Returns: (is_valid, new_value, modified)
    """
    if value is None:
        # Decide if None is allowed. For now, let's assume valid but no change.
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
            # Remove commas and try convert
            clean_str = value.replace(",", "")
            try:
                new_val = float(clean_str)
                return True, new_val, True
            except ValueError:
                pass

        # If we reach here, it's not a valid float or conversion failed
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

    # Handle both Dict and List of Dicts (just in case, though usually invoice is Dict)
    # The previous code assumed data is Dict. User snippet shows "text" is at top level?
    # User said "Date", "Customer", etc.

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


def main():
    target_dir = Path(config.LABEL_DIR)

    if not target_dir.exists():
        logger.info(f"Directory not found: {target_dir}")
        return

    logger.info(f"Scanning directory: {target_dir}")

    count = 0
    updated_count = 0

    # Recursively find all json files
    files = list(target_dir.rglob("*.json"))
    logger.info(f"Found {len(files)} JSON files.")

    for file_path in files:
        if process_file(file_path):
            updated_count += 1
        count += 1

    logger.info(f"Finished. Processed {count} files. Updated {updated_count} files.")
    logger.info(f"Log saved to {LOG_FILE}")


if __name__ == "__main__":
    main()
