"""
PDF Toolkit - Main Application Entry Point
==========================================

A simple, fast PDF manipulation tool with Danish language support.

Usage:
    python src/main.py
"""

import sys

from PyQt6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.ui.styles import get_stylesheet


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Consistent cross-platform look
    app.setStyleSheet(get_stylesheet())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
