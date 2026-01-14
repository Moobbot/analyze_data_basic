import json
import calendar
import re
from pathlib import Path


def analyze_date_match(content, v1, v2):
    """
    Analyzes text content to verify if v1, v2 date parts imply a MM/DD format.
    v1: Potential Month (if verified) or Day (if inverted)
    v2: Potential Day (if verified) or Month (if inverted)

    Returns: (is_verified, note, is_suspicious)
    """
    # Separator pattern: Standard chars or Soft Hyphen (\xad)
    sep_pattern = r"(?:[-/.\s]|\xad)"

    # 1. Check for Alpha-Numeric Match (e.g. 12-Mar) -- confirms MM/DD
    # Hypothesis: JSON is MM/DD. So v1=Month, v2=Day.
    # Text should show Day v2 and MonthName(v1).
    m_abbr_1 = calendar.month_abbr[v1].lower()
    m_name_1 = calendar.month_name[v1].lower()
    m_pat_1 = rf"(?:{m_abbr_1}|{m_name_1})"

    # Regex for verified match: "Day(v2) Month(v1)" or "Month(v1) Day(v2)"
    # e.g. "12 Mar" or "Mar 12"
    verified_patterns = [
        rf"\b0?{v2}(?:st|nd|rd|th)?\s*{sep_pattern}?\s*{m_pat_1}\b",
        rf"\b{m_pat_1}\s*{sep_pattern}?\s*0?{v2}(?:st|nd|rd|th)?\b",
    ]

    for pat in verified_patterns:
        if re.search(pat, content):
            return True, f"Found text matching MM/DD: {v2}-{m_abbr_1}", False

    # 2. Check for Suspicious Match (e.g. 4-Feb where label is 04/02) -- implies Inversion
    # Hypothesis: JSON is Inverted (DD/MM). So v1=Day, v2=Month.
    # Text should show Day v1 and MonthName(v2).
    m_abbr_2 = calendar.month_abbr[v2].lower()
    m_name_2 = calendar.month_name[v2].lower()
    m_pat_2 = rf"(?:{m_abbr_2}|{m_name_2})"

    suspicious_patterns = [
        rf"\b0?{v1}(?:st|nd|rd|th)?\s*{sep_pattern}?\s*{m_pat_2}\b",
        rf"\b{m_pat_2}\s*{sep_pattern}?\s*0?{v1}(?:st|nd|rd|th)?\b",
    ]

    for pat in suspicious_patterns:
        if re.search(pat, content):
            return (
                False,
                f"SUSPICIOUS: Found text matching DD/MM ({v1}-{m_abbr_2}). Label {v1}/{v2} might be inverted.",
                True,
            )

    # 3. Check for Numeric Matches
    # Separator for numeric can be same
    sep_pattern_num = r"(?:[-/.]|\xad)"

    # Case A: Numeric Verified
    # Text has v2/v1 (Day/Month). Matches JSON v1/v2 (Month/Day).
    if re.search(rf"\b0?{v2}\s*{sep_pattern_num}\s*0?{v1}\b", content):
        return (
            True,
            f"NUMERIC VERIFIED: Found text {v2}/{v1} (DD/MM). Matches JSON {v1}/{v2} (MM/DD).",
            False,
        )

    # Case B: Numeric Suspicious
    # Text has v1/v2 (Day/Month). Matches JSON v1/v2 (Day/Month) -> Inverted JSON.
    if re.search(rf"\b0?{v1}\s*{sep_pattern_num}\s*0?{v2}\b", content):
        return (
            False,
            f"SUSPICIOUS (NUMERIC): Found text {v1}/{v2} (DD/MM). Label {v1}/{v2} likely inverted.",
            True,
        )

    return False, "Text file found but no matching distinct date pattern", False


def audit_ambiguous_dates(directory_path):
    print(f"Auditing ambiguous dates (Day <= 12 AND Month <= 12) in: {directory_path}")

    verified_files = []
    still_ambiguous = []

    directory = Path(directory_path)
    if not directory.exists():
        print(f"Directory not found: {directory}")
        return

    # Base dir for text lookup
    # .../analyze_data_invoice/datasets/data-all/labels -> .../analyze_data_invoice
    base_dir = directory.parent.parent.parent
    text_dir = base_dir / "output_analyze" / "data-all" / "extracted_text"

    for file_path in directory.rglob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    continue

            if isinstance(data, dict) and "Date" in data and data["Date"]:
                date_str = data["Date"]
                parts = re.split(r"[/-]", date_str)  # standard split

                if len(parts) == 3:
                    # Check if numeric
                    if parts[0].isdigit() and parts[1].isdigit():
                        v1 = int(parts[0])
                        v2 = int(parts[1])

                        # Check for ambiguity: Both parts <= 12
                        if 1 <= v1 <= 12 and 1 <= v2 <= 12:
                            # It is AMBIGUOUS. Now try to verify with text.

                            # Construct path to text file
                            try:
                                rel_path = file_path.relative_to(directory)
                                txt_path = text_dir / rel_path.with_suffix(".txt")

                                if txt_path.exists():
                                    with open(txt_path, "r", encoding="utf-8") as f_txt:
                                        content = f_txt.read().lower()

                                    if not content.strip():
                                        verification_note = "Text file empty"
                                        still_ambiguous.append(
                                            (
                                                file_path.name,
                                                date_str,
                                                verification_note,
                                            )
                                        )
                                        continue
                                    elif not re.search(r"\d", content):
                                        verification_note = "Text file contains no digits (cannot be a date)"
                                        still_ambiguous.append(
                                            (
                                                file_path.name,
                                                date_str,
                                                verification_note,
                                            )
                                        )
                                        continue

                                    # Use helper function
                                    is_verified, note, is_suspicious = (
                                        analyze_date_match(content, v1, v2)
                                    )

                                    if is_verified:
                                        verified_files.append(
                                            (file_path.name, date_str, note)
                                        )
                                    else:
                                        still_ambiguous.append(
                                            (file_path.name, date_str, note)
                                        )

                                else:
                                    still_ambiguous.append(
                                        (
                                            file_path.name,
                                            date_str,
                                            "Text file not found",
                                        )
                                    )
                            except Exception as e:
                                still_ambiguous.append(
                                    (
                                        file_path.name,
                                        date_str,
                                        f"Error reading text: {e}",
                                    )
                                )

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print(f"\nAudit complete.")
    print(f"Verified Safe (MM/DD confirmed): {len(verified_files)}")
    print(f"Still Ambiguous / Suspicious: {len(still_ambiguous)}")

    output_file = Path("ambiguous_dates_audit.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Ambiguous Date Audit\n")
        f.write(f"Ref: Label Dir: {directory}\n")
        f.write(f"Ref: Text Dir: {text_dir}\n")
        f.write(f"Verified Safe (MM/DD confirmed): {len(verified_files)}\n")
        f.write(f"Still Ambiguous / Suspicious: {len(still_ambiguous)}\n")
        f.write("=" * 60 + "\n\n")

        if verified_files:
            f.write("--- VERIFIED BY TEXT (Matches Label's MM/DD) ---\n")
            for name, date_val, note in verified_files:
                f.write(f"[OK] {name}: {date_val} | {note}\n")
            f.write("\n")

        if still_ambiguous:
            # Sort to put "SUSPICIOUS" ones first
            suspicious = sorted(
                [x for x in still_ambiguous if "SUSPICIOUS" in x[2]], key=lambda x: x[0]
            )
            others = sorted(
                [x for x in still_ambiguous if "SUSPICIOUS" not in x[2]],
                key=lambda x: x[0],
            )

            if suspicious:
                f.write("--- SUSPICIOUS / LIKELY INVERTED (Matches DD/MM) ---\n")
                f.write(
                    "NOTE: These files likely have Date in DD/MM/YYYY format, but schema expects MM/DD/YYYY.\n"
                )
                for name, date_val, note in suspicious:
                    f.write(f"[WARN] {name}: {date_val} | {note}\n")
                f.write("\n")

            f.write("--- STILL AMBIGUOUS / NO MATCHING TEXT ---\n")
            for name, date_val, note in others:
                f.write(f"[?] {name}: {date_val} | {note}\n")

    print(f"Detailed audit report saved to: {output_file.absolute()}")


if __name__ == "__main__":
    target_dir = (
        Path(__file__).parent.parent
        / "datasets"
        / "data-all"
        / "true-2026-01-11"
        / "labels"
    )

    if not target_dir.exists():
        target_dir = Path(
            r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\analyze_data_invoice\datasets\data-all\labels"
        )

    audit_ambiguous_dates(target_dir)
