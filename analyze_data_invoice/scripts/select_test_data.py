import os
import json
import shutil
import random
from collections import defaultdict
from pathlib import Path

# Config
DATA_DIR = r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\analyze_data_invoice\datasets\data-muti-page"
OUTPUT_DIR = r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\analyze_data_invoice\datasets\test-set-100-multipage"
LABELS_DIR = os.path.join(DATA_DIR, "labels")
FILES_DIR = os.path.join(DATA_DIR, "files")
TARGET_COUNT = 100


def get_customer(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                if len(data) > 0 and isinstance(data[0], dict):
                    # Should we take the first one? Or merge?
                    # For now select based on the first one.
                    return data[0].get("Customer", "Unknown")
                else:
                    return "Unknown"
            elif isinstance(data, dict):
                return data.get("Customer", "Unknown")
            else:
                return "Unknown"
    except Exception as e:
        print(f"Error reading {json_path}: {e}")
        return "Error"


def find_source_file(json_path, labels_root, files_root):
    # json_path: .../labels/Cleanedge/foo.json
    # relative: Cleanedge/foo.json
    rel_path = os.path.relpath(json_path, labels_root)
    # rel_dir: Cleanedge
    rel_dir = os.path.dirname(rel_path)
    # stem: foo
    stem = os.path.splitext(os.path.basename(json_path))[0]

    search_dir = os.path.join(files_root, rel_dir)
    if not os.path.exists(search_dir):
        # Try finding in root of files_dir just in case? No, stay strict first.
        return None

    # Check for files with same stem
    for fname in os.listdir(search_dir):
        if os.path.splitext(fname)[0] == stem:
            return os.path.join(search_dir, fname)
    return None


def main():
    print("Scanning for label files...")
    files_by_customer = defaultdict(list)

    all_json_files = []
    if not os.path.exists(LABELS_DIR):
        print(f"Labels directory not found: {LABELS_DIR}")
        return

    for root, dirs, files in os.walk(LABELS_DIR):
        for file in files:
            if file.lower().endswith(".json"):
                path = os.path.join(root, file)
                all_json_files.append(path)

    print(f"Found {len(all_json_files)} JSON files.")

    for path in all_json_files:
        customer = get_customer(path)
        if isinstance(customer, str):
            customer = customer.strip()
        else:
            customer = "Unknown"

        if not customer:
            customer = "Unknown"
        files_by_customer[customer].append(path)

    customers = list(files_by_customer.keys())
    print(f"Found {len(customers)} unique customers.")
    # Sort for deterministic display
    customers.sort()

    print("Files per customer:")
    for c in customers:
        print(f"  - {c}: {len(files_by_customer[c])} files")

    # Selection Logic
    remaining_customers = customers[:]

    # Shuffle files per customer to get random sample
    for c in customers:
        random.shuffle(files_by_customer[c])

    allocation = {c: 0 for c in customers}
    total_selected = 0

    # Only try to balance if we have files
    if len(all_json_files) == 0:
        print("No files to select.")
        return

    while total_selected < TARGET_COUNT and remaining_customers:
        target_per_customer = (TARGET_COUNT - total_selected) // len(
            remaining_customers
        )
        if target_per_customer == 0:
            target_per_customer = 1

        progress_made = False
        to_remove = []

        # Iterate over a copy to allow modification if needed, but we modify remaining_customers outside
        for c in remaining_customers:
            if total_selected >= TARGET_COUNT:
                break

            count_to_take = target_per_customer
            available = len(files_by_customer[c]) - allocation[c]

            take = min(count_to_take, available)
            if take > 0:
                allocation[c] += take
                total_selected += take
                progress_made = True

            if allocation[c] == len(files_by_customer[c]):
                to_remove.append(c)

        for c in to_remove:
            if c in remaining_customers:
                remaining_customers.remove(c)

        if not progress_made and total_selected < TARGET_COUNT:
            break

    print(f"\nSelected {total_selected} files.")
    for c in customers:
        if allocation[c] > 0:
            print(f"  - {c}: {allocation[c]}")

    # Copy files
    if os.path.exists(OUTPUT_DIR):
        print(f"Cleaning output directory {OUTPUT_DIR}...")
        try:
            shutil.rmtree(OUTPUT_DIR)
        except Exception as e:
            print(f"Error cleaning output dir: {e}")

    print(f"Copying to {OUTPUT_DIR}...")

    count_files_copied = 0

    for c in customers:
        count = allocation[c]
        if count == 0:
            continue

        files_to_copy = files_by_customer[c][:count]
        for json_path in files_to_copy:
            # Destination paths
            rel_path = os.path.relpath(json_path, LABELS_DIR)
            dest_json = os.path.join(OUTPUT_DIR, "labels", rel_path)

            os.makedirs(os.path.dirname(dest_json), exist_ok=True)
            shutil.copy2(json_path, dest_json)

            # Source file
            src_path = find_source_file(json_path, LABELS_DIR, FILES_DIR)
            if src_path:
                rel_src = os.path.relpath(src_path, FILES_DIR)
                dest_src = os.path.join(OUTPUT_DIR, "files", rel_src)
                os.makedirs(os.path.dirname(dest_src), exist_ok=True)
                shutil.copy2(src_path, dest_src)
            else:
                print(f"Warning: No source file found for {json_path}")

            count_files_copied += 1

    print(
        f"Done. Copied {count_files_copied} label files (and their sources if found)."
    )


if __name__ == "__main__":
    main()
