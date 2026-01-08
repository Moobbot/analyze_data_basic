import os
import json
import pandas as pd
import glob

# Configuration
DATA_DIR = r"d:\Work\Clients\AIRC\product\ACPA\check_data_table\datasets\labels\Trade_Confirmation"
OUTPUT_FILE = r"d:\Work\Clients\AIRC\product\ACPA\check_data_table\merged_trade_confirmations.xlsx"

# List of columns based on the user's request
COLUMNS = [
    "Client name",
    "Account no.",
    "Name/ Security",
    "Securities ID",
    "Currency",
    "Transaction Type",
    "Trade Date",
    "Settlement Date",
    "Quantity",
    "Foreign Unit Price",
    "Foreign Gross Consideration",
    "Accrued Interest",
    "Foreign Net Consideration",
    "Net Consideration",
    "Exec Commission",
    "Research Commission",
    "Total Commission",
    "Local Fee",
    "Local Tax",
    "Stamp Duty",
    "Foreign GST",
    "GST Equivalent",
    "GST ON (SR)",
]


def process_json_files():
    data_list = []

    # Get all json files in the directory
    json_files = glob.glob(os.path.join(DATA_DIR, "*.json"))

    print(f"Found {len(json_files)} JSON files in {DATA_DIR}")

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                content = json.load(f)

                if isinstance(content, list):
                    for item in content:
                        filtered_data = {col: item.get(col, None) for col in COLUMNS}
                        data_list.append(filtered_data)
                elif isinstance(content, dict):
                    # Filter only the requested columns, handle missing keys gracefully
                    filtered_data = {col: content.get(col, None) for col in COLUMNS}
                    data_list.append(filtered_data)
                else:
                    print(f"Skipping {json_file}: Content is not list or dict")
        except Exception as e:
            print(f"Error processing {json_file}: {e}")

    if data_list:
        df = pd.DataFrame(data_list)

        # Ensure columns are in the requested order
        df = df[COLUMNS]

        try:
            df.to_excel(OUTPUT_FILE, index=False)
            print(f"Successfully created {OUTPUT_FILE}")
            print(df.head())
        except Exception as e:
            print(f"Error writing to Excel: {e}")
    else:
        print("No data found to write.")


if __name__ == "__main__":
    process_json_files()
