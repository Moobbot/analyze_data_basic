# check_transaction_type.py
# ==============================================================================
# Main Controller Script
# ==============================================================================

import os
import json
import csv
import config
import validation_logic  # Import the new validation logic module

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
        filename = os.path.basename(json_path)
        name_no_ext = os.path.splitext(filename)[0]

        # Determine text path based on known directory structure
        if "datasets\\true\\labels" in json_path:
            txt_path = json_path.replace(
                "datasets\\true\\labels", "output_analyze\\datasets\\extracted_text"
            )
            txt_path = txt_path.replace(".json", ".txt")
        elif "datasets/true/labels" in json_path:
            txt_path = json_path.replace(
                "datasets/true/labels", "output_analyze/datasets/extracted_text"
            )
            txt_path = txt_path.replace(".json", ".txt")
        else:
            # Fallback logic
            parent_dir = os.path.basename(base_dir)  # e.g., Trade_Confirmation
            txt_path = os.path.join(
                config.EXTRACTED_TEXT_DIR, parent_dir, name_no_ext + ".txt"
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

        string_fields = ["Client name", "Name/ Security", "Currency"]
        for f in string_fields:
            validation_logic.check_generic_field(f, data, str, result_log)

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
    date_pass = sum(1 for r in results if r.get("Trade Date") == "PASS")
    date_warn = sum(1 for r in results if str(r.get("Trade Date")).startswith("WARN"))
    date_fail = sum(1 for r in results if str(r.get("Trade Date")).startswith("FAIL"))

    # ISIN Stats
    isin_pass = sum(1 for r in results if r.get("ISIN Status") == "PASS")
    isin_fail = sum(1 for r in results if str(r.get("ISIN Status")).startswith("FAIL"))
    isin_missing = sum(1 for r in results if r.get("ISIN Status") == "MISSING")

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
                f"Trade Date:       {date_pass} PASS, {date_fail} FAIL, {date_warn} WARN\n"
            )
            f.write(
                f"ISIN Status:      {isin_pass} PASS, {isin_fail} FAIL, {isin_missing} MISSING\n\n"
            )

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
            "Trade Date",
            "Settlement Date",
            "ISIN Status",
            "Generic Errors",
            "Error",
        ]
        try:
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
            output_report = output_csv.replace(".csv", "_report.txt")
        generate_report(results, output_report)

    else:
        print("No results to write.")


# ==============================================================================
# Execution Entry Point
# ==============================================================================

if __name__ == "__main__":
    # Define default paths
    default_input = r"d:\Work\Clients\AIRC\product\ACPA\check_data_table\datasets\labels\Trade_Confirmation"
    default_output = r"d:\Work\Clients\AIRC\product\ACPA\check_data_table\validation_check_result.csv"

    process_folder(default_input, default_output)
