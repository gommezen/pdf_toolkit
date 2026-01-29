"""
PDF compression engine.
Reduces PDF file size using various optimization techniques.
"""

from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import Callable

import fitz  # PyMuPDF
from PIL import Image


class CompressionLevel(Enum):
    """Available compression levels."""
    HIGH_QUALITY = "high"      # ~10-20% reduction, minimal quality loss
    BALANCED = "balanced"      # ~40-60% reduction, good balance
    MAXIMUM = "maximum"        # ~70-90% reduction, aggressive


@dataclass
class CompressionResult:
    """Result of a compression operation."""
    output_path: Path
    original_size: int
    compressed_size: int
    success: bool
    error_message: str = ""

    @property
    def reduction_percent(self) -> float:
        """Compression ratio as percentage reduction."""
        if self.original_size == 0:
            return 0.0
        return (1 - self.compressed_size / self.original_size) * 100

    @property
    def original_size_mb(self) -> float:
        """Original size in MB."""
        return self.original_size / (1024 * 1024)

    @property
    def compressed_size_mb(self) -> float:
        """Compressed size in MB."""
        return self.compressed_size / (1024 * 1024)


def compress_pdf(
    input_path: str,
    output_path: str,
    level: CompressionLevel = CompressionLevel.BALANCED,
    progress_callback: Callable[[int, str], None] | None = None
) -> CompressionResult:
    """
    Compress a PDF file to reduce its size.

    Args:
        input_path: Path to input PDF file
        output_path: Path for compressed output
        level: Desired compression level
        progress_callback: Optional callback(percent, message)

    Returns:
        CompressionResult with size information
    """
    try:
        original_size = Path(input_path).stat().st_size

        if progress_callback:
            progress_callback(10, "Åbner PDF...")

        doc = fitz.open(input_path)

        if progress_callback:
            progress_callback(20, "Analyserer indhold...")

        # Get compression settings based on level
        settings = _get_compression_settings(level)

        total_pages = doc.page_count
        images_compressed = 0

        # Process each page
        for page_num in range(total_pages):
            if progress_callback:
                percent = 20 + int((page_num / total_pages) * 60)
                progress_callback(percent, f"Komprimerer side {page_num + 1}/{total_pages}...")

            page = doc[page_num]

            # Compress images on this page
            compressed = _compress_page_images(doc, page, settings)
            images_compressed += compressed

        if progress_callback:
            progress_callback(85, f"Komprimerede {images_compressed} billeder...")

        if progress_callback:
            progress_callback(90, "Gemmer komprimeret fil...")

        # Save with compression options
        doc.save(
            output_path,
            garbage=4,           # Maximum garbage collection (remove unused objects)
            deflate=True,        # Use deflate compression for streams
            deflate_images=True, # Compress images with deflate
            deflate_fonts=True,  # Compress fonts with deflate
            clean=True,          # Clean and sanitize content streams
        )
        doc.close()

        compressed_size = Path(output_path).stat().st_size

        # If compression made file larger, use original instead
        if compressed_size >= original_size:
            import shutil
            Path(output_path).unlink()  # Remove larger file
            shutil.copy2(input_path, output_path)
            compressed_size = original_size  # Same size as original

            if progress_callback:
                progress_callback(100, "Filen er allerede optimeret")
        else:
            if progress_callback:
                progress_callback(100, "Færdig!")

        return CompressionResult(
            output_path=Path(output_path),
            original_size=original_size,
            compressed_size=compressed_size,
            success=True
        )

    except Exception as e:
        return CompressionResult(
            output_path=Path(output_path),
            original_size=original_size if 'original_size' in locals() else 0,
            compressed_size=0,
            success=False,
            error_message=str(e)
        )


def _get_compression_settings(level: CompressionLevel) -> dict:
    """Get compression settings for the specified level."""
    if level == CompressionLevel.HIGH_QUALITY:
        return {
            "image_quality": 85,      # JPEG quality (0-100)
            "max_dimension": 2400,    # Max width/height in pixels
            "min_size_kb": 50,        # Don't compress images smaller than this
            "scale_factor": 1.0,      # No scaling
        }
    elif level == CompressionLevel.BALANCED:
        return {
            "image_quality": 65,
            "max_dimension": 1600,
            "min_size_kb": 20,
            "scale_factor": 0.85,     # Scale down to 85%
        }
    else:  # MAXIMUM
        return {
            "image_quality": 40,
            "max_dimension": 1200,
            "min_size_kb": 10,
            "scale_factor": 0.7,      # Scale down to 70%
        }


def _compress_page_images(doc: fitz.Document, page: fitz.Page, settings: dict) -> int:
    """
    Compress images on a page by recompressing with lower quality.

    Returns number of images compressed.
    """
    image_list = page.get_images(full=True)
    compressed_count = 0

    for img_info in image_list:
        xref = img_info[0]

        try:
            # Extract the image
            base_image = doc.extract_image(xref)
            if not base_image:
                continue

            image_bytes = base_image["image"]
            original_size = len(image_bytes)

            # Skip small images (already compressed or icons)
            if original_size < settings["min_size_kb"] * 1024:
                continue

            # Load image with PIL
            pil_image = Image.open(BytesIO(image_bytes))

            # Convert RGBA to RGB (JPEG doesn't support alpha)
            if pil_image.mode in ('RGBA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', pil_image.size, (255, 255, 255))
                if pil_image.mode == 'P':
                    pil_image = pil_image.convert('RGBA')
                background.paste(pil_image, mask=pil_image.split()[-1] if pil_image.mode == 'RGBA' else None)
                pil_image = background
            elif pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')

            # Get original dimensions
            orig_width, orig_height = pil_image.size

            # Calculate new dimensions
            scale = settings["scale_factor"]
            max_dim = settings["max_dimension"]

            new_width = int(orig_width * scale)
            new_height = int(orig_height * scale)

            # Limit to max dimension while preserving aspect ratio
            if new_width > max_dim or new_height > max_dim:
                ratio = min(max_dim / new_width, max_dim / new_height)
                new_width = int(new_width * ratio)
                new_height = int(new_height * ratio)

            # Only resize if dimensions changed significantly
            if new_width < orig_width * 0.95 or new_height < orig_height * 0.95:
                pil_image = pil_image.resize(
                    (new_width, new_height),
                    Image.Resampling.LANCZOS
                )

            # Compress to JPEG
            output_buffer = BytesIO()
            pil_image.save(
                output_buffer,
                format='JPEG',
                quality=settings["image_quality"],
                optimize=True
            )
            compressed_bytes = output_buffer.getvalue()

            # Only replace if we actually reduced size
            if len(compressed_bytes) < original_size * 0.95:
                # Replace the image in the PDF
                doc.update_stream(xref, compressed_bytes)

                # Update the image's metadata to indicate JPEG
                # This tells the PDF reader how to decode the image
                img_dict = doc.xref_get_key(xref, "")
                doc.xref_set_key(xref, "Filter", "/DCTDecode")
                doc.xref_set_key(xref, "ColorSpace", "/DeviceRGB")
                doc.xref_set_key(xref, "BitsPerComponent", "8")
                doc.xref_set_key(xref, "Width", str(new_width if new_width != orig_width else orig_width))
                doc.xref_set_key(xref, "Height", str(new_height if new_height != orig_height else orig_height))

                compressed_count += 1

        except Exception:
            # Skip images that can't be processed (e.g., unsupported format)
            continue

    return compressed_count


def get_pdf_size_info(pdf_path: str) -> dict:
    """
    Get size information about a PDF file.

    Returns dict with:
        - file_size: Total file size in bytes
        - page_count: Number of pages
        - image_count: Number of images
        - has_embedded_fonts: Whether PDF has embedded fonts
    """
    try:
        doc = fitz.open(pdf_path)

        image_count = 0
        total_image_size = 0
        for page in doc:
            images = page.get_images(full=True)
            image_count += len(images)
            # Estimate image sizes
            for img_info in images:
                try:
                    xref = img_info[0]
                    img_data = doc.extract_image(xref)
                    if img_data:
                        total_image_size += len(img_data["image"])
                except Exception:
                    pass

        # Check for embedded fonts
        has_fonts = False
        for page in doc:
            fonts = page.get_fonts()
            if fonts:
                has_fonts = True
                break

        info = {
            "file_size": Path(pdf_path).stat().st_size,
            "page_count": doc.page_count,
            "image_count": image_count,
            "total_image_size": total_image_size,
            "has_embedded_fonts": has_fonts,
        }

        doc.close()
        return info

    except Exception as e:
        return {
            "file_size": 0,
            "page_count": 0,
            "image_count": 0,
            "total_image_size": 0,
            "has_embedded_fonts": False,
            "error": str(e)
        }
