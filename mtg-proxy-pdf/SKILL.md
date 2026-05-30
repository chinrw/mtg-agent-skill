---
name: mtg-proxy-pdf
description: Use when turning an MTG decklist into a print-ready proxy PDF — A4 pages with nine cards per sheet at true Magic card size (63x88 mm) and corner crop marks for clean cutting. Card images auto-download from Scryfall. Triggers — "make proxies", "proxy PDF", "print my deck", "proxy sheet", "print cards to cut out", "print cards at real size". Produces sleeve-ready proxies. NOT for deck analysis or card evaluation.
disable-model-invocation: true
---

# MTG Proxy PDF

## Overview

Turn a decklist into a print-ready PDF of proxies. Each A4 page holds **nine
cards (3×3)** at the **real Magic card size, 63×88 mm**, with a gutter and
corner crop marks so every card can be cut out individually and precisely.
Card images are fetched automatically from the **Scryfall API**.

The whole job is done by one script: **`proxy_pdf.py`**, run with **`uv`**
(no manual install — `uv` builds the environment from the script's inline
dependency metadata).

Print → cut along the crop marks → sleeve the proxy (with a real card or a
piece of cardstock behind it for rigidity). Done.

## The Iron Law

```
GENERATE PROXIES ONLY WITH proxy_pdf.py VIA uv.
NEVER hand-assemble the PDF, guess card dimensions, or scale images by eye.

The script encodes the exact 63x88 mm card size, the 9-up A4 layout, the
crop marks, the DFC front-face handling, and the Scryfall fetch. Reproducing
any of that by hand produces cards that are the wrong size and will not fit a
sleeve. If the layout needs to change, change a flag or the script — not the math.
```

## When to Use

Use this skill when the user wants to **physically print MTG cards to cut out**:

- "Make proxies / a proxy PDF for this deck"
- "Print my decklist so I can cut the cards out and sleeve them"
- "Generate a proxy sheet at real card size"
- "I have a list of cards — turn it into something printable"

**Do NOT use this skill for:**

- Deck analysis, meta positioning, sideboard plans → use `mtg-deck-analysis`
- Whether a card belongs in a deck → use `mtg-card-evaluation`
- Custom card art, custom frames, or fake-rares — this prints the real
  Scryfall card image as-is.

## Prerequisites

- **`uv`** installed (`uv --version`). It manages the Python deps and the venv.
- **Internet access** for the first run of any new card (Scryfall download).
  Downloaded images are cached on disk, so re-runs are fast and offline-friendly.

## Quick Start

Run from this skill's directory (or use the script's absolute path):

```bash
# From a decklist file
uv run proxy_pdf.py mydeck.txt --out proxies.pdf

# From stdin (e.g. pasted list)
pbpaste | uv run proxy_pdf.py - --out proxies.pdf

# Built-in smoke-test deck (8 cards, one page)
uv run proxy_pdf.py samples/sample-deck.txt --out /tmp/proxies.pdf
```

The first run installs `reportlab`, `requests`, and `Pillow` into a uv-managed
environment automatically — there is nothing to `pip install`.

## Decklist Input Format

One card per line. Flexible and forgiving:

```
# Comments (#, //) and blank lines are ignored.
Deck                         <- bare section headers are skipped
4 Lightning Bolt             <- "4 Name"
4x Counterspell              <- "4x Name" also works
1 Delver of Secrets          <- double-faced card: prints FRONT face only
2 Mountain (M21) 274         <- "(SET) collector#" pins an exact printing/art
Brainstorm                   <- no quantity = 1
Sideboard                    <- sideboard cards are included too
2 Surgical Extraction
```

## Options

| Flag | Default | Purpose |
|---|---|---|
| `deck` (positional) or `--deck` | — | Decklist file, or `-` for stdin (required) |
| `--out`, `-o` | `proxies.pdf` | Output PDF path |
| `--gap` | `4.0` | Gutter between cards in mm (room for crop marks + cuts) |
| `--quality` | `png` | Scryfall image: `png` (~300 dpi, best), `large`, or `normal` |
| `--skip-basics` | off | Omit basic lands (Plains/Island/Swamp/Mountain/Forest/Wastes) |
| `--singleton` | off | One copy of each card, ignoring deck quantities |
| `--no-crop-marks` | off | Omit the corner crop marks |
| `--cache-dir` | `<tempdir>/mtg-proxy-cache` | Where downloaded images are cached |

## How It Works

1. **Parse** the decklist (quantities, `(SET) collector#`, comments, sections).
2. **Resolve** each unique card on Scryfall (fuzzy name match, or exact
   set+collector when given), then **download** its image (cached on disk).
3. **Lay out** the images 9-per-A4-page at exactly 63×88 mm, centered, with a
   `--gap` mm gutter and corner crop marks.
4. **Write** the PDF and print a summary.

Locked behaviors:

- **Double-faced cards** (transform / modal DFC / …): the **front face only**
  is printed (Scryfall serves it in `card_faces[0]`).
- **A card whose image can't be found is skipped**, not fatal. The PDF is still
  produced for everything that resolved, and every miss is listed at the end so
  you can fix spelling or pin a `(SET) collector#`.

## Printing Guide (read this — it is the #1 mistake)

The PDF only yields real-size cards if you print it at real size:

- Paper size: **A4**.
- Scale: **100% / "Actual size"**. **Turn OFF "Fit to page" / "Shrink to fit"** —
  fit-to-page silently shrinks the cards and they will no longer fit a sleeve.
- Margins: **None / minimum** (the layout already centers within A4 margins).
- Then **cut along the crop marks**; each card is 63×88 mm.
- Sleeve the proxy, ideally with a real card or cardstock behind it for feel.

## Verifying Output

Confirm the geometry is correct (page = A4, every card = 63×88 mm):

```bash
uv run --with pymupdf python -c "
import fitz
mm = 2.834645669
d = fitz.open('proxies.pdf'); p = d[0]
print('pages:', d.page_count, '| page mm:', round(p.rect.width/mm,1), 'x', round(p.rect.height/mm,1))
for i, im in enumerate(p.get_image_info()):
    b = im['bbox']; print(f'card {i}: {(b[2]-b[0])/mm:.2f} x {(b[3]-b[1])/mm:.2f} mm')
"
# Expect: page 210.0 x 297.0; every card 63.00 x 88.00 mm.
```

For a visual check, render a page: `d[0].get_pixmap(dpi=120).save('preview.png')`.

## Common Mistakes

| Symptom | Cause / Fix |
|---|---|
| Printed cards are too small / don't fit sleeves | Printed with "Fit to page". Reprint at **100% / Actual size**. |
| A card is missing from the PDF | Name not found on Scryfall. Check the end-of-run summary; fix spelling or use `(SET) collector#`. |
| Double-faced card only shows one side | Expected — front face only by design. Add the back's name as its own line if you need it. |
| `Missing dependency` error | You ran it with bare `python`. Use **`uv run proxy_pdf.py …`**. |
| Slow first run | Each new card is downloaded once from Scryfall (with a polite delay). Re-runs hit the on-disk cache and are fast. |
| Grid "does not fit on A4" error | `--gap` is too large. Lower it (default 4 mm). |
