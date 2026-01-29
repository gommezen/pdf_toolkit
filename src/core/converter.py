"""
Document conversion functionality.
Converts DOCX files to PDF using Microsoft Word.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from docx2pdf import convert


@dataclass
class ConvertResult:
    """Result of a conversion operation."""
    output_path: Path
    input_path: Path
    success: bool
    error_message: str | None = None


def convert_docx_to_pdf(
    input_path: str | Path,
    output_path: str | Path | None = None,
    progress_callback: Callable[[int, str], None] | None = None
) -> ConvertResult:
    """
    Convert a DOCX file to PDF.

    Args:
        input_path: Path to input DOCX file
        output_path: Path for output PDF (auto-generated if None)
        progress_callback: Optional callback(percent, message)

    Returns:
        ConvertResult with operation details

    Note:
        Requires Microsoft Word to be installed on the system.
    """
    input_path = Path(input_path)

    if not input_path.exists():
        return ConvertResult(
            output_path=Path(""),
            input_path=input_path,
            success=False,
            error_message=f"Fil ikke fundet: {input_path}"
        )

    if not input_path.suffix.lower() in ('.docx', '.doc'):
        return ConvertResult(
            output_path=Path(""),
            input_path=input_path,
            success=False,
            error_message="Filen skal være en Word-fil (.docx eller .doc)"
        )

    # Auto-generate output path if not provided
    if output_path is None:
        output_path = input_path.with_suffix('.pdf')
    else:
        output_path = Path(output_path)

    if progress_callback:
        progress_callback(10, f"Konverterer {input_path.name}...")

    try:
        if progress_callback:
            progress_callback(30, "Åbner Microsoft Word...")

        # Convert using docx2pdf (uses Microsoft Word)
        convert(str(input_path), str(output_path))

        if progress_callback:
            progress_callback(100, "Færdig!")

        return ConvertResult(
            output_path=output_path,
            input_path=input_path,
            success=True
        )

    except Exception as e:
        error_msg = str(e)
        if "Word" in error_msg or "COM" in error_msg:
            error_msg = "Microsoft Word skal være installeret for at konvertere DOCX til PDF"

        return ConvertResult(
            output_path=output_path,
            input_path=input_path,
            success=False,
            error_message=error_msg
        )


def convert_multiple_docx(
    input_files: list[str | Path],
    output_dir: str | Path | None = None,
    progress_callback: Callable[[int, str], None] | None = None
) -> list[ConvertResult]:
    """
    Convert multiple DOCX files to PDF.

    Args:
        input_files: List of DOCX file paths
        output_dir: Output directory (uses input dir if None)
        progress_callback: Optional callback(percent, message)

    Returns:
        List of ConvertResult for each file
    """
    results = []
    total = len(input_files)

    for i, input_path in enumerate(input_files):
        input_path = Path(input_path)

        if progress_callback:
            percent = int((i / total) * 100)
            progress_callback(percent, f"Konverterer {input_path.name} ({i+1}/{total})...")

        if output_dir:
            output_path = Path(output_dir) / f"{input_path.stem}.pdf"
        else:
            output_path = None

        result = convert_docx_to_pdf(input_path, output_path)
        results.append(result)

    if progress_callback:
        progress_callback(100, f"Færdig! {sum(1 for r in results if r.success)}/{total} konverteret")

    return results
