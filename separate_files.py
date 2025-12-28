import os
import shutil
import config
import utils


def get_files_map_recursive(directory):
    files_map = {}
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return files_map

    for root, _, files in os.walk(directory):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, directory)
            # Use relative path without extension as key to match structure
            # e.g. "subdir/file1"
            base_name = os.path.splitext(rel_path)[0]

            if base_name not in files_map:
                files_map[base_name] = []
            files_map[base_name].append(rel_path)
    return files_map


def copy_files():
    # Create destination directories
    utils.ensure_dir_exists(config.DEST_MISSING)
    utils.ensure_dir_exists(config.DEST_DOCX)
    utils.ensure_dir_exists(config.DEST_LABEL_MISSING_PDF)

    print("Scanning files recursively...")
    dataset_map = get_files_map_recursive(config.DATASET_DIR)
    label_map = get_files_map_recursive(config.LABEL_DIR)

    dataset_bases = set(dataset_map.keys())
    label_bases = set(label_map.keys())

    # Pre-calculate specific bases for correct matching (Align with verify_labels.py)
    dataset_pdf_bases = {
        base
        for base, files in dataset_map.items()
        if any(f.lower().endswith(".pdf") for f in files)
    }
    label_json_bases = {
        base
        for base, files in label_map.items()
        if any(f.lower().endswith(".json") for f in files)
    }

    print(
        f"Total Dataset bases found: {len(dataset_bases)} (PDF bases: {len(dataset_pdf_bases)})"
    )
    print(
        f"Total Label bases found: {len(label_bases)} (JSON bases: {len(label_json_bases)})"
    )

    # 1. Identify Missing Files (In Dataset but NOT in Label)
    # Ensure they don't have matching JSON (strict check)
    missing_bases = dataset_bases - label_json_bases
    count_missing_moved = 0

    print(
        f"Found {len(missing_bases)} missing basenames (in Dataset but not in Label)."
    )

    for base in missing_bases:
        for rel_filename in dataset_map[base]:
            src = os.path.join(config.DATASET_DIR, rel_filename)
            # Flatten structure for destination or keep?
            # Original script flattened it: dst = os.path.join(config.DEST_MISSING, filename)
            # We will keep flattening but calculate basename from relative path
            dst_filename = os.path.basename(rel_filename)
            dst = os.path.join(config.DEST_MISSING, dst_filename)
            try:
                if os.path.exists(dst):
                    # If already copied in previous step, just delete source
                    os.remove(src)
                else:
                    shutil.move(src, dst)
                count_missing_moved += 1
            except Exception as e:
                print(f"Error moving {rel_filename}: {e}")

    # 2. Identify DOCX Files in Dataset
    count_docx_moved = 0
    for base, files in dataset_map.items():
        for rel_filename in files:
            if rel_filename.lower().endswith(".docx"):
                src = os.path.join(config.DATASET_DIR, rel_filename)
                dst_filename = os.path.basename(rel_filename)
                dst = os.path.join(config.DEST_DOCX, dst_filename)

                # Check if it's one of the missing ones we just moved?
                # If so, it won't exist in src anymore.
                if not os.path.exists(src):
                    continue

                try:
                    if os.path.exists(dst):
                        os.remove(src)
                    else:
                        shutil.move(src, dst)
                    count_docx_moved += 1
                except Exception as e:
                    print(f"Error moving {rel_filename}: {e}")

    # 3. Identify Missing PDFs (In Label but NOT in Dataset)
    # Strict check: Label exists (JSON) but PDF does not exist in Dataset
    missing_pdf_bases = label_json_bases - dataset_pdf_bases
    count_label_missing_pdf = 0

    print(f"Found {len(missing_pdf_bases)} labels missing PDFs.")

    for base in missing_pdf_bases:
        for rel_filename in label_map[base]:
            src = os.path.join(config.LABEL_DIR, rel_filename)
            dst_filename = os.path.basename(rel_filename)
            dst = os.path.join(config.DEST_LABEL_MISSING_PDF, dst_filename)
            try:
                if os.path.exists(dst):
                    os.remove(src)
                else:
                    shutil.move(src, dst)
                count_label_missing_pdf += 1
            except Exception as e:
                print(f"Error moving {rel_filename}: {e}")

    print("-" * 50)
    print(f"Process Complete.")
    print(f"1. Moved {count_missing_moved} missing files to:\n   {config.DEST_MISSING}")
    print(f"2. Moved {count_docx_moved} .docx files to:\n   {config.DEST_DOCX}")
    print(
        f"3. Moved {count_label_missing_pdf} labels missing PDFs to:\n   {config.DEST_LABEL_MISSING_PDF}"
    )


if __name__ == "__main__":
    copy_files()
