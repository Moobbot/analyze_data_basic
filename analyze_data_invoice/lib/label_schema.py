"""
Schema definition for Invoice JSON labels.
Used for validation scripts to ensure data integrity.
"""

INVOICE_SCHEMA = {
    "Type": {"type": str, "required": True},
    "No": {
        "type": str,
        "required": True,
        "nullable": True,
    },  # Sometimes No is null if not found? Assume str for now based on files.
    "Date": {
        "type": str,
        "required": True,
        "pattern": r"^\d{2}/\d{2}/\d{4}$",  # MM/DD/YYYY
        "description": "Date must be in MM/DD/YYYY format",
    },
    "Customer": {"type": str, "required": False, "nullable": True},
    "Supplier": {"type": str, "required": False, "nullable": True},
    "Currency": {"type": str, "required": False, "nullable": True},
    "Ex rate": {"type": (int, float), "required": False, "nullable": True},
    "Ex rate to SGD": {"type": (int, float), "required": False, "nullable": True},
    # Description List
    "Description": {
        "type": list,
        "required": True,
        "item_schema": {
            "text": {"type": str, "required": False, "nullable": True},
            "Amount (before tax)": {
                "type": (int, float),
                "required": False,
                "nullable": True,
            },
            "Tax amount": {"type": (int, float), "required": False, "nullable": True},
            "Amount (after GST)": {
                "type": (int, float),
                "required": False,
                "nullable": True,
            },
            "Amount in SGD": {
                "type": (int, float),
                "required": False,
                "nullable": True,
            },
            "Tax amount in SGD": {
                "type": (int, float),
                "required": False,
                "nullable": True,
            },
            "Amount after tax in SGD": {
                "type": (int, float),
                "required": False,
                "nullable": True,
            },
            "Project code": {"type": str, "required": False, "nullable": True},
            "Tax type": {"type": str, "required": False, "nullable": True},
        },
    },
}
