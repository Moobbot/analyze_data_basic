from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Input
DATASET_DIR = BASE_DIR / "datasets" / "data-muti-page" / "files"
LABEL_DIR = BASE_DIR / "datasets" / "data-muti-page" / "labels"
DIRECTORIES = {"Dataset": DATASET_DIR, "Label": LABEL_DIR}

# Output
REVIEW_DIR = BASE_DIR / "output_analyze" / "data-muti-page"
REPORT_DIR = REVIEW_DIR / "reports"
EXTRACTED_TEXT_DIR = REVIEW_DIR / "extracted_text"

# Organization
DEST_MISSING = REVIEW_DIR / "Files_Missing_In_Label"
DEST_LABEL_MISSING_PDF = REVIEW_DIR / "Files_Label_Missing_PDF"
DEST_DOCX = REVIEW_DIR / "Files_Docx"

# PDF directories
PDF_ERROR_DIR = REVIEW_DIR / "PDF_Error_Files"
PDF_ERROR_FILES_DIR = PDF_ERROR_DIR / "files"
PDF_ERROR_LABELS_DIR = PDF_ERROR_DIR / "labels"
PDF_IMAGE_DIR = REVIEW_DIR / "PDF_Image_Files"
PDF_IMAGE_FILES_DIR = PDF_IMAGE_DIR / "files"
PDF_IMAGE_LABELS_DIR = PDF_IMAGE_DIR / "labels"
PDF_NO_LABEL_DIR = REVIEW_DIR / "PDF_No_Label"

# Reports
# Reports
LOG_VALIDATION = REPORT_DIR / "1_json_validation_log.txt"
OUTPUT_CSV_NAME = REPORT_DIR / "2_data_statistics.csv"
OUTPUT_REPORT_NAME = REPORT_DIR / "2_data_summary_report.txt"
ERROR_PDF_REPORT = REPORT_DIR / "3_pdf_error_files.txt"
IMAGE_PDF_REPORT = REPORT_DIR / "3_pdf_image_files.txt"
NO_LABEL_PDF_REPORT = REPORT_DIR / "3_pdf_no_label_files.txt"
PAGE_INFO_REPORT = REPORT_DIR / "3_pdf_page_info.csv"
VERIFY_REPORT_CSV = REPORT_DIR / "4_label_verification.csv"
VERIFY_REPORT_TXT = REPORT_DIR / "4_label_verification_report.txt"
OUTPUT_FILTER_MISSING = REPORT_DIR / "6_label_verification_missing.csv"
OUTPUT_FILTER_SIMILAR = REPORT_DIR / "6_label_verification_similar.csv"
OUTPUT_DIFF_NAME = REPORT_DIR / "7_file_differences.txt"
OUTPUT_FINAL_NAME = REPORT_DIR / "8_final_summary.txt"
STATUS_STATS_REPORT = REPORT_DIR / "status_statistics_report.txt"

# Duplicates
DUPLICATE_DIR = REVIEW_DIR / "duplicates"
DUPLICATE_LABELS_DIR = DUPLICATE_DIR / "labels"
DUPLICATE_FILES_DIR = DUPLICATE_DIR / "files"

# Legacy paths
LABEL_TRUE_DIR = BASE_DIR / "datasets" / "data-muti-page" / "true"
DEFAULT_OUTPUT_CSV = BASE_DIR / OUTPUT_CSV_NAME
DEFAULT_OUTPUT_REPORT = BASE_DIR / OUTPUT_REPORT_NAME
DEFAULT_OUTPUT_DIFF = BASE_DIR / OUTPUT_DIFF_NAME
DEFAULT_OUTPUT_FINAL = BASE_DIR / OUTPUT_FINAL_NAME


def ensure_dirs():
    """Create required directories"""
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
        PDF_NO_LABEL_DIR,
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


ensure_dirs()
