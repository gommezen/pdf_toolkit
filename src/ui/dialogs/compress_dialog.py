"""
Compression dialog for reducing PDF file size.
"""

import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QGroupBox,
    QRadioButton, QProgressBar, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from src.core.compressor import (
    compress_pdf, get_pdf_size_info,
    CompressionLevel, CompressionResult
)


class CompressWorker(QThread):
    """Background worker for PDF compression."""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(object)  # CompressionResult
    error = pyqtSignal(str)

    def __init__(self, input_path: str, output_path: str, level: CompressionLevel):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.level = level
        self._cancelled = False

    def run(self):
        """Execute compression in background thread."""
        try:
            result = compress_pdf(
                self.input_path,
                self.output_path,
                self.level,
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


class CompressDialog(QDialog):
    """Dialog for PDF compression."""

    def __init__(self, files: list[str], parent=None):
        super().__init__(parent)
        self.files = files
        self.worker = None
        self._setup_ui()
        self._load_file_info()

    def _setup_ui(self):
        """Initialize dialog UI."""
        self.setWindowTitle("Komprimér PDF")
        self.setMinimumSize(500, 400)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # File info
        file_name = Path(self.files[0]).name
        file_label = QLabel(f"Fil: {file_name}")
        file_label.setStyleSheet("color: #D4A84B; font-size: 14px; font-weight: bold;")
        layout.addWidget(file_label)

        # File size info frame
        self.info_frame = QFrame()
        self.info_frame.setStyleSheet("""
            QFrame {
                background-color: #1A3333;
                border: 1px solid #2D5A5A;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        info_layout = QVBoxLayout(self.info_frame)

        self.size_label = QLabel("Indlæser fil info...")
        self.size_label.setStyleSheet("color: #E8E4D9;")
        info_layout.addWidget(self.size_label)

        self.details_label = QLabel("")
        self.details_label.setStyleSheet("color: #7FBFB5; font-size: 12px;")
        info_layout.addWidget(self.details_label)

        layout.addWidget(self.info_frame)

        # Compression level
        level_group = QGroupBox("Komprimeringsniveau")
        level_layout = QVBoxLayout(level_group)

        self.radio_high = QRadioButton("Høj kvalitet (lille reduktion)")
        self.radio_high.setToolTip("~10-20% reduktion. Minimal kvalitetstab.")
        level_layout.addWidget(self.radio_high)

        self.radio_balanced = QRadioButton("Balanceret (anbefalet)")
        self.radio_balanced.setToolTip("~40-60% reduktion. God balance mellem størrelse og kvalitet.")
        self.radio_balanced.setChecked(True)
        level_layout.addWidget(self.radio_balanced)

        self.radio_max = QRadioButton("Maksimal (stor reduktion)")
        self.radio_max.setToolTip("~70-90% reduktion. Kan påvirke billedkvalitet.")
        level_layout.addWidget(self.radio_max)

        layout.addWidget(level_group)

        # Output location
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)

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

        # Result info (shown after compression)
        self.result_label = QLabel("")
        self.result_label.setVisible(False)
        self.result_label.setStyleSheet("color: #22c55e; font-weight: bold;")
        layout.addWidget(self.result_label)

        # Spacer
        layout.addStretch()

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Annuller")
        self.btn_cancel.clicked.connect(self._on_cancel)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_start = QPushButton("Komprimér")
        self.btn_start.setProperty("class", "action-btn")
        self.btn_start.clicked.connect(self._start_compression)
        btn_layout.addWidget(self.btn_start)

        layout.addLayout(btn_layout)

    def _load_file_info(self):
        """Load and display file information."""
        info = get_pdf_size_info(self.files[0])

        size_mb = info["file_size"] / (1024 * 1024)
        self.size_label.setText(f"Størrelse: {size_mb:.2f} MB")

        details = f"{info['page_count']} sider · {info['image_count']} billeder"
        if info["has_embedded_fonts"]:
            details += " · Indlejrede skrifttyper"
        self.details_label.setText(details)

    def _get_compression_level(self) -> CompressionLevel:
        """Get selected compression level."""
        if self.radio_high.isChecked():
            return CompressionLevel.HIGH_QUALITY
        elif self.radio_max.isChecked():
            return CompressionLevel.MAXIMUM
        else:
            return CompressionLevel.BALANCED

    def _browse_output(self):
        """Browse for output directory."""
        current = self.label_output_dir.text()
        path = QFileDialog.getExistingDirectory(self, "Vælg output mappe", current)
        if path:
            self.label_output_dir.setText(path)

    def _start_compression(self):
        """Start PDF compression."""
        input_path = self.files[0]
        output_dir = Path(self.label_output_dir.text())
        input_name = Path(input_path).stem
        output_path = str(output_dir / f"{input_name}_compressed.pdf")

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

        # Disable UI
        self.btn_start.setEnabled(False)
        self.radio_high.setEnabled(False)
        self.radio_balanced.setEnabled(False)
        self.radio_max.setEnabled(False)
        self.btn_browse.setEnabled(False)

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setVisible(True)
        self.progress_label.setText("Starter...")
        self.result_label.setVisible(False)

        # Start worker
        level = self._get_compression_level()
        self.worker = CompressWorker(input_path, output_path, level)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_progress(self, percent: int, message: str):
        """Update progress display."""
        self.progress_bar.setValue(percent)
        self.progress_label.setText(message)

    def _on_finished(self, result: CompressionResult):
        """Handle compression completion."""
        self.worker = None

        if result.success:
            self.result_label.setText(
                f"✓ Komprimeret: {result.original_size_mb:.2f} MB → "
                f"{result.compressed_size_mb:.2f} MB "
                f"({result.reduction_percent:.1f}% reduktion)"
            )
            self.result_label.setVisible(True)

            QMessageBox.information(
                self,
                "Komprimering Færdig",
                f"PDF komprimeret!\n\n"
                f"Original: {result.original_size_mb:.2f} MB\n"
                f"Komprimeret: {result.compressed_size_mb:.2f} MB\n"
                f"Reduktion: {result.reduction_percent:.1f}%\n\n"
                f"Gemt som: {result.output_path.name}"
            )
        else:
            QMessageBox.warning(
                self,
                "Komprimering Fejl",
                f"Komprimering fejlede:\n{result.error_message}"
            )

        self._reset_ui()

    def _on_error(self, message: str):
        """Handle compression error."""
        self.worker = None
        QMessageBox.critical(
            self,
            "Fejl",
            f"En fejl opstod under komprimering:\n{message}"
        )
        self._reset_ui()

    def _reset_ui(self):
        """Reset UI after processing."""
        self.btn_start.setEnabled(True)
        self.radio_high.setEnabled(True)
        self.radio_balanced.setEnabled(True)
        self.radio_max.setEnabled(True)
        self.btn_browse.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)

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
