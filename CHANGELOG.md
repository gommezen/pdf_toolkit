# Changelog

All notable changes to PDF Toolkit will be documented in this file.

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
