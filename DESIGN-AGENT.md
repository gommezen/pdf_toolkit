# 🎨 DESIGN AGENT - Metropolis Art Deco Theme

> **KRITISK:** Denne fil definerer de PRÆCISE design-standarder for PDF Toolkit.  
> Claude Code SKAL følge disse specifikationer nøjagtigt.

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
GOLD_BRIGHT  = "#E8C547"    # Aktive states, glow
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

### Display Font (Titler)
```
Font:     "Bebas Neue", "Impact", "Arial Black", sans-serif
Brug:     Hovedtitel, sektion-headers, tool-navne
Style:    ALL CAPS, letter-spacing: 0.2-0.4em
```

### Body Font (Brødtekst)
```
Font:     "Rajdhani", "Segoe UI", sans-serif
Brug:     Beskrivelser, labels, status
Weight:   400-600
```

### Størrelses-hierarki
```
Hovedtitel:      42px, letter-spacing: 12px
Undertitel:      12px, letter-spacing: 6px
Sektion-header:  13-14px, letter-spacing: 4px
Tool-navn:       13px, letter-spacing: 2px
Beskrivelse:     11px
```

---

## 🔲 KOMPONENTER

### Tool Tiles
```css
/* PRÆCIS STYLING */
background: linear-gradient(160deg, 
    rgba(45, 90, 90, 0.4) 0%, 
    rgba(13, 26, 26, 0.9) 100%);
border: 1px solid #2D5A5A;
border-radius: 6px;
padding: 20px 12px;

/* Hover */
border-color: #D4A84B;
border-top: 2px solid #D4A84B;
box-shadow: 0 15px 40px rgba(0,0,0,0.5),
            0 0 25px rgba(212,168,75,0.15);
transform: translateY(-4px);
```

### Drop Zone
```css
background: #0D1A1A;
border: 2px solid #2D5A5A;
border-radius: 8px;
/* Inner dashed border via pseudo-element */

/* Hover */
border-color: #D4A84B;
```

### Status Bar
```css
background: rgba(13, 26, 26, 0.9);
border: 1px solid #2D5A5A;
border-radius: 6px;
/* Pulserende grøn dot for "Klar" status */
```

---

## 🖼️ IKONER

**VIGTIGT:** Brug ALTID de custom SVG Art Deco ikoner defineret i `src/ui/icons.py`.

Ikoner skal:
- Bruge `#D4A84B` (guld) som primær stroke
- Bruge `#7FBFB5` (mint) som sekundær/fill
- Være geometriske og maskinel i stil
- Have stroke-width: 1.5-2px

Se `ICONS-AGENT.md` for præcise SVG-definitioner.

---

## 📐 LAYOUT

### Spacing
```
Container padding:    30px horizontal, 25px vertical
Sektion spacing:      12-15px
Grid gap:             12px
Tile padding:         20px 12px
```

### Dekorative Elementer
```
- Vertikale teal linjer i baggrunden (opacity: 0.2)
- Guld gradient-linje under titel
- Diamant-ornament som separator
- Sektion-headers med fade-linjer på hver side
```

---

## ✅ CHECKLISTE FOR CLAUDE CODE

Når du implementerer UI-elementer, verificer:

- [ ] Bruger præcis HEX farve fra paletten ovenfor
- [ ] Typografi matcher specifikationen
- [ ] Hover/active states er implementeret
- [ ] SVG ikoner bruges (ikke emojis!)
- [ ] Border-radius er konsistent (6px for tiles, 8px for større elementer)
- [ ] Shadows bruger rgba med korrekte værdier
- [ ] Letter-spacing er tilføjet til uppercase tekst

---

## 🚫 UNDGÅ

- ❌ Emojis som ikoner
- ❌ Standard system-farver
- ❌ Flat/hvide baggrunde
- ❌ Afrundede/bløde former (brug geometriske)
- ❌ Standard Windows/Mac UI elementer
- ❌ Farver der ikke er i paletten

---

*Denne fil er den autoritative kilde for design-beslutninger.*
