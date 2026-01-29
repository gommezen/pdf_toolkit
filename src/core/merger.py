"""
PDF merge functionality using PyMuPDF.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import fitz  # PyMuPDF


@dataclass
class MergeOptions:
    """Options for PDF merge operation."""
    preserve_bookmarks: bool = True
    preserve_metadata_from_first: bool = True


@dataclass
class MergeResult:
    """Result of a merge operation."""
    output_path: Path
    total_pages: int
    source_files: int


def merge_pdfs(
    input_files: list[str | Path],
    output_path: str | Path,
    options: MergeOptions | None = None,
    progress_callback: Callable[[int, str], None] | None = None
) -> MergeResult:
    """
    Merge multiple PDF files into one.

    Args:
        input_files: List of PDF file paths to merge
        output_path: Path for the merged output file
        options: Merge configuration options
        progress_callback: Optional callback(percent, message) for progress updates

    Returns:
        MergeResult with operation details

    Raises:
        FileNotFoundError: If any input file doesn't exist
        ValueError: If input list is empty or contains invalid PDFs
    """
    if not input_files:
        raise ValueError("No input files provided")

    options = options or MergeOptions()
    output_path = Path(output_path)
    input_files = [Path(f) for f in input_files]

    # Validate all input files exist
    for f in input_files:
        if not f.exists():
            raise FileNotFoundError(f"Input file not found: {f}")

    # Create output document
    output_doc = fitz.open()
    total_pages = 0
    file_count = len(input_files)

    for i, pdf_path in enumerate(input_files):
        if progress_callback:
            percent = int((i / file_count) * 100)
            progress_callback(percent, f"Behandler {pdf_path.name}...")

        try:
            src_doc = fitz.open(pdf_path)

            # Copy metadata from first file if requested
            if i == 0 and options.preserve_metadata_from_first:
                output_doc.set_metadata(src_doc.metadata)

            # Insert all pages from source
            output_doc.insert_pdf(src_doc)
            total_pages += len(src_doc)

            src_doc.close()

        except Exception as e:
            output_doc.close()
            raise ValueError(f"Error processing {pdf_path.name}: {e}")

    # Save merged document
    if progress_callback:
        progress_callback(95, "Gemmer fil...")

    output_doc.save(output_path)
    output_doc.close()

    if progress_callback:
        progress_callback(100, "Færdig!")

    return MergeResult(
        output_path=output_path,
        total_pages=total_pages,
        source_files=file_count
    )


def merge_page_ranges(
    input_files: list[tuple[str | Path, str]],
    output_path: str | Path,
    progress_callback: Callable[[int, str], None] | None = None
) -> MergeResult:
    """
    Merge specific page ranges from multiple PDFs.

    Args:
        input_files: List of tuples (file_path, page_range)
                    page_range format: "1-3, 5, 8-10" (1-indexed)
        output_path: Path for merged output
        progress_callback: Optional progress callback

    Returns:
        MergeResult with operation details
    """
    from src.core.utils import parse_page_ranges

    output_path = Path(output_path)
    output_doc = fitz.open()
    total_pages = 0
    file_count = len(input_files)

    for i, (pdf_path, page_range) in enumerate(input_files):
        pdf_path = Path(pdf_path)

        if progress_callback:
            percent = int((i / file_count) * 100)
            progress_callback(percent, f"Behandler {pdf_path.name}...")

        src_doc = fitz.open(pdf_path)
        pages = parse_page_ranges(page_range, len(src_doc))

        for page_num in pages:
            output_doc.insert_pdf(src_doc, from_page=page_num, to_page=page_num)
            total_pages += 1

        src_doc.close()

    if progress_callback:
        progress_callback(95, "Gemmer fil...")

    output_doc.save(output_path)
    output_doc.close()

    if progress_callback:
        progress_callback(100, "Færdig!")

    return MergeResult(
        output_path=output_path,
        total_pages=total_pages,
        source_files=file_count
    )
