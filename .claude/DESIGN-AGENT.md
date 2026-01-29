# 🎨 DESIGN AGENT - Metropolis Art Deco Theme

> **KRITISK:** Denne fil definerer de PRÆCISE design-standarder for PDF Toolkit.
> Claude Code SKAL følge disse specifikationer nøjagtigt.
> **Reference:** `pdf-toolkit-unified.html` er den autoritative HTML prototype.

---

## 🎯 Design Filosofi

PDF Toolkit bruger en **Metropolis / Art Deco** æstetik inspireret af Fritz Langs film fra 1927.

**Nøgleelementer:**
- Dyb teal/grøn baggrund
- Guld accenter og highlights
- Geometriske, maskinel formsprog
- Vertikale linjer som dekorativt element
- Elegant, retrofuturistisk stemning

---

## 🎨 FARVEPALETTE (PRÆCISE HEX-VÆRDIER)

### Baggrunde
```
BG_DARK      = "#0D1A1A"    # Dyb mørk teal - primær baggrund
BG_DEEP      = "#122424"    # Mellem baggrund
BG_MID       = "#1A3333"    # Lysere baggrund-accent
```

### Primære Farver
```
TEAL         = "#2D5A5A"    # Primær teal - borders, linjer
TEAL_LIGHT   = "#4A8080"    # Hover states
MINT         = "#7FBFB5"    # Sekundær tekst, accenter
MINT_LIGHT   = "#A8D8D0"    # Highlights
```

### Accent Farver
```
GOLD         = "#D4A84B"    # PRIMÆR ACCENT - titler, hover
GOLD_BRIGHT  = "#E8C547"    # Aktive states, glow, hover text
GOLD_DARK    = "#B8923A"    # Pressed states
RED_ACCENT   = "#C45C5C"    # Fejl, sletning
```

### Tekst
```
TEXT_PRIMARY   = "#E8E4D9"  # Primær tekst (cream)
TEXT_SECONDARY = "#7FBFB5"  # Sekundær tekst (mint)
TEXT_MUTED     = "#4A8080"  # Muted tekst
```

---

## 🔤 TYPOGRAFI

### Display Font (Titler) - Bebas Neue
```
Font:     "Bebas Neue", "Impact", sans-serif
Brug:     Hovedtitel, sektion-headers, tool-navne, drop zone text
Style:    ALL CAPS
```

### Body Font (Brødtekst) - Rajdhani
```
Font:     "Rajdhani", "Segoe UI", sans-serif
Brug:     Undertitel, beskrivelser, labels, status, fil-info
Weight:   400-600
```

### Størrelses-hierarki (PRÆCISE VÆRDIER)
```
Hovedtitel:      56px, letter-spacing: 22px (Bebas Neue)
Undertitel:      16px, letter-spacing: 5px, weight: 500 (Rajdhani)
Sektion-header:  21px, letter-spacing: 5px (Bebas Neue)
Tool-navn:       18px, letter-spacing: 3px (Bebas Neue)
Tool-beskrivelse: 13px, weight: 500, NO letter-spacing (Rajdhani)
Drop zone text:  20px, letter-spacing: 4px (Bebas Neue)
Drop zone formats: 14px, letter-spacing: 3px, weight: 500 (Rajdhani)
Fil-navn:        15px, weight: 600 (Rajdhani)
Fil-meta:        13px (Rajdhani)
```

---

## 🔲 KOMPONENTER

### Tool Tiles
```css
/* Base styling */
background: linear-gradient(160deg,
    rgba(45, 90, 90, 0.4) 0%,
    rgba(13, 26, 26, 0.9) 100%);
border: 1px solid #2D5A5A;
border-radius: 6px;
padding: 20px 12px;
height: 130px;
/* Tiles EXPAND to fill grid columns (not fixed width) */

/* Hover state */
border-color: #D4A84B;
background: linear-gradient(160deg,
    rgba(74, 128, 128, 0.5) 0%,
    rgba(18, 36, 36, 0.95) 100%);
box-shadow: 0 12px 40px rgba(0,0,0,0.5);
/* Text becomes #E8C547 (gold-bright) */

/* Hover decorative lines */
::before - Top gold gradient line (fades in)
::after - Bottom mint line grows to 60% width

/* Icon on hover */
filter: drop-shadow(0 0 16px #D4A84B);

/* Active/pressed state */
box-shadow reduced (offset: 6px, blur: 25px)
```

### Drop Zone
```css
/* Base styling */
background: #0D1A1A;
border: 2px solid #2D5A5A;  /* NOTE: 2px not 1px */
border-radius: 8px;
padding: 45px 30px;
min-height: 200px;

/* Inner dashed border (via paintEvent) */
inset: 12px from edges
border: 1px dashed #2D5A5A;
border-radius: 4px;

/* Hover state */
border-color: #D4A84B;
background: linear-gradient(180deg, rgba(45,90,90,0.2) 0%, #0D1A1A 100%);

/* Hover inner dashed border */
border-color: #D4A84B;
inset: 8px (moves inward);

/* Icon on hover */
filter: drop-shadow(0 0 30px #D4A84B);
```

### File List
```css
/* Container */
background: rgba(13, 26, 26, 0.8);
border: 1px solid #2D5A5A;
border-radius: 6px;

/* File item */
padding: 14px 18px;
border-bottom: 1px solid rgba(45, 90, 90, 0.4);

/* File item hover */
background: rgba(45, 90, 90, 0.3);

/* Action buttons (28x28) */
background: transparent;
border: 1px solid #2D5A5A;
border-radius: 4px;
color: #7FBFB5;

/* Action button hover */
border-color: #D4A84B;
color: #D4A84B;
background: rgba(212, 168, 75, 0.1);
```

### Status Bar
```css
background: #0D1A1A;
border-top: 1px solid #2D5A5A;
/* Version label on right side */
```

---

## 🖼️ DEKORATIVE ELEMENTER

### Vertikale Linjer (Art Deco Lines)
```
Positions: 5%, 12%, 88%, 95% from left edge
Width: 1px
Gradient (vertical):
  0%   - transparent
  30%  - #2D5A5A (teal)
  50%  - #7FBFB5 (mint)
  70%  - #2D5A5A (teal)
  100% - transparent
Opacity: 0.2 (51/255 alpha)
```

### Sektion Headers
```
Left/right gradient lines extending from title
Left:  transparent → #2D5A5A
Right: #2D5A5A → transparent
```

### Header Ornament
```
Gold diamond (◆) centered between two 40px gold lines
```

---

## 📐 LAYOUT & SPACING

### Container
```
max-width: 900px
padding: 30px horizontal, 25-40px vertical
```

### Spacing (PRÆCISE VÆRDIER)
```
Header margin-bottom:       40px
Section title margin-bottom: 20px
Tools section margin-bottom: 35px
Tool grid gap:              12px
Drop zone margin-bottom:    25px
File list section margin:   25px
```

### Responsive Grid
```
> 600px width:  4 columns
400-600px:      3 columns
< 400px:        2 columns
```

---

## 🖱️ INTERAKTIONER

### Transitions (HTML reference)
```css
transition: all 0.3s ease;  /* Standard for alle elementer */
```

### Tool Tile Hover
1. Border changes to gold
2. Background lightens slightly
3. Text brightens to #E8C547
4. Shadow appears (blur: 40px, offset: 12px)
5. Icon gets gold glow
6. Top gold gradient line fades in
7. Bottom mint line grows from center to 60% width

### Tool Tile Active (click)
1. Shadow reduces (blur: 25px, offset: 6px)

### Drop Zone Hover
1. Border changes to gold
2. Background gets gradient
3. Inner dashed border moves inward (12px → 8px)
4. Inner dashed border changes to gold
5. Icon gets gold glow

---

## ✅ CHECKLISTE FOR CLAUDE CODE

Når du implementerer UI-elementer, verificer:

- [ ] Bruger præcis HEX farve fra paletten ovenfor
- [ ] Typografi matcher specifikationen (font, size, weight, letter-spacing)
- [ ] Hover/active states er implementeret med korrekt styling
- [ ] SVG ikoner bruges (ikke emojis!) - se ICONS-AGENT.md
- [ ] Border-radius er konsistent (6px for tiles, 8px for drop zone)
- [ ] Shadows bruger korrekte værdier (blur, offset, color)
- [ ] Letter-spacing er tilføjet til Bebas Neue tekst
- [ ] Rajdhani tekst har INGEN letter-spacing (undtagen subtitle)
- [ ] Spacing matcher HTML reference nøjagtigt
- [ ] Dekorative linjer er implementeret

---

## 🚫 UNDGÅ

- ❌ Emojis som ikoner
- ❌ Standard system-farver
- ❌ Flat/hvide baggrunde
- ❌ Afrundede/bløde former (brug geometriske)
- ❌ Standard Windows/Mac UI elementer
- ❌ Farver der ikke er i paletten
- ❌ Fixed-width tool tiles (de skal EXPAND i grid)
- ❌ Letter-spacing på body text (kun på display text)

---

*Sidst opdateret: 29. januar 2025*
*Denne fil er den autoritative kilde for design-beslutninger.*
