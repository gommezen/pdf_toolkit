"""
Art Deco SVG Icons for PDF Toolkit.
All icons use the Metropolis color scheme:
- Primary stroke: #D4A84B (gold)
- Secondary/fill: #7FBFB5 (mint)

Usage:
    from src.ui.icons import TOOL_ICONS, get_icon_widget

    svg_string = TOOL_ICONS['ocr']
    widget = get_icon_widget('ocr', size=40)

Note: Uses pre-rendered QPixmap cache to avoid QPainter conflicts
that occur when multiple QSvgWidget instances render simultaneously.
"""

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QByteArray, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPainter

# Cache for pre-rendered pixmaps to avoid repeated SVG rendering
_pixmap_cache: dict[tuple[str, int], QPixmap] = {}


# =============================================================================
# COLOR CONSTANTS
# =============================================================================

GOLD = "#D4A84B"
GOLD_BRIGHT = "#E8C547"
MINT = "#7FBFB5"
TEAL = "#2D5A5A"


# =============================================================================
# TOOL ICONS (40x40 viewBox)
# =============================================================================

TOOL_ICONS = {
    "ocr": f'''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="20" cy="20" rx="16" ry="10" stroke="{GOLD}" stroke-width="1.5" fill="none"/>
        <circle cx="20" cy="20" r="6" stroke="{GOLD}" stroke-width="1.5" fill="none"/>
        <circle cx="20" cy="20" r="2.5" fill="{MINT}"/>
        <line x1="4" y1="20" x2="10" y2="20" stroke="{MINT}" stroke-width="1"/>
        <line x1="30" y1="20" x2="36" y2="20" stroke="{MINT}" stroke-width="1"/>
        <line x1="20" y1="4" x2="20" y2="8" stroke="{GOLD}" stroke-width="1" opacity="0.6"/>
        <line x1="20" y1="32" x2="20" y2="36" stroke="{GOLD}" stroke-width="1" opacity="0.6"/>
    </svg>''',
    
    "merge": f'''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="5" y="8" width="14" height="18" rx="1" stroke="{GOLD}" stroke-width="1.5" fill="none"/>
        <rect x="21" y="8" width="14" height="18" rx="1" stroke="{GOLD}" stroke-width="1.5" fill="none"/>
        <path d="M20 28 L20 36 M15 32 L20 37 L25 32" stroke="{MINT}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="8" y1="13" x2="16" y2="13" stroke="{MINT}" stroke-width="1"/>
        <line x1="8" y1="17" x2="16" y2="17" stroke="{MINT}" stroke-width="1"/>
        <line x1="24" y1="13" x2="32" y2="13" stroke="{MINT}" stroke-width="1"/>
        <line x1="24" y1="17" x2="32" y2="17" stroke="{MINT}" stroke-width="1"/>
    </svg>''',
    
    "split": f'''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="13" y="4" width="14" height="18" rx="1" stroke="{GOLD}" stroke-width="1.5" fill="none"/>
        <path d="M12 26 L6 34" stroke="{MINT}" stroke-width="1.5" stroke-linecap="round"/>
        <path d="M28 26 L34 34" stroke="{MINT}" stroke-width="1.5" stroke-linecap="round"/>
        <rect x="2" y="32" width="10" height="6" rx="1" stroke="{GOLD}" stroke-width="1" fill="none"/>
        <rect x="28" y="32" width="10" height="6" rx="1" stroke="{GOLD}" stroke-width="1" fill="none"/>
        <line x1="10" y1="22" x2="30" y2="22" stroke="{GOLD}" stroke-width="1" stroke-dasharray="2 2"/>
    </svg>''',
    
    "compress": f'''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M8 12 L20 20 L8 28" stroke="{MINT}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        <path d="M32 12 L20 20 L32 28" stroke="{MINT}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        <rect x="16" y="14" width="8" height="12" rx="1" stroke="{GOLD}" stroke-width="1.5" fill="none"/>
        <line x1="14" y1="6" x2="26" y2="6" stroke="{GOLD}" stroke-width="1"/>
        <line x1="14" y1="34" x2="26" y2="34" stroke="{GOLD}" stroke-width="1"/>
        <circle cx="20" cy="6" r="2" fill="{GOLD}"/>
        <circle cx="20" cy="34" r="2" fill="{GOLD}"/>
    </svg>''',
    
    "convert": f'''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="4" y="10" width="12" height="16" rx="1" stroke="{GOLD}" stroke-width="1.5" fill="none"/>
        <text x="10" y="21" text-anchor="middle" fill="{MINT}" font-size="6" font-weight="bold" font-family="sans-serif">W</text>
        <path d="M18 18 L22 18 M20 15 L23 18 L20 21" stroke="{GOLD}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        <rect x="24" y="10" width="12" height="16" rx="1" stroke="{GOLD}" stroke-width="1.5" fill="none"/>
        <text x="30" y="20" text-anchor="middle" fill="{MINT}" font-size="5" font-weight="bold" font-family="sans-serif">PDF</text>
        <path d="M4 10 L4 6 L8 6" stroke="{GOLD}" stroke-width="1" fill="none"/>
        <path d="M36 26 L36 30 L32 30" stroke="{GOLD}" stroke-width="1" fill="none"/>
    </svg>''',
    
    "remove": f'''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="10" y="6" width="20" height="28" rx="1" stroke="{GOLD}" stroke-width="1.5" fill="none"/>
        <line x1="15" y1="16" x2="25" y2="26" stroke="{MINT}" stroke-width="2" stroke-linecap="round"/>
        <line x1="25" y1="16" x2="15" y2="26" stroke="{MINT}" stroke-width="2" stroke-linecap="round"/>
        <line x1="13" y1="10" x2="27" y2="10" stroke="{GOLD}" stroke-width="1" opacity="0.5"/>
    </svg>''',
    
    "rotate": f'''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M20 8 A12 12 0 1 1 8 20" stroke="{GOLD}" stroke-width="1.5" fill="none" stroke-linecap="round"/>
        <path d="M20 4 L20 12 L12 8 Z" fill="{MINT}"/>
        <rect x="15" y="15" width="10" height="12" rx="1" stroke="{GOLD}" stroke-width="1" fill="none"/>
    </svg>''',
    
    "encrypt": f'''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="12" y="18" width="16" height="14" rx="2" stroke="{GOLD}" stroke-width="1.5" fill="none"/>
        <path d="M15 18 L15 12 A5 5 0 0 1 25 12 L25 18" stroke="{GOLD}" stroke-width="1.5" fill="none"/>
        <circle cx="20" cy="24" r="2" fill="{MINT}"/>
        <rect x="19" y="24" width="2" height="4" fill="{MINT}"/>
        <line x1="20" y1="4" x2="20" y2="8" stroke="{GOLD}" stroke-width="1" opacity="0.5"/>
        <line x1="8" y1="25" x2="4" y2="25" stroke="{GOLD}" stroke-width="1" opacity="0.5"/>
        <line x1="36" y1="25" x2="32" y2="25" stroke="{GOLD}" stroke-width="1" opacity="0.5"/>
    </svg>''',
    
    "settings": f'''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M20 6 L22 10 L26 8 L26 13 L31 12 L28 17 L33 19 L28 23 L31 28 L26 27 L26 32 L22 30 L20 34 L18 30 L14 32 L14 27 L9 28 L12 23 L7 19 L12 17 L9 12 L14 13 L14 8 L18 10 Z"
              stroke="{GOLD}" stroke-width="1.5" fill="none"/>
        <circle cx="20" cy="20" r="5" stroke="{MINT}" stroke-width="1.5" fill="none"/>
        <circle cx="20" cy="20" r="2" fill="{MINT}"/>
    </svg>''',

    "citation": f'''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="8" y="4" width="24" height="32" rx="2" stroke="{GOLD}" stroke-width="1.5" fill="none"/>
        <path d="M8 10 L32 10" stroke="{GOLD}" stroke-width="1" opacity="0.5"/>
        <text x="14" y="20" fill="{MINT}" font-size="14" font-family="Georgia, serif">"</text>
        <text x="26" y="30" fill="{MINT}" font-size="14" font-family="Georgia, serif">"</text>
        <line x1="16" y1="24" x2="28" y2="24" stroke="{GOLD}" stroke-width="1"/>
        <line x1="12" y1="28" x2="24" y2="28" stroke="{GOLD}" stroke-width="1" opacity="0.6"/>
        <circle cx="32" cy="4" r="3" fill="{GOLD}" opacity="0.4"/>
    </svg>''',
}


# =============================================================================
# DROP ZONE ICON (50x50)
# =============================================================================

DROP_ZONE_ICON = f'''<svg viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="12" y="6" width="26" height="34" rx="2" stroke="{GOLD}" stroke-width="2" fill="none"/>
    <path d="M30 6 L38 14 L30 14 Z" fill="{MINT}" stroke="{GOLD}" stroke-width="1"/>
    <line x1="25" y1="22" x2="25" y2="34" stroke="{MINT}" stroke-width="2" stroke-linecap="round"/>
    <line x1="19" y1="28" x2="31" y2="28" stroke="{MINT}" stroke-width="2" stroke-linecap="round"/>
    <circle cx="6" cy="23" r="2" fill="{GOLD}" opacity="0.5"/>
    <circle cx="44" cy="23" r="2" fill="{GOLD}" opacity="0.5"/>
</svg>'''


# =============================================================================
# FILE ICON (28x28)
# =============================================================================

FILE_ICON = f'''<svg viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="4" y="2" width="16" height="22" rx="1" stroke="{GOLD}" stroke-width="1.5" fill="none"/>
    <path d="M14 2 L20 8 L14 8 Z" fill="{MINT}"/>
    <line x1="7" y1="12" x2="17" y2="12" stroke="{MINT}" stroke-width="1"/>
    <line x1="7" y1="16" x2="17" y2="16" stroke="{MINT}" stroke-width="1"/>
    <line x1="7" y1="20" x2="13" y2="20" stroke="{MINT}" stroke-width="1"/>
</svg>'''


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def svg_to_pixmap(svg_string: str, size: int) -> QPixmap:
    """
    Convert SVG string to QPixmap with caching.
    Uses a cache to avoid repeated rendering and QPainter conflicts.

    Args:
        svg_string: The SVG markup
        size: Size in pixels (square)

    Returns:
        QPixmap rendered from the SVG (cached)
    """
    # Use hash of svg_string for cache key
    cache_key = (hash(svg_string), size)

    if cache_key in _pixmap_cache:
        return _pixmap_cache[cache_key]

    # Render SVG to pixmap
    renderer = QSvgRenderer(QByteArray(svg_string.encode('utf-8')))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    # Cache the result
    _pixmap_cache[cache_key] = pixmap
    return pixmap


def get_icon_pixmap(icon_id: str, size: int = 40) -> QPixmap:
    """
    Get a tool icon as QPixmap by ID (cached).

    Args:
        icon_id: The tool ID (e.g., 'ocr', 'merge', 'split')
        size: Pixmap size in pixels

    Returns:
        QPixmap with the icon, or empty pixmap if not found
    """
    svg_string = TOOL_ICONS.get(icon_id, '')
    if not svg_string:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        return pixmap
    return svg_to_pixmap(svg_string, size)


def get_icon_widget(icon_id: str, size: int = 40) -> QLabel:
    """
    Get a tool icon widget by ID.
    Uses QLabel with pre-rendered pixmap to avoid QPainter conflicts.

    Args:
        icon_id: The tool ID (e.g., 'ocr', 'merge', 'split')
        size: Widget size in pixels

    Returns:
        QLabel with the icon pixmap
    """
    label = QLabel()
    label.setFixedSize(size, size)
    label.setStyleSheet("background: transparent;")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    pixmap = get_icon_pixmap(icon_id, size)
    label.setPixmap(pixmap)
    return label


def get_drop_zone_icon(size: int = 50) -> QLabel:
    """Get the drop zone icon widget as QLabel with pixmap."""
    label = QLabel()
    label.setFixedSize(size, size)
    label.setStyleSheet("background: transparent;")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setPixmap(svg_to_pixmap(DROP_ZONE_ICON, size))
    return label


def get_file_icon(size: int = 28) -> QLabel:
    """Get the file icon widget as QLabel with pixmap."""
    label = QLabel()
    label.setFixedSize(size, size)
    label.setStyleSheet("background: transparent;")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setPixmap(svg_to_pixmap(FILE_ICON, size))
    return label


def get_svg_widget(svg_string: str, size: int = 40) -> QLabel:
    """
    Create a QLabel with pre-rendered SVG pixmap.
    Legacy function name kept for compatibility.

    Args:
        svg_string: The SVG markup as a string
        size: Widget size in pixels (square)

    Returns:
        QLabel with the rendered SVG
    """
    label = QLabel()
    label.setFixedSize(size, size)
    label.setStyleSheet("background: transparent;")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setPixmap(svg_to_pixmap(svg_string, size))
    return label
