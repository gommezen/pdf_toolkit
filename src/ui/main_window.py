"""
Main application window with responsive design.
Matches pdf-toolkit-unified.html reference.
"""

import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QFileDialog, QMessageBox, QStatusBar,
    QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QShortcut, QKeySequence, QPixmap, QResizeEvent, QColor, QPainter, QLinearGradient, QPen
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

from src.ui.widgets.drop_zone import DropZone
from src.ui.widgets.file_list import FileListWidget
from src.ui.widgets.tool_tile import ToolTile
from src.ui.dialogs.merge_dialog import MergeDialog
from src.ui.dialogs.split_dialog import SplitDialog
from src.ui.dialogs.convert_dialog import ConvertDialog
from src.ui.dialogs.settings_dialog import SettingsDialog
from src.ui.dialogs.ocr_dialog import OCRDialog
from src.config.constants import TOOLS, SUPPORTED_EXTENSIONS


class ArtDecoLines(QWidget):
    """
    Decorative vertical lines overlay matching HTML .art-deco-lines.
    4 vertical gradient lines at 5%, 12%, 88%, 95% positions.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter()
        if not painter.begin(self):
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        h = self.height()
        w = self.width()

        # Vertical line positions (percentage from left)
        positions = [0.05, 0.12, 0.88, 0.95]

        for pos in positions:
            x = int(w * pos)

            # Create vertical gradient: transparent -> teal -> mint -> teal -> transparent
            gradient = QLinearGradient(x, 0, x, h)
            gradient.setColorAt(0.0, QColor(45, 90, 90, 0))      # transparent
            gradient.setColorAt(0.3, QColor(45, 90, 90, 51))     # teal with 0.2 opacity
            gradient.setColorAt(0.5, QColor(127, 191, 181, 51))  # mint with 0.2 opacity
            gradient.setColorAt(0.7, QColor(45, 90, 90, 51))     # teal with 0.2 opacity
            gradient.setColorAt(1.0, QColor(45, 90, 90, 0))      # transparent

            pen = QPen()
            pen.setWidth(1)
            pen.setBrush(gradient)
            painter.setPen(pen)
            painter.drawLine(x, 0, x, h)

        painter.end()


def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and PyInstaller."""
    base_path = Path(__file__).parent.parent
    return str(base_path / relative_path)


class ResponsiveToolGrid(QWidget):
    """A responsive grid that adjusts columns based on available width."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tiles = []
        self._layout = QGridLayout(self)
        self._layout.setSpacing(12)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._current_cols = 4
        # Make columns stretch equally
        for i in range(4):
            self._layout.setColumnStretch(i, 1)

    def add_tile(self, tile: ToolTile):
        """Add a tile to the grid."""
        self._tiles.append(tile)
        self._relayout()

    def _relayout(self):
        """Relayout tiles based on current column count."""
        # Remove all widgets
        for i in reversed(range(self._layout.count())):
            item = self._layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        # Reset column stretches
        for i in range(8):
            self._layout.setColumnStretch(i, 0)
        for i in range(self._current_cols):
            self._layout.setColumnStretch(i, 1)

        # Add tiles - no alignment flag so they expand to fill column
        for i, tile in enumerate(self._tiles):
            row, col = divmod(i, self._current_cols)
            self._layout.addWidget(tile, row, col)
            tile.setParent(self)

    def update_columns(self, width: int):
        """Update column count based on available width."""
        # Smaller threshold for mobile-friendly layout
        if width < 400:
            new_cols = 2
        elif width < 600:
            new_cols = 3
        else:
            new_cols = 4

        if new_cols != self._current_cols:
            self._current_cols = new_cols
            self._relayout()


class MainWindow(QMainWindow):
    """
    Main application window matching HTML reference design.
    Metropolis Art Deco theme with responsive layout.
    """

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._setup_shortcuts()

    def _setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("PDF Toolkit - Metropolis Edition")
        self.setMinimumSize(420, 550)
        self.resize(900, 800)

        # Container for scroll area + decorative overlay
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self.setCentralWidget(container)

        # Use a stacked layout approach - scroll area is the base
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Main scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        container_layout.addWidget(scroll_area)

        # Decorative vertical lines overlay (fixed position)
        self._deco_lines = ArtDecoLines(container)
        self._deco_lines.setGeometry(0, 0, self.width(), self.height())
        self._deco_lines.raise_()  # Keep on top but transparent to mouse

        # Content widget
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        scroll_area.setWidget(content_widget)

        layout = QVBoxLayout(content_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(30, 25, 30, 30)

        # ===== HEADER =====
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setSpacing(5)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo - 120x120 with gold border and glow
        self.logo_label = QLabel()
        logo_path = get_resource_path("resources/icons/logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(
                114, 114,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.logo_label.setPixmap(scaled_pixmap)
        self.logo_label.setStyleSheet("""
            border: 3px solid #D4A84B;
            border-radius: 60px;
            padding: 0px;
            background: transparent;
        """)
        self.logo_label.setFixedSize(120, 120)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add glow effect to logo
        logo_glow = QGraphicsDropShadowEffect()
        logo_glow.setBlurRadius(30)
        logo_glow.setOffset(0, 0)
        logo_glow.setColor(QColor(212, 168, 75, 100))
        self.logo_label.setGraphicsEffect(logo_glow)

        header_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        header_layout.addSpacing(10)

        # Title - Large gold text with glow
        self.title_label = QLabel("PDF TOOLKIT")
        self.title_label.setObjectName("title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add glow effect to title
        title_glow = QGraphicsDropShadowEffect()
        title_glow.setBlurRadius(20)
        title_glow.setOffset(0, 2)
        title_glow.setColor(QColor(212, 168, 75, 120))
        self.title_label.setGraphicsEffect(title_glow)

        header_layout.addWidget(self.title_label)

        # Subtitle
        self.subtitle_label = QLabel("DOKUMENTBEHANDLING · ANNO 2025")
        self.subtitle_label.setObjectName("subtitle")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.subtitle_label)

        # Decorative line
        deco_line = QFrame()
        deco_line.setObjectName("deco-line")
        deco_line.setFixedWidth(350)
        deco_line.setFixedHeight(2)
        header_layout.addWidget(deco_line, alignment=Qt.AlignmentFlag.AlignCenter)

        header_layout.addSpacing(2)

        # Diamond ornament
        ornament = self._create_ornament()
        header_layout.addWidget(ornament, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(header_widget)
        # HTML: header margin-bottom: 40px
        layout.addSpacing(40)

        # ===== SECTION: VÆRKTØJER =====
        section_header = self._create_section_header("VÆRKTØJER")
        layout.addWidget(section_header)
        # HTML: section-title margin-bottom: 20px
        layout.addSpacing(20)

        # Tool grid
        self.tools_grid = ResponsiveToolGrid()
        for tool in TOOLS:
            tile = ToolTile(tool)
            tile.tool_clicked.connect(self._on_tool_clicked)
            self.tools_grid.add_tile(tile)

        # Add tools grid directly - tiles expand to fill available width
        layout.addWidget(self.tools_grid)
        # HTML: tools-section margin-bottom: 35px
        layout.addSpacing(35)

        # ===== DROP ZONE =====
        self.drop_zone = DropZone()
        self.drop_zone.files_dropped.connect(self._on_files_dropped)
        self.drop_zone.clicked.connect(self._browse_files)
        layout.addWidget(self.drop_zone)
        # HTML: drop-zone margin-bottom: 25px
        layout.addSpacing(25)

        # ===== FILE LIST SECTION =====
        self.file_list = FileListWidget()
        self.file_list.files_changed.connect(self._update_status)
        self.file_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.file_list.setMinimumHeight(150)
        layout.addWidget(self.file_list, 1)

        # Status bar with version
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Klar")

        # Version label on the right side
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("""
            font-family: 'Rajdhani', 'Segoe UI', sans-serif;
            font-size: 12px;
            color: #7FBFB5;
            padding-right: 10px;
        """)
        self.status_bar.addPermanentWidget(version_label)

    def resizeEvent(self, event: QResizeEvent):
        """Handle window resize for responsive layout."""
        super().resizeEvent(event)

        # Resize decorative lines overlay
        if hasattr(self, '_deco_lines'):
            self._deco_lines.setGeometry(0, 0, event.size().width(), event.size().height())

        available_width = event.size().width() - 80
        self.tools_grid.update_columns(available_width)

        # Responsive header text
        width = event.size().width()
        if width < 550:
            self.title_label.setStyleSheet("""
                font-family: 'Impact', 'Bebas Neue', sans-serif;
                font-size: 32px;
                font-weight: bold;
                letter-spacing: 8px;
                color: #D4A84B;
                padding: 8px;
            """)
            self.subtitle_label.setStyleSheet("""
                font-size: 10px;
                font-weight: 600;
                color: #7FBFB5;
                letter-spacing: 3px;
                padding: 0 8px 10px 8px;
            """)
            self.logo_label.setFixedSize(90, 90)
        else:
            self.title_label.setStyleSheet("")
            self.subtitle_label.setStyleSheet("")
            self.logo_label.setFixedSize(120, 120)

    def _create_section_header(self, text: str) -> QWidget:
        """Create a section header with decorative lines."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
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

    def _create_ornament(self) -> QWidget:
        """Create decorative Art Deco diamond ornament."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        left_line = QFrame()
        left_line.setFixedSize(40, 1)
        left_line.setStyleSheet("background: #D4A84B;")
        layout.addWidget(left_line)

        diamond = QLabel("◆")
        diamond.setStyleSheet("color: #D4A84B; font-size: 10px;")
        layout.addWidget(diamond)

        right_line = QFrame()
        right_line.setFixedSize(40, 1)
        right_line.setStyleSheet("background: #D4A84B;")
        layout.addWidget(right_line)

        return widget

    def _setup_shortcuts(self):
        """Configure keyboard shortcuts."""
        open_shortcut = QShortcut(QKeySequence.StandardKey.Open, self)
        open_shortcut.activated.connect(self._browse_files)

        delete_shortcut = QShortcut(QKeySequence.StandardKey.Delete, self)
        delete_shortcut.activated.connect(self.file_list.remove_selected)

        up_shortcut = QShortcut(QKeySequence("Ctrl+Up"), self)
        up_shortcut.activated.connect(self.file_list.move_up)

        down_shortcut = QShortcut(QKeySequence("Ctrl+Down"), self)
        down_shortcut.activated.connect(self.file_list.move_down)

    def _on_tool_clicked(self, tool: dict):
        """Handle tool tile click."""
        tool_id = tool['id']

        if tool_id == "settings":
            self._show_settings()
            return

        if not self.file_list.has_files():
            QMessageBox.information(
                self,
                "Ingen filer valgt",
                "Tilføj venligst mindst én fil først."
            )
            return

        files = self.file_list.get_files()

        if tool_id == "merge":
            self._show_merge_dialog(files)
        elif tool_id == "split":
            self._show_split_dialog(files)
        elif tool_id == "convert":
            self._show_convert_dialog(files)
        elif tool_id == "ocr":
            self._show_ocr_dialog(files)
        elif tool_id == "compress":
            self._show_compress_placeholder(files)
        else:
            QMessageBox.information(
                self,
                f"{tool['name']}",
                f"{tool['name']} funktionen er under udvikling."
            )

    def _show_merge_dialog(self, files: list[str]):
        if len(files) < 2:
            QMessageBox.information(self, "For få filer", "Tilføj mindst 2 PDF filer for at merge.")
            return
        dialog = MergeDialog(files, self)
        dialog.exec()

    def _show_split_dialog(self, files: list[str]):
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        if not pdf_files:
            QMessageBox.information(self, "Ingen PDF filer", "Tilføj en PDF fil for at splitte.")
            return
        dialog = SplitDialog(pdf_files[0], self)
        dialog.exec()

    def _show_convert_dialog(self, files: list[str]):
        docx_files = [f for f in files if f.lower().endswith(('.docx', '.doc'))]
        if not docx_files:
            QMessageBox.information(self, "Ingen Word-filer", "Tilføj Word-filer (.docx) for at konvertere til PDF.")
            return
        dialog = ConvertDialog(docx_files, self)
        dialog.exec()

    def _show_ocr_dialog(self, files: list[str]):
        """Show OCR dialog for text recognition."""
        # Filter to supported files (PDF and images)
        supported = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp']
        ocr_files = [f for f in files if Path(f).suffix.lower() in supported]

        if not ocr_files:
            QMessageBox.information(
                self,
                "Ingen understøttede filer",
                "Tilføj PDF eller billede filer til OCR."
            )
            return

        dialog = OCRDialog(ocr_files, self)
        dialog.exec()

    def _show_compress_placeholder(self, files: list[str]):
        QMessageBox.information(
            self, "Compress - Komprimér",
            "Komprimering er under udvikling.\n\n"
            "Denne funktion vil:\n"
            "• Reducere PDF filstørrelse\n"
            "• Tilbyde forskellige komprimerings niveauer\n"
            "• Bevare læsbar kvalitet"
        )

    def _show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def _browse_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Vælg filer", "",
            "PDF og Billeder (*.pdf *.png *.jpg *.jpeg *.tiff *.tif);;PDF filer (*.pdf);;Alle filer (*.*)"
        )
        if files:
            self.file_list.add_files(files)

    def _on_files_dropped(self, files: list[str]):
        self.file_list.add_files(files)

    def _update_status(self):
        count = self.file_list.file_count
        if count == 0:
            self.status_bar.showMessage("Klar")
        elif count == 1:
            self.status_bar.showMessage("1 fil valgt")
        else:
            self.status_bar.showMessage(f"{count} filer valgt")
