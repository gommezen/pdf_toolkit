"""
Rotate pages dialog.
"""

import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QGroupBox,
    QRadioButton, QProgressBar, QMessageBox,
    QLineEdit, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from src.core.page_ops import rotate_pages, RotationAngle, PageOpResult
from src.core.pdf_handler import get_pdf_info


class RotateWorker(QThread):
    """Background worker for rotation."""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, input_path: str, output_path: str, angle: RotationAngle, pages: list[int] | None):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.angle = angle
        self.pages = pages

    def run(self):
        try:
            result = rotate_pages(
                self.input_path,
                self.output_path,
                self.angle,
                self.pages,
                self._on_progress
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

    def _on_progress(self, percent: int, message: str):
        self.progress.emit(percent, message)


class RotateDialog(QDialog):
    """Dialog for rotating PDF pages."""

    def __init__(self, files: list[str], parent=None):
        super().__init__(parent)
        self.files = files
        self.worker = None
        self.page_count = 0
        self._setup_ui()
        self._load_file_info()

    def _setup_ui(self):
        """Initialize dialog UI."""
        self.setWindowTitle("Rotér Sider")
        self.setMinimumSize(450, 380)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # File info
        file_name = Path(self.files[0]).name
        file_label = QLabel(f"Fil: {file_name}")
        file_label.setStyleSheet("color: #D4A84B; font-size: 14px; font-weight: bold;")
        layout.addWidget(file_label)

        self.info_label = QLabel("Indlæser...")
        self.info_label.setStyleSheet("color: #7FBFB5;")
        layout.addWidget(self.info_label)

        # Rotation angle
        angle_group = QGroupBox("Rotationsvinkel")
        angle_layout = QVBoxLayout(angle_group)

        self.radio_90cw = QRadioButton("90° med uret →")
        self.radio_90cw.setChecked(True)
        angle_layout.addWidget(self.radio_90cw)

        self.radio_180 = QRadioButton("180°")
        angle_layout.addWidget(self.radio_180)

        self.radio_90ccw = QRadioButton("90° mod uret ←")
        angle_layout.addWidget(self.radio_90ccw)

        layout.addWidget(angle_group)

        # Page selection
        pages_group = QGroupBox("Sider")
        pages_layout = QVBoxLayout(pages_group)

        self.check_all_pages = QCheckBox("Alle sider")
        self.check_all_pages.setChecked(True)
        self.check_all_pages.stateChanged.connect(self._on_all_pages_changed)
        pages_layout.addWidget(self.check_all_pages)

        specific_layout = QHBoxLayout()
        specific_layout.addWidget(QLabel("Specifikke sider:"))
        self.edit_pages = QLineEdit()
        self.edit_pages.setPlaceholderText("f.eks. 1, 3, 5-7")
        self.edit_pages.setEnabled(False)
        specific_layout.addWidget(self.edit_pages)
        pages_layout.addLayout(specific_layout)

        layout.addWidget(pages_group)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        self.progress_label.setStyleSheet("color: #7FBFB5;")
        layout.addWidget(self.progress_label)

        # Spacer
        layout.addStretch()

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Annuller")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_start = QPushButton("Rotér")
        self.btn_start.setProperty("class", "action-btn")
        self.btn_start.clicked.connect(self._start_rotation)
        btn_layout.addWidget(self.btn_start)

        layout.addLayout(btn_layout)

    def _load_file_info(self):
        """Load file information."""
        try:
            info = get_pdf_info(self.files[0])
            self.page_count = info.page_count
            self.info_label.setText(f"{self.page_count} sider")
        except Exception:
            self.info_label.setText("Kunne ikke læse fil info")

    def _on_all_pages_changed(self, state):
        """Handle all pages checkbox change."""
        self.edit_pages.setEnabled(state != Qt.CheckState.Checked.value)

    def _get_angle(self) -> RotationAngle:
        """Get selected rotation angle."""
        if self.radio_90cw.isChecked():
            return RotationAngle.CW_90
        elif self.radio_180.isChecked():
            return RotationAngle.CW_180
        else:
            return RotationAngle.CCW_90

    def _parse_pages(self) -> list[int] | None:
        """Parse page selection. Returns None for all pages."""
        if self.check_all_pages.isChecked():
            return None

        text = self.edit_pages.text().strip()
        if not text:
            return None

        pages = []
        parts = text.split(",")

        for part in parts:
            part = part.strip()
            if "-" in part:
                try:
                    start, end = part.split("-")
                    pages.extend(range(int(start), int(end) + 1))
                except ValueError:
                    continue
            else:
                try:
                    pages.append(int(part))
                except ValueError:
                    continue

        return pages if pages else None

    def _start_rotation(self):
        """Start rotation operation."""
        input_path = self.files[0]
        output_dir = Path(input_path).parent
        input_name = Path(input_path).stem
        output_path = str(output_dir / f"{input_name}_rotated.pdf")

        if os.path.exists(output_path):
            reply = QMessageBox.question(
                self, "Fil eksisterer",
                f"Filen eksisterer allerede. Overskriv?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self.btn_start.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setVisible(True)

        angle = self._get_angle()
        pages = self._parse_pages()

        self.worker = RotateWorker(input_path, output_path, angle, pages)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_progress(self, percent: int, message: str):
        self.progress_bar.setValue(percent)
        self.progress_label.setText(message)

    def _on_finished(self, result: PageOpResult):
        self.worker = None
        if result.success:
            QMessageBox.information(
                self, "Færdig",
                f"Roterede {result.pages_affected} sider.\n"
                f"Gemt som: {result.output_path.name}"
            )
            self.accept()
        else:
            QMessageBox.warning(self, "Fejl", result.error_message)
            self._reset_ui()

    def _on_error(self, message: str):
        self.worker = None
        QMessageBox.critical(self, "Fejl", message)
        self._reset_ui()

    def _reset_ui(self):
        self.btn_start.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
