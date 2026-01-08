# validation_logic.py
import re
from datetime import datetime
import validation_config
import utils  # Import utils

# ==============================================================================
# Helper Functions
# ==============================================================================


def detect_date_format_from_text(text):
    """
    Attempts to detect the prevalent date format (DD/MM vs MM/DD) in text.
    Simple heuristic based on numbers > 12 in first vs second position.
    """
    # Regex for XX/XX/XXXX or XX-XX-XXXX
    matches = re.findall(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", text)
    if not matches:
        return "UNKNOWN"

    first_pos_gt_12 = 0
    second_pos_gt_12 = 0

    for d1, d2, y in matches:
        if int(d1) > 12:
            first_pos_gt_12 += 1
        if int(d2) > 12:
            second_pos_gt_12 += 1

    if first_pos_gt_12 > 0 and second_pos_gt_12 == 0:
        return "DD/MM"
    elif second_pos_gt_12 > 0 and first_pos_gt_12 == 0:
        return "MM/DD"

    return "UNKNOWN"


def match_date_formats(parsed_date, text_content, text_lower, date_format):
    """
    Checks if the parsed_date exists in text in various formats.
    Ported from check_date.py.
    """
    text_lower = text_lower.replace("\xad", "-")

    # Standard Python formats
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

    # Custom formats
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

    # Ordinal Suffixes
    def get_ordinal_suffix(day):
        if 11 <= day <= 13:
            return "th"
        last_digit = day % 10
        return {1: "st", 2: "nd", 3: "rd"}.get(last_digit, "th")

    suffix = get_ordinal_suffix(parsed_date.day)
    # Add ordinal formats
    additional_formats.append(
        f"{parsed_date.strftime('%B')}{parsed_date.day}{suffix}, {parsed_date.year}"
    )
    additional_formats.append(
        f"{parsed_date.strftime('%B')} {parsed_date.day}{suffix}, {parsed_date.year}"
    )
    additional_formats.append(
        f"{parsed_date.day}{suffix} {parsed_date.strftime('%b')} {parsed_date.year}"
    )
    additional_formats.append(
        f"{parsed_date.day}{suffix} {parsed_date.strftime('%B')} {parsed_date.year}"
    )
    additional_formats.append(
        f"{parsed_date.strftime('%b')} {parsed_date.day}{suffix},{parsed_date.year}"
    )
    additional_formats.append(
        f"{parsed_date.strftime('%B')} {parsed_date.day}{suffix},{parsed_date.year}"
    )

    # Compact formats
    additional_formats.append(parsed_date.strftime("%d%b%Y"))
    additional_formats.append(parsed_date.strftime("%d%B%Y"))

    # 2-digit year slash formats based on detected format
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


# ==============================================================================
# Validation Functions
# ==============================================================================


def check_transaction_type(data, text_content, result_log):
    """Validates the 'Transaction Type' field against extracted text."""
    field = "Transaction Type"
    val = data.get(field)

    if not val:
        result_log["Transaction Type"] = "MISSING"
        return

    val_upper = val.upper()
    keywords = validation_config.TRANSACTION_KEYWORDS.get(val_upper, [])

    if not keywords:
        if val_upper not in validation_config.TRANSACTION_KEYWORDS:
            result_log["Transaction Type"] = f"WARN: Unknown Type '{val}'"
        else:
            result_log["Transaction Type"] = f"FAIL: No keywords for '{val}'"
        return

    text_lower = utils.normalize_text(text_content)
    found = False

    for kw in keywords:
        if kw.lower() in text_lower:
            found = True
            break

    if found:
        result_log["Transaction Type"] = "PASS"
    else:
        result_log["Transaction Type"] = f"FAIL: Keywords not found"


def check_date_field(field_name, data, text_content, result_log):
    """Validates date fields using enhanced matching logic."""
    val = data.get(field_name)

    if not val:
        result_log[field_name] = "MISSING"
        return

    # 1. Validate Format (Must be MM/dd/yyyy)
    try:
        val_date = datetime.strptime(val, "%m/%d/%Y")
    except ValueError:
        result_log[field_name] = f"FAIL: Invalid Format '{val}'"
        return

    # 2. Check using match_date_formats
    text_lower = utils.normalize_text(text_content)

    # Check date presence
    match_result = match_date_formats(val_date, text_content, text_lower, "MM/dd/yyyy")

    if match_result:
        # Match result is a tuple/list: (Status, Score, FoundFormat, OriginalFormat)
        status_code = match_result[0]
        if status_code == "FOUND_DATE_ALT_FORMAT":
            result_log[field_name] = f"PASS"
        elif status_code == "CHECK_DATE":
            result_log[field_name] = "WARN: Ambiguous Date Format"
        else:
            result_log[field_name] = "PASS"  # Treat other non-None as pass?
    else:
        result_log[field_name] = f"WARN: Date '{val}' not found in text"

    # 3. Check for Date Keywords Context (Optional enhancement)
    date_keywords = validation_config.DATE_KEYWORDS.get(field_name, [])
    found_context = False
    for kw in date_keywords:
        if kw.lower() in text_lower:
            found_context = True
            break

    if not found_context and result_log[field_name] == "PASS":
        # Determine if we want to fail strict context or just append info
        # Current logic in check_transaction_type.py didn't strictly fail on missing context if date was found
        # But let's stick to the previous behavior of warning logic or just keeping PASS if date found.
        # However, to be helpful, let's append info if context is missing?
        # Simpler: Just rely on date finding for PASS/FAIL
        pass


def check_isin(data, result_log):
    """Validates Securities ID (ISIN) length."""
    sec_id = data.get("Securities ID")

    if sec_id:
        if isinstance(sec_id, str) and len(sec_id) == 12:
            result_log["ISIN Status"] = "PASS"
        else:
            result_log["ISIN Status"] = f"FAIL: Len={len(sec_id)}"
    else:
        result_log["ISIN Status"] = "MISSING"


def check_generic_field(field, data, expected_type, result_log):
    """Validates simple type constraints for generic fields."""
    val = data.get(field)

    if val is None:
        return

    if not isinstance(val, expected_type):
        if isinstance(expected_type, tuple):
            expected_name = " or ".join([t.__name__ for t in expected_type])
        else:
            expected_name = expected_type.__name__

        result_log["Generic Errors"].append(
            f"{field}: Expected {expected_name}, got {type(val).__name__}"
        )
