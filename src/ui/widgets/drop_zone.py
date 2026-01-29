"""
Drag and drop zone widget for file selection.
Matches pdf-toolkit-unified.html reference design exactly.
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QWidget, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QColor

from src.config.constants import SUPPORTED_EXTENSIONS
from src.ui.icons import get_drop_zone_icon


class DropZone(QFrame):
    """
    A drag-and-drop zone for adding PDF and image files.
    Art Deco styled with inner dashed border.
    Matches HTML: border 2px, padding 45px 30px, inner dashed border animates on hover.
    """

    files_dropped = pyqtSignal(list)
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("drop-zone")
        self.setAcceptDrops(True)
        self._hovered = False
        self._icon_widget = None
        self._icon_glow = None
        self._setup_ui()
        self._apply_normal_style()

    def _setup_ui(self):
        """Initialize the UI components."""
        # Match HTML drop zone - taller with proper padding
        self.setMinimumHeight(200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(0)
        # HTML: padding: 45px 30px
        layout.setContentsMargins(30, 45, 30, 45)

        # SVG Icon - 50x50 with glow effect on hover
        self._icon_widget = get_drop_zone_icon(size=50)
        self._icon_widget.setFixedSize(50, 50)
        self._icon_widget.setStyleSheet("background: transparent;")

        # Glow effect for icon - created on demand to avoid QPainter conflicts
        self._icon_glow = None

        icon_container = QWidget()
        icon_container.setStyleSheet("background: transparent;")
        icon_layout = QHBoxLayout(icon_container)
        # HTML: margin-bottom: 15px on icon
        icon_layout.setContentsMargins(0, 0, 0, 15)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(self._icon_widget)
        layout.addWidget(icon_container)

        # Instructions - Bebas Neue
        # HTML: font-size: 1.2rem (19px), letter-spacing: 0.2em (~4px), margin-bottom: 8px
        self._text_label = QLabel("TRÆK FILER HERTIL")
        self._text_label.setStyleSheet("""
            font-family: 'Bebas Neue', 'Impact', sans-serif;
            font-size: 20px;
            letter-spacing: 4px;
            color: #D4A84B;
            background: transparent;
            padding-bottom: 8px;
        """)
        self._text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._text_label)

        # Supported formats - Rajdhani
        # HTML: font-size: 0.9rem (14px), letter-spacing: 0.15em (~2px)
        self._formats_label = QLabel("PDF  ·  PNG  ·  JPG  ·  TIFF")
        self._formats_label.setStyleSheet("""
            font-family: 'Rajdhani', 'Segoe UI', sans-serif;
            font-size: 14px;
            letter-spacing: 3px;
            color: #7FBFB5;
            font-weight: 500;
            background: transparent;
        """)
        self._formats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._formats_label)

        # Inner dashed border (overlay frame)
        self._inner_border = QFrame(self)
        self._inner_border.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._inner_border.setStyleSheet("""
            background: transparent;
            border: 1px dashed #2D5A5A;
            border-radius: 4px;
        """)

    def _apply_normal_style(self):
        """Apply normal (non-hovered) style."""
        self.setStyleSheet("""
            DropZone {
                background: #0D1A1A;
                border: 2px solid #2D5A5A;
                border-radius: 8px;
            }
        """)
        # Remove icon glow effect to avoid QPainter conflicts
        if self._icon_glow:
            self._icon_widget.setGraphicsEffect(None)
            self._icon_glow = None
        # Update inner border
        self._update_inner_border()

    def _apply_hover_style(self):
        """Apply hovered style with gradient background and gold border."""
        self.setStyleSheet("""
            DropZone {
                background: qlineargradient(y1:0, y2:1,
                    stop:0 rgba(45, 90, 90, 0.2),
                    stop:1 #0D1A1A);
                border: 2px solid #D4A84B;
                border-radius: 8px;
            }
        """)
        # Create icon glow on hover - HTML: filter: drop-shadow(0 0 15px var(--gold))
        if not self._icon_glow:
            self._icon_glow = QGraphicsDropShadowEffect()
            self._icon_widget.setGraphicsEffect(self._icon_glow)
        self._icon_glow.setBlurRadius(30)
        self._icon_glow.setColor(QColor(212, 168, 75, 180))
        # Update inner border
        self._update_inner_border()

    def resizeEvent(self, event):
        """Update inner border position on resize."""
        super().resizeEvent(event)
        self._update_inner_border()

    def _update_inner_border(self):
        """Update the inner dashed border frame."""
        if hasattr(self, '_inner_border'):
            margin = 8 if self._hovered else 12
            self._inner_border.setGeometry(
                margin, margin,
                self.width() - 2 * margin,
                self.height() - 2 * margin
            )
            color = "#D4A84B" if self._hovered else "#2D5A5A"
            self._inner_border.setStyleSheet(f"""
                background: transparent;
                border: 1px dashed {color};
                border-radius: 4px;
            """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Accept drag if it contains files."""
        if event.mimeData().hasUrls():
            self._hovered = True
            self._apply_hover_style()
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        """Handle drag leave."""
        self._hovered = False
        self._apply_normal_style()
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent):
        """Handle dropped files."""
        self._hovered = False
        self._apply_normal_style()

        files = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(SUPPORTED_EXTENSIONS):
                files.append(path)

        if files:
            self.files_dropped.emit(files)

    def enterEvent(self, event):
        """Mouse enter - apply hover styling."""
        self._hovered = True
        self._apply_hover_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Mouse leave - reset styling."""
        self._hovered = False
        self._apply_normal_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Emit clicked signal when zone is clicked."""
        self.clicked.emit()
