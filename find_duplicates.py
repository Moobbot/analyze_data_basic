import os
import json
import hashlib
import shutil
import config
import utils

# Output directories for duplicates
DUPLICATE_DIR = os.path.join(config.BASE_DIR, "output_analyze", "duplicates")
DUPLICATE_LABELS_DIR = os.path.join(DUPLICATE_DIR, "labels")
DUPLICATE_FILES_DIR = os.path.join(DUPLICATE_DIR, "files")


def get_json_content_hash(json_path):
    """
    Read JSON, parse it, dump it with sorted keys to ensure canonical representation,
    and return MD5 hash.
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Dump with sort_keys=True to ensure key order doesn't affect hash
        # indent=0 to ignore whitespace differences if we were reading text,
        # but since we parse and dump, formatting is normalized.
        canonical_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(canonical_str.encode("utf-8")).hexdigest()
    except Exception as e:
        print(f"Error processing {json_path}: {e}")
        return None


def find_and_move_duplicates():
    print(">>> STARTING DUPLICATE DETECTION")
    print(f"Scanning directory: {config.LABEL_DIR}")

    if not os.path.exists(config.LABEL_DIR):
        print(f"Error: Label directory not found: {config.LABEL_DIR}")
        return

    # Map: hash -> list of filenames
    content_map = {}

    json_files = [
        f for f in os.listdir(config.LABEL_DIR) if f.lower().endswith(".json")
    ]
    total_files = len(json_files)

    print(f"Found {total_files} JSON files. Calculating hashes...")

    for i, filename in enumerate(json_files):
        file_path = os.path.join(config.LABEL_DIR, filename)
        file_hash = get_json_content_hash(file_path)

        if file_hash:
            if file_hash not in content_map:
                content_map[file_hash] = []
            content_map[file_hash].append(filename)

        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{total_files} files...")

    # Identify duplicates
    duplicates = {k: v for k, v in content_map.items() if len(v) > 1}

    total_duplicates = sum(len(v) - 1 for v in duplicates.values())
    print(
        f"\nFound {len(duplicates)} groups of identical content, totaling {total_duplicates} duplicate files."
    )

    if total_duplicates == 0:
        print("No duplicates found.")
        return

    # Create duplicate directories
    utils.ensure_dir_exists(DUPLICATE_LABELS_DIR)
    utils.ensure_dir_exists(DUPLICATE_FILES_DIR)

    report_path = os.path.join(DUPLICATE_DIR, "duplicate_report.txt")

    moved_count = 0

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("BÁO CÁO CÁC FILE TRÙNG LẶP NỘI DUNG (DUPLICATE CONTENT REPORT)\n")
        f.write("=" * 70 + "\n")
        f.write(f"Tổng số nhóm trùng lặp: {len(duplicates)}\n")
        f.write(f"Tổng số file sẽ bị di chuyển: {total_duplicates}\n")
        f.write("=" * 70 + "\n\n")

        for file_hash, filenames in duplicates.items():
            # Sort filenames to ensure deterministic behavior (keep the first one alphabetically)
            filenames.sort()

            original = filenames[0]
            dupes = filenames[1:]

            f.write(f"Nhóm trùng lặp (Hash: {file_hash}):\n")
            f.write(f"   [GIỮ LẠI] {original}\n")

            for dupe_json in dupes:
                f.write(f"   [DI CHUYỂN] {dupe_json}\n")

                # Move JSON
                try:
                    src_json = os.path.join(config.LABEL_DIR, dupe_json)
                    dst_json = os.path.join(DUPLICATE_LABELS_DIR, dupe_json)
                    if os.path.exists(src_json):
                        shutil.move(src_json, dst_json)
                except Exception as e:
                    f.write(f"      -> Lỗi di chuyển JSON: {e}\n")

                # Move PDF
                try:
                    base_name = os.path.splitext(dupe_json)[0]
                    pdf_filename = base_name + ".pdf"

                    src_pdf = os.path.join(config.DATASET_DIR, pdf_filename)
                    dst_pdf = os.path.join(DUPLICATE_FILES_DIR, pdf_filename)

                    if os.path.exists(src_pdf):
                        shutil.move(src_pdf, dst_pdf)
                        f.write(f"      -> Đã di chuyển PDF: {pdf_filename}\n")
                    else:
                        f.write(f"      -> PDF không tồn tại: {pdf_filename}\n")
                except Exception as e:
                    f.write(f"      -> Lỗi di chuyển PDF: {e}\n")

                moved_count += 1
            f.write("-" * 50 + "\n")

    print(f"\nMoved {moved_count} duplicate files to: {DUPLICATE_DIR}")
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    find_and_move_duplicates()
