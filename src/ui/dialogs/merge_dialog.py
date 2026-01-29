"""
Dialog for merging PDF files.
"""

from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton,
    QFileDialog, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from src.ui.widgets.progress import ProgressWidget
from src.core.merger import merge_pdfs, MergeOptions, MergeResult
from src.core.utils import format_file_size


class MergeWorker(QThread):
    """Background worker for merge operation."""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(object)  # MergeResult
    error = pyqtSignal(str)

    def __init__(self, files: list[str], output_path: str, options: MergeOptions):
        super().__init__()
        self.files = files
        self.output_path = output_path
        self.options = options
        self._cancelled = False

    def run(self):
        """Execute merge in background thread."""
        try:
            result = merge_pdfs(
                self.files,
                self.output_path,
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


class MergeDialog(QDialog):
    """Dialog for configuring and executing PDF merge."""

    def __init__(self, files: list[str], parent=None):
        super().__init__(parent)
        self.files = files.copy()
        self.output_path: str | None = None
        self.worker: MergeWorker | None = None

        self._setup_ui()
        self._populate_file_list()

    def _setup_ui(self):
        """Initialize dialog UI."""
        self.setWindowTitle("Merge - Kombiner PDF filer")
        self.setMinimumSize(500, 450)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # File list group
        files_group = QGroupBox("Filer at kombinere")
        files_layout = QVBoxLayout(files_group)

        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(150)
        self.file_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        files_layout.addWidget(self.file_list)

        # Reorder buttons
        order_layout = QHBoxLayout()
        self.btn_up = QPushButton("↑ Op")
        self.btn_up.clicked.connect(self._move_up)
        order_layout.addWidget(self.btn_up)

        self.btn_down = QPushButton("↓ Ned")
        self.btn_down.clicked.connect(self._move_down)
        order_layout.addWidget(self.btn_down)

        order_layout.addStretch()

        self.btn_remove = QPushButton("Fjern")
        self.btn_remove.clicked.connect(self._remove_selected)
        order_layout.addWidget(self.btn_remove)

        files_layout.addLayout(order_layout)
        layout.addWidget(files_group)

        # Output group
        output_group = QGroupBox("Output")
        output_layout = QHBoxLayout(output_group)

        self.output_label = QLabel("Ingen fil valgt")
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

        self.btn_merge = QPushButton("Merge")
        self.btn_merge.setProperty("class", "action-btn")
        self.btn_merge.clicked.connect(self._start_merge)
        btn_layout.addWidget(self.btn_merge)

        layout.addLayout(btn_layout)

    def _populate_file_list(self):
        """Fill the file list with initial files."""
        for file_path in self.files:
            path = Path(file_path)
            try:
                size = format_file_size(path.stat().st_size)
                text = f"{path.name}  ({size})"
            except OSError:
                text = path.name

            item = QListWidgetItem(f"📄 {text}")
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            self.file_list.addItem(item)

    def _move_up(self):
        """Move selected file up."""
        row = self.file_list.currentRow()
        if row > 0:
            item = self.file_list.takeItem(row)
            self.file_list.insertItem(row - 1, item)
            self.file_list.setCurrentRow(row - 1)
            self._update_files_from_list()

    def _move_down(self):
        """Move selected file down."""
        row = self.file_list.currentRow()
        if row < self.file_list.count() - 1:
            item = self.file_list.takeItem(row)
            self.file_list.insertItem(row + 1, item)
            self.file_list.setCurrentRow(row + 1)
            self._update_files_from_list()

    def _remove_selected(self):
        """Remove selected file from list."""
        row = self.file_list.currentRow()
        if row >= 0:
            self.file_list.takeItem(row)
            self._update_files_from_list()

    def _update_files_from_list(self):
        """Sync internal file list with widget."""
        self.files = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            self.files.append(item.data(Qt.ItemDataRole.UserRole))

    def _browse_output(self):
        """Open file dialog for output file."""
        # Suggest name based on first file
        suggested = "merged.pdf"
        if self.files:
            suggested = f"{Path(self.files[0]).stem}_merged.pdf"

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Gem som",
            suggested,
            "PDF filer (*.pdf)"
        )

        if path:
            self.output_path = path
            self.output_label.setText(Path(path).name)
            self.output_label.setStyleSheet("color: #1e293b;")

    def _start_merge(self):
        """Begin merge operation."""
        if len(self.files) < 2:
            QMessageBox.warning(
                self,
                "For få filer",
                "Tilføj mindst 2 filer for at merge."
            )
            return

        if not self.output_path:
            QMessageBox.warning(
                self,
                "Ingen output fil",
                "Vælg venligst en output fil."
            )
            return

        # Disable UI during operation
        self.btn_merge.setEnabled(False)
        self.btn_browse.setEnabled(False)
        self.progress.start("Starter merge...")

        # Create and start worker
        options = MergeOptions()
        self.worker = MergeWorker(self.files, self.output_path, options)
        self.worker.progress.connect(self.progress.set_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_finished(self, result: MergeResult):
        """Handle successful merge."""
        self.progress.finish(f"Færdig! {result.total_pages} sider kombineret")

        QMessageBox.information(
            self,
            "Merge fuldført",
            f"PDF filer er kombineret!\n\n"
            f"Output: {result.output_path.name}\n"
            f"Sider: {result.total_pages}\n"
            f"Filer: {result.source_files}"
        )
        self.accept()

    def _on_error(self, message: str):
        """Handle merge error."""
        self.progress.set_error(message)
        self.btn_merge.setEnabled(True)
        self.btn_browse.setEnabled(True)

        QMessageBox.critical(
            self,
            "Fejl under merge",
            f"Der opstod en fejl:\n\n{message}"
        )

    def _cancel(self):
        """Cancel ongoing operation."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()
            self.progress.reset()
            self.btn_merge.setEnabled(True)
            self.btn_browse.setEnabled(True)
