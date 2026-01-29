"""
Application settings dialog.
"""

from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QGroupBox,
    QComboBox, QLineEdit, QMessageBox
)

from src.config.settings import AppSettings


class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = AppSettings()
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Initialize dialog UI."""
        self.setWindowTitle("Indstillinger")
        self.setMinimumSize(450, 350)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # OCR Settings
        ocr_group = QGroupBox("OCR Indstillinger")
        ocr_layout = QVBoxLayout(ocr_group)

        # Tesseract path
        tess_layout = QHBoxLayout()
        tess_layout.addWidget(QLabel("Tesseract sti:"))
        self.edit_tesseract = QLineEdit()
        self.edit_tesseract.setPlaceholderText("Auto-detect")
        tess_layout.addWidget(self.edit_tesseract)
        self.btn_browse_tess = QPushButton("...")
        self.btn_browse_tess.setFixedWidth(40)
        self.btn_browse_tess.clicked.connect(self._browse_tesseract)
        tess_layout.addWidget(self.btn_browse_tess)
        ocr_layout.addLayout(tess_layout)

        # Default language
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Standard sprog:"))
        self.combo_language = QComboBox()
        self.combo_language.addItems(["Dansk", "Engelsk", "Dansk + Engelsk"])
        lang_layout.addWidget(self.combo_language)
        lang_layout.addStretch()
        ocr_layout.addLayout(lang_layout)

        # DPI
        dpi_layout = QHBoxLayout()
        dpi_layout.addWidget(QLabel("OCR opløsning:"))
        self.combo_dpi = QComboBox()
        self.combo_dpi.addItems(["150 DPI (hurtig)", "300 DPI (standard)", "600 DPI (høj kvalitet)"])
        self.combo_dpi.setCurrentIndex(1)
        dpi_layout.addWidget(self.combo_dpi)
        dpi_layout.addStretch()
        ocr_layout.addLayout(dpi_layout)

        layout.addWidget(ocr_group)

        # Output Settings
        output_group = QGroupBox("Output Indstillinger")
        output_layout = QVBoxLayout(output_group)

        # Default output directory
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Standard output mappe:"))
        self.edit_output_dir = QLineEdit()
        self.edit_output_dir.setPlaceholderText("Samme som input fil")
        dir_layout.addWidget(self.edit_output_dir)
        self.btn_browse_dir = QPushButton("...")
        self.btn_browse_dir.setFixedWidth(40)
        self.btn_browse_dir.clicked.connect(self._browse_output_dir)
        dir_layout.addWidget(self.btn_browse_dir)
        output_layout.addLayout(dir_layout)

        # Default compression level
        comp_layout = QHBoxLayout()
        comp_layout.addWidget(QLabel("Komprimerings niveau:"))
        self.combo_compression = QComboBox()
        self.combo_compression.addItems([
            "Høj kvalitet (lille reduktion)",
            "Balanceret (standard)",
            "Maksimal (stor reduktion)"
        ])
        self.combo_compression.setCurrentIndex(1)
        comp_layout.addWidget(self.combo_compression)
        comp_layout.addStretch()
        output_layout.addLayout(comp_layout)

        layout.addWidget(output_group)

        # Spacer
        layout.addStretch()

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Annuller")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_save = QPushButton("Gem")
        self.btn_save.setProperty("class", "action-btn")
        self.btn_save.clicked.connect(self._save_settings)
        btn_layout.addWidget(self.btn_save)

        layout.addLayout(btn_layout)

    def _browse_tesseract(self):
        """Browse for Tesseract executable."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Vælg Tesseract",
            "",
            "Executable (*.exe);;Alle filer (*.*)"
        )
        if path:
            self.edit_tesseract.setText(path)

    def _browse_output_dir(self):
        """Browse for default output directory."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Vælg output mappe"
        )
        if path:
            self.edit_output_dir.setText(path)

    def _load_settings(self):
        """Load current settings into UI."""
        # Tesseract path
        self.edit_tesseract.setText(self.settings.tesseract_path)

        # Language
        lang = self.settings.default_language
        if lang == "dan":
            self.combo_language.setCurrentIndex(0)
        elif lang == "eng":
            self.combo_language.setCurrentIndex(1)
        else:
            self.combo_language.setCurrentIndex(2)

        # DPI
        dpi = self.settings.ocr_dpi
        if dpi <= 150:
            self.combo_dpi.setCurrentIndex(0)
        elif dpi <= 300:
            self.combo_dpi.setCurrentIndex(1)
        else:
            self.combo_dpi.setCurrentIndex(2)

        # Output directory
        if self.settings.output_directory:
            self.edit_output_dir.setText(str(self.settings.output_directory))

        # Compression level
        level = self.settings.compression_level
        if level == "high":
            self.combo_compression.setCurrentIndex(0)
        elif level == "balanced":
            self.combo_compression.setCurrentIndex(1)
        else:
            self.combo_compression.setCurrentIndex(2)

    def _save_settings(self):
        """Save settings from UI."""
        # Tesseract path
        self.settings.tesseract_path = self.edit_tesseract.text().strip()

        # Language
        lang_index = self.combo_language.currentIndex()
        if lang_index == 0:
            self.settings.default_language = "dan"
        elif lang_index == 1:
            self.settings.default_language = "eng"
        else:
            self.settings.default_language = "dan+eng"

        # DPI
        dpi_index = self.combo_dpi.currentIndex()
        if dpi_index == 0:
            self.settings.ocr_dpi = 150
        elif dpi_index == 1:
            self.settings.ocr_dpi = 300
        else:
            self.settings.ocr_dpi = 600

        # Output directory
        output_dir = self.edit_output_dir.text().strip()
        if output_dir:
            self.settings.output_directory = Path(output_dir)
        else:
            self.settings.output_directory = None

        # Compression level
        comp_index = self.combo_compression.currentIndex()
        if comp_index == 0:
            self.settings.compression_level = "high"
        elif comp_index == 1:
            self.settings.compression_level = "balanced"
        else:
            self.settings.compression_level = "maximum"

        self.settings.sync()

        QMessageBox.information(
            self,
            "Indstillinger gemt",
            "Dine indstillinger er blevet gemt."
        )
        self.accept()
