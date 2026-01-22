import os
import json
import sys


def patch_net_consideration(directory_path):
    """
    Backfills 'Net Consideration' with value from 'Foreign Net Consideration'
    if 'Net Consideration' is null/empty and 'Foreign Net Consideration' has a value.
    """
    print("=" * 80)
    print("PATCHING NET CONSIDERATION")
    print("=" * 80)

    if not os.path.exists(directory_path):
        print(f"Directory not found: {directory_path}")
        return

    json_files = [f for f in os.listdir(directory_path) if f.endswith(".json")]
    print(f"Total files to process: {len(json_files)}")

    modified_count = 0

    for filename in json_files:
        filepath = os.path.join(directory_path, filename)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = json.load(f)

            # Handle list vs dict
            if isinstance(content, list):
                if not content:
                    continue
                data = content[0]
                is_list = True
            else:
                data = content
                is_list = False

            if not isinstance(data, dict):
                continue

            # Check fields (case-insensitive keys not strictly needed if we assume standard schema,
            # but safer to find exact key casing if present)

            # Helper to find key
            def find_key(d, key_name):
                for k in d.keys():
                    if k.lower() == key_name.lower():
                        return k
                return None

            net_key = find_key(data, "Net Consideration")
            foreign_key = find_key(data, "Foreign Net Consideration")

            modified = False

            if net_key and foreign_key:
                net_val = data[net_key]
                foreign_val = data[foreign_key]

                # Check condition: Net is None/Empty and Foreign is NOT None/Empty
                if (net_val is None or str(net_val).strip() == "") and (
                    foreign_val is not None and str(foreign_val).strip() != ""
                ):

                    data[net_key] = foreign_val
                    modified = True
                    print(f"[{filename}] Updated {net_key} with value: {foreign_val}")

            if modified:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(content, f, indent=4, ensure_ascii=False)
                modified_count += 1

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print("-" * 80)
    print(f"Total files updated: {modified_count}")
    print("=" * 80)


if __name__ == "__main__":
    target_dir = r"datasets/labels/Contact_Note"
    # Allow command line arg override
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]

    patch_net_consideration(target_dir)
