"""
Legacy utils module - For backward compatibility only.

This module maintains backward compatibility with existing code that imports from utils.py.
New code should import from common_lib or lib modules directly for better organization.

DEPRECATED: This module will be removed in a future version.
Please update imports to use:
    - from common_lib import normalize_text, validate_date
    - from lib import get_logger, DATE_RELATED_FIELDS
"""

import warnings
import os
import sys

# Add parent directory to path to import common_lib
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Re-export all commonly used functions from common_lib
from common_lib.date_utils import (
    MONTH_DICT,
    parse_date_dmy,
    validate_date,
    normalize_date_string,
)

from common_lib.text_utils import (
    format_size,
    normalize_whitespace as _normalize_whitespace,
    normalize_text,
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

from common_lib.text_utils import (
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
