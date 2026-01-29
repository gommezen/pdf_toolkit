"""
Utility functions for PDF operations.
"""

from pathlib import Path


def get_pdf_page_count(file_path: str | Path) -> int | None:
    """
    Get the number of pages in a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Number of pages, or None if not a PDF or error
    """
    file_path = Path(file_path)
    if file_path.suffix.lower() != '.pdf':
        return None

    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(file_path))
        count = len(doc)
        doc.close()
        return count
    except Exception:
        return None


def format_file_size(size_bytes: int) -> str:
    """
    Format bytes as human-readable string.

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted string (e.g., "2.4 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def get_output_path(
    input_path: Path,
    suffix: str = "_output",
    output_dir: Path | None = None,
    extension: str | None = None
) -> Path:
    """
    Generate output path based on input file name.

    Args:
        input_path: Original file path
        suffix: Suffix to add before extension
        output_dir: Output directory (uses input dir if None)
        extension: Override extension (uses input extension if None)

    Returns:
        Path object for output file
    """
    input_path = Path(input_path)
    output_dir = output_dir or input_path.parent
    ext = extension or input_path.suffix

    output_name = f"{input_path.stem}{suffix}{ext}"
    return output_dir / output_name


def ensure_unique_path(path: Path) -> Path:
    """
    Add number suffix if file already exists.

    Args:
        path: Desired file path

    Returns:
        Unique path (original if doesn't exist, or with number suffix)
    """
    if not path.exists():
        return path

    counter = 1
    while True:
        new_path = path.parent / f"{path.stem}_{counter}{path.suffix}"
        if not new_path.exists():
            return new_path
        counter += 1


def parse_page_ranges(ranges_str: str, total_pages: int) -> list[int]:
    """
    Parse a range string into list of page numbers.

    Args:
        ranges_str: Range string like "1-3, 5, 8-10"
        total_pages: Total number of pages in document

    Returns:
        Sorted list of unique page numbers (0-indexed)

    Example:
        >>> parse_page_ranges("1-3, 5, 8-10", 10)
        [0, 1, 2, 4, 7, 8, 9]
    """
    pages = set()

    for part in ranges_str.split(','):
        part = part.strip()
        if not part:
            continue

        if '-' in part:
            try:
                start, end = part.split('-', 1)
                start = int(start.strip())
                end = int(end.strip())
                # Convert to 0-indexed and clamp to valid range
                start = max(0, start - 1)
                end = min(total_pages - 1, end - 1)
                pages.update(range(start, end + 1))
            except ValueError:
                continue
        else:
            try:
                page = int(part) - 1  # Convert to 0-indexed
                if 0 <= page < total_pages:
                    pages.add(page)
            except ValueError:
                continue

    return sorted(pages)


def validate_file_extension(file_path: str | Path, allowed_extensions: tuple[str, ...]) -> bool:
    """
    Check if file has an allowed extension.

    Args:
        file_path: Path to check
        allowed_extensions: Tuple of allowed extensions (with dot)

    Returns:
        True if extension is allowed
    """
    return Path(file_path).suffix.lower() in allowed_extensions
