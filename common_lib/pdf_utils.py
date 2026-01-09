"""
PDF text extraction utilities.

Provides functions for extracting text from PDF files using PyMuPDF (fitz).
"""

from pathlib import Path
from typing import Optional
import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path: Path, min_text_length: int = 50) -> Optional[str]:
    """
    Extract text from a PDF file using PyMuPDF.

    Args:
        pdf_path: Path to PDF file (can be Path object or string)
        min_text_length: Minimum text length to consider PDF as text-based

    Returns:
        Extracted text content or None if extraction fails

    Examples:
        >>> text = extract_text_from_pdf("invoice.pdf")
        >>> if text:
        ...     print(f"Extracted {len(text)} characters")
    """
    if isinstance(pdf_path, str):
        pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        return None

    try:
        text_content = ""
        # Open PDF with PyMuPDF
        with fitz.open(pdf_path) as doc:
            # Extract text from each page
            for page in doc:
                text_content += page.get_text() + "\n"

        return text_content.strip()

    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return None


def extract_and_save_to_txt(
    pdf_path: Path, output_txt_path: Path, min_text_length: int = 50
) -> bool:
    """
    Extract text from PDF and save to a TXT file.

    Args:
        pdf_path: Path to PDF file (can be Path object or string)
        output_txt_path: Path for output TXT file (can be Path object or string)
        min_text_length: Minimum text length to consider PDF as text-based

    Returns:
        True if successful, False if extraction or save failed

    Examples:
        >>> success = extract_and_save_to_txt("invoice.pdf", "invoice.txt")
        >>> print(f"Extraction {'succeeded' if success else 'failed'}")
    """
    if isinstance(pdf_path, str):
        pdf_path = Path(pdf_path)
    if isinstance(output_txt_path, str):
        output_txt_path = Path(output_txt_path)

    # Extract text
    text_content = extract_text_from_pdf(pdf_path, min_text_length)

    if text_content is None:
        return False

    # Ensure output directory exists
    output_txt_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Save to TXT file
        with open(output_txt_path, "w", encoding="utf-8") as f_out:
            f_out.write(text_content)
        return True

    except Exception as e:
        print(f"Error saving to {output_txt_path}: {e}")
        return False


def is_text_based_pdf(pdf_path: Path, min_text_length: int = 50) -> bool:
    """
    Check if a PDF contains extractable text (not image/scanned).

    Uses a heuristic: if extracted text is longer than min_text_length,
    consider it text-based.

    Args:
        pdf_path: Path to PDF file (can be Path object or string)
        min_text_length: Minimum text length threshold

    Returns:
        True if PDF contains text, False if it's likely image/scanned

    Examples:
        >>> if is_text_based_pdf("document.pdf"):
        ...     print("Text-based PDF")
        ... else:
        ...     print("Scanned/Image PDF")
    """
    if isinstance(pdf_path, str):
        pdf_path = Path(pdf_path)

    text_content = extract_text_from_pdf(pdf_path, min_text_length)

    if text_content is None:
        return False

    clean_text = text_content.strip()
    return len(clean_text) >= min_text_length
