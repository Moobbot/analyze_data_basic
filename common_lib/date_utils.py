"""
Date parsing and validation utilities.

Handles various date formats and provides robust date validation
for invoice data processing.
"""

import re
from datetime import datetime
from typing import Optional, Tuple, Dict, List

# Month dictionary for parsing dates with month names
MONTH_DICT: Dict[str, str] = {
    "Jan": "01",
    "January": "01",
    "Feb": "02",
    "February": "02",
    "Mar": "03",
    "March": "03",
    "Apr": "04",
    "April": "04",
    "May": "05",
    "Jun": "06",
    "June": "06",
    "Jul": "07",
    "July": "07",
    "Aug": "08",
    "August": "08",
    "Sep": "09",
    "Sept": "09",
    "September": "09",
    "Oct": "10",
    "October": "10",
    "Nov": "11",
    "November": "11",
    "Dec": "12",
    "December": "12",
}


def normalize_date_string(date_str: str) -> str:
    """
    Normalize date string by removing soft hyphens and extra whitespace.

    Args:
        date_str: Date string to normalize

    Returns:
        Normalized date string

    Examples:
        >>> normalize_date_string("  03  Oct  2023  ")
        '03 Oct 2023'
    """
    if not date_str:
        return ""

    # Remove soft hyphens (unicode \xad)
    normalized = date_str.replace("\xad", "")

    # Remove extra whitespace
    normalized = " ".join(normalized.split())

    return normalized.strip()


def parse_date_dmy(date_str: str) -> Optional[datetime]:
    """
    Parse date strings in DD Mon YYYY or DD-Mon-YY formats.

    Supports formats:
    - "DD Mon YYYY" (e.g., "03 Oct 2023")
    - "DD-Mon-YY" (e.g., "31-Jul-21")

    Args:
        date_str: String containing date in supported formats

    Returns:
        datetime object or None if parsing fails

    Examples:
        >>> parse_date_dmy("03 Oct 2023")
        datetime.datetime(2023, 10, 3, 0, 0)
        >>> parse_date_dmy("31-Jul-21")
        datetime.datetime(2021, 7, 31, 0, 0)
    """
    if not date_str or not isinstance(date_str, str):
        return None

    # Normalize the string first
    date_str = normalize_date_string(date_str)

    # Pattern 1: "DD Mon YYYY" format (e.g., "03 Oct 2023")
    pattern1 = r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})"
    match = re.search(pattern1, date_str)

    if match:
        day = match.group(1).zfill(2)  # Pad with zero if needed
        month_name = match.group(2)
        year = match.group(3)

        # Look up month number
        month_num = MONTH_DICT.get(month_name) or MONTH_DICT.get(
            month_name.capitalize()
        )

        if month_num:
            try:
                # Create datetime object to validate the date
                date_obj = datetime.strptime(f"{year}-{month_num}-{day}", "%Y-%m-%d")
                return date_obj
            except ValueError:
                pass

    # Pattern 2: "DD-Mon-YY" format (e.g., "31-Jul-21")
    pattern2 = r"(\d{1,2})-([A-Za-z]+)-(\d{2})"
    match = re.search(pattern2, date_str)

    if match:
        day = match.group(1).zfill(2)
        month_name = match.group(2)
        year_2digit = match.group(3)

        # Convert 2-digit year to 4-digit
        year_int = int(year_2digit)
        if 0 <= year_int <= 99:
            # Assume years 00-50 are 2000-2050, 51-99 are 1951-1999
            year = f"{2000 + year_int if year_int <= 50 else 1900 + year_int}"
        else:
            return None

        # Look up month number
        month_num = MONTH_DICT.get(month_name) or MONTH_DICT.get(
            month_name.capitalize()
        )

        if month_num:
            try:
                # Create datetime object to validate the date
                date_obj = datetime.strptime(f"{year}-{month_num}-{day}", "%Y-%m-%d")
                return date_obj
            except ValueError:
                pass

    return None


def validate_date(date_str: str) -> Tuple[bool, Optional[datetime], str]:
    """
    Validate if a date string is in correct format and represents a valid date.

    Supports multiple formats including "DD Mon YYYY", "DD/MM/YYYY", "YYYY-MM-DD", etc.

    Args:
        date_str: String to validate as date

    Returns:
        Tuple of (is_valid: bool, parsed_date: datetime or None, format_used: str)

    Examples:
        >>> valid, date, fmt = validate_date("03 Oct 2023")
        >>> print(f"Valid: {valid}, Format: {fmt}")
        Valid: True, Format: DD Mon YYYY
    """
    if not date_str or not isinstance(date_str, str):
        return (False, None, "")

    date_str = normalize_date_string(date_str)

    # Try parsing "DD Mon YYYY" format first
    parsed = parse_date_dmy(date_str)
    if parsed:
        return (True, parsed, "DD Mon YYYY")

    # Try other common formats
    formats_to_try = [
        ("%d/%m/%Y", "DD/MM/YYYY"),
        ("%Y-%m-%d", "YYYY-MM-DD"),
        ("%d-%m-%Y", "DD-MM-YYYY"),
        ("%m/%d/%Y", "MM/DD/YYYY"),
        # Extended formats
        ("%d %b %Y", "DD Mon YYYY"),  # 03 Oct 2023
        ("%d %B %Y", "DD Month YYYY"),  # 03 October 2023
        ("%Y/%m/%d", "YYYY/MM/DD"),  # 2023/07/07
        ("%B %d, %Y", "Month DD, YYYY"),  # October 03, 2023
        ("%d %b, %Y", "DD Mon, YYYY"),  # 03 Oct, 2023
        ("%d-%b-%Y", "DD-Mon-YYYY"),  # 03-Oct-2023
        ("%d-%b-%y", "DD-Mon-YY"),  # 03-Oct-23
        ("%d-%B %Y", "DD-Month YYYY"),  # 30-April 2023
        ("%d-%B %y", "DD-Month YY"),  # 30-April 23
        ("%d-%B-%Y", "DD-Month-YYYY"),  # 30-April-2023
        ("%d-%B-%y", "DD-Month-YY"),  # 30-April-23
        ("%d/%m/%y", "DD/MM/YY"),  # 30/05/25
        ("%m/%d/%y", "MM/DD/YY"),  # 05/30/25
        ("%d.%m.%Y", "DD.MM.YYYY"),  # 14.11.2022
        ("%d.%m.%y", "DD.MM.YY"),  # 14.11.22
        ("%Y.%m.%d", "YYYY.MM.DD"),  # 2025.04.11
        ("%y/%m/%d", "YY/MM/DD"),  # 23/01/18
        ("%y-%m-%d", "YY-MM-DD"),  # 23-01-18
        ("%Y%m%d", "YYYYMMDD"),  # 20230103
    ]

    for fmt, fmt_name in formats_to_try:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return (True, parsed, fmt_name)
        except ValueError:
            continue

    return (False, None, "")


def get_date_formats() -> List[Tuple[str, str]]:
    """
    Get list of supported date formats.

    Returns:
        List of tuples (format_code, format_name)

    Examples:
        >>> formats = get_date_formats()
        >>> for code, name in formats[:3]:
        ...     print(f"{name}: {code}")
        DD/MM/YYYY: %d/%m/%Y
        YYYY-MM-DD: %Y-%m-%d
        DD-MM-YYYY: %d-%m-%Y
    """
    return [
        ("%d/%m/%Y", "DD/MM/YYYY"),
        ("%Y-%m-%d", "YYYY-MM-DD"),
        ("%d-%m-%Y", "DD-MM-YYYY"),
        ("%m/%d/%Y", "MM/DD/YYYY"),
        ("%d %b %Y", "DD Mon YYYY"),
        ("%d %B %Y", "DD Month YYYY"),
        ("%Y/%m/%d", "YYYY/MM/DD"),
        ("%B %d, %Y", "Month DD, YYYY"),
        ("%d %b, %Y", "DD Mon, YYYY"),
        ("%d-%b-%Y", "DD-Mon-YYYY"),
        ("%d-%b-%y", "DD-Mon-YY"),
        ("%d.%m.%Y", "DD.MM.YYYY"),
        ("%Y.%m.%d", "YYYY.MM.DD"),
        ("%Y%m%d", "YYYYMMDD"),
    ]
