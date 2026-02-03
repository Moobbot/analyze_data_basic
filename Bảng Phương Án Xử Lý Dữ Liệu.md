# Bảng Phương Án Xử Lý Dữ Liệu (Data Processing Plan)

Tài liệu này mô tả chi tiết phương án xử lý và validate dữ liệu cho các loại giao dịch dựa trên schema đã định nghĩa.

## 1. Trade Information (I.1)
**Mô tả**: Dữ liệu giao dịch mua/bán và các hoạt động liên quan.
**File nguồn**: [trade_information.json](file:///d:/Work/Clients/AIRC/product/ACPA/analyze_data_basic/analyze_data_broker/lib/schemas/trade_information.json)

| Tên trường (Field) | Kiểu (Type) | Bắt buộc | Quy tắc xử lý / Validation | Mô tả |
| :--- | :--- | :---: | :--- | :--- |
| **Transaction Type** | Text | Có | - Kiểm tra từ khóa (Keywords) trong văn bản.<br>- Giá trị cho phép: `BUY`, `SELL`, `BUY CANCELLATION`, `SELL CANCELLATION`, `ADJUSTMENT MAX. NOTIONAL`, `KNOCKOUT ADVICE`, `MATURITY`, `PREPAYMENT...` (xem schema) | Loại giao dịch. |
| **Trade Date** | Date | Có | - Định dạng: `MM/DD/YYYY`<br>- Kiểm tra ngữ cảnh (Context) với từ khóa: `trade date`, `traded on`, ... | Ngày thực hiện giao dịch. |
| **Settlement Date** | Date | Có | - Định dạng: `MM/DD/YYYY`<br>- Kiểm tra ngữ cảnh: `Value date`, `Settlement date`, ... | Ngày thanh toán/bù trừ. |
| **Securities ID** | Text | Có | - Độ dài chính xác: 12 ký tự (ISIN format). | Mã ISIN của chứng khoán. |
| **Quantity** | Number (Float) | Không | - Validate kiểu số.<br>- Lấy giá trị tuyệt đối (nếu là số âm). | Số lượng giao dịch. |
| **Foreign Unit Price** | Number (Float) | Không | - Validate kiểu số. | Đơn giá ngoại tệ. |
| **Foreign Gross Consideration** | Number (Float) | Không | - Validate kiểu số. | Tổng giá trị thô (ngoại tệ). |
| **Foreign Net Consideration** | Number (Float) | Không | - Validate kiểu số. | Giá trị ròng (ngoại tệ). |
| **Net Consideration** | Number (Float) | Không | - Validate kiểu số. | Giá trị ròng (đồng tiền cơ sở). |
| **Exec Commission** | Number (Float) | Không | - Validate kiểu số. | Phí hoa hồng thực hiện. |
| **Client name** | Text | Có | - Validate chuỗi ký tự. | Tên khách hàng. |
| **Name/ Security** | Text | Có | - Validate chuỗi ký tự. | Tên chứng khoán. |
| **Currency** | Text | Có | - Regex: `^[A-Z]{3}$` (Mã 3 ký tự in hoa). | Mã tiền tệ (ISO 4217). |
| **Account no.** | Text | Không | - Validate chuỗi ký tự. | Số tài khoản (Optional). |
| **Accrued Interest** | Number (Float) | Không | - Validate kiểu số. | Lãi tích lũy. |
| **Result/Research Commission** | Number (Float) | Không | - Validate kiểu số. | Các loại phí hoa hồng khác. |
| **Fees/Taxes** (Local Fee, Local Tax, Stamp Duty...) | Number (Float) | Không | - Validate kiểu số. | Các loại phí và thuế địa phương. |
| **GST Fields** (Foreign GST, GST Equivalent, ...) | Number (Float) | Không | - Validate kiểu số. | Thông tin về thuế GST. |

---

## 2. Dividend Information (I.2)
**Mô tả**: Thông tin thanh toán cổ tức.
**File nguồn**: [dividend_information.json](file:///d:/Work/Clients/AIRC/product/ACPA/analyze_data_basic/analyze_data_broker/lib/schemas/dividend_information.json)

| Tên trường (Field) | Kiểu (Type) | Bắt buộc | Quy tắc xử lý / Validation | Mô tả |
| :--- | :--- | :---: | :--- | :--- |
| **Ex-Date** | Date | Có | - Định dạng: `MM/DD/YYYY` | Ngày giao dịch không hưởng quyền. |
| **Payment Date** | Date | Có | - Định dạng: `MM/DD/YYYY` | Ngày thanh toán. |
| **Securities ID** | Text | Có | - Validate chuỗi ký tự (ISIN nếu có). | Mã chứng khoán. |
| **Dividend Rate** | Number (Float) | Không | - Validate kiểu số. | Tỷ lệ cổ tức (số hoặc %). |
| **WHT Rate** | Mixed (Text/%) | Không | - Cho phép số hoặc chuỗi phần trăm (VD: "30%", "0.30"). | Thuế suất thuế nhà thầu (Withholding Tax). |
| **Name/ Security** | Text | Có | - Validate chuỗi ký tự. | Tên chứng khoán. |
| **Client name** | Text | Có | - Validate chuỗi ký tự. | Tên khách hàng. |
| **Currency** | Text | Có | - Regex: `^[A-Z]{3}$` | Mã tiền tệ. |
| **Units** | Number (Float) | Có | - Validate kiểu số. | Số lượng cổ phiếu/đơn vị nắm giữ. |
| **Gross Dividend Amount (Local)** | Number (Float) | Không | - Validate kiểu số. | Tổng cổ tức trước thuế (nội tệ). |
| **WHT Amount** | Number (Float) | Không | - Validate kiểu số. | Số tiền thuế đã khấu trừ. |
| **Net Dividend Amount (Local)** | Number (Float) | Không | - Validate kiểu số. | Cổ tức thực nhận (nội tệ). |
| **Net consideration** | Number (Float) | Không | - Validate kiểu số. | Giá trị ròng (đồng tiền cơ sở). |
| **Account no.** | Text | Không | - Validate chuỗi ký tự. | Số tài khoản. |

---

## 3. FX & TF (I.3)
**Mô tả**: Giao dịch ngoại hối (Foreign Exchange) và Transfer Forward.
**File nguồn**: [fx_tf.json](file:///d:/Work/Clients/AIRC/product/ACPA/analyze_data_basic/analyze_data_broker/lib/schemas/fx_tf.json)

| Tên trường (Field) | Kiểu (Type) | Bắt buộc | Quy tắc xử lý / Validation | Mô tả |
| :--- | :--- | :---: | :--- | :--- |
| **Client name** | Text | Có | - Validate chuỗi ký tự. | Tên khách hàng. |
| **Transaction type** | Text | Có | - Validate chuỗi ký tự. | Loại giao dịch FX/TF. |
| **Trade date** | Date | Có | - Định dạng: `MM/DD/YYYY` | Ngày giao dịch. |
| **Settlement date** | Date | Không | - Định dạng: `MM/DD/YYYY` | Ngày thanh toán. |
| **Rate** | Number (Float) | Không | - Validate kiểu số. | Tỷ giá hối đoái. |
| **Currency Buy** | Text | Có | - Regex: `^[A-Z]{3}$` | Đồng tiền mua. |
| **Amount Buy** | Number (Float) | Không | - Validate kiểu số. | Số tiền mua. |
| **Currency Sell** | Text | Có | - Regex: `^[A-Z]{3}$` | Đồng tiền bán. |
| **Amount Sell** | Number (Float) | Không | - Validate kiểu số. | Số tiền bán. |
| **Account no. Buy** | Text | Không | - Validate chuỗi ký tự. | Số tài khoản bên mua. |
| **Account no. Sell** | Text | Không | - Validate chuỗi ký tự. | Số tài khoản bên bán. |

---

## 4. Others (I.4)
**Mô tả**: Các giao dịch khác (Miscellaneous).
**File nguồn**: [others.json](file:///d:/Work/Clients/AIRC/product/ACPA/analyze_data_basic/analyze_data_broker/lib/schemas/others.json)
**Dấu hiệu nhận diện**: Có trường `Description` và `Trade date` nhưng không khớp các mẫu trên.

| Tên trường (Field) | Kiểu (Type) | Bắt buộc | Quy tắc xử lý / Validation | Mô tả |
| :--- | :--- | :---: | :--- | :--- |
| **Client name** | Text | Có | - Validate chuỗi ký tự. | Tên khách hàng. |
| **Description** | Text | Tidak (Optional) | - Validate chuỗi ký tự. | Mô tả giao dịch. |
| **Securities ID / Ref-No.** | Text | Không | - Validate chuỗi ký tự. | Mã chứng khoán hoặc số tham chiếu. |
| **Transaction type** | Text | Không | - Validate chuỗi ký tự. | Loại giao dịch. |
| **Trade/Settlement date** | Date | Không | - Định dạng: `MM/DD/YYYY` | Ngày giao dịch / thanh toán. |
| **Currency** | Text | Không | - Regex: `^[A-Z]{3}$` | Mã tiền tệ. |
| **Quantity** | Number (Float) | Không | - Validate kiểu số. | Số lượng. |
| **Foreign Unit Price** | Mixed | Không | - Số hoặc Phần trăm. | Đơn giá hoặc lãi suất ngoại tệ. |
| **Tax rate (%)** | Mixed | Không | - Số hoặc Phần trăm. | Thuế suất. |
| **Amounts** (Foreign Gross/Net, Tax, SGD) | Number (Float) | Không | - Validate kiểu số. | Các giá trị tiền tệ. |
| **Payment mode** | Text | Không | - Validate chuỗi ký tự. | Phương thức thanh toán. |
| **Exrate to GST** | Number (Float) | Không | - Validate kiểu số. | Tỷ giá tính GST. |

---

## 5. Positions (I.5)
**Mô tả**: Báo cáo vị thế danh mục đầu tư (Portfolio Snapshot).
**File nguồn**: [positions.json](file:///d:/Work/Clients/AIRC/product/ACPA/analyze_data_basic/analyze_data_broker/lib/schemas/positions.json)

| Tên trường (Field) | Kiểu (Type) | Bắt buộc | Quy tắc xử lý / Validation | Mô tả |
| :--- | :--- | :---: | :--- | :--- |
| **Portfolio No.** | Text | Có | - Validate chuỗi ký tự. | Số danh mục đầu tư. |
| **Type** | Text | Có | - Validate chuỗi ký tự. | Loại tài sản (Equity, Bond, Cash...). |
| **Account No** | Text | Không | - Validate chuỗi ký tự. | Số tài khoản. |
| **Currency** | Text | Có | - Regex: `^[A-Z]{3}$` | Mã tiền tệ. |
| **Quantity/ Amount** | Number (Float) | Không | - Validate kiểu số. | Số lượng hoặc số tiền. |
| **Security ID** | Text | Không | - Validate chuỗi ký tự. | Mã chứng khoán (Lưu ý: có thể có dấu cách đầu). |
| **Security name** | Text | Không | - Validate chuỗi ký tự. | Tên chứng khoán. |
| **Cost price** | Number (Float) | Không | - Validate kiểu số. | Giá vốn. |
| **Market price** | Mixed | Không | - Số hoặc Phần trăm. | Giá thị trường hiện tại. |
| **Market value** | Number (Float) | Không | - Validate kiểu số. | Giá trị thị trường. |
| **Accrued interest** | Number (Float) | Không | - Validate kiểu số. | Lãi tích lũy. |
| **Valuation date** | Date | Có | - Định dạng: `MM/DD/YYYY` | Ngày định giá. |

---

## 6. Bank Account Transaction (I.6)
**Mô tả**: Sao kê tài khoản ngân hàng.
**File nguồn**: [bank_account_transaction.json](file:///d:/Work/Clients/AIRC/product/ACPA/analyze_data_basic/analyze_data_broker/lib/schemas/bank_account_transaction.json)
**Cấu trúc đặc biệt**: Chứa mảng các bản ghi (`Records`).

| Tên trường (Field) | Kiểu (Type) | Bắt buộc | Quy tắc xử lý / Validation | Mô tả |
| :--- | :--- | :---: | :--- | :--- |
| **Account no.** | Text | Có | - Validate chuỗi ký tự. | Số tài khoản ngân hàng. |
| **Currency** | Text | Có | - Regex: `^[A-Z]{3}$` | Mã tiền tệ của tài khoản. |
| **Records** | Array | Có | - Danh sách các giao dịch con. | Mảng chứa chi tiết giao dịch. |

### Chi tiết bản ghi trong "Records":

| Tên trường (Field) | Kiểu (Type) | Bắt buộc | Quy tắc xử lý / Validation | Mô tả |
| :--- | :--- | :---: | :--- | :--- |
| **Date** | Date | Có | - Định dạng: `MM/DD/YYYY` | Ngày giao dịch. |
| **Transaction type** | Text | Có | - Kiểm tra Keywords (Opening balance, FOREX SALE, INTEREST...).<br>- Xem danh sách `allowed_values`. | Loại giao dịch ngân hàng. |
| **Reference** | Text | Không | - Validate chuỗi ký tự (có thể nhiều dòng). | Số tham chiếu / Diễn giải. |
| **Amounts** | Number (Float) | Có | - Kết hợp từ cột Debit (âm) và Credit (dương). | Số tiền giao dịch (+/-). |
| **Value date** | Date | Có | - Định dạng: `MM/DD/YYYY` | Ngày hiệu lực. |
| **Balances** | Number (Float) | Có | - Validate kiểu số. | Số dư sau giao dịch. |
