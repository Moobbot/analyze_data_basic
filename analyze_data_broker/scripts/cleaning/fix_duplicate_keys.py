import re
import os
import glob

# Correct path to the folder
folder_path = "datasets/labels/Trade_Confirmation"


def fix_duplicate_keys_in_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        key_pattern = re.compile(r'\s*"([^"]+)"\s*:')

        # First pass: count non-null occurrences for each key
        key_counts = {}

        for line in lines:
            match = key_pattern.match(line)
            if match:
                key = match.group(1)
                # Check for null value (rudimentary check)
                parts = line.split(":", 1)
                if len(parts) > 1:
                    is_null = "null" in parts[1]
                else:
                    is_null = False  # Should not happen for valid key: value line

                if key not in key_counts:
                    key_counts[key] = {"null": 0, "value": 0}

                if is_null:
                    key_counts[key]["null"] += 1
                else:
                    key_counts[key]["value"] += 1

        # Second pass: write only lines that should be kept
        changed = False
        for line in lines:
            match = key_pattern.match(line)
            if match:
                key = match.group(1)
                parts = line.split(":", 1)
                if len(parts) > 1:
                    is_null = "null" in parts[1]
                else:
                    is_null = False

                # If valid value exists, skip nulls
                if is_null and key_counts[key]["value"] > 0:
                    # print(f"  Removing duplicate null key: {key} in {os.path.basename(file_path)}")
                    changed = True
                    continue

            new_lines.append(line)

        if changed:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            print(f"Fixed duplicates in {os.path.basename(file_path)}")
        # else:
        # print(f"No duplicates found in {os.path.basename(file_path)}")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")


def process_folder(folder):
    if not os.path.exists(folder):
        print(f"Folder not found: {folder}")
        return

    json_files = glob.glob(os.path.join(glob.escape(folder), "*.json"))
    print(f"Found {len(json_files)} JSON files in {folder}")

    for json_file in json_files:
        fix_duplicate_keys_in_file(json_file)


if __name__ == "__main__":
    process_folder(folder_path)
