"""PDF Toolkit core functionality."""

from .pdf_handler import get_pdf_info, validate_pdf, PDFInfo
from .merger import merge_pdfs, MergeOptions
from .splitter import split_pdf, SplitMode, SplitOptions
from .ocr_engine import (
    OCROptions, OCRLanguage, OCRResult,
    perform_ocr, extract_text_only,
    check_tesseract_available, get_available_languages
)

__all__ = [
    'get_pdf_info', 'validate_pdf', 'PDFInfo',
    'merge_pdfs', 'MergeOptions',
    'split_pdf', 'SplitMode', 'SplitOptions',
    'OCROptions', 'OCRLanguage', 'OCRResult',
    'perform_ocr', 'extract_text_only',
    'check_tesseract_available', 'get_available_languages'
]
