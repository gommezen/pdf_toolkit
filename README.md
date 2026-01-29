# PDF Toolkit

En simpel og hurtig desktop-applikation til PDF-manipulation med dansk sprogunderstøttelse.

**Metropolis Art Deco Theme** - Moderne UI inspireret af 1920'ernes Art Deco æstetik.

## Features

### Implementeret
- **OCR Tekstgenkendelse** - Gør scannede dokumenter søgbare (dansk + engelsk)
- **Kombiner PDFs** - Saml flere PDF-filer til én
- **Opdel PDF** - Split en PDF i flere filer
- **Konverter Word til PDF** - Konverter .docx filer

### Under udvikling
- Komprimér PDF
- Rotér sider
- Fjern sider
- Password beskyttelse

## Installation

### Forudsætninger

1. **Python 3.10+**
   ```powershell
   python --version
   ```

2. **Tesseract OCR** (til tekstgenkendelse)
   - Download fra: https://github.com/UB-Mannheim/tesseract/wiki
   - Vælg dansk sprogpakke under installation
   - Tilføj til PATH: `C:\Program Files\Tesseract-OCR`

   Eller download dansk sprogpakke separat:
   ```powershell
   # Download dan.traineddata til tessdata mappen
   curl -L -o "C:\Program Files\Tesseract-OCR\tessdata\dan.traineddata" "https://github.com/tesseract-ocr/tessdata/raw/main/dan.traineddata"
   ```

### Installer PDF Toolkit

```powershell
# Klon eller download projektet
git clone <repo-url> pdf-toolkit
cd pdf-toolkit

# Opret virtuelt miljø (valgfrit men anbefalet)
python -m venv venv
.\venv\Scripts\Activate

# Installer dependencies
pip install -r requirements.txt

# Kør applikationen
python run_app.py
```

## Brug

### Start applikationen
```powershell
cd pdf-toolkit
python run_app.py
```

Eller brug `run.bat` på Windows.

### Grundlæggende workflow

1. **Træk filer** ind i applikationen (eller klik for at vælge)
2. **Vælg værktøj** fra toolbaren (OCR, Merge, Split, etc.)
3. **Konfigurer indstillinger** i dialogen
4. **Kør operationen** og gem resultatet

## Konfiguration

### Tesseract sti
Hvis Tesseract ikke er i PATH, angiv stien i **Indstillinger**:
- Tesseract sti: `C:\Program Files\Tesseract-OCR\tesseract.exe`

### Tilgængelige sprog
```powershell
tesseract --list-langs
# Skal vise: dan, eng, osd
```

## Teknisk Stack

- **UI:** PyQt6
- **PDF Processing:** PyMuPDF (fitz)
- **OCR:** Tesseract + pytesseract
- **Image Processing:** Pillow

## Projektstruktur

```
pdf-toolkit/
├── run_app.py          # Launcher script
├── requirements.txt    # Python dependencies
├── src/
│   ├── main.py         # Application entry point
│   ├── ui/             # UI components
│   │   ├── main_window.py
│   │   ├── styles.py   # Art Deco theme
│   │   ├── widgets/    # Custom widgets
│   │   └── dialogs/    # Tool dialogs
│   ├── core/           # Core functionality
│   │   ├── ocr_engine.py
│   │   ├── merger.py
│   │   ├── splitter.py
│   │   └── converter.py
│   └── config/         # Settings
└── tests/              # Unit tests
```

## Fejlfinding

### "Tesseract not found"
- Verificer installation: `tesseract --version`
- Tilføj til PATH eller angiv sti i Indstillinger

### OCR giver forkerte danske tegn
- Sikr dansk sprogpakke er installeret
- Vælg "Dansk" i OCR indstillinger

### QPainter errors i konsollen
- Kan ignoreres - påvirker ikke funktionalitet

## Licens

MIT License - Fri til brug og modifikation.

## Bidrag

Fejlrapporter og forbedringsforslag er velkomne!
