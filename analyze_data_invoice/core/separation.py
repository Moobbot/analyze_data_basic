import os
import shutil
import config
from common_lib import file_utils


def copy_files():
    # Create destination directories
    config.DEST_MISSING.mkdir(parents=True, exist_ok=True)
    config.DEST_DOCX.mkdir(parents=True, exist_ok=True)
    config.DEST_LABEL_MISSING_PDF.mkdir(parents=True, exist_ok=True)

    print("Scanning files recursively...")
    dataset_map = file_utils.get_files_map_recursive(config.DATASET_DIR)
    label_map = file_utils.get_files_map_recursive(config.LABEL_DIR)

    dataset_bases = set(dataset_map.keys())
    label_bases = set(label_map.keys())

    # Pre-calculate specific bases
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
    missing_bases = dataset_bases - label_json_bases
    count_missing_moved = 0

    print(
        f"Found {len(missing_bases)} missing basenames (in Dataset but not in Label)."
    )

    for base in missing_bases:
        for rel_filename in dataset_map[base]:
            src = config.DATASET_DIR / rel_filename
            dst = config.DEST_MISSING / rel_filename
            dst.parent.mkdir(parents=True, exist_ok=True)
            try:
                if dst.exists():
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
                src = config.DATASET_DIR / rel_filename
                dst = config.DEST_DOCX / rel_filename
                dst.parent.mkdir(parents=True, exist_ok=True)

                if not src.exists():
                    continue

                try:
                    if dst.exists():
                        os.remove(src)
                    else:
                        shutil.move(src, dst)
                    count_docx_moved += 1
                except Exception as e:
                    print(f"Error moving {rel_filename}: {e}")

    # 3. Identify Missing PDFs (In Label but NOT in Dataset)
    missing_pdf_bases = label_json_bases - dataset_pdf_bases
    count_label_missing_pdf = 0

    print(f"Found {len(missing_pdf_bases)} labels missing PDFs.")

    for base in missing_pdf_bases:
        for rel_filename in label_map[base]:
            src = config.LABEL_DIR / rel_filename
            dst = config.DEST_LABEL_MISSING_PDF / rel_filename
            dst.parent.mkdir(parents=True, exist_ok=True)
            try:
                if dst.exists():
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
