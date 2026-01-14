import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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
    print("INVOICE DATA AUDIT PIPELINE")
    print("=" * 60)

    print("\n[1] CLEANING JSON DATA")
    core.cleaning.clean_json_files()

    print("\n[2] ANALYZING FILES")
    core.analysis.analyze_directories()

    print("\n[3] EXTRACTING PDF TEXT")
    core.extraction.extract_text_from_pdfs()

    print("\n[4] VERIFYING LABELS")
    core.verification.verify_labels()

    print("\n[5] SEPARATING FILES")
    core.separation.copy_files()

    print("\n[6] FILTERING RESULTS")
    core.filtering.filter_results()

    print("\n[7] COMPARING DATASET")
    core.comparison.compare_directories()

    print("\n[8] GENERATING REPORTS")
    reports.merger.merge()
    reports.generator.generate_reports()
    reports.status_details.generate_status_report()

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"Output: {config.REVIEW_DIR}")


if __name__ == "__main__":
    run_pipeline()
