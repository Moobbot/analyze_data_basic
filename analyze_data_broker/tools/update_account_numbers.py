import os
import re
import json
import sys

# Add parent directory to path to allow importing config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Define paths (using config if possible, but hardcoding for specificity based on user prompt context)
TEXT_DIR = os.path.join(
    config.BASE_DIR, "output_analyze", "datasets", "extracted_text", "Contact_Note"
)
JSON_DIR = os.path.join(config.BASE_DIR, "datasets", "labels", "Contact_Note")
LOG_FILE = os.path.join(config.BASE_DIR, "account_update_log.txt")


def update_account_numbers():
    print(f"Scanning text files in: {TEXT_DIR}")
    print(f"Updating JSON files in: {JSON_DIR}")

    updated_count = 0
    log_entries = []

    if not os.path.exists(TEXT_DIR):
        print(f"Error: Text directory not found: {TEXT_DIR}")
        return

    files = os.listdir(TEXT_DIR)

    # Regex details:
    # "To the debit of account" literal
    # \s+ matches one or more whitespace (including newlines)
    # (\d+) captures the first part (e.g., 0546)
    # \s+ matches whitespace between parts (often a newline)
    # ([0-9A-Z\.]+) captures the second part (e.g., 00196118.03G)
    pattern = re.compile(
        r"To the debit of account\s+(\d+)\s+([0-9A-Z\.]+)", re.MULTILINE | re.IGNORECASE
    )

    for filename in files:
        if not filename.endswith(".txt"):
            continue

        file_id = filename.replace(".txt", "")
        text_path = os.path.join(TEXT_DIR, filename)
        json_filename = f"{file_id}.json"
        json_path = os.path.join(JSON_DIR, json_filename)

        # Read text content
        try:
            with open(text_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue

        # Search for pattern
        match = pattern.search(content)
        if match:
            part1 = match.group(1)
            part2 = match.group(2)
            account_no = f"{part1} {part2}"

            # Update JSON if exists
            if os.path.exists(json_path):
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    old_account = data.get("Account no.")

                    # Update the field
                    data["Account no."] = account_no

                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)

                    log_entry = f"{file_id}: Updated 'Account no.' from '{old_account}' to '{account_no}'"
                    log_entries.append(log_entry)
                    updated_count += 1
                    # print(log_entry)
                except Exception as e:
                    print(f"Error updating {json_filename}: {e}")
            else:
                log_entries.append(
                    f"{file_id}: JSON file not found for extracted match '{account_no}'"
                )
        else:
            # print(f"{file_id}: Pattern not found")
            pass

    # Write log file
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"Total files updated: {updated_count}\n")
        f.write("-" * 40 + "\n")
        f.write("\n".join(log_entries))

    print(f"Finished. Total updated: {updated_count}")
    print(f"Log saved to: {LOG_FILE}")


if __name__ == "__main__":
    update_account_numbers()
