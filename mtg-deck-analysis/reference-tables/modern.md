# Modern Reference Tables — STUB

This file is populated in **Phase 4** of `PLAN-modern-mode-b.md`. Only the Live Banlist Verification Sources section (added in Phase 1) is canonical content; the rest are placeholders.

Mirror structure of `legacy.md` once populated.

## Live Banlist Verification Sources (Modern) — CANONICAL

**The Iron Law:** never cite Modern legality from this file or from memory. Always fetch live.

### Primary: Scryfall API (parseable JSON)

```bash
curl -s -H "User-Agent: chinrw-mtg-skill/1.0" -H "Accept: application/json" \
  "https://api.scryfall.com/cards/search?q=banned%3Amodern&order=name" \
  | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d['data']), 'cards'); [print(c['name']) for c in d['data']]"
```

Returns JSON with `data[]` of full card objects. As of 2026-05-25 verification, the endpoint returns **52 banned-in-Modern cards** (includes a few silver-bordered joke entries — filter on `border_color != "silver"` if you need only tournament-relevant bans).

For pagination (Scryfall caps at 175 per page):

```bash
# If has_more=true in response, fetch next_page URL from response
```

### Secondary: Wizards B&R page (authoritative on announcement day)

```bash
curl -s -H "User-Agent: chinrw-mtg-skill/1.0" \
  "https://magic.wizards.com/en/banned-restricted-list" \
  | grep -A 1000 "Modern" | head -200
```

Wizards page is canonical on B&R announcement days (Scryfall may lag by a few hours). Use this for tiebreaking. The page section header is `Modern` — grep from there.

### Citation discipline

Every Modern legality claim in an analysis output must include:
- The fetch date of the banlist consulted
- Source: `Scryfall API banned:modern` OR `Wizards B&R - Modern section`
- If older than 24 hours, refetch before citing

Do NOT paste a cached banlist into this file. Reference tables document HOW to fetch, never WHAT was last fetched.

---

## TODO (Phase 4)

- [ ] Top staples by archetype (Ragavan, DRC, Murktide, Wrenn and Six, Boseiju, The One Ring, Solitude, Subtlety, etc. — verify each via Scryfall on Phase 4 day)
- [ ] Modern-specific mana-base patterns (fetchlands, Triomes, MDFCs, Boseiju, no Wasteland)
- [ ] Modern interaction pitfalls (Force of Negation vs Force of Will cost difference; evoke-pitch elementals MV=5 not 0; companion mechanics if currently relevant; Modern Horizons cards that look like Legacy reprints but interact differently)
- [ ] "Cards That Look Meta But Aren't" — Modern edition (cards that look played but aren't in the current top archetypes — separate concept from "banned but isn't")
- [ ] Modern manabase math notes (Triome ETB-tapped affects T1 plays)

When populated, this section should mirror `legacy.md`'s structure for one-to-one comparability.
