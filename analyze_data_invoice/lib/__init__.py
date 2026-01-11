"""
Utility library for Invoice Data Audit Tool.

This package combines common utilities from common_lib with invoice-specific modules:
- Common utilities (from common_lib): text, file, date processing, PDF extraction
- Invoice-specific: constants, logger, matchers

Usage:
    from lib import normalize_text, validate_date  # From common_lib
    from lib import get_logger, DATE_RELATED_FIELDS  # Invoice-specific
"""

import os
import sys

# Add parent directory to path to import common_lib
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    # Import from common_lib
    from common_lib.date_utils import (
        MONTH_DICT,
        parse_date_dmy,
        validate_date,
        normalize_date_string,
        get_date_formats,
    )

    from common_lib.text_utils import (
        format_size,
        normalize_whitespace,
        normalize_text,
        remove_non_alphanumeric,
        truncate_text,
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

    from common_lib.pdf_utils import (
        extract_text_from_pdf,
        extract_and_save_to_txt,
        is_text_based_pdf,
    )
except ImportError:
    # Allow running without common_lib (e.g. for standalone scripts that don't need it)
    pass

# Import invoice-specific modules (use relative imports)
from .constants import (
    DATE_RELATED_FIELDS,
    PERCENTAGE_FIELDS,
    NUMERIC_FIELDS,
    FUZZY_MATCH_THRESHOLD,
    NUMERIC_EPSILON,
    MIN_TEXT_LENGTH_FOR_VALID_PDF,
    DEFAULT_ENCODING,
)

from .logger import get_logger, set_log_level

# Import invoice-specific matchers (use relative import)
from .matchers import (
    get_best_match,
    is_numeric_match,
    match_date_formats,
    find_context_line,
    detect_date_format_from_text,
)

__all__ = [
    # Constants (invoice-specific)
    "DATE_RELATED_FIELDS",
    "PERCENTAGE_FIELDS",
    "NUMERIC_FIELDS",
    "FUZZY_MATCH_THRESHOLD",
    "NUMERIC_EPSILON",
    "MIN_TEXT_LENGTH_FOR_VALID_PDF",
    "DEFAULT_ENCODING",
    # Logger (invoice-specific)
    "get_logger",
    "set_log_level",
    # Date utils (from common_lib)
    "MONTH_DICT",
    "parse_date_dmy",
    "validate_date",
    "normalize_date_string",
    "get_date_formats",
    # File utils (from common_lib)
    "format_size",
    "ensure_dir_exists",
    "read_file",
    "get_files_map",
    "get_files_map_recursive",
    "list_files_recursive",
    "get_json_content_hash",
    "move_file_safe",
    # Text utils (from common_lib)
    "normalize_whitespace",
    "normalize_text",
    "remove_non_alphanumeric",
    "truncate_text",
    # PDF utils (from common_lib)
    "extract_text_from_pdf",
    "extract_and_save_to_txt",
    "is_text_based_pdf",
    # Matchers (invoice-specific)
    "get_best_match",
    "is_numeric_match",
    "match_date_formats",
    "find_context_line",
    "detect_date_format_from_text",
]
