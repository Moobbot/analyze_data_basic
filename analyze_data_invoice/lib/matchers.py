"""
Matching algorithms for label verification.

Provides various matching strategies for comparing label values
with extracted text content, including exact, fuzzy, date, and numeric matching.
"""

import re
import math
import difflib
from datetime import datetime
from typing import Tuple, Optional

from lib.constants import DATE_RELATED_FIELDS, PERCENTAGE_FIELDS, FUZZY_MATCH_THRESHOLD


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text by replacing multiple spaces/newlines with single space.

    Args:
        text: Text to normalize

    Returns:
        Normalized text
    """
    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_context_line(
    value: str, text_content: str, case_insensitive: bool = False
) -> str:
    """
    Find the line containing the value in text content.

    Args:
        value: Value to search for
        text_content: Text content to search in
        case_insensitive: Whether to perform case-insensitive search

    Returns:
        The line containing the value, or empty string if not found
    """
    if not value or not text_content:
        return ""

    lines = text_content.splitlines()
    val_check = value.lower() if case_insensitive else value

    for line in lines:
        line_check = line.lower() if case_insensitive else line
        if val_check in line_check:
            return line.strip()

    return ""


def detect_date_format_from_text(text_content: str) -> str:
    """
    Detect whether dates in text are in DD/MM or MM/DD format.

    Args:
        text_content: Text to analyze

    Returns:
        "DD/MM", "MM/DD", or "UNKNOWN"
    """
    date_pattern = r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b"
    matches = re.findall(date_pattern, text_content)

    for first, second, year in matches:
        first_num = int(first)
        second_num = int(second)
        if first_num > 12:
            return "DD/MM"
        if second_num > 12:
            return "MM/DD"

    return "UNKNOWN"


def is_numeric_match(value_str: str, text_content: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a numeric value exists in text with various number formats.

    Handles:
    - Comma separators (1,234.56)
    - Accounting format negatives ((123))
    - Unicode minus signs

    Args:
        value_str: Numeric value to find
        text_content: Text to search in

    Returns:
        Tuple of (is_match: bool, matched_format: str or None)
    """
    try:
        target_val = float(value_str)
    except (ValueError, TypeError):
        return False, None

    # Normalize various dash/minus characters
    normalized_text = (
        text_content.replace("\u2212", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u00ad", "-")
    )

    # Pattern to match numbers with optional accounting format
    pattern = r"\(?\s*-?\s*[\d,]+(?:\.\d+)?\s*\)?"

    for match in re.finditer(pattern, normalized_text):
        original_text = match.group(0)
        is_accounting_negative = False
        clean_text = original_text.strip()

        # Check for accounting format: (123) means -123
        if clean_text.startswith("(") and clean_text.endswith(")"):
            is_accounting_negative = True
            clean_text = clean_text[1:-1]

        # Remove commas and spaces
        clean_text = clean_text.replace(",", "").replace(" ", "")

        if not any(c.isdigit() for c in clean_text):
            continue

        try:
            candidate_val = float(clean_text)
            if is_accounting_negative:
                candidate_val = -candidate_val

            # Compare with very small tolerance
            if math.isclose(target_val, candidate_val, rel_tol=1e-9, abs_tol=1e-9):
                return True, original_text
        except ValueError:
            continue

    return False, None


def match_date_formats(
    parsed_date: datetime, text_content: str, text_lower: str, date_format: str
) -> Optional[Tuple[str, float, str, str]]:
    """
    Match a date against text content in various date-time formats.

    Args:
        parsed_date: Parsed datetime object
        text_content: Text content to search in
        text_lower: Lowercased version of text_content
        date_format: Original date format string

    Returns:
        Tuple of (status, confidence_score, matched_text, date_format) or None
    """
    # Remove soft hyphens
    text_lower = text_lower.replace("\xad", "-")

    # Standard Python date formats
    alternate_formats = [
        parsed_date.strftime("%d %b %Y"),
        parsed_date.strftime("%d %B %Y"),
        parsed_date.strftime("%d/%m/%Y"),
        parsed_date.strftime("%Y-%m-%d"),
        parsed_date.strftime("%Y/%m/%d"),
        parsed_date.strftime("%d-%m-%Y"),
        parsed_date.strftime("%m/%d/%Y"),
        parsed_date.strftime("%B %d, %Y"),
        parsed_date.strftime("%d %b, %Y"),
        parsed_date.strftime("%d-%b-%Y"),
        parsed_date.strftime("%d-%b-%y"),
        parsed_date.strftime("%d-%B %Y"),
        parsed_date.strftime("%d-%B %y"),
        parsed_date.strftime("%d-%B-%Y"),
        parsed_date.strftime("%d-%B-%y"),
        parsed_date.strftime("%d/%m/%y"),
        parsed_date.strftime("%m/%d/%y"),
    ]

    for alt_format in alternate_formats:
        if alt_format.lower() in text_lower:
            return "FOUND_DATE_ALT_FORMAT", 0.95, alt_format, date_format

    # Custom formats without leading zeros
    day_no_zero = str(parsed_date.day)
    month_no_zero = str(parsed_date.month)
    year_2digit = str(parsed_date.year)[2:]
    detected_format = detect_date_format_from_text(text_content)

    additional_formats = [
        f"{day_no_zero} {parsed_date.strftime('%b')} {parsed_date.year}",
        f"{day_no_zero}-{parsed_date.strftime('%b')} {parsed_date.year}",
        f"{day_no_zero}/{month_no_zero}/{parsed_date.year}",
        f"{month_no_zero}/{day_no_zero}/{parsed_date.year}",
        f"{parsed_date.year}/{month_no_zero}/{day_no_zero}",
        f"{day_no_zero}-{month_no_zero}-{parsed_date.year}",
        f"{month_no_zero}-{day_no_zero}-{parsed_date.year}",
        f"{day_no_zero}-{parsed_date.strftime('%b')}-{parsed_date.year}",
        f"{parsed_date.strftime('%b')} {day_no_zero}, {parsed_date.year}",
        f"{parsed_date.strftime('%B')} {day_no_zero}, {parsed_date.year}",
        parsed_date.strftime("%d.%m.%Y"),
        parsed_date.strftime("%d.%m.%y"),
        f"{day_no_zero}.{month_no_zero}.{parsed_date.year}",
        f"{day_no_zero}.{month_no_zero}.{year_2digit}",
        parsed_date.strftime("%Y.%m.%d"),
        f"{parsed_date.year}.{month_no_zero}.{day_no_zero}",
    ]

    # Helper function for ordinal suffixes
    def get_ordinal_suffix(day: int) -> str:
        if 11 <= day <= 13:
            return "th"
        last_digit = day % 10
        return {1: "st", 2: "nd", 3: "rd"}.get(last_digit, "th")

    suffix = get_ordinal_suffix(parsed_date.day)

    # Add ordinal formats
    additional_formats.extend(
        [
            f"{parsed_date.strftime('%B')}{parsed_date.day}{suffix}, {parsed_date.year}",
            f"{parsed_date.strftime('%B')} {parsed_date.day}{suffix}, {parsed_date.year}",
            f"{parsed_date.day}{suffix} {parsed_date.strftime('%b')} {parsed_date.year}",
            f"{parsed_date.day}{suffix} {parsed_date.strftime('%B')} {parsed_date.year}",
            f"{parsed_date.strftime('%b')} {parsed_date.day}{suffix},{parsed_date.year}",
            f"{parsed_date.strftime('%B')} {parsed_date.day}{suffix},{parsed_date.year}",
        ]
    )

    # Compact formats
    additional_formats.append(parsed_date.strftime("%d%b%Y"))
    additional_formats.append(parsed_date.strftime("%d%B%Y"))

    # 2-digit year formats based on detected format
    if detected_format == "DD/MM":
        additional_formats.append(f"{day_no_zero}/{month_no_zero}/{year_2digit}")
    elif detected_format == "MM/DD":
        additional_formats.append(f"{month_no_zero}/{day_no_zero}/{year_2digit}")
    else:
        additional_formats.append(f"{day_no_zero}/{month_no_zero}/{year_2digit}")
        additional_formats.append(f"{month_no_zero}/{day_no_zero}/{year_2digit}")

    for alt_format in additional_formats:
        if alt_format.lower() in text_lower:
            return "FOUND_DATE_ALT_FORMAT", 0.95, alt_format, date_format

    if detected_format == "UNKNOWN":
        return (
            "CHECK_DATE",
            0,
            "Date format ambiguous - needs manual verification",
            date_format,
        )

    return None


def get_best_match(
    value: any, text_content: str, field_name: str = ""
) -> Tuple[str, float, str, str, str]:
    """
    Find the best match for a value in text content using multiple strategies.

    Matching strategies (in order):
    1. Exact match (case-sensitive)
    2. Case-insensitive match
    3. Normalized whitespace/dash match
    4. Date-specific matching (if applicable)
    5. Numeric matching (if applicable)
    6. Fuzzy matching

    Args:
        value: Value to find
        text_content: Text content to search in
        field_name: Name of the field (for specialized matching)

    Returns:
        Tuple of (status, confidence_score, matched_text, date_format, context_line)
    """
    # Import here to avoid circular dependency
    from common_lib import date_utils

    if value is None or (isinstance(value, str) and value.strip() == ""):
        return "N/A", 0, "", "", ""

    val_str = str(value).strip()

    # Special handling for currency aliases
    if "currency" in field_name.lower() and val_str == "USD":
        if "US$" in text_content:
            context = find_context_line("US$", text_content)
            return "FOUND_ALIAS", 1.0, "US$", "", context

    # Validate if value is a date
    is_date_valid, parsed_date, date_format = date_utils.validate_date(val_str)

    # 1. Exact Match Check
    if val_str in text_content:
        # Check for whole word match
        val_pattern = re.escape(val_str)
        whole_word_pattern = f"(?<![a-zA-Z0-9]){val_pattern}(?![a-zA-Z0-9])"

        if re.search(whole_word_pattern, text_content):
            context = find_context_line(val_str, text_content)
            return "FOUND", 1.0, val_str, date_format if is_date_valid else "", context
        else:
            # Found but not as whole word (substring)
            context = find_context_line(val_str, text_content)
            return (
                "FOUND_SUBSTRING",
                0.95,
                val_str,
                date_format if is_date_valid else "",
                context,
            )

    text_lower = text_content.lower()
    val_lower = val_str.lower()

    # 2. Case Insensitive Match
    if val_lower in text_lower:
        context = find_context_line(val_str, text_content, True)
        return (
            "FOUND_CASE_INSENSITIVE",
            0.9,
            val_str,
            date_format if is_date_valid else "",
            context,
        )

    # 2.2 Dash Normalization
    val_norm_dash = val_str.replace("–", "-").replace("—", "-").replace("\xad", "-")
    text_norm_dash = (
        text_content.replace("–", "-").replace("—", "-").replace("\xad", "-")
    )
    if val_norm_dash.lower() in text_norm_dash.lower():
        return "FOUND", 1.0, val_norm_dash, "", ""

    # 2.5 Normalized Whitespace
    val_norm = normalize_whitespace(val_str)
    text_norm = normalize_whitespace(text_content)
    if val_norm in text_norm:
        return (
            "FOUND_NORMALIZED",
            1.0,
            val_str,
            date_format if is_date_valid else "",
            "",
        )

    # 2.6 Normalized + Dash + Case
    val_clean = val_norm.replace("–", "-").replace("—", "-").replace("\xad", "-")
    text_clean = text_norm.replace("–", "-").replace("—", "-").replace("\xad", "-")
    if val_clean.lower() in text_clean.lower():
        return (
            "FOUND_NORMALIZED_FUZZY",
            0.95,
            val_str,
            date_format if is_date_valid else "",
            "",
        )

    # 3. Date Specific Matching
    if is_date_valid and field_name.lower() in DATE_RELATED_FIELDS:
        result = match_date_formats(parsed_date, text_content, text_lower, date_format)
        if result:
            status, score, match_text, fmt = result
            context = ""
            if status != "CHECK_DATE":
                context = find_context_line(match_text, text_content, True)
            return status, score, match_text, fmt, context

    # 3.5 Numeric Matching
    is_match, matched_format = is_numeric_match(val_str, text_content)
    if is_match:
        context = find_context_line(matched_format, text_content)
        return "FOUND_NUMERIC_FORMAT", 1.0, matched_format, "", context

    # 4. Fuzzy Matching
    lines = [line.strip() for line in text_content.splitlines() if line.strip()]
    best_ratio = 0.0
    best_line = ""

    for line in lines:
        ratio = difflib.SequenceMatcher(None, val_lower, line.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_line = line

    if best_ratio >= FUZZY_MATCH_THRESHOLD:
        return (
            "SIMILAR",
            best_ratio,
            best_line,
            date_format if is_date_valid else "",
            best_line,
        )

    return "MISSING", best_ratio, best_line, date_format if is_date_valid else "", ""
