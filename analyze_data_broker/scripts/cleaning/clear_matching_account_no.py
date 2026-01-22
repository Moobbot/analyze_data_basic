import os
import json
import argparse

LABEL_DIR = r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\analyze_data_broker\datasets\labels\Contact_Note"


def main():
    files = [f for f in os.listdir(LABEL_DIR) if f.endswith('.json')]

    count_updated = 0

    print(f"Checking {len(files)} files in {LABEL_DIR}...")
    print("-" * 30)

    for filename in files:
        file_path = os.path.join(LABEL_DIR, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            updated = False
            # Handle list of objects
            if isinstance(data, list):
                for item in data:
                    acct_no = item.get('Account no.', '').strip(
                    ) if item.get('Account no.') else None

                    # Handle account_0 which might have a trailing dot key issue from previous steps
                    acct_0 = item.get('account_0', '').strip(
                    ) if item.get('account_0.') else None
                    if not acct_0:
                        acct_0 = item.get('account_0', '').strip(
                        ) if item.get('account_0') else None

                    # If they match, clear Account no.
                    if acct_no and acct_0 and acct_no == acct_0:
                        print(
                            f"Clearing Account no. in {filename} (Matched: {acct_no})")
                        item['Account no.'] = ""
                        updated = True

            elif isinstance(data, dict):
                # Handle single dict if exists
                item = data
                acct_no = item.get('Account no.', '').strip(
                ) if item.get('Account no.') else None
                acct_0 = item.get('account_0', '').strip(
                ) if item.get('account_0') else None

                if acct_no and acct_0 and acct_no == acct_0:
                    print(
                        f"Clearing Account no. in {filename} (Matched: {acct_no})")
                    item['Account no.'] = ""
                    updated = True

            if updated:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                count_updated += 1

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print("-" * 30)
    print(f"Total Files Updated: {count_updated}")


if __name__ == "__main__":
    main()
