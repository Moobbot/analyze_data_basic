#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import pandas as pd
import json
import sys
from openpyxl import Workbook

sys.path.insert(0, str(Path(__file__).parent))
from broker_accuracy_common import (
    FX_TRADE_FIELDS,
    normalize_filename,
    calculate_field_accuracy,
    create_excel_report,
)

BASE_DIR = Path(__file__).parent
GT_DIR = BASE_DIR / "datasets" / "test-set-broker" / "labels" / "FX-FT"
MODEL_CSV = BASE_DIR / "danh_gia_ket_qua" / "fx_trade_2026_02_03.csv"
OUTPUT_DIR = BASE_DIR / "danh_gia_ket_qua" / "2026_02_04"
OUTPUT_FILE = OUTPUT_DIR / "accuracy_report_fx_trade.xlsx"


def load_gt():
    all_data = []
    for f in GT_DIR.glob("*.json"):
        data = json.load(open(f, encoding="utf-8"))
        if isinstance(data, list):
            for item in data:
                item["_filename"] = f.stem
                all_data.append(item)
        else:
            data["_filename"] = f.stem
            all_data.append(data)
    df = pd.DataFrame(all_data)
    df["_filename_normalized"] = df["_filename"].apply(normalize_filename)
    return df


def load_model():
    df = pd.read_csv(MODEL_CSV)
    df["_filename"] = df["_fileName"].apply(normalize_filename)
    df["_filename_normalized"] = df["_filename"].apply(normalize_filename)
    return df


def main():
    print("=" * 80)
    print("FX TRADE")
    print("=" * 80)
    gt = load_gt()
    model = load_model()
    matched = set(gt["_filename_normalized"].unique()) & set(
        model["_filename_normalized"].unique()
    )
    print(f"Matched: {len(matched)} files")
    results = []
    for field in FX_TRADE_FIELDS:
        if field in gt.columns or field in model.columns:
            results.append(calculate_field_accuracy(field, gt, model, matched))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    acc, prec, rec, f1 = create_excel_report(
        wb, gt, model, results, matched, FX_TRADE_FIELDS
    )
    wb.save(OUTPUT_FILE)
    print("=" * 80)
    print("OVERALL METRICS:")
    print("=" * 80)
    print(f"  Accuracy:  {acc:.2f}%")
    print(f"  Precision: {prec:.2f}%")
    print(f"  Recall:    {rec:.2f}%")
    print(f"  F1-Score:  {f1:.2f}%")
    print("=" * 80)
    print(f"Report: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
