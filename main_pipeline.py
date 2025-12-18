import os
import shutil
import config
import utils

# Import existing modules
import analyze_data
import compare_files
import merge_reports
import separate_files

# --- Workflow ---
def run_pipeline():
    print(">>> STARTING PIPELINE")
    
    # Ensure review dir exists
    utils.ensure_dir_exists(config.REVIEW_DIR)

    # 1. Initial Analysis (Pre-Separation)
    print("\n[Step 1] Initial Analysis...")
    pre_report = os.path.join(config.REVIEW_DIR, "data_summary_report_pre.txt")
    pre_diff = os.path.join(config.REVIEW_DIR, "file_differences_pre.txt")
    pre_final = os.path.join(config.REVIEW_DIR, "final_summary_pre.txt")
    pre_csv = os.path.join(config.REVIEW_DIR, "data_statistics_pre.csv") 

    # Run Analyze
    analyze_data.analyze_directories(output_csv=pre_csv, output_report=pre_report)
    
    # Run Compare
    compare_files.compare_directories(output_file=pre_diff)
    
    # Run Merge
    merge_reports.merge(report_path=pre_report, diff_path=pre_diff, output_path=pre_final)
    
    # 2. Files Separation (Move)
    print("\n[Step 2] Moving Files...")
    separate_files.copy_files() # Note: function name is copy_files but logic moves files (as updated)
    
    # 3. Post-Separation Analysis
    print("\n[Step 3] Post-Separation Analysis...")
        
    post_report = os.path.join(config.REVIEW_DIR, "data_summary_report.txt")
    post_diff = os.path.join(config.REVIEW_DIR, "file_differences.txt")
    post_csv = os.path.join(config.REVIEW_DIR, "data_statistics.csv")
    # Note: User didn't ask for a final merged summary in review_data, but only "Lưu các file phân tích vào folder review_data"
    # Analyze and Compare are the main analysis scripts.
    
    # Run Analyze
    analyze_data.analyze_directories(output_csv=post_csv, output_report=post_report)
    
    # Run Compare
    compare_files.compare_directories(output_file=post_diff)

    print("\n>>> PIPELINE FINISHED.")
    print(f"Pre-Analysis Reports: {pre_final}")
    print(f"Post-Analysis Reports: {config.REVIEW_DIR}")

if __name__ == "__main__":
    run_pipeline()
