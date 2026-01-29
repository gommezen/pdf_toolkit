"""
Application settings management using QSettings.
"""

from pathlib import Path
from PyQt6.QtCore import QSettings

from src.config.constants import DEFAULTS


class AppSettings:
    """Manages application configuration persistence."""

    def __init__(self):
        self._settings = QSettings("PDFToolkit", "PDFToolkit")

    @property
    def tesseract_path(self) -> str:
        """Path to Tesseract executable."""
        return self._settings.value("tesseract_path", "", str)

    @tesseract_path.setter
    def tesseract_path(self, value: str):
        self._settings.setValue("tesseract_path", value)

    @property
    def default_language(self) -> str:
        """Default OCR language."""
        return self._settings.value("default_language", DEFAULTS["ocr_language"], str)

    @default_language.setter
    def default_language(self, value: str):
        self._settings.setValue("default_language", value)

    @property
    def ocr_dpi(self) -> int:
        """OCR DPI setting."""
        return self._settings.value("ocr_dpi", DEFAULTS["ocr_dpi"], int)

    @ocr_dpi.setter
    def ocr_dpi(self, value: int):
        self._settings.setValue("ocr_dpi", value)

    @property
    def output_directory(self) -> Path | None:
        """Default output directory."""
        path = self._settings.value("output_directory", "", str)
        return Path(path) if path else None

    @output_directory.setter
    def output_directory(self, value: Path | None):
        self._settings.setValue("output_directory", str(value) if value else "")

    @property
    def compression_level(self) -> str:
        """Default compression level."""
        return self._settings.value("compression_level", DEFAULTS["compression_level"], str)

    @compression_level.setter
    def compression_level(self, value: str):
        self._settings.setValue("compression_level", value)

    @property
    def recent_files(self) -> list[str]:
        """List of recently used files."""
        return self._settings.value("recent_files", [], list)

    @recent_files.setter
    def recent_files(self, value: list[str]):
        self._settings.setValue("recent_files", value)

    def add_recent_file(self, file_path: str):
        """Add a file to recent files list."""
        recent = self.recent_files
        if file_path in recent:
            recent.remove(file_path)
        recent.insert(0, file_path)
        # Keep only last 10
        self.recent_files = recent[:10]

    def sync(self):
        """Force sync settings to storage."""
        self._settings.sync()
