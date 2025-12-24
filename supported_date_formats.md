# Các định dạng Date được hỗ trợ (Supported Date Formats)

Hệ thống hiện tại hỗ trợ các định dạng ngày tháng sau (trong `verify_labels.py`):

## 1. Định dạng chuẩn (Standard)
- `DD/MM/YYYY` (e.g., 03/10/2023)
- `MM/DD/YYYY` (e.g., 10/03/2023)
- `YYYY-MM-DD` (e.g., 2023-10-03)
- `YYYY/MM/DD` (e.g., 2023/07/07)
- `DD-MM-YYYY` (e.g., 03-10-2023)
- `MM-DD-YYYY` (e.g., 10-03-2023)

## 2. Định dạng chữ (Text-based)
- **Khoảng trắng (Spaces):**
  - `DD Mon YYYY` (e.g., 03 Oct 2023)
  - `DD Month YYYY` (e.g., 03 October 2023)
  - `Month DD, YYYY` (e.g., October 03, 2023)
  - `DD Mon, YYYY` (e.g., 03 Oct, 2023)
  - `D Mon YYYY` (e.g., 3 Oct 2023) - *Day without leading zero*

- **Gạch nối (Hyphens):**
  - `DD-Mon-YYYY` (e.g., 03-Oct-2023)
  - `DD-Mon-YY` (e.g., 03-Oct-23)
  - `D-Mon-YYYY` (e.g., 5-Sep-2021)
  - `DD-Month-YYYY` (e.g., 30-April-2023)
  - `DD-Month-YY` (e.g., 30-April-23)
  - **Lưu ý:** Hỗ trợ cả Soft Hyphen (`\xad`) ẩn (ví dụ: `01­Nov­2021`).

- **Hỗn hợp (Mixed):**
  - `DD-Month YYYY` (e.g., 30-April 2023)
  - `DD-Month YY` (e.g., 30-April 23)
  - `{D}-{Mon} {YYYY}` (e.g., 31-Jan 2024)

## 3. Định dạng dấu chấm (Dot-separated)
- `DD.MM.YYYY` (e.g., 14.11.2022)
- `DD.MM.YY` (e.g., 14.11.22)
- `D.M.YYYY` (e.g., 3.4.2023)
- `D.M.YY` (e.g., 3.4.23)

## 4. Định dạng đặc biệt (Special)
- **Không khoảng trắng (Compact):**
  - `DDMonYYYY` (e.g., 23Dec2022)
  - `DDMonthYYYY` (e.g., 23December2022)

- **Số thứ tự (Ordinal):**
  - `MonthDaySuffix, Year` (e.g., November25th, 2022)
  - `MONTHDaySuffix, Year` (e.g., NOVEMBER25TH, 2022)
  - `MONTH DaySuffix, Year` (e.g., NOVEMBER 25TH, 2022) - *With space*
  - `MonthDaySuffix,Year` (e.g., Jul 1st,2025) - *No space after comma*
  - `DaySuffix Month Year` (e.g., 2nd Dec 2022)

- **Ngày không số 0 đầu (Single digit day):**
  - `Mon D, YYYY` (e.g., Jul 3, 2023)
  - `Month D, YYYY` (e.g., July 3, 2023)

- **Ký tự ẩn (Hidden Characters):**
  - `DD­Mon­YYYY` (e.g., 01­Nov­2021) - *Contains Soft Hyphen (U+00AD)*
