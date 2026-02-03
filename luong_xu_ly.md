# Phương án xử lý chi tiết (Processing Logic)

Tài liệu này mô tả chi tiết các bước xử lý và các trường hợp (cases) logic được áp dụng trong hệ thống để chuyển đổi từ file PDF sang dữ liệu Excel.

## 1. Quy trình xử lý tổng quát (Step-by-Step)

| Bước                   | Mô tả                         | Chi tiết kỹ thuật                                                                                                                                                                                                                                                                                                                |
| :--------------------- | :---------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Input**           | Nhận file PDF đầu vào         | API Upload ([main.py](file:///d:/Work/Clients/AIRC/product/ACPA/broker-extraction-api/app/main.py))                                                                                                                                                                                                                              |
| **2. Pre-processing**  | Chuyển đổi PDF sang ảnh       | `pdf2image` (mỗi trang 1 ảnh)                                                                                                                                                                                                                                                                                                    |
| **3. Classification**  | Phân loại trang (Page Type)   | Dựa vào từ khóa (keywords) trên trang để xác định là **Position**, **Transaction**, hay **Liquidity** (xem [classify_page](file:///d:/Work/Clients/AIRC/product/ACPA/broker-extraction-api/app/services/pdf_processor.py#42-54) trong [utils.py](file:///d:/Work/Clients/AIRC/product/ACPA/broker-extraction-api/app/utils.py)). |
| **4. Detection & OCR** | Nhận diện vùng và Text        | - **YOLO**: Nhận diện các dòng (rows) dữ liệu.<br>- **PaddleOCR**: Nhận diện text và vị trí (box) của text.                                                                                                                                                                                                                      |
| **5. Mapping**         | Ghép Text vào Cột (Mapping)   | Sử dụng tọa độ để map text từ OCR vào các cột tương ứng của dòng được YOLO phát hiện ([boxes_aligned_in_column_idx](file:///d:/Work/Clients/AIRC/product/ACPA/broker-extraction-api/app/utils.py#180-216)).                                                                                                                      |
| **6. Extraction**      | Trích xuất & Làm sạch dữ liệu | Áp dụng logic riêng cho từng loại (Case) để lấy giá trị sạch (số, ngày tháng, currency...).                                                                                                                                                                                                                                      |
| **7. Output**          | Xuất Excel                    | Ghi dữ liệu đã làm sạch vào các file Excel tương ứng (`trade.xlsx`, `postion.xlsx`, v.v.).                                                                                                                                                                                                                                       |

---

## 2. Chi tiết xử lý Transaction ([transaction_processor.py](file:///d:/Work/Clients/AIRC/product/ACPA/broker-extraction-api/app/services/transaction_processor.py))

Hệ thống phân loại Transaction dựa vào **"Booking text"** để quyết định logic xử lý ([get_transaction_type](file:///d:/Work/Clients/AIRC/product/ACPA/broker-extraction-api/app/utils.py#229-243)).

| Case (Loại giao dịch)   | Điều kiện nhận diện                                                                                                                                  | Logic trích xuất & Các trường quan trọng                                                                                                                                                                                                 | Output File  |
| :---------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------- |
| **1. Purchase / Sale**  | `Booking text` là:<br>- "Sec. receipt against payment" -> **Purchase**<br>- "Sec. delivery against payment" -> **Sale**<br>- "Sale Spot" -> **Sale** | - **Security**: Lấy từ Description/Custody account.<br>- **ISIN**: Tách từ chuỗi "ISIN...".<br>- **Foreign Unit Price**: Tách từ cột "Cost/Purchase price" hoặc "Transaction price".<br>- **Amount**: Tính toán Gross/Net consideration. | `trade.xlsx` |
| **2. FX Forward**       | `Booking text` chứa "FX Forward"                                                                                                                     | - **Rate**: Lấy từ cột "Cost/Purchase price".<br>- **Buy/Sell**: Phân tích text "You bought..." / "You sold..." để lấy Currency và Amount tương ứng cho 2 chiều Buy/Sell.                                                                | `fx_tf.xlsx` |
| **3. UBS Call Deposit** | `Booking text` chứa:<br>- "Reduction"<br>- "Repayment"<br>- "Interest Cap."                                                                          | - **Description**: Lấy trực tiếp từ Booking text.<br>- **Foreign Gross/Net**: Trích xuất từ cột "Transaction value".                                                                                                                     | `other.xlsx` |
| **4. Default**          | Các trường hợp khác                                                                                                                                  | Lấy theo title của Booking text. (Hiện tại logic map vào `trade.xlsx` nhưng có thể cần review thêm).                                                                                                                                     | `trade.xlsx` |

---

## 3. Chi tiết xử lý Position ([position_processor.py](file:///d:/Work/Clients/AIRC/product/ACPA/broker-extraction-api/app/services/position_processor.py))

Hệ thống xác định loại Position dựa vào tiêu đề section ([get_position_type](file:///d:/Work/Clients/AIRC/product/ACPA/broker-extraction-api/app/utils.py#559-579)).

| Case (Loại tài sản)                                      | Điều kiện nhận diện                                                                                               | Logic trích xuất & Các trường quan trọng                                                                                                                                                                                                                                      | Output File                         |
| :------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------- |
| **1. Liquidity Items**                                   | Header chứa: "Liquidity - Accounts"                                                                               | - **Account No**: Lấy từ Description.<br>- **Amount**: Lấy từ cột Description hoặc cột giá trị cuối cùng.<br>- **Currency**: Map từ danh sách tiền tệ ([app/utils.py](file:///d:/Work/Clients/AIRC/product/ACPA/broker-extraction-api/app/utils.py)).                         | `postion.xlsx`<br>(Type: Liquidity) |
| **2. Standard Positions**<br>(Bonds, Equities, Funds...) | Header chứa:<br>- "Bonds - Bond investments"<br>- "Equities - Equity investments"<br>- "Money market investments" | - **Security Name**: Tách từ Description (loại bỏ mã đầu dòng).<br>- **ISIN**: Tìm "ISIN" trong Description.<br>- **Quantity/Amount**: Logic ưu tiên lấy số từ các cột cuối của "By investment category".<br>- **Cost/Market Price**: Làm sạch ký tự lạ, xử lý phần trăm (%). | `postion.xlsx`                      |

---

## 4. Các quy tắc làm sạch dữ liệu (Data Cleaning Rules)

- **Số (Number)**: Loại bỏ dấu phẩy (`,`), khoảng trắng. Xử lý dấu trừ (`-`) đặt trước hoặc sau số.
- **Ngày (Date)**: Chuyển đổi format từ `dd.mm.yyyy` sang `mm/dd/yyyy`.
- **Tiền tệ (Currency)**: Đối chiếu với danh sách mã tiền tệ chuẩn (ISO 4217) trong [utils.py](file:///d:/Work/Clients/AIRC/product/ACPA/broker-extraction-api/app/utils.py).
- **Tài khoản (Account No)**: Dùng Regex `\b\d{3}-\d{6}\.[A-Z0-9]+\b` để bắt đúng định dạng tài khoản ngân hàng.
