# 🎭 ICONS AGENT - Art Deco SVG Ikoner

> **KRITISK:** Denne fil indeholder de PRÆCISE SVG ikoner til PDF Toolkit.
> Claude Code SKAL bruge disse ikoner - ALDRIG emojis!

---

## 📋 Oversigt

Alle ikoner er designet i Art Deco stil med:
- **Primær stroke:** `#D4A84B` (guld)
- **Sekundær/fill:** `#7FBFB5` (mint)
- **Stroke-width:** 1.5px (standard), 2px (emphasis)
- **ViewBox:** 40x40 (tool icons), 50x50 (drop zone), 28x28 (file icon)

---

## 🔧 Tool Ikoner (40x40)

Alle tool ikoner er defineret i `src/ui/icons.py` som `TOOL_ICONS` dictionary.

### OCR - Øje/Scanner
```svg
<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="20" cy="20" rx="16" ry="10" stroke="#D4A84B" stroke-width="1.5" fill="none"/>
  <circle cx="20" cy="20" r="6" stroke="#D4A84B" stroke-width="1.5" fill="none"/>
  <circle cx="20" cy="20" r="2.5" fill="#7FBFB5"/>
  <line x1="4" y1="20" x2="10" y2="20" stroke="#7FBFB5" stroke-width="1"/>
  <line x1="30" y1="20" x2="36" y2="20" stroke="#7FBFB5" stroke-width="1"/>
  <line x1="20" y1="4" x2="20" y2="8" stroke="#D4A84B" stroke-width="1" opacity="0.6"/>
  <line x1="20" y1="32" x2="20" y2="36" stroke="#D4A84B" stroke-width="1" opacity="0.6"/>
</svg>
```

### MERGE - Dokumenter der samles
```svg
<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="5" y="8" width="14" height="18" rx="1" stroke="#D4A84B" stroke-width="1.5" fill="none"/>
  <rect x="21" y="8" width="14" height="18" rx="1" stroke="#D4A84B" stroke-width="1.5" fill="none"/>
  <path d="M20 28 L20 36 M15 32 L20 37 L25 32" stroke="#7FBFB5" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  <line x1="8" y1="13" x2="16" y2="13" stroke="#7FBFB5" stroke-width="1"/>
  <line x1="8" y1="17" x2="16" y2="17" stroke="#7FBFB5" stroke-width="1"/>
  <line x1="24" y1="13" x2="32" y2="13" stroke="#7FBFB5" stroke-width="1"/>
  <line x1="24" y1="17" x2="32" y2="17" stroke="#7FBFB5" stroke-width="1"/>
</svg>
```

### SPLIT - Dokument der deles
```svg
<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="13" y="4" width="14" height="18" rx="1" stroke="#D4A84B" stroke-width="1.5" fill="none"/>
  <path d="M12 26 L6 34" stroke="#7FBFB5" stroke-width="1.5" stroke-linecap="round"/>
  <path d="M28 26 L34 34" stroke="#7FBFB5" stroke-width="1.5" stroke-linecap="round"/>
  <rect x="2" y="32" width="10" height="6" rx="1" stroke="#D4A84B" stroke-width="1" fill="none"/>
  <rect x="28" y="32" width="10" height="6" rx="1" stroke="#D4A84B" stroke-width="1" fill="none"/>
  <line x1="10" y1="22" x2="30" y2="22" stroke="#D4A84B" stroke-width="1" stroke-dasharray="2 2"/>
</svg>
```

### COMPRESS - Komprimering
```svg
<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M8 12 L20 20 L8 28" stroke="#7FBFB5" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
  <path d="M32 12 L20 20 L32 28" stroke="#7FBFB5" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
  <rect x="16" y="14" width="8" height="12" rx="1" stroke="#D4A84B" stroke-width="1.5" fill="none"/>
  <line x1="14" y1="6" x2="26" y2="6" stroke="#D4A84B" stroke-width="1"/>
  <line x1="14" y1="34" x2="26" y2="34" stroke="#D4A84B" stroke-width="1"/>
  <circle cx="20" cy="6" r="2" fill="#D4A84B"/>
  <circle cx="20" cy="34" r="2" fill="#D4A84B"/>
</svg>
```

### REMOVE (FJERN) - Fjern sider
```svg
<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="6" width="20" height="28" rx="1" stroke="#D4A84B" stroke-width="1.5" fill="none"/>
  <line x1="15" y1="16" x2="25" y2="26" stroke="#7FBFB5" stroke-width="2" stroke-linecap="round"/>
  <line x1="25" y1="16" x2="15" y2="26" stroke="#7FBFB5" stroke-width="2" stroke-linecap="round"/>
  <line x1="13" y1="10" x2="27" y2="10" stroke="#D4A84B" stroke-width="1" opacity="0.5"/>
</svg>
```

### ROTATE (ROTÉR) - Rotér sider
```svg
<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M20 8 A12 12 0 1 1 8 20" stroke="#D4A84B" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <path d="M20 4 L20 12 L12 8 Z" fill="#7FBFB5"/>
  <rect x="15" y="15" width="10" height="12" rx="1" stroke="#D4A84B" stroke-width="1" fill="none"/>
</svg>
```

### PROTECT (KRYPTÉR) - Kryptering/Lås
```svg
<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="12" y="18" width="16" height="14" rx="2" stroke="#D4A84B" stroke-width="1.5" fill="none"/>
  <path d="M15 18 L15 12 A5 5 0 0 1 25 12 L25 18" stroke="#D4A84B" stroke-width="1.5" fill="none"/>
  <circle cx="20" cy="24" r="2" fill="#7FBFB5"/>
  <rect x="19" y="24" width="2" height="4" fill="#7FBFB5"/>
  <line x1="20" y1="4" x2="20" y2="8" stroke="#D4A84B" stroke-width="1" opacity="0.5"/>
  <line x1="8" y1="25" x2="4" y2="25" stroke="#D4A84B" stroke-width="1" opacity="0.5"/>
  <line x1="36" y1="25" x2="32" y2="25" stroke="#D4A84B" stroke-width="1" opacity="0.5"/>
</svg>
```

### SETTINGS (INDSTIL.) - Tandhjul
```svg
<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M20 6 L22 10 L26 8 L26 13 L31 12 L28 17 L33 19 L28 23 L31 28 L26 27 L26 32 L22 30 L20 34 L18 30 L14 32 L14 27 L9 28 L12 23 L7 19 L12 17 L9 12 L14 13 L14 8 L18 10 Z"
        stroke="#D4A84B" stroke-width="1.5" fill="none"/>
  <circle cx="20" cy="20" r="5" stroke="#7FBFB5" stroke-width="1.5" fill="none"/>
  <circle cx="20" cy="20" r="2" fill="#7FBFB5"/>
</svg>
```

---

## 📁 Drop Zone Ikon (50x50)

### Dokument med Plus
```svg
<svg viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="12" y="6" width="26" height="34" rx="2" stroke="#D4A84B" stroke-width="2" fill="none"/>
  <path d="M30 6 L38 14 L30 14 Z" fill="#7FBFB5" stroke="#D4A84B" stroke-width="1"/>
  <line x1="25" y1="22" x2="25" y2="34" stroke="#7FBFB5" stroke-width="2" stroke-linecap="round"/>
  <line x1="19" y1="28" x2="31" y2="28" stroke="#7FBFB5" stroke-width="2" stroke-linecap="round"/>
  <circle cx="6" cy="23" r="2" fill="#D4A84B" opacity="0.5"/>
  <circle cx="44" cy="23" r="2" fill="#D4A84B" opacity="0.5"/>
</svg>
```

---

## 📄 Fil-ikon (28x28)

### PDF Dokument
```svg
<svg viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="4" y="2" width="16" height="22" rx="1" stroke="#D4A84B" stroke-width="1.5" fill="none"/>
  <path d="M14 2 L20 8 L14 8 Z" fill="#7FBFB5"/>
  <line x1="7" y1="12" x2="17" y2="12" stroke="#7FBFB5" stroke-width="1"/>
  <line x1="7" y1="16" x2="17" y2="16" stroke="#7FBFB5" stroke-width="1"/>
  <line x1="7" y1="20" x2="13" y2="20" stroke="#7FBFB5" stroke-width="1"/>
</svg>
```

---

## ✨ HOVER EFFEKTER

### Icon Glow on Hover
Ikoner får en guld glow-effekt ved hover via `QGraphicsDropShadowEffect`:

```python
# Tool tile icon glow
icon_glow = QGraphicsDropShadowEffect()
icon_glow.setBlurRadius(16)
icon_glow.setOffset(0, 0)
icon_glow.setColor(QColor(212, 168, 75, 200))  # Gold with alpha
icon_widget.setGraphicsEffect(icon_glow)

# Drop zone icon glow (larger)
icon_glow.setBlurRadius(30)
icon_glow.setColor(QColor(212, 168, 75, 180))
```

---

## 💡 Implementering i PyQt6

### Brug icons.py modulet
```python
from src.ui.icons import get_icon_widget, get_drop_zone_icon, get_file_icon

# Tool icon (40x40)
icon = get_icon_widget('ocr', size=40)

# Drop zone icon (50x50)
drop_icon = get_drop_zone_icon(size=50)

# File icon (28x28)
file_icon = get_file_icon(size=28)
```

### Manuel SVG loading
```python
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import QByteArray

svg_data = '''<svg viewBox="0 0 40 40"...>...</svg>'''
icon_widget = QSvgWidget()
icon_widget.load(QByteArray(svg_data.encode('utf-8')))
icon_widget.setFixedSize(40, 40)
```

---

## 📐 Ikon Størrelser

| Kontekst | Størrelse | ViewBox |
|----------|-----------|---------|
| Tool tiles | 40x40 px | 0 0 40 40 |
| Drop zone | 50x50 px | 0 0 50 50 |
| File list | 28x28 px | 0 0 28 28 |

---

## 🎨 Farve Reference

| Element | Farve | HEX |
|---------|-------|-----|
| Primær stroke | Guld | #D4A84B |
| Sekundær/fill | Mint | #7FBFB5 |
| Hover glow | Guld bright | #E8C547 |
| Disabled | 35% opacity | rgba(212,168,75,0.35) |

---

*Sidst opdateret: 29. januar 2025*
*Denne fil er den autoritative kilde for ikon-design.*
