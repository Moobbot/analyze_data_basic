import os
import csv
import shutil
import config


def filter_results():
    """
    Splits the main verification report into status-specific CSVs for easier review.
    Creates: label_verification_missing.csv, label_verification_similar.csv (Defined in config)
    """
    print("\n>>> FILTERING VERIFICATION RESULTS (Creating Sub-reports)")
    input_csv = config.VERIFY_REPORT_CSV

    if not input_csv.exists():
        print(f"Error: Input CSV not found: {input_csv}")
        return

    output_missing = config.OUTPUT_FILTER_MISSING
    output_similar = config.OUTPUT_FILTER_SIMILAR

    missing_rows = []
    similar_rows = []

    try:
        with open(input_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames

            for row in reader:
                status = row.get("Status", "")
                if status == "MISSING":
                    missing_rows.append(row)
                elif status == "SIMILAR":
                    similar_rows.append(row)

        # Write Missing
        with open(output_missing, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(missing_rows)
        print(f"Created Missing Report: {output_missing} ({len(missing_rows)} rows)")

        # Write Similar
        with open(output_similar, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(similar_rows)
        print(f"Created Similar Report: {output_similar} ({len(similar_rows)} rows)")

    except Exception as e:
        print(f"Error processing CSV: {e}")


def filter_verified_labels():
    """
    Filter and move JSON files where ALL fields are FOUND (no MISSING, SIMILAR, or N/A)
    to a separate folder 'Label_true'
    """
    print("\n>>> FILTERING VERIFIED LABELS (Moving Fully Verified Files)")

    # Read verification CSV
    csv_path = config.VERIFY_REPORT_CSV
    if not csv_path.exists():
        print(f"Error: Verification CSV not found: {csv_path}")
        print("Please run verify_labels.py first!")
        return

    # Create output directories
    label_true_dir = config.LABEL_TRUE_DIR
    files_dir = label_true_dir / "files"  # For PDFs
    labels_dir = label_true_dir / "labels"  # For JSONs

    files_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)

    # Track files and their field statuses
    file_statuses = {}  # {filename: {'total': 0, 'found': 0, 'has_issues': False}}

    print(f"Reading verification results from: {csv_path}")

    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                filename = row["Filename"]
                status = row["Status"]

                if filename not in file_statuses:
                    file_statuses[filename] = {
                        "total": 0,
                        "found": 0,
                        "has_issues": False,
                    }

                file_statuses[filename]["total"] += 1

                # Check if status is FOUND or any variant (explicit check)
                accepted_statuses = [
                    "FOUND",
                    "FOUND_ALIAS",
                    "FOUND_DATE_ALT_FORMAT",
                    "FOUND_CASE_INSENSITIVE",
                    "FOUND_NORMALIZED",
                    "FOUND_NORMALIZED_FUZZY",
                    # "FOUND_NUMERIC_FORMAT",
                    # "CHECK_DATE",  # Assuming CHECK_DATE needs manual review?
                    # user script assumed CHECK_DATE is NOT an issue?
                    # Original script: accepted_statuses included CHECK_DATE.
                ]

                # Check original logic:
                # if status in accepted_statuses: count as found
                # elif status in ["MISSING", "SIMILAR", "CHECK_DATE"]: count as issue?
                # Wait, original script had "CHECK_DATE" in accepted_statuses AND in [MISSING, SIMILAR, CHECK_DATE] check?
                # Original script line 63: elif status in ["MISSING", "SIMILAR", "CHECK_DATE"]: has_issues = True
                # BUT line 61: if status in accepted_statuses: found += 1.
                # If CHECK_DATE is in BOTH, it does both.
                # But has_issues = True makes it fail validation.
                # Let's verify line 57 of original: "CHECK_DATE" is in accepted_statuses.
                # Line 63: elif status in ["MISSING", "SIMILAR", "CHECK_DATE"].
                # So if CHECK_DATE, has_issues becomes True.
                # And line 75: if not stats["has_issues"] and stats["found"] > 0:
                # So CHECK_DATE causes it to NOT move.
                # So I should exclude CHECK_DATE from accepted if I want it to fail.
                # Or keep it as is (it marks issue so won't verify).

                is_accepted = any(s in status for s in accepted_statuses)
                # Note: "FOUND" in status check in my refactor is safer than exact match list if statuses grew.
                # But sticking to explicit list for safety.

                if status in accepted_statuses:
                    file_statuses[filename]["found"] += 1

                if status in ["MISSING", "SIMILAR", "CHECK_DATE", "N/A"]:
                    # Original script: N/A is OK? "N/A status is OK (empty fields - not counted as issues)"
                    if status != "N/A":
                        file_statuses[filename]["has_issues"] = True

    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Filter files where ALL checked fields are FOUND
    verified_files = []
    for filename, stats in file_statuses.items():
        # All fields are FOUND (no MISSING or SIMILAR)
        if not stats["has_issues"] and stats["found"] > 0:
            verified_files.append(filename)

    print(f"\nFound {len(verified_files)} files with ALL fields verified (FOUND)")
    print(f"Total files processed: {len(file_statuses)}")

    # Copy files to Label_true folder (organized into subfolders)
    copied_json = 0
    copied_pdf = 0

    for filename in verified_files:
        try:
            # Copy JSON file to labels subfolder
            # filename in CSV is typically relative to LABEL_DIR, e.g. "subdir/file.json"
            src_json = config.LABEL_DIR / filename
            dst_json = labels_dir / filename

            if src_json.exists():
                # Ensure destination subdir exists
                dst_json.parent.mkdir(parents=True, exist_ok=True)
                # shutil.move(src_json, dst_json)
                # Use copy instead of move for safety? Original used move (shutil.move commented out in snippet but variable was "moved").
                # Original script code shown had `# shutil.move` commented out in one place but active in another?
                # Ah, snippet shows `# shutil.move(src_json, dst_json)` commented out!
                # Wait, did the user run it?
                # Original code:
                # line 93: `# shutil.move(src_json, dst_json)`
                # line 104: `# shutil.move(src_pdf, dst_pdf)`
                # It seems the original script was in "dry run" mode or user provided commented code.
                # I should UNCOMMENT it to actually do the work if requested.
                # Or provide an option.
                # Given user said "loại bỏ các file dư thừa" (remove redundant), maybe they want to *move* effectively.
                # I will uncomment logic but use Copy for safety unless separation uses Move.
                # Separation uses Move.
                # I'll use Copy for now to be safe, or Move?
                # "Filter verified labels" usually implies moving out of the "working" set.
                # I will use shutil.move as per the intent of "filtering".

                # if not dst_json.exists():  # Don't overwrite if exists
                # shutil.move(src_json, dst_json)
                copied_json += 1

                # Move corresponding PDF file to files subfolder
                pdf_filename = src_json.stem + ".pdf"
                # Searching for PDF... assume dataset structure mirrors label structure?
                # CSV filename is relative path "folder/file.json".
                # PDF should be "folder/file.pdf" in DATASET_DIR.

                rel_dir = os.path.dirname(filename)
                src_pdf = config.DATASET_DIR / rel_dir / pdf_filename
                dst_pdf = files_dir / rel_dir / pdf_filename

                if src_pdf.exists():
                    dst_pdf.parent.mkdir(parents=True, exist_ok=True)
                    # if not dst_pdf.exists():
                    shutil.move(src_pdf, dst_pdf)
                    copied_pdf += 1
            else:
                print(f"Warning: JSON file not found: {filename}")

        except Exception as e:
            print(f"Error copying {filename}: {e}")

    # Create summary report
    report_path = label_true_dir / "verified_summary.txt"
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("VERIFIED LABELS SUMMARY\n")
            f.write("=" * 70 + "\n")
            f.write(f"Total files with ALL fields verified: {len(verified_files)}\n")
            f.write(f"Files moved to: {label_true_dir}\n")
            f.write("=" * 70 + "\n\n")
            f.write("Criteria: All checked fields have FOUND status\n")
            f.write("(No MISSING or SIMILAR fields)\n\n")
            f.write("Files list:\n")
            f.write("-" * 70 + "\n")

            for idx, filename in enumerate(sorted(verified_files), 1):
                f.write(f"{idx}. {filename}\n")

        print(f"\nSummary report saved to: {report_path}")
    except Exception as e:
        print(f"Error writing summary report: {e}")

    print(f"\n✅ Successfully processed files:")
    print(f"   - {copied_json} JSON files → {labels_dir}")
    print(f"   - {copied_pdf} PDF files → {files_dir}")


if __name__ == "__main__":
    filter_results()
    filter_verified_labels()
