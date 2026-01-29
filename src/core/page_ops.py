"""
Page operations for PDFs.
Includes rotation, removal, and reordering of pages.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable

import fitz  # PyMuPDF


class RotationAngle(Enum):
    """Available rotation angles."""
    CW_90 = 90      # Clockwise 90°
    CW_180 = 180    # 180°
    CCW_90 = 270    # Counter-clockwise 90° (same as CW 270°)


@dataclass
class PageOpResult:
    """Result of a page operation."""
    output_path: Path
    pages_affected: int
    success: bool
    error_message: str = ""


def rotate_pages(
    input_path: str,
    output_path: str,
    angle: RotationAngle,
    page_numbers: list[int] | None = None,
    progress_callback: Callable[[int, str], None] | None = None
) -> PageOpResult:
    """
    Rotate pages in a PDF.

    Args:
        input_path: Path to input PDF
        output_path: Path for output PDF
        angle: Rotation angle
        page_numbers: List of page numbers to rotate (1-indexed), None for all
        progress_callback: Optional callback(percent, message)

    Returns:
        PageOpResult with operation info
    """
    try:
        if progress_callback:
            progress_callback(10, "Åbner PDF...")

        doc = fitz.open(input_path)
        total_pages = doc.page_count

        # Determine which pages to rotate
        if page_numbers is None:
            pages_to_rotate = list(range(total_pages))
        else:
            # Convert 1-indexed to 0-indexed
            pages_to_rotate = [p - 1 for p in page_numbers if 0 < p <= total_pages]

        if progress_callback:
            progress_callback(20, "Roterer sider...")

        pages_affected = 0
        for i, page_num in enumerate(pages_to_rotate):
            if progress_callback:
                percent = 20 + int((i / len(pages_to_rotate)) * 70)
                progress_callback(percent, f"Roterer side {page_num + 1}...")

            page = doc[page_num]
            page.set_rotation(page.rotation + angle.value)
            pages_affected += 1

        if progress_callback:
            progress_callback(95, "Gemmer fil...")

        doc.save(output_path, garbage=4, deflate=True)
        doc.close()

        if progress_callback:
            progress_callback(100, "Færdig!")

        return PageOpResult(
            output_path=Path(output_path),
            pages_affected=pages_affected,
            success=True
        )

    except Exception as e:
        return PageOpResult(
            output_path=Path(output_path),
            pages_affected=0,
            success=False,
            error_message=str(e)
        )


def remove_pages(
    input_path: str,
    output_path: str,
    page_numbers: list[int],
    progress_callback: Callable[[int, str], None] | None = None
) -> PageOpResult:
    """
    Remove pages from a PDF.

    Args:
        input_path: Path to input PDF
        output_path: Path for output PDF
        page_numbers: List of page numbers to remove (1-indexed)
        progress_callback: Optional callback(percent, message)

    Returns:
        PageOpResult with operation info
    """
    try:
        if progress_callback:
            progress_callback(10, "Åbner PDF...")

        doc = fitz.open(input_path)
        total_pages = doc.page_count

        # Convert to 0-indexed and validate
        pages_to_remove = sorted(
            [p - 1 for p in page_numbers if 0 < p <= total_pages],
            reverse=True  # Remove from end to preserve indices
        )

        if not pages_to_remove:
            return PageOpResult(
                output_path=Path(output_path),
                pages_affected=0,
                success=False,
                error_message="Ingen gyldige sider at fjerne"
            )

        # Check we're not removing all pages
        if len(pages_to_remove) >= total_pages:
            return PageOpResult(
                output_path=Path(output_path),
                pages_affected=0,
                success=False,
                error_message="Kan ikke fjerne alle sider"
            )

        if progress_callback:
            progress_callback(30, "Fjerner sider...")

        pages_removed = 0
        for i, page_num in enumerate(pages_to_remove):
            if progress_callback:
                percent = 30 + int((i / len(pages_to_remove)) * 60)
                progress_callback(percent, f"Fjerner side {page_num + 1}...")

            doc.delete_page(page_num)
            pages_removed += 1

        if progress_callback:
            progress_callback(95, "Gemmer fil...")

        doc.save(output_path, garbage=4, deflate=True)
        doc.close()

        if progress_callback:
            progress_callback(100, "Færdig!")

        return PageOpResult(
            output_path=Path(output_path),
            pages_affected=pages_removed,
            success=True
        )

    except Exception as e:
        return PageOpResult(
            output_path=Path(output_path),
            pages_affected=0,
            success=False,
            error_message=str(e)
        )


def extract_pages(
    input_path: str,
    output_path: str,
    page_numbers: list[int],
    progress_callback: Callable[[int, str], None] | None = None
) -> PageOpResult:
    """
    Extract specific pages from a PDF to a new file.

    Args:
        input_path: Path to input PDF
        output_path: Path for output PDF
        page_numbers: List of page numbers to extract (1-indexed)
        progress_callback: Optional callback(percent, message)

    Returns:
        PageOpResult with operation info
    """
    try:
        if progress_callback:
            progress_callback(10, "Åbner PDF...")

        doc = fitz.open(input_path)
        total_pages = doc.page_count

        # Convert to 0-indexed and validate
        pages_to_extract = [p - 1 for p in page_numbers if 0 < p <= total_pages]

        if not pages_to_extract:
            return PageOpResult(
                output_path=Path(output_path),
                pages_affected=0,
                success=False,
                error_message="Ingen gyldige sider at udtrække"
            )

        if progress_callback:
            progress_callback(30, "Udtrækker sider...")

        # Create new document with selected pages
        new_doc = fitz.open()

        for i, page_num in enumerate(pages_to_extract):
            if progress_callback:
                percent = 30 + int((i / len(pages_to_extract)) * 60)
                progress_callback(percent, f"Kopierer side {page_num + 1}...")

            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

        if progress_callback:
            progress_callback(95, "Gemmer fil...")

        new_doc.save(output_path, garbage=4, deflate=True)
        new_doc.close()
        doc.close()

        if progress_callback:
            progress_callback(100, "Færdig!")

        return PageOpResult(
            output_path=Path(output_path),
            pages_affected=len(pages_to_extract),
            success=True
        )

    except Exception as e:
        return PageOpResult(
            output_path=Path(output_path),
            pages_affected=0,
            success=False,
            error_message=str(e)
        )


def get_page_thumbnails(
    pdf_path: str,
    max_size: int = 150
) -> list[tuple[int, bytes]]:
    """
    Generate thumbnail images for each page.

    Args:
        pdf_path: Path to PDF file
        max_size: Maximum dimension for thumbnails

    Returns:
        List of (page_number, png_bytes) tuples (1-indexed page numbers)
    """
    thumbnails = []

    try:
        doc = fitz.open(pdf_path)

        for page_num in range(doc.page_count):
            page = doc[page_num]

            # Calculate scale to fit max_size
            rect = page.rect
            scale = max_size / max(rect.width, rect.height)
            mat = fitz.Matrix(scale, scale)

            # Render to pixmap
            pix = page.get_pixmap(matrix=mat)
            png_bytes = pix.tobytes("png")

            thumbnails.append((page_num + 1, png_bytes))

        doc.close()

    except Exception:
        pass

    return thumbnails
