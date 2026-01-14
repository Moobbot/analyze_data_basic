# Invoice Data Audit Pipeline

**Status:** Production Ready ✅

## Mục lục (Table of Contents)

- [Invoice Data Audit Pipeline](#invoice-data-audit-pipeline)
  - [Mục lục (Table of Contents)](#mục-lục-table-of-contents)
  - [Giới thiệu](#giới-thiệu)
  - [Cách chạy (Usage)](#cách-chạy-usage)
  - [Cấu trúc dự án](#cấu-trúc-dự-án)
  - [Luồng xử lý (Pipeline)](#luồng-xử-lý-pipeline)
  - [Ý nghĩa các báo cáo (Output Reports)](#ý-nghĩa-các-báo-cáo-output-reports)
  - [Cấu hình](#cấu-hình)
  - [Troubleshooting](#troubleshooting)
  - [Tài liệu tham khảo](#tài-liệu-tham-khảo)

## Giới thiệu

**Invoice Data Audit Tool** là hệ thống tự động hóa quy trình kiểm tra, đối soát và chuẩn hóa dữ liệu hóa đơn. Công cụ này giúp phát hiện các sai sót giữa dữ liệu nhãn (Label JSON) và dữ liệu gốc (PDF), đồng thời cung cấp các báo cáo chi tiết về chất lượng dữ liệu.

Các chức năng chính:

- **Làm sạch dữ liệu**: Chuẩn hóa định dạng JSON.
- **Trích xuất thông tin**: Lấy dữ liệu text từ PDF.
- **Đối soát (Verification)**: So sánh giá trị giữa Label và PDF (Fuzzy match, Date match, Numeric match).
- **Phân loại**: Tách các file lỗi, file thiếu dữ liệu.
- **Báo cáo**: Tổng hợp thống kê và sai lệch.

## Cách chạy (Usage)

```bash
# 1. Cài đặt thư viện
pip install -r requirements.txt

# 2. Chạy toàn bộ pipeline
python main.py

# 3. Các công cụ bổ trợ
# Kiểm tra JSON schema
python scripts/validate_json_schema.py

# Scan định dạng tiền tệ
python scripts/scan_currency_format.py
```

## Cấu trúc dự án

```
analyze_data_invoice/
├── main.py                    ← Script chính điều phối luồng xử lý
├── config.py                  ← File cấu hình đường dẫn
├── core/                      ← Các module xử lý chính
│   ├── cleaning.py           [Step 1] Clean JSON
│   ├── analysis.py           [Step 2] Analyze
│   ├── extraction.py         [Step 3] Extract PDFs
│   ├── verification.py       [Step 4] Verify labels
│   ├── separation.py         [Step 5] Separate files
│   ├── filtering.py          [Step 6] Filter
│   ├── comparison.py         [Step 7] Compare
│   └── deduplication.py      [Utility] Tìm file trùng lặp
├── reports/                   ← Module tạo báo cáo
├── lib/                       ← Thư viện tiện ích (common_lib)
├── scripts/                   ← Các script bổ trợ
├── datasets/                  ← Thư mục chứa dữ liệu đầu vào
└── output_analyze/            ← Thư mục chứa kết quả và báo cáo
```

## Luồng xử lý (Pipeline)

Hệ thống thực hiện 8 bước xử lý tuần tự sau:

| #   | Bước (Step) | Input         | Output              | Mô tả chi tiết                                              |
| --- | ----------- | ------------- | ------------------- | ----------------------------------------------------------- |
| 1   | Clean       | JSON files    | Cleaned JSON + log  | Chuẩn hóa kiểu dữ liệu, định dạng ngày tháng trong JSON.    |
| 2   | Analyze     | All files     | Statistics          | Thống kê số lượng, kích thước file, phát hiện trùng lặp.    |
| 3   | Extract     | PDFs          | Extracted text      | Dùng PyMuPDF để trích xuất text từ PDF phục vụ đối soát.    |
| 4   | Verify      | Text + Labels | Verification report | So khớp thông tin trong JSON với nội dung Text trong PDF.   |
| 5   | Separate    | Analysis      | Organized files     | Tách các file thiếu cặp (có JSON không PDF hoặc ngược lại). |
| 6   | Filter      | Verification  | Filtered results    | Lọc kết quả đối soát, tách các file đã verify thành công.   |
| 7   | Compare     | All files     | Differences         | So sánh tổng thể danh sách file giữa Dataset và Label.      |
| 8   | Report      | All data      | Final reports       | Tổng hợp tất cả các kết quả thành báo cáo cuối cùng.        |

> Xem chi tiết logic xử lý tại [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Ý nghĩa các báo cáo (Output Reports)

Sau khi chạy xong, các báo cáo sẽ được lưu tại `output_analyze/<dataset_name>/reports/`.

```
output_analyze/data-muti-page/reports/
├── 1_json_validation_log.txt
├── 2_data_statistics.csv
├── 2_data_summary_report.txt
├── 3_pdf_error_files.txt
├── 3_pdf_image_files.txt
├── 3_pdf_no_label_files.txt
├── 3_pdf_page_info.csv
├── 4_label_verification.csv
├── 4_label_verification_report.txt
├── 6_label_verification_missing.csv
├── 6_label_verification_similar.csv
├── 7_file_differences.txt
└── 8_final_summary.txt
```

Dưới đây là ý nghĩa của từng file:

1. `8_final_summary.txt`:

   - **Là gì**: Báo cáo tổng hợp quan trọng nhất.
   - **Nội dung**: Tóm tắt toàn bộ quá trình, số lượng file đã xử lý, số lượng lỗi phát hiện, và các thống kê chính. Nên đọc file này đầu tiên.

2. `4_label_verification_report.txt` (và `.csv`):

   - **Là gì**: Kết quả đối soát chi tiết từng trường (Field).
   - **Nội dung**: Cho biết trường nào trong JSON **không tìm thấy** (MISSING) hoặc **giống một phần** (SIMILAR) trong file PDF. Giúp phát hiện sai sót dữ liệu gán nhãn.

3. `7_file_differences.txt`:

   - **Là gì**: Báo cáo chênh lệch file.
   - **Nội dung**: Liệt kê danh sách các file có trong thư mục này nhưng thiếu trong thư mục kia (ví dụ: có PDF nhưng thiếu JSON nhãn).

4. `2_data_statistics.csv`:

   - **Là gì**: Thống kê thô.
   - **Nội dung**: Kích thước file, định dạng file, số lượng file theo từng loại.

5. `1_json_validation_log.txt`:

   - **Là gì**: Log sửa lỗi JSON.
   - **Nội dung**: Ghi lại các thay đổi đã thực hiện lên file JSON (ví dụ: sửa format ngày, convert số).

6. `3_pdf_no_label_files.txt`:

   - **Là gì**: Danh sách file PDF không tìm thấy Label tương ứng.
   - **Nội dung**: Các file ảnh/scan cần kiểm tra lại.

7. `6_label_verification_missing.csv`:
   - **Là gì**: Danh sách chi tiết các trường bị thiếu khi đối soát.
   - **Nội dung**: File CSV lọc riêng các lỗi MISSING để dễ review.

## Cấu hình

Tùy chỉnh đường dẫn và tham số tại `config.py`:

```python
# Input Directories
DATASET_DIR = "datasets/data-muti-page/files"      # Nơi chứa file PDF
LABEL_DIR = "datasets/data-muti-page/labels"       # Nơi chứa file JSON

# Output Directories
REVIEW_DIR = "output_analyze/data-muti-page"       # Nơi xuất báo cáo
```

## Troubleshooting

| Vấn đề (Problem)      | Nguyên nhân & Cách khắc phục (Fix)                                   |
| --------------------- | -------------------------------------------------------------------- |
| "Directory not found" | Kiểm tra lại đường dẫn trong `config.py`. Folder input phải tồn tại. |
| "Module not found"    | Chạy `pip install -r requirements.txt` để cài đủ thư viện.           |
| "Permission denied"   | Kiểm tra quyền ghi (write permission) của thư mục output.            |
| "No files found"      | Đảm bảo bạn đã copy PDF vào `DATASET_DIR` và JSON vào `LABEL_DIR`.   |

## Tài liệu tham khảo

- [Architecture Guide](docs/ARCHITECTURE.md): Tài liệu kỹ thuật chi tiết về kiến trúc hệ thống.
- [Supported Date Formats](docs/supported_date_formats.md): Danh sách các định dạng ngày tháng hệ thống hỗ trợ.
- [Common Data Errors](docs/COMMON_DATA_ERRORS.md): Các lỗi dữ liệu thường gặp cần lưu ý.
- [PDF Page Info Guide](docs/PDF_PAGE_INFO_GUIDE.md): Hướng dẫn sử dụng báo cáo thông tin trang PDF.
