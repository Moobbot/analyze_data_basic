import csv
import sys
from pathlib import Path
from collections import defaultdict

import config


def generate_status_report(csv_path_str=None):
    if csv_path_str:
        csv_path = Path(csv_path_str)
    else:
        # Try to find the latest report or default path
        # User mentioned: output_analyze/data-all/reports-1/label_verification.csv
        # Let's check config path first
        csv_path = config.VERIFY_REPORT_CSV

        # If config path doesn't exist, check specifically requested path structure if possible or warn
        if not csv_path.exists():
            # Fallback to try finding in output_analyze/data-all/reports*/label_verification.csv
            candidates = list(config.REVIEW_DIR.glob("**/label_verification.csv"))
            if candidates:
                csv_path = candidates[0]  # Pick first found

    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        return

    print(f"Reading verification data from: {csv_path}")

    # Data aggregation
    stats = defaultdict(int)
    details_by_status = defaultdict(list)

    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                status = row["Status"]
                stats[status] += 1

                # Store snippet for detailed report (e.g., up to 10 examples per status or all?)
                # User asked for "statistical report for each status".
                # Likely wants counts + maybe list of broken items if small, but if large just counts.
                # Or maybe grouping by Field Key or File?
                # Let's do a summary count + breakdown by Key frequency for issues.

                details_by_status[status].append(row)

    except Exception as e:
        print(f"Error reading SCV: {e}")
        return

    # Generate Output Report
    # Generate Output Report
    output_report = config.STATUS_STATS_REPORT

    with open(output_report, "w", encoding="utf-8") as f:
        f.write("DETAILED STATUS STATISTICS REPORT\n")
        f.write("=" * 60 + "\n")
        f.write(f"Source CSV: {csv_path}\n")
        f.write(f"Total Entries: {sum(stats.values())}\n\n")

        f.write("1. SUMMARY BY STATUS\n")
        f.write("-" * 30 + "\n")
        maxlen = max([len(k) for k in stats.keys()] + [0])
        for status, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{status.ljust(maxlen)} : {count}\n")
        f.write("\n")

        f.write("2. DETAILED BREAKDOWN\n")
        f.write("=" * 60 + "\n")

        # Breakdown for non-perfect statuses
        # FOUND is usually fine, maybe skip details unless requested?
        # Let's detail MISSING, SIMILAR, and maybe others.

        priority_statuses = [
            "MISSING",
            "SIMILAR",
            "CHECK_DATE",
            "FOUND_DATE_ALT_FORMAT",
        ]

        for status in priority_statuses:
            if status not in stats or stats[status] == 0:
                continue

            items = details_by_status[status]
            f.write(f"\n>>> STATUS: {status} ({len(items)} items)\n")
            f.write("-" * 40 + "\n")

            # Analyze by Key
            key_counts = defaultdict(int)
            for item in items:
                key_counts[item["Key"]] += 1

            f.write("Top Affected Fields:\n")
            for k, v in sorted(key_counts.items(), key=lambda x: x[1], reverse=True)[
                :10
            ]:
                f.write(f"   - {k}: {v}\n")

            if len(key_counts) > 10:
                f.write(f"   ... and {len(key_counts)-10} other keys.\n")

            f.write("\nSample Entries (First 5):\n")
            for item in items[:5]:
                f.write(f"   - File: {item['Filename']}\n")
                f.write(f"     Key : {item['Key']}\n")
                f.write(f"     Val : {item['Value']}\n")
                if "BestMatchLine" in item and item["BestMatchLine"]:
                    f.write(f"     Match: {item['BestMatchLine']}\n")
                f.write("\n")

    print(f"Report generated: {output_report}")


if __name__ == "__main__":
    target_csv = sys.argv[1] if len(sys.argv) > 1 else None
    generate_status_report(target_csv)
