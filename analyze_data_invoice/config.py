import os
import sys
from pathlib import Path

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Source Directories
DATASET_DIR = BASE_DIR / "Datasets" / "data-all-check-v2" / "files"
LABEL_DIR = BASE_DIR / "Datasets" / "data-all-check-v2" / "labels"

DIRECTORIES = {"Dataset": DATASET_DIR, "Label": LABEL_DIR}

# Verified Labels Output
LABEL_TRUE_DIR = BASE_DIR / "Datasets" / "data-all-check-v2" / "true"

# Output Directory
REVIEW_DIR = BASE_DIR / "output_analyze" / "data-all-check-v2"

# Destination Directories (for separation)
DEST_MISSING = REVIEW_DIR / "Files_Missing_In_Label"
DEST_LABEL_MISSING_PDF = REVIEW_DIR / "Files_Label_Missing_PDF"
DEST_DOCX = REVIEW_DIR / "Files_Docx"

# PDF Separation Directories
PDF_ERROR_DIR = REVIEW_DIR / "PDF_Error_Files"
PDF_ERROR_FILES_DIR = PDF_ERROR_DIR / "files"
PDF_ERROR_LABELS_DIR = PDF_ERROR_DIR / "labels"

PDF_IMAGE_DIR = REVIEW_DIR / "PDF_Image_Files"
PDF_IMAGE_FILES_DIR = PDF_IMAGE_DIR / "files"
PDF_IMAGE_LABELS_DIR = PDF_IMAGE_DIR / "labels"

PDF_NO_LABEL_DIR = REVIEW_DIR / "PDF_No_Label"

EXTRACTED_TEXT_DIR = REVIEW_DIR / "extracted_text"

# Default Output Filenames
REPORT_DIR = REVIEW_DIR / "reports"
OUTPUT_CSV_NAME = "data_statistics.csv"
OUTPUT_REPORT_NAME = "data_summary_report.txt"
OUTPUT_DIFF_NAME = REPORT_DIR / "file_differences.txt"
OUTPUT_FINAL_NAME = REPORT_DIR / "final_summary.txt"

# PDF Extraction Reports
ERROR_PDF_REPORT = REPORT_DIR / "pdf_error_files.txt"
IMAGE_PDF_REPORT = REPORT_DIR / "pdf_image_files.txt"
NO_LABEL_PDF_REPORT = REPORT_DIR / "pdf_no_label_files.txt"

# Label Verification Reports
VERIFY_REPORT_CSV = REPORT_DIR / "label_verification.csv"
VERIFY_REPORT_TXT = REPORT_DIR / "label_verification_report.txt"

# Default Paths (for standalone execution compatibility)
DEFAULT_OUTPUT_CSV = BASE_DIR / OUTPUT_CSV_NAME
DEFAULT_OUTPUT_REPORT = BASE_DIR / OUTPUT_REPORT_NAME
DEFAULT_OUTPUT_DIFF = BASE_DIR / OUTPUT_DIFF_NAME
DEFAULT_OUTPUT_FINAL = BASE_DIR / OUTPUT_FINAL_NAME

# Output directories for duplicates
DUPLICATE_DIR = REVIEW_DIR / "duplicates"
DUPLICATE_LABELS_DIR = DUPLICATE_DIR / "labels"
DUPLICATE_FILES_DIR = DUPLICATE_DIR / "files"


# Ensure critical directories exist
def ensure_dirs():
    dirs = [
        REVIEW_DIR,
        REPORT_DIR,
        EXTRACTED_TEXT_DIR,
        PDF_ERROR_DIR,
        PDF_IMAGE_DIR,
        DEST_MISSING,
        DEST_LABEL_MISSING_PDF,
        DUPLICATE_DIR,
        DUPLICATE_LABELS_DIR,
        DUPLICATE_FILES_DIR,
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


# Run ensure_dirs on import to be safe, or call it explicitly in main
ensure_dirs()
