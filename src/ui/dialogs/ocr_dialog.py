"""
OCR dialog for text recognition processing.
"""

import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QGroupBox,
    QComboBox, QProgressBar, QTextEdit,
    QCheckBox, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from src.config.settings import AppSettings
from src.core.ocr_engine import (
    OCROptions, OCRLanguage, OCRResult,
    perform_ocr, extract_text_only,
    check_tesseract_available, get_available_languages
)


class OCRWorker(QThread):
    """Background worker for OCR processing."""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(object)  # OCRResult
    error = pyqtSignal(str)

    def __init__(
        self,
        input_path: str,
        output_path: str,
        options: OCROptions,
        tesseract_path: str,
        extract_only: bool = False
    ):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.options = options
        self.tesseract_path = tesseract_path
        self.extract_only = extract_only
        self._cancelled = False

    def run(self):
        """Execute OCR in background thread."""
        try:
            if self.extract_only:
                text, success, error = extract_text_only(
                    self.input_path,
                    self.options,
                    self.tesseract_path,
                    self._on_progress
                )
                result = OCRResult(
                    output_path=Path(self.output_path),
                    pages_processed=1,
                    text_extracted=text,
                    success=success,
                    error_message=error
                )
            else:
                result = perform_ocr(
                    self.input_path,
                    self.output_path,
                    self.options,
                    self.tesseract_path,
                    self._on_progress
                )

            if not self._cancelled:
                self.finished.emit(result)

        except Exception as e:
            if not self._cancelled:
                self.error.emit(str(e))

    def _on_progress(self, percent: int, message: str):
        """Progress callback."""
        if not self._cancelled:
            self.progress.emit(percent, message)

    def cancel(self):
        """Cancel the operation."""
        self._cancelled = True


class OCRDialog(QDialog):
    """Dialog for OCR text recognition."""

    def __init__(self, files: list[str], parent=None):
        super().__init__(parent)
        self.files = files
        self.settings = AppSettings()
        self.worker = None
        self._setup_ui()
        self._check_tesseract()

    def _setup_ui(self):
        """Initialize dialog UI."""
        self.setWindowTitle("OCR - Tekstgenkendelse")
        self.setMinimumSize(550, 500)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # File info
        file_info = QLabel(f"Fil: {Path(self.files[0]).name}")
        file_info.setStyleSheet("color: #D4A84B; font-size: 14px; font-weight: bold;")
        layout.addWidget(file_info)

        if len(self.files) > 1:
            more_label = QLabel(f"(+{len(self.files) - 1} flere filer)")
            more_label.setStyleSheet("color: #7FBFB5; font-size: 12px;")
            layout.addWidget(more_label)

        # Tesseract status
        self.status_frame = QFrame()
        self.status_frame.setStyleSheet("""
            QFrame {
                background-color: #1A3333;
                border: 1px solid #2D5A5A;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        status_layout = QHBoxLayout(self.status_frame)

        self.status_icon = QLabel("⚠")
        self.status_icon.setStyleSheet("font-size: 18px;")
        status_layout.addWidget(self.status_icon)

        self.status_label = QLabel("Kontrollerer Tesseract...")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label, 1)

        layout.addWidget(self.status_frame)

        # OCR Settings
        settings_group = QGroupBox("OCR Indstillinger")
        settings_layout = QVBoxLayout(settings_group)

        # Language
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Sprog:"))
        self.combo_language = QComboBox()
        self.combo_language.addItems(["Dansk", "Engelsk", "Dansk + Engelsk"])
        self._load_language_setting()
        lang_layout.addWidget(self.combo_language)
        lang_layout.addStretch()
        settings_layout.addLayout(lang_layout)

        # DPI
        dpi_layout = QHBoxLayout()
        dpi_layout.addWidget(QLabel("Opløsning:"))
        self.combo_dpi = QComboBox()
        self.combo_dpi.addItems([
            "150 DPI (hurtig)",
            "300 DPI (standard)",
            "600 DPI (høj kvalitet)"
        ])
        self._load_dpi_setting()
        dpi_layout.addWidget(self.combo_dpi)
        dpi_layout.addStretch()
        settings_layout.addLayout(dpi_layout)

        # Options
        self.check_preserve = QCheckBox("Bevar original udseende (tilføj usynligt tekstlag)")
        self.check_preserve.setChecked(True)
        settings_layout.addWidget(self.check_preserve)

        self.check_extract_only = QCheckBox("Kun udtræk tekst (gem ikke PDF)")
        self.check_extract_only.stateChanged.connect(self._on_extract_only_changed)
        settings_layout.addWidget(self.check_extract_only)

        layout.addWidget(settings_group)

        # Output settings
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)

        # Output directory
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Gem i:"))
        self.label_output_dir = QLabel(str(Path(self.files[0]).parent))
        self.label_output_dir.setStyleSheet("color: #7FBFB5;")
        self.label_output_dir.setWordWrap(True)
        dir_layout.addWidget(self.label_output_dir, 1)
        self.btn_browse = QPushButton("Vælg...")
        self.btn_browse.clicked.connect(self._browse_output)
        dir_layout.addWidget(self.btn_browse)
        output_layout.addLayout(dir_layout)

        layout.addWidget(output_group)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        self.progress_label.setStyleSheet("color: #7FBFB5;")
        layout.addWidget(self.progress_label)

        # Text preview (for extract only mode)
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        self.text_preview.setVisible(False)
        self.text_preview.setMinimumHeight(150)
        self.text_preview.setStyleSheet("""
            QTextEdit {
                background-color: #0D1A1A;
                border: 1px solid #2D5A5A;
                border-radius: 6px;
                color: #E8E4D9;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.text_preview)

        # Spacer
        layout.addStretch()

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Annuller")
        self.btn_cancel.clicked.connect(self._on_cancel)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_start = QPushButton("Start OCR")
        self.btn_start.setProperty("class", "action-btn")
        self.btn_start.clicked.connect(self._start_ocr)
        self.btn_start.setEnabled(False)
        btn_layout.addWidget(self.btn_start)

        layout.addLayout(btn_layout)

    def _check_tesseract(self):
        """Check if Tesseract is available."""
        tesseract_path = self.settings.tesseract_path
        available, message = check_tesseract_available(tesseract_path)

        if available:
            self.status_icon.setText("✓")
            self.status_icon.setStyleSheet("font-size: 18px; color: #22c55e;")
            self.status_label.setText(message)
            self.status_label.setStyleSheet("color: #22c55e;")
            self.btn_start.setEnabled(True)

            # Check for Danish language
            langs = get_available_languages(tesseract_path)
            if 'dan' not in langs:
                self.status_label.setText(
                    f"{message}\n⚠ Dansk sprogpakke ikke fundet. "
                    "Installer 'tesseract-ocr-dan' for dansk support."
                )
                self.status_label.setStyleSheet("color: #f59e0b;")
        else:
            self.status_icon.setText("✕")
            self.status_icon.setStyleSheet("font-size: 18px; color: #ef4444;")
            self.status_label.setText(message)
            self.status_label.setStyleSheet("color: #ef4444;")
            self.btn_start.setEnabled(False)

    def _load_language_setting(self):
        """Load saved language preference."""
        lang = self.settings.default_language
        if lang == "dan":
            self.combo_language.setCurrentIndex(0)
        elif lang == "eng":
            self.combo_language.setCurrentIndex(1)
        else:
            self.combo_language.setCurrentIndex(2)

    def _load_dpi_setting(self):
        """Load saved DPI preference."""
        dpi = self.settings.ocr_dpi
        if dpi <= 150:
            self.combo_dpi.setCurrentIndex(0)
        elif dpi <= 300:
            self.combo_dpi.setCurrentIndex(1)
        else:
            self.combo_dpi.setCurrentIndex(2)

    def _get_language(self) -> OCRLanguage:
        """Get selected language."""
        idx = self.combo_language.currentIndex()
        if idx == 0:
            return OCRLanguage.DANISH
        elif idx == 1:
            return OCRLanguage.ENGLISH
        else:
            return OCRLanguage.DANISH_ENGLISH

    def _get_dpi(self) -> int:
        """Get selected DPI."""
        idx = self.combo_dpi.currentIndex()
        if idx == 0:
            return 150
        elif idx == 1:
            return 300
        else:
            return 600

    def _browse_output(self):
        """Browse for output directory."""
        current = self.label_output_dir.text()
        path = QFileDialog.getExistingDirectory(self, "Vælg output mappe", current)
        if path:
            self.label_output_dir.setText(path)

    def _on_extract_only_changed(self, state):
        """Handle extract only checkbox change."""
        extract_only = state == Qt.CheckState.Checked.value
        self.check_preserve.setEnabled(not extract_only)
        self.btn_browse.setEnabled(not extract_only)

        if extract_only:
            self.text_preview.setVisible(True)
            self.text_preview.setPlaceholderText("Udtrukket tekst vises her...")
        else:
            self.text_preview.setVisible(False)

    def _start_ocr(self):
        """Start OCR processing."""
        # Build options
        options = OCROptions(
            language=self._get_language(),
            dpi=self._get_dpi(),
            preserve_original=self.check_preserve.isChecked()
        )

        input_path = self.files[0]
        extract_only = self.check_extract_only.isChecked()

        # Generate output path
        if not extract_only:
            output_dir = Path(self.label_output_dir.text())
            input_name = Path(input_path).stem
            output_path = str(output_dir / f"{input_name}_ocr.pdf")

            # Check if output exists
            if os.path.exists(output_path):
                reply = QMessageBox.question(
                    self,
                    "Fil eksisterer",
                    f"Filen '{Path(output_path).name}' eksisterer allerede.\n"
                    "Vil du overskrive den?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
        else:
            output_path = ""

        # Disable UI
        self.btn_start.setEnabled(False)
        self.combo_language.setEnabled(False)
        self.combo_dpi.setEnabled(False)
        self.check_preserve.setEnabled(False)
        self.check_extract_only.setEnabled(False)
        self.btn_browse.setEnabled(False)

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setVisible(True)
        self.progress_label.setText("Starter...")

        # Start worker
        self.worker = OCRWorker(
            input_path,
            output_path,
            options,
            self.settings.tesseract_path,
            extract_only
        )
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_progress(self, percent: int, message: str):
        """Update progress display."""
        self.progress_bar.setValue(percent)
        self.progress_label.setText(message)

    def _on_finished(self, result: OCRResult):
        """Handle OCR completion."""
        self.worker = None

        if result.success:
            if self.check_extract_only.isChecked():
                # Show extracted text
                self.text_preview.setText(result.text_extracted)
                self.progress_label.setText("Tekst udtrukket!")

                # Enable copy button behavior
                QMessageBox.information(
                    self,
                    "OCR Færdig",
                    f"Tekst udtrukket fra {result.pages_processed} side(r).\n"
                    "Teksten er vist nedenfor og kan kopieres."
                )
            else:
                QMessageBox.information(
                    self,
                    "OCR Færdig",
                    f"OCR gennemført!\n\n"
                    f"Sider behandlet: {result.pages_processed}\n"
                    f"Output: {result.output_path.name}"
                )
                self.accept()
        else:
            QMessageBox.warning(
                self,
                "OCR Fejl",
                f"OCR fejlede:\n{result.error_message}"
            )

        self._reset_ui()

    def _on_error(self, message: str):
        """Handle OCR error."""
        self.worker = None
        QMessageBox.critical(
            self,
            "Fejl",
            f"En fejl opstod under OCR:\n{message}"
        )
        self._reset_ui()

    def _reset_ui(self):
        """Reset UI after processing."""
        self.btn_start.setEnabled(True)
        self.combo_language.setEnabled(True)
        self.combo_dpi.setEnabled(True)
        self.check_preserve.setEnabled(not self.check_extract_only.isChecked())
        self.check_extract_only.setEnabled(True)
        self.btn_browse.setEnabled(not self.check_extract_only.isChecked())
        self.progress_bar.setVisible(False)

    def _on_cancel(self):
        """Handle cancel button."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait(1000)
            self.worker = None

        self.reject()

    def closeEvent(self, event):
        """Handle dialog close."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait(1000)
        event.accept()
