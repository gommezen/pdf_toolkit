"""
Dialog for converting DOCX files to PDF.
"""

from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton,
    QFileDialog, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from src.ui.widgets.progress import ProgressWidget
from src.core.converter import convert_multiple_docx, ConvertResult
from src.core.utils import format_file_size


class ConvertWorker(QThread):
    """Background worker for conversion operation."""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list)  # List of ConvertResult
    error = pyqtSignal(str)

    def __init__(self, files: list[str], output_dir: str | None):
        super().__init__()
        self.files = files
        self.output_dir = output_dir
        self._cancelled = False

    def run(self):
        """Execute conversion in background thread."""
        try:
            results = convert_multiple_docx(
                self.files,
                self.output_dir,
                progress_callback=self._on_progress
            )
            if not self._cancelled:
                self.finished.emit(results)
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


class ConvertDialog(QDialog):
    """Dialog for converting DOCX files to PDF."""

    def __init__(self, files: list[str], parent=None):
        super().__init__(parent)
        # Filter to only DOCX files
        self.files = [f for f in files if f.lower().endswith(('.docx', '.doc'))]
        self.output_dir: str | None = None
        self.worker: ConvertWorker | None = None

        self._setup_ui()
        self._populate_file_list()

    def _setup_ui(self):
        """Initialize dialog UI."""
        self.setWindowTitle("Konverter - DOCX til PDF")
        self.setMinimumSize(500, 400)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Info label
        info_label = QLabel("Konverterer Word-dokumenter til PDF ved hjælp af Microsoft Word.")
        info_label.setStyleSheet("color: #7FBFB5; font-style: italic;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # File list group
        files_group = QGroupBox("FILER AT KONVERTERE")
        files_layout = QVBoxLayout(files_group)

        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(120)
        files_layout.addWidget(self.file_list)

        # Add/remove buttons
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("+ Tilføj")
        self.btn_add.setProperty("class", "secondary-btn")
        self.btn_add.clicked.connect(self._add_files)
        btn_layout.addWidget(self.btn_add)

        self.btn_remove = QPushButton("Fjern")
        self.btn_remove.setProperty("class", "secondary-btn")
        self.btn_remove.clicked.connect(self._remove_selected)
        btn_layout.addWidget(self.btn_remove)

        btn_layout.addStretch()
        files_layout.addLayout(btn_layout)

        layout.addWidget(files_group)

        # Output group
        output_group = QGroupBox("OUTPUT MAPPE")
        output_layout = QHBoxLayout(output_group)

        self.output_label = QLabel("Samme mappe som original")
        self.output_label.setStyleSheet("color: #7FBFB5;")
        output_layout.addWidget(self.output_label, 1)

        self.btn_browse = QPushButton("Vælg...")
        self.btn_browse.setProperty("class", "secondary-btn")
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
        self.btn_cancel.setProperty("class", "secondary-btn")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_convert = QPushButton("Konverter")
        self.btn_convert.setProperty("class", "action-btn")
        self.btn_convert.clicked.connect(self._start_convert)
        btn_layout.addWidget(self.btn_convert)

        layout.addLayout(btn_layout)

    def _populate_file_list(self):
        """Fill the file list with initial files."""
        for file_path in self.files:
            self._add_file_item(file_path)

        self._update_convert_button()

    def _add_file_item(self, file_path: str):
        """Add a file to the list widget."""
        path = Path(file_path)
        try:
            size = format_file_size(path.stat().st_size)
            text = f"{path.name}  ({size})"
        except OSError:
            text = path.name

        item = QListWidgetItem(f"📄 {text}")
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        self.file_list.addItem(item)

    def _add_files(self):
        """Open file dialog to add more files."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Vælg Word-filer",
            "",
            "Word dokumenter (*.docx *.doc)"
        )
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self._add_file_item(f)

        self._update_convert_button()

    def _remove_selected(self):
        """Remove selected file from list."""
        row = self.file_list.currentRow()
        if row >= 0:
            item = self.file_list.takeItem(row)
            file_path = item.data(Qt.ItemDataRole.UserRole)
            self.files.remove(file_path)

        self._update_convert_button()

    def _update_convert_button(self):
        """Enable/disable convert button based on file count."""
        self.btn_convert.setEnabled(len(self.files) > 0)

    def _browse_output(self):
        """Open directory dialog for output."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Vælg output mappe"
        )
        if path:
            self.output_dir = path
            self.output_label.setText(path)
            self.output_label.setStyleSheet("color: #E8E4D9;")

    def _start_convert(self):
        """Begin conversion operation."""
        if not self.files:
            QMessageBox.warning(
                self,
                "Ingen filer",
                "Tilføj mindst én Word-fil."
            )
            return

        # Disable UI during operation
        self.btn_convert.setEnabled(False)
        self.btn_browse.setEnabled(False)
        self.btn_add.setEnabled(False)
        self.progress.start("Starter konvertering...")

        # Create and start worker
        self.worker = ConvertWorker(self.files, self.output_dir)
        self.worker.progress.connect(self.progress.set_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_finished(self, results: list[ConvertResult]):
        """Handle successful conversion."""
        success_count = sum(1 for r in results if r.success)
        total = len(results)

        self.progress.finish(f"Færdig! {success_count}/{total} konverteret")

        # Build result message
        message = f"Konvertering fuldført!\n\n"
        message += f"Succesfulde: {success_count}\n"
        message += f"Fejlede: {total - success_count}\n\n"

        if success_count > 0:
            message += "Oprettede filer:\n"
            for r in results:
                if r.success:
                    message += f"  • {r.output_path.name}\n"

        if any(not r.success for r in results):
            message += "\nFejl:\n"
            for r in results:
                if not r.success:
                    message += f"  • {r.input_path.name}: {r.error_message}\n"

        QMessageBox.information(self, "Konvertering fuldført", message)
        self.accept()

    def _on_error(self, message: str):
        """Handle conversion error."""
        self.progress.set_error(message)
        self._reset_ui()

        QMessageBox.critical(
            self,
            "Fejl under konvertering",
            f"Der opstod en fejl:\n\n{message}"
        )

    def _reset_ui(self):
        """Reset UI after operation."""
        self.btn_convert.setEnabled(True)
        self.btn_browse.setEnabled(True)
        self.btn_add.setEnabled(True)

    def _cancel(self):
        """Cancel ongoing operation."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()
            self.progress.reset()
            self._reset_ui()
