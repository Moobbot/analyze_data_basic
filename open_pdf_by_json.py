import os
import sys
import config


def open_file_default(file_path):
    # Ensure absolute path and correct separators for Windows
    abs_path = os.path.abspath(file_path)
    abs_path = os.path.normpath(abs_path)

    print(f"Opening file: {abs_path}")

    try:
        if sys.platform == "win32":
            os.startfile(abs_path)
        elif sys.platform == "darwin":
            os.system(f'open "{abs_path}"')
        else:
            os.system(f'xdg-open "{abs_path}"')
    except Exception as e:
        print(f"Error opening file: {e}")


def find_and_open_files(json_path):
    # 1. Open the JSON file itself
    if os.path.exists(json_path):
        open_file_default(json_path)
    else:
        print(f"Error: JSON file not found at {json_path}")
        return

    # 2. Find and open the corresponding PDF
    base_name = os.path.splitext(os.path.basename(json_path))[0]
    dataset_dir = config.DATASET_DIR
    print(f"Searching for PDF for '{base_name}' in: {dataset_dir}")

    pdf_path = None

    # Recursively search for the PDF file
    if os.path.exists(dataset_dir):
        for root, dirs, files in os.walk(dataset_dir):
            for file in files:
                if file.lower().endswith(".pdf"):
                    file_base = os.path.splitext(file)[0]
                    if file_base == base_name:
                        pdf_path = os.path.join(root, file)
                        break
            if pdf_path:
                break
    else:
        print(f"Error: Dataset directory not found: {dataset_dir}")

    if pdf_path:
        print(f"Found PDF: {pdf_path}")
        open_file_default(pdf_path)
    else:
        print(
            f"Error: Could not find corresponding PDF for '{base_name}' in {dataset_dir}"
        )

    # 3. Open the corresponding text file in output_analyze/Extracted_Text_data_1
    txt_filename = base_name + ".txt"
    # Assuming output_analyze is relative to the script's directory or current working directory
    # We can use os.getcwd() or relative to this script file if needed.
    # For now, let's try relative to CWD as the user usually runs from root of project.
    # Or better, relative to the script's location.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    txt_path = os.path.join(
        script_dir, "output_analyze", "Extracted_Text_data_1", txt_filename
    )

    if os.path.exists(txt_path):
        open_file_default(txt_path)
    else:
        print(f"Warning: Text file not found at {txt_path}")


if __name__ == "__main__":
    # Default values compatible with user's typical usage pattern
    json_input_dir = "Datasets_edit-2025-12-23-Hoang/Data"

    # List of files to process if no command line args are given
    default_file_list = [
        "2025-GCP-012 - Daytona Investments Pte Ltd.json",
        "2025-GCP-017 & 2025-GCP-018 - GIAPL (SGD) (Details).json",
    ]

    files_to_process = []

    # If command line arguments are provided, use them as the list
    if len(sys.argv) > 1:
        files_to_process = sys.argv[1:]
    else:
        # Otherwise use the default list and prepend the directory
        files_to_process = [
            os.path.join(json_input_dir, f) if not os.path.dirname(f) else f
            for f in default_file_list
        ]

    for link_f in files_to_process:
        print(f"\n--- Opening set for: {link_f} ---")
        find_and_open_files(link_f)

# python open_pdf_by_json.py "Datasets_edit-2025-12-23-Hoang/Data/2022.02 -  Invoice-ARA-FLO29367.json"
