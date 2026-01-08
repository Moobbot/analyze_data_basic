import os
import json
import csv
import config

# Import from lib modules
from lib.logger import get_logger
from lib.matchers import get_best_match
from lib.constants import DATE_RELATED_FIELDS, PERCENTAGE_FIELDS, DEFAULT_BATCH_SIZE

# Setup logger
logger = get_logger(__name__)


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


# Note: get_best_match and helper functions are now imported from lib.matchers
#       This significantly reduces code duplication and improves maintainability


# Keep this function for backward compatibility if needed elsewhere
def _legacy_get_best_match(value, text_content, field_name=""):
    """Legacy wrapper - use lib.matchers.get_best_match instead."""
    return get_best_match(value, text_content, field_name)

    # 1. Exact Match Check
    # Distinguish between Whole Word Match (FOUND) and Substring Match (FOUND_SUBSTRING)
    if val_str in text_content:
        # Check for whole word match using regex
        # Escape special regex characters in val_str
        val_pattern = re.escape(val_str)
        # Look for the value surrounded by word boundaries (or start/end of string)
        # Note: \b works for alphanumerics. For symbols, it depends.
        # Let's try a safer word boundary approach that includes whitespace/punctuation

        # Simple regex word boundary check first
        whole_word_pattern = f"(?<![a-zA-Z0-9]){val_pattern}(?![a-zA-Z0-9])"

        if re.search(whole_word_pattern, text_content):
            context = find_context_line(val_str, text_content)
            return "FOUND", 1.0, val_str, date_format if is_date_valid else "", context
        else:
            # Found but NOT as a whole word (e.g. "RSPHL" in "RSPHL2510")
            # Wait, user example: "RSPHL/2510/00" in "RSPHL/2510/002"
            # 0 vs 2 are digits, so \b or alphanumeric check works.
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

    # 2. Case Insensitive
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

    # 2.3 Percentage
    is_pct_field = any(k in field_name.lower() for k in PERCENTAGE_FIELDS)
    if "%" in val_str and is_pct_field:
        # (Simplified logic from original for brevity, maintaining core intent)
        val_norm = val_str.rstrip("0").rstrip(".").replace(" ", "")  # Very basic norm
        # Ideally import the full logic if critical, but standard fuzzy match helps too.
        pass

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

    # 3. Date Specific
    if is_date_valid and field_name.lower() in DATE_RELATED_FIELDS:
        result = match_date_formats(parsed_date, text_content, text_lower, date_format)
        if result:
            status, score, match_text, fmt = result
            context = ""
            if status != "CHECK_DATE":
                context = find_context_line(match_text, text_content, True)
            return status, score, match_text, fmt, context

    # 3.5 Numeric
    is_match, matched_format = is_numeric_match(val_str, text_content)
    if is_match:
        context = find_context_line(matched_format, text_content)
        return "FOUND_NUMERIC_FORMAT", 1.0, matched_format, "", context

    # 4. Fuzzy
    lines = [line.strip() for line in text_content.splitlines() if line.strip()]
    best_ratio = 0.0
    best_line = ""
    for line in lines:
        ratio = difflib.SequenceMatcher(None, val_lower, line.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_line = line

    if best_ratio >= 0.6:
        return (
            "SIMILAR",
            best_ratio,
            best_line,
            date_format if is_date_valid else "",
            best_line,
        )

    return "MISSING", best_ratio, best_line, date_format if is_date_valid else "", ""


def check_file_consistency():
    logger.info("Checking file consistency")
    if not config.LABEL_DIR.exists():
        return
    if not config.DATASET_DIR.exists():
        return

    json_files = {f.stem for f in config.LABEL_DIR.rglob("*.json")}
    pdf_files = {f.stem for f in config.DATASET_DIR.rglob("*.pdf")}

    json_only = json_files - pdf_files
    pdf_only = pdf_files - json_files

    report_path = config.REVIEW_DIR / "missing_files_reference.txt"
    config.REVIEW_DIR.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("FILE CONSISTENCY CHECK\n" + "=" * 50 + "\n")
        f.write(f"Labels without PDF: {len(json_only)}\n")
        f.write(f"PDFs without Label: {len(pdf_only)}\n\n")
        if json_only:
            f.write("Labels missing PDF:\n" + "\n".join(sorted(json_only)) + "\n\n")
        if pdf_only:
            f.write("PDFs missing Label:\n" + "\n".join(sorted(pdf_only)) + "\n")
    logger.info(f"Consistency report saved to: {report_path}")


def verify_labels():
    logger.info("Starting label verification")
    check_file_consistency()
    config.REVIEW_DIR.mkdir(parents=True, exist_ok=True)

    json_files = list(config.LABEL_DIR.rglob("*.json"))
    total_files = len(json_files)
    logger.info(f"Found {total_files} JSON label files")

    stats = {
        "Total Fields": 0,
        "Found": 0,
        "Found Alias": 0,
        "Found Case Insensitive": 0,
        "Found Normalized": 0,
        "Found Numeric": 0,
        "Similar": 0,
        "Missing": 0,
        "Date Fields": 0,
        "Date Alt Format Found": 0,
        "Found Substring": 0,
    }

    results = []
    json_errors = []

    for i, json_path in enumerate(json_files):
        base_name = json_path.stem

        rel_path = json_path.relative_to(config.LABEL_DIR)
        txt_rel_path = rel_path.with_suffix(".txt")
        txt_path = config.EXTRACTED_TEXT_DIR / txt_rel_path

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            json_errors.append({"Filename": str(rel_path), "Error": str(e)})
            continue

        text_content = ""
        if txt_path.exists():
            with open(txt_path, "r", encoding="utf-8") as f:
                text_content = f.read()

        flat_data = flatten_json(data)
        for key, value in flat_data.items():
            if value is None or str(value).strip() == "":
                continue

            stats["Total Fields"] += 1

            status, score, match_text, date_fmt, context = get_best_match(
                value, text_content, key
            )

            # Update Stats
            if status == "FOUND":
                stats["Found"] += 1
            elif status == "FOUND_ALIAS":
                stats["Found Alias"] += 1
                stats["Found"] += 1
            elif status == "FOUND_CASE_INSENSITIVE":
                stats["Found Case Insensitive"] += 1
                stats["Found"] += 1
            elif status in ["FOUND_NORMALIZED", "FOUND_NORMALIZED_FUZZY"]:
                stats["Found Normalized"] += 1
                stats["Found"] += 1
            elif status == "FOUND_NUMERIC_FORMAT":
                stats["Found Numeric"] += 1
                stats["Found"] += 1
            elif status == "FOUND_DATE_ALT_FORMAT":
                stats["Date Alt Format Found"] += 1
                stats["Found"] += 1
            elif status == "FOUND_SUBSTRING":
                stats["Found Substring"] += 1
            elif status == "SIMILAR":
                stats["Similar"] += 1
            elif status == "MISSING":
                stats["Missing"] += 1

            if date_fmt:
                stats["Date Fields"] += 1

            results.append(
                {
                    "Filename": str(rel_path),
                    "Key": key,
                    "Value": str(value),
                    "Status": status,
                    "Score": f"{score:.2f}",
                    "BestMatchLine": match_text if "FOUND" in status else "",
                    "DateFormat": date_fmt,
                    "ContextLine": context,
                }
            )

        if (i + 1) % DEFAULT_BATCH_SIZE == 0:
            logger.info(f"Processed {i+1}/{total_files} files")

    # Save CSV
    try:
        with open(config.VERIFY_REPORT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "Filename",
                    "Key",
                    "Value",
                    "Status",
                    "Score",
                    "BestMatchLine",
                    "DateFormat",
                    "ContextLine",
                ],
            )
            writer.writeheader()
            writer.writerows(results)
        logger.info(f"Results saved to {config.VERIFY_REPORT_CSV}")
    except Exception as e:
        logger.error(f"Error saving CSV: {e}")

    # Generate Text Report
    try:
        report_lines = []
        report_lines.append("LABEL VERIFICATION REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Total Files Processed: {total_files}")
        report_lines.append(f"Total Fields Checked: {stats['Total Fields']}")
        report_lines.append("-" * 60)
        report_lines.append(f"1. FOUND (Exact/High Confidence): {stats['Found']}")
        report_lines.append(
            f"   - Exact Match: {stats['Found'] - stats['Found Alias'] - stats['Found Case Insensitive'] - stats['Found Normalized'] - stats['Found Numeric'] - stats['Date Alt Format Found']}"
        )
        report_lines.append(f"   - Alias (e.g. USD -> US$): {stats['Found Alias']}")
        report_lines.append(f"   - Case Insensitive: {stats['Found Case Insensitive']}")
        report_lines.append(
            f"   - Normalized (Whitespace/Dash): {stats['Found Normalized']}"
        )
        report_lines.append(
            f"   - Numeric Match (Format diff): {stats['Found Numeric']}"
        )
        report_lines.append(
            f"   - Date Alternate Format: {stats['Date Alt Format Found']}"
        )
        report_lines.append(f"   - Substring Match: {stats['Found Substring']}")
        report_lines.append("-" * 60)
        report_lines.append(f"2. SIMILAR (Needs Review): {stats['Similar']}")
        report_lines.append(f"3. MISSING (Not Found): {stats['Missing']}")
        report_lines.append("-" * 60)
        report_lines.append(f"Date Fields Detected: {stats['Date Fields']}")
        report_lines.append("=" * 60)

        with open(config.VERIFY_REPORT_TXT, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
        logger.info(f"Text report saved to {config.VERIFY_REPORT_TXT}")

    except Exception as e:
        logger.error(f"Error writing text report: {e}")

    if json_errors:
        logger.warning(
            f"Found {len(json_errors)} JSON errors. Check report for details."
        )


if __name__ == "__main__":
    verify_labels()
