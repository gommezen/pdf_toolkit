"""
Citation extraction dialog for extracting bibliographic metadata from PDFs.
Supports export to BibTeX and CSL-JSON formats.
"""

import webbrowser
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QGroupBox,
    QRadioButton, QTextEdit, QMessageBox, QFrame,
    QScrollArea, QWidget, QApplication, QButtonGroup
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from src.core.citation_extractor import (
    extract_citation, to_bibtex, to_json,
    CitationResult, CitationMetadata
)


class ExtractWorker(QThread):
    """Background worker for citation extraction."""

    finished = pyqtSignal(object)  # CitationResult
    error = pyqtSignal(str)

    def __init__(self, pdf_path: str):
        super().__init__()
        self.pdf_path = pdf_path

    def run(self):
        """Execute extraction in background thread."""
        try:
            result = extract_citation(self.pdf_path)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class CitationDialog(QDialog):
    """Dialog for extracting and exporting citation metadata."""

    def __init__(self, files: list[str], parent=None):
        super().__init__(parent)
        self.files = files
        self.worker = None
        self.result: CitationResult | None = None
        self._setup_ui()
        self._start_extraction()

    def _setup_ui(self):
        """Initialize dialog UI."""
        self.setWindowTitle("Citationsudtræk")
        self.setMinimumSize(550, 600)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # File info
        file_name = Path(self.files[0]).name
        file_label = QLabel(f"Fil: {file_name}")
        file_label.setStyleSheet("color: #D4A84B; font-size: 14px; font-weight: bold;")
        layout.addWidget(file_label)

        # Loading indicator (shown during extraction)
        self.loading_label = QLabel("Udtrækker metadata...")
        self.loading_label.setStyleSheet("color: #7FBFB5; font-style: italic;")
        layout.addWidget(self.loading_label)

        # Metadata section
        self.metadata_group = QGroupBox("METADATA")
        self.metadata_group.setVisible(False)
        metadata_layout = QVBoxLayout(self.metadata_group)
        metadata_layout.setSpacing(8)

        # Title
        title_row = QHBoxLayout()
        title_row.addWidget(self._create_field_label("Titel:"))
        self.title_value = QLabel("")
        self.title_value.setWordWrap(True)
        self.title_value.setStyleSheet("color: #E8E4D9;")
        title_row.addWidget(self.title_value, 1)
        metadata_layout.addLayout(title_row)

        # Authors
        authors_row = QHBoxLayout()
        authors_row.addWidget(self._create_field_label("Forfattere:"))
        self.authors_value = QLabel("")
        self.authors_value.setWordWrap(True)
        self.authors_value.setStyleSheet("color: #E8E4D9;")
        authors_row.addWidget(self.authors_value, 1)
        metadata_layout.addLayout(authors_row)

        # Year
        year_row = QHBoxLayout()
        year_row.addWidget(self._create_field_label("År:"))
        self.year_value = QLabel("")
        self.year_value.setStyleSheet("color: #E8E4D9;")
        year_row.addWidget(self.year_value, 1)
        metadata_layout.addLayout(year_row)

        # DOI with link
        doi_row = QHBoxLayout()
        doi_row.addWidget(self._create_field_label("DOI:"))
        self.doi_value = QLabel("")
        self.doi_value.setStyleSheet("color: #E8E4D9;")
        doi_row.addWidget(self.doi_value, 1)
        self.btn_open_doi = QPushButton("Åbn i browser")
        self.btn_open_doi.setVisible(False)
        self.btn_open_doi.clicked.connect(self._open_doi)
        self.btn_open_doi.setStyleSheet("font-size: 11px; padding: 2px 8px;")
        doi_row.addWidget(self.btn_open_doi)
        metadata_layout.addLayout(doi_row)

        # Journal
        journal_row = QHBoxLayout()
        journal_row.addWidget(self._create_field_label("Journal:"))
        self.journal_value = QLabel("")
        self.journal_value.setWordWrap(True)
        self.journal_value.setStyleSheet("color: #E8E4D9;")
        journal_row.addWidget(self.journal_value, 1)
        metadata_layout.addLayout(journal_row)

        layout.addWidget(self.metadata_group)

        # Abstract section
        self.abstract_group = QGroupBox("ABSTRACT")
        self.abstract_group.setVisible(False)
        abstract_layout = QVBoxLayout(self.abstract_group)

        self.abstract_text = QTextEdit()
        self.abstract_text.setReadOnly(True)
        self.abstract_text.setMaximumHeight(120)
        self.abstract_text.setStyleSheet("""
            QTextEdit {
                background-color: #1A3333;
                border: 1px solid #2D5A5A;
                border-radius: 4px;
                color: #E8E4D9;
                padding: 8px;
            }
        """)
        abstract_layout.addWidget(self.abstract_text)

        layout.addWidget(self.abstract_group)

        # Warnings section
        self.warnings_frame = QFrame()
        self.warnings_frame.setVisible(False)
        self.warnings_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(212, 168, 75, 0.1);
                border: 1px solid #D4A84B;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        warnings_layout = QVBoxLayout(self.warnings_frame)
        warnings_layout.setContentsMargins(10, 8, 10, 8)
        self.warnings_label = QLabel("")
        self.warnings_label.setWordWrap(True)
        self.warnings_label.setStyleSheet("color: #D4A84B; font-size: 12px;")
        warnings_layout.addWidget(self.warnings_label)
        layout.addWidget(self.warnings_frame)

        # Export section
        self.export_group = QGroupBox("EKSPORT")
        self.export_group.setVisible(False)
        export_layout = QVBoxLayout(self.export_group)

        # Format selector
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))

        self.format_group = QButtonGroup(self)
        self.radio_bibtex = QRadioButton("BibTeX")
        self.radio_bibtex.setChecked(True)
        self.radio_bibtex.toggled.connect(self._update_preview)
        self.format_group.addButton(self.radio_bibtex)
        format_layout.addWidget(self.radio_bibtex)

        self.radio_json = QRadioButton("JSON (Zotero)")
        self.radio_json.toggled.connect(self._update_preview)
        self.format_group.addButton(self.radio_json)
        format_layout.addWidget(self.radio_json)

        format_layout.addStretch()
        export_layout.addLayout(format_layout)

        # Preview
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Consolas", 10))
        self.preview_text.setMinimumHeight(150)
        self.preview_text.setStyleSheet("""
            QTextEdit {
                background-color: #0D1A1A;
                border: 1px solid #2D5A5A;
                border-radius: 4px;
                color: #7FBFB5;
                padding: 8px;
            }
        """)
        export_layout.addWidget(self.preview_text)

        layout.addWidget(self.export_group)

        # Spacer
        layout.addStretch()

        # Confidence indicator
        self.confidence_label = QLabel("")
        self.confidence_label.setStyleSheet("color: #7FBFB5; font-size: 11px;")
        layout.addWidget(self.confidence_label)

        # Action buttons
        btn_layout = QHBoxLayout()

        self.btn_copy = QPushButton("Kopiér")
        self.btn_copy.setEnabled(False)
        self.btn_copy.clicked.connect(self._copy_to_clipboard)
        btn_layout.addWidget(self.btn_copy)

        self.btn_save = QPushButton("Gem fil...")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self._save_to_file)
        btn_layout.addWidget(self.btn_save)

        btn_layout.addStretch()

        self.btn_close = QPushButton("Luk")
        self.btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

    def _create_field_label(self, text: str) -> QLabel:
        """Create a styled field label."""
        label = QLabel(text)
        label.setStyleSheet("color: #7FBFB5; font-weight: bold;")
        label.setMinimumWidth(80)
        return label

    def _start_extraction(self):
        """Start metadata extraction in background."""
        self.worker = ExtractWorker(self.files[0])
        self.worker.finished.connect(self._on_extraction_finished)
        self.worker.error.connect(self._on_extraction_error)
        self.worker.start()

    def _on_extraction_finished(self, result: CitationResult):
        """Handle extraction completion."""
        self.worker = None
        self.result = result
        self.loading_label.setVisible(False)

        if not result.success:
            QMessageBox.warning(
                self,
                "Udtræk fejlede",
                f"Kunne ikke udtrække metadata:\n{result.error_message}"
            )
            return

        metadata = result.metadata

        # Show metadata section
        self.metadata_group.setVisible(True)

        # Populate fields
        self.title_value.setText(metadata.title or "(ikke fundet)")
        self.authors_value.setText(metadata.author_string or "(ikke fundet)")
        self.year_value.setText(str(metadata.year) if metadata.year else "(ikke fundet)")

        if metadata.doi:
            self.doi_value.setText(metadata.doi)
            self.btn_open_doi.setVisible(True)
        else:
            self.doi_value.setText("(ikke fundet)")

        self.journal_value.setText(metadata.journal or "(ikke angivet)")

        # Abstract
        if metadata.abstract:
            self.abstract_group.setVisible(True)
            self.abstract_text.setText(metadata.abstract)

        # Warnings
        if result.warnings:
            self.warnings_frame.setVisible(True)
            self.warnings_label.setText("⚠ " + "\n⚠ ".join(result.warnings))

        # Confidence
        confidence_pct = int(result.confidence * 100)
        confidence_text = "Høj" if confidence_pct >= 70 else "Medium" if confidence_pct >= 40 else "Lav"
        self.confidence_label.setText(f"Konfidens: {confidence_text} ({confidence_pct}%)")

        # Enable export
        self.export_group.setVisible(True)
        self.btn_copy.setEnabled(True)
        self.btn_save.setEnabled(True)

        # Update preview
        self._update_preview()

    def _on_extraction_error(self, message: str):
        """Handle extraction error."""
        self.worker = None
        self.loading_label.setVisible(False)
        QMessageBox.critical(
            self,
            "Fejl",
            f"En fejl opstod under udtræk:\n{message}"
        )

    def _update_preview(self):
        """Update the export preview based on selected format."""
        if not self.result or not self.result.metadata:
            return

        if self.radio_bibtex.isChecked():
            output = to_bibtex(self.result.metadata)
        else:
            output = to_json(self.result.metadata)

        self.preview_text.setText(output)

    def _get_current_output(self) -> str:
        """Get the current formatted output."""
        return self.preview_text.toPlainText()

    def _copy_to_clipboard(self):
        """Copy formatted output to clipboard."""
        output = self._get_current_output()
        if output:
            clipboard = QApplication.clipboard()
            clipboard.setText(output)

            # Show feedback
            original_text = self.btn_copy.text()
            self.btn_copy.setText("Kopieret!")
            self.btn_copy.setEnabled(False)

            # Reset button after delay
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1500, lambda: self._reset_copy_button(original_text))

    def _reset_copy_button(self, text: str):
        """Reset copy button to original state."""
        self.btn_copy.setText(text)
        self.btn_copy.setEnabled(True)

    def _save_to_file(self):
        """Save formatted output to file."""
        output = self._get_current_output()
        if not output:
            return

        # Determine extension and filter
        if self.radio_bibtex.isChecked():
            default_ext = ".bib"
            file_filter = "BibTeX filer (*.bib);;Alle filer (*.*)"
        else:
            default_ext = ".json"
            file_filter = "JSON filer (*.json);;Alle filer (*.*)"

        # Default filename based on source
        source_stem = Path(self.files[0]).stem
        default_name = f"{source_stem}_citation{default_ext}"
        default_path = Path(self.files[0]).parent / default_name

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Gem citation",
            str(default_path),
            file_filter
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(output)

                QMessageBox.information(
                    self,
                    "Gemt",
                    f"Citation gemt til:\n{Path(file_path).name}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Fejl",
                    f"Kunne ikke gemme fil:\n{str(e)}"
                )

    def _open_doi(self):
        """Open DOI in web browser."""
        if self.result and self.result.metadata.doi:
            doi = self.result.metadata.doi
            # Ensure it's a full URL
            if not doi.startswith("http"):
                doi = f"https://doi.org/{doi}"
            webbrowser.open(doi)

    def closeEvent(self, event):
        """Handle dialog close."""
        if self.worker and self.worker.isRunning():
            self.worker.wait(1000)
        event.accept()
