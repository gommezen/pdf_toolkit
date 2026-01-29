"""
PDF Toolkit - Project Setup Script
-----------------------------------
Run this script to create the full project structure.

Usage:
    python setup_project.py
"""

import os
from pathlib import Path

# Project structure definition
STRUCTURE = {
    "src": {
        "__init__.py": "",
        "main.py": "# Entry point - implement main window here",
        "ui": {
            "__init__.py": "",
            "main_window.py": "# Main application window",
            "styles.py": "# QSS stylesheets",
            "widgets": {
                "__init__.py": "",
                "drop_zone.py": "# Drag & drop file widget",
                "file_list.py": "# File list with preview",
                "progress.py": "# Progress indicators",
                "tool_tile.py": "# Clickable tool buttons",
            },
            "dialogs": {
                "__init__.py": "",
                "ocr_dialog.py": "# OCR settings dialog",
                "merge_dialog.py": "# Merge PDFs dialog",
                "split_dialog.py": "# Split PDF dialog",
                "compress_dialog.py": "# Compression dialog",
                "settings_dialog.py": "# App settings dialog",
            },
        },
        "core": {
            "__init__.py": "",
            "pdf_handler.py": "# Basic PDF operations",
            "ocr_engine.py": "# Tesseract OCR integration",
            "compressor.py": "# PDF compression",
            "merger.py": "# PDF merge functionality",
            "splitter.py": "# PDF split functionality",
            "utils.py": "# Helper functions",
        },
        "config": {
            "__init__.py": "",
            "settings.py": "# App settings management",
            "constants.py": "# Constants and defaults",
        },
        "resources": {
            "icons": {".gitkeep": ""},
            "translations": {".gitkeep": ""},
            "styles": {".gitkeep": ""},
        },
    },
    "tests": {
        "__init__.py": "",
        "test_ocr.py": "# OCR tests",
        "test_merger.py": "# Merger tests",
        "test_splitter.py": "# Splitter tests",
        "test_compressor.py": "# Compressor tests",
    },
    "dist": {".gitkeep": ""},
}


def create_structure(base_path: Path, structure: dict):
    """Recursively create directory structure."""
    for name, content in structure.items():
        path = base_path / name
        
        if isinstance(content, dict):
            # It's a directory
            path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created: {path}")
            create_structure(path, content)
        else:
            # It's a file
            if not path.exists():
                path.write_text(content, encoding="utf-8")
                print(f"📄 Created: {path}")
            else:
                print(f"⏭️  Exists:  {path}")


def main():
    print("=" * 50)
    print("PDF Toolkit - Project Setup")
    print("=" * 50)
    print()
    
    base_path = Path(__file__).parent
    print(f"Base path: {base_path}")
    print()
    
    create_structure(base_path, STRUCTURE)
    
    print()
    print("=" * 50)
    print("✅ Project structure created!")
    print()
    print("Next steps:")
    print("  1. Create virtual environment: python -m venv venv")
    print("  2. Activate: .\\venv\\Scripts\\Activate")
    print("  3. Install deps: pip install -r requirements.txt")
    print("  4. Start coding: open src/main.py")
    print("=" * 50)


if __name__ == "__main__":
    main()
