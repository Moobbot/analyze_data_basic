import os
import shutil
import config
import utils

def copy_files():
    # Create destination directories
    utils.ensure_dir_exists(config.DEST_MISSING)
    utils.ensure_dir_exists(config.DEST_DOCX)

    dataset_map = utils.get_files_map(config.DATASET_DIR)
    label_map = utils.get_files_map(config.LABEL_DIR)

    dataset_bases = set(dataset_map.keys())
    label_bases = set(label_map.keys())

    # 1. Identify Missing Files (In Dataset but NOT in Label)
    missing_bases = dataset_bases - label_bases
    count_missing_moved = 0

    print(f"Found {len(missing_bases)} missing basenames.")

    for base in missing_bases:
        for filename in dataset_map[base]:
            src = os.path.join(config.DATASET_DIR, filename)
            dst = os.path.join(config.DEST_MISSING, filename)
            try:
                if os.path.exists(dst):
                    # If already copied in previous step, just delete source
                    os.remove(src)
                else:
                    shutil.move(src, dst)
                count_missing_moved += 1
            except Exception as e:
                print(f"Error moving {filename}: {e}")

    # 2. Identify DOCX Files in Dataset
    count_docx_moved = 0
    for base, files in dataset_map.items():
        for filename in files:
            if filename.lower().endswith('.docx'):
                src = os.path.join(config.DATASET_DIR, filename)
                dst = os.path.join(config.DEST_DOCX, filename)
                
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
                    print(f"Error moving {filename}: {e}")

    print("-" * 50)
    print(f"Process Complete.")
    print(f"1. Moved {count_missing_moved} missing files to:\n   {config.DEST_MISSING}")
    print(f"2. Moved {count_docx_moved} .docx files to:\n   {config.DEST_DOCX}")

if __name__ == "__main__":
    copy_files()
