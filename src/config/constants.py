"""
Application constants and tool definitions.
"""

# Application metadata
VERSION = "1.0.0"
APP_NAME = "PDF Toolkit"

# Supported file extensions
SUPPORTED_EXTENSIONS = ('.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.docx', '.doc')
PDF_EXTENSIONS = ('.pdf',)
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp')
DOCX_EXTENSIONS = ('.docx', '.doc')

# Tool definitions for the main window - matching HTML prototype order
TOOLS = [
    # Row 1
    {"id": "ocr", "name": "OCR", "desc": "Genkend tekst", "icon": "📝", "enabled": True},
    {"id": "merge", "name": "Merge", "desc": "Kombiner filer", "icon": "📎", "enabled": True},
    {"id": "split", "name": "Split", "desc": "Opdel sider", "icon": "✂️", "enabled": True},
    {"id": "compress", "name": "Compress", "desc": "Komprimér", "icon": "📦", "enabled": True},
    # Row 2
    {"id": "remove", "name": "Fjern", "desc": "Fjern sider", "icon": "🗑️", "enabled": False},
    {"id": "rotate", "name": "Rotér", "desc": "Rotér sider", "icon": "🔄", "enabled": False},
    {"id": "protect", "name": "Kryptér", "desc": "Password", "icon": "🔒", "enabled": False},
    {"id": "settings", "name": "Indstil.", "desc": "Opsætning", "icon": "⚙️", "enabled": True},
]

# Color theme - METROPOLIS ART DECO
# Reference: DESIGN-AGENT.md for complete specification
COLORS = {
    # Backgrounds
    "bg_dark": "#0D1A1A",       # Dyb mørk teal - primær baggrund
    "bg_deep": "#122424",       # Mellem baggrund
    "bg_mid": "#1A3333",        # Lysere baggrund-accent
    
    # Primary teal colors
    "teal": "#2D5A5A",          # Primær teal - borders, linjer
    "teal_light": "#4A8080",    # Hover states
    
    # Mint accent
    "mint": "#7FBFB5",          # Sekundær tekst, accenter
    "mint_light": "#A8D8D0",    # Highlights
    
    # Gold accent (PRIMARY)
    "gold": "#D4A84B",          # PRIMÆR ACCENT - titler, hover
    "gold_bright": "#E8C547",   # Aktive states, glow
    "gold_dark": "#B8923A",     # Pressed states
    
    # Text
    "text_primary": "#E8E4D9",  # Primær tekst (cream)
    "text_secondary": "#7FBFB5", # Sekundær tekst (mint)
    "text_muted": "#4A8080",    # Muted tekst
    
    # Status
    "success": "#7FBFB5",       # Mint
    "warning": "#D4A84B",       # Gold
    "error": "#C45C5C",         # Red accent
}

# Default settings
DEFAULTS = {
    "ocr_language": "dan",
    "ocr_dpi": 300,
    "compression_level": "balanced",
}
