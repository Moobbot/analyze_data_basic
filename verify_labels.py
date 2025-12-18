import os
import json
import difflib
import csv
import config
import utils

def flatten_json(y):
    out = {}
    
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '.')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '.')
                i += 1
        else:
            out[name[:-1]] = x
            
    flatten(y)
    return out

def get_best_match(value, text_content):
    if not value or str(value).strip() == "":
        return "N/A", 0, ""

    val_str = str(value).strip()
    
    # 1. Exact Match case-sensitive
    if val_str in text_content:
        return "FOUND", 1.0, val_str

    # 2. Exact Match case-insensitive
    text_lower = text_content.lower()
    val_lower = val_str.lower()
    if val_lower in text_lower:
        return "FOUND_CASE_INSENSITIVE", 0.9, val_str

    # 3. Fuzzy Match
    # Split text into lines to compare against
    lines = [line.strip() for line in text_content.splitlines() if line.strip()]
    best_ratio = 0.0
    best_line = ""
    
    for line in lines:
        # Check similarity
        # ratio() returns float in [0, 1]
        ratio = difflib.SequenceMatcher(None, val_lower, line.lower()).ratio()
        
        # Checking substring fuzzy match might be better for long lines?
        # But let's stick to simple SequenceMatcher for now as per plan
        if ratio > best_ratio:
            best_ratio = ratio
            best_line = line
            
    if best_ratio >= 0.8:
        return "SIMILAR", best_ratio, best_line
    
    return "MISSING", best_ratio, best_line

def verify_labels():
    print(">>> STARTING LABEL VERIFICATION")
    
    # Ensure review dir exists
    utils.ensure_dir_exists(config.REVIEW_DIR)
    
    # Get JSON files
    if not os.path.exists(config.LABEL_DIR):
        print(f"Error: Label directory not found: {config.LABEL_DIR}")
        return

    json_files = [f for f in os.listdir(config.LABEL_DIR) if f.lower().endswith('.json')]
    total_files = len(json_files)
    print(f"Found {total_files} JSON label files.")
    
    results = []
    
    stats = {
        "Total Fields": 0,
        "Found": 0,
        "Similar": 0,
        "Missing": 0
    }

    for i, json_filename in enumerate(json_files):
        json_path = os.path.join(config.LABEL_DIR, json_filename)
        base_name = os.path.splitext(json_filename)[0]
        txt_filename = base_name + ".txt"
        txt_path = os.path.join(config.EXTRACTED_TEXT_DIR, txt_filename)
        
        # Read JSON
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading JSON {json_filename}: {e}")
            continue
            
        # Read Text
        text_content = utils.read_file(txt_path)
        if text_content.startswith("[Error"):
             # If text extracted failed or file missing, mark all as missing
             text_content = ""

        # Flatten JSON to get all values
        flat_data = flatten_json(data)
        
        for key, value in flat_data.items():
            if value is None or str(value).strip() == "":
                continue # Skip empty fields
                
            stats["Total Fields"] += 1
            
            status, score, match_text = get_best_match(value, text_content)
            
            if "FOUND" in status:
                stats["Found"] += 1
            elif status == "SIMILAR":
                stats["Similar"] += 1
            else:
                stats["Missing"] += 1
                
            results.append({
                "Filename": json_filename,
                "Key": key,
                "Value": str(value),
                "Status": status,
                "Score": f"{score:.2f}",
                "BestMatchLine": match_text if status != "FOUND" else "" 
            })
            
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{total_files} labels...")

    # Write CSV Report
    try:
        with open(config.VERIFY_REPORT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Filename', 'Key', 'Value', 'Status', 'Score', 'BestMatchLine']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r)
        print(f"Detailed verification CSV saved to: {config.VERIFY_REPORT_CSV}")
    except Exception as e:
        print(f"Error writing CSV report: {e}")

    # Write Summary Text Report
    try:
        with open(config.VERIFY_REPORT_TXT, 'w', encoding='utf-8') as f:
            f.write("BÁO CÁO ĐỐI SOÁT DỮ LIỆU LABEL VS EXTRACTED TEXT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Tổng số file Label: {total_files}\n")
            f.write(f"Tổng số trường dữ liệu (Fields) kiểm tra: {stats['Total Fields']}\n")
            f.write("-" * 40 + "\n")
            f.write(f"1. Tìm thấy chính xác (Found): {stats['Found']} ({stats['Found']/stats['Total Fields']*100:.2f}%)\n")
            f.write(f"2. Tương đồng (Similar > 80%): {stats['Similar']} ({stats['Similar']/stats['Total Fields']*100:.2f}%)\n")
            f.write(f"3. Không tìm thấy (Missing):    {stats['Missing']} ({stats['Missing']/stats['Total Fields']*100:.2f}%)\n")
            f.write("=" * 60 + "\n")
            f.write("Chi tiết xem tại file: label_verification.csv\n")
            
        print(f"Summary report saved to: {config.VERIFY_REPORT_TXT}")
    except Exception as e:
        print(f"Error writing TXT report: {e}")

if __name__ == "__main__":
    verify_labels()
