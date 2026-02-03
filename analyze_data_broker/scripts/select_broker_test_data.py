import os
import shutil
import random

# Config
DATA_DIR = (
    r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\analyze_data_broker\datasets"
)
OUTPUT_DIR = r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\analyze_data_broker\datasets\test-set-broker"
LABELS_DIR = os.path.join(DATA_DIR, "labels")
FILES_DIR = os.path.join(DATA_DIR, "files")
TARGET_PER_TYPE = 20


def find_source_file(label_rel_path):
    # label_rel_path: Type/foo.json
    type_dir = os.path.dirname(label_rel_path)
    stem = os.path.splitext(os.path.basename(label_rel_path))[0]

    search_dir = os.path.join(FILES_DIR, type_dir)
    if not os.path.exists(search_dir):
        return None

    # Simple check for pdf first, then iterate
    pdf_path = os.path.join(search_dir, f"{stem}.pdf")
    if os.path.exists(pdf_path):
        return pdf_path

    for fname in os.listdir(search_dir):
        if os.path.splitext(fname)[0] == stem:
            return os.path.join(search_dir, fname)

    return None


def main():
    print("Selecting broker test data...")

    # Types are subdirectories in labels
    if not os.path.exists(LABELS_DIR):
        print("Labels dir not found.")
        return

    types = [
        d for d in os.listdir(LABELS_DIR) if os.path.isdir(os.path.join(LABELS_DIR, d))
    ]
    print(f"Found types: {types}")

    total_copied = 0

    if os.path.exists(OUTPUT_DIR):
        try:
            shutil.rmtree(OUTPUT_DIR)
        except Exception as e:
            print(f"Error cleaning output dir: {e}")

    for type_name in types:
        type_path = os.path.join(LABELS_DIR, type_name)
        files = [f for f in os.listdir(type_path) if f.lower().endswith(".json")]

        count_to_take = min(len(files), TARGET_PER_TYPE)
        selected_files = random.sample(files, count_to_take)

        print(
            f"Type '{type_name}': {len(files)} files found. Selecting {count_to_take}."
        )

        for f in selected_files:
            # Copy label
            src_label = os.path.join(type_path, f)
            rel_path = os.path.join(type_name, f)
            dest_label = os.path.join(OUTPUT_DIR, "labels", rel_path)

            os.makedirs(os.path.dirname(dest_label), exist_ok=True)
            shutil.copy2(src_label, dest_label)

            # Copy source
            src_file = find_source_file(rel_path)
            if src_file:
                # Calculate dest path for source
                file_rel_path = os.path.relpath(src_file, FILES_DIR)
                dest_file = os.path.join(OUTPUT_DIR, "files", file_rel_path)
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                shutil.copy2(src_file, dest_file)
            else:
                print(f"  Warning: No source file found for {rel_path}")

            total_copied += 1

    print(f"\nDone. Selected {total_copied} total files across {len(types)} types.")


if __name__ == "__main__":
    main()
