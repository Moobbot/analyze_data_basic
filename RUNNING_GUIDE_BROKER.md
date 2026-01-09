# Hướng Dẫn Chạy - analyze_data_broker

> **Công cụ xử lý và validation dữ liệu tài chính (Trade Confirmations, Contact Notes)**

## 🚀 Quick Start

### Chạy Validation

```bash
cd analyze_data_broker
python check_transaction_type.py
```

**Chức năng:**

- Validate Transaction Type
- Kiểm tra ngày tháng
- Verify ISIN (Securities ID)
- So sánh dữ liệu với extracted text

---

## 📋 Yêu Cầu Hệ Thống

### Dependencies

```bash
# Cài đặt từ thư mục gốc
cd d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic
pip install -r requirements.txt
```

**Thư viện:**

- Python 3.7+ (standard library)
- `pymupdf` (optional, cho PDF extraction)

### Cấu Trúc Thư Mục

```
analyze_data_broker/
├── datasets/          # ← Đặt dữ liệu ở đây
│   ├── files/        # PDF/Document files
│   └── labels/       # JSON labels
├── lib/              # Core library
│   ├── config.py
│   ├── utils.py      # ← Đã refactored, dùng common_lib
│   ├── validation_config.py
│   └── validation_logic.py
├── scripts/          # Data processing scripts
├── tools/            # One-time utilities
└── output/           # ← Kết quả tự động tạo
    ├── reports/
    └── exports/
```

---

## ⚙️ Cấu Hình

### File: `lib/config.py`

```python
# Thư mục nguồn
DATASET_DIR = os.path.join(BASE_DIR, "datasets", "files")
LABEL_DIR = os.path.join(BASE_DIR, "datasets", "labels")

# Thư mục đầu ra
REVIEW_DIR = os.path.join(BASE_DIR, "output_analyze", "datasets")
```

> **💡 Tip:** Config tự động tạo thư mục nếu chưa tồn tại.

---

## 📖 Workflows Chính

### 1. Data Preparation Workflow

Chuẩn bị dữ liệu trước khi validation:

```bash
# Step 1: Làm sạch khoảng trắng
python scripts/clean_whitespace.py datasets/labels/Trade_Confirmation

# Step 2: Chuẩn hóa Transaction Type
python scripts/standardize_transaction_type.py datasets/labels/Trade_Confirmation

# Step 3: Sắp xếp lại JSON keys
python scripts/reorder_json.py datasets/labels/Trade_Confirmation datasets/labels/Trade_Confirmation

# Step 4: Chuyển đổi format ngày (nếu cần)
python scripts/convert_date_format.py datasets/labels/Trade_Confirmation
```

**Kết quả:** Dữ liệu đã chuẩn hóa, sẵn sàng validate

---

### 2. Data Analysis Workflow

Phân tích và export dữ liệu:

```bash
# Phân tích format ngày tháng
python scripts/analyze_date_formats.py datasets/labels > output/analysis/date_analysis.txt

# Export sang Excel để review
python scripts/json_to_excel.py datasets/labels/Trade_Confirmation output/exports/trades.xlsx
```

---

### 3. Validation Workflow

Validate dữ liệu:

```bash
# Chạy validation
python check_transaction_type.py

# Kết quả trong: output_analyze/datasets/
# - label_verification.csv
# - label_verification_report.txt
```

---

## 🛠️ Scripts Chi Tiết

### Data Cleaning

#### 1. Clean Whitespace

```bash
# Một file
python scripts/clean_whitespace.py datasets/labels/Contact_Note/0817.json

# Cả thư mục
python scripts/clean_whitespace.py datasets/labels/Trade_Confirmation

# Output ra folder khác
python scripts/clean_whitespace.py datasets/labels/Trade_Confirmation --output cleaned_data
```

**Chức năng:**

- Xóa khoảng trắng đầu/cuối
- Chuẩn hóa nhiều spaces thành 1 space
- Giữ nguyên structure JSON

---

#### 2. Standardize Transaction Type

```bash
# Chuẩn hóa: Purchase/Sale → BUY/SELL
python scripts/standardize_transaction_type.py datasets/labels/Contact_Note

# Một file
python scripts/standardize_transaction_type.py datasets/labels/Contact_Note/0817.json
```

**Mapping:**

- `Purchase` → `BUY`
- `Sale` → `SELL`
- `Buy` → `BUY`
- `Sell` → `SELL`

---

#### 3. Reorder JSON Keys

```bash
# Sắp xếp theo thứ tự chuẩn (overwrite)
python scripts/reorder_json.py datasets/labels/Trade_Confirmation datasets/labels/Trade_Confirmation

# Output ra folder mới
python scripts/reorder_json.py datasets/labels/Trade_Confirmation output/reordered
```

**Chức năng:**

- Sắp xếp keys theo `TARGET_ORDER` trong script
- Thêm keys thiếu với giá trị `null`
- Giữ keys thừa ở cuối

---

### Date Processing

#### 4. Convert Date Format

```bash
# Convert tất cả dates trong folder
python scripts/convert_date_format.py datasets/labels/Trade_Confirmation
```

**Chức năng:**

- Detect format hiện tại
- Convert sang format chuẩn
- Hỗ trợ nhiều formats

---

#### 5. Analyze Date Formats

```bash
# Phân tích format ngày trong dataset
python scripts/analyze_date_formats.py datasets/labels

# Lưu kết quả
python scripts/analyze_date_formats.py datasets/labels > date_analysis.txt
```

**Output:**

- Danh sách formats được tìm thấy
- Số lượng file sử dụng mỗi format
- Recommendations

---

### Export Tools

#### 6. JSON to Excel

```bash
# Export folder sang Excel
python scripts/json_to_excel.py datasets/labels/Trade_Confirmation output/exports/trades.xlsx

# Single file
python scripts/json_to_excel.py datasets/labels/Contact_Note/0817.json output/exports/contact.xlsx
```

**Output:** File Excel với:

- Mỗi JSON object = 1 row
- Keys = Columns
- Formatted cells

---

## 🔧 Tools (One-time Fixes)

### PDF Extraction

```bash
# Trích xuất text từ PDFs
python tools/extract_pdf.py
```

**Chức năng:**

- Sử dụng **common_lib.pdf_utils**
- Phát hiện PDF ảnh/scan
- Output: `extracted_text/*.txt`

---

### Fix Utilities

```bash
# Fix duplicate JSON keys
python tools/fix_duplicate_keys.py datasets/labels/problematic_file.json

# Wrap JSON objects in arrays
python tools/wrap_json_arrays.py datasets/labels/Trade_Confirmation

# Verify date conversions
python tools/verify_date_conversion.py datasets/labels/Trade_Confirmation

# Update account numbers
python tools/update_account_numbers.py
```

---

## 📊 Validation Logic

### Transaction Type Validation

```python
# Từ lib/validation_logic.py
def check_transaction_type(data, text_content, result_log):
    """
    Validates Transaction Type field against text.

    Logic:
    - Check if value exists in data
    - Look up keywords for transaction type
    - Search keywords in extracted text
    - Return PASS/FAIL
    """
```

**Keywords mapping:** Xem `lib/validation_config.py`

---

### Date Field Validation

```python
def check_date_field(field_name, data, text_content, result_log):
    """
    Validates date fields.

    Steps:
    1. Validate format (MM/dd/yyyy)
    2. Check date presence in text (multiple formats)
    3. Check context keywords

    Returns: PASS/WARN/FAIL
    """
```

**Hỗ trợ:** 20+ date formats via `common_lib.date_utils`

---

### ISIN Validation

```python
def check_isin(data, result_log):
    """
    Validates Securities ID (ISIN).

    Rule: Must be 12 characters

    Returns: PASS/FAIL/MISSING
    """
```

---

## 📁 Output Files

### Validation Reports

| File                            | Mô Tả                       | Location                   |
| ------------------------------- | --------------------------- | -------------------------- |
| `label_verification.csv`        | Kết quả validation chi tiết | `output_analyze/datasets/` |
| `label_verification_report.txt` | Báo cáo tổng hợp            | `output_analyze/datasets/` |
| `pdf_error_files.txt`           | Danh sách PDF lỗi           | `output_analyze/datasets/` |
| `pdf_image_files.txt`           | Danh sách PDF ảnh           | `output_analyze/datasets/` |

### Export Files

| File                | Mô Tả                | Location           |
| ------------------- | -------------------- | ------------------ |
| `*.xlsx`            | Excel exports        | `output/exports/`  |
| `date_analysis.txt` | Date format analysis | `output/analysis/` |

---

## ❗ Troubleshooting

### Import Error: "cannot import common_lib"

**Nguyên nhân:** Python không tìm thấy common_lib

**Giải pháp:**

```bash
# Option 1: Chạy từ thư mục gốc
cd d:\Work\Clients\AIRC\product\ACPA\analyze_data_basic
python analyze_data_broker/check_transaction_type.py

# Option 2: Thủ công thêm path (already fixed in code)
# lib/utils.py đã tự động: sys.path.insert(0, parent_dir)
```

---

### Validation Fails for Dates

**Nguyên nhân có thể:**

1. Date format không được hỗ trợ
2. Date không có trong text
3. Context keywords missing

**Giải pháp:**

1. **Kiểm tra supported formats:**

   ```bash
   # Xem danh sách formats
   python -c "from common_lib.date_utils import get_date_formats; print(get_date_formats())"
   ```

2. **Phân tích dates trong dataset:**

   ```bash
   python scripts/analyze_date_formats.py datasets/labels
   ```

3. **Update validation config nếu cần:**
   - Edit `lib/validation_config.py`
   - Thêm keywords mới

---

### Transaction Type Not Recognized

**Giải pháp:**

1. **Chuẩn hóa trước:**

   ```bash
   python scripts/standardize_transaction_type.py datasets/labels
   ```

2. **Kiểm tra mapping:**

   - Xem `lib/validation_config.py`
   - `TRANSACTION_KEYWORDS` dict

3. **Thêm keyword mới nếu cần**

---

## 💡 Tips & Best Practices

### 1. Data Preparation Best Practices

```bash
# Luôn chạy theo thứ tự này:
1. clean_whitespace.py        # Làm sạch
2. standardize_transaction_type.py  # Chuẩn hóa
3. reorder_json.py            # Sắp xếp
4. convert_date_format.py     # Convert dates
5. check_transaction_type.py  # Validate
```

### 2. Backup Trước Khi Xử Lý

```bash
# Backup folder
cp -r datasets/labels datasets/labels_backup_$(date +%Y%m%d)
```

### 3. Sử Dụng common_lib

```python
# Trong code mới, import từ common_lib
from common_lib import normalize_text, validate_date
from common_lib.pdf_utils import extract_text_from_pdf

# Thay vì:
from lib import utils  # Old way
```

### 4. Review Output

```bash
# Sau mỗi step, review output
cat output_analyze/datasets/label_verification_report.txt

# Kiểm tra FAIL cases
grep "FAIL" output_analyze/datasets/label_verification.csv
```

---

## 🔗 Xem Thêm

- [../common_lib/](../common_lib/) - Shared utilities library
- [../COMMON_UTILS_SUMMARY.md](../COMMON_UTILS_SUMMARY.md) - Tổng hợp hàm chung
- [lib/validation_config.py](lib/validation_config.py) - Validation rules
- [lib/validation_logic.py](lib/validation_logic.py) - Validation logic

---

## 📝 Notes

- Tất cả scripts hỗ trợ cả **single file** và **folder processing**
- Scripts giữ nguyên folder structure khi dùng `--output`
- JSON formatting: 2-space indentation
- Encoding: UTF-8 throughout
- **common_lib integration**: Đã refactored để dùng common utilities

---

**Version:** 2.0 (After Refactoring)  
**Last Updated:** 2026-01-09  
**Maintainer:** ACPA Team
