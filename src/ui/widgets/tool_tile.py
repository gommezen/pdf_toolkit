"""
Tool tile button widget - Art Deco style with SVG icons.
Matches pdf-toolkit-unified.html reference design exactly.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QFrame, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor

from src.ui.icons import get_icon_widget


class ToolTile(QFrame):
    """
    Clickable tool tile with SVG icon, name, and description.
    Art Deco styled matching HTML reference exactly.

    HTML interactions:
    - transition: all 0.3s ease
    - hover: translateY(-4px), gold border, box-shadow, icon glow
    - active: translateY(-2px)
    - ::before top gold line fades in
    - ::after bottom mint line grows to 60%
    """

    tool_clicked = pyqtSignal(dict)

    def __init__(self, tool_config: dict, parent=None):
        super().__init__(parent)
        self.tool_config = tool_config
        self._enabled = tool_config.get('enabled', True)
        self._icon_widget = None
        self._icon_glow = None
        self._hovered = False
        self._pressed = False

        self._setup_ui()
        self._apply_normal_style()

    def _setup_ui(self):
        """Initialize the UI components with SVG icon."""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        # HTML: padding: 20px 12px
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # SVG Icon - 40x40 with margin-bottom: 12px
        tool_id = self.tool_config.get('id', '')
        self._icon_widget = get_icon_widget(tool_id, size=40)
        self._icon_widget.setFixedSize(40, 40)
        self._icon_widget.setStyleSheet("background: transparent;")

        # Icon glow effect - created on demand to avoid QPainter conflicts at startup
        self._icon_glow = None

        # Center the icon
        icon_container = QWidget()
        icon_container.setStyleSheet("background: transparent;")
        icon_container.setFixedHeight(52)  # 40px icon + 12px margin
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 12)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(self._icon_widget)
        layout.addWidget(icon_container)

        # Name - Bebas Neue, gold, uppercase
        # HTML: font-size: 1.1rem (18px), letter-spacing: 0.15em (~2.7px)
        self.name_label = QLabel(self.tool_config['name'].upper())
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label)

        # Description - Rajdhani, mint
        # HTML: font-size: 0.8rem (13px), font-weight: 500, NO letter-spacing
        self.desc_label = QLabel(self.tool_config['desc'])
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.desc_label)

        # Expand to fill available width in grid
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumSize(140, 120)
        self.setFixedHeight(130)
        self.setCursor(Qt.CursorShape.PointingHandCursor if self._enabled else Qt.CursorShape.ForbiddenCursor)

        # Set tooltip from config
        self.setToolTip(self.tool_config.get('tooltip', ''))

        # Shadow effect for tile - created on demand to avoid QPainter conflicts at startup
        self._shadow = None

        # Decorative lines (overlays, hidden by default)
        self._top_line = QFrame(self)
        self._top_line.setFixedHeight(2)
        self._top_line.setVisible(False)
        self._top_line.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self._bottom_line = QFrame(self)
        self._bottom_line.setFixedHeight(2)
        self._bottom_line.setVisible(False)
        self._bottom_line.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def _apply_normal_style(self):
        """Apply normal (non-hovered) style."""
        if self._enabled:
            self.setStyleSheet("""
                ToolTile {
                    background: qlineargradient(x1:0, y1:0, x2:0.8, y2:1,
                        stop:0 rgba(45, 90, 90, 0.4),
                        stop:1 rgba(13, 26, 26, 0.9));
                    border: 1px solid #2D5A5A;
                    border-radius: 6px;
                }
            """)
            self.name_label.setStyleSheet("""
                font-family: 'Bebas Neue', 'Impact', sans-serif;
                font-size: 18px;
                letter-spacing: 3px;
                color: #D4A84B;
                background: transparent;
            """)
            self.desc_label.setStyleSheet("""
                font-family: 'Rajdhani', 'Segoe UI', sans-serif;
                font-size: 13px;
                font-weight: 500;
                color: #7FBFB5;
                background: transparent;
            """)
        else:
            self.setStyleSheet("""
                ToolTile {
                    background: rgba(13, 26, 26, 0.5);
                    border: 1px solid rgba(45, 90, 90, 0.25);
                    border-radius: 6px;
                }
            """)
            self.name_label.setStyleSheet("""
                font-family: 'Bebas Neue', 'Impact', sans-serif;
                font-size: 18px;
                letter-spacing: 3px;
                color: rgba(212, 168, 75, 0.35);
                background: transparent;
            """)
            self.desc_label.setStyleSheet("""
                font-family: 'Rajdhani', 'Segoe UI', sans-serif;
                font-size: 13px;
                font-weight: 500;
                color: rgba(127, 191, 181, 0.35);
                background: transparent;
            """)

        # Remove shadow effects when not hovered (avoids QPainter conflicts)
        if self._shadow:
            self.setGraphicsEffect(None)
            self._shadow = None
        if self._icon_glow:
            self._icon_widget.setGraphicsEffect(None)
            self._icon_glow = None

    def _apply_hover_style(self):
        """Apply hover style with gold border, shadow, and icon glow."""
        self.setStyleSheet("""
            ToolTile {
                background: qlineargradient(x1:0, y1:0, x2:0.8, y2:1,
                    stop:0 rgba(74, 128, 128, 0.5),
                    stop:1 rgba(18, 36, 36, 0.95));
                border: 1px solid #D4A84B;
                border-radius: 6px;
            }
        """)

        # Brighter gold text
        self.name_label.setStyleSheet("""
            font-family: 'Bebas Neue', 'Impact', sans-serif;
            font-size: 18px;
            letter-spacing: 3px;
            color: #E8C547;
            background: transparent;
        """)

        # Create shadow effect on hover - HTML: 0 15px 40px rgba(0,0,0,0.5)
        if not self._shadow:
            self._shadow = QGraphicsDropShadowEffect()
            self.setGraphicsEffect(self._shadow)
        self._shadow.setBlurRadius(40)
        self._shadow.setOffset(0, 12)
        self._shadow.setColor(QColor(0, 0, 0, 130))

        # Create icon glow on hover - HTML: filter: drop-shadow(0 0 8px var(--gold))
        if not self._icon_glow:
            self._icon_glow = QGraphicsDropShadowEffect()
            self._icon_widget.setGraphicsEffect(self._icon_glow)
        self._icon_glow.setBlurRadius(16)
        self._icon_glow.setColor(QColor(212, 168, 75, 200))

    def resizeEvent(self, event):
        """Update decorative lines position on resize."""
        super().resizeEvent(event)
        self._update_decorative_lines()

    def _update_decorative_lines(self):
        """Update position and visibility of decorative lines."""
        w = self.width()
        h = self.height()

        # Top gold gradient line
        self._top_line.setGeometry(0, 0, w, 2)
        self._top_line.setStyleSheet("""
            background: qlineargradient(x1:0, x2:1,
                stop:0 transparent,
                stop:0.3 rgba(212, 168, 75, 200),
                stop:0.5 rgba(232, 197, 71, 255),
                stop:0.7 rgba(212, 168, 75, 200),
                stop:1 transparent);
        """)

        # Bottom mint line (60% width, centered)
        line_width = int(w * 0.6)
        start_x = (w - line_width) // 2
        self._bottom_line.setGeometry(start_x, h - 2, line_width, 2)
        self._bottom_line.setStyleSheet("background: #7FBFB5;")

    def _show_decorative_lines(self, show: bool):
        """Show or hide the decorative hover lines."""
        self._top_line.setVisible(show)
        self._bottom_line.setVisible(show)
        if show:
            self._update_decorative_lines()

    def mousePressEvent(self, event):
        """Handle mouse press - active state."""
        if self._enabled and event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            # Slightly reduce shadow on press (HTML: translateY(-2px) vs -4px on hover)
            if self._shadow:
                self._shadow.setOffset(0, 6)
                self._shadow.setBlurRadius(25)

    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if self._enabled and event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            if self._hovered and self._shadow:
                # Restore hover shadow
                self._shadow.setOffset(0, 12)
                self._shadow.setBlurRadius(40)
            # Emit click signal
            self.tool_clicked.emit(self.tool_config)

    def enterEvent(self, event):
        """Handle mouse enter - hover effect."""
        if self._enabled:
            self._hovered = True
            self._apply_hover_style()
            self._show_decorative_lines(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave - reset to normal."""
        if self._enabled:
            self._hovered = False
            self._pressed = False
            self._apply_normal_style()
            self._show_decorative_lines(False)
        super().leaveEvent(event)

    @property
    def tool_id(self) -> str:
        """Get the tool ID."""
        return self.tool_config.get('id', '')

    def set_enabled(self, enabled: bool):
        """Enable or disable the tool tile."""
        self._enabled = enabled
        self.tool_config['enabled'] = enabled
        self._apply_normal_style()
        self.setCursor(Qt.CursorShape.PointingHandCursor if enabled else Qt.CursorShape.ForbiddenCursor)
