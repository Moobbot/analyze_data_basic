import os
import json
import uuid

# --- CẤU HÌNH ĐƯỜNG DẪN (Bạn chỉnh sửa phần này) ---

# 1. Đường dẫn folder gốc chứa các folder con (Credit Note, Invoice...)
INPUT_ROOT_FOLDER = "datasets/data-all/true-2026-01-11/labels"

# 2. Tên file kết quả đầu ra
OUTPUT_FILE = (
    "datasets/data-all/true-2026-01-11/acpa_invoice_sft_dataset_generated.jsonl"
)

# 3. Đường dẫn giả định cho ảnh trong server training (Prefix)
# Code sẽ ghép: IMAGE_PREFIX + Tên_File.png
IMAGE_PREFIX = "playground/invoices/acpa_pdf_images/"

# 4. Đuôi file ảnh bạn muốn gán (png, jpg, jpeg...)
IMAGE_EXTENSION = ".png"

# ----------------------------------------------------


def generate_jsonl_from_folders(root_folder, output_path, img_prefix, img_ext):
    print(f"🔄 Đang quét folder: {root_folder}...")

    records = []
    file_count = 0

    # os.walk sẽ duyệt qua root_folder và TẤT CẢ các folder con bên trong
    for current_root, dirs, files in os.walk(root_folder):
        for filename in files:
            if filename.endswith(".json"):
                json_path = os.path.join(current_root, filename)

                try:
                    # 1. Đọc nội dung file JSON
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    # 2. Chuẩn bị dữ liệu cho jsonl
                    # Tạo ID duy nhất
                    unique_id = uuid.uuid4().hex

                    # Tạo tên file ảnh tương ứng (Lấy tên file json bỏ đuôi .json, thêm đuôi ảnh)
                    base_name = os.path.splitext(filename)[0]
                    image_filename = base_name + img_ext

                    # Tạo đường dẫn ảnh đầy đủ (dùng forward slash '/' cho chuẩn json)
                    full_image_path = os.path.join(img_prefix, image_filename).replace(
                        "\\", "/"
                    )

                    # Chuyển nội dung JSON thành string để đưa vào prompt
                    json_str_content = json.dumps(data, ensure_ascii=False)

                    # Tạo nội dung conversation
                    conversation = [
                        {
                            "from": "human",
                            "value": "<image>\nExtract structured data from the acpa invoice and return JSON.",
                        },
                        {"from": "gpt", "value": f"```json\n{json_str_content}\n```"},
                    ]

                    # Tạo record hoàn chỉnh
                    record = {
                        "id": unique_id,
                        "image": full_image_path,
                        "width": 0,  # Mặc định là 0 vì trong file json không có thông tin size ảnh
                        "height": 0,  # Mặc định là 0
                        "conversations": conversation,
                    }

                    records.append(record)
                    file_count += 1

                except Exception as e:
                    print(f"❌ Lỗi đọc file {filename}: {e}")

    # 3. Ghi tất cả ra file .jsonl
    print(f"💾 Đang ghi {file_count} dòng vào file {output_path}...")
    with open(output_path, "w", encoding="utf-8") as out_f:
        for rec in records:
            # ensure_ascii=False để giữ nguyên tiếng Việt nếu có
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print("✅ Hoàn tất!")


if __name__ == "__main__":
    if os.path.exists(INPUT_ROOT_FOLDER):
        generate_jsonl_from_folders(
            INPUT_ROOT_FOLDER, OUTPUT_FILE, IMAGE_PREFIX, IMAGE_EXTENSION
        )
    else:
        print(f"❌ Không tìm thấy đường dẫn: {INPUT_ROOT_FOLDER}")
