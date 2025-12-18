import os
import config
import utils

def merge(report_path=config.DEFAULT_OUTPUT_REPORT, diff_path=config.DEFAULT_OUTPUT_DIFF, output_path=config.DEFAULT_OUTPUT_FINAL):
    report_content = utils.read_file(report_path)
    diff_content = utils.read_file(diff_path)

    final_lines = []
    final_lines.append("BÁO CÁO TỔNG HỢP DỮ LIỆU (DATA REPORT)")
    final_lines.append("=" * 80)
    final_lines.append("Thời gian tạo: " + os.popen('date /t').read().strip() + " " + os.popen('time /t').read().strip())
    final_lines.append("=" * 80)
    
    final_lines.append("\nI. THỐNG KÊ CHI TIẾT (STATISTICS)")
    final_lines.append("-" * 80)
    final_lines.append(report_content)
    
    final_lines.append("\n\n" + "=" * 80)
    final_lines.append("II. SO SÁNH & KHÁC BIỆT FILE (FILE DIFFERENCES)")
    final_lines.append("-" * 80)
    final_lines.append(diff_content)
    
    final_lines.append("\n\n" + "=" * 80)
    final_lines.append("KẾT THÚC BÁO CÁO")

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(final_lines))
        print(f"Final summary created successfully at:\n{output_path}")
    except Exception as e:
        print(f"Error writing final summary: {e}")

if __name__ == "__main__":
    merge()
