# Schema Validation System

## Overview

Comprehensive schema validation system for broker transaction data. Validates JSON files against predefined schemas with type checking and format validation.

## Schema Types

### 1. Trade Information (I.1)

**File**: `lib/schemas/trade_information.json`  
**Fields**: 14 fields including:

- Trade date, Settlement date (MM/DD/YYYY format)
- Securities ID, Quantity (absolute value), Foreign Unit Price
- Transaction type, Client name, Currency
- Foreign/Net consideration, Accrued interest, Commission fees

**Use Case**: Buy/sell transactions, trade confirmations

### 2. Dividend Information (I.2)

**File**: `lib/schemas/dividend_information.json`  
**Fields**: 13 fields including:

- Ex-Date, Payment Date
- Securities ID, Dividend Rate, WHT Rate
- Units, Gross/Net Dividend amounts
- Client name, Account number

**Use Case**: Dividend payments and distributions

### 3. FX & TF (I.3)

**File**: `lib/schemas/fx_tf.json`  
**Fields**: 11 fields including:

- Trade/Settlement dates
- Currency Buy/Sell, Amount Buy/Sell
- Exchange Rate, Account numbers
- Client name, Remark

**Use Case**: Foreign exchange and transfer forward transactions

### 4. Others (I.4)

**File**: `lib/schemas/others.json`  
**Fields**: 17 fields including:

- Trade/Settlement dates, Description
- Securities ID, Transaction type
- Foreign amounts, Tax information
- Payment mode, SGD amounts

**Use Case**: Miscellaneous transactions not covered by other schemas

### 5. Positions (I.5)

**File**: `lib/schemas/positions.json`  
**Fields**: 11 fields including:

- Portfolio No., Type, Account No
- Quantity, Security ID/name
- Cost/Market price, Market value
- Accrued interest, Valuation date

**Use Case**: Portfolio position snapshots

### 6. Bank Account Transaction (I.6)

**File**: `lib/schemas/bank_account_transaction.json`  
**Fields**: 2 top-level + nested records

- Account no., Currency
- Records[] with: Date, Transaction type, Reference, Amounts, Value date, Balances

**Use Case**: Bank account statements and transaction histories

## Usage

### Command Line Validation

```bash
# Validate all JSON files in a folder
python tools/validate_schema.py --input datasets/labels/Trade_Confirmation --output output/validation_results.csv

# Validate dividend files
python tools/validate_schema.py --input datasets/labels/Dividend --output output/dividend_validation.csv
```

### Python API

```python
from lib import schema_validator

# Validate a single file
result = schema_validator.validate_file("path/to/file.json")
print(f"Valid: {result['is_valid']}")
print(f"Schema: {result['schema_detected']}")
print(f"Errors: {result['errors']}")

# Load and use schema directly
schema = schema_validator.load_schema("trade_information")
data = {"Trade date": "01/15/2026", ...}
is_valid, errors = schema_validator.validate_against_schema(data, schema)

# Detect schema type
schema_name = schema_validator.detect_schema_type(data)
```

## Field Type Validators

### Date Fields

- **Format**: MM/DD/YYYY (default)
- **Validation**: Valid date string, correct format
- **Example**: "01/15/2026"

### Number Fields

- **Subtypes**: float (default), int
- **Validation**: Numeric type, optional null check
- **Special**: Quantity uses absolute value transform
- **Example**: 123.45, -456.78

### Text Fields

- **Validation**: String type, optional pattern matching
- **Pattern example**: Currency codes (^[A-Z]{3}$)
- **Example**: "USD", "Client Name"

### Percentage Fields

- **Formats**: "96.126%" or numeric value
- **Validation**: Accepts string with % or number
- **Example**: "30%", 0.30, 3.5

### Mixed Type Fields

- **Allowed types**: Defined per field
- **Example**: Foreign Unit Price can be number (123.45) or percentage string ("96.126%")

## Schema Detection

The system automatically detects schema type based on field presence:

1. **Bank Account** - Has "Records" array with "Amounts" and "Balances"
2. **Dividend** - Has "Ex-Date" + "Payment Date" + "Dividend Rate"
3. **FX & TF** - Has "Currency Buy" + "Currency Sell"
4. **Positions** - Has "Portfolio No." + "Valuation date"
5. **Trade** - Has trade dates + "Securities ID" + "Foreign Unit Price"
6. **Others** - Has "Description" + "Trade date" (catch-all)

## Output Format

### CSV Output

Contains columns:

- **file**: Filename
- **schema_detected**: Detected schema type
- **is_valid**: true/false
- **errors**: Semicolon-separated error list

### Summary Report

Text file with:

- Total files processed
- Valid/Invalid counts
- Success rate percentage
- Schema type distribution
- Detailed list of invalid files with errors

## Integration

To integrate with existing validation pipeline:

```python
from lib import schema_validator

# In validate_file() function:
schema_name = schema_validator.detect_schema_type(data)
if schema_name:
    schema = schema_validator.load_schema(schema_name)
    is_valid, errors = schema_validator.validate_against_schema(data, schema)
    result_log["Schema Type"] = schema_name
    result_log["Schema Valid"] = is_valid
    result_log["Schema Errors"] = "; ".join(errors)
```

## Error Messages

Common validation errors:

- **"Date is null"** - Required date field missing
- **"Invalid date format, expected MM/DD/YYYY"** - Wrong date format
- **"Expected number, got str"** - Type mismatch
- **"Text does not match pattern ^[A-Z]{3}$"** - Invalid currency code
- **"Field is required but missing"** - Missing required field
- **"Unexpected fields found: ..."** - Extra fields not in schema

## Examples

See `lib/schemas/*.json` for complete schema definitions with field specifications, types, and validation rules.
