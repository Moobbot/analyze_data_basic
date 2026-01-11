import sys
from pathlib import Path

# Add project root to sys.path to ensure imports work if run from subdirs (though usually run from root)
sys.path.append(str(Path(__file__).resolve().parent))
# Add parent directory to allow importing common_lib
sys.path.append(str(Path(__file__).resolve().parent.parent))

import config
import core.cleaning
import core.analysis
import core.extraction
import core.verification
import core.separation
import core.comparison
import core.filtering
import reports.merger
import reports.generator
import reports.status_details


def run_pipeline():
    print("=" * 60)
    print("      INVOICE DATA AUDIT PIPELINE (REFACTORED)")
    print("=" * 60)

    # 1. Cleaning
    print("\n>>> [STEP 1] CLEANING JSON DATA (FORMATS)")
    core.cleaning.clean_json_files()

    # 2. Analysis (Initial)
    print("\n>>> [STEP 2] ANALYZING FILE STATISTICS")
    core.analysis.analyze_directories()

    # 3. Extraction
    print("\n>>> [STEP 3] EXTRACTING TEXT FROM PDFS")
    core.extraction.extract_text_from_pdfs()

    # 4. Verification
    print("\n>>> [STEP 4] VERIFYING LABELS VS EXTRACTED TEXT")
    core.verification.verify_labels()

    # 5. Separation (Move Files)
    print("\n>>> [STEP 5] SEPARATING FILES (MOVING PROBLEM FILES)")
    core.separation.copy_files()

    # 6. Filtering (Post-Verification)
    print("\n>>> [STEP 6] FILTERING RESULTS & VERIFIED FILES")
    core.filtering.filter_results()
    # core.filtering.filter_verified_labels() # Uncomment to enable moving verified files to 'true' folder

    # 7. Comparison (Final Check)
    print("\n>>> [STEP 7] COMPARING DATASET VS LABEL (DIFFERENCES)")
    core.comparison.compare_directories()

    # 8. Reporting
    print("\n>>> [STEP 8] GENERATING FINAL REPORTS")
    reports.merger.merge()
    reports.generator.generate_reports()

    print("\n   [+] Generating Detailed Status Report...")
    reports.status_details.generate_status_report()

    print("\n" + "=" * 60)
    print("      PIPELINE COMPLETE")
    print("=" * 60)
    print(f"Check output in: {config.REVIEW_DIR}")


if __name__ == "__main__":
    run_pipeline()
