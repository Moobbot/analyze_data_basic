import os
import json

folders = [
    r"d:\Work\Clients\AIRC\product\ACPA\check_data_table\datasets\labels\Account_Statements",
    r"d:\Work\Clients\AIRC\product\ACPA\check_data_table\datasets\labels\Contact_Note",
    r"d:\Work\Clients\AIRC\product\ACPA\check_data_table\datasets\labels\Contact_Note_backup",
    r"d:\Work\Clients\AIRC\product\ACPA\check_data_table\datasets\labels\Dividend",
    r"d:\Work\Clients\AIRC\product\ACPA\check_data_table\datasets\labels\FX-FT",
    r"d:\Work\Clients\AIRC\product\ACPA\check_data_table\datasets\labels\Others_Template",
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
