import os
import json
from collections import defaultdict

# Config
DATA_DIR = r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\analyze_data_invoice\datasets\test-set-100-multipage\labels"


def get_customer(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                if len(data) > 0 and isinstance(data[0], dict):
                    return data[0].get("Customer", "Unknown")
                else:
                    return "Unknown"
            elif isinstance(data, dict):
                return data.get("Customer", "Unknown")
            else:
                return "Unknown"
    except:
        return "Error"


def main():
    print("Checking test set distribution...")
    files_by_customer = defaultdict(list)

    file_count = 0
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.lower().endswith(".json"):
                path = os.path.join(root, file)
                customer = get_customer(path)
                files_by_customer[customer].append(file)
                file_count += 1

    print(f"Total files: {file_count}")
    print(f"Total customers: {len(files_by_customer)}")

    # Sort by count desc
    sorted_customers = sorted(
        files_by_customer.items(), key=lambda x: len(x[1]), reverse=True
    )

    print("Distribution:")
    for c, files in sorted_customers:
        print(f"  - {c}: {len(files)}")


if __name__ == "__main__":
    main()
