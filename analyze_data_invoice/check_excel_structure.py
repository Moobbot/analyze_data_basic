#!/usr/bin/env python3
"""Check Excel file structure and find the row with the specific text"""

import pandas as pd
from pathlib import Path

# Read the Excel file
excel_path = (
    Path(__file__).parent
    / "danh_gia_ket_qua"
    / "2026_02_04"
    / "accuracy_report_test-set-100.xlsx"
)

# Check all sheets
xl_file = pd.ExcelFile(excel_path)
print(f"Sheet names: {xl_file.sheet_names}")
print()

# Read all sheets and search for the text
search_text = "100% Complete PM @ Impact 360 - V11 Physical [1] Completed On 12"

for sheet_name in xl_file.sheet_names:
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    print(f"\n{'='*80}")
    print(f"Sheet: {sheet_name}")
    print(f"{'='*80}")
    print(f"Total rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    # Search for the text in all columns
    found = False
    for idx, row in df.iterrows():
        for col in df.columns:
            val = str(row[col])
            if search_text in val:
                print(
                    f"\n*** FOUND at row {idx + 2} (Excel row, 1-indexed with header) ***"
                )
                print(f"Column: {col}")
                print(f"Full value: {val}")
                print(f"\nFull row details:")
                for c in df.columns:
                    print(f"  {c}: {row[c]}")
                found = True
                break
        if found:
            break

    if not found:
        print(f"\nText not found in sheet '{sheet_name}'")
