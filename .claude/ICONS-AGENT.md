# Icons Agent - Art Deco SVG Ikoner

> Autoritative kilde for ikon-design. Alle ikoner defineret i `src/ui/icons.py`.

---

## Generelt

- **Primaer stroke:** `#D4A84B` (guld), width 1.5px
- **Sekundaer/fill:** `#7FBFB5` (mint)
- **Stil:** Art Deco, geometrisk

## Storrelser

| Kontekst | Storrelse | ViewBox |
|----------|-----------|---------|
| Tool tiles | 40x40 px | 0 0 40 40 |
| Drop zone | 50x50 px | 0 0 50 50 |
| File list | 28x28 px | 0 0 28 28 |

## Implementerede ikoner

| ID | Navn | Beskrivelse |
|----|------|-------------|
| ocr | OCR | Oje/scanner |
| merge | Merge | Dokumenter der samles |
| split | Split | Dokument der deles |
| compress | Compress | Komprimering |
| remove | Fjern | Dokument med kryds |
| rotate | Roter | Cirkulaer pil med dokument |
| encrypt | Krypter | Haengelaas |
| citation | Citater | Bog med citationstegn |
| settings | Indstillinger | Tandhjul |
| dropzone | Drop zone | Dokument med plus |
| file | Fil | PDF-dokument |

## Brug i kode

```python
from src.ui.icons import get_icon_widget, get_drop_zone_icon, get_file_icon

icon = get_icon_widget('ocr', size=40)       # Tool icon
drop_icon = get_drop_zone_icon(size=50)       # Drop zone
file_icon = get_file_icon(size=28)            # File list
```

## Hover-effekter

```python
# Icon glow via QGraphicsDropShadowEffect
effect = QGraphicsDropShadowEffect()
effect.setBlurRadius(16)        # 30 for drop zone
effect.setOffset(0, 0)          # Centreret
effect.setColor(QColor(212, 168, 75, 200))  # Guld med alpha
```

## Regler

- ALDRIG emojis som ikoner i UI
- Brug pixmap-cache (ikke QSvgWidget) for at undga QPainter-konflikter
- Opret QGraphicsDropShadowEffect on-demand ved hover, fjern ved mouse leave
