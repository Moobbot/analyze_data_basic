"""
Legacy utils module - For backward compatibility only.

This module maintains backward compatibility with existing code that imports from utils.py.
New code should import from lib.* modules directly for better organization and clarity.

DEPRECATED: This module will be removed in a future version.
Please update imports to use lib.* modules directly:
    - from lib.date_utils import parse_date_dmy, validate_date
    - from lib.file_utils import get_files_map, ensure_dir_exists
    - from lib.text_utils import format_size, normalize_whitespace
"""

import warnings

# Re-export all commonly used functions from lib modules
from lib.date_utils import (
    MONTH_DICT,
    parse_date_dmy,
    validate_date,
    normalize_date_string,
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
    normalize_whitespace as _normalize_whitespace,
    normalize_text,
)

# For backward compatibility, keep normalize_whitespace signature
normalize_whitespace = _normalize_whitespace

# Issue deprecation warning (commented out for now to avoid spamming during migration)
# warnings.warn(
#     "utils.py is deprecated. Please import from lib.* modules instead.",
#     DeprecationWarning,
#     stacklevel=2
# )

__all__ = [
    # Date utils
    "MONTH_DICT",
    "parse_date_dmy",
    "validate_date",
    "normalize_date_string",
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
]
