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
- "Should I add card X to deck Y" (then also see `mtg-card-evaluation.md`)
- Comparing two decks
- Predicting matchup performance vs current meta
- Probability or math questions about a deck
- Recommending optimizations

## The Iron Law

```
NO REASONING WITHOUT VERIFICATION
```

This applies to **every** card you cite — not only the ones being analyzed. Cards used as math inputs (e.g., "4 Mishra's Workshop as enabler") or interaction examples (e.g., "Chalice@2 catches Counterspell") count equally. A claim citing a banned or unplayed card invalidates the whole conclusion.

## Workflow

**Step 1 — Read literally.** Note every card name. Flag any you're not 100% sure of.

**Step 2 — Verify Oracle text via Scryfall API.** `WebFetch` returns 403 against `api.scryfall.com`. Use `curl` with `User-Agent` + `Accept` headers — see the Scryfall block under "Tooling" below for the exact command and batch loop. Capture: Oracle text, type, subtypes, mana value, MDFC faces. Re-verify every card before citing.

**Step 3 — Verify the format ban list.** curl `https://magic.wizards.com/en/banned-restricted-list` and grep the format section directly (see "B&R" tooling block). No banlist is cached in this skill. Cite the URL and fetch date. If unreachable, refuse to assert ban status.

**Step 4 — Verify current meta archetypes.** Pull top 10 by share from mtgtop8 (curl with UA works; mtgdecks and aetherhub are Cloudflare-blocked — see the source-reliability matrix below). Note the date and `meta=` code.

**Step 4b — Verify deck PRESENCE, not just card existence.** Before claiming an interaction matters (e.g., "Chalice@2 catches Counterspell"), confirm the target card is **actually mainboarded** in current decklists. Parse 2–3 sample decklists per top archetype from mtgtop8 (parser below) and tabulate. Drop any interaction claim whose target card is absent from the sample. Card legality ≠ card play rate.

**Step 5 — Identify critical interactions.** Subtypes, mana value (not paid cost), mana vs activated abilities, MDFC graveyard semantics, trigger conditions, **and the "already-resolved permanent" semantics** — Chalice / Trinisphere / Thalia / Sphere only tax future casts; they don't undo permanents that already resolved. See `reference-tables.md`.

**Step 6 — Compute probabilities in Python.** Never write "approximately X%". Use `python3` with `math.comb` (template under "Tooling" below). For tempo questions, ALSO compute the conditional: P(your lock card resolves BEFORE opp's threats deploy). Chalice on the draw against tempo is often "too late" — ~95% of opponents deploy a T1 threat.

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

# 1. Find archetype IDs (one-time lookup)
fmt_page = fetch("https://www.mtgtop8.com/format?f=LE")
archetypes = re.findall(r'archetype\?a=(\d+)[^"]+>([^<]+)</a>', fmt_page)
# e.g., 213 → UR Tempo, 1606 → Dimir Tempo, 553 → Eldrazi Aggro

# 2. List recent decks for an archetype (note: meta code changes each period)
arch_page = fetch("https://www.mtgtop8.com/archetype?a=213&meta=338&f=LE")
decks = re.findall(r'event\?e=(\d+)&d=(\d+)&f=LE', arch_page)

# 3. Fetch each decklist and parse cards (mainboard only)
for e, d in decks[:3]:
    html = fetch(f"https://www.mtgtop8.com/event?e={e}&d={d}&f=LE")
    for count, name, sec in parse_deck(html):
        if sec == "MD":
            print(count, name)
```

**The `meta=NNN` code changes each meta period.** Find the current one by grepping the format page for `<select` options or by checking the URL when you manually click "current 2 weeks". Was `meta=34` in early May 2026, `meta=338` by late May.

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

### When Things Break

| Symptom | Fix |
|---|---|
| Scryfall returns 403 | Add User-Agent + Accept headers (see above) |
| Scryfall returns 429 | Sleep longer (0.5s+), respect `Retry-After` |
| mtgtop8 returns empty cards | `meta=` param is stale; fetch `format?f=LE` to find current |
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

These supporting files load via `Read` only when an analysis needs them:

- `reference-tables.md` — Card-name pitfalls (Workshop confusion, Tamiyo MV, Counterspell-not-actually-played), mana-value rules, Chalice / Bowmasters / Wasteland reference, Locus / Urza / Tron geometry, permanent-immunity caveat, "looks played but isn't" list, Legacy staples / manabase / sideboard / combo tables.
- `mtg-card-evaluation.md` — Five-lens scoring framework for "does card X fit deck Y" with worked examples.

The Skill tool loads `SKILL.md` only. All tooling commands are inline above — supporting files contain reference data, not procedural steps.

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
