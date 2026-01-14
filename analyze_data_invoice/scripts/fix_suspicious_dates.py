import json
import re
from pathlib import Path


def fix_suspicious_dates():
    # Paths
    base_dir = Path(__file__).parent.parent
    audit_report = base_dir / "ambiguous_dates_audit.txt"
    labels_dir = base_dir / "datasets" / "data-all" / "labels"

    if not audit_report.exists():
        print(f"Error: Audit report not found at {audit_report}")
        return

    print(f"Reading report: {audit_report}")

    fixed_count = 0
    error_count = 0

    with open(audit_report, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Regex to parse the WARN line
    # [WARN] filename.json: 06/11/2025 | SUSPICIOUS: ...
    warn_pattern = re.compile(
        r"^\[WARN\]\s+(.+?\.json):\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s+\|"
    )

    for line in lines:
        if line.startswith("[WARN]"):
            match = warn_pattern.match(line)
            if match:
                filename = match.group(1).strip()
                date_str = match.group(2).strip()

                # Find the file
                # Since we don't know the subdirectory, we use rglob
                found_files = list(labels_dir.rglob(filename))

                if not found_files:
                    print(f"Warning: File not found for {filename}")
                    continue

                # Should essentially be unique, but take the first if duplicates (shouldn't happen in flat structure conceptually)
                file_path = found_files[0]

                try:
                    with open(file_path, "r", encoding="utf-8") as json_file:
                        data = json.load(json_file)

                    current_date = data.get("Date")

                    # Sanity check: Ensure the date in file matches the one in report
                    # Normalize separators for check
                    if current_date and current_date.replace(
                        "-", "/"
                    ) == date_str.replace("-", "/"):
                        # Perform the swap
                        parts = re.split(r"[/-]", current_date)
                        if len(parts) == 3:
                            v1, v2, y = parts
                            # Swap v1 and v2
                            new_date = f"{v2}/{v1}/{y}"

                            data["Date"] = new_date

                            # Write back
                            with open(file_path, "w", encoding="utf-8") as json_file:
                                json.dump(data, json_file, indent=4, ensure_ascii=False)

                            print(f"[FIXED] {filename}: {current_date} -> {new_date}")
                            fixed_count += 1
                        else:
                            print(
                                f"[SKIP] Invalid date format in {filename}: {current_date}"
                            )
                    else:
                        print(
                            f"[SKIP] Date mismatch in {filename}. Report: {date_str}, File: {current_date}"
                        )

                except Exception as e:
                    print(f"[ERROR] Failed to process {filename}: {e}")
                    error_count += 1

    print(f"\nProcessing complete.")
    print(f"Total Fixed: {fixed_count}")
    print(f"Errors: {error_count}")


if __name__ == "__main__":
    fix_suspicious_dates()
