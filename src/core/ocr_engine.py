"""
OCR processing engine using Tesseract.
Converts scanned PDFs and images to searchable PDFs.
"""

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable

import fitz  # PyMuPDF

# Optional imports - handle gracefully if not installed
try:
    import pytesseract
    from PIL import Image
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

try:
    from pdf2image import convert_from_path
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False


class OCRLanguage(Enum):
    """Supported OCR languages."""
    DANISH = "dan"
    ENGLISH = "eng"
    DANISH_ENGLISH = "dan+eng"


@dataclass
class OCROptions:
    """Options for OCR processing."""
    language: OCRLanguage = OCRLanguage.DANISH
    dpi: int = 300
    preserve_original: bool = True  # Keep original appearance, add text layer


@dataclass
class OCRResult:
    """Result of an OCR operation."""
    output_path: Path
    pages_processed: int
    text_extracted: str
    success: bool
    error_message: str = ""


def check_tesseract_available(tesseract_path: str = "") -> tuple[bool, str]:
    """
    Check if Tesseract OCR is available.

    Returns:
        Tuple of (is_available, message)
    """
    if not HAS_TESSERACT:
        return False, "pytesseract ikke installeret. Kør: pip install pytesseract"

    # Set custom path if provided
    if tesseract_path and os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

    try:
        version = pytesseract.get_tesseract_version()
        return True, f"Tesseract {version} fundet"
    except Exception as e:
        return False, f"Tesseract ikke fundet: {e}\nInstaller fra: https://github.com/UB-Mannheim/tesseract/wiki"


def get_available_languages(tesseract_path: str = "") -> list[str]:
    """Get list of available Tesseract languages."""
    if not HAS_TESSERACT:
        return []

    if tesseract_path and os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

    try:
        langs = pytesseract.get_languages()
        return [l for l in langs if l != 'osd']  # Remove orientation detection
    except Exception:
        return []


def is_scanned_pdf(pdf_path: str) -> bool:
    """
    Check if a PDF appears to be scanned (image-based without text).

    Returns True if the PDF has very little extractable text relative to pages.
    """
    try:
        doc = fitz.open(pdf_path)
        total_text = ""
        for page in doc:
            total_text += page.get_text()
        doc.close()

        # If average text per page is very low, it's likely scanned
        avg_chars_per_page = len(total_text.strip()) / max(doc.page_count, 1)
        return avg_chars_per_page < 100
    except Exception:
        return True  # Assume scanned if we can't read it


def perform_ocr(
    input_path: str,
    output_path: str,
    options: OCROptions,
    tesseract_path: str = "",
    progress_callback: Callable[[int, str], None] | None = None
) -> OCRResult:
    """
    Perform OCR on a PDF or image file.

    Args:
        input_path: Path to input PDF or image
        output_path: Path for output searchable PDF
        options: OCR processing options
        tesseract_path: Optional custom Tesseract path
        progress_callback: Optional callback(percent, message)

    Returns:
        OCRResult with processing information
    """
    if not HAS_TESSERACT:
        return OCRResult(
            output_path=Path(output_path),
            pages_processed=0,
            text_extracted="",
            success=False,
            error_message="pytesseract ikke installeret"
        )

    # Set tesseract path if provided
    if tesseract_path and os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

    input_ext = Path(input_path).suffix.lower()

    try:
        if input_ext == '.pdf':
            return _ocr_pdf(input_path, output_path, options, progress_callback)
        elif input_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp']:
            return _ocr_image(input_path, output_path, options, progress_callback)
        else:
            return OCRResult(
                output_path=Path(output_path),
                pages_processed=0,
                text_extracted="",
                success=False,
                error_message=f"Ikke-understøttet filtype: {input_ext}"
            )
    except Exception as e:
        return OCRResult(
            output_path=Path(output_path),
            pages_processed=0,
            text_extracted="",
            success=False,
            error_message=str(e)
        )


def _ocr_pdf(
    input_path: str,
    output_path: str,
    options: OCROptions,
    progress_callback: Callable[[int, str], None] | None = None
) -> OCRResult:
    """Perform OCR on a PDF file using Tesseract's PDF output."""

    doc = fitz.open(input_path)
    total_pages = doc.page_count
    all_text = []
    pdf_pages = []

    for page_num, page in enumerate(doc):
        if progress_callback:
            percent = int((page_num / total_pages) * 85)
            progress_callback(percent, f"Behandler side {page_num + 1}/{total_pages}...")

        # Get page as image at specified DPI
        mat = fitz.Matrix(options.dpi / 72, options.dpi / 72)
        pix = page.get_pixmap(matrix=mat)

        # Convert to PIL Image for Tesseract
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        lang = options.language.value

        # Get plain text for result
        page_text = pytesseract.image_to_string(img, lang=lang)
        all_text.append(page_text)

        # Generate searchable PDF page using Tesseract
        # This creates a PDF with invisible text layer properly
        pdf_bytes = pytesseract.image_to_pdf_or_hocr(
            img,
            lang=lang,
            extension='pdf',
            config=f'--dpi {options.dpi}'
        )
        pdf_pages.append(pdf_bytes)

    doc.close()

    if progress_callback:
        progress_callback(90, "Kombinerer sider...")

    # Combine all PDF pages
    output_doc = fitz.open()

    for i, pdf_bytes in enumerate(pdf_pages):
        if progress_callback:
            progress_callback(90 + int((i / len(pdf_pages)) * 8), f"Samler side {i + 1}...")

        # Open the single-page PDF from bytes
        page_doc = fitz.open("pdf", pdf_bytes)
        output_doc.insert_pdf(page_doc)
        page_doc.close()

    if progress_callback:
        progress_callback(98, "Gemmer fil...")

    # Save output
    output_doc.save(output_path, garbage=4, deflate=True)
    output_doc.close()

    if progress_callback:
        progress_callback(100, "Færdig!")

    return OCRResult(
        output_path=Path(output_path),
        pages_processed=total_pages,
        text_extracted="\n\n".join(all_text),
        success=True
    )


def _ocr_image(
    input_path: str,
    output_path: str,
    options: OCROptions,
    progress_callback: Callable[[int, str], None] | None = None
) -> OCRResult:
    """Perform OCR on an image file and create a searchable PDF."""

    if progress_callback:
        progress_callback(10, "Indlæser billede...")

    # Open image
    img = Image.open(input_path)

    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')

    if progress_callback:
        progress_callback(30, "Udfører OCR...")

    lang = options.language.value

    # Get plain text for result
    page_text = pytesseract.image_to_string(img, lang=lang)

    if progress_callback:
        progress_callback(60, "Opretter søgbar PDF...")

    # Generate searchable PDF directly using Tesseract
    # This creates a PDF with proper invisible text layer
    pdf_bytes = pytesseract.image_to_pdf_or_hocr(
        img,
        lang=lang,
        extension='pdf',
        config=f'--dpi {options.dpi}'
    )

    if progress_callback:
        progress_callback(90, "Gemmer fil...")

    # Save the PDF
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)

    if progress_callback:
        progress_callback(100, "Færdig!")

    return OCRResult(
        output_path=Path(output_path),
        pages_processed=1,
        text_extracted=page_text,
        success=True
    )


def extract_text_only(
    input_path: str,
    options: OCROptions,
    tesseract_path: str = "",
    progress_callback: Callable[[int, str], None] | None = None
) -> tuple[str, bool, str]:
    """
    Extract text from PDF or image without creating searchable PDF.

    Returns:
        Tuple of (extracted_text, success, error_message)
    """
    if not HAS_TESSERACT:
        return "", False, "pytesseract ikke installeret"

    if tesseract_path and os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

    input_ext = Path(input_path).suffix.lower()
    lang = options.language.value

    try:
        if input_ext == '.pdf':
            doc = fitz.open(input_path)
            all_text = []

            for page_num, page in enumerate(doc):
                if progress_callback:
                    percent = int((page_num / doc.page_count) * 90)
                    progress_callback(percent, f"Side {page_num + 1}/{doc.page_count}...")

                mat = fitz.Matrix(options.dpi / 72, options.dpi / 72)
                pix = page.get_pixmap(matrix=mat)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                text = pytesseract.image_to_string(img, lang=lang)
                all_text.append(text)

            doc.close()
            return "\n\n".join(all_text), True, ""

        elif input_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp']:
            if progress_callback:
                progress_callback(50, "Udfører OCR...")

            img = Image.open(input_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            text = pytesseract.image_to_string(img, lang=lang)
            return text, True, ""

        else:
            return "", False, f"Ikke-understøttet filtype: {input_ext}"

    except Exception as e:
        return "", False, str(e)
