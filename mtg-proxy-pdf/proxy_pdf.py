#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "reportlab>=4.0",
#     "requests>=2.31",
#     "Pillow>=10.0",
# ]
# ///
"""
mtg-proxy-pdf — turn an MTG decklist into a print-ready A4 proxy-sheet PDF.

Pipeline:
    decklist text -> parse -> resolve each card on Scryfall -> download images
    -> lay out 3x3 (nine) cards per A4 page at the real Magic card size
       (63 x 88 mm) with corner crop marks -> write the PDF.

Locked design decisions (agreed with the user):
  * Card images come from the Scryfall API (auto-download, cached on disk).
  * 3x3 = 9 cards per A4 page, real card size 63 x 88 mm, with a gutter and
    corner crop marks so each card can be cut out individually and precisely.
  * Double-faced cards (transform / modal_dfc / ...): FRONT face only.
  * A card whose image cannot be found is SKIPPED; every miss is listed in a
    summary at the end. The PDF is still produced for everything that resolved.

Run it with uv — no manual install needed, uv builds the environment from the
inline metadata block above:

    uv run proxy_pdf.py mydeck.txt --out proxies.pdf
    pbpaste | uv run proxy_pdf.py - --out proxies.pdf
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

try:
    import requests
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas
except ModuleNotFoundError as exc:  # pragma: no cover - dependency guard
    sys.stderr.write(
        f"Missing dependency: {exc.name}.\n"
        "Run this script with uv so dependencies install automatically:\n"
        "    uv run proxy_pdf.py mydeck.txt --out proxies.pdf\n"
    )
    sys.exit(1)


# --- Layout constants -------------------------------------------------------

# A genuine Magic card is 63 x 88 mm. Printing proxies at this exact size lets
# them sit in a sleeve in front of (or behind) a real card with no trimming.
CARD_W_MM = 63.0
CARD_H_MM = 88.0
COLS, ROWS = 3, 3
PER_PAGE = COLS * ROWS  # 9 cards per A4 page

DEFAULT_GAP_MM = 4.0   # gutter between cards: room for crop marks + clean cuts
DEFAULT_CROP_MM = 3.0  # length of each corner crop-mark tick
CROP_LINE_PT = 0.4     # crop-mark stroke width (thin hairline)


# --- Scryfall constants -----------------------------------------------------

SCRYFALL_API = "https://api.scryfall.com"
SCRYFALL_NAMED = f"{SCRYFALL_API}/cards/named"
USER_AGENT = "mtg-proxy-pdf/1.0 (proxy sheet generator)"
REQUEST_DELAY_S = 0.12  # politeness delay between Scryfall network calls

# At each quality we fall back to the next-best image if it is unavailable.
# Scryfall "png" is 745x1040 -> ~300 dpi at 63x88 mm, ideal for printing.
QUALITY_FALLBACK = {
    "png": ["png", "large", "normal"],
    "large": ["large", "normal", "png"],
    "normal": ["normal", "large", "png"],
}

BASIC_LAND_NAMES = {
    "Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes",
    "Snow-Covered Plains", "Snow-Covered Island", "Snow-Covered Swamp",
    "Snow-Covered Mountain", "Snow-Covered Forest", "Snow-Covered Wastes",
}

# Bare section labels found in decklist exports; skipped, never treated as cards.
SECTION_HEADERS = {
    "deck", "mainboard", "main", "sideboard", "sb", "commander",
    "companion", "maybeboard", "tokens",
}

# "4 Lightning Bolt" / "4x Lightning Bolt" / "1 Delver of Secrets (ISD) 51"
# "2 Mountain (M21) 274 *F*" / "Counterspell"  (quantity optional -> 1)
LINE_RE = re.compile(
    r"""^\s*
        (?:(?P<qty>\d+)\s*[xX]?\s+)?              # optional quantity
        (?P<name>.+?)                              # card name (non-greedy)
        (?:\s+\((?P<set>[A-Za-z0-9]{2,6})\)\s*     # optional (SET)
            (?P<num>[0-9A-Za-z-]+))?               # optional collector number
        (?:\s+[*][^*]*[*])?                        # optional *F* / *E* marker
        \s*$""",
    re.VERBOSE,
)


# --- Deck parsing -----------------------------------------------------------

@dataclass
class DeckEntry:
    name: str
    count: int
    set_code: "str | None" = None
    collector: "str | None" = None

    @property
    def identity(self) -> tuple:
        if self.set_code and self.collector:
            return ("setnum", self.set_code.lower(), self.collector.lower())
        return ("name", self.name.lower())

    @property
    def label(self) -> str:
        if self.set_code and self.collector:
            return f"{self.name} ({self.set_code.upper()}) {self.collector}"
        return self.name


def parse_deck(text: str) -> "list[DeckEntry]":
    """Parse decklist text into ordered DeckEntry rows.

    Tolerates blank lines, ``#``/``//`` comments, and bare section headers
    (Deck / Sideboard / Commander / ...). Quantity is optional, defaulting to 1.
    """
    entries: "list[DeckEntry]" = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        if line.lower().rstrip(":") in SECTION_HEADERS:
            continue
        match = LINE_RE.match(line)
        if not match:
            continue
        name = match.group("name").strip()
        if not name:
            continue
        qty = int(match.group("qty")) if match.group("qty") else 1
        entries.append(DeckEntry(
            name=name,
            count=qty,
            set_code=match.group("set"),
            collector=match.group("num"),
        ))
    return entries


# --- Scryfall resolution + image download -----------------------------------

@dataclass
class ResolvedCard:
    label: str
    image_path: Path


def _session() -> "requests.Session":
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
    return session


def _get_json(session, url, params=None):
    try:
        resp = session.get(url, params=params, timeout=20)
        time.sleep(REQUEST_DELAY_S)
        if resp.status_code != 200:
            return None
        return resp.json()
    except (requests.RequestException, ValueError):
        return None


def _fetch_card(session, entry: DeckEntry):
    """Resolve a DeckEntry to a Scryfall card object, or None."""
    if entry.set_code and entry.collector:
        url = f"{SCRYFALL_API}/cards/{entry.set_code.lower()}/{entry.collector.lower()}"
        card = _get_json(session, url)
        if card:
            return card
        # Bad set/collector: fall back to a fuzzy name lookup.
    return _get_json(session, SCRYFALL_NAMED, params={"fuzzy": entry.name})


def pick_image_url(card: dict, quality: str) -> "str | None":
    """Best FRONT-face image URL at the requested quality (with fallbacks).

    Double-faced layouts (transform, modal_dfc, ...) have no top-level
    ``image_uris``; their front face lives in ``card_faces[0]``.
    """
    order = QUALITY_FALLBACK.get(quality, QUALITY_FALLBACK["png"])
    uris = card.get("image_uris")
    if not uris:
        faces = card.get("card_faces") or []
        if faces and isinstance(faces[0], dict):
            uris = faces[0].get("image_uris")
    if not uris:
        return None
    for q in order:
        if uris.get(q):
            return uris[q]
    return None


def _cache_key(identity: tuple, quality: str) -> str:
    safe = "_".join(str(p) for p in identity)
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", safe).strip("-")
    return f"{safe}__{quality}"


def _find_cached(cache_dir: Path, key: str) -> "Path | None":
    for ext in (".png", ".jpg", ".jpeg"):
        path = cache_dir / (key + ext)
        if path.exists() and path.stat().st_size > 0:
            return path
    return None


def resolve_card(session, entry: DeckEntry, quality: str, cache_dir: Path):
    """Return a ResolvedCard (image on disk) or None if it cannot be found."""
    key = _cache_key(entry.identity, quality)
    cached = _find_cached(cache_dir, key)
    if cached:
        return ResolvedCard(label=entry.label, image_path=cached)

    card = _fetch_card(session, entry)
    if not card:
        return None
    img_url = pick_image_url(card, quality)
    if not img_url:
        return None

    try:
        resp = session.get(img_url, timeout=30)
        time.sleep(REQUEST_DELAY_S)
        resp.raise_for_status()
    except requests.RequestException:
        return None

    ext = ".png" if ".png" in img_url.lower() else ".jpg"
    out_path = cache_dir / (key + ext)
    out_path.write_bytes(resp.content)
    return ResolvedCard(label=card.get("name", entry.label), image_path=out_path)


def resolve_deck(entries: "list[DeckEntry]", quality: str, cache_dir: Path):
    """Resolve every unique card once, then expand to an ordered slot list.

    Returns ``(image_paths, missing_labels)`` where image_paths honors deck
    order and per-card quantities.
    """
    session = _session()
    seen: dict = {}
    uniques: "list[DeckEntry]" = []
    for entry in entries:
        if entry.identity not in seen:
            seen[entry.identity] = entry
            uniques.append(entry)

    resolved: dict = {}
    missing: "list[str]" = []
    for idx, entry in enumerate(uniques, 1):
        card = resolve_card(session, entry, quality, cache_dir)
        status = "ok" if card else "MISSING"
        print(f"  [{idx}/{len(uniques)}] {entry.label} ... {status}", file=sys.stderr)
        if card:
            resolved[entry.identity] = card
        else:
            missing.append(entry.label)

    slots: "list[Path]" = []
    for entry in entries:
        card = resolved.get(entry.identity)
        if card:
            slots.extend([card.image_path] * entry.count)
    return slots, missing


# --- PDF generation ---------------------------------------------------------

def _draw_crop_marks(c, x, y, w, h, length):
    """Draw four L-shaped corner ticks pointing outward from a card rect."""
    c.saveState()
    c.setLineWidth(CROP_LINE_PT)
    c.setStrokeColorRGB(0, 0, 0)
    # (corner x, corner y, horizontal direction, vertical direction)
    corners = [
        (x,     y,     -1, -1),  # bottom-left
        (x + w, y,      1, -1),  # bottom-right
        (x,     y + h, -1,  1),  # top-left
        (x + w, y + h,  1,  1),  # top-right
    ]
    for cx, cy, sx, sy in corners:
        c.line(cx, cy, cx + sx * length, cy)  # horizontal tick
        c.line(cx, cy, cx, cy + sy * length)  # vertical tick
    c.restoreState()


def build_pdf(slots: "list[Path]", out_path: Path, gap_mm: float,
              crop_mm: float, crop_marks: bool = True) -> int:
    """Lay out card images 9-per-A4-page and write the PDF. Returns page count."""
    page_w, page_h = A4  # points
    card_w, card_h = CARD_W_MM * mm, CARD_H_MM * mm
    gap = gap_mm * mm
    grid_w = COLS * card_w + (COLS - 1) * gap
    grid_h = ROWS * card_h + (ROWS - 1) * gap
    if grid_w > page_w or grid_h > page_h:
        raise SystemExit(
            f"Error: the 3x3 grid is {grid_w / mm:.1f} x {grid_h / mm:.1f} mm "
            f"with --gap {gap_mm} mm and does not fit on A4. Reduce --gap."
        )
    margin_x = (page_w - grid_w) / 2
    margin_y = (page_h - grid_h) / 2

    c = canvas.Canvas(str(out_path), pagesize=A4)
    for i, img_path in enumerate(slots):
        slot = i % PER_PAGE
        if i > 0 and slot == 0:
            c.showPage()
        col = slot % COLS
        row = slot // COLS  # row 0 is the top row
        x = margin_x + col * (card_w + gap)
        y = page_h - margin_y - row * (card_h + gap) - card_h
        c.drawImage(
            ImageReader(str(img_path)), x, y,
            width=card_w, height=card_h,
            preserveAspectRatio=False, mask="auto",
        )
        if crop_marks:
            _draw_crop_marks(c, x, y, card_w, card_h, crop_mm * mm)
    c.showPage()
    c.save()
    return (len(slots) + PER_PAGE - 1) // PER_PAGE


# --- CLI --------------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate an A4 MTG proxy-sheet PDF from a decklist "
                    "(card images fetched from Scryfall).",
    )
    parser.add_argument("deck", nargs="?",
                        help="Decklist file path, or '-' to read from stdin.")
    parser.add_argument("--deck", dest="deck_opt",
                        help="Decklist file path, or '-' for stdin (alternative to positional).")
    parser.add_argument("--out", "-o", default="proxies.pdf",
                        help="Output PDF path (default: proxies.pdf).")
    parser.add_argument("--gap", type=float, default=DEFAULT_GAP_MM,
                        help=f"Gutter between cards in mm (default: {DEFAULT_GAP_MM}).")
    parser.add_argument("--quality", choices=["png", "large", "normal"], default="png",
                        help="Scryfall image quality (default: png, ~300 dpi).")
    parser.add_argument("--cache-dir", default=None,
                        help="Image cache directory (default: <tempdir>/mtg-proxy-cache).")
    parser.add_argument("--skip-basics", action="store_true",
                        help="Skip basic lands (Plains / Island / Swamp / Mountain / Forest / Wastes).")
    parser.add_argument("--singleton", action="store_true",
                        help="Print one copy of each card, ignoring deck quantities.")
    parser.add_argument("--no-crop-marks", action="store_true",
                        help="Do not draw corner crop marks.")
    args = parser.parse_args(argv)

    deck_src = args.deck_opt or args.deck
    if not deck_src:
        parser.error("provide a decklist file (positional or --deck), or '-' for stdin")
    if deck_src == "-":
        text = sys.stdin.read()
    else:
        path = Path(deck_src)
        if not path.is_file():
            parser.error(f"decklist not found: {deck_src}")
        text = path.read_text(encoding="utf-8")

    entries = parse_deck(text)
    if args.skip_basics:
        entries = [e for e in entries if e.name not in BASIC_LAND_NAMES]
    if args.singleton:
        entries = [DeckEntry(e.name, 1, e.set_code, e.collector) for e in entries]
    if not entries:
        raise SystemExit("Error: no cards parsed from the decklist.")

    total = sum(e.count for e in entries)
    uniq = len({e.identity for e in entries})
    print(f"Parsed {total} cards ({uniq} unique). Fetching images from Scryfall...",
          file=sys.stderr)

    cache_dir = (Path(args.cache_dir) if args.cache_dir
                 else Path(tempfile.gettempdir()) / "mtg-proxy-cache")
    cache_dir.mkdir(parents=True, exist_ok=True)

    slots, missing = resolve_deck(entries, args.quality, cache_dir)
    if not slots:
        raise SystemExit("Error: no card images could be resolved; nothing to write.")

    out_path = Path(args.out)
    pages = build_pdf(slots, out_path, args.gap, DEFAULT_CROP_MM,
                      crop_marks=not args.no_crop_marks)

    print(f"\nWrote {out_path}  —  {len(slots)} cards across {pages} page(s), "
          f"9 per A4 at {CARD_W_MM:.0f}x{CARD_H_MM:.0f} mm.", file=sys.stderr)
    if missing:
        print(f"\n{len(missing)} card(s) could NOT be found and were skipped:",
              file=sys.stderr)
        for label in missing:
            print(f"  - {label}", file=sys.stderr)
        print("Check spelling, or specify an exact '(SET) collector#'.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
