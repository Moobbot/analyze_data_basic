import os
import time
import PyPDF2
import fitz  # PyMuPDF
import pdfplumber
import config
import utils

def extract_with_pypdf2(path):
    start_time = time.time()
    text = ""
    try:
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                t = page.extract_text()
                if t: text += t + "\n"
    except Exception as e:
        text = f"Error: {e}"
    duration = time.time() - start_time
    return text, duration

def extract_with_pymupdf(path):
    start_time = time.time()
    text = ""
    try:
        doc = fitz.open(path)
        for page in doc:
            text += page.get_text() + "\n"
    except Exception as e:
        text = f"Error: {e}"
    duration = time.time() - start_time
    return text, duration

def extract_with_pdfplumber(path):
    start_time = time.time()
    text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: text += t + "\n"
    except Exception as e:
        text = f"Error: {e}"
    duration = time.time() - start_time
    return text, duration

def compare_libs():
    # Target file
    filename = "[TO CANCEL] Theme International - Sphere Invoice INV-23100208[45].pdf"
    pdf_path = os.path.join(config.DATASET_DIR, filename)
    
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        # Try to find another one
        files = [f for f in os.listdir(config.DATASET_DIR) if f.endswith('.pdf')]
        if not files:
            print("No PDF files found.")
            return
        pdf_path = os.path.join(config.DATASET_DIR, files[0])
        print(f"Using alternative file: {files[0]}")
    else:
        print(f"Using target file: {filename}")

    output_dir = os.path.join(config.BASE_DIR, "lib_comparison")
    utils.ensure_dir_exists(output_dir)

    print("-" * 60)
    
    # 1. PyPDF2
    print("Testing PyPDF2...")
    text_pypdf2, time_pypdf2 = extract_with_pypdf2(pdf_path)
    with open(os.path.join(output_dir, "output_pypdf2.txt"), 'w', encoding='utf-8') as f:
        f.write(text_pypdf2)
    print(f"  Duration: {time_pypdf2:.4f}s")
    print(f"  Length: {len(text_pypdf2)} chars")

    # 2. PyMuPDF
    print("Testing PyMuPDF (fitz)...")
    text_fitz, time_fitz = extract_with_pymupdf(pdf_path)
    with open(os.path.join(output_dir, "output_pymupdf.txt"), 'w', encoding='utf-8') as f:
        f.write(text_fitz)
    print(f"  Duration: {time_fitz:.4f}s")
    print(f"  Length: {len(text_fitz)} chars")

    # 3. pdfplumber
    print("Testing pdfplumber...")
    text_plumber, time_plumber = extract_with_pdfplumber(pdf_path)
    with open(os.path.join(output_dir, "output_pdfplumber.txt"), 'w', encoding='utf-8') as f:
        f.write(text_plumber)
    print(f"  Duration: {time_plumber:.4f}s")
    print(f"  Length: {len(text_plumber)} chars")

    print("-" * 60)
    print(f"Outputs saved to: {output_dir}")

if __name__ == "__main__":
    compare_libs()
