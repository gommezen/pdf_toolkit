"""
Progress indicator widgets for long-running operations.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QProgressBar, QLabel, QPushButton
)
from PyQt6.QtCore import pyqtSignal


class ProgressWidget(QWidget):
    """
    Widget showing operation progress with status text and cancel button.
    """

    cancelled = pyqtSignal()  # Emits when cancel button is clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Status label
        self.status_label = QLabel("Klar")
        self.status_label.setStyleSheet("color: #475569;")
        layout.addWidget(self.status_label)

        # Progress bar row
        progress_layout = QHBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        self.cancel_btn = QPushButton("Annuller")
        self.cancel_btn.setProperty("class", "secondary-btn")
        self.cancel_btn.clicked.connect(self._on_cancel)
        self.cancel_btn.setEnabled(False)
        progress_layout.addWidget(self.cancel_btn)

        layout.addLayout(progress_layout)

    def _on_cancel(self):
        """Handle cancel button click."""
        self.cancelled.emit()

    def set_progress(self, percent: int, message: str = ""):
        """
        Update progress bar and status message.

        Args:
            percent: Progress percentage (0-100)
            message: Status message to display
        """
        self.progress_bar.setValue(percent)
        if message:
            self.status_label.setText(message)

    def set_indeterminate(self, message: str = "Arbejder..."):
        """
        Set progress bar to indeterminate (spinning) mode.

        Args:
            message: Status message to display
        """
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Indeterminate mode
        self.status_label.setText(message)

    def set_determinate(self):
        """Switch back to determinate progress mode."""
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)

    def start(self, message: str = "Starter..."):
        """
        Start progress indication.

        Args:
            message: Initial status message
        """
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(message)

    def finish(self, message: str = "Færdig"):
        """
        Complete progress indication.

        Args:
            message: Completion message
        """
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setValue(100)
        self.status_label.setText(message)

    def reset(self):
        """Reset progress widget to initial state."""
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.set_determinate()
        self.status_label.setText("Klar")

    def set_error(self, message: str):
        """
        Show error state.

        Args:
            message: Error message to display
        """
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Fejl: {message}")
        self.status_label.setStyleSheet("color: #ef4444;")

    def clear_error(self):
        """Clear error state."""
        self.status_label.setStyleSheet("color: #475569;")
