import os
import json
from collections import defaultdict

# Base path to the labels directory
labels_path = r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\analyze_data_broker\datasets\labels"
output_txt = (
    r"d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic\THONG_KE_GIAO_DICH.txt"
)


def count_transactions_in_file(file_path):
    """Count transactions (objects) in a JSON file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return len(data)
        else:
            return 1
    except:
        return 0


def generate_statistics():
    """Generate all statistics and write to text file"""

    # Collect data
    file_stats = []
    all_tx_counts = defaultdict(int)  # tx_count -> number of files
    type_stats = {}

    main_categories = [
        "Account_Statements",
        "Contact_Note",
        "Dividend",
        "FX-FT",
        "Trade_Confirmation",
        "Others_Template",
    ]

    print("🔍 Đang thu thập thông tin...")

    for category in main_categories:
        category_path = os.path.join(labels_path, category)
        type_stats[category] = {"files": 0, "transactions": 0}

        if category == "Others_Template":
            if os.path.exists(category_path):
                # Root level JSON files
                for file in sorted(os.listdir(category_path)):
                    if file.endswith(".json"):
                        file_path = os.path.join(category_path, file)
                        file_id = file.replace(".json", "")
                        count = count_transactions_in_file(file_path)

                        if count > 0:
                            file_stats.append(
                                {
                                    "type": category,
                                    "subtype": "Root",
                                    "file_id": file_id,
                                    "count": count,
                                }
                            )
                            all_tx_counts[count] += 1
                            type_stats[category]["files"] += 1
                            type_stats[category]["transactions"] += count

                # Subdirectories
                for subdir in sorted(os.listdir(category_path)):
                    subdir_path = os.path.join(category_path, subdir)
                    if os.path.isdir(subdir_path):
                        for file in sorted(os.listdir(subdir_path)):
                            if file.endswith(".json"):
                                file_path = os.path.join(subdir_path, file)
                                file_id = file.replace(".json", "")
                                count = count_transactions_in_file(file_path)

                                if count > 0:
                                    file_stats.append(
                                        {
                                            "type": category,
                                            "subtype": subdir,
                                            "file_id": file_id,
                                            "count": count,
                                        }
                                    )
                                    all_tx_counts[count] += 1
                                    type_stats[category]["files"] += 1
                                    type_stats[category]["transactions"] += count
        else:
            if os.path.exists(category_path):
                for file in sorted(os.listdir(category_path)):
                    if file.endswith(".json"):
                        file_path = os.path.join(category_path, file)
                        file_id = file.replace(".json", "")
                        count = count_transactions_in_file(file_path)

                        if count > 0:
                            file_stats.append(
                                {
                                    "type": category,
                                    "subtype": "",
                                    "file_id": file_id,
                                    "count": count,
                                }
                            )
                            all_tx_counts[count] += 1
                            type_stats[category]["files"] += 1
                            type_stats[category]["transactions"] += count

    total_files = sum(v["files"] for v in type_stats.values())
    total_tx = sum(v["transactions"] for v in type_stats.values())

    print(f"✍️  Đang ghi file thống kê...")

    # Write to text file
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("=" * 100 + "\n")
        f.write("THỐNG KÊ SỐ LƯỢNG GIAO DỊCH TRONG CÁC FILES\n")
        f.write("=" * 100 + "\n\n")

        # Overall summary
        f.write("📊 TÓNG HỢP CHUNG:\n")
        f.write("-" * 100 + "\n")
        f.write(f"Tổng files:           {total_files:,}\n")
        f.write(f"Tổng giao dịch:       {total_tx:,}\n")
        f.write(f"Trung bình tx/file:   {total_tx/total_files:.2f}\n")
        f.write(f"Giao dịch tối thiểu:  {min(all_tx_counts.keys())}\n")
        f.write(f"Giao dịch tối đa:     {max(all_tx_counts.keys())}\n")
        f.write("\n\n")

        # Chi tiết danh sách files theo số giao dịch
        f.write("📊 CHI TIẾT: FILE CÓ N GIAO DỊCH LÀ BAO NHIÊU FILE?\n")
        f.write("-" * 100 + "\n")

        for tx_count in sorted(all_tx_counts.keys()):
            file_count = all_tx_counts[tx_count]
            percentage = file_count / total_files * 100
            f.write(
                f"File có {tx_count:>3} giao dịch  : {file_count:>4} file(s)  ({percentage:>6.2f}%)\n"
            )

        f.write("\n\n")

        # By type
        f.write("📋 THỐNG KÊ THEO LOẠI GIAO DỊCH:\n")
        f.write("-" * 100 + "\n")
        f.write(
            f"{'Loại Giao Dịch':<30} {'Số Files':<15} {'Tổng TX':<15} {'Trung bình TX/File':<15}\n"
        )
        f.write("-" * 100 + "\n")

        for cat in main_categories:
            file_count = type_stats[cat]["files"]
            total = type_stats[cat]["transactions"]
            avg = total / file_count if file_count > 0 else 0
            f.write(f"{cat:<30} {file_count:<15} {total:<15} {avg:<15.2f}\n")

        f.write("-" * 100 + "\n")
        f.write(f"{'TỔNG CỘNG':<30} {total_files:<15} {total_tx:<15}\n")

        f.write("\n\n")

        # Files with multiple transactions
        multi_tx = [s for s in file_stats if s["count"] > 1]
        if multi_tx:
            f.write("🔍 DANH SÁCH CÁC FILES CÓ NHIỀU HƠN 1 GIAO DỊCH:\n")
            f.write("-" * 100 + "\n")
            f.write(f"{'Type':<30} {'SubType':<30} {'FileID':<15} {'TX Count':<15}\n")
            f.write("-" * 100 + "\n")

            for stat in sorted(multi_tx, key=lambda x: (-x["count"], x["file_id"])):
                type_name = stat["type"]
                subtype = stat["subtype"] if stat["subtype"] else ""
                file_id = stat["file_id"]
                tx_count = stat["count"]
                f.write(f"{type_name:<30} {subtype:<30} {file_id:<15} {tx_count:<15}\n")

    print(f"✅ Hoàn tất! File thống kê được lưu tại:")
    print(f"   {output_txt}")


if __name__ == "__main__":
    generate_statistics()
