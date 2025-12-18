import os
import fitz # PyMuPDF
import config
import utils

def extract_text_from_pdfs():
    print(">>> STARTING PDF EXTRACTION (using PyMuPDF)")
    
    # Ensure output directory exists
    utils.ensure_dir_exists(config.EXTRACTED_TEXT_DIR)
    
    # Stats
    count_success = 0
    count_error = 0
    count_image = 0
    
    error_files = []
    image_files = []
    
    # Get List of PDF files
    if not os.path.exists(config.DATASET_DIR):
        print(f"Error: Dataset directory not found: {config.DATASET_DIR}")
        return

    files = [f for f in os.listdir(config.DATASET_DIR) if f.lower().endswith('.pdf')]
    total_files = len(files)
    print(f"Found {total_files} PDF files in {config.DATASET_DIR}")
    
    for i, filename in enumerate(files):
        pdf_path = os.path.join(config.DATASET_DIR, filename)
        txt_filename = os.path.splitext(filename)[0] + ".txt"
        txt_path = os.path.join(config.EXTRACTED_TEXT_DIR, txt_filename)
        
        try:
            text_content = ""
            # PyMuPDF Open
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text_content += page.get_text() + "\n"
            
            # Analyze extracted text
            clean_text = text_content.strip()
            
            # HEURISTIC: If text is empty or very short (< 50 chars), assume it's an image/scanned PDF
            if not clean_text or len(clean_text) < 50:
                image_files.append(filename)
                count_image += 1
            else:
                count_success += 1

            # Save to text file
            with open(txt_path, 'w', encoding='utf-8') as f_out:
                f_out.write(text_content)
                
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            error_files.append(f"{filename} | Error: {str(e)}")
            count_error += 1
            
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{total_files} files...")

    # Write Report Files
    # 1. Error Files
    with open(config.ERROR_PDF_REPORT, 'w', encoding='utf-8') as f:
        f.write(f"DANH SÁCH FILE LỖI KHÔNG ĐỌC ĐƯỢC ({len(error_files)} files)\n")
        f.write("=" * 60 + "\n")
        f.write('\n'.join(error_files))
    print(f"Error report saved to: {config.ERROR_PDF_REPORT}")

    # 2. Image/Scanned Files
    with open(config.IMAGE_PDF_REPORT, 'w', encoding='utf-8') as f:
        f.write(f"DANH SÁCH FILE ẢNH/KHÔNG CÓ TEXT ({len(image_files)} files)\n")
        f.write("=" * 60 + "\n")
        f.write('\n'.join(image_files))
    print(f"Image report saved to: {config.IMAGE_PDF_REPORT}")

    # Summary
    print("\n>>> EXTRACTION COMPLETE")
    print(f"Total processed: {total_files}")
    print(f"Success (Text found): {count_success}")
    print(f"Image/Scanned (Text empty/low): {count_image}")
    print(f"Errors (Read failed): {count_error}")

if __name__ == "__main__":
    extract_text_from_pdfs()
