"""PDF Toolkit core functionality."""

from .pdf_handler import get_pdf_info, validate_pdf, PDFInfo
from .merger import merge_pdfs, MergeOptions
from .splitter import split_pdf, SplitMode, SplitOptions
from .ocr_engine import (
    OCROptions, OCRLanguage, OCRResult,
    perform_ocr, extract_text_only,
    check_tesseract_available, get_available_languages
)
from .compressor import compress_pdf, CompressionLevel, CompressionResult
from .page_ops import rotate_pages, remove_pages, RotationAngle, PageOpResult
from .encryption import encrypt_pdf, decrypt_pdf, EncryptionResult
from .citation_extractor import (
    extract_citation, to_bibtex, to_json,
    CitationMetadata, CitationResult
)

__all__ = [
    'get_pdf_info', 'validate_pdf', 'PDFInfo',
    'merge_pdfs', 'MergeOptions',
    'split_pdf', 'SplitMode', 'SplitOptions',
    'OCROptions', 'OCRLanguage', 'OCRResult',
    'perform_ocr', 'extract_text_only',
    'check_tesseract_available', 'get_available_languages',
    'compress_pdf', 'CompressionLevel', 'CompressionResult',
    'rotate_pages', 'remove_pages', 'RotationAngle', 'PageOpResult',
    'encrypt_pdf', 'decrypt_pdf', 'EncryptionResult',
    'extract_citation', 'to_bibtex', 'to_json',
    'CitationMetadata', 'CitationResult',
]
