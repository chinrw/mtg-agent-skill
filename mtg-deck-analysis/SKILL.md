---
name: mtg-deck-analysis
description: Use when analyzing Magic the Gathering decklists, evaluating whether a card belongs in a specific deck, predicting matchup performance against current meta, comparing two decks, or recommending optimizations. Apply whenever card-name-based assumptions or stale training data would mislead the analysis.
disable-model-invocation: true
---

# MTG Deck Analysis

## Overview

MTG card knowledge from training data is stale and unreliable. Card names mislead. Ban lists change monthly. Set releases shift the meta. Cards get errata.

Core principle: **A card's name, your recall of it, or an analogy is not evidence. Scryfall Oracle text is.**

## When to Use

- Decklist evaluation
- "Should I add card X to deck Y" — for this specific question, invoke the sibling `mtg-card-evaluation` skill via the Skill tool (see **Sub-Skills and References** below)
- For "how does card X fit format Y's current meta?" questions (no target deck given) — invoke the sibling `mtg-card-evaluation` skill in **Mode B (card-in-meta positioning)**.
- Comparing two decks
- Predicting matchup performance vs current meta
- Probability or math questions about a deck
- Recommending optimizations

## The Iron Law

```
NO REASONING WITHOUT VERIFICATION
NO ANALYSIS WITHOUT AN IDENTIFIED FORMAT
```

This applies to **every** card you cite — not only the ones being analyzed. Cards used as math inputs (e.g., "4 Mishra's Workshop as enabler") or interaction examples (e.g., "Chalice@2 catches Counterspell") count equally. A claim citing a banned or unplayed card invalidates the whole conclusion.

**Format-binding discipline.** The format identified in Step 0 is bound to the analysis run. All downstream paths and queries (`reference-tables/<format>.md`, `samples/<format>/`, mtgtop8 `?f=LE`/`?f=MO`, B&R `banned:legacy`/`banned:modern`) branch on this single string. Never silently swap formats mid-analysis. If a card you're citing turns out to be illegal in the identified format, that's a flag to investigate (wrong format identified? wrong card name? card moved between formats?), NOT a license to switch formats.

## Workflow

**Step 0 — Identify the format. MANDATORY.** This step runs before every analysis. The skill refuses to proceed without an identified format. Result is a string `format ∈ {legacy, modern}` bound for the rest of the run.

**Decision rule (simple, on purpose):**

1. **Explicit user statement (always honored, never overridden).**
   - "Modern: [decklist]" / "Legacy: [decklist]" / "in Modern, ..." / "for my Legacy deck, ..." → use that format verbatim. Do NOT second-guess via card observations even if cards look unusual. (B&R violations against the user-asserted format become Step 3 findings, NOT format reassignments.)

2. **Otherwise, ASK the user.** Do NOT try to infer the format from card heuristics — even when observations strongly suggest one format, the cost of asking is one short prompt; the cost of guessing wrong is a whole analysis built on the wrong banlist and the wrong meta. **When not sure, just ask.**

   When asking, you MAY include a one-line hint based on observed cards — this saves the user typing on obvious cases, but the answer is still up to them:

   > "Which format are you analyzing? (legacy / modern). Hint: I see `Wasteland` in your list, which suggests Legacy — confirm or correct."

   > "Which format are you analyzing? (legacy / modern). Hint: I see `Ragavan, Nimble Pilferer` + `Wrenn and Six` — looks Modern; confirm or correct."

   > "Which format are you analyzing? (legacy / modern). Cards present (e.g., Lightning Bolt, Counterspell, Snapcaster Mage) are legal in both — no hint to offer."

   The skill refuses to proceed until the user answers.

3. **Rule 3 — Unsupported formats.** If the user explicitly requests a format outside `{legacy, modern}` (e.g., Pioneer, Pauper, Standard, Commander), refuse with: 'This skill currently supports Legacy and Modern only. Please rephrase as a Legacy or Modern question, or invoke a different skill that targets your format.' Do NOT silently fall through to a default format.

**Why this is simple by design:** previous drafts of Step 0 tried to auto-decide format from "hard signal" card lists. That approach failed twice during skill authoring — first by misclassifying Boseiju's speed/scope, then by classifying Solitude/Subtlety/Endurance as hard Modern signals when they're actually legal in both formats. The taxonomy is fragile because B&R announcements change card legality every few months, and a 6-month-stale signal list silently produces wrong format identifications. Asking the user is robust against B&R drift; auto-detection isn't.

**Optional hint reference (suggestion only — never a decision):**

When forming the hint, you may consult Scryfall live for any card whose `modern` and `legacy` legalities differ. For convenience, examples that often signal a format (verify via Scryfall before quoting them as the hint reason):

- Often-Legacy-only-played: Wasteland, Brainstorm, Ponder, Daze, Force of Will, original-dual lands (Volcanic Island, etc.)
- Often-Modern-only-played: Ragavan Nimble Pilferer, Wrenn and Six (both Legacy-banned at last fetch)
- Legal-in-both (do NOT use as hint reason): Counterspell, Lightning Bolt, Snapcaster Mage, Force of Negation, Solitude, Subtlety, Endurance, The One Ring, Murktide Regent, shock lands, fetch lands

These lists are only for forming the hint sentence; the user's answer is what gets bound to `format` for the run.

**Output of Step 0:** state the identified format and the evidence:

> "Format: Modern (user-confirmed; cited evidence: 4 Ragavan + 4 Wrenn and Six in mainboard)"

> "Format: Legacy (explicit format prefix in user input)"

> "Format: ASKING USER — input cards [Lightning Bolt, Counterspell, Force of Will] legal in both formats."

This becomes the citable first sentence of the analysis output.

**Step 1 — Read literally.** Note every card name. Flag any you're not 100% sure of.

**Step 2 — Verify Oracle text via Scryfall API.** `WebFetch` returns 403 against `api.scryfall.com`. Use `curl` with `User-Agent` + `Accept` headers — see the Scryfall block under "Tooling" below for the exact command and batch loop. Capture: Oracle text, type, subtypes, mana value, MDFC faces. Re-verify every card before citing.

**Step 3 — Verify the format ban list.** Prefer the Scryfall API banlist endpoint (parseable JSON, faster) over the Wizards HTML page:

- **Primary:** `https://api.scryfall.com/cards/search?q=banned%3A<format>&order=name` (replace `<format>` with `legacy` or `modern`). Returns full card objects in `data[]`. Filter `border_color != "silver"` to exclude joke entries. Verified counts as of 2026-05-25: Legacy 169, Modern 52.
- **Secondary (tiebreaker, especially on B&R announcement day where Scryfall may lag):** `https://magic.wizards.com/en/banned-restricted-list`, grep section per format.

Use the `curl` block in Tooling below for both. No banlist is cached in this skill. Cite the URL + fetch date + source (`Scryfall API banned:<format>` or `Wizards B&R - <format> section`). If both URLs unreachable, refuse to assert ban status — do not fall back to memory.

Per-format reference for verification URLs: `reference-tables/<format>.md` "Live Banlist Verification Sources" section.

**Step 4 — Verify current meta archetypes.** Pull top 10 by share from mtgtop8 for the bound format (`?f=LE` for Legacy, `?f=MO` for Modern — see "mtgtop8 Decklist Parser" below). curl with UA works; mtgdecks and aetherhub are Cloudflare-blocked — see the source-reliability matrix below. Note the date and `meta=` code (different per format).

**Step 4b — Verify deck PRESENCE, not just card existence.** Before claiming an interaction matters (e.g., "Chalice@2 catches Counterspell"), confirm the target card is **actually mainboarded** in current decklists. First check `samples/<format>/` (e.g., `samples/legacy/`) for a recent sample of that archetype (see **Using Sample Decklists** below for the staleness check); if the sample is fresh and you only need 1 deck per archetype, that's enough. For 2–3 decklists per archetype (the standard for inclusion claims), parse live from mtgtop8 with the parser below. Drop any interaction claim whose target card is absent. Card legality ≠ card play rate.

**Step 5 — Identify critical interactions.** Subtypes, mana value (not paid cost), mana vs activated abilities, MDFC graveyard semantics, trigger conditions, **and the "already-resolved permanent" semantics** — Chalice / Trinisphere / Thalia / Sphere only tax future casts; they don't undo permanents that already resolved. See `reference-tables/<format>.md` (e.g., `reference-tables/legacy.md`).

**Step 6 — Compute probabilities in Python.** Never write "approximately X%". Use `python3` with `math.comb` (template under "Tooling" below). For tempo questions, ALSO compute the conditional: P(your lock card resolves BEFORE opp's threats deploy). Chalice on the draw against tempo is often "too late" — ~95% of opponents deploy a T1 threat.

**Step 6b — Run deterministic validators on the parsed decklist.** Before drawing inferential conclusions ("the deck looks like X", "this seems uncastable", "deck is ~80% similar to UR Tempo"), run the relevant Python validators in the **Deterministic Validators** block under Tooling below. Each validator turns a vibe-based judgment into a citable number. **At minimum**: run mana-base color validation (catches uncastable cards) and 4-of legality. **When relevant**: archetype similarity vs samples, color devotion (combo decks), N-card joint probability (Tron/combo openers), cantrip filtering depth (combo decks with Brainstorm/Ponder/Flow State). Quote the validator's output verbatim in your analysis; do NOT paraphrase numbers.

**Step 7 — Label evidence types.** Every claim is one of:
- **Sourced fact** (Scryfall Oracle / Wizards B&R)
- **Verified data** (tournament decklist with URL)
- **Inference** (your derivation, math result)
- **Recommendation** (proposed action)

Never mix categories.

## Tooling — How to Get the Data

This skill never auto-loads (`disable-model-invocation: true`), so all the fetch patterns live inline. Use these as-is.

### Scryfall API — Card Oracle Text

**`WebFetch` returns 403** against `api.scryfall.com`. Scryfall's [API policy](https://scryfall.com/docs/api) requires every request to send both a `User-Agent` and an `Accept` header. WebFetch sends neither.

**Use `curl` via Bash, not WebFetch.**

#### Single-card fetch

```bash
curl -sS \
  -H "User-Agent: mtg-deck-analysis/1.0 (your-email@example.com)" \
  -H "Accept: application/json" \
  -G --data-urlencode "exact=Chalice of the Void" \
  "https://api.scryfall.com/cards/named" \
  | jq -r '"\(.name) | \(.mana_cost//"none") | MV \(.cmc) | \(.type_line) | \((.oracle_text//"—") | gsub("\n";" / "))"'
```

Key flags:
- `-G --data-urlencode "exact=NAME"` — URL-encodes spaces, apostrophes, accents correctly
- `exact=` — requires an exact name match. Use `fuzzy=` only when you're sure no near-collision exists
- `jq -r` — extracts `name`, `mana_cost`, `cmc` (mana value), `type_line`, `oracle_text` and collapses line breaks

#### Batch fetch (multiple cards)

```bash
H1="User-Agent: mtg-deck-analysis/1.0 (you@example.com)"
H2="Accept: application/json"
cards=("Chalice of the Void" "Flow State" "Brainstorm" "Daze")
for c in "${cards[@]}"; do
  curl -sS -H "$H1" -H "$H2" -G --data-urlencode "exact=$c" \
    "https://api.scryfall.com/cards/named" \
    | jq -r '"\(.name) | \(.mana_cost//"none") | MV \(.cmc) | \(.type_line) | \((.oracle_text//"—") | gsub("\n";" / "))"'
  sleep 0.12  # Scryfall asks for 50-100ms between requests
done
```

#### Notes and gotchas

- **MDFCs** (Delver of Secrets, Tamiyo Inquisitive Student) return `mana_cost: ""` on the top-level object. Faces are under `.card_faces[0]` and `.card_faces[1]`. `.cmc` still gives the correct mana value of the front face.
  ```bash
  jq -r '.name + " | front: " + .card_faces[0].mana_cost + " | back: " + .card_faces[1].mana_cost'
  ```
- **Specific printings**: append `&set=mrd` to disambiguate when needed.
- **Rate limit**: 429 means slow down. Default `sleep 0.12`. Respect any `Retry-After` header.
- **Don't trust the search endpoint** for exact lookups — use `/cards/named`.

### Scryfall — Banlist (Live, Primary)

```bash
# Substitute <format> with: legacy, modern, etc.
curl -sS \
  -H 'User-Agent: mtg-agent-skill/1.0' \
  -H 'Accept: application/json' \
  'https://api.scryfall.com/cards/search?q=banned%3A<format>&order=name' \
  | jq -r '.data[].name'
```

Returns one banned card name per line. Use this as the PRIMARY banlist source per Step 3.

### Wizards B&R — Banlist (Live)

```bash
curl -sSL -H "User-Agent: mtg-deck-analysis/1.0" \
  "https://magic.wizards.com/en/banned-restricted-list" \
  > /tmp/banlist.html
```

Then grep for the format section heading and the card:

```bash
# Find the Legacy section
grep -n 'id="legacy-banned"' /tmp/banlist.html

# Find a specific card in context
grep -B2 -A2 -i "mishra" /tmp/banlist.html
```

The page lists bans under `<section id="<format>-banned">` with `<li>Card Name</li>` entries. WebFetch's summarization may flatten or omit cards — prefer raw curl + grep when verifying any specific card.

**Never cache the banlist in this skill.** Re-fetch every session that touches legality.

### Data Source Reliability (as of 2026-05)

| Source | curl+UA | WebFetch | Use for |
|---|---|---|---|
| `api.scryfall.com` | ✓ 200 | ✗ 403 | Card Oracle, MV, type — primary source |
| `magic.wizards.com` (B&R) | ✓ 200 | ✓ 200 | Live banlist |
| `mtgtop8.com` (archetype & event pages) | ✓ 200 | ✓ 200 (partial) | Meta share, decklists, top cards |
| `scryfall.com/card/...` (HTML) | mostly ✗ | mostly ✗ | Use the API instead |
| `mtgdecks.net` | ✗ 403 (Cloudflare) | ✗ 403 | Avoid for fetch; WebSearch snippets only |
| `aetherhub.com` | ✗ 403 (Cloudflare) | ✗ 403 | Avoid for fetch |
| `mtggoldfish.com` | mixed | mixed | Articles via WebSearch snippets |
| `edhrec.com` | varies | varies | EDH/Commander only; usually not needed |

**Rule:** if curl fails twice with proper headers, the site is Cloudflare-blocked for non-browser clients. Switch to WebSearch and quote only what the result snippet shows. Do NOT fabricate data from blocked sources.

### mtgtop8 Decklist Parser

mtgtop8 is the most reliable Legacy data source. Each decklist's mainboard entries follow this HTML pattern (verified May 2026):

```html
<div id="md<set><num>" class="deck_line hover_tr" onclick="AffCard('<set><num>','Card+Name','','');">
  N <span class=L14>Card Name</span>
</div>
```

Sideboard entries use `id="sb..."`.

#### Python parser

```python
import re
PATTERN = re.compile(
    r'<div\s+id=(?P<section>md|sb)[^"\s]+\s+class="deck_line[^"]*"[^>]*>\s*'
    r'(?P<count>\d+)\s*<span\s+class=L14>(?P<name>[^<]+)</span>',
    re.IGNORECASE,
)

def parse_deck(html_text):
    """Yield (count, card_name, section) where section in {'MD', 'SB'}."""
    for m in PATTERN.finditer(html_text):
        yield int(m.group("count")), m.group("name").strip(), m.group("section").upper()
```

#### Workflow: archetype → decklists → cards

```python
import urllib.request, re
headers = {"User-Agent": "mtg-deck-analysis/1.0 (you@example.com)"}

def fetch(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="replace")

# Format code from Step 0's identified format:
#   Legacy → "LE"    Modern → "MO"
# Pass through as f={fmt_code} in every URL.
FMT = "LE"  # or "MO" — bind from Step 0 result, do not hardcode

# 1. Find archetype IDs (one-time lookup per format)
fmt_page = fetch(f"https://www.mtgtop8.com/format?f={FMT}")
archetypes = re.findall(r'archetype\?a=(\d+)[^"]+>([^<]+)</a>', fmt_page)
# Legacy examples: 213 → UR Tempo, 1606 → Dimir Tempo, 553 → Eldrazi Aggro
# Modern examples: populated from mtgtop8 fetch 2026-05-25; check current top-archetype IDs at mtgtop8.com/format?f=MO

# 2. List recent decks for an archetype (note: meta code changes per period AND per format)
arch_page = fetch(f"https://www.mtgtop8.com/archetype?a=213&meta=338&f={FMT}")
decks = re.findall(rf'event\?e=(\d+)&d=(\d+)&f={FMT}', arch_page)

# 3. Fetch each decklist and parse cards (mainboard only)
for e, d in decks[:3]:
    html = fetch(f"https://www.mtgtop8.com/event?e={e}&d={d}&f={FMT}")
    for count, name, sec in parse_deck(html):
        if sec == "MD":
            print(count, name)
```

**Format URL summary:**

| Format | URL pattern | Verified 2026-05-25 |
|---|---|---|
| Legacy | `https://www.mtgtop8.com/format?f=LE` | 200 OK, ~83KB, title "Legacy events and metagame @ mtgtop8.com" |
| Modern | `https://www.mtgtop8.com/format?f=MO` | 200 OK, ~85KB, title "Modern events and metagame @ mtgtop8.com" |

**The `meta=NNN` code changes each meta period AND differs between formats.** Find the current one by grepping the format page for `<select` options or by checking the URL when you manually click "current 2 weeks". Legacy was `meta=34` in early May 2026, `meta=338` by late May. Modern's current code: fetch and inspect on Phase 3 / on day-of-analysis.

### Hypergeometric Probability Template

Use `python3` with `math.comb`. **Never write "approximately X%" — run the numbers.**

```python
from math import comb

def p_at_least_k(N, K, n, k=1):
    """P(>=k successes) — N=deck size, K=successes in deck, n=cards drawn."""
    return 1 - sum(comb(K, i) * comb(N - K, n - i) / comb(N, n)
                   for i in range(k))

def p_joint_two(N, K1, K2, n):
    """P(>=1 of A AND >=1 of B), disjoint card pools."""
    p_no_a = comb(N - K1, n) / comb(N, n)
    p_no_b = comb(N - K2, n) / comb(N, n)
    p_no_either = comb(N - K1 - K2, n) / comb(N, n)
    return 1 - p_no_a - p_no_b + p_no_either
```

#### Hand sizes by turn (60-card deck)

| Turn | On the play | On the draw |
|---|---|---|
| T1 | n=7 | n=8 |
| T2 | n=8 | n=9 |
| T3 | n=9 | n=10 |
| London mull to 6 | n≈10 (scry + bottom) | n≈11 |
| Mull to 5 | n≈12 | n≈13 |

#### Tempo-asymmetric scenarios (Chalice / lock pieces)

Compute BOTH sides of the race, not just yours:

```python
# Your side: P(Chalice + 2-mana enabler in opener on the play)
p_yours = p_joint_two(60, K1=4, K2=8, n=7)  # 4 Chalice, 8 enabler

# Their side: P(opp has any T1 deployable threat — they go first)
p_theirs = p_at_least_k(60, K=20, n=7, k=1)  # 20 MV-1 cards

# Your effective lock rate on the draw against a deploying opponent:
# Chalice@1 doesn't undo a resolved permanent → real "stops a threat" rate
# is much lower than p_yours when you're on the draw.
```

#### Joint with overlapping card types

If your "good cards" overlap (e.g., a card counts as both a threat AND a draw spell), `p_joint_two` over-counts. Switch to direct simulation or inclusion-exclusion across the actual disjoint subsets.

### Deterministic Validators (Python Helpers)

Run these BEFORE inferring anything about a deck. Each replaces a vibe-based judgment with a citable number. Workflow Step 6b mandates the first two; the rest are situational.

```python
# === Shared types ===
# A "parsed decklist" is a tuple (mainboard, sideboard) where each section
# is a list of (count, card_name) tuples. Build it once via mtgtop8 parser
# or by parsing user-pasted text per Step 1 + "Input format" section.

from math import comb
from itertools import combinations
import re
```

#### 1. Mana-base color validation — catches uncastable cards

```python
def validate_manabase(mainboard, scryfall_data):
    """
    Catch spells the deck can't cast because no land produces the colored mana.

    mainboard: list of (count, name)
    scryfall_data: dict mapping card_name -> Scryfall JSON
      (must include `produced_mana` for lands/permanents and `mana_cost` for spells)

    Returns: list of (name, missing_colors) for any spell whose colored
             requirements aren't met by the deck's mana sources.

    Caveat: doesn't model "spend only on X" restrictions (e.g., Eldrazi Temple
            only casts Eldrazi). Doesn't model City of Brass / Mana Confluence
            "any color" (those auto-pass). Strict subset check on {W,U,B,R,G}.
    """
    produced = set()
    for _, name in mainboard:
        data = scryfall_data.get(name, {})
        produced.update(data.get("produced_mana", []))

    uncastable = []
    for _, name in mainboard:
        data = scryfall_data.get(name, {})
        if "Land" in data.get("type_line", ""):
            continue  # lands don't need to be cast
        cost = data.get("mana_cost", "")
        required = set(re.findall(r'\{([WUBRG])\}', cost))
        missing = required - produced
        if missing:
            uncastable.append((name, sorted(missing)))
    return uncastable

# Usage:
# >>> validate_manabase(mb, scryfall_data)
# [('Punishing Fire', ['R'])]
```

#### 2. 4-of legality + card multiset

```python
def check_four_of(mainboard, sideboard, basic_lands=None):
    """
    Flag non-basic cards appearing > 4 times across mainboard + sideboard.

    basic_lands: set of names exempt from the 4-copy rule
                 (default: standard Magic basics + snow basics + wastes)

    Returns: list of (name, total_count) for any violation.
    """
    if basic_lands is None:
        basic_lands = {
            "Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes",
            "Snow-Covered Plains", "Snow-Covered Island", "Snow-Covered Swamp",
            "Snow-Covered Mountain", "Snow-Covered Forest",
        }
    # Cards explicitly allowed > 4: e.g., Relentless Rats, Persistent
    # Petitioners, Shadowborn Apostle, Rat Colony, Dragon's Approach,
    # Seven Dwarves (capped at 7), Slime Against Humanity.
    any_number = {
        "Relentless Rats", "Persistent Petitioners", "Shadowborn Apostle",
        "Rat Colony", "Dragon's Approach", "Slime Against Humanity",
        "Templar Knight",
    }

    totals = {}
    for section in (mainboard, sideboard):
        for count, name in section:
            totals[name] = totals.get(name, 0) + count
    violations = [
        (n, c) for n, c in totals.items()
        if c > 4 and n not in basic_lands and n not in any_number
    ]
    return violations

# Usage:
# >>> check_four_of(mb, sb)
# []  # legal
```

#### 3. Color devotion (for Thassa's Oracle / Painter's / mono-color combos)

```python
def devotion(permanents_on_battlefield, scryfall_data):
    """
    Count colored mana symbols (W,U,B,R,G) across permanents on battlefield.
    Doomsday/Thassa's Oracle wants devotion to blue >= 1 to win.
    Painter's Servant + mono-color check uses this.

    permanents_on_battlefield: list of card names assumed in play
    Returns: dict {color: int} mapping each color to its devotion count.
    """
    counts = {c: 0 for c in "WUBRG"}
    for name in permanents_on_battlefield:
        cost = scryfall_data.get(name, {}).get("mana_cost", "")
        for sym in re.findall(r'\{([WUBRG])\}', cost):
            counts[sym] += 1
        # Hybrid like {W/U} contributes to both: parse if needed.
        for sym in re.findall(r'\{([WUBRG])/([WUBRG])\}', cost):
            counts[sym[0]] += 1
            counts[sym[1]] += 1
    return counts

# Usage:
# >>> devotion(["Thassa's Oracle"], scryfall_data)
# {'W': 0, 'U': 2, 'B': 0, 'R': 0, 'G': 0}  # Oracle cost is {U}{U}, so 2 blue devotion
# (Comfortably above the >=1 threshold for Oracle's win trigger.)
```

#### 4. Archetype similarity vs samples (weighted Jaccard)

```python
def archetype_similarity(user_mainboard, sample_files):
    """
    Score user's mainboard against each sample deck. Returns ranked list.

    user_mainboard: list of (count, name) tuples
    sample_files: list of filesystem paths to sample .txt files

    Similarity = sum(min(user[card], sample[card]) for card in both)
               / sum(max(user[card], sample[card]) for card in either)
    (Weighted Jaccard on multisets — 0.0 = nothing in common, 1.0 = identical.)

    Returns: list of (sample_path, similarity_pct, shared_cards_count),
             sorted descending.
    """
    user = {n: c for c, n in user_mainboard}

    def parse_sample(path):
        out = {}
        for line in open(path):
            line = line.strip()
            if not line or line.lower() == "sideboard":
                if line.lower() == "sideboard":
                    break  # stop at SB boundary
                continue
            m = re.match(r'^(\d+)\s*[xX]?\s+(.+?)\s*$', line)
            if m:
                out[m.group(2)] = int(m.group(1))
        return out

    results = []
    for path in sample_files:
        sample = parse_sample(path)
        union_keys = set(user) | set(sample)
        if not union_keys:
            continue
        sum_min = sum(min(user.get(k, 0), sample.get(k, 0)) for k in union_keys)
        sum_max = sum(max(user.get(k, 0), sample.get(k, 0)) for k in union_keys)
        sim = sum_min / sum_max if sum_max else 0.0
        shared = sum(1 for k in union_keys if k in user and k in sample)
        results.append((path, round(sim * 100, 1), shared))
    return sorted(results, key=lambda r: -r[1])

# Usage — pull samples from the format-aware directory via format_data.py:
# >>> from pathlib import Path
# >>> import format_data
# >>> skill_root = Path(format_data.__file__).parent
# >>> sample_dir = skill_root / format_data.ARCHETYPE_SAMPLE_DIRS[fmt]  # fmt from Step 0
# >>> files = sorted(str(p) for p in sample_dir.glob("*.txt"))
# >>> archetype_similarity(user_mb, files)
# Legacy example:
# [('samples/legacy/Legacy_UR_Tempo_by_silviawataru.txt', 78.4, 23),
#  ('samples/legacy/Legacy_Dimir_Tempo_by_kyataoka.txt', 41.2, 14), ...]
# Modern example:
# [('samples/modern/Modern_UR_Aggro_by_Eggybenny.txt', 72.1, 19),
#  ('samples/modern/Modern_Boros_Aggro_by_BigDadChad.txt', 38.7, 11), ...]
```

#### 5. N-card joint probability (Tron pieces, combo openers)

```python
def joint_n_cards(N, card_counts, n_drawn):
    """
    P(>=1 of EACH listed card type in opener) via inclusion-exclusion.

    card_counts: list of ints, one per disjoint card type (e.g., [4, 4, 4]
                 for 4 Urza's Tower + 4 Mine + 4 Power Plant)
    N: deck size (typically 60)
    n_drawn: cards seen (7 opener on play; 8 on draw; etc.)

    Returns: probability as a float in [0, 1].

    Note: card types MUST be disjoint (no card is in two pools). For
    Planar Nexus which counts as all subtypes, model it as a separate
    type with its own count.
    """
    total = comb(N, n_drawn)
    union_prob = 0
    # Sum over non-empty subsets of card types: (-1)^(|S|+1) * P(no card in S)
    K_list = card_counts
    n_types = len(K_list)
    for size in range(1, n_types + 1):
        for subset in combinations(range(n_types), size):
            excluded = sum(K_list[i] for i in subset)
            if N - excluded < n_drawn:
                continue  # impossible to avoid drawing any from this subset
            p_avoid_subset = comb(N - excluded, n_drawn) / total
            union_prob += ((-1) ** (size + 1)) * p_avoid_subset
    return 1 - union_prob

# Usage:
# >>> joint_n_cards(60, [4, 4, 4], 7)  # P(all 3 Tron pieces in opener on play)
# 0.0471  # 4.71% — Tron T1 without any "wildcards"
# >>> joint_n_cards(60, [4, 1], 7)  # Doomsday (4) + LED (1) — fast-kill hand
# 0.0416  # 4.16%
#
# IMPORTANT: this helper assumes DISJOINT pools — every card belongs to
# exactly one type bucket. For cards that satisfy multiple slots (e.g.,
# Planar Nexus counts as Tower AND Mine AND Power-Plant simultaneously,
# or Cavern of Souls naming a chosen creature type), you MUST pre-process
# differently. For Planar Nexus + Tron:
#
#   P(Tron complete) = P(all 3 specific pieces)
#                    + P(NOT all 3) * P(Nexus drawn AND ≥1 missing piece)
#                    [or just simulate — closed-form gets messy]
#
# For combos where one card replaces multiple slots, simulate via
# random.choices or write the explicit inclusion-exclusion by hand.
```

#### 6. Cantrip filtering depth and target-find probability

The `CANTRIPS` catalog below holds per-card metadata (look/keep/draws/shuffles). The legality of each card per format is sourced from `format_data.py`'s `CANTRIP_POOLS` dict — import that and intersect with the user's mainboard to know which cantrips actually apply for the format identified in Step 0.

```python
from format_data import CANTRIP_POOLS  # legal-cantrips-per-format whitelist

# Cantrip catalog (format-agnostic metadata): each entry = (look_depth, keep_depth, draws_card, shuffles)
# look_depth = how many top cards the cantrip reveals to you
# keep_depth = how many go to hand
# draws_card = +1 if the cantrip itself draws a card (Ponder's "then draw a card")
# shuffles = True if the unrevealed cards return via a shuffle (Ponder optional)
CANTRIPS = {
    "Brainstorm": dict(look=3, keep=1, draws=2, shuffles=False),  # +3 see, net +1 (puts 2 back). Legacy only.
    "Ponder":     dict(look=3, keep=0, draws=1, shuffles=True),   # Legacy only (banned in Modern)
    "Preordain":  dict(look=2, keep=0, draws=1, shuffles=False),  # legal both
    "Opt":        dict(look=1, keep=0, draws=1, shuffles=False),  # legal both
    "Consider":   dict(look=1, keep=0, draws=1, shuffles=False),  # legal both — Modern-meta cantrip
    "Stock Up":   dict(look=5, keep=2, draws=0, shuffles=False),  # legal both
    "Flow State": dict(look=3, keep=1, draws=0, shuffles=False),  # legal both
    "Lorien Revealed": dict(look=3, keep=0, draws=3, shuffles=False),  # cast mode
    "Mishra's Bauble": dict(look=1, keep=0, draws=1, shuffles=False),  # top of YOUR library, delayed draw
    "Thundertrap Trainer": dict(look=4, keep=1, draws=0, shuffles=False),  # Legacy mostly
    "Otherworldly Gaze": dict(look=3, keep=0, draws=0, shuffles=False),  # Modern (surveil 3)
    "Expressive Iteration": dict(look=3, keep=2, draws=0, shuffles=False),  # Modern only (Legacy-banned)
    "Reckless Impulse": dict(look=2, keep=2, draws=0, shuffles=False),  # impulse-exile cast (legal both)
    "Wrenn's Resolve": dict(look=2, keep=2, draws=0, shuffles=False),    # impulse-exile cast (legal both)
    "Manamorphose": dict(look=1, keep=0, draws=1, shuffles=False),       # ritual + cantrip (legal both)
}

# Filter to format-legal cantrips before counting from a decklist:
#   legal_cantrips = {n: c for n, c in CANTRIPS.items() if n in CANTRIP_POOLS[format]}
# Use legal_cantrips in cantrip_depth() below.

def cantrip_depth(deck_cantrips_count, turn, on_play, format):
    """
    Estimate effective cards seen by turn N given cantrip density.

    deck_cantrips_count: dict {cantrip_name: count_in_deck}
    turn:    which turn you're computing through
    on_play: True if you're on the play (no T1 draw)
    format:  REQUIRED. "legacy" or "modern" — used to filter cantrips by per-format
             legality. Mandatory under the v5 format-binding rules (Step 0 binds
             the format string for the entire run; no silent defaulting).

    Returns: (cards_drawn_raw, effective_cards_seen_upper_bound, dropped)
      - cards_drawn_raw: raw card-draw count by turn N
      - effective_cards_seen_upper_bound: ceiling including cantrip "look" depth
      - dropped: list of cantrip names that were not legal in the bound format

    Upper bound assumes every cantrip is drawn AND cast — actual will be lower.
    Treat the second number as a ceiling, not an expectation. Cantrips not legal
    in the bound format are dropped from the count and returned in `dropped`.
    Callers receive the `dropped` list and may warn/log on it themselves — this
    function performs no I/O.
    """
    fmt = format.strip().lower()
    if fmt not in CANTRIP_POOLS:
        raise ValueError(f"format must be one of {sorted(CANTRIP_POOLS)}, got {format!r}")
    legal_for_format = set(CANTRIP_POOLS[fmt])
    raw_draws = 7 + (turn - 1) + (0 if on_play else 1)
    drawn_fraction = min(0.6, 0.2 * turn)
    extra_seen = 0
    dropped = []
    for name, ct in deck_cantrips_count.items():
        if not isinstance(name, str) or not name:
            dropped.append(name)
            continue
        canonical = name.strip().strip('"\'').split(' // ')[0].strip()
        if canonical not in legal_for_format:
            dropped.append(name)
            continue
        cantrip = CANTRIPS.get(canonical)
        if not cantrip:
            continue
        copies_drawn = ct * drawn_fraction
        extra_seen += copies_drawn * cantrip["look"]
    return raw_draws, raw_draws + int(extra_seen), dropped

def p_find_target_with_cantrips(N, K, deck_cantrips_count, turn, on_play, format):
    """
    Upper bound on P(see >=1 of target by turn N) accounting for cantrip selection.
    See cantrip_depth for caveats — this is a CEILING, not an exact probability.

    format: REQUIRED. "legacy" or "modern". Mandatory under v5 format-binding
            rules — no silent default. The format string must come from Step 0.

    For a precise answer on a specific game state, simulate.
    """
    fmt = format.strip().lower()
    if fmt not in CANTRIP_POOLS:
        raise ValueError(f"format must be one of {sorted(CANTRIP_POOLS)}, got {format!r}")
    raw, eff, _dropped = cantrip_depth(deck_cantrips_count, turn, on_play, fmt)
    p_raw = 1 - comb(N - K, raw) / comb(N, raw) if N - K >= raw else 1.0
    p_eff = 1 - comb(N - K, eff) / comb(N, eff) if N - K >= eff else 1.0
    return {"P_raw": round(p_raw, 4), "P_with_cantrips_upper_bound": round(p_eff, 4)}

# Usage (Doomsday looking for its namesake by T3 on the draw — Legacy):
# >>> p_find_target_with_cantrips(60, 4,
# ...     {"Brainstorm": 4, "Ponder": 4, "Flow State": 4}, turn=3, on_play=False,
# ...     format="legacy")
# {'P_raw': 0.5277, 'P_with_cantrips_upper_bound': 0.9513}
# True P is somewhere in [0.53, 0.95]; cantrips bias toward keeping good cards.

# Usage (Modern UR Aggro looking for Cori-Steel Cutter by T2 on the play):
# >>> p_find_target_with_cantrips(60, 4,
# ...     {"Mishra's Bauble": 4, "Consider": 4, "Expressive Iteration": 4},
# ...     turn=2, on_play=True, format="modern")
# Brainstorm would NOT count here — format=modern excludes it from CANTRIP_POOLS.
```

**Why cantrip filtering is an upper bound, not exact:**
- Cantrips selectively KEEP good cards and BOTTOM bad ones → real P(find target | see it) > 1 ideally, but the model is "uniform random look"
- Brainstorm puts 2 cards back on top → next draw step re-sees them (not a fresh look)
- Ponder's shuffle option randomizes the next K cards → adds variance
- For precise answers in specific game states, write a Monte Carlo simulation

When reporting cantrip-fueled probabilities, ALWAYS quote both bounds: "raw hypergeometric P = X; with-cantrip ceiling = Y; true expected P is between these, leaning toward Y in selectively-built combo decks."

### When Things Break

| Symptom | Fix |
|---|---|
| Scryfall returns 403 | Add User-Agent + Accept headers (see above) |
| Scryfall returns 429 | Sleep longer (0.5s+), respect `Retry-After` |
| mtgtop8 returns empty cards | `meta=` param is stale OR wrong format code; fetch `format?f=<LE\|MO>` for the bound format to find current |
| mtgdecks/aetherhub 403 | Cloudflare-blocked; use WebSearch snippets, don't fabricate |
| WebFetch on Scryfall API | Always 403 — use curl |
| Parser finds 0 cards | mtgtop8 may have changed HTML structure; inspect with `curl ... -o /tmp/x.html` and grep |

### Tooling Don'ts

- Don't cache Oracle text or banlist in this skill. Both drift; the workflow enforces live lookup.
- Don't WebFetch Scryfall and trust the summarization — the model may hallucinate fields the page never showed.
- Don't approximate probabilities. Even "the math is obvious" is wrong often enough that Python costs ~5 seconds and saves wrong claims.
- Don't claim a card is meta-relevant without checking a real decklist. Card existence ≠ deck presence.

## Red Flags — STOP and Verify

| Thought | Action |
|---|---|
| "I remember this card does..." | Search Scryfall (curl, not WebFetch) |
| "Probably the Meta is..." | Check mtgtop8 |
| "Card X was banned" / "wasn't" | Check current B&R (curl + grep) |
| "From the card name..." | Search Oracle text |
| "Chalice@N catches X" | Verify X is actually played (Step 4b) |
| "Around X% chance..." | Run `python3` with `math.comb` |
| "Chalice/lock would have shut this down" | Check whether it resolves BEFORE the threat — permanents in play are immune |
| "WebFetch returned 403 on Scryfall" | Use `curl` with `User-Agent` header |
| "Infinite mana via X + Y..." | State-machine the cycle |
| "I'll cite this card as a background assumption" | Re-verify it's not banned and is actually played |

## Sub-Skills and References (opt-in, not auto-loaded)

Two kinds of opt-in content. Each loads only when the analysis needs it.

### Sibling skill — invoke via the Skill tool

- **`mtg-card-evaluation`** — Five-lens scoring framework for "does card X fit deck Y" with worked examples. Invoke via `Skill` tool with `skill='mtg-card-evaluation'` whenever the question is specifically about whether a single card belongs in a single deck (inclusion, replacement-after-ban, sideboard slot, set-release evaluation). Treat its scorecard + verdict as the inclusion answer; integrate it into your evidence-labeled response. Do NOT inline the five lenses by hand — invoke the skill so its tests and worked examples stay authoritative.
  - The skill has two modes: **Mode A** (card vs single deck — the inclusion question above) and **Mode B** (card vs current meta — "how does card X fit format Y's current meta?" with no target deck given). Pick the mode that matches the question.

### Supporting files in this skill — load via `Read`, branched by format

- **`reference-tables/<format>.md`** — Per-format pitfalls, mana-value rules, lock-card references, manabase/sideboard/combo tables, AND the Live Banlist Verification Sources for that format. Choose based on the format identified at the start of the analysis (Legacy → `reference-tables/legacy.md`; Modern → `reference-tables/modern.md`).
- **`samples/<format>/`** — Real decklists for that format, captured at a known date. The `samples/<format>/README.md` indexes them by archetype, player, tournament, source URL, fetch date. See the **Using Sample Decklists** section below for when to consult them.

The Skill tool loads `SKILL.md` only. All tooling commands are inline above — supporting files contain reference data, not procedural steps. The sibling `mtg-card-evaluation` skill is a separate skill load, not a Read of a file inside this directory.

**Note on format-awareness:** Phases 1-5 of the multi-format restructure are shipped: Legacy data is in `reference-tables/legacy.md` and `samples/legacy/`, Modern data is in `reference-tables/modern.md` and `samples/modern/`, and `format_data.py` carries per-format constants.

## Using Sample Decklists

The `samples/<format>/` directory contains real tournament decklists for that format, captured at a known date (Legacy samples currently May 2026; Modern samples populated in Phase 3 of `PLAN-modern-mode-b.md`). The index `samples/<format>/README.md` lists each file's archetype, player, tournament, mtgtop8 source URL, and fetch date.

### When to use samples (two valid cases)

1. **As reference examples for archetype shape.** When the user pastes a deck and asks "is this competitive?", samples show what a tournament-going version of that archetype looks like — card choices, ratios, manabase, sideboard. The deviation between the user's list and the matching sample IS the analysis. Cite the sample file and its fetch date as evidence.

2. **As cached input for Step 4b deck-presence verification — only when sample is fresh enough.** Live mtgtop8 fetches are slow (~5–15s per archetype) and Cloudflare-prone. If the question only needs "what does archetype X typically run", a recent sample answers without the fetch.

### When samples are NOT enough (require live fetch)

- Any question about **current meta share** — samples are one decklist each, not a sample of the population. Use mtgtop8's format page for percentages.
- The sample's fetch date predates a B&R announcement or set release that has happened since. Check the format's `samples/<format>/README.md` date column; if stale, refetch.
- Step 4b says "2–3 sample decklists per top archetype" — that's the requirement for inclusion claims. If you cite "Card X is played in archetype Y" based on a SINGLE sample, you have not satisfied Step 4b — fetch live for more lists.

### Why this is not a contradiction of "don't cache"

The "don't cache Oracle text / banlist" rule applies to authoritative facts that change without warning. Sample decklists are **examples at an explicit timestamp**, not facts about the current meta. Any claim derived from a sample MUST cite the sample's fetch date — never present sample-derived data as "current."

### Input format for user-pasted decklists

Samples in `samples/<format>/*.txt` use the canonical mtgtop8 export format — the same format users commonly paste:

```
4 Brainstorm
4 Ponder
...
Sideboard
2 Pyroblast
...
```

When parsing a user paste, be tolerant of these variations:
- `4 Card Name` (canonical) / `4x Card Name` / `4    Card Name` — match `^\s*(\d+)\s*[xX]?\s+(.+?)\s*$`
- Sideboard separator: literal `Sideboard` (any case) on its own line — also accept `// Sideboard`, `SB:`, or `Sideboard (15)`
- Strip category headers like `Creatures (12)`, `Lands (22)`, `Spells (26)` — keep only count-prefixed lines
- If no `Sideboard` label and the list has 75 lines, treat the last 15 as SB; if 65, last 15; otherwise ask the user to disambiguate
- MDFCs may be written as `Tamiyo, Inquisitive Student` or `Tamiyo, Inquisitive Student // Tamiyo, Seasoned Scholar` — verify via Scryfall regardless

After parsing, sum the counts; reject a paste where mainboard ≠ 60 (or ≠ 80 for Yorion companion decks) or sideboard > 15 or sideboard < 0, and ask the user to confirm. Modern/Legacy allow sideboards ≤ 15 — a 14-card sideboard is legal (e.g., the shipped UW Control sample under `samples/modern/`).

### Regression-testing the skill itself

When you change `SKILL.md` or any `reference-tables/<format>.md`, run analysis against at least one sample (e.g., `samples/legacy/Legacy_Doomsday_by_Sinflower.txt`) before committing. Confirm the updated workflow still produces a sensible analysis — catches drift between the workflow description and how Claude actually acts on it.

### Sample staleness check

Each entry in `samples/<format>/README.md` has a fetch date. Before relying on a sample, scan recent B&R announcements:

```bash
curl -sSL -H "User-Agent: mtg-deck-analysis/1.0" \
  "https://magic.wizards.com/en/news/announcements" \
  | grep -i "banned\|restricted" | head -10
```

If a Legacy B&R announcement is dated AFTER your sample, the sample's archetype shape may be obsolete — refetch via the mtgtop8 parser above before citing.

## TDD Status

v3. RED failures driving the current version:
- Tamiyo, Inq. Student MV claimed as 2 (actual `{U}` = MV 1) — Scryfall verification re-emphasized
- Mishra's Workshop used as a math input despite being banned in Legacy — Iron Law extended to math inputs
- Counterspell cited as a meta target without checking deck presence (0/12 archetypes play it in May 2026) — Step 4b added
- Probabilities estimated as "~65%" instead of computed via `math.comb` — Step 6 strengthened to require Python
- Chalice treated as if it removed resolved permanents — "permanent immunity" added to Step 5
- Scryfall API 403 not diagnosed (missing User-Agent header) — Scryfall tooling block inlined into SKILL.md

v3 also consolidated `tooling-notes.md` into this file since the skill is manual-invoke (`disable-model-invocation: true`) — there's no auto-load context cost, and inlining removes the risk of Claude skipping supporting files.

GREEN-verified by subagent test 2026-05-25: applied to a fresh Trinisphere meta question, the agent correctly used curl+headers for Scryfall, parsed 27 real mtgtop8 decklists for Step 4b, computed exact hypergeometric probabilities in Python, and discussed the resolved-permanent caveat. All 7 rubric points passed.

v4 (2026-05-25): repo restructured — each skill is its own folder at the repo root. The five-lens inclusion framework moved out of this directory (`mtg-card-evaluation.md`) and became a sibling skill (`mtg-card-evaluation/SKILL.md`), invoked via the Skill tool when an inclusion question arises. Motivation: name-folder correspondence so each skill installs independently, and the inclusion framework is reusable (callable standalone via `/mtg-card-evaluation`, not gated behind a full deck-analysis pass).

v5 Phase 1 (2026-05-25): multi-format restructure preparation. Per `PLAN-modern-mode-b.md`. File moves: `reference-tables.md` → `reference-tables/legacy.md`; `samples/` → `samples/legacy/`. Stubs created for Modern: `reference-tables/modern.md` (populated in Phase 4) and `samples/modern/README.md` (populated in Phase 3). Step 3 updated to prefer Scryfall API banlist endpoint (`https://api.scryfall.com/cards/search?q=banned%3A<format>`) over Wizards HTML, with both URLs documented per format in their `reference-tables/<format>.md`. **Phase 1 leaves the skill fully functional for Legacy** via the new paths; Modern data populates in Phases 3–4. Step 0 (mandatory format identification) lands in Phase 2.

v5 Phase 5 (2026-05-25): format_data.py module added at `mtg-deck-analysis/format_data.py`. Importable Python module exporting per-format constants: CANTRIP_POOLS (13 Legacy + 11 Modern cantrips, 15 unique across both formats, each Scryfall-verified for format legality and draw/filter effect), ARCHETYPE_SAMPLE_DIRS, WASTELAND_ANALOG, CHALICE_VULNERABILITY (per Chalice setting × format), FORMAT_CODES (mtgtop8 URL params + Scryfall banlist queries + Wizards page section anchors). Validators in SKILL.md updated: `cantrip_depth(...)` and `p_find_target_with_cantrips(...)` now accept `format=` keyword and filter the cantrip count dict by `CANTRIP_POOLS[format]`, returning a `dropped` list (e.g., `['Brainstorm', 'Ponder']` when called under `format='modern'`) so callers can log or warn without this function performing I/O. Catalog grew from 8 → 15 cantrips (added Opt, Consider, Otherworldly Gaze, Expressive Iteration, Reckless Impulse, Wrenn's Resolve, Manamorphose). `archetype_similarity()` example usage shows the `ARCHETYPE_SAMPLE_DIRS[format]` lookup. **File name uses underscore** (`format_data.py`) not hyphen — required for Python `from format_data import` to work. Module ships a `_self_check()` runnable via `python3 format_data.py` to assert all per-format dicts have matching keys and no duplicates. GREEN-verified live: same `p_find_target_with_cantrips` query ({'Brainstorm': 4, 'Ponder': 4, 'Flow State': 4}, T3 on the draw) under `format='legacy'` returns ceiling 0.9513 (Brainstorm/Ponder counted); under `format='modern'` returns ceiling 0.7469 (Brainstorm and Ponder correctly dropped, only Flow State counted).

v5 Phase 4 (2026-05-25): Modern reference table content populated. `reference-tables/modern.md` now mirrors `legacy.md`'s structure with Modern-specific content: Card Name Pitfalls (Boseiju instant-speed/3-type targeting, evoke-pitch elementals MV != paid cost, MDFCs like Ajani/Ral, Cori-Steel Cutter Flurry trigger, Sowing Mycospawn Legacy-banned-not-Modern), Mana Value vs Paid Cost table (Solitude=5, Subtlety=4, Endurance=3, FoN=3), Top Staples by Archetype (per-archetype 4-of cards observed in the 10 Phase 3 samples), Manabase Patterns (fetchlands + shocklands + Surveil lands + Triomes + utility lands + Tron pieces), Format-Specific Interaction Pitfalls (FoN vs FoW cost difference, Triome ETB-tapped affects T1, Karn wishboards, Cascade), "Looks Played But Isn't" with verified-absent expected staples (Wrenn and Six, Murktide, Yawgmoth not in current top 10), "Looks Modern But Isn't" with Scryfall-verified banlist state. All cards in the file batch-verified via Scryfall cards/collection endpoint (61/61 found on first call). GREEN-verified by subagent: 6/6 checks pass on Boseiju oracle, evoke MVs, Legacy-banned/Modern-legal trio (Ragavan/Expressive Iteration/Sowing Mycospawn), Boros Aggro staples cross-checked against sample, Tron typeline (Land — Urza's Power-Plant with hyphen), and Live Banlist Verification Sources section presence. **Phase 4 makes the skill fully functional for Modern analyses** end-to-end.

v5 Phase 3 (2026-05-25): Modern samples populated. 10 Modern decklists fetched live from mtgtop8 (meta=54), one per top-meta archetype as of fetch date: Boros Aggro (12%), Affinity (12%), Blink (7%), UR Aggro (4%), UrzaTron (4%), Ruby Storm (4%), Eldrazi Ramp (3%), UW Control (3%), Living End (3%), Amulet Titan (3%). Files at `samples/modern/Modern_<Archetype>_by_<Player>.txt`, each with canonical header (Format / Archetype / Player / Tournament / Source URL / Fetched date / Tournament date / Mainboard count / Sideboard count). README index updated. All MB=60; one SB=14 (UW Control, legal — sideboards are ≤15 not =15). Modern meta turned out different from plan assumptions (no Yawgmoth Pod, no Hammer Time at the top — Boros Aggro and Affinity dominate). Phase 4 (Modern reference table content) shipped subsequently — see Phase 4 entry above.

v5 Phase 2 (2026-05-25): mandatory Step 0 added. Workflow now starts with **Step 0 — Identify the format**, refuses to proceed without an identified format ∈ {legacy, modern}. Iron Law gains a second clause: "NO ANALYSIS WITHOUT AN IDENTIFIED FORMAT". Format-binding discipline added: the format string is bound for the run and never silently swapped mid-analysis. Tooling block updated: mtgtop8 URLs use `?f={FMT}` template (Legacy `LE`, Modern `MO`, both verified live 2026-05-25 returning correct format pages). Step 4 updated to reference the format-bound URL.

**Step 0 detection rules deliberately simple — per user directive 2026-05-25 ("if not sure just ask"):**
1. Explicit user prefix wins (e.g., `Modern: ...`, `Legacy: ...`, "in Modern, ...").
2. Otherwise, ASK the user. Heuristic hints (Wasteland → likely Legacy; Ragavan/W6 → likely Modern) are offered as suggestions inside the prompt, but the user's answer is the decision. No auto-detect path.

RED that led to this simplification: previous Step 0 draft tried two iterations of "hard signal" auto-detect lists. First miss: described Boseiju as "sorcery-speed" (memory error). Second miss: classified Solitude/Subtlety/Endurance as hard Modern signals when Scryfall verification showed all three are legal in both formats. Lesson: any card-classification list goes stale every B&R cycle and can be wrong in subtle ways; asking the user is robust against both card-pool drift and skill-author error. **Phase 2 leaves the skill safe to use on Modern inputs structurally**, even though Modern reference data isn't fully populated until Phase 4.
