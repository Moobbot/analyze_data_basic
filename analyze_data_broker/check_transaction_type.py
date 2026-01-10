# check_transaction_type.py
# ==============================================================================
# Main Controller Script
# ==============================================================================

import os
import sys

# Add parent directory to path to access common_lib
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

import json
import csv
import shutil
from lib import config, validation_logic

# ==============================================================================
# Helper Functions (File Loading)
# ==============================================================================


def load_json(json_path):
    """Loads JSON data from a file."""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON {json_path}: {e}")
        return None


def load_text(json_path):
    """Loads corresponding extracted text content for a given JSON path."""
    try:
        base_dir = os.path.dirname(json_path)
        parent_dir_name = os.path.basename(base_dir)  # e.g., Trade_Confirmation
        filename = os.path.basename(json_path)
        name_no_ext = os.path.splitext(filename)[0]

        # Use fixed extracted_text directory with the label subfolder
        txt_path = os.path.join(
            config.EXTRACTED_TEXT_DIR, parent_dir_name, name_no_ext + ".txt"
        )

        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return None
    except Exception as e:
        print(f"Error loading Text for {json_path}: {e}")
        return None


# ==============================================================================
# Validation Controller
# ==============================================================================


def validate_file(json_path):
    """Orchestrates validation for a single JSON file."""
    try:
        # Load JSON Data
        data = load_json(json_path)

        if data is None:
            return {"File": os.path.basename(json_path), "Error": "JSON Load Failed"}

        # Handle case where JSON is a list
        if isinstance(data, list):
            if not data:
                return {"File": os.path.basename(json_path), "Error": "Empty JSON List"}
            data = data[0]

        # Ensure root element is a dictionary
        if not isinstance(data, dict):
            return {
                "File": os.path.basename(json_path),
                "Error": f"JSON Root is {type(data)}",
            }

        # Load Extracted Text
        text_content = load_text(json_path)

        # Initialize Result Row
        result_log = {
            "File": os.path.basename(json_path),
            "Text Status": "N/A",
            "Transaction Type": "N/A",
            "Trade Date": "N/A",
            "Settlement Date": "N/A",
            "ISIN Status": "N/A",
            "Generic Errors": [],
            "Error": "",
        }

        # Check Text Status
        if text_content is None:
            result_log["Text Status"] = "MISSING FILE"
            result_log["Error"] = "Text file not found"
            text_content = ""  # Safe fallback
        elif not text_content.strip():
            result_log["Text Status"] = "EMPTY"
            text_content = ""
        else:
            result_log["Text Status"] = "OK"

        # --- STEP 1: Verify Transaction Type ---
        validation_logic.check_transaction_type(data, text_content, result_log)

        # --- STEP 2: Verify Dates ---
        validation_logic.check_date_field("Trade Date", data, text_content, result_log)
        validation_logic.check_date_field(
            "Settlement Date", data, text_content, result_log
        )

        # --- STEP 3: Verify ISIN ---
        validation_logic.check_isin(data, result_log)

        # --- STEP 4: Verify Generic Fields ---
        numeric_fields = [
            "Quantity",
            "Foreign Unit Price",
            "Foreign Net Consideration",
            "Net Consideration",
            "Exec Commission",
            "Foreign Gross Consideration",
        ]
        for f in numeric_fields:
            validation_logic.check_generic_field(f, data, (int, float), result_log)
            validation_logic.check_field_presence(f, data, text_content, result_log)

        string_fields = ["Client name", "Name/ Security", "Currency", "Securities ID"]
        for f in string_fields:
            validation_logic.check_generic_field(f, data, str, result_log)
            validation_logic.check_field_presence(f, data, text_content, result_log)

        # Format Generic Errors
        if result_log["Generic Errors"]:
            result_log["Generic Errors"] = "; ".join(result_log["Generic Errors"])
        else:
            result_log["Generic Errors"] = ""

        return result_log

    except Exception as e:
        print(f"CRITICAL ERROR processing {json_path}: {e}")
        return {"File": os.path.basename(json_path), "Error": f"Exception: {str(e)}"}


# ==============================================================================
# Reporting
# ==============================================================================


def generate_report(results, report_path):
    """Generates a summary text report from the validation results."""
    if not results:
        return

    total_files = len(results)

    # Text Status Stats
    text_ok = sum(1 for r in results if r.get("Text Status") == "OK")
    text_missing = sum(1 for r in results if r.get("Text Status") == "MISSING FILE")
    text_empty = sum(1 for r in results if r.get("Text Status") == "EMPTY")

    # Transaction Type Stats
    trans_pass = sum(1 for r in results if r.get("Transaction Type") == "PASS")
    trans_fail = sum(
        1 for r in results if str(r.get("Transaction Type")).startswith("FAIL")
    )
    trans_warn = sum(
        1 for r in results if str(r.get("Transaction Type")).startswith("WARN")
    )

    # Trade Date Stats
    trade_pass = sum(1 for r in results if r.get("Trade Date") == "PASS")
    trade_warn = sum(1 for r in results if str(r.get("Trade Date")).startswith("WARN"))
    trade_fail = sum(1 for r in results if str(r.get("Trade Date")).startswith("FAIL"))

    # Settlement Date Stats
    settle_pass = sum(1 for r in results if r.get("Settlement Date") == "PASS")
    settle_warn = sum(
        1 for r in results if str(r.get("Settlement Date")).startswith("WARN")
    )
    settle_fail = sum(
        1 for r in results if str(r.get("Settlement Date")).startswith("FAIL")
    )

    # ISIN Stats
    isin_pass = sum(1 for r in results if r.get("ISIN Status") == "PASS")
    isin_fail = sum(1 for r in results if str(r.get("ISIN Status")).startswith("FAIL"))
    isin_missing = sum(1 for r in results if r.get("ISIN Status") == "MISSING")

    # Presence stats for other fields (JSON vs Text)
    presence_fields = [
        "Quantity",
        "Foreign Unit Price",
        "Foreign Net Consideration",
        "Net Consideration",
        "Exec Commission",
        "Foreign Gross Consideration",
        "Client name",
        "Name/ Security",
        "Currency",
    ]

    def presence_counts(field):
        json_key = f"{field} (JSON)"
        text_key = f"{field} (Text)"
        p_pass = 0
        p_fail = 0
        p_missing = 0
        for r in results:
            json_val = r.get(json_key)
            text_val = r.get(text_key)
            has_json = json_val not in (None, "")
            has_text = text_val not in (None, "")
            if not has_json:
                p_missing += 1
            elif has_text:
                p_pass += 1
            else:
                p_fail += 1
        return p_pass, p_fail, p_missing

    # Critical Errors (Files with "Error" field populated)
    critical_errors = [r for r in results if r.get("Error")]

    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("DATA VALIDATION SUMMARY REPORT\n")
            f.write("==============================\n")
            f.write(f"Total Files Processed: {total_files}\n\n")

            f.write("TEXT EXTRACTION STATUS\n")
            f.write("----------------------\n")
            f.write(f"OK:            {text_ok}\n")
            f.write(f"MISSING FILE:  {text_missing}\n")
            f.write(f"EMPTY:         {text_empty}\n\n")

            f.write("FIELD VALIDATION STATS\n")
            f.write("----------------------\n")
            f.write(
                f"Transaction Type: {trans_pass} PASS, {trans_fail} FAIL, {trans_warn} WARN\n"
            )
            f.write(
                f"Trade Date:       {trade_pass} PASS, {trade_fail} FAIL, {trade_warn} WARN\n"
            )
            f.write(
                f"Settlement Date:  {settle_pass} PASS, {settle_fail} FAIL, {settle_warn} WARN\n"
            )
            f.write(
                f"ISIN Status:      {isin_pass} PASS, {isin_fail} FAIL, {isin_missing} MISSING\n\n"
            )

            f.write("PRESENCE IN TEXT (Other Fields)\n")
            f.write("--------------------------------\n")
            for field in presence_fields:
                p_pass, p_fail, p_missing = presence_counts(field)
                f.write(f"{field}: {p_pass} PASS, {p_fail} FAIL, {p_missing} MISSING\n")

            f.write("\n")
            if critical_errors:
                f.write("CRITICAL ERRORS\n")
                f.write("---------------\n")
                for err in critical_errors:
                    f.write(f"{err['File']}: {err['Error']}\n")
            else:
                f.write("No Critical Errors Found.\n")

        print(f"Successfully wrote report to {report_path}")
    except Exception as e:
        print(f"Error writing report: {e}")


# ==============================================================================
# File Filtering and Organization
# ==============================================================================


def copy_ambiguous_date_files(results, input_folder, output_dir):
    """Copies JSON files and their corresponding text files with ambiguous date format warnings to a separate folder.

    Args:
        results: List of validation results
        input_folder: Source folder where original JSON files are located
        output_dir: Base output directory where ambiguous_dates folder will be created
    """
    # Find files with ambiguous date warnings
    ambiguous_files = []
    for r in results:
        trade_date = r.get("Trade Date", "")
        settlement_date = r.get("Settlement Date", "")

        if "WARN: Ambiguous Date Format" in str(
            trade_date
        ) or "WARN: Ambiguous Date Format" in str(settlement_date):
            ambiguous_files.append(r.get("File"))

    if not ambiguous_files:
        print("No files with ambiguous date format found.")
        return

    # Create output folder for ambiguous date files
    ambiguous_folder = os.path.join(output_dir, "ambiguous_dates")
    os.makedirs(ambiguous_folder, exist_ok=True)

    # Copy JSON files and corresponding text files
    copied_json_count = 0
    copied_text_count = 0

    for filename in ambiguous_files:
        # Find and copy JSON file
        for root, dirs, filenames in os.walk(input_folder):
            if filename in filenames:
                source_json_path = os.path.join(root, filename)
                dest_json_path = os.path.join(ambiguous_folder, filename)

                try:
                    shutil.copy2(source_json_path, dest_json_path)
                    copied_json_count += 1
                    print(f"Copied JSON: {filename}")
                except Exception as e:
                    print(f"Error copying JSON {filename}: {e}")

                # Find and copy corresponding text file
                try:
                    parent_dir_name = os.path.basename(root)  # e.g., Trade_Confirmation
                    name_no_ext = os.path.splitext(filename)[0]

                    # Use fixed extracted_text directory with the label subfolder
                    txt_path = os.path.join(
                        config.EXTRACTED_TEXT_DIR, parent_dir_name, name_no_ext + ".txt"
                    )

                    if os.path.exists(txt_path):
                        dest_txt_path = os.path.join(
                            ambiguous_folder, name_no_ext + ".txt"
                        )
                        shutil.copy2(txt_path, dest_txt_path)
                        copied_text_count += 1
                        print(f"Copied TEXT: {name_no_ext}.txt")
                    else:
                        print(f"Text file not found for: {filename}")
                except Exception as e:
                    print(f"Error copying text file for {filename}: {e}")

                break

    print(
        f"\nSuccessfully copied {copied_json_count} JSON files and {copied_text_count} text files to: {ambiguous_folder}"
    )


# ==============================================================================
# Batch Processing Controller
# ==============================================================================


def process_folder(input_folder, output_csv, output_report=None):
    """Iterates through a folder, validates files, and writes CSV."""
    print(f"Processing folder: {input_folder}")
    results = []

    files = []
    for root, dirs, filenames in os.walk(input_folder):
        for f in filenames:
            if f.lower().endswith(".json"):
                files.append(os.path.join(root, f))

    print(f"Found {len(files)} JSON files.")

    for i, json_file in enumerate(files):
        res = validate_file(json_file)
        if res:
            results.append(res)

        if (i + 1) % 10 == 0:
            print(f"Processed {i+1}/{len(files)}")

    # Write Results to CSV
    if results:
        fieldnames = [
            "File",
            "Text Status",
            "Transaction Type",
            "Transaction Type (JSON)",
            "Transaction Type (Text)",
            "Trade Date",
            "Trade Date (JSON)",
            "Trade Date (Text)",
            "Settlement Date",
            "Settlement Date (JSON)",
            "Settlement Date (Text)",
            "ISIN Status",
            "ISIN (JSON)",
            "ISIN (Text)",
            # Numeric fields (JSON/Text)
            "Quantity (JSON)",
            "Quantity (Text)",
            "Foreign Unit Price (JSON)",
            "Foreign Unit Price (Text)",
            "Foreign Net Consideration (JSON)",
            "Foreign Net Consideration (Text)",
            "Net Consideration (JSON)",
            "Net Consideration (Text)",
            "Exec Commission (JSON)",
            "Exec Commission (Text)",
            "Foreign Gross Consideration (JSON)",
            "Foreign Gross Consideration (Text)",
            # String fields (JSON/Text)
            "Client name (JSON)",
            "Client name (Text)",
            "Name/ Security (JSON)",
            "Name/ Security (Text)",
            "Currency (JSON)",
            "Currency (Text)",
            "Generic Errors",
            "Error",
        ]
        try:
            # Ensure output directory exists
            out_dir = os.path.dirname(output_csv)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for data in results:
                    row = {k: data.get(k, "") for k in fieldnames}
                    writer.writerow(row)
            print(f"Successfully wrote results to {output_csv}")
        except Exception as e:
            print(f"Error writing CSV: {e}")

        # Generate Text Report
        if not output_report:
            base = os.path.splitext(os.path.basename(output_csv))[0]
            output_report = os.path.join(
                os.path.dirname(output_csv), f"{base}_report.txt"
            )
        generate_report(results, output_report)

        # Copy files with ambiguous date format to separate folder
        output_dir = os.path.dirname(output_csv)
        copy_ambiguous_date_files(results, input_folder, output_dir)

    else:
        print("No results to write.")


# ==============================================================================
# Execution Entry Point
# ==============================================================================

if __name__ == "__main__":
    # Define default paths
    default_input = "datasets/labels/Trade_Confirmation"
    reports_dir = os.path.join(os.path.dirname(__file__), "output", "reports")
    default_output = os.path.join(reports_dir, "validation_check_result.csv")

    process_folder(default_input, default_output)
