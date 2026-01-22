# Scripts Directory

This directory contains utility scripts for the analyze_data_broker module, organized into logical subdirectories:

## Directory Structure

### analysis/

Scripts for analyzing and debugging data:

- `analyze_date_formats.py` - Analyzes date format patterns in JSON files
- `analyze_validation_errors.py` - Comprehensive validation error analysis and reporting
- `compare_account_no.py` - Compares account number fields across files
- `debug_date.py` - Debug utility for date parsing issues

### cleaning/

Scripts that modify or clean data:

- `add_client_no_contact_note.py` - Extracts and updates account numbers from Contact Notes
- `clean_whitespace.py` - Removes extra whitespace from JSON files
- `clear_matching_account_no.py` - Clears matching account number fields
- `fix_duplicate_keys.py` - Fixes duplicate keys in JSON files
- `fix_remaining_dates.py` - Fixes remaining date format issues
- `patch_net_consideration.py` - Patches net consideration calculations
- `reorder_json.py` - Reorders JSON fields for consistency
- `standardize_transaction_type.py` - Standardizes transaction type values
- `update_account_numbers.py` - Updates account numbers using regex patterns
- `wrap_json_arrays.py` - Wraps JSON objects in arrays

### conversion/

Conversion and extraction scripts:

- `convert_date_format.py` - Converts dates to MM/DD/YYYY format
- `convert_jsonl.py` - Converts between JSON and JSONL formats
- `convert_string_to_number.py` - Converts string numbers to numeric types
- `extract_pdf.py` - Extracts text from PDF files using PyMuPDF
- `json_to_excel.py` - Exports JSON data to Excel format

### validation/

Validation scripts:

- `validate_schema.py` - Validates JSON files against schemas
- `verify_date_conversion.py` - Verifies date conversion results

### utils/

Helper utilities:

- `open_matching_pdfs.py` - Opens PDF files matching specific criteria

## Usage Notes

Most scripts support command-line arguments. Run with `--help` to see available options:

```bash
python scripts/analysis/analyze_validation_errors.py --help
```

## Important Path Considerations

Scripts in subdirectories have been updated to correctly reference the parent `analyze_data_broker` module. If you move scripts or create new ones, ensure `sys.path` is adjusted appropriately (typically 2 levels up from the script location).
