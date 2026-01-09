import os
import sys

# Base Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Source Directories
# DATASET_DIR = os.path.join(BASE_DIR, "datasets", "Dataset_Invoice_one_page")
# LABEL_DIR = os.path.join(BASE_DIR, "Label_Invoice_One_Page")
DATASET_DIR = os.path.join(BASE_DIR, "datasets", "files")
LABEL_DIR = os.path.join(BASE_DIR, "datasets", "labels")
DIRECTORIES = {"Dataset": DATASET_DIR, "Label": LABEL_DIR}

# Verified Labels Output
LABEL_TRUE_DIR = os.path.join(BASE_DIR, "datasets", "true")

# Destination Directories (for separation)
DEST_MISSING = os.path.join(
    BASE_DIR, "output_analyze", "datasets", "Files_Missing_In_Label"
)
DEST_LABEL_MISSING_PDF = os.path.join(
    BASE_DIR, "output_analyze", "datasets", "Files_Label_Missing_PDF"
)
DEST_DOCX = os.path.join(BASE_DIR, "output_analyze", "datasets", "Files_Docx")

# PDF Separation Directories
PDF_ERROR_DIR = os.path.join(BASE_DIR, "output_analyze", "datasets", "PDF_Error_Files")
PDF_ERROR_FILES_DIR = os.path.join(PDF_ERROR_DIR, "files")
PDF_ERROR_LABELS_DIR = os.path.join(PDF_ERROR_DIR, "labels")

PDF_IMAGE_DIR = os.path.join(BASE_DIR, "output_analyze", "datasets", "PDF_Image_Files")
PDF_IMAGE_FILES_DIR = os.path.join(PDF_IMAGE_DIR, "files")
PDF_IMAGE_LABELS_DIR = os.path.join(PDF_IMAGE_DIR, "labels")

PDF_NO_LABEL_DIR = os.path.join(BASE_DIR, "output_analyze", "datasets", "PDF_No_Label")

# Output Directory
REVIEW_DIR = os.path.join(BASE_DIR, "output_analyze", "datasets")
EXTRACTED_TEXT_DIR = os.path.join(
    BASE_DIR, "output_analyze", "datasets", "extracted_text"
)

# Default Output Filenames
OUTPUT_CSV_NAME = "data_statistics.csv"
OUTPUT_REPORT_NAME = "data_summary_report.txt"
OUTPUT_DIFF_NAME = "file_differences.txt"
OUTPUT_FINAL_NAME = "final_summary.txt"

# PDF Extraction Reports
ERROR_PDF_REPORT = os.path.join(REVIEW_DIR, "pdf_error_files.txt")
IMAGE_PDF_REPORT = os.path.join(REVIEW_DIR, "pdf_image_files.txt")
NO_LABEL_PDF_REPORT = os.path.join(REVIEW_DIR, "pdf_no_label_files.txt")

# Label Verification Reports
VERIFY_REPORT_CSV = os.path.join(REVIEW_DIR, "label_verification.csv")
VERIFY_REPORT_TXT = os.path.join(REVIEW_DIR, "label_verification_report.txt")

# Default Paths (for standalone execution)
DEFAULT_OUTPUT_CSV = os.path.join(BASE_DIR, OUTPUT_CSV_NAME)
DEFAULT_OUTPUT_REPORT = os.path.join(BASE_DIR, OUTPUT_REPORT_NAME)
DEFAULT_OUTPUT_DIFF = os.path.join(BASE_DIR, OUTPUT_DIFF_NAME)
DEFAULT_OUTPUT_FINAL = os.path.join(BASE_DIR, OUTPUT_FINAL_NAME)
