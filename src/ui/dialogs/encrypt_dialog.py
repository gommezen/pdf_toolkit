"""
Encryption/Password protection dialog.
"""

import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QGroupBox,
    QLineEdit, QProgressBar, QCheckBox, QTabWidget,
    QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from src.core.encryption import (
    encrypt_pdf, decrypt_pdf, is_pdf_encrypted,
    EncryptionResult, PERM_PRINT, PERM_MODIFY, PERM_COPY, PERM_ANNOTATE
)


class EncryptWorker(QThread):
    """Background worker for encryption."""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, input_path: str, output_path: str,
                 user_pw: str, owner_pw: str, permissions: int):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.user_pw = user_pw
        self.owner_pw = owner_pw
        self.permissions = permissions

    def run(self):
        try:
            result = encrypt_pdf(
                self.input_path,
                self.output_path,
                self.user_pw,
                self.owner_pw,
                self.permissions,
                self._on_progress
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

    def _on_progress(self, percent: int, message: str):
        self.progress.emit(percent, message)


class DecryptWorker(QThread):
    """Background worker for decryption."""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, input_path: str, output_path: str, password: str):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.password = password

    def run(self):
        try:
            result = decrypt_pdf(
                self.input_path,
                self.output_path,
                self.password,
                self._on_progress
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

    def _on_progress(self, percent: int, message: str):
        self.progress.emit(percent, message)


class EncryptDialog(QDialog):
    """Dialog for PDF encryption/decryption."""

    def __init__(self, files: list[str], parent=None):
        super().__init__(parent)
        self.files = files
        self.worker = None
        self._setup_ui()
        self._check_encryption_status()

    def _setup_ui(self):
        """Initialize dialog UI."""
        self.setWindowTitle("Kryptér / Fjern Password")
        self.setMinimumSize(500, 450)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # File info
        file_name = Path(self.files[0]).name
        file_label = QLabel(f"Fil: {file_name}")
        file_label.setStyleSheet("color: #D4A84B; font-size: 14px; font-weight: bold;")
        layout.addWidget(file_label)

        # Status label
        self.status_label = QLabel("Kontrollerer fil...")
        self.status_label.setStyleSheet("color: #7FBFB5;")
        layout.addWidget(self.status_label)

        # Tab widget for encrypt/decrypt
        self.tabs = QTabWidget()

        # Encrypt tab
        encrypt_tab = QWidget()
        encrypt_layout = QVBoxLayout(encrypt_tab)

        # User password (to open)
        user_group = QGroupBox("Åbnings-password (valgfrit)")
        user_layout = QVBoxLayout(user_group)
        user_layout.addWidget(QLabel("Password for at åbne dokumentet:"))
        self.edit_user_pw = QLineEdit()
        self.edit_user_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.edit_user_pw.setPlaceholderText("Efterlad tomt hvis ingen åbnings-password")
        user_layout.addWidget(self.edit_user_pw)
        encrypt_layout.addWidget(user_group)

        # Owner password
        owner_group = QGroupBox("Ejer-password (påkrævet)")
        owner_layout = QVBoxLayout(owner_group)
        owner_layout.addWidget(QLabel("Password for fuld adgang:"))
        self.edit_owner_pw = QLineEdit()
        self.edit_owner_pw.setEchoMode(QLineEdit.EchoMode.Password)
        owner_layout.addWidget(self.edit_owner_pw)

        owner_layout.addWidget(QLabel("Bekræft password:"))
        self.edit_owner_pw2 = QLineEdit()
        self.edit_owner_pw2.setEchoMode(QLineEdit.EchoMode.Password)
        owner_layout.addWidget(self.edit_owner_pw2)
        encrypt_layout.addWidget(owner_group)

        # Permissions
        perm_group = QGroupBox("Tilladelser")
        perm_layout = QVBoxLayout(perm_group)

        self.check_print = QCheckBox("Tillad print")
        self.check_print.setChecked(True)
        perm_layout.addWidget(self.check_print)

        self.check_copy = QCheckBox("Tillad kopiering af tekst")
        self.check_copy.setChecked(True)
        perm_layout.addWidget(self.check_copy)

        self.check_modify = QCheckBox("Tillad redigering")
        self.check_modify.setChecked(False)
        perm_layout.addWidget(self.check_modify)

        self.check_annotate = QCheckBox("Tillad annotationer")
        self.check_annotate.setChecked(True)
        perm_layout.addWidget(self.check_annotate)

        encrypt_layout.addWidget(perm_group)
        encrypt_layout.addStretch()

        self.tabs.addTab(encrypt_tab, "Kryptér")

        # Decrypt tab
        decrypt_tab = QWidget()
        decrypt_layout = QVBoxLayout(decrypt_tab)

        decrypt_layout.addWidget(QLabel("Indtast password for at fjerne kryptering:"))
        self.edit_decrypt_pw = QLineEdit()
        self.edit_decrypt_pw.setEchoMode(QLineEdit.EchoMode.Password)
        decrypt_layout.addWidget(self.edit_decrypt_pw)

        decrypt_layout.addStretch()

        self.tabs.addTab(decrypt_tab, "Fjern Password")

        layout.addWidget(self.tabs)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Annuller")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_start = QPushButton("Udfør")
        self.btn_start.setProperty("class", "action-btn")
        self.btn_start.clicked.connect(self._start_operation)
        btn_layout.addWidget(self.btn_start)

        layout.addLayout(btn_layout)

    def _check_encryption_status(self):
        """Check if the PDF is already encrypted."""
        is_encrypted, needs_pw = is_pdf_encrypted(self.files[0])

        if is_encrypted:
            self.status_label.setText("🔒 PDF'en er krypteret")
            self.status_label.setStyleSheet("color: #f59e0b;")
            self.tabs.setCurrentIndex(1)  # Switch to decrypt tab
        else:
            self.status_label.setText("🔓 PDF'en er ikke krypteret")
            self.status_label.setStyleSheet("color: #22c55e;")
            self.tabs.setCurrentIndex(0)  # Encrypt tab

    def _get_permissions(self) -> int:
        """Get permission flags based on checkboxes."""
        perms = 0
        if self.check_print.isChecked():
            perms |= PERM_PRINT
        if self.check_copy.isChecked():
            perms |= PERM_COPY
        if self.check_modify.isChecked():
            perms |= PERM_MODIFY
        if self.check_annotate.isChecked():
            perms |= PERM_ANNOTATE
        return perms

    def _start_operation(self):
        """Start encrypt or decrypt based on current tab."""
        if self.tabs.currentIndex() == 0:
            self._start_encryption()
        else:
            self._start_decryption()

    def _start_encryption(self):
        """Start encryption."""
        owner_pw = self.edit_owner_pw.text()
        owner_pw2 = self.edit_owner_pw2.text()
        user_pw = self.edit_user_pw.text()

        if not owner_pw:
            QMessageBox.warning(self, "Mangler password", "Ejer-password er påkrævet.")
            return

        if owner_pw != owner_pw2:
            QMessageBox.warning(self, "Password matcher ikke", "Ejer-passwords matcher ikke.")
            return

        if len(owner_pw) < 4:
            QMessageBox.warning(self, "Password for kort", "Password skal være mindst 4 tegn.")
            return

        input_path = self.files[0]
        output_dir = Path(input_path).parent
        input_name = Path(input_path).stem
        output_path = str(output_dir / f"{input_name}_encrypted.pdf")

        if os.path.exists(output_path):
            reply = QMessageBox.question(
                self, "Fil eksisterer",
                f"Filen eksisterer allerede. Overskriv?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self._disable_ui()

        permissions = self._get_permissions()
        self.worker = EncryptWorker(input_path, output_path, user_pw, owner_pw, permissions)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _start_decryption(self):
        """Start decryption."""
        password = self.edit_decrypt_pw.text()

        if not password:
            QMessageBox.warning(self, "Mangler password", "Indtast password for at fjerne kryptering.")
            return

        input_path = self.files[0]
        output_dir = Path(input_path).parent
        input_name = Path(input_path).stem
        output_path = str(output_dir / f"{input_name}_decrypted.pdf")

        if os.path.exists(output_path):
            reply = QMessageBox.question(
                self, "Fil eksisterer",
                f"Filen eksisterer allerede. Overskriv?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self._disable_ui()

        self.worker = DecryptWorker(input_path, output_path, password)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _disable_ui(self):
        """Disable UI during operation."""
        self.btn_start.setEnabled(False)
        self.tabs.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setVisible(True)

    def _on_progress(self, percent: int, message: str):
        self.progress_bar.setValue(percent)
        self.progress_label.setText(message)

    def _on_finished(self, result: EncryptionResult):
        self.worker = None
        if result.success:
            action = "krypteret" if self.tabs.currentIndex() == 0 else "dekrypteret"
            QMessageBox.information(
                self, "Færdig",
                f"PDF {action}!\n"
                f"Gemt som: {result.output_path.name}"
            )
            self.accept()
        else:
            QMessageBox.warning(self, "Fejl", result.error_message)
            self._reset_ui()

    def _on_error(self, message: str):
        self.worker = None
        QMessageBox.critical(self, "Fejl", message)
        self._reset_ui()

    def _reset_ui(self):
        self.btn_start.setEnabled(True)
        self.tabs.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
