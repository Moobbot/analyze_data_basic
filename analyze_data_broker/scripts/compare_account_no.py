import os
import json
import argparse
import shutil

LABEL_DIR = r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\analyze_data_broker\datasets\labels\Contact_Note"


def main(output_dir=None):
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    files = [f for f in os.listdir(LABEL_DIR) if f.endswith('.json')]

    total_files = 0
    match_files = []
    mismatch_files = []
    missing_keys_files = []

    print(f"{'Filename':<15} | {'Account no.':<30} | {'account_0':<30} | Match")
    print("-" * 90)

    for filename in files:
        file_path = os.path.join(LABEL_DIR, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Helper to handle list or dict
            if isinstance(data, list) and len(data) > 0:
                item = data[0]
            elif isinstance(data, dict):
                item = data
            else:
                continue

            total_files += 1

            acct_no = item.get('Account no.', '').strip(
            ) if item.get('Account no.') else None
            # Handle potential trailing dot key from previous context or extraction issues
            acct_0 = item.get('account_0', '').strip(
            ) if item.get('account_0.') else None
            if not acct_0:
                acct_0 = item.get('account_0', '').strip(
                ) if item.get('account_0') else None

            is_match = "MISSING"
            if acct_no is not None and acct_0 is not None:
                if acct_no == acct_0:
                    match_files.append(filename)
                    is_match = "YES"
                    if output_dir:
                        dest_path = os.path.join(output_dir, filename)
                        shutil.copy2(file_path, dest_path)
                else:
                    mismatch_files.append(filename)
                    is_match = "NO"
            else:
                missing_keys_files.append(filename)
                is_match = "MISSING"

            # debug print for first 5
            if total_files <= 5:
                print(
                    f"{filename:<15} | {str(acct_no):<30} | {str(acct_0):<30} | {is_match}")

        except Exception as e:
            print(f"Error reading {filename}: {e}")

    print("-" * 90)
    print(f"Total Files Checked: {total_files}")
    print(f"Exact Matches: {len(match_files)}")
    print(f"Mismatches: {len(mismatch_files)}")
    print(f"Missing Fields: {len(missing_keys_files)}")

    if output_dir:
        print(f"\nCopied {len(match_files)} matching files to: {output_dir}")

    if match_files:
        print("\nFiles with Exact Match:")
        for f in match_files:
            print(f" - {f}")
    else:
        print("\nNo exact matches found.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare account numbers and optionally copy matches.")
    parser.add_argument(
        "--output_dir", help="Directory to copy matching files to.")
    args = parser.parse_args()
    main(args.output_dir)
