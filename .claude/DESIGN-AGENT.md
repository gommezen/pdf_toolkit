# Design Agent - Metropolis Art Deco Theme

> Autoritative kilde for design-beslutninger. Reference: `pdf-toolkit-unified.html`

---

## Farvepalette

### Baggrunde
| Token | HEX | Brug |
|-------|-----|------|
| BG_DARK | `#0D1A1A` | Primaer baggrund |
| BG_DEEP | `#122424` | Mellem baggrund |
| BG_MID | `#1A3333` | Lysere accent |

### Primaere
| Token | HEX | Brug |
|-------|-----|------|
| TEAL | `#2D5A5A` | Borders, linjer |
| TEAL_LIGHT | `#4A8080` | Hover states |
| MINT | `#7FBFB5` | Sekundaer tekst, accenter |
| MINT_LIGHT | `#A8D8D0` | Highlights |

### Accent
| Token | HEX | Brug |
|-------|-----|------|
| GOLD | `#D4A84B` | Primaer accent, titler, hover |
| GOLD_BRIGHT | `#E8C547` | Aktive states, glow |
| GOLD_DARK | `#B8923A` | Pressed states |
| RED_ACCENT | `#C45C5C` | Fejl, sletning |

### Tekst
| Token | HEX | Brug |
|-------|-----|------|
| TEXT_PRIMARY | `#E8E4D9` | Primaer tekst (cream) |
| TEXT_SECONDARY | `#7FBFB5` | Sekundaer (mint) |
| TEXT_MUTED | `#4A8080` | Nedtonet |

---

## Typografi

**Display (titler):** Bebas Neue, ALL CAPS
**Body (brodtekst):** Rajdhani, weight 400-600

| Element | Font | Size | Letter-spacing | Weight |
|---------|------|------|----------------|--------|
| Hovedtitel | Bebas Neue | 56px | 22px | - |
| Undertitel | Rajdhani | 16px | 5px | 500 |
| Sektion-header | Bebas Neue | 21px | 5px | - |
| Tool-navn | Bebas Neue | 18px | 3px | - |
| Tool-beskrivelse | Rajdhani | 13px | 0 | 500 |
| Drop zone tekst | Bebas Neue | 20px | 4px | - |
| Fil-navn | Rajdhani | 15px | 0 | 600 |
| Fil-meta | Rajdhani | 13px | 0 | - |

---

## Komponenter

### Tool Tiles
- Background: gradient 160deg, teal/dark
- Border: 1px solid `#2D5A5A`, radius 6px
- Padding: 20px 12px, height: 130px
- Expand to fill grid columns (ikke fixed width)
- **Hover:** border gold, shadow 12px/40px, text `#E8C547`, icon glow
- **Active:** shadow 6px/25px
- **Dekor:** Top guld-linje (fade in), bund mint-linje (grow 0-60%)

### Drop Zone
- Border: 2px solid `#2D5A5A`, radius 8px
- Padding: 45px 30px, min-height: 200px
- Inner dashed border: 12px inset (8px on hover)
- **Hover:** border gold, gradient baggrund, icon glow

### File List
- Border: 1px solid `#2D5A5A`, radius 6px
- Item padding: 14px 18px
- Action buttons: 28x28, transparent bg, teal border
- **Hover:** gold border, gold text

---

## Dekorative elementer

### Vertikale Art Deco linjer
- Positioner: 5%, 12%, 88%, 95% fra venstre
- Gradient: transparent -> teal -> mint -> teal -> transparent
- Opacity: 0.2

### Spacing
| Element | Margin |
|---------|--------|
| Header bottom | 40px |
| Section title bottom | 20px |
| Tools section bottom | 35px |
| Grid gap | 12px |
| Drop zone bottom | 25px |

### Responsivt grid
- \>600px: 4 kolonner
- 400-600px: 3 kolonner
- <400px: 2 kolonner

---

## Regler

- Brug KUN farver fra paletten
- SVG ikoner - ALDRIG emojis
- Letter-spacing KUN pa Bebas Neue tekst
- Tiles SKAL expand i grid
- Alle transitions: 300ms ease
