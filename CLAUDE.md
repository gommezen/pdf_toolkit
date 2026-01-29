# PDF Toolkit - Produktionsplan

> **Projektnavn:** PDF Toolkit  
> **Version:** 1.0.0  
> **Sprog:** Dansk UI, Engelsk kodebase  
> **Platform:** Windows (primær), cross-platform kompatibel

---

## 🎯 Projektoversigt

### Vision
En simpel, hurtig og brugervenlig desktop-applikation til PDF-manipulation med fokus på:
- OCR/tekstgenkendelse (særligt optimeret til dansk)
- Merge, split, og sidehåndtering
- Komprimering
- Lokal processing (ingen cloud upload)

### Inspiration
Inspireret af PDF24, men med forbedringer:
- Unified interface (ikke separate moduler)
- Logisk gruppering af funktioner
- Moderne, clean UI
- Bedre dansk sprogunderstøttelse

---

## 🏗️ Teknisk Arkitektur

### Stack
```
┌─────────────────────────────────────────────────────┐
│                    PDF Toolkit                      │
├─────────────────────────────────────────────────────┤
│  UI Layer          │  PyQt6                         │
│  PDF Processing    │  PyMuPDF (fitz)                │
│  OCR Engine        │  Tesseract + pytesseract       │
│  Image Processing  │  Pillow, pdf2image             │
│  Packaging         │  PyInstaller                   │
└─────────────────────────────────────────────────────┘
```

### Krav til Dependencies
```
# requirements.txt
PyQt6>=6.6.0
PyMuPDF>=1.23.0
pytesseract>=0.3.10
pdf2image>=1.16.0
Pillow>=10.0.0
```

### Eksterne Dependencies (skal installeres separat)
- **Tesseract OCR** med dansk sprogpakke (`tesseract-ocr-dan`)
- **Poppler** (til pdf2image på Windows)

---

## 📁 Projektstruktur

```
pdf-toolkit/
├── CLAUDE.md                 # Denne fil - projektkontext
├── README.md                 # Bruger-dokumentation
├── requirements.txt          # Python dependencies
├── setup.py                  # Installation script
├── build.spec                # PyInstaller spec fil
│
├── src/
│   ├── __init__.py
│   ├── main.py               # Application entry point
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py    # Hovedvindue med tool-tiles
│   │   ├── styles.py         # QSS stylesheets
│   │   ├── widgets/
│   │   │   ├── __init__.py
│   │   │   ├── drop_zone.py  # Drag & drop widget
│   │   │   ├── file_list.py  # Fil-liste med preview
│   │   │   ├── progress.py   # Progress indicators
│   │   │   └── tool_tile.py  # Klikbare tool-knapper
│   │   └── dialogs/
│   │       ├── __init__.py
│   │       ├── ocr_dialog.py
│   │       ├── merge_dialog.py
│   │       ├── split_dialog.py
│   │       ├── compress_dialog.py
│   │       └── settings_dialog.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── pdf_handler.py    # Basis PDF operationer
│   │   ├── ocr_engine.py     # OCR processing
│   │   ├── compressor.py     # PDF komprimering
│   │   ├── merger.py         # Merge funktionalitet
│   │   ├── splitter.py       # Split funktionalitet
│   │   └── utils.py          # Hjælpefunktioner
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py       # App settings management
│   │   └── constants.py      # Konstanter og defaults
│   │
│   └── resources/
│       ├── icons/            # App ikoner (SVG/PNG)
│       ├── translations/     # Sprog-filer (da, en)
│       └── styles/           # QSS theme filer
│
├── tests/
│   ├── __init__.py
│   ├── test_ocr.py
│   ├── test_merger.py
│   ├── test_splitter.py
│   └── test_compressor.py
│
└── dist/                     # Build output
    └── PDFToolkit.exe
```

---

## 🎨 UI Design Specifikation

### Hovedvindue Layout
```
┌─────────────────────────────────────────────────────────────┐
│  📄 PDF Toolkit                                    [—][□][×]│
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    VÆRKTØJER                            ││
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   ││
│  │  │  📝 OCR  │ │ 📎 Merge │ │ ✂️ Split │ │📦Compress│   ││
│  │  │ Genkend  │ │ Kombiner │ │  Opdel   │ │Komprimér │   ││
│  │  │  tekst   │ │  filer   │ │  sider   │ │          │   ││
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   ││
│  │                                                         ││
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   ││
│  │  │ 🗑️ Fjern │ │ 🔄 Rotér │ │ 🔒 Krypt │ │ ⚙️ Indst.│   ││
│  │  │  sider   │ │  sider   │ │ Password │ │          │   ││
│  │  │          │ │          │ │          │ │          │   ││
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                                                         ││
│  │     📁 Træk filer hertil eller klik for at vælge       ││
│  │                                                         ││
│  │                    (Drop Zone)                          ││
│  │                                                         ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Valgte filer:                                          ││
│  │  ┌────┬─────────────────────────────┬────────┬───────┐ ││
│  │  │ # │ Filnavn                      │ Sider  │ Størr.│ ││
│  │  ├────┼─────────────────────────────┼────────┼───────┤ ││
│  │  │ 1 │ dokument.pdf                 │ 12     │ 2.4MB │ ││
│  │  │ 2 │ scan_2024.pdf                │ 3      │ 8.1MB │ ││
│  │  └────┴─────────────────────────────┴────────┴───────┘ ││
│  │  [↑ Flyt op] [↓ Flyt ned] [✕ Fjern] [🗑️ Ryd alle]      ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  Status: Klar                                    v1.0.0    │
└─────────────────────────────────────────────────────────────┘
```

### Farvetema (Light Mode)
```css
/* Primary colors */
--primary: #2563eb;        /* Blue - primary actions */
--primary-hover: #1d4ed8;
--secondary: #64748b;      /* Slate - secondary elements */

/* Background */
--bg-main: #ffffff;
--bg-secondary: #f8fafc;
--bg-tile: #f1f5f9;
--bg-tile-hover: #e2e8f0;

/* Text */
--text-primary: #1e293b;
--text-secondary: #64748b;

/* Borders */
--border: #e2e8f0;
--border-focus: #2563eb;

/* Status */
--success: #22c55e;
--warning: #f59e0b;
--error: #ef4444;
```

### Tool Tile Specifikation
```
Størrelse: 120x100 px
Border-radius: 12px
Ikon størrelse: 32x32 px
Font: System default, 13px
Hover: Subtle shadow + background change
Click: Scale down 0.98 + darker background
```

---

## 🔧 Feature Specifikationer

### 1. OCR - Tekstgenkendelse

**Formål:** Konvertér scannet PDF/billede til søgbar PDF med tekstlag.

**Input:**
- PDF (billede-baseret)
- Billeder: PNG, JPG, TIFF, BMP

**Output:**
- PDF med usynligt tekstlag (original udseende bevaret)
- Valgfrit: Kun tekst-udtræk (.txt)

**Indstillinger:**
- Sprog: Dansk (default), Engelsk, Auto-detect
- DPI: 150, 300 (default), 600
- Output kvalitet: Høj, Medium, Lav
- Bevar original vs. kun tekst

**Implementation:**
```python
# Pseudo-kode for OCR flow
def perform_ocr(input_path: str, options: OCROptions) -> str:
    """
    1. Konverter PDF sider til billeder (pdf2image)
    2. Kør Tesseract OCR på hver side
    3. Hent tekst + positioner (bounding boxes)
    4. Opret ny PDF med original billede + usynligt tekstlag
    5. Gem output fil
    """
    pass
```

**Dansk Sprogunderstøttelse:**
- Kræver `tesseract-ocr-dan` installeret
- Fallback til post-processing korrektioner hvis dansk ikke tilgængelig
- Almindelige OCR-fejl mapping: ø→o, æ→ae, å→a (omvendt)

---

### 2. Merge - Kombiner PDFs

**Formål:** Saml flere PDF-filer til én.

**Features:**
- Drag & drop rækkefølge
- Tilføj specifikke sider fra hver fil
- Preview af første side
- Bevar/fjern bookmarks

**Implementation:**
```python
def merge_pdfs(files: list[str], output: str, options: MergeOptions) -> None:
    """
    Brug PyMuPDF til at kombinere PDFs.
    Optioner: behold metadata fra første fil, kombiner bookmarks.
    """
    pass
```

---

### 3. Split - Opdel PDF

**Formål:** Opdel én PDF i flere filer.

**Modes:**
- Split alle sider (én fil per side)
- Split ved specifikke sider (fx "1-3, 5, 8-10")
- Split i lige store dele (fx 3 filer)
- Fjern specifikke sider

**Implementation:**
```python
def split_pdf(input_path: str, mode: SplitMode, options: SplitOptions) -> list[str]:
    """
    Returnerer liste af output fil-stier.
    """
    pass
```

---

### 4. Compress - Komprimér

**Formål:** Reducer PDF filstørrelse.

**Niveauer:**
- **Høj kvalitet:** Minimal komprimering (~10-20% reduktion)
- **Balanceret:** God kvalitet/størrelse trade-off (~40-60%)
- **Maksimal:** Aggressiv komprimering (~70-90%)

**Teknikker:**
- Downsample billeder
- Fjern embedded fonts (erstat med subset)
- Fjern metadata
- Optimér object streams

**Implementation:**
```python
def compress_pdf(input_path: str, level: CompressionLevel) -> CompressionResult:
    """
    Returnerer: output_path, original_size, new_size, ratio
    """
    pass
```

---

### 5. Rotate - Rotér sider

**Formål:** Rotér udvalgte sider.

**Options:**
- Rotér alle sider: 90°, 180°, 270°
- Rotér specifikke sider
- Auto-detect orientation (valgfrit)

---

### 6. Remove Pages - Fjern sider

**Formål:** Fjern uønskede sider fra PDF.

**Interface:**
- Thumbnail preview af alle sider
- Klik for at vælge/fravælge
- Bulk selection (Ctrl+klik, Shift+klik)

---

### 7. Password Protection - Kryptering

**Formål:** Tilføj/fjern password beskyttelse.

**Options:**
- User password (åbne dokument)
- Owner password (redigere/printe)
- Encryption level: AES-128, AES-256

---

## 📋 Implementeringsplan

### Fase 1: Grundlæggende Infrastruktur (Uge 1)
```
□ Opsæt projektstruktur
□ Implementer main.py entry point
□ Opret basis PyQt6 hovedvindue
□ Implementer DropZone widget
□ Implementer FileList widget
□ Opret tool tile komponenter
□ Basis styling (QSS)
```

**Deliverable:** Kørende app med UI, ingen funktionalitet

### Fase 2: Core PDF Funktioner (Uge 2)
```
□ pdf_handler.py - basis operationer
□ merger.py - kombiner PDFs
□ splitter.py - opdel PDFs
□ Integrer med UI dialogs
□ File save/open dialogs
□ Error handling
```

**Deliverable:** Fungerende merge/split

### Fase 3: OCR Implementation (Uge 3)
```
□ ocr_engine.py - Tesseract integration
□ Dansk sprog support
□ Progress feedback under OCR
□ OCR dialog med indstillinger
□ Batch processing support
□ Test med danske dokumenter
```

**Deliverable:** Fungerende OCR med dansk support

### Fase 4: Komprimering & Extras (Uge 4)
```
□ compressor.py - PDF komprimering
□ Rotate funktionalitet
□ Remove pages med preview
□ Password protection
□ Settings dialog
□ Gem bruger-præferencer
```

**Deliverable:** Alle kernefunktioner implementeret

### Fase 5: Polish & Packaging (Uge 5)
```
□ Fejlhåndtering og edge cases
□ Loading states og progress bars
□ Keyboard shortcuts
□ Tooltips og hjælpetekst
□ PyInstaller build setup
□ Test på ren Windows installation
□ Opret installer (valgfrit: Inno Setup)
```

**Deliverable:** Distribuerbar .exe fil

---

## 🧪 Test Strategi

### Unit Tests
```python
# tests/test_merger.py
def test_merge_two_pdfs():
    """Verificer at to PDFs kombineres korrekt."""
    pass

def test_merge_preserves_page_count():
    """Total sider = sum af input sider."""
    pass

# tests/test_ocr.py
def test_ocr_danish_text():
    """Verificer korrekt dansk tekstgenkendelse."""
    pass

def test_ocr_creates_text_layer():
    """Output PDF skal have søgbar tekst."""
    pass
```

### Manuel Test Checklist
```
□ Drag & drop filer virker
□ Flere filer kan tilføjes
□ Fil-rækkefølge kan ændres
□ OCR på dansk dokument
□ OCR på engelsk dokument
□ Merge 2+ PDFs
□ Split PDF i enkelte sider
□ Komprimér stor PDF
□ Password protect/unprotect
□ Rotér sider
□ Fjern specifikke sider
□ App starter uden filer
□ App håndterer korrupte PDFs gracefully
□ Cancel operation virker
□ Progress vises under lange operationer
```

---

## 🚀 Build & Distribution

### PyInstaller Kommando
```bash
pyinstaller --name="PDF Toolkit" \
            --windowed \
            --onefile \
            --icon=src/resources/icons/app.ico \
            --add-data="src/resources;resources" \
            src/main.py
```

### build.spec Template
```python
# build.spec
a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/resources/icons', 'resources/icons'),
        ('src/resources/styles', 'resources/styles'),
    ],
    hiddenimports=['PyQt6.sip'],
    ...
)
```

### Installer Checklist
```
□ Bundled Tesseract OCR (eller instruktioner)
□ Dansk sprogpakke inkluderet
□ Poppler DLLs (til pdf2image)
□ Visual C++ Redistributable check
□ Desktop shortcut
□ Start menu entry
□ Uninstaller
```

---

## 📝 Kode Konventioner

### Generelt
- **Sprog:** Engelsk i kode, dansk i UI/kommentarer hvor relevant
- **Formattering:** Black formatter, 88 char line length
- **Type hints:** Brug overalt
- **Docstrings:** Google style

### Eksempel
```python
"""
Module for PDF compression operations.
Provides multiple compression levels for different use cases.
"""

from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import fitz  # PyMuPDF


class CompressionLevel(Enum):
    """Available compression levels."""
    HIGH_QUALITY = "high"      # ~10-20% reduction
    BALANCED = "balanced"      # ~40-60% reduction  
    MAXIMUM = "maximum"        # ~70-90% reduction


@dataclass
class CompressionResult:
    """Result of a compression operation."""
    output_path: Path
    original_size: int
    compressed_size: int
    
    @property
    def ratio(self) -> float:
        """Compression ratio as percentage reduction."""
        return (1 - self.compressed_size / self.original_size) * 100


def compress_pdf(
    input_path: Path,
    output_path: Path,
    level: CompressionLevel = CompressionLevel.BALANCED
) -> CompressionResult:
    """
    Compress a PDF file to reduce its size.
    
    Args:
        input_path: Path to input PDF file
        output_path: Path for compressed output
        level: Desired compression level
        
    Returns:
        CompressionResult with size information
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If input is not a valid PDF
    """
    # Implementation here
    pass
```

### UI Kode Pattern
```python
"""
Dialog for OCR settings and execution.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QComboBox, QPushButton, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread


class OCRWorker(QThread):
    """Background worker for OCR processing."""
    
    progress = pyqtSignal(int, str)  # percent, status message
    finished = pyqtSignal(str)       # output path
    error = pyqtSignal(str)          # error message
    
    def __init__(self, input_path: str, options: dict):
        super().__init__()
        self.input_path = input_path
        self.options = options
    
    def run(self):
        """Execute OCR in background thread."""
        try:
            # OCR processing here
            self.progress.emit(50, "Behandler side 1/2...")
            # ...
            self.finished.emit(output_path)
        except Exception as e:
            self.error.emit(str(e))


class OCRDialog(QDialog):
    """Dialog for configuring and running OCR."""
    
    def __init__(self, files: list[str], parent=None):
        super().__init__(parent)
        self.files = files
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize dialog UI components."""
        self.setWindowTitle("OCR - Tekstgenkendelse")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Sprog:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Dansk", "Engelsk", "Auto-detect"])
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start OCR")
        self.start_btn.clicked.connect(self.start_ocr)
        self.cancel_btn = QPushButton("Annuller")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.start_btn)
        layout.addLayout(btn_layout)
    
    def start_ocr(self):
        """Begin OCR processing."""
        self.progress_bar.setVisible(True)
        self.start_btn.setEnabled(False)
        
        options = {
            "language": self.lang_combo.currentText(),
        }
        
        self.worker = OCRWorker(self.files[0], options)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()
    
    def on_progress(self, percent: int, message: str):
        """Update progress bar."""
        self.progress_bar.setValue(percent)
        self.progress_bar.setFormat(message)
    
    def on_finished(self, output_path: str):
        """Handle successful completion."""
        self.accept()
    
    def on_error(self, message: str):
        """Handle error during OCR."""
        # Show error dialog
        pass
```

---

## 🔗 Nyttige Ressourcer

### Dokumentation
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [Tesseract OCR](https://tesseract-ocr.github.io/)
- [PyInstaller Manual](https://pyinstaller.org/en/stable/)

### Tesseract Installation (Windows)
```
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Install med dansk sprogpakke
3. Tilføj til PATH: C:\Program Files\Tesseract-OCR
4. Verificer: tesseract --list-langs (skal vise 'dan')
```

### Poppler Installation (Windows)
```
1. Download: https://github.com/oschwartz10612/poppler-windows/releases
2. Udpak til fx C:\poppler
3. Tilføj til PATH: C:\poppler\bin
4. Verificer: pdftoppm -h
```

---

## 💡 Tips til Claude Code

Når du arbejder med dette projekt i Claude Code:

1. **Start her:** `cd pdf-toolkit-project && cat CLAUDE.md`

2. **Implementer i rækkefølge:** Følg faserne i implementeringsplanen

3. **Test løbende:** Kør appen efter hver større ændring

4. **Spørg om UI feedback:** Tag screenshots og spørg brugeren

5. **Husk dependencies:** Installer krav før kode-eksekvering

---

## 📞 Kommandoer til Claude Code

```bash
# Opsæt projekt
mkdir -p src/{ui/widgets,ui/dialogs,core,config,resources/icons}
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt

# Kør app under udvikling
python src/main.py

# Kør tests
pytest tests/

# Byg executable
pyinstaller build.spec

# Check Tesseract
tesseract --list-langs
```

---

*Sidst opdateret: Januar 2025*
