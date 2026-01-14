import json
import os
import math


def filter_tax_anomalies(root_dir):
    matches = []

    print(f"Scanning directory: {root_dir}")
    print("-" * 30)

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if not file.endswith(".json"):
                continue

            file_path = os.path.join(root, file)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                # print(f"Error reading {file}: {e}")
                continue

            if isinstance(data, dict):
                descriptions = data.get("Description", [])
            elif isinstance(data, list):
                descriptions = data
            else:
                descriptions = []

            if not isinstance(descriptions, list):
                descriptions = []

            for i, item in enumerate(descriptions):
                # Condition 1: Tax fields are null
                tax_amount = item.get("Tax amount")
                tax_type = item.get("Tax type")
                tax_amount_sgd = item.get("Tax amount in SGD")

                cond1 = (
                    (tax_amount is None)
                    or (tax_type is None)
                    or (tax_amount_sgd is None)
                )

                # Condition 2: Amount has value (not None)
                amount_after_gst = item.get("Amount (after GST)")
                amount_after_tax_sgd = item.get("Amount after tax in SGD")

                cond2 = (amount_after_gst is not None) or (
                    amount_after_tax_sgd is not None
                )

                if cond1 and cond2:
                    print(f"[MATCH] File: {os.path.basename(file_path)} (Item {i})")
                    print(f"  Tax amount: {tax_amount}")
                    print(f"  Tax type: {tax_type}")
                    print(f"  Tax amount in SGD: {tax_amount_sgd}")
                    print(f"  Amount (after GST): {amount_after_gst}")
                    matches.append((file_path, i, item))

    print("-" * 30)
    if matches:
        print(f"Total matching cases found: {len(matches)}")
    else:
        print("No matching cases found.")


if __name__ == "__main__":
    # Scan the labels directory
    root_dir = r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\analyze_data_invoice\datasets\data-muti-page\labels"
    filter_tax_anomalies(root_dir)
