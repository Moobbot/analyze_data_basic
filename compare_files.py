import os
import config
import utils

def compare_directories(output_file=config.DEFAULT_OUTPUT_DIFF):
    dataset_files = utils.get_files_map(config.DATASET_DIR)
    label_files = utils.get_files_map(config.LABEL_DIR)

    dataset_bases = set(dataset_files.keys())
    label_bases = set(label_files.keys())

    # Files in Dataset but not in Label
    missing_in_label = dataset_bases - label_bases
    # Files in Label but not in Dataset
    missing_in_dataset = label_bases - dataset_bases

    lines = []
    lines.append("THỐNG KÊ KHÁC BIỆT FILE (So sánh theo tên file không tính đuôi mở rộng)")
    lines.append("=" * 80)
    lines.append(f"Tổng số file gốc (Dataset): {sum(len(v) for v in dataset_files.values())} file ({len(dataset_bases)} tên duy nhất)")
    lines.append(f"Tổng số file nhãn (Label): {sum(len(v) for v in label_files.values())} file ({len(label_bases)} tên duy nhất)")
    lines.append("-" * 80)
    
    lines.append(f"\n1. Có trong Dataset nhưng KHÔNG CÓ trong Label: {len(missing_in_label)} tên file")
    if missing_in_label:
        lines.append(f"{'Tên File':<60} | {'Đuôi':<10} | {'Kích thước'}")
        lines.append("-" * 90)
        for base in sorted(missing_in_label):
            # List all actual files with this base name
            for f in dataset_files[base]:
                full_path = os.path.join(config.DATASET_DIR, f)
                ext = os.path.splitext(f)[1].lower()
                try:
                    size_bytes = os.path.getsize(full_path)
                    readable_size = utils.format_size(size_bytes)
                except:
                    readable_size = "N/A"
                
                lines.append(f"{f:<60} | {ext:<10} | {readable_size}")
    else:
        lines.append("  (Không có)")

    lines.append(f"\n2. Có trong Label nhưng KHÔNG CÓ trong Dataset: {len(missing_in_dataset)} tên file")
    if missing_in_dataset:
        lines.append(f"{'Tên File':<60} | {'Đuôi':<10} | {'Kích thước'}")
        lines.append("-" * 90)
        for base in sorted(missing_in_dataset):
            for f in label_files[base]:
                full_path = os.path.join(config.LABEL_DIR, f)
                ext = os.path.splitext(f)[1].lower()
                try:
                    size_bytes = os.path.getsize(full_path)
                    readable_size = utils.format_size(size_bytes)
                except:
                    readable_size = "N/A"
                
                lines.append(f"{f:<60} | {ext:<10} | {readable_size}")
    else:
        lines.append("  (Không có)")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f"Report saved to {os.path.abspath(output_file)}")
    except Exception as e:
        print(f"Error writing report: {e}")

if __name__ == "__main__":
    compare_directories()
