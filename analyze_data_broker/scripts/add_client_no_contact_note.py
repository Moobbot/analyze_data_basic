import os
import json
import re
import argparse

# Paths
TEXT_DIR = r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\analyze_data_broker\output_analyze\datasets\extracted_text\Contact_Note"
LABEL_DIR = r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\analyze_data_broker\datasets\labels\Contact_Note"


def extract_account_no_from_header(text_file_path):
    """Extracts Account no. (original logic) from the text file."""
    try:
        with open(text_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            # Originally this was checking "Client no." or "Account no." depending on revisions
            # Let's keep looking for "Account no." lines as per previous user edits in this file
            if "Account no." in line:
                # Note: The user renamed the function to extract_account_no and changed target to "Account no."
                # But previously "Client no." mapped to account_0.
                # Let's preserve the logic that finds the line AFTER the label.
                if i + 1 < len(lines):
                    return lines[i+1].strip()
    except Exception as e:
        print(f"Error reading {text_file_path}: {e}")
    return None


def extract_account_no_from_body(text_file_path):
    """Extracts account number from 'of account' pattern."""
    try:
        if not os.path.exists(text_file_path):
            return None
        with open(text_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            if "of account" in line.lower():  # Case insensitive check
                match = re.search(r"of account\s+(.+)", line, re.IGNORECASE)
                if match:
                    raw_val = match.group(1).strip()
                    # Remove common currencies
                    raw_val = re.sub(
                        r"\s+(USD|SGD|HKD|EUR|GBP|AUD|JPY|CAD|CHF|CNY)$", "", raw_val, flags=re.IGNORECASE)
                    clean_val = raw_val.replace(" ", "")
                    return clean_val
    except Exception as e:
        print(f"Error reading text file {text_file_path}: {e}")
    return None


def update_label_file(json_file_path, account_0_val=None, account_no_val=None):
    """Updates the JSON label file."""
    try:
        if not os.path.exists(json_file_path):
            print(f"Label file not found: {json_file_path}")
            return False

        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        updated = False
        if isinstance(data, list):
            for item in data:
                if account_0_val:
                    item['account_0'] = account_0_val
                    updated = True

                if account_no_val:
                    if item.get('Account no.') != account_no_val:
                        item['Account no.'] = account_no_val
                        updated = True
        else:
            print(f"Unexpected JSON format in {json_file_path}")
            return False

        if updated:
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
    except Exception as e:
        print(f"Error updating {json_file_path}: {e}")
    return False


def main(target_file=None):
    files_to_process = []
    if target_file:
        files_to_process.append(target_file)
    else:
        files_to_process = [f for f in os.listdir(
            TEXT_DIR) if f.endswith('.txt')]

    count_updated = 0

    for filename in files_to_process:
        text_path = os.path.join(TEXT_DIR, filename)
        json_filename = filename.replace('.txt', '.json')
        json_path = os.path.join(LABEL_DIR, json_filename)

        # 1. Formatting extraction (often matches Client no / Account no in header) -> account_0
        # The user previously renamed extract_client_no to extract_account_no.
        # And mapped it to account_0.
        val_for_account_0 = extract_account_no_from_header(text_path)

        # 2. Body extraction (of account ...) -> Account no.
        val_for_account_no = extract_account_no_from_body(text_path)

        if val_for_account_0 or val_for_account_no:
            if update_label_file(json_path, account_0_val=val_for_account_0, account_no_val=val_for_account_no):
                print(f"Updated {json_filename}")
                count_updated += 1
            else:
                # If extraction worked but update failed (e.g. file missing)
                pass
        else:
            # print(f"No relevant data found in {filename}")
            pass

    print("-" * 30)
    print(f"Total Processed: {len(files_to_process)}")
    print(f"Files Updated: {count_updated}")
    print("-" * 30)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract and update account info in labels")
    parser.add_argument(
        "--file", help="Specific file to process (filename only, e.g. 0816.txt)")
    args = parser.parse_args()

    main(args.file)
