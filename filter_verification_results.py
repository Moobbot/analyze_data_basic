import csv
import os
import config

def filter_results():
    input_csv = config.VERIFY_REPORT_CSV
    
    if not os.path.exists(input_csv):
        print(f"Error: Input CSV not found: {input_csv}")
        return

    output_missing = os.path.join(config.REVIEW_DIR, "label_verification_missing.csv")
    output_similar = os.path.join(config.REVIEW_DIR, "label_verification_similar.csv")
    
    missing_rows = []
    similar_rows = []
    
    try:
        with open(input_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            for row in reader:
                status = row.get('Status', '')
                if status == 'MISSING':
                    missing_rows.append(row)
                elif status == 'SIMILAR':
                    similar_rows.append(row)
                    
        # Write Missing
        with open(output_missing, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(missing_rows)
        print(f"Created Missing Report: {output_missing} ({len(missing_rows)} rows)")

        # Write Similar
        with open(output_similar, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(similar_rows)
        print(f"Created Similar Report: {output_similar} ({len(similar_rows)} rows)")
            
    except Exception as e:
        print(f"Error processing CSV: {e}")

if __name__ == "__main__":
    filter_results()
