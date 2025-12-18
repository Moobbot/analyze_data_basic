import os

# Base Directory
BASE_DIR = r"d:\Work\Clients\AIRC\product\ACPA\check_data_2025_12_19"

# Source Directories
DATASET_DIR = os.path.join(BASE_DIR, "Dataset_Invoice_one_page")
LABEL_DIR = os.path.join(BASE_DIR, "Label_Invoice_One_Page")

DIRECTORIES = {
    "Dataset": DATASET_DIR,
    "Label": LABEL_DIR
}

# Destination Directories (for separation)
DEST_MISSING = os.path.join(BASE_DIR, "Files_Missing_In_Label")
DEST_DOCX = os.path.join(BASE_DIR, "Files_Docx")

# Output Directory
REVIEW_DIR = os.path.join(BASE_DIR, "review_data")
EXTRACTED_TEXT_DIR = os.path.join(BASE_DIR, "Extracted_Text")

# Default Output Filenames
OUTPUT_CSV_NAME = "data_statistics.csv"
OUTPUT_REPORT_NAME = "data_summary_report.txt"
OUTPUT_DIFF_NAME = "file_differences.txt"
OUTPUT_FINAL_NAME = "final_summary.txt"

# PDF Extraction Reports
ERROR_PDF_REPORT = os.path.join(REVIEW_DIR, "pdf_error_files.txt")
IMAGE_PDF_REPORT = os.path.join(REVIEW_DIR, "pdf_image_files.txt") 

# Label Verification Reports
VERIFY_REPORT_CSV = os.path.join(REVIEW_DIR, "label_verification.csv")
VERIFY_REPORT_TXT = os.path.join(REVIEW_DIR, "label_verification_report.txt")

# Default Paths (for standalone execution)
DEFAULT_OUTPUT_CSV = os.path.join(BASE_DIR, OUTPUT_CSV_NAME)
DEFAULT_OUTPUT_REPORT = os.path.join(BASE_DIR, OUTPUT_REPORT_NAME)
DEFAULT_OUTPUT_DIFF = os.path.join(BASE_DIR, OUTPUT_DIFF_NAME)
DEFAULT_OUTPUT_FINAL = os.path.join(BASE_DIR, OUTPUT_FINAL_NAME)
