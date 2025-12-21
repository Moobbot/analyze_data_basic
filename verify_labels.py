import os
import json
import difflib
import csv
import shutil
import config
import utils


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


def is_numeric_match(value_str, text_content):
    """
    Check if a numeric value appears in text with different decimal formatting.
    Handles cases like JSON: 0.0 vs PDF Text: 0.00

    Returns: (is_match, matched_format) or (False, None)
    """
    try:
        # Try to parse as a number
        num_value = float(value_str)

        # Generate common decimal formats
        # Handle both positive and negative numbers, with/without leading spaces
        formats_to_try = [
            f"{num_value:.0f}",  # 0, 10, 100
            f"{num_value:.1f}",  # 0.0, 10.5, 100.0
            f"{num_value:.2f}",  # 0.00, 10.50, 100.00
            f"{num_value:.3f}",  # 0.000, 10.500, 100.000
            f" {num_value:.2f}",  # With leading space (common in PDFs)
            f" {num_value:.0f}",
            f" {num_value:.1f}",
        ]

        # Also add the original string representation
        formats_to_try.append(value_str)

        # Search for any of these formats in the text
        for fmt in formats_to_try:
            if fmt in text_content:
                return True, fmt

        return False, None
    except (ValueError, TypeError):
        # Not a numeric value
        return False, None


def get_best_match(value, text_content):
    """
    Enhanced version with date-aware matching.
    If the value is a date, it tries to find the date in different formats in the text.

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

    # 3. DATE-SPECIFIC MATCHING: If value is a date, try to find it in alternate formats
    if is_date_valid:
        # Generate alternative date formats to search for
        alternate_formats = [
            parsed_date.strftime("%d %b %Y"),  # "03 Oct 2023"
            parsed_date.strftime("%d %B %Y"),  # "03 October 2023"
            parsed_date.strftime("%d/%m/%Y"),  # "03/10/2023"
            parsed_date.strftime("%Y-%m-%d"),  # "2023-10-03"
            parsed_date.strftime("%d-%m-%Y"),  # "03-10-2023"
            parsed_date.strftime("%m/%d/%Y"),  # "10/03/2023"
            parsed_date.strftime("%B %d, %Y"),  # "October 03, 2023"
            parsed_date.strftime("%d %b, %Y"),  # "03 Oct, 2023"
        ]

        # Try to find any of these formats in the text
        for alt_format in alternate_formats:
            if alt_format.lower() in text_lower:
                return "FOUND_DATE_ALT_FORMAT", 0.95, alt_format, date_format

        # Also check without leading zeros
        day_no_zero = str(parsed_date.day)
        month_no_zero = str(parsed_date.month)

        additional_formats = [
            f"{day_no_zero} {parsed_date.strftime('%b')} {parsed_date.year}",  # "3 Oct 2023"
            f"{day_no_zero}/{month_no_zero}/{parsed_date.year}",  # "3/10/2023"
        ]

        for alt_format in additional_formats:
            if alt_format.lower() in text_lower:
                return "FOUND_DATE_ALT_FORMAT", 0.95, alt_format, date_format

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


def verify_labels():
    print(">>> STARTING LABEL VERIFICATION")

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

            # Use enhanced date-aware matching
            status, score, match_text, date_format = get_best_match(value, text_content)

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
                "Lưu ý: Các file này có độ tương đồng > 80% nhưng không khớp chính xác.\n"
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
