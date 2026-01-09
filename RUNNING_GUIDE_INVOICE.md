# Hướng Dẫn Chạy - analyze_data_invoice

> **Công cụ phân tích dữ liệu hóa đơn (Invoice Data Audit Tool)**

## 🚀 Quick Start

### Chạy Toàn Bộ Pipeline (Recommended)

```bash
cd analyze_data_invoice
python main.py
```

Pipeline tự động thực hiện đầy đủ 8 bước:

1. **Cleaning** → Chuẩn hóa số và ngày
2. **Analysis** → Thống kê file
3. **Extraction** → Trích xuất text từ PDF
4. **Verification** → Đối soát dữ liệu
5. **Separation** → Phân loại file lỗi
6. **Filtering** → Lọc kết quả
7. **Comparison** → So sánh Dataset vs Label
8. **Reporting** → Tổng hợp báo cáo

---

## 📋 Yêu Cầu Hệ Thống

### Dependencies

```bash
# Cài đặt từ thư mục gốc
cd d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic
pip install -r analyze_data_invoice/requirements.txt
```

**Thư viện chính:**

- `pymupdf` (fitz) - Trích xuất text từ PDF
- Python 3.10+

### Cấu Trúc Thư Mục Bắt Buộc

```
analyze_data_invoice/
├── datasets/           # ← Đặt dữ liệu ở đây
│   ├── files/         # PDF files
│   └── labels/        # JSON labels
└── output_analyze/    # ← Kết quả tự động tạo
```

---

## ⚙️ Cấu Hình

### File: `config.py`

```python
# Thư mục nguồn
DATASET_DIR = Path(BASE_DIR) / "datasets" / "files"
LABEL_DIR = Path(BASE_DIR) / "datasets" / "labels"

# Thư mục đầu ra
REVIEW_DIR = Path(BASE_DIR) / "output_analyze"
EXTRACTED_TEXT_DIR = REVIEW_DIR / "extracted_text"
```

> **💡 Tip:** Tất cả đường dẫn là relative, không cần chỉnh sửa nếu giữ cấu trúc mặc định.

---

## 📖 Hướng Dẫn Chi Tiết

### Option 1: Chạy Pipeline Đầy Đủ (Dễ Nhất)

```bash
cd analyze_data_invoice
python main.py
```

**Kết quả:**

- ✅ `output_analyze/final_summary.txt` - Tổng hợp
- ✅ `output_analyze/label_verification_report.txt` - Chi tiết verify
- ✅ `output_analyze/pdf_error_files.txt` - File lỗi
- ✅ `output_analyze/label_verification.csv` - Dữ liệu CSV

**Thời gian:** ~2-5 phút cho 1000 files

---

### Option 2: Chạy Từng Bước (Advanced)

#### Bước 1: Chuẩn Hóa Dữ Liệu

```bash
python -m core.cleaning
```

**Chức năng:**

- Chuyển format số: `1,234.56` → `1234.56`
- Chuẩn hóa ngày: `dd/MM/yyyy` → `MM/dd/yyyy`
- Xóa khoảng trắng thừa

---

#### Bước 2: Thống Kê File

```bash
python -m core.analysis
```

**Output:** `data_summary_report.txt`

- Tổng số file PDF: X
- Tổng số label: Y
- File thiếu/thừa: Z

---

#### Bước 3: Trích Xuất Text từ PDF

```bash
python -m core.extraction
```

**Chức năng:**

- Trích xuất text từ PDF bằng **PyMuPDF**
- Phát hiện PDF dạng ảnh/scan
- Tự động phân loại:
  - ✅ Text-based PDF → `extracted_text/`
  - 🖼️ Image PDF → `PDF_Image_Files/`
  - ❌ Error PDF → `PDF_Error_Files/`

**Output:**

- `extracted_text/*.txt` - Text đã trích xuất
- `pdf_image_files.txt` - Danh sách PDF ảnh
- `pdf_error_files.txt` - Danh sách PDF lỗi

---

#### Bước 4: Đối Soát Dữ Liệu

```bash
python -m core.verification
```

**Chức năng:**

- So sánh dữ liệu JSON với text trích xuất
- **Fuzzy matching** thông minh
- Hỗ trợ 20+ format ngày tháng
- Xử lý số tiền với nhiều format

**Logic matching:**

- `PASS` - Tìm thấy chính xác
- `SIMILAR` - Tìm thấy tương đồng (>90%)
- `MISSING` - Không tìm thấy

**Output:** `label_verification.csv`

---

#### Bước 5: Phân Loại File

```bash
python -m core.separation
```

Di chuyển file lỗi vào thư mục riêng:

- `Files_Missing_In_Label/` - File PDF không có label
- `Files_Label_Missing_PDF/` - Label không có PDF
- `Files_Docx/` - File DOCX (nếu có)

---

#### Bước 6: Lọc Kết Quả

```bash
python -m core.filtering
```

**Output:**

- `label_verification_missing.csv` - Chỉ MISSING (⚠️ Ưu tiên cao)
- `label_verification_similar.csv` - Chỉ SIMILAR (cần review)
- `label_verification_report.txt` - Báo cáo tổng hợp

---

#### Bước 7: Tìm File Trùng Lặp

```bash
python -m core.deduplication
```

Tìm file trùng dựa trên **MD5 hash** của nội dung JSON.

---

#### Bước 8: Tạo Báo Cáo Cuối

```bash
python -m reports.merger
```

Tổng hợp tất cả báo cáo vào `final_summary.txt`

---

## 🛠️ Các Script Tiện Ích

### 1. Di Chuyển File Cần Review

```bash
python scripts/move_files_for_verification.py "datasets/labels/invoice_001.json"
```

**Chức năng:**

- Di chuyển JSON, PDF, TXT vào `verification_needed/`
- Dùng để review thủ công

---

### 2. Mở File Nhanh

```bash
python scripts/open_pdf_by_json.py "datasets/labels/invoice_001.json"
```

Tự động mở:

- ✅ JSON file
- ✅ PDF tương ứng
- ✅ TXT đã trích xuất

---

## 📊 Hiểu Kết Quả

### File Báo Cáo Chính

| File                             | Mô Tả            | Action                        |
| -------------------------------- | ---------------- | ----------------------------- |
| `final_summary.txt`              | Tổng hợp toàn bộ | Đọc đầu tiên                  |
| `label_verification_missing.csv` | Trường MISSING   | **Ưu tiên cao** - Review ngay |
| `label_verification_similar.csv` | Trường SIMILAR   | Review nhanh                  |
| `pdf_image_files.txt`            | PDF dạng ảnh     | Cần OCR                       |
| `pdf_error_files.txt`            | PDF lỗi          | Kiểm tra file                 |

### Hiểu Status Codes

```
PASS     ✅ - Tìm thấy chính xác trong PDF
SIMILAR  🟡 - Tìm thấy tương đồng (>90% match)
MISSING  ❌ - Không tìm thấy trong PDF
```

---

## ❗ Troubleshooting

### Lỗi: "Directory not found"

**Nguyên nhân:** Thư mục datasets chưa tồn tại

**Giải pháp:**

```bash
mkdir -p datasets/files datasets/labels
```

---

### Lỗi: "No matching files found"

**Nguyên nhân:** Chưa chạy extraction

**Giải pháp:**

```bash
# Phải chạy extraction trước verify
python -m core.extraction
python -m core.verification
```

---

### Nhiều Trường MISSING

**Nguyên nhân có thể:**

1. PDF dạng ảnh/scan (không có text layer)
2. Format ngày không được hỗ trợ
3. OCR kém chất lượng

**Giải pháp:**

1. **Kiểm tra PDF có phải ảnh không:**

   ```bash
   # Xem danh sách PDF ảnh
   cat output_analyze/pdf_image_files.txt
   ```

2. **Xem format ngày được hỗ trợ:**

   - Đọc `supported_date_formats.md`
   - Hỗ trợ 20+ formats

3. **Kiểm tra chất lượng text:**
   ```bash
   # Xem text đã trích xuất
   cat output_analyze/extracted_text/invoice_001.txt
   ```

---

### Import Error

**Nguyên nhân:** Python không tìm thấy common_lib

**Giải pháp:**

```bash
# Chạy từ thư mục gốc analyze_data_basic
cd d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic
python analyze_data_invoice/main.py
```

Hoặc thêm vào Python path:

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

---

## 💡 Tips & Best Practices

1. **Luôn backup dữ liệu** trước khi chạy scripts
2. **Chạy toàn bộ pipeline** bằng `main.py` (dễ nhất)
3. **Review SIMILAR trước MISSING** (thường chỉ khác format nhỏ)
4. **Kiểm tra encoding UTF-8** cho file JSON và TXT
5. **Sử dụng common_lib** để tái sử dụng code

---

## 🔗 Xem Thêm

- [ARCHITECTURE.md](ARCHITECTURE.md) - Kiến trúc hệ thống
- [supported_date_formats.md](supported_date_formats.md) - Format ngày được hỗ trợ
- [../common_lib/](../common_lib/) - Shared utilities library
- [../COMMON_UTILS_SUMMARY.md](../COMMON_UTILS_SUMMARY.md) - Tổng hợp hàm chung

---

**Version:** 2.0 (After Refactoring)  
**Last Updated:** 2026-01-09  
**Maintainer:** ACPA Team
