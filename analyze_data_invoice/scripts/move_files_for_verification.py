import os
import shutil
import sys

# Add parent directory to path to import config
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
# Add grandparent directory to path to import common_lib
sys.path.insert(0, os.path.dirname(parent_dir))

import config
from common_lib import file_utils

# Define the destination folder name
# Files will be moved to: <script_directory>/verification_needed
DESTINATION_FOLDER = "verification_needed"


def find_and_move_files(json_path):
    # Ensure absolute path and correct separators
    json_path = os.path.abspath(json_path)
    json_path = os.path.normpath(json_path)

    # Prepare destination directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dest_dir = os.path.join(script_dir, DESTINATION_FOLDER)

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Created destination directory: {dest_dir}")

    # 1. Move the JSON file itself
    if os.path.exists(json_path):
        print(f"Processing JSON: {json_path}")
        file_utils.move_file_safe(json_path, dest_dir)
    else:
        print(f"Error: JSON file not found at {json_path}")
        # We continue to try to find other files based on the name of the json input
        # assuming the filename without path is the key.

    # 2. Find and move the corresponding PDF
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
        file_utils.move_file_safe(pdf_path, dest_dir)
    else:
        print(
            f"Error: Could not find corresponding PDF for '{base_name}' in {dataset_dir}"
        )

    # 3. Move the corresponding text file in output_analyze/Extracted_Text_data_1
    txt_filename = base_name + ".txt"
    txt_path = os.path.join(
        script_dir, "output_analyze", "Extracted_Text_data_1", txt_filename
    )

    if os.path.exists(txt_path):
        print(f"Found TXT: {txt_path}")
        file_utils.move_file_safe(txt_path, dest_dir)
    else:
        print(f"Warning: Text file not found at {txt_path}")


if __name__ == "__main__":
    # Default values compatible with user's typical usage pattern
    json_input_dir = "datasets_edit-2025-12-23-Hoang/Data"

    # List of files to process if no command line args are given
    # You can add multiple filenames to this list
    default_file_list = []

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

    print(f"Processing {len(files_to_process)} files...")

    for link_f in files_to_process:
        print(f"\n--- Processing: {link_f} ---")
        find_and_move_files(link_f)
