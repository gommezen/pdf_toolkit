"""
PDF encryption and password protection.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import fitz  # PyMuPDF


@dataclass
class EncryptionResult:
    """Result of an encryption operation."""
    output_path: Path
    success: bool
    error_message: str = ""


# Permission flags for PDF
PERM_PRINT = fitz.PDF_PERM_PRINT
PERM_MODIFY = fitz.PDF_PERM_MODIFY
PERM_COPY = fitz.PDF_PERM_COPY
PERM_ANNOTATE = fitz.PDF_PERM_ANNOTATE
PERM_ALL = PERM_PRINT | PERM_MODIFY | PERM_COPY | PERM_ANNOTATE


def encrypt_pdf(
    input_path: str,
    output_path: str,
    user_password: str = "",
    owner_password: str = "",
    permissions: int = PERM_ALL,
    progress_callback: Callable[[int, str], None] | None = None
) -> EncryptionResult:
    """
    Encrypt a PDF with password protection.

    Args:
        input_path: Path to input PDF
        output_path: Path for encrypted output
        user_password: Password to open the document (empty = no password to open)
        owner_password: Password for full access (required)
        permissions: Permission flags (use PERM_* constants)
        progress_callback: Optional callback(percent, message)

    Returns:
        EncryptionResult with operation info
    """
    try:
        if not owner_password:
            return EncryptionResult(
                output_path=Path(output_path),
                success=False,
                error_message="Owner password er påkrævet"
            )

        if progress_callback:
            progress_callback(10, "Åbner PDF...")

        doc = fitz.open(input_path)

        if progress_callback:
            progress_callback(50, "Krypterer dokument...")

        # Set encryption
        encrypt_dict = {
            "owner": owner_password,
            "user": user_password,
            "encryption": fitz.PDF_ENCRYPT_AES_256,  # Strong encryption
            "permissions": permissions,
        }

        if progress_callback:
            progress_callback(80, "Gemmer krypteret fil...")

        doc.save(
            output_path,
            encryption=fitz.PDF_ENCRYPT_AES_256,
            owner_pw=owner_password,
            user_pw=user_password,
            permissions=permissions,
            garbage=4,
            deflate=True
        )
        doc.close()

        if progress_callback:
            progress_callback(100, "Færdig!")

        return EncryptionResult(
            output_path=Path(output_path),
            success=True
        )

    except Exception as e:
        return EncryptionResult(
            output_path=Path(output_path),
            success=False,
            error_message=str(e)
        )


def decrypt_pdf(
    input_path: str,
    output_path: str,
    password: str,
    progress_callback: Callable[[int, str], None] | None = None
) -> EncryptionResult:
    """
    Remove encryption from a PDF.

    Args:
        input_path: Path to encrypted PDF
        output_path: Path for decrypted output
        password: Password to unlock the PDF
        progress_callback: Optional callback(percent, message)

    Returns:
        EncryptionResult with operation info
    """
    try:
        if progress_callback:
            progress_callback(10, "Åbner krypteret PDF...")

        doc = fitz.open(input_path)

        # Check if PDF is encrypted
        if not doc.is_encrypted:
            doc.close()
            return EncryptionResult(
                output_path=Path(output_path),
                success=False,
                error_message="PDF'en er ikke krypteret"
            )

        if progress_callback:
            progress_callback(30, "Forsøger at låse op...")

        # Try to authenticate
        if not doc.authenticate(password):
            doc.close()
            return EncryptionResult(
                output_path=Path(output_path),
                success=False,
                error_message="Forkert password"
            )

        if progress_callback:
            progress_callback(60, "Fjerner kryptering...")

        # Save without encryption
        if progress_callback:
            progress_callback(80, "Gemmer ukrypteret fil...")

        doc.save(output_path, garbage=4, deflate=True)
        doc.close()

        if progress_callback:
            progress_callback(100, "Færdig!")

        return EncryptionResult(
            output_path=Path(output_path),
            success=True
        )

    except Exception as e:
        return EncryptionResult(
            output_path=Path(output_path),
            success=False,
            error_message=str(e)
        )


def is_pdf_encrypted(pdf_path: str) -> tuple[bool, bool]:
    """
    Check if a PDF is encrypted.

    Returns:
        Tuple of (is_encrypted, needs_password_to_open)
    """
    try:
        doc = fitz.open(pdf_path)
        is_encrypted = doc.is_encrypted
        needs_password = doc.needs_pass
        doc.close()
        return is_encrypted, needs_password
    except Exception:
        return False, False
