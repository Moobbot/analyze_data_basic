# Check Data Table

Data processing and validation tools for financial documents (Trade Confirmations, Contact Notes, etc.)

> **📖 v2.0 Update:** Module refactored to use shared `common_lib/`. See [RUNNING_GUIDE_BROKER.md](../RUNNING_GUIDE_BROKER.md) for detailed guide.

## Project Structure

```
analyze_data_broker/
├── scripts/           # Main executable scripts
├── lib/              # Core library modules
│   ├── utils.py      # Refactored utilities (uses common_lib)
│   ├── config.py
│   ├── validation_config.py
│   └── validation_logic.py
├── tools/            # Utility tools and one-time fixes
├── output/           # Generated outputs
│   ├── reports/      # Validation and verification reports
│   ├── exports/      # Excel exports
│   └── analysis/     # Analysis results
├── datasets/         # Data files
└── README.md

../common_lib/        # Shared Utilities (v2.0)
├── __init__.py
├── text_utils.py     # Shared text processing
├── file_utils.py     # Shared file operations
├── date_utils.py     # Shared date parsing
└── pdf_utils.py      # Shared PDF extraction
```

> **Note:** After v2.0 refactoring, common utilities are shared via `common_lib/`. See [RUNNING_GUIDE_BROKER.md](../RUNNING_GUIDE_BROKER.md) for details.

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

### Broker-Specific (lib/)

- `lib/utils.py` - Broker utilities (refactored to use common_lib v2.0)
- `lib/config.py` - Project configuration
- `lib/validation_config.py` - Validation rules and keywords
- `lib/validation_logic.py` - Validation logic implementation

### Shared Utilities (common_lib/)

After v2.0 refactoring, common utilities are centralized:

- `common_lib/text_utils.py` - Text normalization, formatting
- `common_lib/file_utils.py` - File operations, directory management
- `common_lib/date_utils.py` - Date parsing & validation (20+ formats)
- `common_lib/pdf_utils.py` - PDF text extraction (PyMuPDF)

**Usage:**

```python
# Import from common_lib
from common_lib import normalize_text, validate_date

# Or via broker utils (backward compatible)
from lib import utils
text = utils.normalize_text("...")
```

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
- Dependencies managed via root `requirements.txt`

```bash
# Install from project root
cd d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic
pip install -r requirements.txt
```

**Core dependencies:**

- `pymupdf` (optional, for PDF extraction via common_lib)
- `openpyxl` (for Excel exports)

> **Note:** v2.0 uses centralized dependency management. Common utilities shared via `common_lib/`.

## Notes

- All scripts support both single file and folder processing
- Scripts preserve folder structure when using `--output`
- JSON files are formatted with 2-space indentation
- UTF-8 encoding is used throughout
