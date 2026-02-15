# Changelog

All notable changes to PDF Toolkit will be documented in this file.

---

## [Unreleased] - Phase 5 Features

### Added - Phase 5 Features

#### Tooltips
- Added Danish tooltip help text to all 9 tool tiles
- Tooltips appear on hover with gold border styling
- Describes each tool's function and capabilities

#### Citation Extraction (`src/core/citation_extractor.py`, `src/ui/dialogs/citation_dialog.py`)
- **New "Citater" tool** for extracting bibliographic metadata from academic PDFs
- Extracts: Title, Authors, Year, DOI, Abstract, Journal, Publisher
- Smart extraction from PDF metadata and text content
- Multi-author detection with proper name parsing
- DOI detection via regex pattern matching
- Abstract extraction with hyphenation artifact cleanup
- Export formats:
  - **BibTeX** - Standard citation format with auto-generated citation key
  - **CSL-JSON** - Zotero-compatible format with family/given name parsing
- Copy to clipboard and save to file functionality
- "Open DOI in browser" link for found DOIs
- Confidence indicator showing extraction quality

#### New Icon
- Added "citation" icon (book with quotation marks) to `icons.py`

#### Hover Animation Improvements (`src/ui/widgets/tool_tile.py`)
- **Tile lift animation** - Entire tile box now lifts on hover (not just content)
  - translateY(-4px) on hover, translateY(-2px) on press
  - Smooth 300ms ease animation matching CSS `transition: all 0.3s ease`
  - Implemented via `QPropertyAnimation` on tile frame geometry
- **Mint line animation** - Bottom mint line grows from center point outward
  - Animates from 0% to 60% width on hover
  - Synced with lift animation (300ms duration)
  - Uses custom `AnimatedFrame` class with `pyqtProperty`
- **Centered icon glow** - Drop shadow effect centered behind icon
  - BlurRadius: 30px for soft falloff
  - Offset: (0, 0) for centered glow
  - Gold color with 220/255 opacity
- **Drop zone icon glow** - Also centered with `setOffset(0, 0)`
- **Architecture change** - ToolTile refactored from QFrame to QWidget container
  - Inner `_tile_frame` (QFrame) holds visual styling and animates
  - Outer container stays fixed in grid layout
  - Prevents layout disruption during lift animation

---

## [1.1.0] - Phase 4 Complete

### Added - Phase 4 Features

#### Compression (`src/core/compressor.py`, `src/ui/dialogs/compress_dialog.py`)
- PDF compression with 3 levels: High Quality, Balanced, Maximum
- Shows original size, compressed size, and reduction percentage
- Progress feedback during compression

#### Page Operations (`src/core/page_ops.py`)
- **Rotate Pages** - 90° CW, 180°, 90° CCW for all or specific pages
- **Remove Pages** - Select pages visually with thumbnails or enter manually
- **Extract Pages** - Extract specific pages to new PDF
- **Thumbnails** - Generate page thumbnails for preview

#### Rotation Dialog (`src/ui/dialogs/rotate_dialog.py`)
- Rotate all pages or specific pages (e.g., "1, 3, 5-7")
- Three rotation options: 90° med uret, 180°, 90° mod uret

#### Remove Pages Dialog (`src/ui/dialogs/remove_dialog.py`)
- Visual page selection with thumbnail previews
- Multi-select support (click to toggle)
- Manual page entry as alternative
- Background thumbnail loading with threading

#### Encryption (`src/core/encryption.py`, `src/ui/dialogs/encrypt_dialog.py`)
- **Encrypt PDF** - Add password protection with AES-256
- **Decrypt PDF** - Remove password from encrypted PDFs
- User password (to open) and Owner password (full access)
- Permission controls: Print, Copy, Modify, Annotate
- Auto-detects if PDF is already encrypted

### Changed
- Enabled all Phase 4 tools in `constants.py` (Remove, Rotate, Encrypt)
- Fixed tool ID: "protect" → "encrypt" for consistency with main_window.py
- Updated `src/core/__init__.py` to export new modules
- Updated `src/ui/dialogs/__init__.py` to export new dialogs
- Updated `src/ui/main_window.py` with handlers for new dialogs

### Fixed
- `QSize` import error in remove_dialog.py (was `Qt.QSize`, now `QSize`)
- QPainter threading issue in thumbnail loading (added QueuedConnection)
- Thumbnail updates now disable widget updates to prevent paint conflicts
- **Compression engine completely rewritten** - was not actually compressing images
  - Now uses PIL/Pillow to recompress images at specified quality levels
  - High Quality: 85% JPEG, max 2400px, no scaling
  - Balanced: 65% JPEG, max 1600px, 85% scale
  - Maximum: 40% JPEG, max 1200px, 70% scale
- **File size increase bug fixed** - if compression makes file larger, keeps original
  - Shows "Filen er allerede optimeret" message
  - Reports 0% reduction instead of negative percentage
- **QPainter conflicts at startup fixed** - eliminated "paint device can only be painted by one painter" errors
  - Replaced QSvgWidget with QLabel + pre-rendered QPixmap (cached)
  - QGraphicsDropShadowEffect now created on-demand (hover only), not at startup
  - Effects removed when mouse leaves to prevent conflicts
  - Affected: tool_tile.py, drop_zone.py, file_list.py, icons.py

### Styling Updates (`src/ui/styles.py`)
- Added QTabWidget styling (dark theme for encrypt dialog tabs)
- Added QCheckBox styling (dark theme indicators)
- Fixed QComboBox dropdown arrow positioning

### Fixed
- **Icon mapping**: "protect" → "encrypt" in `icons.py` to match tool ID in constants.py

### Still TODO (Phase 6)
- [ ] PyInstaller build setup (build.spec)
- [ ] Test on clean Windows installation
- [ ] Optional: Inno Setup installer

---

## [1.0.0] - 2025-01-29

### Added

#### UI Components
- **Decorative Vertical Lines** - 4 gradient lines at 5%, 12%, 88%, 95% positions matching HTML prototype
  - Gradient: transparent → teal (#2D5A5A) → mint (#7FBFB5) → teal → transparent
  - 20% opacity for subtle Art Deco effect
  - Implemented via `ArtDecoLines` overlay widget in `main_window.py`

- **Tool Tile Hover Effects**
  - Top gold gradient line fades in on hover (::before equivalent)
  - Bottom mint line grows to 60% width on hover (::after equivalent)
  - Icon glow effect (drop-shadow) on hover
  - Enhanced box-shadow: blur 40px, offset 12px
  - Active/pressed state with reduced shadow
  - Gold border and brighter text (#E8C547) on hover

- **Drop Zone Improvements**
  - Increased height to 200px minimum
  - Inner dashed border animates from 12px to 8px inset on hover
  - Icon glow effect on hover (gold drop-shadow)
  - Background gradient on hover
  - 2px solid border matching HTML

- **File List Panel**
  - SVG file icons (28x28)
  - Inline action buttons (↑ ↓ ✕) per row
  - Page count display for PDFs ("12 sider · 2.4 MB")
  - Proper Rajdhani font styling

- **Version indicator** in status bar (v1.0.0)

### Changed

#### Typography (matching HTML exactly)
- **Title**: Bebas Neue 56px, letter-spacing 22px
- **Subtitle**: Rajdhani 16px, font-weight 500, letter-spacing 5px
- **Section titles**: Bebas Neue 21px, letter-spacing 5px
- **Tool names**: Bebas Neue 18px, letter-spacing 3px
- **Tool descriptions**: Rajdhani 13px, font-weight 500 (no letter-spacing)
- **Drop text**: Bebas Neue 20px, letter-spacing 4px
- **File names**: Rajdhani 15px, font-weight 600
- **File meta**: Rajdhani 13px

#### Layout & Spacing (matching HTML)
- Header margin-bottom: 40px
- Section title margin-bottom: 20px
- Tools section margin-bottom: 35px
- Drop zone margin-bottom: 25px
- Tool tile padding: 20px 12px
- Drop zone padding: 45px 30px
- File item padding: 14px 18px

#### Tool Grid
- Tiles now expand to fill available width (like CSS `grid-template-columns: repeat(4, 1fr)`)
- Responsive columns: 4 (>600px), 3 (400-600px), 2 (<400px)
- Tool order updated to match HTML: OCR, Merge, Split, Compress, Fjern, Rotér, Kryptér, Indstil.

### Fixed
- Tool tiles no longer fixed size - they expand to fill grid columns
- Drop zone border changed from 1px to 2px to match HTML
- Removed conflicting styles from `styles.py` (drop zone now styled in widget)
- Icon sizes properly set (40x40 for tools, 50x50 for drop zone, 28x28 for files)

### Technical
- Added `ArtDecoLines` widget class for decorative background lines
- Added `get_pdf_page_count()` utility function
- Tool tile uses `QGraphicsDropShadowEffect` for both tile shadow and icon glow
- Drop zone uses `QGraphicsDropShadowEffect` for icon glow
- Custom `paintEvent` for tool tiles draws top gold line and bottom mint line

---

## Reference Files
- HTML Prototype: `pdf-toolkit-unified.html`
- Design Spec: `.claude/DESIGN-AGENT.md`
- Icon Spec: `.claude/ICONS-AGENT.md`
