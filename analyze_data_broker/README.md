# Check Data Table

Data processing and validation tools for financial documents (Trade Confirmations, Contact Notes, etc.)

## Project Structure

```
check_data_table/
├── scripts/           # Main executable scripts
├── lib/              # Core library modules
├── tools/            # Utility tools and one-time fixes
├── output/           # Generated outputs
│   ├── reports/      # Validation and verification reports
│   ├── exports/      # Excel exports
│   └── analysis/     # Analysis results
├── datasets/         # Data files
└── README.md
```

## Main Scripts

### Data Cleaning

**clean_whitespace.py** - Clean whitespace from JSON files

```bash
# Process single file
python scripts/clean_whitespace.py datasets/labels/Contact_Note/0817.json

# Process entire folder
python scripts/clean_whitespace.py datasets/labels/Trade_Confirmation

# Output to different folder
python scripts/clean_whitespace.py datasets/labels/Trade_Confirmation --output cleaned_data
```

### Data Standardization

**standardize_transaction_type.py** - Standardize Transaction Type field

```bash
# Standardize transaction types (Purchase/Sale → BUY/SELL)
python scripts/standardize_transaction_type.py datasets/labels/Contact_Note

# Single file
python scripts/standardize_transaction_type.py datasets/labels/Contact_Note/0817.json
```

**reorder_json.py** - Reorder JSON keys to standard format

```bash
# Reorder keys in folder (overwrites)
python scripts/reorder_json.py datasets/labels/Trade_Confirmation datasets/labels/Trade_Confirmation

# Reorder with output to different folder
python scripts/reorder_json.py datasets/labels/Trade_Confirmation output/reordered
```

### Date Processing

**convert_date_format.py** - Convert date formats

```bash
# Convert dates in folder
python scripts/convert_date_format.py datasets/labels/Trade_Confirmation
```

**analyze_date_formats.py** - Analyze date formats in dataset

```bash
# Analyze date formats
python scripts/analyze_date_formats.py datasets/labels
```

### Export

**json_to_excel.py** - Export JSON to Excel

```bash
# Export folder to Excel
python scripts/json_to_excel.py datasets/labels/Trade_Confirmation output/exports/trades.xlsx
```

## Library Modules

- `lib/utils.py` - Utility functions (date parsing, file operations, text normalization)
- `lib/config.py` - Project configuration
- `lib/validation_config.py` - Validation rules and keywords
- `lib/validation_logic.py` - Validation logic implementation

## Tools

One-time fix and utility tools:

- `tools/fix_duplicate_keys.py` - Fix duplicate JSON keys
- `tools/wrap_json_arrays.py` - Wrap JSON objects in arrays
- `tools/extract_pdf.py` - Extract text from PDFs
- `tools/verify_date_conversion.py` - Verify date conversions
- `tools/update_account_numbers.py` - Update account numbers

## Common Workflows

### Complete Data Preparation

```bash
# 1. Clean whitespace
python scripts/clean_whitespace.py datasets/labels/Trade_Confirmation

# 2. Standardize transaction types
python scripts/standardize_transaction_type.py datasets/labels/Trade_Confirmation

# 3. Reorder JSON keys
python scripts/reorder_json.py datasets/labels/Trade_Confirmation datasets/labels/Trade_Confirmation

# 4. Convert date formats (if needed)
python scripts/convert_date_format.py datasets/labels/Trade_Confirmation
```

### Data Analysis

```bash
# Analyze date formats
python scripts/analyze_date_formats.py datasets/labels > output/analysis/date_analysis.txt

# Export to Excel for review
python scripts/json_to_excel.py datasets/labels/Trade_Confirmation output/exports/review.xlsx
```

## Requirements

- Python 3.7+
- No external dependencies (uses standard library only)

## Notes

- All scripts support both single file and folder processing
- Scripts preserve folder structure when using `--output`
- JSON files are formatted with 2-space indentation
- UTF-8 encoding is used throughout
