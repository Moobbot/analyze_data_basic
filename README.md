# Invoice Data Audit Tool

Bộ công cụ tự động hóa việc phân tích, trích xuất và đối soát dữ liệu hóa đơn (PDF) với dữ liệu nhãn (JSON).

## Mục Lục

- [Mô Tả](#mô-tả)
- [Cài Đặt](#cài-đặt)
- [Cấu Hình](#cấu-hình)
- [Cấu Trúc Dự Án](#cấu-trúc-dự-án)
- [Hướng Dẫn Sử Dụng](#hướng-dẫn-sử-dụng)
- [Các Script Tiện Ích](#các-script-tiện-ích)
- [Ý Nghĩa Các Báo Cáo](#ý-nghĩa-các-báo-cáo)
- [Troubleshooting](#troubleshooting)

## Mô Tả

Project này cung cấp quy trình tự động để kiểm tra chất lượng dữ liệu hóa đơn:

1. **Thống kê file**: Đếm số lượng, kiểm tra định dạng, phát hiện file thiếu/thừa
2. **Sàng lọc**: Tự động di chuyển file không phù hợp (docx, missing label)
3. **Trích xuất PDF**: Sử dụng PyMuPDF để lấy nội dung text từ PDF
4. **Đối soát**: So sánh dữ liệu JSON với text trích xuất để tìm lỗi

### Tính Năng Chính

- ✅ Hỗ trợ nhiều định dạng ngày tháng (xem [supported_date_formats.md](supported_date_formats.md))
- ✅ Fuzzy matching thông minh cho text
- ✅ Xử lý số tiền với nhiều format (dấu phẩy, dấu chấm, accounting format)
- ✅ Phát hiện file trùng lặp dựa trên nội dung
- ✅ Báo cáo chi tiết theo từng trường dữ liệu

## Cài Đặt

### Yêu Cầu

- Python 3.10 trở lên
- Windows/Linux/macOS

### Các Bước Cài Đặt

1. Clone repository hoặc tải source code
2. Cài đặt dependencies:

```bash
pip install -r requirements.txt
```

Các thư viện chính:

- `pymupdf` - Trích xuất text từ PDF
- `pdfplumber` - Thư viện PDF bổ sung
- `PyPDF2` - Xử lý PDF cơ bản

## Cấu Hình

File cấu hình chính: [`config.py`](config.py)

### Các Thư Mục Quan Trọng

```python
# Thư mục nguồn
DATASET_DIR = "data_x/files"      # Chứa file PDF gốc
LABEL_DIR = "data_x/labels"       # Chứa file JSON nhãn

# Thư mục đầu ra
REVIEW_DIR = "output_analyze/data_x"           # Báo cáo và kết quả
EXTRACTED_TEXT_DIR = "output_analyze/data_2/extracted_text"  # Text đã trích xuất

# Thư mục phân loại
DEST_MISSING = "output_analyze/data_x/Files_Missing_In_Label"
DEST_DOCX = "output_analyze/data_x/Files_Docx"
PDF_ERROR_DIR = "output_analyze/data_x/PDF_Error_Files"
PDF_IMAGE_DIR = "output_analyze/data_x/PDF_Image_Files"
```

> **Lưu ý**: Tất cả đường dẫn đều relative từ thư mục gốc của project. Hệ thống tự động tạo các thư mục nếu chưa tồn tại.

## Cấu Trúc Dự Án

```
check_data_2025_12_19/
├── main.py                      # Unifed Entry Point (Chạy toàn bộ pipeline)
├── config.py                    # Cấu hình chính
├── utils.py                     # Hàm tiện ích dùng chung
├── requirements.txt             # Dependencies
│
├── core/                        # Core Logic Modules
│   ├── __init__.py
│   ├── analysis.py              # Thống kê file
│   ├── cleaning.py              # Làm sạch dữ liệu JSON (số, ngày)
│   ├── comparison.py            # So sánh Dataset vs Label
│   ├── deduplication.py         # Tìm file trùng lặp
│   ├── extraction.py            # Trích xuất text từ PDF
│   ├── filtering.py             # Lọc kết quả verification & labels
│   ├── separation.py            # Phân loại file (di chuyển file lỗi)
│   └── verification.py          # Đối soát dữ liệu (Logic chính)
│
├── reports/                     # Reporting Modules
│   ├── __init__.py
│   ├── generator.py             # Tạo báo cáo Markdown/HTML
│   └── merger.py                # Gộp báo cáo cuối cùng
│
├── scripts/                     # Standalone Utility Scripts
│   ├── __init__.py
│   ├── compare_pdf_libs.py      # So sánh thư viện PDF
│   ├── convert_jsonl.py         # Convert JSONL
│   ├── filter_comma_format.py   # Tìm format số có dấu phẩy
│   ├── move_files_for_verification.py  # Di chuyển file cần verify
│   └── open_pdf_by_json.py      # Mở PDF từ JSON path
│
├── Datasets/                    # Dữ liệu nguồn (Cấu hình trong config.py)
│   ├── data-all/dest/           # PDF files
│   └── data-all/labels/         # JSON labels
│
└── output_analyze/              # Kết quả đầu ra
    └── data-all/                # Báo cáo và file phân loại
```

## Hướng Dẫn Sử Dụng

### Workflow Cơ Bản (Recommended)

Cách đơn giản nhất là chạy toàn bộ quy trình bằng `main.py`:

```bash
python main.py
```

Pipeline sẽ tự động thực hiện tuần tự các bước:

1.  **Cleaning**: Chuẩn hóa format số và ngày trong JSON.
2.  **Analysis**: Thống kê file gốc.
3.  **Extraction**: Trích xuất text từ PDF.
4.  **Verification**: Đối soát dữ liệu (Fuzzy matching).
5.  **Separation**: Di chuyển các file lỗi/thiếu.
6.  **Filtering**: Lọc kết quả và tạo báo cáo chi tiết.
7.  **Comparison**: So sánh tổng quan Dataset vs Label.
8.  **Reporting**: Tổng hợp báo cáo cuối cùng.

**Kết quả đầu ra** (trong thư mục `output_analyze/data-all/reports/` và `review/`):

- `final_summary.txt`: Báo cáo tổng hợp.
- `label_verification_report.txt`: Chi tiết kết quả verify.
- `file_differences.txt`: Danh sách file lệch.
- `pdf_error_files.txt`, `pdf_image_files.txt`: Danh sách file lỗi/ảnh.

---

### Chạy Từng Module Riêng Lẻ (Advanced)

Nếu cần chạy riêng từng bước, bạn có thể gọi module qua flag `-m`:

#### 1. Cleaning Only

```bash
python -m core.cleaning
```

#### 2. Extraction Only

```bash
python -m core.extraction
```

_Lưu ý: Cần chạy Extraction trước khi Verification._

#### 3. Verification Only

```bash
python -m core.verification
```

#### 4. Tìm File Trùng Lặp

```bash
python -m core.deduplication
```

#### 5. Lọc Kết Quả Verify

```bash
python -m core.filtering
```

## Các Script Tiện Ích

Các script trong thư mục `scripts/` hỗ trợ các tác vụ đặc biệt:

### 1. Tìm Format Số Có Dấu Phẩy

```bash
python scripts/filter_comma_format.py [directory]
```

Tìm các file JSON có số dùng dấu phẩy (ví dụ: `12,00` thay vì `12.00`).

**Tham số**:

- `directory` (optional) - Thư mục chứa JSON, mặc định dùng `config.LABEL_DIR`

---

### 2. Di Chuyển File Cần Verification

```bash
python scripts/move_files_for_verification.py <json_file1> <json_file2> ...
```

Di chuyển JSON, PDF và TXT file tương ứng vào thư mục `verification_needed/` để review thủ công.

**Ví dụ**:

```bash
python scripts/move_files_for_verification.py "data_x/labels/invoice001.json"
```

---

### 3. Mở PDF và Text File

```bash
python scripts/open_pdf_by_json.py <json_file>
```

Mở JSON, PDF và TXT file tương ứng bằng ứng dụng mặc định của hệ thống.

**Ví dụ**:

```bash
python scripts/open_pdf_by_json.py "data_x/labels/invoice001.json"
```

## Ý Nghĩa Các Báo Cáo

### Trong thư mục `output_analyze/data_x/`

| File                             | Mô Tả                                        | Cách Sử Dụng                           |
| -------------------------------- | -------------------------------------------- | -------------------------------------- |
| `data_summary_report.txt`        | Thống kê tổng quan số lượng file, dung lượng | Kiểm tra tổng quan dữ liệu             |
| `file_differences.txt`           | File thiếu/thừa giữa Dataset và Label        | Xác định file cần bổ sung              |
| `pdf_error_files.txt`            | PDF không đọc được                           | Cần xử lý lại (OCR hoặc kiểm tra file) |
| `pdf_image_files.txt`            | PDF dạng ảnh/scan                            | Cần OCR để trích xuất text             |
| `label_verification.csv`         | Kết quả đối soát chi tiết                    | Phân tích từng trường dữ liệu          |
| `label_verification_missing.csv` | Trường KHÔNG tìm thấy                        | **Ưu tiên cao** - Cần kiểm tra kỹ      |
| `label_verification_similar.csv` | Trường TƯƠNG ĐỒNG                            | Review nhanh để xác nhận               |

### Báo Cáo Markdown

| File                         | Mô Tả                                |
| ---------------------------- | ------------------------------------ |
| `General_Overview_Report.md` | Tổng quan toàn bộ quy trình xử lý    |
| `Detailed_Error_Report.md`   | Chi tiết các lỗi và vấn đề cần xử lý |

## Troubleshooting

### Lỗi Thường Gặp

#### 1. "Directory not found"

**Nguyên nhân**: Đường dẫn trong `config.py` không đúng

**Giải pháp**:

```python
# Kiểm tra và cập nhật config.py
DATASET_DIR = os.path.join(BASE_DIR, "data_x", "files")
LABEL_DIR = os.path.join(BASE_DIR, "data_x", "labels")
```

---

#### 2. "No matching files found" trong verify_labels.py

**Nguyên nhân**: Text chưa được trích xuất hoặc file name không khớp

**Giải pháp**:

1. Chạy `extract_pdf.py` trước
2. Kiểm tra tên file PDF và JSON phải giống nhau (không tính extension)

---

#### 3. Nhiều trường bị MISSING

**Nguyên nhân**:

- PDF dạng ảnh/scan (không có text layer)
- Format ngày/số không được hỗ trợ
- OCR kém chất lượng

**Giải pháp**:

1. Kiểm tra `pdf_image_files.txt` - nếu file trong đó thì cần OCR
2. Xem [supported_date_formats.md](supported_date_formats.md) để biết format được hỗ trợ
3. Kiểm tra text file trong `Extracted_Text/` để xem chất lượng trích xuất

---

#### 4. Import Error khi chạy scripts/

**Nguyên nhân**: Python không tìm thấy module config hoặc utils

**Giải pháp**: Các script trong `scripts/` đã được cập nhật để tự động thêm parent directory vào path. Nếu vẫn lỗi, chạy từ thư mục gốc:

```bash
# Từ thư mục gốc của project
python scripts/filter_comma_format.py
```

---

### Tips & Best Practices

1. **Luôn chạy pipeline theo thứ tự**: analyze → extract → verify → filter
2. **Backup dữ liệu** trước khi chạy các script di chuyển file
3. **Review file SIMILAR** trước khi xử lý MISSING (thường chỉ khác format nhỏ)
4. **Kiểm tra encoding**: Đảm bảo file JSON và TXT đều dùng UTF-8

---

## Đóng Góp

Xem [ARCHITECTURE.md](ARCHITECTURE.md) để hiểu kiến trúc hệ thống trước khi đóng góp.

## License

[Thêm license information nếu cần]
