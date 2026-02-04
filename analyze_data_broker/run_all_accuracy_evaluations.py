#!/usr/bin/env python3
"""
Run all broker accuracy evaluations
"""

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent

scripts = [
    ("Contract Note", "calculate_accuracy_contract_note.py"),
    ("Dividend Advice", "calculate_accuracy_dividend.py"),
    ("FX Trade", "calculate_accuracy_fx_trade.py"),
    ("Interest Payment", "calculate_accuracy_interest.py"),
    ("Trade Confirmation", "calculate_accuracy_trade_conf.py"),
]

print("=" * 80)
print("RUNNING ALL BROKER ACCURACY EVALUATIONS")
print("=" * 80)
print()

results = {}

for name, script in scripts:
    script_path = BASE_DIR / script

    if not script_path.exists():
        print(f"⚠️  {name}: Script not found - {script}")
        results[name] = "SKIPPED"
        continue

    print(f"Running {name}...")
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            cwd=str(BASE_DIR),
        )

        if result.returncode == 0:
            print(f"✓ {name}: SUCCESS")
            results[name] = "SUCCESS"
        else:
            print(f"✗ {name}: FAILED")
            print(f"  Error: {result.stderr[:200]}")
            results[name] = "FAILED"
    except Exception as e:
        print(f"✗ {name}: ERROR - {e}")
        results[name] = "ERROR"

    print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
for name, status in results.items():
    symbol = "✓" if status == "SUCCESS" else "✗" if status == "FAILED" else "⚠️"
    print(f"{symbol} {name}: {status}")
print("=" * 80)
