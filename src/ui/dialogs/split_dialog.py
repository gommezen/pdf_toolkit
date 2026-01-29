"""
Dialog for splitting PDF files.
"""

from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QMessageBox, QGroupBox,
    QRadioButton, QButtonGroup, QSpinBox, QLineEdit
)
from PyQt6.QtCore import QThread, pyqtSignal

from src.ui.widgets.progress import ProgressWidget
from src.core.splitter import split_pdf, SplitMode, SplitOptions, SplitResult
from src.core.pdf_handler import get_pdf_info


class SplitWorker(QThread):
    """Background worker for split operation."""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(object)  # SplitResult
    error = pyqtSignal(str)

    def __init__(self, input_path: str, output_dir: str, options: SplitOptions):
        super().__init__()
        self.input_path = input_path
        self.output_dir = output_dir
        self.options = options
        self._cancelled = False

    def run(self):
        """Execute split in background thread."""
        try:
            result = split_pdf(
                self.input_path,
                self.output_dir,
                self.options,
                progress_callback=self._on_progress
            )
            if not self._cancelled:
                self.finished.emit(result)
        except Exception as e:
            if not self._cancelled:
                self.error.emit(str(e))

    def _on_progress(self, percent: int, message: str):
        """Forward progress to signal."""
        if not self._cancelled:
            self.progress.emit(percent, message)

    def cancel(self):
        """Request cancellation."""
        self._cancelled = True


class SplitDialog(QDialog):
    """Dialog for configuring and executing PDF split."""

    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.output_dir: str | None = None
        self.worker: SplitWorker | None = None

        # Get PDF info
        try:
            self.pdf_info = get_pdf_info(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Fejl", f"Kunne ikke læse PDF: {e}")
            self.reject()
            return

        self._setup_ui()

    def _setup_ui(self):
        """Initialize dialog UI."""
        self.setWindowTitle("Split - Opdel PDF")
        self.setMinimumSize(450, 500)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # File info
        info_group = QGroupBox("Fil information")
        info_layout = QVBoxLayout(info_group)

        file_name = Path(self.file_path).name
        info_layout.addWidget(QLabel(f"📄 {file_name}"))
        info_layout.addWidget(QLabel(f"Sider: {self.pdf_info.page_count}"))

        layout.addWidget(info_group)

        # Split mode selection
        mode_group = QGroupBox("Split metode")
        mode_layout = QVBoxLayout(mode_group)

        self.mode_group = QButtonGroup(self)

        # Single pages mode
        self.radio_single = QRadioButton("Én fil per side")
        self.radio_single.setChecked(True)
        self.mode_group.addButton(self.radio_single)
        mode_layout.addWidget(self.radio_single)

        # Equal parts mode
        parts_layout = QHBoxLayout()
        self.radio_equal = QRadioButton("Opdel i")
        self.mode_group.addButton(self.radio_equal)
        parts_layout.addWidget(self.radio_equal)

        self.spin_parts = QSpinBox()
        self.spin_parts.setMinimum(2)
        self.spin_parts.setMaximum(self.pdf_info.page_count)
        self.spin_parts.setValue(2)
        self.spin_parts.setEnabled(False)
        parts_layout.addWidget(self.spin_parts)

        parts_layout.addWidget(QLabel("lige store dele"))
        parts_layout.addStretch()
        mode_layout.addLayout(parts_layout)

        # Page ranges mode
        ranges_layout = QHBoxLayout()
        self.radio_ranges = QRadioButton("Sideintervaller:")
        self.mode_group.addButton(self.radio_ranges)
        ranges_layout.addWidget(self.radio_ranges)

        self.edit_ranges = QLineEdit()
        self.edit_ranges.setPlaceholderText("f.eks. 1-3; 4-6; 7-10")
        self.edit_ranges.setEnabled(False)
        ranges_layout.addWidget(self.edit_ranges)
        mode_layout.addLayout(ranges_layout)

        # Extract pages mode
        extract_layout = QHBoxLayout()
        self.radio_extract = QRadioButton("Udtræk sider:")
        self.mode_group.addButton(self.radio_extract)
        extract_layout.addWidget(self.radio_extract)

        self.edit_extract = QLineEdit()
        self.edit_extract.setPlaceholderText("f.eks. 1, 3, 5-7")
        self.edit_extract.setEnabled(False)
        extract_layout.addWidget(self.edit_extract)
        mode_layout.addLayout(extract_layout)

        layout.addWidget(mode_group)

        # Connect mode changes
        self.radio_single.toggled.connect(self._on_mode_changed)
        self.radio_equal.toggled.connect(self._on_mode_changed)
        self.radio_ranges.toggled.connect(self._on_mode_changed)
        self.radio_extract.toggled.connect(self._on_mode_changed)

        # Output directory
        output_group = QGroupBox("Output mappe")
        output_layout = QHBoxLayout(output_group)

        self.output_label = QLabel("Ingen mappe valgt")
        self.output_label.setStyleSheet("color: #64748b;")
        output_layout.addWidget(self.output_label, 1)

        self.btn_browse = QPushButton("Vælg...")
        self.btn_browse.clicked.connect(self._browse_output)
        output_layout.addWidget(self.btn_browse)

        layout.addWidget(output_group)

        # Progress
        self.progress = ProgressWidget()
        self.progress.cancelled.connect(self._cancel)
        layout.addWidget(self.progress)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Annuller")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_split = QPushButton("Split")
        self.btn_split.setProperty("class", "action-btn")
        self.btn_split.clicked.connect(self._start_split)
        btn_layout.addWidget(self.btn_split)

        layout.addLayout(btn_layout)

    def _on_mode_changed(self):
        """Update UI when split mode changes."""
        self.spin_parts.setEnabled(self.radio_equal.isChecked())
        self.edit_ranges.setEnabled(self.radio_ranges.isChecked())
        self.edit_extract.setEnabled(self.radio_extract.isChecked())

    def _browse_output(self):
        """Open directory dialog for output."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Vælg output mappe",
            str(Path(self.file_path).parent)
        )

        if path:
            self.output_dir = path
            self.output_label.setText(path)
            self.output_label.setStyleSheet("color: #1e293b;")

    def _get_split_options(self) -> SplitOptions | None:
        """Build split options from UI state."""
        if self.radio_single.isChecked():
            return SplitOptions(mode=SplitMode.SINGLE_PAGES)

        elif self.radio_equal.isChecked():
            return SplitOptions(
                mode=SplitMode.EQUAL_PARTS,
                parts=self.spin_parts.value()
            )

        elif self.radio_ranges.isChecked():
            ranges = self.edit_ranges.text().strip()
            if not ranges:
                QMessageBox.warning(self, "Manglende input", "Angiv sideintervaller.")
                return None
            return SplitOptions(
                mode=SplitMode.PAGE_RANGES,
                ranges=ranges
            )

        elif self.radio_extract.isChecked():
            pages_str = self.edit_extract.text().strip()
            if not pages_str:
                QMessageBox.warning(self, "Manglende input", "Angiv sider at udtrække.")
                return None
            # Parse pages string
            from src.core.utils import parse_page_ranges
            pages = parse_page_ranges(pages_str, self.pdf_info.page_count)
            if not pages:
                QMessageBox.warning(self, "Ugyldigt input", "Kunne ikke parse sidenumre.")
                return None
            return SplitOptions(
                mode=SplitMode.EXTRACT_PAGES,
                pages=pages
            )

        return None

    def _start_split(self):
        """Begin split operation."""
        if not self.output_dir:
            QMessageBox.warning(
                self,
                "Ingen output mappe",
                "Vælg venligst en output mappe."
            )
            return

        options = self._get_split_options()
        if not options:
            return

        # Disable UI during operation
        self.btn_split.setEnabled(False)
        self.btn_browse.setEnabled(False)
        self.progress.start("Starter split...")

        # Create and start worker
        self.worker = SplitWorker(self.file_path, self.output_dir, options)
        self.worker.progress.connect(self.progress.set_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_finished(self, result: SplitResult):
        """Handle successful split."""
        self.progress.finish(f"Færdig! {len(result.output_files)} filer oprettet")

        file_list = "\n".join([f.name for f in result.output_files[:5]])
        if len(result.output_files) > 5:
            file_list += f"\n... og {len(result.output_files) - 5} flere"

        QMessageBox.information(
            self,
            "Split fuldført",
            f"PDF er opdelt!\n\n"
            f"Oprettede filer:\n{file_list}"
        )
        self.accept()

    def _on_error(self, message: str):
        """Handle split error."""
        self.progress.set_error(message)
        self.btn_split.setEnabled(True)
        self.btn_browse.setEnabled(True)

        QMessageBox.critical(
            self,
            "Fejl under split",
            f"Der opstod en fejl:\n\n{message}"
        )

    def _cancel(self):
        """Cancel ongoing operation."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()
            self.progress.reset()
            self.btn_split.setEnabled(True)
            self.btn_browse.setEnabled(True)
