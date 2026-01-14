# PDF_PAGE_INFO.CSV - HƯỚNG DẪN SỬ DỤNG

📊 TẬP TIN: pdf_page_info.csv
📍 Vị trí: reports/pdf_page_info.csv
📝 Tổng dòng: 785 (1 header + 783 PDF files + 1 dòng cuối)

## CẤU TRÚC CỘT DỮ LIỆU

Cột 1: Filename
• Tên file PDF
• Bao gồm đường dẫn folder (ví dụ: Clearned\, Leuco\, Mon\, etc.)
• Ví dụ: Clearned\ABN Australia - I#INV-20198 - Nov 25.pdf

Cột 2: Pages
• Số trang của PDF
• Giá trị số: 1, 2, 3, ..., 100+
• "ERROR" nếu file không đọc được

Cột 3: TextLength
• Độ dài của text trích xuất (ký tự)
• Giá trị số: 0, 100, 5000, 10000+
• 0 = File rỗng (không có text hoặc chỉ ảnh)

Cột 4: IsEmpty
• Kiểm tra xem text có rỗng không
• True = Không trích xuất được text
• False = Có text được trích xuất

Cột 5: IsEncrypted
• Kiểm tra PDF có bị mã hóa không
• True = PDF bị mã hóa (protected)
• False = PDF không bị mã hóa

Cột 6: FileSizeKB
• Kích thước file PDF (kilobytes)
• Giá trị thập phân: 48.58, 2898.5, 8417.94
• Dùng để phát hiện file rỗng hoặc bị hỏng

Cột 7: HasLabel
• Kiểm tra có nhãn JSON tương ứng không
• True = Có file JSON nhãn
• False = Không có nhãn

Cột 8: Status
• Trạng thái xử lý
• "success" = Xử lý thành công
• "error: ..." = Lỗi (chi tiết lỗi)

## VÍ DỤ PHÂN TÍCH DỮ LIỆU

1. FILE BÌNH THƯỜNG (CÓ TEXT):
   Clearned\ABN Australia - I#INV-20198 - Nov 25.pdf,2,2216,False,False,48.58,True,"success"
   → 2 trang, 2216 ký tự, không rỗng, không mã hóa, 48.58 KB, có nhãn ✅

2. FILE RỖ NG (CHỈ ẢNH/SCANNED):
   Leuco\1,2,3. Hotel and Meal Thailand - THB6051.78.pdf,2,0,True,False,505.12,True,"success"
   → 2 trang, 0 ký tự (RỖNG!), không mã hóa, 505.12 KB, có nhãn ⚠️

3. FILE NHIỀU TRANG:
   Clearned\SI2604_CLEANEDGE...PAYROLL-merged.pdf,14,9366,False,False,2898.5,True,"success"
   → 14 trang (!), 9366 ký tự, không rỗng, không mã hóa, 2.9 MB, có nhãn 📄

4. FILE LỚN LẠ (PHẦN ĐẠI):
   Leuco\Holiday Inn.pdf,2,0,True,False,8417.94,True,"success"
   → 2 trang, 0 ký tự (RỖ NG!), không mã hóa, 8.4 MB (RẤT LỚN!), có nhãn ⚠️⚠️

## LỰA CHỌN/LỌC DỮ LIỆU

A. TÌM CÁC FILE KHÔNG CÓ TEXT (SCAN/ẢNH):
Filter: IsEmpty = True
Tổng: 68 files
→ Cần xem xét lại dữ liệu hoặc chuyển nhân công

B. TÌM CÁC FILE BỊ MÃ HÓA:
Filter: IsEncrypted = True
Tổng: ? files
→ Cần mật khẩu hoặc phần mềm giải mã

C. TÌM CÁC FILE LỚN (> 2 MB):
Filter: FileSizeKB > 2048
→ Có thể là file chứa ảnh, cần kiểm tra

D. TÌM CÁC FILE NHIỀU TRANG (> 5 trang):
Filter: Pages > 5
→ Có thể cần xử lý đặc biệt

E. TÌM CÁC FILE LỖI:
Filter: Status LIKE "error%"
→ Kiểm tra chi tiết lỗi trong cột Status

## THỐNG KÊ NHANH DARI TẬP TIN

Lệnh Excel/LibreOffice Calc:

1. Đếm số file rỗng:
   =COUNTIF(D:D, TRUE)
   Kết quả: 68

2. Tổng số trang:
   =SUM(B:B)
   (Chú ý: Loại bỏ header và "ERROR" rows)

3. File lớn nhất:
   =MAX(F:F)
   Kết quả: 8417.94 KB

4. Số file bị mã hóa:
   =COUNTIF(E:E, TRUE)
   Kết quả: 0 (Tất cả đều không mã hóa)

5. Số file có nhãn:
   =COUNTIF(G:G, TRUE)
   Kết quả: 783 (Tất cả đều có nhãn)

## HƯỚNG DẪN SỬ DỤNG VỚI PYTHON

import pandas as pd

### Đọc file CSV

df = pd.read_csv('pdf_page_info.csv')

### Thống kê cơ bản

print(df.describe())

### Tìm file rỗng

empty_files = df[df['IsEmpty'] == True]
print(f"Số file rỗng: {len(empty_files)}")

### Tìm file lớn hơn 2MB

large_files = df[df['FileSizeKB'] > 2048]
print(f"File lớn: {len(large_files)}")

### Tìm file từ 5+ trang

multi_page = df[df['Pages'] >= 5]
print(f"File nhiều trang: {len(multi_page)}")

### Thống kê theo folder

by_folder = df['Filename'].str.split('\\').str[0].value_counts()
print(by_folder)

## KẾT QUẢ KIỂM TRA 2026-01-14

Tổng file PDF: 783
File có text: 715 (91.4%)
File rỗng/scan: 68 (8.7%)
File lỗi: 0 (0%)

Kích thước:
• Nhỏ nhất: 48.58 KB
• Lớn nhất: 8417.94 KB
• Trung bình: ~650 KB

Mã hóa:
• Có mã hóa: 0 files
• Không mã hóa: 783 files

Nhãn:
• Có nhãn: 783 files
• Không nhãn: 0 files

##
