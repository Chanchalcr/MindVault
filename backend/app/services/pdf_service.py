import io
from typing import Optional
from pypdf import PdfReader


class PDFExtractionError(Exception):
    """Custom exception for PDF extraction errors"""
    pass


def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract text from a PDF file.

    Args:
        file_content: PDF file as bytes

    Returns:
        Extracted text as a string

    Raises:
        PDFExtractionError: If PDF is invalid or text extraction fails
    """
    try:
        # Create a file-like object from bytes
        pdf_file = io.BytesIO(file_content)

        # Read the PDF
        reader = PdfReader(pdf_file)

        # Check if PDF has pages
        if len(reader.pages) == 0:
            raise PDFExtractionError("PDF file is empty (no pages)")

        # Extract text from all pages
        text_content = []
        for page_num, page in enumerate(reader.pages, start=1):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
            except Exception as e:
                # Log error but continue with other pages
                print(f"Warning: Failed to extract text from page {page_num}: {e}")

        # Join all pages with newlines
        full_text = "\n\n".join(text_content)

        # Check if any text was extracted
        if not full_text.strip():
            raise PDFExtractionError("No text could be extracted from the PDF. The document may be image-based or empty.")

        return full_text

    except PDFExtractionError:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Catch all other exceptions and wrap them
        raise PDFExtractionError(f"Failed to process PDF file: {str(e)}")


def validate_pdf_size(file_size: int, max_size_mb: int = 10) -> None:
    """
    Validate PDF file size.

    Args:
        file_size: Size of the file in bytes
        max_size_mb: Maximum allowed size in megabytes

    Raises:
        PDFExtractionError: If file is too large
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise PDFExtractionError(f"PDF file too large. Maximum size is {max_size_mb}MB")
