"""
Remove pages dialog.
"""

import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QGroupBox,
    QLineEdit, QProgressBar, QListWidget,
    QListWidgetItem, QAbstractItemView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QIcon

from src.core.page_ops import remove_pages, get_page_thumbnails, PageOpResult
from src.core.pdf_handler import get_pdf_info


class RemoveWorker(QThread):
    """Background worker for page removal."""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, input_path: str, output_path: str, pages: list[int]):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.pages = pages

    def run(self):
        try:
            result = remove_pages(
                self.input_path,
                self.output_path,
                self.pages,
                self._on_progress
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

    def _on_progress(self, percent: int, message: str):
        self.progress.emit(percent, message)


class ThumbnailLoader(QThread):
    """Background worker for loading thumbnails."""

    thumbnail_ready = pyqtSignal(int, bytes)  # page_num, png_bytes
    finished = pyqtSignal()

    def __init__(self, pdf_path: str):
        super().__init__()
        self.pdf_path = pdf_path

    def run(self):
        thumbnails = get_page_thumbnails(self.pdf_path, max_size=100)
        for page_num, png_bytes in thumbnails:
            self.thumbnail_ready.emit(page_num, png_bytes)
        self.finished.emit()


class RemoveDialog(QDialog):
    """Dialog for removing PDF pages."""

    def __init__(self, files: list[str], parent=None):
        super().__init__(parent)
        self.files = files
        self.worker = None
        self.thumb_loader = None
        self.page_count = 0
        self._setup_ui()
        self._load_file_info()

    def _setup_ui(self):
        """Initialize dialog UI."""
        self.setWindowTitle("Fjern Sider")
        self.setMinimumSize(500, 500)
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

        # Instructions
        instructions = QLabel("Vælg sider der skal fjernes (klik for at markere/afmarkere):")
        instructions.setStyleSheet("color: #E8E4D9;")
        layout.addWidget(instructions)

        # Page list with thumbnails
        self.page_list = QListWidget()
        self.page_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.page_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.page_list.setIconSize(QSize(80, 100))
        self.page_list.setSpacing(10)
        self.page_list.setMinimumHeight(250)
        layout.addWidget(self.page_list)

        # Alternative: manual entry
        manual_group = QGroupBox("Eller angiv sider manuelt")
        manual_layout = QHBoxLayout(manual_group)
        manual_layout.addWidget(QLabel("Sider:"))
        self.edit_pages = QLineEdit()
        self.edit_pages.setPlaceholderText("f.eks. 1, 3, 5-7")
        manual_layout.addWidget(self.edit_pages)
        layout.addWidget(manual_group)

        # Selection info
        self.selection_label = QLabel("0 sider valgt til fjernelse")
        self.selection_label.setStyleSheet("color: #f59e0b;")
        layout.addWidget(self.selection_label)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)

        # Action buttons
        btn_layout = QHBoxLayout()

        self.btn_select_all = QPushButton("Vælg alle")
        self.btn_select_all.clicked.connect(self._select_all)
        btn_layout.addWidget(self.btn_select_all)

        self.btn_select_none = QPushButton("Fravælg alle")
        self.btn_select_none.clicked.connect(self._select_none)
        btn_layout.addWidget(self.btn_select_none)

        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Annuller")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_start = QPushButton("Fjern Sider")
        self.btn_start.setProperty("class", "action-btn")
        self.btn_start.clicked.connect(self._start_removal)
        btn_layout.addWidget(self.btn_start)

        layout.addLayout(btn_layout)

        # Connect selection change
        self.page_list.itemSelectionChanged.connect(self._update_selection_info)

    def _load_file_info(self):
        """Load file information and thumbnails."""
        try:
            info = get_pdf_info(self.files[0])
            self.page_count = info.page_count
            self.info_label.setText(f"{self.page_count} sider")

            # Add placeholder items
            for i in range(self.page_count):
                item = QListWidgetItem(f"Side {i + 1}")
                item.setData(Qt.ItemDataRole.UserRole, i + 1)
                self.page_list.addItem(item)

            # Load thumbnails in background
            self.thumb_loader = ThumbnailLoader(self.files[0])
            self.thumb_loader.thumbnail_ready.connect(
                self._on_thumbnail_ready,
                Qt.ConnectionType.QueuedConnection
            )
            self.thumb_loader.start()

        except Exception as e:
            self.info_label.setText(f"Fejl: {e}")

    def _on_thumbnail_ready(self, page_num: int, png_bytes: bytes):
        """Handle thumbnail loaded."""
        if page_num <= self.page_list.count():
            item = self.page_list.item(page_num - 1)
            # Disable updates while setting icon to avoid QPainter conflicts
            self.page_list.setUpdatesEnabled(False)
            try:
                pixmap = QPixmap()
                pixmap.loadFromData(png_bytes)
                item.setIcon(QIcon(pixmap))
            finally:
                self.page_list.setUpdatesEnabled(True)

    def _select_all(self):
        """Select all pages."""
        self.page_list.selectAll()

    def _select_none(self):
        """Deselect all pages."""
        self.page_list.clearSelection()

    def _update_selection_info(self):
        """Update selection count label."""
        count = len(self.page_list.selectedItems())
        self.selection_label.setText(f"{count} sider valgt til fjernelse")

        if count >= self.page_count:
            self.selection_label.setStyleSheet("color: #ef4444;")
            self.selection_label.setText(f"{count} sider valgt - Kan ikke fjerne alle sider!")
        elif count > 0:
            self.selection_label.setStyleSheet("color: #f59e0b;")
        else:
            self.selection_label.setStyleSheet("color: #7FBFB5;")

    def _get_pages_to_remove(self) -> list[int]:
        """Get list of pages to remove."""
        # Check manual entry first
        manual_text = self.edit_pages.text().strip()
        if manual_text:
            pages = []
            parts = manual_text.split(",")
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
            return pages

        # Otherwise use list selection
        pages = []
        for item in self.page_list.selectedItems():
            page_num = item.data(Qt.ItemDataRole.UserRole)
            pages.append(page_num)

        return sorted(pages)

    def _start_removal(self):
        """Start page removal."""
        pages = self._get_pages_to_remove()

        if not pages:
            QMessageBox.warning(self, "Ingen sider valgt", "Vælg mindst én side at fjerne.")
            return

        if len(pages) >= self.page_count:
            QMessageBox.warning(self, "For mange sider", "Du kan ikke fjerne alle sider fra PDF'en.")
            return

        # Confirm
        reply = QMessageBox.question(
            self,
            "Bekræft fjernelse",
            f"Er du sikker på at du vil fjerne {len(pages)} sider?\n\n"
            f"Sider: {', '.join(map(str, pages[:10]))}{'...' if len(pages) > 10 else ''}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        input_path = self.files[0]
        output_dir = Path(input_path).parent
        input_name = Path(input_path).stem
        output_path = str(output_dir / f"{input_name}_modified.pdf")

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

        self.worker = RemoveWorker(input_path, output_path, pages)
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
                f"Fjernede {result.pages_affected} sider.\n"
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

    def closeEvent(self, event):
        if self.thumb_loader and self.thumb_loader.isRunning():
            self.thumb_loader.quit()
            self.thumb_loader.wait(500)
        if self.worker and self.worker.isRunning():
            self.worker.wait(500)
        event.accept()
