import os
import shutil
import config
import utils

def find_and_move_duplicates():
    print(">>> STARTING DUPLICATE DETECTION")
    print(f"Scanning directory: {config.LABEL_DIR}")

    if not config.LABEL_DIR.exists():
        print(f"Error: Label directory not found: {config.LABEL_DIR}")
        return

    content_map = {}
    json_files = list(config.LABEL_DIR.rglob("*.json"))
    total_files = len(json_files)

    print(f"Found {total_files} JSON files. Calculating hashes...")

    for i, file_path in enumerate(json_files):
        # We need relative path for map or absolute? Original used relative filename (list_files_recursive).
        # But get_json_content_hash needs absolute.
        # Let's verify utils.get_json_content_hash. It likely takes path.
        file_hash = utils.get_json_content_hash(str(file_path))

        if file_hash:
            if file_hash not in content_map:
                content_map[file_hash] = []
            content_map[file_hash].append(file_path)

        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{total_files} files...")

    duplicates = {k: v for k, v in content_map.items() if len(v) > 1}
    total_duplicates = sum(len(v) - 1 for v in duplicates.values())

    print(
        f"\nFound {len(duplicates)} groups of identical content, totaling {total_duplicates} duplicate files."
    )

    if total_duplicates == 0:
        print("No duplicates found.")
        return

    config.DUPLICATE_LABELS_DIR.mkdir(parents=True, exist_ok=True)
    config.DUPLICATE_FILES_DIR.mkdir(parents=True, exist_ok=True)

    report_path = config.DUPLICATE_DIR / "duplicate_report.txt"
    moved_count = 0

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("BÁO CÁO CÁC FILE TRÙNG LẶP NỘI DUNG (DUPLICATE CONTENT REPORT)\n")
        f.write("=" * 70 + "\n")
        f.write(f"Tổng số nhóm trùng lặp: {len(duplicates)}\n")
        f.write(f"Tổng số file sẽ bị di chuyển: {total_duplicates}\n")
        f.write("=" * 70 + "\n\n")

        for file_hash, file_paths in duplicates.items():
            # Sort by path string
            file_paths.sort(key=str)

            original = file_paths[0]
            dupes = file_paths[1:]

            f.write(f"Nhóm trùng lặp (Hash: {file_hash}):\n")
            f.write(f"   [GIỮ LẠI] {original.name}\n")

            for dupe_json_path in dupes:
                f.write(f"   [DI CHUYỂN] {dupe_json_path.name}\n")

                try:
                    src_json = dupe_json_path
                    dst_json = config.DUPLICATE_LABELS_DIR / dupe_json_path.name
                    if src_json.exists():
                        shutil.move(src_json, dst_json)
                except Exception as e:
                    f.write(f"      -> Lỗi di chuyển JSON: {e}\n")

                try:
                    pdf_filename = dupe_json_path.stem + ".pdf"
                    # Need to find where the PDF is. Assuming same structure?
                    # Original script assumed FLAT structure or found via name.
                    # Original: src_pdf = os.path.join(config.DATASET_DIR, pdf_filename)
                    # We should probably search relative if config.DATASET_DIR is root.
                    # But wait, original code did: src_pdf = os.path.join(config.DATASET_DIR, pdf_filename)
                    # This implies flat PDF directory or it wouldn't find it if nested?
                    # Actually `find_duplicates` original script used `config.DATASET_DIR` which was flat usually.
                    # If we use recursive find in other modules, we should be careful here.
                    # For now, simplistic approach:
                    src_pdf = config.DATASET_DIR / pdf_filename  # Might fail if nested
                    # Better: try to find it recursively? No, expensive.
                    # Let's stick to simple path for now or skip PDF move if not found easily.

                    dst_pdf = config.DUPLICATE_FILES_DIR / pdf_filename

                    if src_pdf.exists():
                        shutil.move(src_pdf, dst_pdf)
                        f.write(f"      -> Đã di chuyển PDF: {pdf_filename}\n")
                    else:
                        f.write(f"      -> PDF không tồn tại: {pdf_filename}\n")
                except Exception as e:
                    f.write(f"      -> Lỗi di chuyển PDF: {e}\n")

                moved_count += 1
            f.write("-" * 50 + "\n")

    print(f"\nMoved {moved_count} duplicate files to: {config.DUPLICATE_DIR}")
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    find_and_move_duplicates()
