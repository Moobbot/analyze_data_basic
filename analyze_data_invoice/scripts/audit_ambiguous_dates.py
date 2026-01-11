import json
from pathlib import Path


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

    import calendar
    import re

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
                            is_verified = False
                            verification_note = ""

                            # Construct path to text file
                            try:
                                rel_path = file_path.relative_to(directory)
                                txt_path = text_dir / rel_path.with_suffix(".txt")

                                if txt_path.exists():
                                    with open(txt_path, "r", encoding="utf-8") as f_txt:
                                        content = f_txt.read().lower()

                                    # Hypothesis: Label is MM/DD/YYYY (v1=Month, v2=Day)
                                    m_abbr_1 = calendar.month_abbr[
                                        v1
                                    ].lower()  # e.g. mar for 3

                                    # Look for "12 mar" or "mar 12" (Day v2 + Month v1)
                                    # Use regex boundaries to match exact words
                                    if re.search(
                                        rf"\b{v2}\s*[-/.]?\s*{m_abbr_1}\b", content
                                    ) or re.search(
                                        rf"\b{m_abbr_1}\s*[-/.]?\s*{v2}\b", content
                                    ):
                                        is_verified = True
                                        verification_note = f"Found text matching MM/DD: {v2}-{m_abbr_1}"
                                    else:
                                        verification_note = "Text file found but no matching distinct date pattern"
                                else:
                                    verification_note = "Text file not found"
                            except Exception as e:
                                verification_note = f"Error reading text: {e}"

                            if is_verified:
                                verified_files.append(
                                    (file_path.name, date_str, verification_note)
                                )
                            else:
                                still_ambiguous.append(
                                    (file_path.name, date_str, verification_note)
                                )

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print(f"\nAudit complete.")
    print(f"Verified Safe (MM/DD confirmed): {len(verified_files)}")
    print(f"Still Ambiguous: {len(still_ambiguous)}")

    output_file = Path("ambiguous_dates_audit.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Ambiguous Date Audit\n")
        f.write(f"Ref: Label Dir: {directory}\n")
        f.write(f"Ref: Text Dir: {text_dir}\n")
        f.write(f"Verified Safe (MM/DD confirmed): {len(verified_files)}\n")
        f.write(f"Still Ambiguous: {len(still_ambiguous)}\n")
        f.write("=" * 60 + "\n\n")

        if verified_files:
            f.write("--- VERIFIED BY TEXT (Matches Label's MM/DD) ---\n")
            for name, date_val, note in verified_files:
                f.write(f"[OK] {name}: {date_val} | {note}\n")
            f.write("\n")

        if still_ambiguous:
            f.write("--- STILL AMBIGUOUS / NO MATCHING TEXT ---\n")
            for name, date_val, note in still_ambiguous:
                f.write(f"[?] {name}: {date_val} | {note}\n")

    print(f"Detailed audit report saved to: {output_file.absolute()}")


if __name__ == "__main__":
    target_dir = Path(__file__).parent.parent / "datasets" / "data-all" / "labels"

    if not target_dir.exists():
        target_dir = Path(
            r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\analyze_data_invoice\datasets\data-all\labels"
        )

    audit_ambiguous_dates(target_dir)
