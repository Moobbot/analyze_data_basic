"""
Utility library for Invoice Data Audit Tool.

This package provides commonly used utilities organized by functionality:
- constants: Field types, thresholds, and configuration values
- logger: Centralized logging infrastructure
- date_utils: Date parsing and validation
- file_utils: File operations and directory management
- text_utils: Text processing and formatting
- matchers: Matching algorithms for verification
"""

# Convenience imports for commonly used items
from lib.constants import (
    DATE_RELATED_FIELDS,
    PERCENTAGE_FIELDS,
    NUMERIC_FIELDS,
    FUZZY_MATCH_THRESHOLD,
    NUMERIC_EPSILON,
    MIN_TEXT_LENGTH_FOR_VALID_PDF,
    DEFAULT_ENCODING,
)

from lib.logger import get_logger, set_log_level

from lib.date_utils import (
    MONTH_DICT,
    parse_date_dmy,
    validate_date,
    normalize_date_string,
    get_date_formats,
)

from lib.file_utils import (
    format_size,
    ensure_dir_exists,
    read_file,
    get_files_map,
    get_files_map_recursive,
    list_files_recursive,
    copy_file_and_label,
    move_file_and_label,
    move_file_safe,
    get_json_content_hash,
)

from lib.text_utils import (
    normalize_whitespace,
    normalize_text,
    remove_non_alphanumeric,
    truncate_text,
)

from lib.matchers import (
    get_best_match,
    is_numeric_match,
    match_date_formats,
    find_context_line,
    detect_date_format_from_text,
)

__all__ = [
    # Constants
    "DATE_RELATED_FIELDS",
    "PERCENTAGE_FIELDS",
    "NUMERIC_FIELDS",
    "FUZZY_MATCH_THRESHOLD",
    "NUMERIC_EPSILON",
    "MIN_TEXT_LENGTH_FOR_VALID_PDF",
    "DEFAULT_ENCODING",
    # Logger
    "get_logger",
    "set_log_level",
    # Date utils
    "MONTH_DICT",
    "parse_date_dmy",
    "validate_date",
    "normalize_date_string",
    "get_date_formats",
    # File utils
    "format_size",
    "ensure_dir_exists",
    "read_file",
    "get_files_map",
    "get_files_map_recursive",
    "list_files_recursive",
    "copy_file_and_label",
    "move_file_and_label",
    "move_file_safe",
    "get_json_content_hash",
    # Text utils
    "normalize_whitespace",
    "normalize_text",
    "remove_non_alphanumeric",
    "truncate_text",
    # Matchers
    "get_best_match",
    "is_numeric_match",
    "match_date_formats",
    "find_context_line",
    "detect_date_format_from_text",
]
