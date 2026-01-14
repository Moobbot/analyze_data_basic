import json
import os

# Use raw string for path to handle backslashes
file_path = r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\analyze_data_invoice\datasets\data-all\labels\data_1\[TO CANCEL] Theme International - Sphere Invoice INV-23100208[45].json"

if not os.path.exists(file_path):
    print(f"Error: File not found at {file_path}")
    exit(1)

try:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    old_date = data.get("Date")
    print(f"Found date: {old_date}")

    if old_date == "03/10/2023":
        data["Date"] = "10/03/2023"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Successfully updated date from {old_date} to 10/03/2023")
    else:
        print(f"Date was {old_date}, expected 03/10/2023. Not updating.")

except Exception as e:
    print(f"An error occurred: {e}")
