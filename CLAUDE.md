# PDF Toolkit - Projektkontext

> **Version:** 1.1.0 (Fase 5 færdig, Fase 6 i gang)
> **Sprog:** Dansk UI, Engelsk kodebase
> **Platform:** Windows (primær), cross-platform kompatibel
> **Status:** Feature-complete, mangler tests og distribution

---

## Stack

- **UI:** PyQt6 + Art Deco / Metropolis-tema
- **PDF:** PyMuPDF (fitz), pypdf
- **OCR:** Tesseract + pytesseract + pdf2image
- **Billeder:** Pillow
- **Build:** PyInstaller
- **Eksternt:** Tesseract OCR (dansk sprogpakke), Poppler (Windows)

## Projektstruktur

```
src/
  main.py                    # Entry point
  ui/
    main_window.py           # Hovedvindue, responsivt grid
    styles.py                # QSS Art Deco tema
    icons.py                 # SVG ikoner med pixmap-cache
    widgets/
      tool_tile.py           # Klikbare tool-tiles med animationer
      drop_zone.py           # Drag & drop zone
      file_list.py           # Fil-liste med inline kontroller
      progress.py            # Progress-indikator
    dialogs/
      ocr_dialog.py          # OCR-indstillinger og kørsel
      merge_dialog.py        # Kombiner PDFs
      split_dialog.py        # Opdel PDF (4 modes)
      compress_dialog.py     # Komprimér med niveau-valg
      rotate_dialog.py       # Rotér sider
      remove_dialog.py       # Fjern sider med thumbnail-preview
      encrypt_dialog.py      # Password-beskyttelse (AES-256)
      citation_dialog.py     # Udtræk referencer (BibTeX/JSON)
      convert_dialog.py      # DOCX til PDF
      settings_dialog.py     # App-indstillinger
  core/
    pdf_handler.py           # Basis PDF-operationer
    merger.py                # Merge med progress callback
    splitter.py              # Split (single/ranges/equal/extract)
    ocr_engine.py            # Tesseract-integration
    compressor.py            # Komprimering (3 niveauer)
    page_ops.py              # Rotér/fjern/udtræk sider
    encryption.py            # Kryptér/dekryptér
    citation_extractor.py    # Metadata-udtræk fra akademiske PDFs
    converter.py             # DOCX til PDF
    utils.py                 # Hjælpefunktioner
  config/
    constants.py             # 9 tool-definitioner, farver
    settings.py              # QSettings-baseret persistens
```

## Kode Konventioner

- **Sprog:** Engelsk i kode, dansk i UI-tekst
- **Formattering:** Black, 88 chars
- **Type hints:** Overalt
- **Docstrings:** Google style
- **UI pattern:** QThread workers med progress/finished/error signals
- **Resultater:** Dataclasses (CompressionResult, SplitResult, etc.)
- **Enums:** SplitMode, CompressionLevel, OCRLanguage, RotationAngle

## Design-regler

Se `.claude/DESIGN-AGENT.md` for farvepalette, typografi og komponent-specs.
Se `.claude/ICONS-AGENT.md` for SVG-ikoner.

Kort opsummering:
- **Tema:** Metropolis Art Deco (mork teal baggrund, guld/mint accenter)
- **Farver:** BG `#0D1A1A`, Teal `#2D5A5A`, Mint `#7FBFB5`, Guld `#D4A84B`
- **Fonte:** Bebas Neue (titler), Rajdhani (brodtekst)
- **Ikoner:** SVG med guld stroke, mint fill - ALDRIG emojis i UI
- **Tiles:** Expand i grid, lift-animation pa hover, mint-linje og guld-border

## Kommandoer

```bash
# Kor app
python run_app.py

# Tests
pytest tests/

# Byg executable
pyinstaller build.spec
```

## Naste skridt

Se `TODO.md` for komplet opgaveliste. Prioritet:
1. Unit tests for core-moduler
2. PyInstaller build setup
3. Test pa ren Windows-installation
