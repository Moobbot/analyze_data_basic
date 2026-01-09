import os
import sys
import shutil

# Add parent directory to path to import common_lib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common_lib.pdf_utils import extract_text_from_pdf, is_text_based_pdf
from common_lib.file_utils import ensure_dir_exists, list_files_recursive
from lib import utils
from lib import config


def extract_text_from_pdfs():
    print(">>> STARTING PDF EXTRACTION (using PyMuPDF)")

    # Ensure output directory exists
    utils.ensure_dir_exists(config.EXTRACTED_TEXT_DIR)

    # Ensure PDF Separation Directories exist
    os.makedirs(config.PDF_ERROR_FILES_DIR, exist_ok=True)
    os.makedirs(config.PDF_ERROR_LABELS_DIR, exist_ok=True)
    os.makedirs(config.PDF_IMAGE_FILES_DIR, exist_ok=True)
    os.makedirs(config.PDF_IMAGE_LABELS_DIR, exist_ok=True)
    os.makedirs(config.PDF_NO_LABEL_DIR, exist_ok=True)

    # Stats
    count_success = 0
    count_error = 0
    count_image_with_label = 0
    count_image_no_label = 0

    error_files = []
    image_files = []
    no_label_files = []

    # Get List of PDF files
    if not os.path.exists(config.DATASET_DIR):
        print(f"Error: Dataset directory not found: {config.DATASET_DIR}")
        return

    files = utils.list_files_recursive(config.DATASET_DIR, ".pdf")
    total_files = len(files)
    print(f"Found {total_files} PDF files in {config.DATASET_DIR}")

    for i, filename in enumerate(files):
        pdf_path = os.path.join(config.DATASET_DIR, filename)
        txt_filename = os.path.splitext(filename)[0] + ".txt"
        txt_path = os.path.join(config.EXTRACTED_TEXT_DIR, txt_filename)

        # Ensure txt output subdirectory exists
        utils.ensure_dir_exists(os.path.dirname(txt_path))

        # Check if label exists
        label_filename = os.path.splitext(filename)[0] + ".json"
        label_path = os.path.join(config.LABEL_DIR, label_filename)
        has_label = os.path.exists(label_path)

        try:
            # Use common_lib extraction function
            text_content = extract_text_from_pdf(pdf_path)

            if text_content is None:
                # Extraction error
                raise Exception("Failed to extract text from PDF")

            # Analyze extracted text
            clean_text = text_content.strip()

            # HEURISTIC: If text is empty or very short (< 50 chars), assume it's an image/scanned PDF
            if not is_text_based_pdf(pdf_path, min_text_length=50):

                if has_label:
                    image_files.append(filename)
                    count_image_with_label += 1
                    # Move to image folder (PDF + Label)
                    utils.move_file_and_label(
                        filename,
                        config.PDF_IMAGE_FILES_DIR,
                        config.PDF_IMAGE_LABELS_DIR,
                    )
                else:
                    no_label_files.append(filename)
                    count_image_no_label += 1
                    # Move to No Label folder (PDF only)
                    try:
                        dest_no_label = os.path.join(config.PDF_NO_LABEL_DIR, filename)
                        utils.ensure_dir_exists(os.path.dirname(dest_no_label))
                        shutil.move(pdf_path, dest_no_label)
                    except Exception as e:
                        print(f"  Error moving PDF {filename} to No Label: {e}")
            else:
                count_success += 1

            # Save to text file
            with open(txt_path, "w", encoding="utf-8") as f_out:
                f_out.write(text_content)

        except Exception as e:
            print(f"Error reading {filename}: {e}")
            error_files.append(f"{filename} | Error: {str(e)}")
            count_error += 1
            # Copy to error folder
            utils.copy_file_and_label(
                filename, config.PDF_ERROR_FILES_DIR, config.PDF_ERROR_LABELS_DIR
            )

        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{total_files} files...")

    # Write Report Files
    # 1. Error Files
    with open(config.ERROR_PDF_REPORT, "w", encoding="utf-8") as f:
        f.write(f"DANH SÁCH FILE LỖI KHÔNG ĐỌC ĐƯỢC ({len(error_files)} files)\n")
        f.write("=" * 60 + "\n")
        f.write("\n".join(error_files))
    print(f"Error report saved to: {config.ERROR_PDF_REPORT}")

    # 2. Image/Scanned Files (With Labels)
    with open(config.IMAGE_PDF_REPORT, "w", encoding="utf-8") as f:
        f.write(
            f"DANH SÁCH FILE ẢNH/KHÔNG CÓ TEXT - CÓ LABEL ({len(image_files)} files)\n"
        )
        f.write("=" * 60 + "\n")
        f.write("\n".join(image_files))
    print(f"Image report saved to: {config.IMAGE_PDF_REPORT}")

    # 3. No Label Files (Image/Scanned)
    with open(config.NO_LABEL_PDF_REPORT, "w", encoding="utf-8") as f:
        f.write(
            f"DANH SÁCH FILE ẢNH/KHÔNG CÓ TEXT - KHÔNG CÓ LABEL ({len(no_label_files)} files)\n"
        )
        f.write("=" * 60 + "\n")
        f.write("\n".join(no_label_files))
    print(f"No Label report saved to: {config.NO_LABEL_PDF_REPORT}")

    # Summary
    print("\n>>> EXTRACTION COMPLETE")
    print(f"Total processed: {total_files}")
    print(f"Success (Text found): {count_success}")
    print(f"Image - Has Label: {count_image_with_label}")
    print(f"Image - No Label: {count_image_no_label}")
    print(f"Errors (Read failed): {count_error}")
    print(f"\n>>> FILE SEPARATION COMPLETE")
    print(f"Error files → {config.PDF_ERROR_FILES_DIR}")
    print(f"Image files (w/ Label) → {config.PDF_IMAGE_FILES_DIR}")
    print(f"No Label files → {config.PDF_NO_LABEL_DIR}")


if __name__ == "__main__":
    extract_text_from_pdfs()
