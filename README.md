# Invoice Data Audit Tool

Bộ công cụ tự động hóa việc phân tích, trích xuất và đối soát dữ liệu hóa đơn (PDF) với dữ liệu nhãn (JSON).

## Mô Tả

Project này gồm các script Python thực hiện quy trình sau:
1.  **Thống kê file**: Đếm số lượng, kiểm tra định dạng, phát hiện file thiếu/thừa giữa thư mục Label và Dataset.
2.  **Sàng lọc**: Tự động di chuyển các file không phù hợp (docx, missing label) sang thư mục riêng.
3.  **Trích xuất PDF**: Sử dụng thư viện `PyMuPDF` để lấy nội dung text từ file PDF.
4.  **Đối soát (Audit)**: So sánh dữ liệu trong file JSON (nhãn) với nội dung trích xuất từ PDF để tìm lỗi hoặc thông tin sai lệch.

## Cài Đặt

1.  Yêu cầu: Python 3.10+
2.  Cài đặt thư viện phụ thuộc:
    ```bash
    pip install -r requirements.txt
    ```
    (Thư viện chính: `pymupdf`, `pdfplumber`, `PyPDF2`)

## Cấu Hình

File cấu hình chính: `config.py`
*   `BASE_DIR`: Thư mục gốc của dự án.
*   `DATASET_DIR`: Thư mục chứa file PDF gốc.
*   `LABEL_DIR`: Thư mục chứa file JSON nhãn.
*   `REVIEW_DIR`: Thư mục chứa các báo cáo, file CSV kết quả.

## Hướng Dẫn Sử Dụng (Workflow)

Chạy các script theo thứ tự sau hoặc chạy các bước riêng lẻ tùy nhu cầu:

### Bước 1: Phân tích & Sàng lọc file
Chạy pipeline chính để thống kê số lượng file và di chuyển các file lỗi/thừa:
```bash
python main_pipeline.py
```
*   Đầu ra: `review_data/data_summary_report_pre.txt`, `file_differences.txt`.
*   Tác vụ: Di chuyển file .docx và file thiếu nhãn vào thư mục `Files_Docx`, `Files_Missing_In_Label`.

### Bước 2: Trích xuất nội dung PDF
Chạy script đọc text từ toàn bộ file PDF trong Dataset:
```bash
python extract_pdf.py
```
*   Đầu ra: Thư mục `Extracted_Text/` chứa các file .txt tương ứng.
*   Báo cáo: `review_data/pdf_error_files.txt` (file lỗi), `pdf_image_files.txt` (file ảnh).

### Bước 3: Đối soát dữ liệu (Verify Labels)
So sánh giá trị trong JSON với nội dung Text đã trích xuất:
```bash
python verify_labels.py
```
*   Đầu ra: `review_data/label_verification.csv` (dữ liệu thô), `label_verification_report.txt` (thống kê).

### Bước 4: Lọc kết quả đối soát
Tách kết quả thành các file riêng biệt để dễ kiểm tra:
```bash
python filter_verification_results.py
```
*   Đầu ra:
    *   `review_data/label_verification_missing.csv`: Các trường dữ liệu **KHÔNG** tìm thấy.
    *   `review_data/label_verification_similar.csv`: Các trường dữ liệu **TƯƠNG ĐỒNG** (Fuzzy match > 80%).

### Bước 5: Tạo báo cáo tổng kết
Tổng hợp tất cả kết quả thành file Markdown báo cáo cuối cùng:
```bash
python generate_final_reports.py
```
*   Đầu ra: `General_Overview_Report.md`, `Detailed_Error_Report.md`.

## Ý Nghĩa Các Báo Cáo (Trong thư mục review_data)

*   `data_summary_report.txt`: Thống kê tổng quan số lượng file, dung lượng.
*   `label_verification_missing.csv`: Cần kiểm tra kỹ, có thể do lỗi OCR hoặc dữ liệu nhập sai.
*   `label_verification_similar.csv`: Cần review nhanh để xác nhận (thường là đúng nhưng sai format nhỏ).
