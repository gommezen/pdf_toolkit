"""
Application stylesheet definitions - Metropolis/Art Deco Theme.
Matches the pdf-toolkit-unified.html reference design.
"""


def get_stylesheet() -> str:
    """Return the main application stylesheet with Art Deco theme."""
    return """
/* ============================================
   METROPOLIS / ART DECO THEME
   Matches HTML reference design
   ============================================ */

QMainWindow {
    background: qlineargradient(y1:0, y2:1,
        stop:0 #0D1A1A,
        stop:0.5 #122424,
        stop:1 #1A3333);
}

QWidget {
    font-family: 'Segoe UI', 'Rajdhani', sans-serif;
    color: #E8E4D9;
}

QScrollArea {
    border: none;
    background: transparent;
}

QScrollArea > QWidget > QWidget {
    background: transparent;
}

/* ============================================
   HEADER STYLING
   ============================================ */

QLabel#title {
    font-family: 'Bebas Neue', 'Impact', sans-serif;
    font-size: 56px;
    font-weight: normal;
    letter-spacing: 22px;
    color: #D4A84B;
    padding: 10px 10px 5px 10px;
}

QLabel#subtitle {
    font-family: 'Rajdhani', 'Segoe UI', sans-serif;
    font-size: 16px;
    font-weight: 500;
    color: #7FBFB5;
    letter-spacing: 5px;
    text-transform: uppercase;
    padding: 0 10px 15px 10px;
}

/* ============================================
   TOOL TILES - ART DECO STYLE
   ============================================ */

/* Handled in ToolTile widget directly */

/* ============================================
   DROP ZONE - ART DECO
   Styled directly in drop_zone.py widget
   ============================================ */

/* ============================================
   FILE LIST
   ============================================ */

QListWidget {
    background: rgba(13, 26, 26, 0.95);
    border: 1px solid #2D5A5A;
    border-radius: 6px;
    padding: 4px;
    outline: none;
}

QListWidget::item {
    padding: 10px 14px;
    border-radius: 4px;
    border-bottom: 1px solid rgba(45, 90, 90, 0.3);
    color: #E8E4D9;
    font-size: 13px;
}

QListWidget::item:last-child {
    border-bottom: none;
}

QListWidget::item:selected {
    background: rgba(212, 168, 75, 0.15);
    border: 1px solid rgba(212, 168, 75, 0.5);
    color: #E8E4D9;
}

QListWidget::item:hover {
    background: rgba(45, 90, 90, 0.25);
}

/* ============================================
   STATUS BAR
   ============================================ */

QStatusBar {
    background: #0D1A1A;
    border-top: 1px solid #2D5A5A;
    color: #7FBFB5;
    font-weight: 500;
    font-size: 12px;
    padding: 6px 12px;
}

/* ============================================
   BUTTONS
   ============================================ */

/* Primary action buttons - Gold */
QPushButton.action-btn {
    background: qlineargradient(y1:0, y2:1,
        stop:0 #D4A84B,
        stop:1 #B8923A);
    color: #0D1A1A;
    border: none;
    border-radius: 4px;
    padding: 10px 24px;
    font-weight: bold;
    font-size: 12px;
    letter-spacing: 2px;
}

QPushButton.action-btn:hover {
    background: qlineargradient(y1:0, y2:1,
        stop:0 #E8C547,
        stop:1 #D4A84B);
}

QPushButton.action-btn:pressed {
    background: #B8923A;
}

QPushButton.action-btn:disabled {
    background: rgba(45, 90, 90, 0.4);
    color: rgba(127, 191, 181, 0.4);
}

/* Secondary buttons - Outlined */
QPushButton.secondary-btn {
    background: transparent;
    color: #7FBFB5;
    border: 1px solid #2D5A5A;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: 500;
    font-size: 12px;
}

QPushButton.secondary-btn:hover {
    border-color: #D4A84B;
    color: #D4A84B;
    background: rgba(45, 90, 90, 0.2);
}

QPushButton.secondary-btn:pressed {
    background: rgba(45, 90, 90, 0.4);
}

/* ============================================
   DIALOG STYLES
   ============================================ */

QDialog {
    background: qlineargradient(y1:0, y2:1,
        stop:0 #0D1A1A,
        stop:0.5 #122424,
        stop:1 #1A3333);
}

QGroupBox {
    font-family: 'Impact', 'Bebas Neue', sans-serif;
    font-weight: bold;
    font-size: 13px;
    letter-spacing: 3px;
    color: #7FBFB5;
    border: 1px solid #2D5A5A;
    border-radius: 6px;
    margin-top: 18px;
    padding-top: 16px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 12px;
    color: #7FBFB5;
}

/* ComboBox */
QComboBox {
    background-color: #0D1A1A;
    border: 1px solid #2D5A5A;
    border-radius: 4px;
    padding: 8px 14px;
    min-width: 140px;
    color: #E8E4D9;
    font-size: 12px;
}

QComboBox:hover {
    border-color: #4A8080;
}

QComboBox:focus {
    border-color: #D4A84B;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
    background: transparent;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #7FBFB5;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #0D1A1A;
    border: 1px solid #2D5A5A;
    selection-background-color: rgba(212, 168, 75, 0.3);
    selection-color: #E8C547;
    color: #E8E4D9;
    outline: none;
}

QComboBox QAbstractItemView::item {
    background-color: #0D1A1A;
    color: #E8E4D9;
    padding: 8px 12px;
    min-height: 24px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #1A3333;
}

QComboBox QAbstractItemView::item:selected {
    background-color: rgba(212, 168, 75, 0.25);
    color: #E8C547;
}

/* Progress bar */
QProgressBar {
    border: 1px solid #2D5A5A;
    border-radius: 4px;
    background: #0D1A1A;
    text-align: center;
    height: 24px;
    color: #E8E4D9;
    font-size: 11px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, x2:1,
        stop:0 #B8923A,
        stop:0.5 #D4A84B,
        stop:1 #E8C547);
    border-radius: 3px;
}

/* Radio buttons */
QRadioButton {
    spacing: 10px;
    color: #E8E4D9;
    font-size: 12px;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #2D5A5A;
    border-radius: 9px;
    background: #0D1A1A;
}

QRadioButton::indicator:hover {
    border-color: #4A8080;
}

QRadioButton::indicator:checked {
    border-color: #D4A84B;
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.4,
        fx:0.5, fy:0.5,
        stop:0 #D4A84B,
        stop:1 #B8923A);
}

/* Spin box and line edit */
QSpinBox, QLineEdit {
    background-color: #0D1A1A;
    border: 1px solid #2D5A5A;
    border-radius: 4px;
    padding: 8px 12px;
    color: #E8E4D9;
    font-size: 12px;
}

QSpinBox:hover, QLineEdit:hover {
    border-color: #4A8080;
}

QSpinBox:focus, QLineEdit:focus {
    border-color: #D4A84B;
}

QSpinBox::up-button, QSpinBox::down-button {
    background-color: #1A3333;
    border: none;
    width: 20px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: rgba(212, 168, 75, 0.25);
}

/* Dialog buttons */
QDialog QPushButton {
    background-color: #1A3333;
    color: #7FBFB5;
    border: 1px solid #2D5A5A;
    border-radius: 4px;
    padding: 8px 20px;
    min-width: 80px;
    font-size: 12px;
}

QDialog QPushButton:hover {
    border-color: #D4A84B;
    color: #D4A84B;
    background-color: #1A3333;
}

QDialog QPushButton:pressed {
    background-color: #0D1A1A;
}

QDialog QPushButton[class="action-btn"] {
    background: qlineargradient(y1:0, y2:1,
        stop:0 #D4A84B,
        stop:1 #B8923A);
    color: #0D1A1A;
    border: none;
    font-weight: bold;
    letter-spacing: 2px;
}

QDialog QPushButton[class="action-btn"]:hover {
    background: qlineargradient(y1:0, y2:1,
        stop:0 #E8C547,
        stop:1 #D4A84B);
    color: #0D1A1A;
}

/* Labels */
QLabel {
    color: #E8E4D9;
}

/* Scroll bars */
QScrollBar:vertical {
    background: #0D1A1A;
    width: 10px;
    border-radius: 5px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: #2D5A5A;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #4A8080;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: #0D1A1A;
    height: 10px;
    border-radius: 5px;
    margin: 2px;
}

QScrollBar::handle:horizontal {
    background: #2D5A5A;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: #4A8080;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Message boxes */
QMessageBox {
    background: #122424;
}

QMessageBox QLabel {
    color: #E8E4D9;
    font-size: 12px;
}

QMessageBox QPushButton {
    background: transparent;
    color: #7FBFB5;
    border: 1px solid #2D5A5A;
    border-radius: 4px;
    padding: 8px 24px;
    min-width: 80px;
    font-size: 12px;
}

QMessageBox QPushButton:hover {
    border-color: #D4A84B;
    color: #D4A84B;
}

/* Tooltips */
QToolTip {
    background: #1A3333;
    border: 1px solid #D4A84B;
    color: #E8E4D9;
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 11px;
}

/* ============================================
   DECORATIVE SEPARATOR
   ============================================ */

QFrame#deco-line {
    background: qlineargradient(x1:0, x2:1,
        stop:0 transparent,
        stop:0.15 #2D5A5A,
        stop:0.5 #D4A84B,
        stop:0.85 #2D5A5A,
        stop:1 transparent);
    max-height: 2px;
    min-height: 2px;
}
"""
