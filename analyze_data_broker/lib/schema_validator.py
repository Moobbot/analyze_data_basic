# schema_validator.py
"""
Schema validation module for broker transaction data.
Validates JSON data against defined schemas with comprehensive type checking.
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional


# ==============================================================================
# Schema Loading
# ==============================================================================


def load_schema(schema_name: str) -> Optional[Dict]:
    """Load a schema JSON file by name."""
    schema_dir = os.path.join(os.path.dirname(__file__), "schemas")
    schema_path = os.path.join(schema_dir, f"{schema_name}.json")

    if not os.path.exists(schema_path):
        return None

    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading schema {schema_name}: {e}")
        return None


def get_all_schemas() -> Dict[str, Dict]:
    """Load all available schemas."""
    schema_names = [
        "trade_information",
        "dividend_information",
        "fx_tf",
        "others",
        "positions",
        "bank_account_transaction",
    ]

    schemas = {}
    for name in schema_names:
        schema = load_schema(name)
        if schema:
            schemas[name] = schema

    return schemas


# ==============================================================================
# Type Validators
# ==============================================================================


def validate_date(value: Any, date_format: str = "MM/DD/YYYY") -> Tuple[bool, str]:
    """
    Validate date value and format.

    Args:
        value: The value to validate
        date_format: Expected date format (default: MM/DD/YYYY)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None:
        return False, "Date is null"

    if not isinstance(value, str):
        return False, f"Date must be string, got {type(value).__name__}"

    # Convert schema format to strptime format
    strptime_format = (
        date_format.replace("MM", "%m").replace("DD", "%d").replace("YYYY", "%Y")
    )

    try:
        datetime.strptime(value, strptime_format)
        return True, ""
    except ValueError:
        return False, f"Invalid date format, expected {date_format}"


def validate_number(
    value: Any, subtype: str = "float", allow_null: bool = False
) -> Tuple[bool, str]:
    """
    Validate numeric value.

    Args:
        value: The value to validate
        subtype: Type of number (float or int)
        allow_null: Whether null values are allowed

    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None:
        if allow_null:
            return True, ""
        return False, "Number cannot be null"

    if not isinstance(value, (int, float)):
        return False, f"Expected number, got {type(value).__name__}"

    if subtype == "int" and not isinstance(value, int):
        if not (isinstance(value, float) and value.is_integer()):
            return False, "Expected integer"

    return True, ""


def validate_text(
    value: Any, allow_null: bool = False, pattern: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Validate text/string value.

    Args:
        value: The value to validate
        allow_null: Whether null values are allowed
        pattern: Optional regex pattern to match

    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None:
        if allow_null:
            return True, ""
        return False, "Text cannot be null"

    if not isinstance(value, str):
        return False, f"Expected string, got {type(value).__name__}"

    if pattern:
        if not re.match(pattern, value):
            return False, f"Text does not match pattern {pattern}"

    return True, ""


def validate_percentage(value: Any) -> Tuple[bool, str]:
    """
    Validate percentage value (can be string like "96.126%" or number).

    Args:
        value: The value to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None:
        return False, "Percentage cannot be null"

    # Allow numeric values
    if isinstance(value, (int, float)):
        return True, ""

    # Allow percentage strings
    if isinstance(value, str):
        if value.strip().endswith("%"):
            # Try to parse the numeric part
            try:
                float(value.strip().rstrip("%"))
                return True, ""
            except ValueError:
                return False, "Invalid percentage format"
        else:
            # Try to parse as number string
            try:
                float(value)
                return True, ""
            except ValueError:
                return False, "Invalid percentage value"

    return False, f"Expected number or percentage string, got {type(value).__name__}"


def validate_mixed(
    value: Any, allowed_types: List[str], allow_null: bool = False
) -> Tuple[bool, str]:
    """
    Validate mixed type field that can be one of multiple types.

    Args:
        value: The value to validate
        allowed_types: List of allowed type names
        allow_null: Whether null values are allowed

    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None:
        if allow_null:
            return True, ""
        return False, "Value cannot be null"

    for type_name in allowed_types:
        if type_name == "number_float":
            if isinstance(value, (int, float)):
                return True, ""
        elif type_name == "text_percentage":
            if isinstance(value, str) and (
                "%" in value or value.replace(".", "").replace("-", "").isdigit()
            ):
                return True, ""
        elif type_name == "text":
            if isinstance(value, str):
                return True, ""

    return False, f"Value does not match any allowed types: {allowed_types}"


# ==============================================================================
# Field Validation
# ==============================================================================


def validate_field(field_name: str, field_schema: Dict, value: Any) -> Tuple[bool, str]:
    """
    Validate a single field against its schema definition.

    Args:
        field_name: Name of the field
        field_schema: Schema definition for the field
        value: The actual value to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    field_type = field_schema.get("type")
    required = field_schema.get("required", False)
    nullable = field_schema.get("nullable", False)

    # Check required fields
    if value is None and required and not nullable:
        return False, f"{field_name} is required but missing"

    # Allow null for nullable fields
    if value is None and nullable:
        return True, ""

    # Skip validation if field is optional and missing
    if value is None and not required:
        return True, ""

    # Type-specific validation
    if field_type == "date":
        date_format = field_schema.get("format", "MM/DD/YYYY")
        return validate_date(value, date_format)

    elif field_type == "number":
        subtype = field_schema.get("subtype", "float")
        return validate_number(value, subtype, nullable)

    elif field_type == "text":
        pattern = field_schema.get("validation", {}).get("pattern")
        return validate_text(value, nullable, pattern)

    elif field_type == "mixed":
        allowed_types = field_schema.get("allowed_types", [])
        return validate_mixed(value, allowed_types, nullable)

    elif field_type == "array":
        if not isinstance(value, list):
            return False, f"Expected array, got {type(value).__name__}"
        # Validate array items if item_schema is defined
        item_schema = field_schema.get("item_schema")
        if item_schema:
            for i, item in enumerate(value):
                if item_schema.get("type") == "object":
                    for item_field_name, item_field_schema in item_schema.get(
                        "fields", {}
                    ).items():
                        item_value = (
                            item.get(item_field_name)
                            if isinstance(item, dict)
                            else None
                        )
                        is_valid, error = validate_field(
                            item_field_name, item_field_schema, item_value
                        )
                        if not is_valid:
                            return False, f"Array item {i}: {error}"
        return True, ""

    else:
        return False, f"Unknown field type: {field_type}"

    return True, ""


# ==============================================================================
# Schema Validation
# ==============================================================================


def validate_against_schema(data: Dict, schema: Dict) -> Tuple[bool, List[str]]:
    """
    Validate data against a schema.

    Args:
        data: The data to validate
        schema: The schema definition

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    if not isinstance(data, dict):
        return False, [f"Data must be a dictionary, got {type(data).__name__}"]

    fields = schema.get("fields", {})

    # Validate each field in schema
    for field_name, field_schema in fields.items():
        value = data.get(field_name)
        is_valid, error = validate_field(field_name, field_schema, value)

        if not is_valid:
            errors.append(f"{field_name}: {error}")

    # Check for unexpected fields (optional warning)
    data_fields = set(data.keys())
    schema_fields = set(fields.keys())
    unexpected = data_fields - schema_fields

    if unexpected:
        errors.append(f"Unexpected fields found: {', '.join(unexpected)}")

    return len(errors) == 0, errors


# ==============================================================================
# Schema Detection
# ==============================================================================


def detect_schema_type(data: Dict) -> Optional[str]:
    """
    Detect which schema type a data dictionary matches best.
    Uses case-insensitive field matching for robustness.

    Args:
        data: The data to analyze

    Returns:
        Schema name or None if no match
    """
    if not isinstance(data, dict):
        return None

    # Create case-insensitive field lookup
    data_fields_lower = {k.lower(): k for k in data.keys()}

    def has_field(field_name: str) -> bool:
        """Check if field exists (case-insensitive)"""
        return field_name.lower() in data_fields_lower

    # Bank Account Transaction - Check for flat array structure (Account Statements)
    # Account Statements are stored as array of records with Account no., Currency, Date, Transaction type, etc
    if (
        has_field("Account no.")
        and has_field("Currency")
        and has_field("Date")
        and has_field("Transaction type")
        and has_field("Balances")
    ):
        return "bank_account_transaction"

    # Bank Account Transaction - nested structure with Records array
    if has_field("Account no.") and has_field("Records"):
        records = data.get("Records") or data.get("records")
        if isinstance(records, list) and len(records) > 0:
            if isinstance(records[0], dict):
                rec_fields_lower = {k.lower(): k for k in records[0].keys()}
                if "amounts" in rec_fields_lower and "balances" in rec_fields_lower:
                    return "bank_account_transaction"

    # Dividend - has Ex-Date, Payment Date, Dividend Rate, WHT
    if (
        has_field("Ex-Date")
        and has_field("Payment Date")
        and has_field("Dividend Rate")
    ):
        return "dividend_information"

    # FX & TF - has Currency Buy/Sell and Amount Buy/Sell
    if has_field("Currency Buy") and has_field("Currency Sell"):
        return "fx_tf"

    # Positions - has Portfolio No., Valuation date
    if has_field("Portfolio No.") and has_field("Valuation date"):
        return "positions"

    # Others - catch-all for miscellaneous (has Description field typically)
    # Check this BEFORE trade_information to avoid misclassification of bonus issues, etc.
    if has_field("Description") and (
        has_field("Trade date") or has_field("Trade Date")
    ):
        return "others"

    # Trade Information - has Trade date, Settlement date, Securities ID
    if (
        (has_field("Trade date") or has_field("Trade Date"))
        and (has_field("Settlement date") or has_field("Settlement Date"))
        and has_field("Securities ID")
    ):
        if (
            has_field("Foreign Unit Price")
            or has_field("Foreign Gross consideration")
            or has_field("Foreign Gross Consideration")
        ):
            return "trade_information"

    return None


# ==============================================================================
# Batch Validation
# ==============================================================================


def validate_file(file_path: str) -> Dict[str, Any]:
    """
    Validate a JSON file against appropriate schema.
    Handles both single records and arrays of records.

    Args:
        file_path: Path to JSON file

    Returns:
        Dictionary with validation results
    """
    result = {
        "file": os.path.basename(file_path),
        "schema_detected": None,
        "is_valid": False,
        "errors": [],
    }

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Special handling for Account Statements - flat array structure
        if isinstance(data, list) and data:
            # Check if this is Account Statements format
            first_item = data[0]
            if isinstance(first_item, dict):
                # Try to detect schema from first item
                schema_name = detect_schema_type(first_item)

                if schema_name == "bank_account_transaction":
                    # Validate each record in the array
                    result["schema_detected"] = schema_name
                    schema = load_schema(schema_name)

                    if not schema:
                        result["errors"].append(f"Schema {schema_name} not found")
                        return result

                    # Validate all records
                    all_valid = True
                    for i, record in enumerate(data):
                        # For flat array, validate each record against the item_schema fields
                        # We need to validate against the individual record structure
                        record_errors = []

                        # Check required fields for Account Statements
                        required_fields = [
                            "Account no.",
                            "Currency",
                            "Date",
                            "Transaction type",
                            "Balances",
                        ]
                        for field in required_fields:
                            if field not in record or record[field] is None:
                                if (
                                    field != "Value date" and field != "Amounts"
                                ):  # These can be null for opening/closing balance
                                    record_errors.append(
                                        f"Record {i}: {field} is required"
                                    )

                        if record_errors:
                            all_valid = False
                            result["errors"].extend(record_errors)

                    result["is_valid"] = all_valid
                    return result
                else:
                    # Regular array handling (wrapped single object)
                    data = first_item
            else:
                result["errors"].append(
                    f"JSON Root is an array, but first item is {type(first_item).__name__}, expected dict"
                )
                return result
        elif isinstance(data, list) and not data:
            result["errors"].append("Empty JSON array")
            return result

        # Ensure root element is a dictionary
        if not isinstance(data, dict):
            result["errors"].append(
                f"JSON Root is {type(data).__name__}, expected dict"
            )
            return result

        # Detect schema
        schema_name = detect_schema_type(data)
        result["schema_detected"] = schema_name

        if not schema_name:
            result["errors"].append("Could not detect schema type")
            return result

        # Load and validate
        schema = load_schema(schema_name)
        if not schema:
            result["errors"].append(f"Schema {schema_name} not found")
            return result

        is_valid, errors = validate_against_schema(data, schema)
        result["is_valid"] = is_valid
        result["errors"] = errors

    except Exception as e:
        result["errors"].append(f"Exception: {str(e)}")

    return result


if __name__ == "__main__":
    # Test schema loading
    schemas = get_all_schemas()
    print(f"Loaded {len(schemas)} schemas:")
    for name in schemas.keys():
        print(f"  - {name}")
