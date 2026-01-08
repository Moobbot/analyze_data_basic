"""
Constants and configuration values for Invoice Data Audit Tool.

This module centralizes all magic numbers, field type definitions,
and threshold values used throughout the codebase.
"""

from typing import List

# Field Type Constants
# Fields that should use date-specific matching logic
DATE_RELATED_FIELDS: List[str] = [
    "date",
    "invoice date",
    "due date",
    "payment date",
    "contract date",
]

# Fields that should use percentage normalization
PERCENTAGE_FIELDS: List[str] = [
    "tax type",
    "tax rate",
    "gst",
    "vat",
    "gst rate",
]

# Fields that should use numeric matching
NUMERIC_FIELDS: List[str] = [
    "amount",
    "total",
    "subtotal",
    "price",
    "quantity",
    "unit price",
]

# Matching Thresholds
FUZZY_MATCH_THRESHOLD: float = 0.8  # Similarity threshold for fuzzy matching
NUMERIC_EPSILON: float = 0.01  # Tolerance for numeric comparisons

# PDF Extraction Constants
MIN_TEXT_LENGTH_FOR_VALID_PDF: int = 50  # Minimum characters for text-based PDF

# Encoding
DEFAULT_ENCODING: str = "utf-8"

# Batch Processing
DEFAULT_BATCH_SIZE: int = 100  # Files to process before progress update

# File Extensions
PDF_EXTENSION: str = ".pdf"
JSON_EXTENSION: str = ".json"
TXT_EXTENSION: str = ".txt"
DOCX_EXTENSION: str = ".docx"
