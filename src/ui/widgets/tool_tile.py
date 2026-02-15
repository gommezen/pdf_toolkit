"""
Tool tile button widget - Art Deco style with SVG icons.
Matches pdf-toolkit-unified.html reference design exactly.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QFrame, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import pyqtSignal, pyqtProperty, Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor

from src.ui.icons import get_icon_widget


class AnimatedFrame(QFrame):
    """QFrame subclass with animatable properties for mint line."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._line_width_percent = 0

    def get_line_width_percent(self):
        return self._line_width_percent

    def set_line_width_percent(self, value):
        self._line_width_percent = value
        self._update_width()

    def _update_width(self):
        parent = self.parent()
        if parent:
            w = parent.width()
            line_width = int(w * self._line_width_percent / 100)
            start_x = (w - line_width) // 2
            h = parent.height()
            self.setGeometry(start_x, h - 2, line_width, 2)

    lineWidthPercent = pyqtProperty(int, fget=get_line_width_percent, fset=set_line_width_percent)


class ToolTile(QWidget):
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
        self._tile_frame = None  # The visual box that moves
        self._mint_animation = None
        self._lift_animation = None
        self._lift_amount = 0

        self._setup_ui()
        self._apply_normal_style()

    def _setup_ui(self):
        """Initialize the UI components with SVG icon."""
        # This widget is the container (transparent, fixed in grid)
        self.setStyleSheet("background: transparent;")

        # The visual tile frame that will move up/down
        self._tile_frame = QFrame(self)
        self._tile_frame.setObjectName("TileFrame")

        # Content layout inside the tile frame
        layout = QVBoxLayout(self._tile_frame)
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

        # Container size (extra height for lift headroom)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumSize(140, 134)
        self.setFixedHeight(134)  # 130 + 4 for lift headroom
        self.setCursor(Qt.CursorShape.PointingHandCursor if self._enabled else Qt.CursorShape.ForbiddenCursor)

        # Set tooltip from config
        self.setToolTip(self.tool_config.get('tooltip', ''))

        # Shadow effect for tile - created on demand to avoid QPainter conflicts at startup
        self._shadow = None

        # Decorative lines (overlays on the tile frame)
        self._top_line = QFrame(self._tile_frame)
        self._top_line.setFixedHeight(2)
        self._top_line.setVisible(False)
        self._top_line.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Animated bottom mint line
        self._bottom_line = AnimatedFrame(self._tile_frame)
        self._bottom_line.setFixedHeight(2)
        self._bottom_line.setVisible(False)
        self._bottom_line.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._bottom_line.setStyleSheet("background: #7FBFB5;")

    def _apply_normal_style(self):
        """Apply normal (non-hovered) style."""
        if self._enabled:
            self._tile_frame.setStyleSheet("""
                QFrame#TileFrame {
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
            self._tile_frame.setStyleSheet("""
                QFrame#TileFrame {
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
            self._tile_frame.setGraphicsEffect(None)
            self._shadow = None
        if self._icon_glow:
            self._icon_widget.setGraphicsEffect(None)
            self._icon_glow = None

    def _apply_hover_style(self):
        """Apply hover style with gold border, shadow, and icon glow."""
        self._tile_frame.setStyleSheet("""
            QFrame#TileFrame {
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
            self._tile_frame.setGraphicsEffect(self._shadow)
        self._shadow.setBlurRadius(40)
        self._shadow.setOffset(0, 15)
        self._shadow.setColor(QColor(0, 0, 0, 130))

        # Create icon glow on hover - HTML: filter: drop-shadow(0 0 8px var(--gold))
        # Centered glow behind icon, soft falloff
        if not self._icon_glow:
            self._icon_glow = QGraphicsDropShadowEffect()
            self._icon_widget.setGraphicsEffect(self._icon_glow)
        self._icon_glow.setBlurRadius(30)  # Larger blur for softer falloff
        self._icon_glow.setOffset(0, 0)  # Centered
        self._icon_glow.setColor(QColor(212, 168, 75, 220))  # Slightly transparent for smoother fade

    def resizeEvent(self, event):
        """Update tile frame and decorative lines on resize."""
        super().resizeEvent(event)
        self._update_tile_frame_position()
        self._update_decorative_lines()

    def _update_decorative_lines(self):
        """Update position and visibility of decorative lines."""
        if not self._tile_frame:
            return
        w = self._tile_frame.width()
        h = self._tile_frame.height()

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

        # Bottom mint line - AnimatedFrame handles its own geometry
        self._bottom_line._update_width()

    def _show_decorative_lines(self, show: bool):
        """Show or hide the decorative hover lines."""
        self._top_line.setVisible(show)
        self._bottom_line.setVisible(show)
        if show:
            self._update_decorative_lines()

    def mousePressEvent(self, event):
        """Handle mouse press - active state (translateY(-2px))."""
        if self._enabled and event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            # Reduce lift on press: -2px instead of -4px
            self._set_lift(2)
            # Reduce shadow on press
            if self._shadow:
                self._shadow.setOffset(0, 8)
                self._shadow.setBlurRadius(30)

    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if self._enabled and event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            if self._hovered:
                # Restore hover lift (-4px) and shadow
                self._set_lift(4)
                if self._shadow:
                    self._shadow.setOffset(0, 15)
                    self._shadow.setBlurRadius(40)
            # Emit click signal
            self.tool_clicked.emit(self.tool_config)

    def _update_tile_frame_position(self):
        """Update tile frame position based on lift amount."""
        if self._tile_frame:
            w = self.width()
            h = self.height()
            tile_height = 130  # Visual tile height
            # Position: 4px headroom at top, lift moves it up
            top = 4 - self._lift_amount
            self._tile_frame.setGeometry(0, top, w, tile_height)

    def _set_lift(self, lift_amount: int):
        """Set tile lift by moving the tile frame up."""
        self._lift_amount = lift_amount
        self._update_tile_frame_position()

    def _get_lift(self):
        return self._lift_amount

    # pyqtProperty for QPropertyAnimation
    liftAmount = pyqtProperty(int, fget=_get_lift, fset=_set_lift)

    def _animate_lift(self, target: int):
        """Animate the lift with 0.3s ease transition."""
        if self._lift_animation is None:
            self._lift_animation = QPropertyAnimation(self, b"liftAmount")
            self._lift_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._lift_animation.stop()
        self._lift_animation.setDuration(300)  # 0.3s like CSS transition
        self._lift_animation.setStartValue(self._lift_amount)
        self._lift_animation.setEndValue(target)
        self._lift_animation.start()

    def _animate_mint_line(self, target_percent: int):
        """Animate the mint line width from center."""
        if self._mint_animation is None:
            self._mint_animation = QPropertyAnimation(self._bottom_line, b"lineWidthPercent")
            self._mint_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._mint_animation.stop()
        self._mint_animation.setDuration(300)  # 0.3s - same as lift animation
        self._mint_animation.setStartValue(self._bottom_line.get_line_width_percent())
        self._mint_animation.setEndValue(target_percent)
        self._mint_animation.start()

    def enterEvent(self, event):
        """Handle mouse enter - hover effect with lift."""
        if self._enabled:
            self._hovered = True
            self._apply_hover_style()
            self._show_decorative_lines(True)
            self._animate_lift(4)  # translateY(-4px) with 0.3s ease
            self._animate_mint_line(60)  # Grow to 60%
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave - reset to normal."""
        if self._enabled:
            self._hovered = False
            self._pressed = False
            self._apply_normal_style()
            self._show_decorative_lines(False)
            self._animate_lift(0)  # Reset lift with 0.3s ease
            self._animate_mint_line(0)  # Shrink to 0%
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
