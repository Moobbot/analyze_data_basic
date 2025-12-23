import os
import json
import difflib
import csv
import shutil
import config
import utils

# Fields that should use date-specific matching logic
DATE_RELATED_FIELDS = [
    "date",
    "invoice date",
    "due date",
    "payment date",
    "contract date",
]

# Fields that should use percentage normalization (handle "7%" vs "7 %")
PERCENTAGE_FIELDS = ["tax type", "tax rate", "gst", "vat", "gst rate"]


def flatten_json(y):
    out = {}

    def flatten(x, name=""):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + ".")
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + ".")
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


def detect_date_format_from_text(text_content):
    """
    Detect date format (DD/MM or MM/DD) from text by finding dates with day > 12.

    Args:
        text_content: Text to analyze

    Returns:
        "DD/MM" if format is day-first, "MM/DD" if month-first, "UNKNOWN" if ambiguous
    """
    import re

    # Find all dates in format d/d/yy or d/d/yyyy
    date_pattern = r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b"
    matches = re.findall(date_pattern, text_content)

    for first, second, year in matches:
        first_num = int(first)
        second_num = int(second)

        # If first number > 12, must be DD/MM format
        if first_num > 12:
            return "DD/MM"

        # If second number > 12, must be MM/DD format
        if second_num > 12:
            return "MM/DD"

    # If no conclusive evidence, return unknown
    return "UNKNOWN"


def is_numeric_match(value_str, text_content):
    """
    Check if a numeric value appears in text with different decimal formatting.
    Handles cases like JSON: 0.0 vs PDF Text: 0.00
    Uses word boundary matching to ensure exact numeric matches.
    Prioritizes matching formats with equal or higher precision than the original value.

    Returns: (is_match, matched_format) or (False, None)
    """
    import re

    try:
        # Try to parse as a number
        num_value = float(value_str)

        # Determine the original precision of the value_str
        original_precision = 0
        if "." in value_str:
            decimal_part = value_str.split(".")[-1]
            original_precision = len(decimal_part)

        formats_to_try = set()  # Use a set to avoid duplicates

        # Generate formats with equal or higher precision
        # We'll check up to 3 decimal places beyond the original, or a max of 5 total
        max_additional_precision = 3
        max_total_precision = original_precision + max_additional_precision
        if max_total_precision > 5:  # Cap total precision to avoid excessive checks
            max_total_precision = 5

        for p in range(original_precision, max_total_precision + 1):
            formats_to_try.add(f"{num_value:.{p}f}")

        # Also add the original string representation, as it might have specific formatting
        # (e.g., "150.0" vs "150") or more precision than our generated ones.
        formats_to_try.add(value_str)

        # Add formats without trailing zeros if original had them (e.g., 150.40 -> 150.4)
        # This is important if the text has less precision but is still a valid match.
        # However, the instruction specifically says "equal or higher precision".
        # So, we will only add lower precision formats if the original_precision is > 0
        # and we want to allow matching "150.41" to "150.4" if the user meant it.
        # For now, sticking to the instruction: "equal or higher precision".
        # If original_precision is 0, we can still match 150 to 150.0, 150.00 etc.
        # The loop `range(original_precision, ...)` already handles this.
        # So, if original is "150.41", it will try "150.41", "150.410", "150.4100".
        # It will NOT try "150.4" or "150".

        # Search for any of these formats in the text with word boundaries
        for fmt in formats_to_try:
            # Escape special regex characters (like .)
            escaped_fmt = re.escape(fmt)
            # Use word boundary \b to ensure we match complete numbers
            # \b matches at positions where one side is a word character and the other is not
            pattern = r"\b" + escaped_fmt + r"\b"

            if re.search(pattern, text_content):
                return True, fmt

        return False, None
    except (ValueError, TypeError):
        # Not a numeric value
        return False, None


def normalize_whitespace(text):
    """
    Normalize whitespace by replacing newlines and multiple spaces with single space.
    Useful for comparing text that may be split across multiple lines in PDFs.
    """
    import re

    # Replace newlines and tabs with space
    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    # Replace multiple spaces with single space
    text = re.sub(r"\s+", " ", text)
    # Strip leading/trailing whitespace
    return text.strip()


def match_date_formats(parsed_date, text_content, text_lower, date_format):
    """
    Match date in various formats within text content.

    Args:
        parsed_date: datetime object of the date to match
        text_content: Full text content to search in
        text_lower: Lowercase version of text_content
        date_format: Original date format string

    Returns:
        Tuple of (status, score, match_text, date_format) if found, None otherwise
    """
    # Generate alternative date formats to search for
    alternate_formats = [
        parsed_date.strftime("%d %b %Y"),  # "03 Oct 2023"
        parsed_date.strftime("%d %B %Y"),  # "03 October 2023"
        parsed_date.strftime("%d/%m/%Y"),  # "03/10/2023"
        parsed_date.strftime("%Y-%m-%d"),  # "2023-10-03"
        parsed_date.strftime("%Y/%m/%d"),  # "2023/07/07" (YYYY/MM/DD)
        parsed_date.strftime("%d-%m-%Y"),  # "03-10-2023"
        parsed_date.strftime("%m/%d/%Y"),  # "10/03/2023"
        parsed_date.strftime("%B %d, %Y"),  # "October 03, 2023"
        parsed_date.strftime("%d %b, %Y"),  # "03 Oct, 2023"
        parsed_date.strftime("%d-%b-%Y"),  # "03-Oct-2023" (4-digit year)
        parsed_date.strftime("%d-%b-%y"),  # "03-Oct-23" (2-digit year)
    ]

    # Try to find any of these formats in the text
    for alt_format in alternate_formats:
        if alt_format.lower() in text_lower:
            return "FOUND_DATE_ALT_FORMAT", 0.95, alt_format, date_format

    # Also check without leading zeros
    day_no_zero = str(parsed_date.day)
    month_no_zero = str(parsed_date.month)
    year_2digit = str(parsed_date.year)[2:]  # "2024" -> "24"

    # Detect date format from text to handle ambiguous dates intelligently
    detected_format = detect_date_format_from_text(text_content)

    additional_formats = [
        f"{day_no_zero} {parsed_date.strftime('%b')} {parsed_date.year}",  # "3 Oct 2023"
        f"{day_no_zero}-{parsed_date.strftime('%b')} {parsed_date.year}",  # "31-Jan 2024"
        f"{day_no_zero}/{month_no_zero}/{parsed_date.year}",  # "3/10/2023" (DD/MM)
        f"{month_no_zero}/{day_no_zero}/{parsed_date.year}",  # "10/3/2023" (MM/DD)
        f"{parsed_date.year}/{month_no_zero}/{day_no_zero}",  # "2023/5/9" (YYYY/M/D)
        f"{day_no_zero}-{month_no_zero}-{parsed_date.year}",  # "3-10-2023" (DD-MM)
        f"{month_no_zero}-{day_no_zero}-{parsed_date.year}",  # "10-3-2023" (MM-DD)
        f"{day_no_zero}-{parsed_date.strftime('%b')}-{parsed_date.year}",  # "5-Sep-2021"
    ]

    # Add 2-digit year formats based on detected format
    if detected_format == "DD/MM":
        additional_formats.append(f"{day_no_zero}/{month_no_zero}/{year_2digit}")
    elif detected_format == "MM/DD":
        additional_formats.append(f"{month_no_zero}/{day_no_zero}/{year_2digit}")
    else:
        # Unknown format - try both
        additional_formats.append(f"{day_no_zero}/{month_no_zero}/{year_2digit}")
        additional_formats.append(f"{month_no_zero}/{day_no_zero}/{year_2digit}")

    for alt_format in additional_formats:
        if alt_format.lower() in text_lower:
            return "FOUND_DATE_ALT_FORMAT", 0.95, alt_format, date_format

    # If date not found and format is ambiguous, return CHECK_DATE
    if detected_format == "UNKNOWN":
        return (
            "CHECK_DATE",
            0,
            "Date format ambiguous - needs manual verification",
            date_format,
        )

    return None


def get_best_match(value, text_content, field_name=""):
    """
    Enhanced version with date-aware matching.
    If the value is a date, it tries to find the date in different formats in the text.

    Args:
        value: The value to search for
        text_content: The text to search in
        field_name: Name of the field being checked (for Date-specific logic)

    Returns: (status, score, match_text, date_format)
    """
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return "N/A", 0, "", ""

    val_str = str(value).strip()

    # Check if value is a date
    is_date_valid, parsed_date, date_format = utils.validate_date(val_str)

    # 1. Exact Match case-sensitive
    if val_str in text_content:
        return "FOUND", 1.0, val_str, date_format if is_date_valid else ""

    # 2. Exact Match case-insensitive
    text_lower = text_content.lower()
    val_lower = val_str.lower()
    if val_lower in text_lower:
        return (
            "FOUND_CASE_INSENSITIVE",
            0.9,
            val_str,
            date_format if is_date_valid else "",
        )

    # 2.2. DASH NORMALIZATION: Handle different dash types (–, —, -)
    # Normalize en-dash (U+2013), em-dash (U+2014) to regular hyphen-minus (U+002D)
    val_normalized_dash = val_str.replace("–", "-").replace("—", "-")
    text_normalized_dash = text_content.replace("–", "-").replace("—", "-")
    if val_normalized_dash.lower() in text_normalized_dash.lower():
        return "FOUND", 1.0, val_normalized_dash, ""

    # 2.3. PERCENTAGE MATCHING: Handle "7%" vs "7 %" and "8%" vs "8.00%"
    # Check if field name contains any percentage-related keyword
    is_percentage_field = any(
        keyword in field_name.lower() for keyword in PERCENTAGE_FIELDS
    )
    if "%" in val_str and is_percentage_field:
        import re

        # Normalize percentage: strip trailing zeros (8.00% -> 8%)
        def normalize_percentage(pct_str):
            # Extract number part before %
            match = re.match(r"^([\d.]+)%$", pct_str.strip())
            if match:
                num_str = match.group(1)
                # Convert to float and back to remove trailing zeros
                try:
                    num = float(num_str)
                    # Format without unnecessary decimals
                    normalized_num = str(num).rstrip("0").rstrip(".")
                    return normalized_num + "%"
                except ValueError:
                    return pct_str
            return pct_str

        # Normalize the JSON value
        val_normalized = normalize_percentage(val_str)

        # Also normalize all percentages in text for comparison
        text_normalized_pct = text_content
        for match in re.finditer(r"\b([\d.]+)\s*%", text_content):
            original = match.group(0)
            normalized = normalize_percentage(match.group(1) + "%")
            # Replace with space variant
            normalized_with_space = normalized.replace("%", " %")
            text_normalized_pct = text_normalized_pct.replace(
                original, normalized_with_space
            )

        # Try with space before % sign (e.g., "8%" -> "8 %")
        val_with_space = val_normalized.replace("%", " %")
        if val_with_space.lower() in text_normalized_pct.lower():
            return "FOUND", 1.0, val_with_space, ""

        # Try without space (original normalized value)
        if val_normalized.lower() in text_normalized_pct.lower():
            return "FOUND", 1.0, val_normalized, ""

    # 2.5. NORMALIZED WHITESPACE MATCHING: Handle multi-line text from PDFs
    val_normalized = normalize_whitespace(val_str)
    text_normalized = normalize_whitespace(text_content)

    if val_normalized in text_normalized:
        return "FOUND_NORMALIZED", 1.0, val_str, date_format if is_date_valid else ""

    # 3. DATE-SPECIFIC MATCHING: Only for date-related fields
    if is_date_valid and field_name.lower() in DATE_RELATED_FIELDS:
        result = match_date_formats(parsed_date, text_content, text_lower, date_format)
        if result:  # If date match found or CHECK_DATE returned
            return result

    # 3.5. NUMERIC MATCHING: Check if value is numeric with different decimal formatting
    is_match, matched_format = is_numeric_match(val_str, text_content)
    if is_match:
        return "FOUND_NUMERIC_FORMAT", 1.0, matched_format, ""

    # 4. Fuzzy Match
    lines = [line.strip() for line in text_content.splitlines() if line.strip()]
    best_ratio = 0.0
    best_line = ""

    for line in lines:
        ratio = difflib.SequenceMatcher(None, val_lower, line.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_line = line

    if best_ratio >= 0.6:
        return "SIMILAR", best_ratio, best_line, date_format if is_date_valid else ""

    return "MISSING", best_ratio, best_line, date_format if is_date_valid else ""


def check_file_consistency():
    """
    Check consistency between JSON labels and PDF datasets.
    Finds files present in Label directory but missing in Dataset directory, and vice versa.
    """
    print(">>> CHECKING FILE CONSISTENCY (Labels vs Datasets)")

    # Get all JSON files from LABEL_DIR
    if not os.path.exists(config.LABEL_DIR):
        print(f"Error: Label directory not found: {config.LABEL_DIR}")
        return

    json_files = {
        os.path.splitext(f)[0]
        for f in os.listdir(config.LABEL_DIR)
        if f.lower().endswith(".json")
    }

    # Get all PDF files from DATASET_DIR
    if not os.path.exists(config.DATASET_DIR):
        print(f"Error: Dataset directory not found: {config.DATASET_DIR}")
        return

    pdf_files = {
        os.path.splitext(f)[0]
        for f in os.listdir(config.DATASET_DIR)
        if f.lower().endswith(".pdf")
    }

    # Find discrepancies
    json_only = json_files - pdf_files
    pdf_only = pdf_files - json_files

    # Report results
    print(f"Total Labels (JSON): {len(json_files)}")
    print(f"Total PDFs: {len(pdf_files)}")
    print(f"Labels without PDF: {len(json_only)}")
    print(f"PDFs without Label: {len(pdf_only)}")

    missing_refs_report = os.path.join(config.REVIEW_DIR, "missing_files_reference.txt")
    utils.ensure_dir_exists(config.REVIEW_DIR)

    try:
        with open(missing_refs_report, "w", encoding="utf-8") as f:
            f.write("BÁO CÁO KIỂM TRA SỰ NHẤT QUÁN FILE (FILE CONSISTENCY CHECK)\n")
            f.write("=" * 70 + "\n")
            f.write(f"Label Directory: {config.LABEL_DIR}\n")
            f.write(f"Dataset Directory: {config.DATASET_DIR}\n")
            f.write("-" * 70 + "\n")
            f.write(f"Tổng số file Label (JSON): {len(json_files)}\n")
            f.write(f"Tổng số file Dataset (PDF): {len(pdf_files)}\n")
            f.write("=" * 70 + "\n\n")

            f.write(f"1. CÁC FILE CÓ LABEL NHƯNG THIẾU PDF ({len(json_only)} files)\n")
            f.write("-" * 50 + "\n")
            if json_only:
                for name in sorted(json_only):
                    f.write(f"{name}.json (Missing {name}.pdf)\n")
            else:
                f.write("Không có (Tất cả label đều có PDF tương ứng).\n")
            f.write("\n")

            f.write(f"2. CÁC FILE CÓ PDF NHƯNG THIẾU LABEL ({len(pdf_only)} files)\n")
            f.write("-" * 50 + "\n")
            if pdf_only:
                for name in sorted(pdf_only):
                    f.write(f"{name}.pdf (Missing {name}.json)\n")
            else:
                f.write("Không có (Tất cả PDF đều có Label tương ứng).\n")
            f.write("\n")

        print(f"Consistency report saved to: {missing_refs_report}")

    except Exception as e:
        print(f"Error writing consistency report: {e}")
    print("=" * 70 + "\n")


def verify_labels():
    print(">>> STARTING LABEL VERIFICATION")

    # Check file consistency first
    check_file_consistency()

    # Ensure review dir exists
    utils.ensure_dir_exists(config.REVIEW_DIR)

    # Get JSON files
    if not os.path.exists(config.LABEL_DIR):
        print(f"Error: Label directory not found: {config.LABEL_DIR}")
        return

    json_files = [
        f for f in os.listdir(config.LABEL_DIR) if f.lower().endswith(".json")
    ]
    total_files = len(json_files)
    print(f"Found {total_files} JSON label files.")

    results = []
    json_errors = []  # Track JSON files with parsing errors

    stats = {
        "Total Fields": 0,
        "Found": 0,
        "Similar": 0,
        "Missing": 0,
        "Date Fields": 0,
        "Date Alt Format Found": 0,
    }

    for i, json_filename in enumerate(json_files):
        json_path = os.path.join(config.LABEL_DIR, json_filename)
        base_name = os.path.splitext(json_filename)[0]
        txt_filename = base_name + ".txt"
        txt_path = os.path.join(config.EXTRACTED_TEXT_DIR, txt_filename)

        # Read JSON
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            error_msg = f"Error reading JSON {json_filename}: {e}"
            print(error_msg)
            json_errors.append({"Filename": json_filename, "Error": str(e)})
            continue

        # Read Text
        text_content = utils.read_file(txt_path)
        if text_content.startswith("[Error"):
            # If text extracted failed or file missing, mark all as missing
            text_content = ""

        # Flatten JSON to get all values
        flat_data = flatten_json(data)

        for key, value in flat_data.items():
            if value is None or str(value).strip() == "":
                continue  # Skip empty fields

            stats["Total Fields"] += 1

            # Use enhanced date-aware matching (pass key for date-specific logic)
            status, score, match_text, date_format = get_best_match(
                value, text_content, key
            )

            # Track date fields
            if date_format:
                stats["Date Fields"] += 1

            if "FOUND" in status:
                stats["Found"] += 1
                if status == "FOUND_DATE_ALT_FORMAT":
                    stats["Date Alt Format Found"] += 1
            elif status == "SIMILAR":
                stats["Similar"] += 1
            else:
                stats["Missing"] += 1

            results.append(
                {
                    "Filename": json_filename,
                    "Key": key,
                    "Value": str(value),
                    "Status": status,
                    "Score": f"{score:.2f}",
                    "BestMatchLine": match_text if status != "FOUND" else "",
                    "DateFormat": date_format,
                }
            )

        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{total_files} labels...")

    # Analyze results to find files with MISSING, N/A, or SIMILAR status
    files_with_missing = set()
    files_with_na = set()
    files_with_similar = set()

    for result in results:
        filename = result["Filename"]
        status = result["Status"]

        if status == "MISSING":
            files_with_missing.add(filename)
        elif status == "N/A":
            files_with_na.add(filename)
        elif status == "SIMILAR":
            files_with_similar.add(filename)

    # Write JSON Error Report and copy error files to check_for folder
    json_error_report = os.path.join(config.REVIEW_DIR, "json_parsing_errors.txt")
    check_for_dir = os.path.join(config.REVIEW_DIR, "check_for")

    try:
        # Create check_for directory if there are errors
        if json_errors:
            utils.ensure_dir_exists(check_for_dir)

        with open(json_error_report, "w", encoding="utf-8") as f:
            f.write("DANH SÁCH FILE JSON BỊ LỖI KHI PARSE\n")
            f.write("=" * 70 + "\n")
            f.write(f"Tổng số file lỗi: {len(json_errors)}\n")
            f.write(
                f"Tổng số file xử lý thành công: {total_files - len(json_errors)}\n"
            )
            f.write("=" * 70 + "\n\n")

            if json_errors:
                f.write(f"Các file lỗi đã được copy vào: {check_for_dir}\n")
                f.write("=" * 70 + "\n\n")

                for idx, error_info in enumerate(json_errors, 1):
                    f.write(f"{idx}. {error_info['Filename']}\n")
                    f.write(f"   Lỗi: {error_info['Error']}\n\n")

                    # Copy error file to check_for folder
                    try:
                        src = os.path.join(config.LABEL_DIR, error_info["Filename"])
                        dst = os.path.join(check_for_dir, error_info["Filename"])
                        shutil.copy2(src, dst)
                    except Exception as copy_error:
                        f.write(f"   [Không thể copy file: {copy_error}]\n\n")
            else:
                f.write("Không có file JSON nào bị lỗi.\n")

        print(f"JSON error report saved to: {json_error_report}")
        if json_errors:
            print(f"Error JSON files copied to: {check_for_dir}")
    except Exception as e:
        print(f"Error writing JSON error report: {e}")

    # Copy MISSING, N/A, and SIMILAR files to separate folders
    missing_dir = os.path.join(config.REVIEW_DIR, "check_for_missing")
    na_dir = os.path.join(config.REVIEW_DIR, "check_for_na")
    similar_dir = os.path.join(config.REVIEW_DIR, "check_for_similar")

    # Process MISSING files
    if files_with_missing:
        utils.ensure_dir_exists(missing_dir)
        print(f"\nCopying {len(files_with_missing)} files with MISSING status...")

        missing_report = os.path.join(config.REVIEW_DIR, "missing_files_report.txt")
        with open(missing_report, "w", encoding="utf-8") as f:
            f.write("DANH SÁCH FILE CÓ TRƯỜNG DỮ LIỆU MISSING\n")
            f.write("=" * 70 + "\n")
            f.write(f"Tổng số file: {len(files_with_missing)}\n")
            f.write(f"Đã copy vào: {missing_dir}\n")
            f.write("=" * 70 + "\n\n")

            for idx, json_filename in enumerate(sorted(files_with_missing), 1):
                f.write(f"{idx}. {json_filename}\n")

                # Copy JSON file
                try:
                    src_json = os.path.join(config.LABEL_DIR, json_filename)
                    dst_json = os.path.join(missing_dir, json_filename)
                    if os.path.exists(src_json):
                        shutil.copy2(src_json, dst_json)
                except Exception as e:
                    f.write(f"   [Lỗi copy JSON: {e}]\n")

                # Copy corresponding PDF file
                try:
                    base_name = os.path.splitext(json_filename)[0]
                    pdf_filename = base_name + ".pdf"
                    src_pdf = os.path.join(config.DATASET_DIR, pdf_filename)
                    dst_pdf = os.path.join(missing_dir, pdf_filename)

                    if os.path.exists(src_pdf):
                        shutil.copy2(src_pdf, dst_pdf)
                    else:
                        f.write(f"   [PDF không tồn tại: {pdf_filename}]\n")
                except Exception as e:
                    f.write(f"   [Lỗi copy PDF: {e}]\n")

        print(f"MISSING files report saved to: {missing_report}")
        print(f"MISSING files copied to: {missing_dir}")

    # Process N/A files
    if files_with_na:
        utils.ensure_dir_exists(na_dir)
        print(f"\nCopying {len(files_with_na)} files with N/A status...")

        na_report = os.path.join(config.REVIEW_DIR, "na_files_report.txt")
        with open(na_report, "w", encoding="utf-8") as f:
            f.write("DANH SÁCH FILE CÓ TRƯỜNG DỮ LIỆU N/A\n")
            f.write("=" * 70 + "\n")
            f.write(f"Tổng số file: {len(files_with_na)}\n")
            f.write(f"Đã copy vào: {na_dir}\n")
            f.write("=" * 70 + "\n\n")

            for idx, json_filename in enumerate(sorted(files_with_na), 1):
                f.write(f"{idx}. {json_filename}\n")

                # Copy JSON file
                try:
                    src_json = os.path.join(config.LABEL_DIR, json_filename)
                    dst_json = os.path.join(na_dir, json_filename)
                    if os.path.exists(src_json):
                        shutil.copy2(src_json, dst_json)
                except Exception as e:
                    f.write(f"   [Lỗi copy JSON: {e}]\n")

                # Copy corresponding PDF file
                try:
                    base_name = os.path.splitext(json_filename)[0]
                    pdf_filename = base_name + ".pdf"
                    src_pdf = os.path.join(config.DATASET_DIR, pdf_filename)
                    dst_pdf = os.path.join(na_dir, pdf_filename)

                    if os.path.exists(src_pdf):
                        shutil.copy2(src_pdf, dst_pdf)
                    else:
                        f.write(f"   [PDF không tồn tại: {pdf_filename}]\n")
                except Exception as e:
                    f.write(f"   [Lỗi copy PDF: {e}]\n")

        print(f"N/A files report saved to: {na_report}")
        print(f"N/A files copied to: {na_dir}")

    # Process SIMILAR files
    if files_with_similar:
        utils.ensure_dir_exists(similar_dir)
        print(f"\nCopying {len(files_with_similar)} files with SIMILAR status...")

        similar_report = os.path.join(config.REVIEW_DIR, "similar_files_report.txt")
        with open(similar_report, "w", encoding="utf-8") as f:
            f.write("DANH SÁCH FILE CÓ TRƯỜNG DỮ LIỆU SIMILAR (Tương đồng > 80%)\n")
            f.write("=" * 70 + "\n")
            f.write(f"Tổng số file: {len(files_with_similar)}\n")
            f.write(f"Đã copy vào: {similar_dir}\n")
            f.write("=" * 70 + "\n")
            f.write(
                "Lưu ý: Các file này có độ tương đồng > 60% nhưng không khớp chính xác.\n"
            )
            f.write("Cần kiểm tra để xác nhận dữ liệu có đúng hay không.\n")
            f.write("=" * 70 + "\n\n")

            for idx, json_filename in enumerate(sorted(files_with_similar), 1):
                f.write(f"{idx}. {json_filename}\n")

                # Copy JSON file
                try:
                    src_json = os.path.join(config.LABEL_DIR, json_filename)
                    dst_json = os.path.join(similar_dir, json_filename)
                    if os.path.exists(src_json):
                        shutil.copy2(src_json, dst_json)
                except Exception as e:
                    f.write(f"   [Lỗi copy JSON: {e}]\n")

                # Copy corresponding PDF file
                try:
                    base_name = os.path.splitext(json_filename)[0]
                    pdf_filename = base_name + ".pdf"
                    src_pdf = os.path.join(config.DATASET_DIR, pdf_filename)
                    dst_pdf = os.path.join(similar_dir, pdf_filename)

                    if os.path.exists(src_pdf):
                        shutil.copy2(src_pdf, dst_pdf)
                    else:
                        f.write(f"   [PDF không tồn tại: {pdf_filename}]\n")
                except Exception as e:
                    f.write(f"   [Lỗi copy PDF: {e}]\n")

        print(f"SIMILAR files report saved to: {similar_report}")
        print(f"SIMILAR files copied to: {similar_dir}")

    # Write CSV Report
    try:
        with open(
            config.VERIFY_REPORT_CSV, "w", newline="", encoding="utf-8"
        ) as csvfile:
            fieldnames = [
                "Filename",
                "Key",
                "Value",
                "Status",
                "Score",
                "BestMatchLine",
                "DateFormat",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r)
        print(f"Detailed verification CSV saved to: {config.VERIFY_REPORT_CSV}")
    except Exception as e:
        print(f"Error writing CSV report: {e}")

    # Write Summary Text Report
    try:
        with open(config.VERIFY_REPORT_TXT, "w", encoding="utf-8") as f:
            f.write(
                "BÁO CÁO ĐỐI SOÁT DỮ LIỆU LABEL VS EXTRACTED TEXT (With Date Checking)\n"
            )
            f.write("=" * 70 + "\n")
            f.write(f"Tổng số file Label: {total_files}\n")
            f.write(
                f"Tổng số trường dữ liệu (Fields) kiểm tra: {stats['Total Fields']}\n"
            )
            f.write(f"Số trường dữ liệu là ngày tháng: {stats['Date Fields']}\n")
            f.write("-" * 70 + "\n")
            f.write(
                f"1. Tìm thấy chính xác (Found): {stats['Found']} ({stats['Found']/stats['Total Fields']*100:.2f}%)\n"
            )
            f.write(
                f"   - Trong đó tìm thấy dạng thay thế (Date Alt Format): {stats['Date Alt Format Found']}\n"
            )
            f.write(
                f"2. Tương đồng (Similar > 60%): {stats['Similar']} ({stats['Similar']/stats['Total Fields']*100:.2f}%)\n"
            )
            f.write(
                f"3. Không tìm thấy (Missing):    {stats['Missing']} ({stats['Missing']/stats['Total Fields']*100:.2f}%)\n"
            )
            f.write("=" * 70 + "\n")
            f.write("Chi tiết xem tại file: label_verification.csv\n")
            f.write(
                "Các ngày tháng sẽ được tìm kiếm trong nhiều định dạng khác nhau.\n"
            )

        print(f"Summary report saved to: {config.VERIFY_REPORT_TXT}")
    except Exception as e:
        print(f"Error writing TXT report: {e}")


if __name__ == "__main__":
    verify_labels()
