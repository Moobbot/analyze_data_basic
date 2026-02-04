#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculate accuracy for Contract Note documents
Compares ground truth JSON files with model CSV output
"""

import pandas as pd
import json
from pathlib import Path
from openpyxl import Workbook
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from broker_accuracy_common import (
    CONTRACT_NOTE_FIELDS,
    normalize_filename,
    calculate_field_accuracy,
    create_excel_report,
)

# Paths
BASE_DIR = Path(__file__).parent
GT_DIR = BASE_DIR / "datasets" / "test-set-broker" / "labels" / "Contact_Note"
MODEL_CSV = BASE_DIR / "danh_gia_ket_qua" / "contract_note_2026_02_03.csv"
OUTPUT_DIR = BASE_DIR / "danh_gia_ket_qua" / "2026_02_04"
OUTPUT_FILE = OUTPUT_DIR / "accuracy_report_contract_note.xlsx"


def load_ground_truth():
    """Load all ground truth JSON files"""
    print("[1/4] Loading ground truth...")

    all_data = []
    json_files = list(GT_DIR.glob("*.json"))

    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

            if isinstance(data, list):
                for item in data:
                    item["_filename"] = json_file.stem
                    all_data.append(item)
            else:
                data["_filename"] = json_file.stem
                all_data.append(data)

    df = pd.DataFrame(all_data)
    df["_filename_normalized"] = df["_filename"].apply(normalize_filename)

    print(f"  Loaded {len(df)} rows from {len(json_files)} JSON files")
    return df


def load_model_output():
    """Load model CSV output"""
    print("[2/4] Loading model output...")

    df = pd.read_csv(MODEL_CSV)

    column_mapping = {
        "Transaction type": "Transaction Type",
        "Trade date": "Trade Date",
        "Settlement date": "Settlement Date",
    }

    df = df.rename(columns=column_mapping)

    if "_fileName" in df.columns:
        df["_filename"] = df["_fileName"].apply(normalize_filename)
    else:
        raise ValueError("Model CSV missing _fileName column")

    df["_filename_normalized"] = df["_filename"].apply(normalize_filename)

    print(f"  Loaded {len(df)} rows from CSV")
    return df


def match_documents(gt_df, model_df):
    """Match ground truth and model documents by filename"""
    print("[3/4] Matching documents...")

    gt_files = set(gt_df["_filename_normalized"].unique())
    model_files = set(model_df["_filename_normalized"].unique())

    matched = gt_files & model_files
    missing_in_model = gt_files - model_files
    extra_in_model = model_files - gt_files

    print(f"  GT files: {len(gt_files)}")
    print(f"  Model files: {len(model_files)}")
    print(f"  Matched: {len(matched)}")

    if missing_in_model:
        print(f"  Missing in Model: {len(missing_in_model)}")

    if extra_in_model:
        print(f"  Extra in Model: {len(extra_in_model)}")

    return matched


def main():
    """Main execution"""
    print("=" * 80)
    print("CONTRACT NOTE ACCURACY EVALUATION")
    print("=" * 80)
    print()

    gt_df = load_ground_truth()
    model_df = load_model_output()

    matched_files = match_documents(gt_df, model_df)

    if len(matched_files) == 0:
        print("\nNo matched files found!")
        return

    print()
    print("[4/4] Calculating accuracy metrics...")
    results = []

    for field in CONTRACT_NOTE_FIELDS:
        if field not in gt_df.columns and field not in model_df.columns:
            continue

        print(f"  Evaluating: {field}")
        result = calculate_field_accuracy(field, gt_df, model_df, matched_files)
        results.append(result)

    print()
    print("[5/5] Creating Excel report...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    overall_acc, overall_prec, overall_rec, overall_f1 = create_excel_report(
        wb, gt_df, model_df, results, matched_files, CONTRACT_NOTE_FIELDS
    )

    wb.save(OUTPUT_FILE)
    print(f"  Report saved: {OUTPUT_FILE}")
    print()

    print("=" * 80)
    print("OVERALL METRICS:")
    print("=" * 80)
    print(f"  Accuracy:  {overall_acc:.2f}%")
    print(f"  Precision: {overall_prec:.2f}%")
    print(f"  Recall:    {overall_rec:.2f}%")
    print(f"  F1-Score:  {overall_f1:.2f}%")
    print("=" * 80)
    print()
    print(f"Contract Note accuracy report completed!")
    print(f"  Report: {OUTPUT_FILE}")
    print()


if __name__ == "__main__":
    main()
