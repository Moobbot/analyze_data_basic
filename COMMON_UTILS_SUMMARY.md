# TỔNG HỢP CÁC HÀM LOGIC CHUNG CƠ BẢN

Tài liệu này tổng hợp các hàm tiện ích chung được sử dụng trong dự án analyze_data_basic.

---

## 1. XỬ LÝ TEXT (Text Processing)

### 1.1. Xóa khoảng trắng 2 đầu và chuẩn hóa

**File:** `analyze_data_invoice/lib/text_utils.py`

```python
def normalize_whitespace(text: str) -> str:
    """
    Chuẩn hóa khoảng trắng trong text bằng cách:
    - Thay thế nhiều khoảng trắng/newline liên tiếp thành 1 khoảng trắng
    - Xóa khoảng trắng 2 đầu (đầu và cuối)
    
    Args:
        text: Text cần chuẩn hóa
    
    Returns:
        Text đã được chuẩn hóa
    """
    if not text:
        return ""
    
    # Thay thế nhiều khoảng trắng (bao gồm cả newline) thành 1 khoảng trắng
    normalized = re.sub(r"\s+", " ", text)
    
    return normalized.strip()
```

**Ví dụ sử dụng:**
```python
text = "  Hello   World  \n  Test  "
result = normalize_whitespace(text)
# Output: "Hello World Test"
```

---

### 1.2. Chuẩn hóa text tổng hợp

**File:** `analyze_data_invoice/lib/text_utils.py`

```python
def normalize_text(text: str, lowercase: bool = False) -> str:
    """
    Chuẩn hóa text toàn diện:
    - Xóa soft hyphens (ký tự đặc biệt)
    - Chuẩn hóa khoảng trắng
    - Tùy chọn chuyển về lowercase
    
    Args:
        text: Text cần chuẩn hóa
        lowercase: Có chuyển về chữ thường không
    
    Returns:
        Text đã được chuẩn hóa
    """
    if not text:
        return ""
    
    # Xóa soft hyphens
    normalized = text.replace("\xad", "")
    
    # Chuẩn hóa khoảng trắng
    normalized = normalize_whitespace(normalized)
    
    # Tùy chọn chuyển về lowercase
    if lowercase:
        normalized = normalized.lower()
    
    return normalized
```

**File:** `analyze_data_broker/lib/utils.py` (phiên bản đơn giản hơn)

```python
def normalize_text(text):
    """Chuẩn hóa text để so sánh dễ hơn (lowercase, xóa newlines)."""
    if not text:
        return ""
    # Chuyển về lowercase, thay newlines thành spaces, và strip khoảng trắng
    return text.lower().replace("\n", " ").strip()
```

---

### 1.3. Làm sạch khoảng trắng (Clean Whitespace)

**File:** `analyze_data_broker/lib/utils.py`

```python
def clean_whitespace(text):
    """
    Làm sạch khoảng trắng từ text bằng cách:
    1. Xóa khoảng trắng đầu và cuối
    2. Thay thế nhiều khoảng trắng liên tiếp thành 1 khoảng trắng
    
    Args:
        text: String cần làm sạch
    
    Returns:
        String đã được làm sạch với khoảng trắng chuẩn hóa
    """
    if not text or not isinstance(text, str):
        return text
    
    # Strip khoảng trắng đầu và cuối
    text = text.strip()
    
    # Thay thế nhiều khoảng trắng liên tiếp thành 1 khoảng trắng
    text = re.sub(r"\s+", " ", text)
    
    return text
```

---

### 1.4. Xóa ký tự không phải chữ số/chữ cái

**File:** `analyze_data_invoice/lib/text_utils.py`

```python
def remove_non_alphanumeric(text: str, keep_spaces: bool = True) -> str:
    """
    Xóa các ký tự không phải chữ số/chữ cái.
    
    Args:
        text: Text cần làm sạch
        keep_spaces: Có giữ khoảng trắng không
    
    Returns:
        Text đã được làm sạch
    """
    if not text:
        return ""
    
    if keep_spaces:
        # Giữ chữ cái, số và khoảng trắng
        return re.sub(r"[^a-zA-Z0-9\s]", "", text)
    else:
        # Chỉ giữ chữ cái và số
        return re.sub(r"[^a-zA-Z0-9]", "", text)
```

---

### 1.5. Cắt ngắn text

**File:** `analyze_data_invoice/lib/text_utils.py`

```python
def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Cắt ngắn text đến độ dài chỉ định và thêm suffix.
    
    Args:
        text: Text cần cắt ngắn
        max_length: Độ dài tối đa (bao gồm suffix)
        suffix: Hậu tố thêm vào nếu bị cắt
    
    Returns:
        Text đã được cắt ngắn
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[: max_length - len(suffix)] + suffix
```

---

## 2. XUẤT TEXT TỪ PDF

### 2.1. Hàm trích xuất text từ PDF bằng PyMuPDF

**File:** `analyze_data_invoice/core/extraction.py` và `analyze_data_broker/tools/extract_pdf.py`

```python
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Trích xuất text từ file PDF sử dụng PyMuPDF.
    
    Args:
        pdf_path: Đường dẫn đến file PDF
    
    Returns:
        Text đã trích xuất từ tất cả các trang
    """
    text_content = ""
    
    try:
        # Mở file PDF
        with fitz.open(pdf_path) as doc:
            # Đọc từng trang
            for page in doc:
                text_content += page.get_text() + "\n"
        
        return text_content.strip()
    
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""
```

**Ví dụ sử dụng:**
```python
pdf_file = "invoice_001.pdf"
text = extract_text_from_pdf(pdf_file)
print(text)
```

---

### 2.2. Hàm trích xuất và lưu vào file TXT

**File:** `analyze_data_invoice/core/extraction.py`

```python
def extract_and_save_pdf_to_txt(pdf_path: str, output_txt_path: str) -> bool:
    """
    Trích xuất text từ PDF và lưu vào file TXT.
    
    Args:
        pdf_path: Đường dẫn đến file PDF
        output_txt_path: Đường dẫn file TXT output
    
    Returns:
        True nếu thành công, False nếu có lỗi
    """
    try:
        text_content = ""
        
        # Trích xuất text từ PDF
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text_content += page.get_text() + "\n"
        
        # Lưu vào file TXT
        with open(output_txt_path, "w", encoding="utf-8") as f_out:
            f_out.write(text_content)
        
        return True
    
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return False
```

**Ví dụ sử dụng:**
```python
pdf_file = "data/invoice_001.pdf"
txt_file = "output/invoice_001.txt"
success = extract_and_save_pdf_to_txt(pdf_file, txt_file)
```

---

## 3. XỬ LÝ FILE VÀ THƯ MỤC

### 3.1. Đọc nội dung file text

**File:** `analyze_data_invoice/lib/file_utils.py` và `analyze_data_broker/lib/utils.py`

```python
def read_file(path: str) -> str:
    """
    Đọc file text và trả về nội dung (đã strip khoảng trắng).
    
    Args:
        path: Đường dẫn đến file
    
    Returns:
        Nội dung file hoặc thông báo lỗi
    """
    if not os.path.exists(path):
        return f"[Error: File not found - {path}]"
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        return f"[Error reading {path}: {e}]"
```

---

### 3.2. Tạo thư mục nếu chưa tồn tại

**File:** `analyze_data_invoice/lib/file_utils.py`

```python
from pathlib import Path

def ensure_dir_exists(directory: Path) -> bool:
    """
    Tạo thư mục nếu chưa tồn tại.
    
    Args:
        directory: Path đến thư mục
    
    Returns:
        True nếu thư mục tồn tại hoặc được tạo thành công
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {directory}: {e}")
        return False
```

**File:** `analyze_data_broker/lib/utils.py` (phiên bản dùng os)

```python
def ensure_dir_exists(directory):
    """Tạo thư mục nếu chưa tồn tại."""
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            return True
        except Exception as e:
            print(f"Error creating directory {directory}: {e}")
            return False
    return True
```

---

### 3.3. Liệt kê file theo extension

**File:** `analyze_data_invoice/lib/file_utils.py`

```python
from pathlib import Path
from typing import List

def list_files_recursive(directory: Path, extension: str) -> List[str]:
    """
    Liệt kê tất cả file có extension cụ thể (đệ quy tất cả các cấp).
    
    Args:
        directory: Thư mục cần tìm
        extension: Đuôi file (ví dụ: '.pdf')
    
    Returns:
        Danh sách đường dẫn tương đối từ directory
    """
    files: List[str] = []
    
    if not directory.exists():
        return files
    
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.lower().endswith(extension.lower()):
                full_path = Path(root) / filename
                rel_path = full_path.relative_to(directory)
                files.append(str(rel_path))
    
    return files
```

**Ví dụ sử dụng:**
```python
from pathlib import Path

pdf_dir = Path("data/pdfs")
pdf_files = list_files_recursive(pdf_dir, ".pdf")
print(f"Found {len(pdf_files)} PDF files")
```

---

### 3.4. Chuyển đổi bytes sang định dạng dễ đọc

**File:** `analyze_data_invoice/lib/text_utils.py` và `analyze_data_broker/lib/utils.py`

```python
def format_size(size_bytes: float) -> str:
    """
    Chuyển đổi bytes sang định dạng dễ đọc (B, KB, MB, GB, TB).
    
    Args:
        size_bytes: Kích thước tính bằng bytes
    
    Returns:
        String định dạng kích thước
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"
```

**Ví dụ sử dụng:**
```python
file_size = 1536000  # bytes
print(format_size(file_size))  # Output: "1.46 MB"
```

---

## 4. XỬ LÝ NGÀY THÁNG (Date Processing)

### 4.1. Chuẩn hóa chuỗi ngày tháng

**File:** `analyze_data_invoice/lib/date_utils.py`

```python
def normalize_date_string(date_str: str) -> str:
    """
    Chuẩn hóa chuỗi ngày tháng bằng cách:
    - Xóa soft hyphens
    - Xóa khoảng trắng thừa
    
    Args:
        date_str: Chuỗi ngày tháng cần chuẩn hóa
    
    Returns:
        Chuỗi ngày tháng đã được chuẩn hóa
    """
    if not date_str:
        return ""
    
    # Xóa soft hyphens (unicode \xad)
    normalized = date_str.replace("\xad", "")
    
    # Xóa khoảng trắng thừa
    normalized = " ".join(normalized.split())
    
    return normalized.strip()
```

---

### 4.2. Parse ngày tháng định dạng "DD Mon YYYY"

**File:** `analyze_data_invoice/lib/date_utils.py`

```python
from datetime import datetime
import re

# Dictionary ánh xạ tên tháng
MONTH_DICT = {
    "Jan": "01", "January": "01",
    "Feb": "02", "February": "02",
    "Mar": "03", "March": "03",
    "Apr": "04", "April": "04",
    "May": "05",
    "Jun": "06", "June": "06",
    "Jul": "07", "July": "07",
    "Aug": "08", "August": "08",
    "Sep": "09", "Sept": "09", "September": "09",
    "Oct": "10", "October": "10",
    "Nov": "11", "November": "11",
    "Dec": "12", "December": "12",
}

def parse_date_dmy(date_str: str) -> Optional[datetime]:
    """
    Parse chuỗi ngày tháng theo định dạng:
    - "DD Mon YYYY" (ví dụ: "03 Oct 2023")
    - "DD-Mon-YY" (ví dụ: "31-Jul-21")
    
    Args:
        date_str: Chuỗi chứa ngày tháng
    
    Returns:
        Đối tượng datetime hoặc None nếu parse thất bại
    """
    if not date_str or not isinstance(date_str, str):
        return None
    
    # Chuẩn hóa trước
    date_str = normalize_date_string(date_str)
    
    # Pattern 1: "DD Mon YYYY" (ví dụ: "03 Oct 2023")
    pattern1 = r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})"
    match = re.search(pattern1, date_str)
    
    if match:
        day = match.group(1).zfill(2)  # Thêm số 0 nếu cần
        month_name = match.group(2)
        year = match.group(3)
        
        # Tra cứu số tháng
        month_num = MONTH_DICT.get(month_name) or MONTH_DICT.get(month_name.capitalize())
        
        if month_num:
            try:
                date_obj = datetime.strptime(f"{year}-{month_num}-{day}", "%Y-%m-%d")
                return date_obj
            except ValueError:
                pass
    
    # Pattern 2: "DD-Mon-YY" (ví dụ: "31-Jul-21")
    pattern2 = r"(\d{1,2})-([A-Za-z]+)-(\d{2})"
    match = re.search(pattern2, date_str)
    
    if match:
        day = match.group(1).zfill(2)
        month_name = match.group(2)
        year_2digit = match.group(3)
        
        # Chuyển đổi năm 2 chữ số sang 4 chữ số
        year_int = int(year_2digit)
        if 0 <= year_int <= 99:
            # Giả định năm 00-50 là 2000-2050, 51-99 là 1951-1999
            year = f"{2000 + year_int if year_int <= 50 else 1900 + year_int}"
        else:
            return None
        
        month_num = MONTH_DICT.get(month_name) or MONTH_DICT.get(month_name.capitalize())
        
        if month_num:
            try:
                date_obj = datetime.strptime(f"{year}-{month_num}-{day}", "%Y-%m-%d")
                return date_obj
            except ValueError:
                pass
    
    return None
```

---

### 4.3. Validate ngày tháng

**File:** `analyze_data_invoice/lib/date_utils.py`

```python
def validate_date(date_str: str) -> Tuple[bool, Optional[datetime], str]:
    """
    Kiểm tra xem chuỗi ngày tháng có đúng định dạng và hợp lệ không.
    
    Hỗ trợ nhiều định dạng: "DD Mon YYYY", "DD/MM/YYYY", "YYYY-MM-DD", v.v.
    
    Args:
        date_str: Chuỗi cần kiểm tra
    
    Returns:
        Tuple (is_valid: bool, parsed_date: datetime or None, format_used: str)
    """
    if not date_str or not isinstance(date_str, str):
        return (False, None, "")
    
    date_str = normalize_date_string(date_str)
    
    # Thử parse định dạng "DD Mon YYYY" trước
    parsed = parse_date_dmy(date_str)
    if parsed:
        return (True, parsed, "DD Mon YYYY")
    
    # Thử các định dạng khác
    formats_to_try = [
        ("%d/%m/%Y", "DD/MM/YYYY"),
        ("%Y-%m-%d", "YYYY-MM-DD"),
        ("%d-%m-%Y", "DD-MM-YYYY"),
        ("%m/%d/%Y", "MM/DD/YYYY"),
        ("%d.%m.%Y", "DD.MM.YYYY"),
        ("%Y.%m.%d", "YYYY.MM.DD"),
    ]
    
    for fmt, fmt_name in formats_to_try:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return (True, parsed, fmt_name)
        except ValueError:
            continue
    
    return (False, None, "")
```

**Ví dụ sử dụng:**
```python
date_string = "03 Oct 2023"
is_valid, date_obj, format_name = validate_date(date_string)

if is_valid:
    print(f"Valid date: {date_obj}, Format: {format_name}")
else:
    print("Invalid date")
```

---

## 5. XỬ LÝ JSON

### 5.1. Tính hash MD5 của nội dung JSON

**File:** `analyze_data_invoice/lib/file_utils.py` và `analyze_data_broker/lib/utils.py`

```python
import json
import hashlib
from pathlib import Path

def get_json_content_hash(json_path: Path) -> Optional[str]:
    """
    Đọc file JSON, parse và trả về MD5 hash của nội dung.
    Sử dụng sorted keys để đảm bảo hash nhất quán bất kể thứ tự key.
    
    Args:
        json_path: Đường dẫn đến file JSON
    
    Returns:
        MD5 hash của nội dung JSON, hoặc None nếu có lỗi
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Dump với sort_keys=True để đảm bảo thứ tự key không ảnh hưởng hash
        canonical_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(canonical_str.encode("utf-8")).hexdigest()
    
    except Exception as e:
        print(f"Error processing {json_path}: {e}")
        return None
```

**Ví dụ sử dụng:**
```python
json_file = Path("data/invoice_001.json")
hash_value = get_json_content_hash(json_file)
print(f"JSON hash: {hash_value}")
```

---

## 6. CÁC HÀM MAP FILES

### 6.1. Map files theo basename

**File:** `analyze_data_broker/lib/utils.py`

```python
def get_files_map(directory):
    """
    Scan thư mục và trả về dictionary map basenames (không có extension)
    sang danh sách tên file đầy đủ.
    
    Ví dụ: {'report': ['report.pdf', 'report.docx']}
    
    Args:
        directory: Thư mục cần scan
    
    Returns:
        Dictionary map basenames sang list filenames
    """
    files_map = {}
    
    if not os.path.exists(directory):
        print(f"Error: Directory not found: {directory}")
        return files_map
    
    try:
        for f in os.listdir(directory):
            full_path = os.path.join(directory, f)
            if os.path.isfile(full_path):
                base_name = os.path.splitext(f)[0]
                if base_name not in files_map:
                    files_map[base_name] = []
                files_map[base_name].append(f)
    except Exception as e:
        print(f"Error reading {directory}: {e}")
    
    return files_map
```

---

### 6.2. Map files đệ quy

**File:** `analyze_data_invoice/lib/file_utils.py`

```python
def get_files_map_recursive(directory: Path) -> Dict[str, List[str]]:
    """
    Scan thư mục đệ quy và trả về dictionary map basenames
    (đường dẫn tương đối không có extension) sang danh sách file paths tương đối.
    
    Chuẩn hóa case để xử lý sự khác biệt về chữ hoa/thường trong tên thư mục.
    
    Ví dụ: {'subdir/report': ['subdir/report.pdf', 'subdir/report.json']}
    
    Args:
        directory: Thư mục gốc để scan
    
    Returns:
        Dictionary map normalized base paths sang list của relative file paths
    """
    files_map: Dict[str, List[str]] = {}
    
    if not directory.exists():
        print(f"Directory not found: {directory}")
        return files_map
    
    for root, _, files in os.walk(directory):
        for f in files:
            full_path = Path(root) / f
            rel_path = full_path.relative_to(directory)
            
            # Sử dụng đường dẫn tương đối không có extension làm key
            # Chuẩn hóa case để xử lý sự khác biệt về chữ hoa/thường
            base_name = os.path.normcase(str(rel_path.with_suffix("")))
            
            if base_name not in files_map:
                files_map[base_name] = []
            files_map[base_name].append(str(rel_path))
    
    return files_map
```

---

## 7. TỔNG KẾT

### Các thư viện cần thiết:

```python
import os
import re
import json
import hashlib
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import fitz  # PyMuPDF - cài đặt: pip install PyMuPDF
```

### Cài đặt dependencies:

```bash
pip install PyMuPDF  # Để trích xuất text từ PDF
```

### File locations chính:

- **Text Utils:** `analyze_data_invoice/lib/text_utils.py`
- **File Utils:** `analyze_data_invoice/lib/file_utils.py`
- **Date Utils:** `analyze_data_invoice/lib/date_utils.py`
- **Broker Utils:** `analyze_data_broker/lib/utils.py`
- **PDF Extraction:** 
  - `analyze_data_invoice/core/extraction.py`
  - `analyze_data_broker/tools/extract_pdf.py`

---

## CÁC HÀM PHỔ BIẾN NHẤT

### Top 5 hàm hay dùng:

1. **`normalize_whitespace(text)`** - Chuẩn hóa và xóa khoảng trắng thừa
2. **`extract_text_from_pdf(pdf_path)`** - Trích xuất text từ PDF
3. **`read_file(path)`** - Đọc nội dung file text
4. **`ensure_dir_exists(directory)`** - Tạo thư mục nếu chưa có
5. **`validate_date(date_str)`** - Kiểm tra và parse ngày tháng

---

**Ngày tạo:** 2026-01-09  
**Tác giả:** Antigravity AI  
**Dự án:** ACPA - analyze_data_basic
