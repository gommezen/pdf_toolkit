"""
Base PDF operations using PyMuPDF.
"""

from dataclasses import dataclass
from pathlib import Path
from io import BytesIO

import fitz  # PyMuPDF


@dataclass
class PDFInfo:
    """Information about a PDF file."""
    path: Path
    page_count: int
    file_size: int
    title: str | None = None
    author: str | None = None
    subject: str | None = None
    creator: str | None = None


def get_pdf_info(path: str | Path) -> PDFInfo:
    """
    Get metadata about a PDF file.

    Args:
        path: Path to PDF file

    Returns:
        PDFInfo with file metadata

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a valid PDF
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    try:
        doc = fitz.open(path)
        metadata = doc.metadata

        info = PDFInfo(
            path=path,
            page_count=len(doc),
            file_size=path.stat().st_size,
            title=metadata.get('title') or None,
            author=metadata.get('author') or None,
            subject=metadata.get('subject') or None,
            creator=metadata.get('creator') or None,
        )
        doc.close()
        return info

    except Exception as e:
        raise ValueError(f"Invalid PDF file: {e}")


def validate_pdf(path: str | Path) -> bool:
    """
    Check if file is a valid PDF.

    Args:
        path: Path to check

    Returns:
        True if valid PDF, False otherwise
    """
    try:
        doc = fitz.open(path)
        is_valid = len(doc) > 0
        doc.close()
        return is_valid
    except Exception:
        return False


def get_page_thumbnail(
    path: str | Path,
    page_num: int = 0,
    width: int = 150
) -> bytes:
    """
    Generate thumbnail image of a PDF page.

    Args:
        path: Path to PDF file
        page_num: Page number (0-indexed)
        width: Desired thumbnail width in pixels

    Returns:
        PNG image data as bytes
    """
    doc = fitz.open(path)

    if page_num >= len(doc):
        page_num = 0

    page = doc[page_num]

    # Calculate zoom factor for desired width
    zoom = width / page.rect.width
    matrix = fitz.Matrix(zoom, zoom)

    # Render page to pixmap
    pix = page.get_pixmap(matrix=matrix)

    # Convert to PNG bytes
    img_data = pix.tobytes("png")

    doc.close()
    return img_data


def get_page_count(path: str | Path) -> int:
    """
    Get number of pages in PDF.

    Args:
        path: Path to PDF file

    Returns:
        Number of pages
    """
    doc = fitz.open(path)
    count = len(doc)
    doc.close()
    return count


def extract_page(
    input_path: str | Path,
    output_path: str | Path,
    page_num: int
) -> Path:
    """
    Extract a single page from a PDF.

    Args:
        input_path: Source PDF path
        output_path: Output PDF path
        page_num: Page number to extract (0-indexed)

    Returns:
        Path to output file
    """
    output_path = Path(output_path)

    src_doc = fitz.open(input_path)
    dst_doc = fitz.open()

    dst_doc.insert_pdf(src_doc, from_page=page_num, to_page=page_num)
    dst_doc.save(output_path)

    dst_doc.close()
    src_doc.close()

    return output_path


def rotate_page(
    input_path: str | Path,
    output_path: str | Path,
    page_num: int,
    rotation: int
) -> Path:
    """
    Rotate a specific page in a PDF.

    Args:
        input_path: Source PDF path
        output_path: Output PDF path
        page_num: Page number to rotate (0-indexed)
        rotation: Rotation angle (90, 180, or 270)

    Returns:
        Path to output file
    """
    output_path = Path(output_path)

    doc = fitz.open(input_path)
    page = doc[page_num]
    page.set_rotation(rotation)
    doc.save(output_path)
    doc.close()

    return output_path
