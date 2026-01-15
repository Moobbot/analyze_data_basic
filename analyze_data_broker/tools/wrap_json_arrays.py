import os
import json

folders = [
    "datasets/labels/Account_Statements",
    "datasets/labels/Contact_Note",
    "datasets/labels/Dividend",
    "datasets/labels/FX-FT",
    "datasets/labels/Others_Template",
    "datasets/labels/Others_Template/Interest_Payment",
    "datasets/labels/Others_Template/Credit_Advice",
    "datasets/labels/Others_Template/Deposit",
]

for folder in folders:
    folder_name = os.path.basename(folder)
    if not os.path.exists(folder):
        print(f"{folder_name}: NOT FOUND")
        continue

    fixed_count = 0
    already_array = 0
    errors = []

    json_files = [f for f in os.listdir(folder) if f.endswith(".json")]

    for filename in json_files:
        filepath = os.path.join(folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if content.startswith("["):
            already_array += 1
            continue

        if content.startswith("{"):
            try:
                obj = json.loads(content)
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump([obj], f, indent=4, ensure_ascii=False)
                fixed_count += 1
            except json.JSONDecodeError as e:
                errors.append(filename)

    err_str = f", Errors: {len(errors)}" if errors else ""
    print(f"{folder_name}: Fixed={fixed_count}, Already[]={already_array}{err_str}")
