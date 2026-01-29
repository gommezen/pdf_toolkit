"""
File list widget for displaying and managing selected files.
Matches HTML prototype exactly with SVG icons and inline controls.
"""

from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.core.utils import format_file_size, get_pdf_page_count
from src.ui.icons import get_file_icon


class FileItemWidget(QWidget):
    """Custom widget for a file item with inline controls matching HTML."""

    move_up_clicked = pyqtSignal()
    move_down_clicked = pyqtSignal()
    remove_clicked = pyqtSignal()

    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(self)
        # HTML: padding: 14px 18px
        layout.setContentsMargins(18, 14, 18, 14)
        # HTML: margin-right: 14px on icon
        layout.setSpacing(14)

        # File icon - pre-rendered 28x28 pixmap (avoids QPainter conflicts)
        icon_widget = get_file_icon(28)
        layout.addWidget(icon_widget)

        # File info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        info_layout.setContentsMargins(0, 0, 0, 0)

        path = Path(self.file_path)

        # File name - Rajdhani (body font, no letter-spacing)
        # HTML: font-weight: 600, font-size: 0.95rem (15px), margin-bottom: 2px
        name_label = QLabel(path.name)
        name_label.setStyleSheet("""
            font-family: 'Rajdhani', 'Segoe UI', sans-serif;
            font-size: 15px;
            font-weight: 600;
            color: #E8E4D9;
            background: transparent;
            padding-bottom: 2px;
        """)
        info_layout.addWidget(name_label)

        # File meta - Rajdhani (body font)
        # HTML: font-size: 0.8rem (13px), color: mint
        try:
            size = format_file_size(path.stat().st_size)
            page_count = get_pdf_page_count(path)

            if page_count is not None:
                meta_text = f"{page_count} sider · {size}"
            else:
                meta_text = size

            meta_label = QLabel(meta_text)
            meta_label.setStyleSheet("""
                font-family: 'Rajdhani', 'Segoe UI', sans-serif;
                font-size: 13px;
                color: #7FBFB5;
                background: transparent;
            """)
            info_layout.addWidget(meta_label)
        except OSError:
            pass

        layout.addLayout(info_layout, 1)

        # Action buttons - 28x28 matching HTML
        btn_style = """
            QPushButton {
                background: transparent;
                color: #7FBFB5;
                border: 1px solid #2D5A5A;
                border-radius: 4px;
                font-family: 'Rajdhani', 'Segoe UI', sans-serif;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                border-color: #D4A84B;
                color: #D4A84B;
                background: rgba(212, 168, 75, 0.1);
            }
        """

        self.btn_up = QPushButton("↑")
        self.btn_up.setFixedSize(28, 28)
        self.btn_up.setStyleSheet(btn_style)
        self.btn_up.setToolTip("Flyt op")
        self.btn_up.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_up.clicked.connect(self.move_up_clicked.emit)
        layout.addWidget(self.btn_up)

        self.btn_down = QPushButton("↓")
        self.btn_down.setFixedSize(28, 28)
        self.btn_down.setStyleSheet(btn_style)
        self.btn_down.setToolTip("Flyt ned")
        self.btn_down.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_down.clicked.connect(self.move_down_clicked.emit)
        layout.addWidget(self.btn_down)

        self.btn_remove = QPushButton("✕")
        self.btn_remove.setFixedSize(28, 28)
        self.btn_remove.setStyleSheet(btn_style)
        self.btn_remove.setToolTip("Fjern")
        self.btn_remove.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_remove.clicked.connect(self.remove_clicked.emit)
        layout.addWidget(self.btn_remove)

    def enterEvent(self, event):
        """Hover effect on file item."""
        self.setStyleSheet("background: rgba(45, 90, 90, 0.3);")
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Remove hover effect."""
        self.setStyleSheet("background: transparent;")
        super().leaveEvent(event)


class FileListWidget(QWidget):
    """
    Widget for displaying and managing a list of selected files.
    Matches HTML prototype with SVG icons and inline controls.
    """

    files_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._files: list[str] = []
        self._setup_ui()

    def _create_section_header(self, text: str) -> QWidget:
        """Create a section header with decorative lines."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 10)
        layout.setSpacing(15)

        left_line = QFrame()
        left_line.setStyleSheet("""
            background: qlineargradient(x1:0, x2:1,
                stop:0 transparent,
                stop:1 #2D5A5A);
            max-height: 1px;
            min-height: 1px;
        """)
        left_line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(left_line)

        # Section title - Bebas Neue
        # HTML: font-size: 1.3rem (21px), letter-spacing: 0.25em (~5px)
        label = QLabel(text)
        label.setStyleSheet("""
            font-family: 'Bebas Neue', 'Impact', sans-serif;
            font-size: 21px;
            letter-spacing: 5px;
            color: #7FBFB5;
        """)
        layout.addWidget(label)

        right_line = QFrame()
        right_line.setStyleSheet("""
            background: qlineargradient(x1:0, x2:1,
                stop:0 #2D5A5A,
                stop:1 transparent);
            max-height: 1px;
            min-height: 1px;
        """)
        right_line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(right_line)

        return widget

    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Section header with decorative lines
        header = self._create_section_header("VALGTE FILER")
        layout.addWidget(header)

        # File list container with scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: rgba(13, 26, 26, 0.8);
                border: 1px solid #2D5A5A;
                border-radius: 6px;
            }
        """)

        self.list_widget = QWidget()
        self.list_widget.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(0)

        self.scroll_area.setWidget(self.list_widget)
        layout.addWidget(self.scroll_area, 1)

        # Initialize with empty state
        self._refresh_list()

    def _refresh_list(self):
        """Refresh the file list display."""
        # Clear existing items
        while self.list_layout.count() > 0:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._files:
            # Empty state
            empty_container = QWidget()
            empty_layout = QVBoxLayout(empty_container)
            empty_layout.setContentsMargins(20, 40, 20, 40)

            empty_label = QLabel("Ingen filer valgt")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("""
                font-family: 'Rajdhani', 'Segoe UI', sans-serif;
                color: #4A8080;
                font-size: 13px;
                background: transparent;
            """)
            empty_layout.addWidget(empty_label)
            self.list_layout.addWidget(empty_container)
        else:
            # Add file items
            for i, file_path in enumerate(self._files):
                # Separator between items
                if i > 0:
                    separator = QFrame()
                    separator.setFixedHeight(1)
                    separator.setStyleSheet("background: rgba(45, 90, 90, 0.4);")
                    self.list_layout.addWidget(separator)

                item_widget = FileItemWidget(file_path)
                item_widget.move_up_clicked.connect(lambda idx=i: self._move_up(idx))
                item_widget.move_down_clicked.connect(lambda idx=i: self._move_down(idx))
                item_widget.remove_clicked.connect(lambda idx=i: self._remove(idx))
                self.list_layout.addWidget(item_widget)

        self.list_layout.addStretch()

    def _move_up(self, index: int):
        if index > 0:
            self._files[index], self._files[index - 1] = self._files[index - 1], self._files[index]
            self._refresh_list()
            self.files_changed.emit()

    def _move_down(self, index: int):
        if index < len(self._files) - 1:
            self._files[index], self._files[index + 1] = self._files[index + 1], self._files[index]
            self._refresh_list()
            self.files_changed.emit()

    def _remove(self, index: int):
        if 0 <= index < len(self._files):
            self._files.pop(index)
            self._refresh_list()
            self.files_changed.emit()

    def add_files(self, files: list[str]):
        for file_path in files:
            if file_path not in self._files:
                self._files.append(file_path)
        self._refresh_list()
        self.files_changed.emit()

    def remove_selected(self):
        if self._files:
            self._files.pop()
            self._refresh_list()
            self.files_changed.emit()

    def move_up(self):
        if len(self._files) > 1:
            self._move_up(len(self._files) - 1)

    def move_down(self):
        if len(self._files) > 1:
            self._move_down(0)

    def clear(self):
        self._files.clear()
        self._refresh_list()
        self.files_changed.emit()

    def get_files(self) -> list[str]:
        return self._files.copy()

    def get_selected_file(self) -> str | None:
        return self._files[0] if self._files else None

    @property
    def file_count(self) -> int:
        return len(self._files)

    def has_files(self) -> bool:
        return len(self._files) > 0
