"""
PDF split functionality using PyMuPDF.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable

import fitz  # PyMuPDF

from src.core.utils import parse_page_ranges


class SplitMode(Enum):
    """Available split modes."""
    SINGLE_PAGES = "single"      # One file per page
    PAGE_RANGES = "ranges"       # Split by specified ranges
    EQUAL_PARTS = "equal"        # Split into N equal parts
    EXTRACT_PAGES = "extract"    # Extract specific pages to one file


@dataclass
class SplitOptions:
    """Options for PDF split operation."""
    mode: SplitMode
    ranges: str | None = None      # For PAGE_RANGES: e.g., "1-3, 5, 8-10"
    parts: int | None = None       # For EQUAL_PARTS: number of parts
    pages: list[int] | None = None # For EXTRACT_PAGES: specific pages (0-indexed)
    output_prefix: str = ""        # Prefix for output files


@dataclass
class SplitResult:
    """Result of a split operation."""
    output_files: list[Path]
    total_pages_processed: int


def split_pdf(
    input_path: str | Path,
    output_dir: str | Path,
    options: SplitOptions,
    progress_callback: Callable[[int, str], None] | None = None
) -> SplitResult:
    """
    Split a PDF file according to specified options.

    Args:
        input_path: Path to input PDF
        output_dir: Directory for output files
        options: Split configuration
        progress_callback: Optional callback(percent, message)

    Returns:
        SplitResult with list of created files
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(input_path)
    total_pages = len(doc)
    base_name = options.output_prefix or input_path.stem

    output_files = []

    if options.mode == SplitMode.SINGLE_PAGES:
        output_files = _split_single_pages(
            doc, output_dir, base_name, progress_callback
        )

    elif options.mode == SplitMode.PAGE_RANGES:
        if not options.ranges:
            raise ValueError("Page ranges must be specified for RANGES mode")
        output_files = _split_by_ranges(
            doc, output_dir, base_name, options.ranges, progress_callback
        )

    elif options.mode == SplitMode.EQUAL_PARTS:
        if not options.parts or options.parts < 2:
            raise ValueError("Number of parts must be >= 2 for EQUAL_PARTS mode")
        output_files = _split_equal_parts(
            doc, output_dir, base_name, options.parts, progress_callback
        )

    elif options.mode == SplitMode.EXTRACT_PAGES:
        if not options.pages:
            raise ValueError("Pages must be specified for EXTRACT mode")
        output_files = _extract_pages(
            doc, output_dir, base_name, options.pages, progress_callback
        )

    doc.close()

    return SplitResult(
        output_files=output_files,
        total_pages_processed=total_pages
    )


def _split_single_pages(
    doc: fitz.Document,
    output_dir: Path,
    base_name: str,
    progress_callback: Callable[[int, str], None] | None
) -> list[Path]:
    """Split PDF into one file per page."""
    output_files = []
    total = len(doc)

    for i in range(total):
        if progress_callback:
            percent = int((i / total) * 100)
            progress_callback(percent, f"Side {i + 1} af {total}...")

        output_path = output_dir / f"{base_name}_side_{i + 1:03d}.pdf"

        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=i, to_page=i)
        new_doc.save(output_path)
        new_doc.close()

        output_files.append(output_path)

    if progress_callback:
        progress_callback(100, "Færdig!")

    return output_files


def _split_by_ranges(
    doc: fitz.Document,
    output_dir: Path,
    base_name: str,
    ranges_str: str,
    progress_callback: Callable[[int, str], None] | None
) -> list[Path]:
    """Split PDF by specified page ranges."""
    output_files = []

    # Parse ranges into groups
    # Format: "1-3; 5-7; 10-12" creates 3 files
    # or "1-3, 5, 8-10" creates 1 file with those pages
    range_groups = ranges_str.split(';')

    total = len(range_groups)
    for i, range_group in enumerate(range_groups):
        range_group = range_group.strip()
        if not range_group:
            continue

        if progress_callback:
            percent = int((i / total) * 100)
            progress_callback(percent, f"Opretter fil {i + 1} af {total}...")

        pages = parse_page_ranges(range_group, len(doc))
        if not pages:
            continue

        output_path = output_dir / f"{base_name}_del_{i + 1:02d}.pdf"

        new_doc = fitz.open()
        for page_num in pages:
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        new_doc.save(output_path)
        new_doc.close()

        output_files.append(output_path)

    if progress_callback:
        progress_callback(100, "Færdig!")

    return output_files


def _split_equal_parts(
    doc: fitz.Document,
    output_dir: Path,
    base_name: str,
    num_parts: int,
    progress_callback: Callable[[int, str], None] | None
) -> list[Path]:
    """Split PDF into N equal parts."""
    output_files = []
    total_pages = len(doc)
    pages_per_part = total_pages // num_parts
    remainder = total_pages % num_parts

    start_page = 0
    for i in range(num_parts):
        if progress_callback:
            percent = int((i / num_parts) * 100)
            progress_callback(percent, f"Opretter del {i + 1} af {num_parts}...")

        # Distribute remainder pages across first parts
        extra = 1 if i < remainder else 0
        end_page = start_page + pages_per_part + extra - 1

        output_path = output_dir / f"{base_name}_del_{i + 1:02d}.pdf"

        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)
        new_doc.save(output_path)
        new_doc.close()

        output_files.append(output_path)
        start_page = end_page + 1

    if progress_callback:
        progress_callback(100, "Færdig!")

    return output_files


def _extract_pages(
    doc: fitz.Document,
    output_dir: Path,
    base_name: str,
    pages: list[int],
    progress_callback: Callable[[int, str], None] | None
) -> list[Path]:
    """Extract specific pages into a single file."""
    if progress_callback:
        progress_callback(50, "Udtrækker sider...")

    output_path = output_dir / f"{base_name}_udvalgte.pdf"

    new_doc = fitz.open()
    for page_num in sorted(pages):
        if 0 <= page_num < len(doc):
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

    new_doc.save(output_path)
    new_doc.close()

    if progress_callback:
        progress_callback(100, "Færdig!")

    return [output_path]
