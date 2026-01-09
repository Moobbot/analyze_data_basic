"""
Common Library - Shared utilities for all analyze_data modules.

This library provides reusable utilities for:
- Text processing and normalization
- File and directory operations
- Date parsing and validation
- PDF text extraction

Usage:
    from common_lib import normalize_text, validate_date, extract_text_from_pdf
    from common_lib.text_utils import normalize_whitespace
    from common_lib.date_utils import parse_date_dmy
"""

# Text utilities
from .text_utils import (
    format_size,
    normalize_whitespace,
    normalize_text,
    remove_non_alphanumeric,
    truncate_text,
    clean_whitespace,
)

# File utilities
from .file_utils import (
    ensure_dir_exists,
    read_file,
    get_files_map,
    get_files_map_recursive,
    list_files_recursive,
    get_json_content_hash,
    copy_file_and_label,
    move_file_and_label,
    move_file_safe,
)

# Date utilities
from .date_utils import (
    MONTH_DICT,
    normalize_date_string,
    parse_date_dmy,
    validate_date,
    get_date_formats,
)

# PDF utilities
from .pdf_utils import (
    extract_text_from_pdf,
    extract_and_save_to_txt,
    is_text_based_pdf,
)

__all__ = [
    # Text utils
    "format_size",
    "normalize_whitespace",
    "normalize_text",
    "remove_non_alphanumeric",
    "truncate_text",
    "clean_whitespace",
    # File utils
    "ensure_dir_exists",
    "read_file",
    "get_files_map",
    "get_files_map_recursive",
    "list_files_recursive",
    "get_json_content_hash",
    "copy_file_and_label",
    "move_file_and_label",
    "move_file_safe",
    # Date utils
    "MONTH_DICT",
    "normalize_date_string",
    "parse_date_dmy",
    "validate_date",
    "get_date_formats",
    # PDF utils
    "extract_text_from_pdf",
    "extract_and_save_to_txt",
    "is_text_based_pdf",
]
