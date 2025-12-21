import os
import csv
import shutil
import config


def filter_verified_labels():
    """
    Filter and move JSON files where ALL fields are FOUND (no MISSING, SIMILAR, or N/A)
    to a separate folder 'Label_true'
    """
    print(">>> FILTERING VERIFIED LABELS")

    # Read verification CSV
    csv_path = config.VERIFY_REPORT_CSV
    if not os.path.exists(csv_path):
        print(f"Error: Verification CSV not found: {csv_path}")
        print("Please run verify_labels.py first!")
        return

    # Create output directories
    label_true_dir = os.path.join(config.BASE_DIR, "Label_true")
    files_dir = os.path.join(label_true_dir, "files")  # For PDFs
    labels_dir = os.path.join(label_true_dir, "labels")  # For JSONs

    os.makedirs(files_dir, exist_ok=True)
    os.makedirs(labels_dir, exist_ok=True)

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
                    "FOUND_DATE_ALT_FORMAT",
                    "FOUND_CASE_INSENSITIVE",
                    "FOUND_NORMALIZED",
                    # "FOUND_NUMERIC_FORMAT",
                ]

                if status in accepted_statuses:
                    file_statuses[filename]["found"] += 1
                elif status in ["MISSING", "SIMILAR", "CHECK_DATE"]:
                    file_statuses[filename]["has_issues"] = True
                # N/A status is OK (empty fields - not counted as issues)

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
            src_json = os.path.join(config.LABEL_DIR, filename)
            dst_json = os.path.join(labels_dir, filename)

            if os.path.exists(src_json):
                shutil.move(src_json, dst_json)
                copied_json += 1

                # Copy corresponding PDF file to files subfolder
                base_name = os.path.splitext(filename)[0]
                pdf_filename = base_name + ".pdf"
                src_pdf = os.path.join(config.DATASET_DIR, pdf_filename)
                dst_pdf = os.path.join(files_dir, pdf_filename)

                if os.path.exists(src_pdf):
                    shutil.move(src_pdf, dst_pdf)
                    copied_pdf += 1
            else:
                print(f"Warning: JSON file not found: {filename}")

        except Exception as e:
            print(f"Error copying {filename}: {e}")

    # Create summary report
    report_path = os.path.join(label_true_dir, "verified_summary.txt")
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

    print(f"\n✅ Successfully moved files:")
    print(f"   - {copied_json} JSON files → {labels_dir}")
    print(f"   - {copied_pdf} PDF files → {files_dir}")
    print(f"\n📁 Folder structure:")
    print(f"   Label_true/")
    print(f"   ├── files/    ({copied_pdf} PDFs)")
    print(f"   └── labels/   ({copied_json} JSONs)")


if __name__ == "__main__":
    filter_verified_labels()
