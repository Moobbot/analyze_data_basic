import os
import shutil
import fitz  # PyMuPDF
import config
import utils


def copy_file_and_label(filename, dest_folder_files, dest_folder_labels):
    """
    Copy both the PDF file and its corresponding JSON label to destination folders.

    Args:
        filename: Name of the PDF file
        dest_folder_files: Destination folder for PDF files
        dest_folder_labels: Destination folder for JSON label files

    Returns:
        Tuple of (pdf_copied: bool, label_copied: bool)
    """
    pdf_copied = False
    label_copied = False

    # Copy PDF file
    source_pdf = os.path.join(config.DATASET_DIR, filename)
    dest_pdf = os.path.join(dest_folder_files, filename)

    if os.path.exists(source_pdf):
        try:
            shutil.copy2(source_pdf, dest_pdf)
            pdf_copied = True
        except Exception as e:
            print(f"  Error copying PDF {filename}: {e}")

    # Copy corresponding JSON label
    label_filename = os.path.splitext(filename)[0] + ".json"
    source_label = os.path.join(config.LABEL_DIR, label_filename)
    dest_label = os.path.join(dest_folder_labels, label_filename)

    if os.path.exists(source_label):
        try:
            shutil.copy2(source_label, dest_label)
            label_copied = True
        except Exception as e:
            print(f"  Error copying label {label_filename}: {e}")

    return pdf_copied, label_copied


def move_file_and_label(filename, dest_folder_files, dest_folder_labels):
    """
    Move both the PDF file and its corresponding JSON label to destination folders.

    Args:
        filename: Name of the PDF file
        dest_folder_files: Destination folder for PDF files
        dest_folder_labels: Destination folder for JSON label files

    Returns:
        Tuple of (pdf_moved: bool, label_moved: bool)
    """
    pdf_moved = False
    label_moved = False

    # Move PDF file
    source_pdf = os.path.join(config.DATASET_DIR, filename)
    dest_pdf = os.path.join(dest_folder_files, filename)

    if os.path.exists(source_pdf):
        try:
            shutil.move(source_pdf, dest_pdf)
            pdf_moved = True
        except Exception as e:
            print(f"  Error moving PDF {filename}: {e}")

    # Move corresponding JSON label
    label_filename = os.path.splitext(filename)[0] + ".json"
    source_label = os.path.join(config.LABEL_DIR, label_filename)
    dest_label = os.path.join(dest_folder_labels, label_filename)

    if os.path.exists(source_label):
        try:
            shutil.move(source_label, dest_label)
            label_moved = True
        except Exception as e:
            print(f"  Error moving label {label_filename}: {e}")

    return pdf_moved, label_moved


def extract_text_from_pdfs():
    print(">>> STARTING PDF EXTRACTION (using PyMuPDF)")

    # Ensure output directory exists
    utils.ensure_dir_exists(config.EXTRACTED_TEXT_DIR)

    # Create destination folders for separation
    error_files_folder = os.path.join(
        config.BASE_DIR, "output_analyze", "PDF_Error_Files", "files"
    )
    error_labels_folder = os.path.join(
        config.BASE_DIR, "output_analyze", "PDF_Error_Files", "labels"
    )

    image_files_folder = os.path.join(
        config.BASE_DIR, "output_analyze", "PDF_Image_Files", "files"
    )
    image_labels_folder = os.path.join(
        config.BASE_DIR, "output_analyze", "PDF_Image_Files", "labels"
    )

    no_label_folder = os.path.join(config.BASE_DIR, "output_analyze", "PDF_No_Label")

    os.makedirs(error_files_folder, exist_ok=True)
    os.makedirs(error_labels_folder, exist_ok=True)
    os.makedirs(image_files_folder, exist_ok=True)
    os.makedirs(image_labels_folder, exist_ok=True)
    os.makedirs(no_label_folder, exist_ok=True)

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

    files = [f for f in os.listdir(config.DATASET_DIR) if f.lower().endswith(".pdf")]
    total_files = len(files)
    print(f"Found {total_files} PDF files in {config.DATASET_DIR}")

    for i, filename in enumerate(files):
        pdf_path = os.path.join(config.DATASET_DIR, filename)
        txt_filename = os.path.splitext(filename)[0] + ".txt"
        txt_path = os.path.join(config.EXTRACTED_TEXT_DIR, txt_filename)

        # Check if label exists
        label_filename = os.path.splitext(filename)[0] + ".json"
        label_path = os.path.join(config.LABEL_DIR, label_filename)
        has_label = os.path.exists(label_path)

        try:
            text_content = ""
            # PyMuPDF Open
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text_content += page.get_text() + "\n"

            # Analyze extracted text
            clean_text = text_content.strip()

            # HEURISTIC: If text is empty or very short (< 50 chars), assume it's an image/scanned PDF
            if not clean_text or len(clean_text) < 50:
                if has_label:
                    image_files.append(filename)
                    count_image_with_label += 1
                    # Move to image folder (PDF + Label)
                    move_file_and_label(
                        filename, image_files_folder, image_labels_folder
                    )
                else:
                    no_label_files.append(filename)
                    count_image_no_label += 1
                    # Move to No Label folder (PDF only)
                    try:
                        shutil.move(pdf_path, os.path.join(no_label_folder, filename))
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
            copy_file_and_label(filename, error_files_folder, error_labels_folder)

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
    no_label_report_path = os.path.join(config.REVIEW_DIR, "pdf_no_label_files.txt")
    with open(no_label_report_path, "w", encoding="utf-8") as f:
        f.write(
            f"DANH SÁCH FILE ẢNH/KHÔNG CÓ TEXT - KHÔNG CÓ LABEL ({len(no_label_files)} files)\n"
        )
        f.write("=" * 60 + "\n")
        f.write("\n".join(no_label_files))
    print(f"No Label report saved to: {no_label_report_path}")

    # Summary
    print("\n>>> EXTRACTION COMPLETE")
    print(f"Total processed: {total_files}")
    print(f"Success (Text found): {count_success}")
    print(f"Image - Has Label: {count_image_with_label}")
    print(f"Image - No Label: {count_image_no_label}")
    print(f"Errors (Read failed): {count_error}")
    print(f"\n>>> FILE SEPARATION COMPLETE")
    print(f"Error files → {error_files_folder}")
    print(f"Image files (w/ Label) → {image_files_folder}")
    print(f"No Label files → {no_label_folder}")


if __name__ == "__main__":
    extract_text_from_pdfs()
