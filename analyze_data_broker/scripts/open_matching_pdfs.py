import os
import argparse
import platform
import subprocess

# Default paths
MATCHED_JSON_DIR = r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\analyze_data_broker\datasets\labels\Contact_Note\matched_test_v2"
PDF_DIR = r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\analyze_data_broker\datasets\files\Contact_Note"


def open_file(path):
    """Opens a file with the default application."""
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.call(["open", path])
    else:
        subprocess.call(["xdg-open", path])


def main(matched_dir=MATCHED_JSON_DIR, pdf_dir=PDF_DIR):
    if not os.path.exists(matched_dir):
        print(f"Matched directory not found: {matched_dir}")
        return

    if not os.path.exists(pdf_dir):
        print(f"PDF directory not found: {pdf_dir}")
        return

    files = [f for f in os.listdir(matched_dir) if f.endswith('.json')]

    print(f"Found {len(files)} matching JSON files.")
    print(f"Attempting to open corresponding PDFs from: {pdf_dir}")
    print("-" * 30)

    opened_count = 0
    missing_count = 0

    for filename in files:
        # 0819.json -> 0819.pdf
        pdf_filename = filename.replace('.json', '.pdf')
        pdf_path = os.path.join(pdf_dir, pdf_filename)

        if os.path.exists(pdf_path):
            print(f"Opening {pdf_filename}...")
            open_file(pdf_path)
            opened_count += 1
        else:
            print(f"PDF not found: {pdf_filename}")
            missing_count += 1

    print("-" * 30)
    print(f"Total PDFs Opened: {opened_count}")
    print(f"Missing PDFs: {missing_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Open PDFs for matching JSON files.")
    parser.add_argument("--matched_dir", default=MATCHED_JSON_DIR,
                        help="Directory containing matched JSON files.")
    parser.add_argument("--pdf_dir", default=PDF_DIR,
                        help="Directory containing source PDF files.")

    args = parser.parse_args()
    main(args.matched_dir, args.pdf_dir)
