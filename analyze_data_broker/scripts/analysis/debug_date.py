import re


def identify_date_format(date_str):
    patterns = {
        r"^\d{1,2}/\d{1,2}/\d{4}$": "MM/DD/YYYY or DD/MM/YYYY",
        r"^\d{4}-\d{2}-\d{2}$": "YYYY-MM-DD",
        r"^\d{2}-\d{2}-\d{4}$": "DD-MM-YYYY or MM-DD-YYYY",
        r"^\d{1,2}\.\d{1,2}\.\d{4}$": "DD.MM.YYYY or MM.DD.YYYY",
        r"^\d{4}/\d{2}/\d{2}$": "YYYY/MM/DD",
        r"^\d{1,2}-\w{3}-\d{4}$": "DD-MMM-YYYY",
        r"^\w{3}\s+\d{1,2},\s+\d{4}$": "MMM DD, YYYY",
        # Additional Formats
        r"^\d{1,2}-\w{3}-\d{2}$": "DD-MMM-YY",
        r"^\d{4}\.\d{2}\.\d{2}$": "YYYY.MM.DD",
        r"^\d{1,2}/\d{1,2}/\d{2}$": "MM/DD/YY or DD/MM/YY",
        r"^\d{2}-\d{2}-\d{2}$": "DD-MM-YY",
        r"^\d{8}$": "YYYYMMDD",
        r"^\d{1,2}\s+[A-Za-z]+\s+\d{4}$": "DD MMM YYYY",
    }

    print(f"Testing string: '{date_str}'")
    for pattern, format_name in patterns.items():
        if re.match(pattern, date_str):
            print(f"Match found! Pattern: {pattern} -> Format: {format_name}")
            return format_name
    print("No match found.")
    return "unknown"


identify_date_format("26-May-25")
identify_date_format("28-May-25")
