"""
Broker-specific utilities.

This module imports shared utilities from common_lib and provides
broker-specific helper functions with config dependencies.

For common utilities, use common_lib directly:
    from common_lib import normalize_text, validate_date, etc.
"""

import os
import sys

# Add parent directory to path to import common_lib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import shared utilities from common_lib
from common_lib.text_utils import (
    format_size,
    normalize_text as _normalize_text_base,
    normalize_whitespace,
    clean_whitespace,
)
from common_lib.date_utils import (
    MONTH_DICT,
    parse_date_dmy,
    validate_date,
    normalize_date_string,
)
from common_lib.file_utils import (
    ensure_dir_exists,
    read_file,
    get_files_map,
    get_files_map_recursive,
    list_files_recursive,
    get_json_content_hash,
    move_file_safe,
)

# Re-export common utilities for backward compatibility
__all__ = [
    # Text utils
    "format_size",
    "normalize_text",
    "normalize_whitespace",
    "clean_whitespace",
    # Date utils
    "MONTH_DICT",
    "parse_date_dmy",
    "validate_date",
    "normalize_date_string",
    # File utils
    "ensure_dir_exists",
    "read_file",
    "get_files_map",
    "get_files_map_recursive",
    "list_files_recursive",
    "get_json_content_hash",
    "move_file_safe",
    # Broker-specific
    "copy_file_and_label",
    "move_file_and_label",
]


def normalize_text(text):
    """
    Broker-specific text normalization (lowercase, remove soft hyphens, collapse whitespace).

    This is a specialized version for broker module that always lowercases.
    For general normalization, use common_lib.text_utils.normalize_text()

    Performs:
    - Removes soft hyphens (\xad) common in PDFs
    - Converts to lowercase
    - Collapses all whitespace (spaces, newlines, tabs) into single spaces
    - Strips leading/trailing whitespace
    """
    if not text:
        return ""

    import re

    # Remove soft hyphens (common in PDFs)
    normalized = text.replace("\xad", "")

    # Convert to lowercase, replace newlines with spaces, collapse multiple spaces, and strip
    normalized = (
        normalized.lower().replace("\n", " ").replace("\r", " ").replace("\t", " ")
    )
    # Collapse multiple spaces into single space
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


# ============================================================================
# BROKER-SPECIFIC FUNCTIONS (with config dependencies)
# ============================================================================


def copy_file_and_label(
    filename,
    dest_folder_files,
    dest_folder_labels,
    source_files_dir=None,
    source_labels_dir=None,
):
    """
    Copy both a file and its corresponding JSON label to destination folders.

    Broker-specific version that uses broker config.

    Args:
        filename: Name of the file (typically PDF)
        dest_folder_files: Destination folder for files
        dest_folder_labels: Destination folder for JSON label files
        source_files_dir: Source directory for files (defaults to config.DATASET_DIR)
        source_labels_dir: Source directory for labels (defaults to config.LABEL_DIR)

    Returns:
        Tuple of (file_copied: bool, label_copied: bool)
    """
    import shutil
    from . import config

    if source_files_dir is None:
        source_files_dir = config.DATASET_DIR
    if source_labels_dir is None:
        source_labels_dir = config.LABEL_DIR

    file_copied = False
    label_copied = False

    # Copy main file
    source_file = os.path.join(source_files_dir, filename)
    dest_file = os.path.join(dest_folder_files, filename)

    # Ensure dest dir exists
    ensure_dir_exists(os.path.dirname(dest_file))

    if os.path.exists(source_file):
        try:
            shutil.copy2(source_file, dest_file)
            file_copied = True
        except Exception as e:
            print(f"  Error copying file {filename}: {e}")

    # Copy corresponding JSON label
    label_filename = os.path.splitext(filename)[0] + ".json"
    source_label = os.path.join(source_labels_dir, label_filename)
    dest_label = os.path.join(dest_folder_labels, label_filename)

    # Ensure dest label dir exists
    ensure_dir_exists(os.path.dirname(dest_label))

    if os.path.exists(source_label):
        try:
            shutil.copy2(source_label, dest_label)
            label_copied = True
        except Exception as e:
            print(f"  Error copying label {label_filename}: {e}")

    return file_copied, label_copied


def move_file_and_label(
    filename,
    dest_folder_files,
    dest_folder_labels,
    source_files_dir=None,
    source_labels_dir=None,
):
    """
    Move both a file and its corresponding JSON label to destination folders.

    Broker-specific version that uses broker config.

    Args:
        filename: Name of the file (typically PDF)
        dest_folder_files: Destination folder for files
        dest_folder_labels: Destination folder for JSON label files
        source_files_dir: Source directory for files (defaults to config.DATASET_DIR)
        source_labels_dir: Source directory for labels (defaults to config.LABEL_DIR)

    Returns:
        Tuple of (file_moved: bool, label_moved: bool)
    """
    import shutil
    from . import config

    if source_files_dir is None:
        source_files_dir = config.DATASET_DIR
    if source_labels_dir is None:
        source_labels_dir = config.LABEL_DIR

    file_moved = False
    label_moved = False

    # Move main file
    source_file = os.path.join(source_files_dir, filename)
    dest_file = os.path.join(dest_folder_files, filename)

    # Ensure dest dir exists
    ensure_dir_exists(os.path.dirname(dest_file))

    if os.path.exists(source_file):
        try:
            shutil.move(source_file, dest_file)
            file_moved = True
        except Exception as e:
            print(f"  Error moving file {filename}: {e}")

    # Move corresponding JSON label
    label_filename = os.path.splitext(filename)[0] + ".json"
    source_label = os.path.join(source_labels_dir, label_filename)
    dest_label = os.path.join(dest_folder_labels, label_filename)

    # Ensure dest label dir exists
    ensure_dir_exists(os.path.dirname(dest_label))

    if os.path.exists(source_label):
        try:
            shutil.move(source_label, dest_label)
            label_moved = True
        except Exception as e:
            print(f"  Error moving label {label_filename}: {e}")

    return file_moved, label_moved
