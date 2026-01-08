import os
import shutil
import fitz  # PyMuPDF
import config
from lib.file_utils import move_file_and_label, copy_file_and_label
from lib.logger import get_logger
from lib.constants import MIN_TEXT_LENGTH_FOR_VALID_PDF

# Setup logger
logger = get_logger(__name__)


def extract_text_from_pdfs():
    logger.info("Starting PDF extraction using PyMuPDF")

    # Ensure output directory exists
    config.EXTRACTED_TEXT_DIR.mkdir(parents=True, exist_ok=True)

    # Ensure PDF Separation Directories exist
    config.PDF_ERROR_FILES_DIR.mkdir(parents=True, exist_ok=True)
    config.PDF_ERROR_LABELS_DIR.mkdir(parents=True, exist_ok=True)
    config.PDF_IMAGE_FILES_DIR.mkdir(parents=True, exist_ok=True)
    config.PDF_IMAGE_LABELS_DIR.mkdir(parents=True, exist_ok=True)
    config.PDF_NO_LABEL_DIR.mkdir(parents=True, exist_ok=True)

    # Stats
    count_success = 0
    count_error = 0
    count_image_with_label = 0
    count_image_no_label = 0

    error_files = []
    image_files = []
    no_label_files = []

    # Get List of PDF files
    if not config.DATASET_DIR.exists():
        logger.error(f"Dataset directory not found: {config.DATASET_DIR}")
        return

    # Import list_files_recursive from backward-compatible utils
    from lib.file_utils import list_files_recursive

    files = list_files_recursive(config.DATASET_DIR, ".pdf")
    total_files = len(files)
    logger.info(f"Found {total_files} PDF files in {config.DATASET_DIR}")

    for i, filename in enumerate(files):
        pdf_path = config.DATASET_DIR / filename
        txt_filename = os.path.splitext(filename)[0] + ".txt"
        txt_path = config.EXTRACTED_TEXT_DIR / txt_filename

        # Ensure txt output subdirectory exists (if filename includes subdirs)
        txt_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if label exists
        label_filename = os.path.splitext(filename)[0] + ".json"
        label_path = config.LABEL_DIR / label_filename
        has_label = label_path.exists()

        try:
            text_content = ""
            # PyMuPDF Open
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text_content += page.get_text() + "\n"

            # Analyze extracted text
            clean_text = text_content.strip()

            # HEURISTIC: If text is empty or very short, assume it's an image/scanned PDF
            if not clean_text or len(clean_text) < MIN_TEXT_LENGTH_FOR_VALID_PDF:
                if has_label:
                    image_files.append(filename)
                    count_image_with_label += 1
                    # Move to image folder (PDF + Label)
                    move_file_and_label(
                        filename,
                        config.PDF_IMAGE_FILES_DIR,
                        config.PDF_IMAGE_LABELS_DIR,
                    )
                else:
                    no_label_files.append(filename)
                    count_image_no_label += 1
                    # Move to No Label folder (PDF only)
                    try:
                        dest_no_label = config.PDF_NO_LABEL_DIR / filename
                        dest_no_label.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(pdf_path, dest_no_label)
                    except Exception as e:
                        logger.error(f"Error moving PDF {filename} to No Label: {e}")
            else:
                count_success += 1

            # Save to text file
            with open(txt_path, "w", encoding="utf-8") as f_out:
                f_out.write(text_content)

        except Exception as e:
            logger.error(f"Error reading {filename}: {e}")
            error_files.append(f"{filename} | Error: {str(e)}")
            count_error += 1
            # Copy to error folder
            copy_file_and_label(
                filename, config.PDF_ERROR_FILES_DIR, config.PDF_ERROR_LABELS_DIR
            )

        if (i + 1) % 100 == 0:
            logger.info(f"Processed {i + 1}/{total_files} files")

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
