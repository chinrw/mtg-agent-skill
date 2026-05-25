# PLAN: Multi-Format (Legacy + Modern) Support + `mtg-card-evaluation` Mode B

**Status:** DRAFT — awaiting user review on the **Open Questions** section before implementation begins.
**Created:** 2026-05-25
**Owner:** @chinrw
**Estimated effort:** ~6–10 hours over multiple sessions (samples are the slow part — mtgtop8 fetches Cloudflare-throttle).

---

## 1. Goals

Two work items shipped as one coherent release:

1. **Add Modern format support** to `mtg-deck-analysis`, alongside the existing Legacy support. Single skill, format-aware. Reference tables and samples split by format inside the skill folder.
2. **Add Mode B (card-in-meta positioning)** to `mtg-card-evaluation`. Same Iron Law (evidence per lens), but the input is a single card + format meta (no target deck), and the output is a meta-tier prediction + best-home recommendation.

Both work items share verification machinery (live Scryfall, live B&R, live mtgtop8) so it's cheaper to do them together than back-to-back.

## 2. Architecture decisions (locked)

| Decision | Choice | Rejected alternatives |
|---|---|---|
| Format support shape | Single skill, format-aware. Reference + samples split internally by format | Per-format skill folders (too much workflow duplication); parameter-flag-only (no clean split point) |
| Format scope | Legacy + Modern only | Pioneer / Pauper / Standard deferred |
| Mode B timing | Roll into Modern release | Sequential Mode B → Modern → ship |
| Modern depth | Full: 8–10 samples + reference table + Modern-specific Python validator config | Lighter samples-only; samples-only without Modern-tuned validators |

## 3. Target file layout

```
mtg-agent-skill/
├── README.md                                  (updated for multi-format)
├── mtg-deck-analysis/
│   ├── SKILL.md                               (adds Step 0: identify format)
│   ├── reference-tables/
│   │   ├── legacy.md                          (renamed from reference-tables.md)
│   │   └── modern.md                          (new)
│   ├── format-data.py                         (new — cantrip pools, manabase patterns per format)
│   └── samples/
│       ├── legacy/  (10 existing decks)
│       └── modern/  (8–10 new decks)
└── mtg-card-evaluation/
    └── SKILL.md                               (adds Mode B section + Mode B worked example)
```

The Nix flake config (`~/Documents/shell-config/home-manager/programs/claude-code/default.nix`) does NOT need to change — it mounts the skill folders, the internal restructure is transparent.

## 4. Phased implementation

### Phase 1 — Repo restructure for format-aware paths

- `git mv mtg-deck-analysis/reference-tables.md mtg-deck-analysis/reference-tables/legacy.md`
- `git mv mtg-deck-analysis/samples mtg-deck-analysis/samples/legacy` (or `mkdir + git mv` per-file if simpler)
- Update all `samples/` references in `mtg-deck-analysis/SKILL.md` → `samples/legacy/`
- Update all `reference-tables.md` references → `reference-tables/legacy.md`
- Stub `reference-tables/modern.md` and `samples/modern/` (empty placeholders, README explaining what goes here)

**Risk:** every existing reference to `samples/<file>` and `reference-tables.md` must update. Use `grep -rn` to confirm none missed.

### Phase 2 — Add Step 0 format identification to `mtg-deck-analysis/SKILL.md`

Insert before Step 1:

```
Step 0 — Identify the format.
  - If the user's input names a format explicitly (e.g., "Modern: ..."), accept it verbatim.
  - If a decklist is pasted without a format named, scan for format-disjoint cards:
      • Wasteland present → Legacy (Wasteland is Modern-banned-list-equivalent)
      • Ragavan + Wrenn and Six + Murktide → likely Modern
      • If still ambiguous, ASK the user before proceeding.
  - Treat the identified format as a string ∈ {legacy, modern} bound for the rest of the workflow.
  - All subsequent paths (`samples/<format>/`, `reference-tables/<format>.md`, mtgtop8 format code, B&R section name) branch on this string.
```

Update the **Tooling** block to show both Legacy (`?meta_id=LE`) and Modern (`?meta_id=MO`) mtgtop8 URLs. Update B&R section to show the page is shared but the per-format section grep differs.

### Phase 3 — Build Modern samples

Target archetypes per mtgtop8 Modern May 2026 (fetch on implementation day, do not assume):
- UR Murktide / UR Tempo
- Yawgmoth Pod
- Living End
- Eldrazi Tron (or Mono-Green Tron — pick the dominant variant)
- Domain / Domain Zoo
- Boros Energy
- Hammer Time
- Amulet Titan
- Through the Breach Scapeshift OR Goryo's Vengeance combo
- Mill or another off-meta-but-tier-2 deck for variety

**Approach:** parallel `curl` to mtgtop8 with `User-Agent`, parse with the existing mtgtop8 HTML pattern (`deck_line` class + `L14` span), capture player name + tournament + date in each file's header comment.

**Risk:** Cloudflare throttle. Mitigation: serial fetches with 3-5s gap; if blocked, retry with browser User-Agent variation.

Each Modern sample file gets the same header format as Legacy samples:

```
# Format: Modern
# Archetype: UR Murktide
# Player: <name>
# Tournament: <name>
# Source: https://mtgtop8.com/event?e=<id>&d=<deck-id>
# Fetched: 2026-MM-DD

4 Murktide Regent
...
```

Add `samples/modern/README.md` index mirroring `samples/legacy/README.md`.

### Phase 4 — Build `reference-tables/modern.md`

Mirror structure of `legacy.md` but for Modern. Sections needed:

1. **Banlist link + last-update reminder** — Modern B&R page section
2. **Top staples by archetype** — Ragavan, DRC, Murktide, Wrenn and Six, Boseiju, The One Ring, Solitude, Subtlety, etc. (verify each via Scryfall on implementation day)
3. **Modern-specific mana-base patterns** — fetchlands (same as Legacy), Triomes (3-color ETB-tapped), MDFCs (modal DFCs from Zendikar Rising / Kamigawa, common in Modern manabases), Boseiju (channel-tutor), no Wasteland
4. **Modern interaction pitfalls** — examples to verify and add:
   - Force of Negation vs Force of Will (different costs, different format presence)
   - Solitude / Subtlety / Endurance / Grief evoke-pitch incantations (5-mana cards typically cast for free; MV is 5 not 0)
   - Companion mechanics if any Companion is currently legal
   - Modern Horizons cards that look like Legacy reprints but interact differently
5. **"Looks Modern but isn't" list** — cards banned in Modern that frequently get recalled wrongly: Hogaak, Lurrus (if currently banned — verify), Faithful Mending, Birthing Pod, etc.
6. **Modern manabase math** — fetchland + shockland cycle, Surveil land cycle, Triomes; how `validate_manabase` should treat Triomes (ETB tapped affects T1 plays)

### Phase 5 — `format-data.py` for format-specific validator config

Create a small Python module that the deterministic validators import:

```python
# mtg-deck-analysis/format-data.py

CANTRIP_POOLS = {
    "legacy": ["Brainstorm", "Ponder", "Preordain", "Stock Up", "Flow State", "Mishra's Bauble"],
    "modern": ["Consider", "Mishra's Bauble", "Otherworldly Gaze", "Opt"],  # VERIFY each name live before use
}

WASTELAND_ANALOG = {
    "legacy": ["Wasteland"],
    "modern": [],  # No Wasteland in Modern. Note Boseiju, Field of Ruin role.
}

# format-aware archetype similarity baselines
ARCHETYPE_SAMPLE_DIRS = {
    "legacy": "samples/legacy",
    "modern": "samples/modern",
}
```

The existing validators (`validate_manabase`, `check_four_of`, `archetype_similarity`, `joint_n_cards`, `p_find_target_with_cantrips`) take a `format=` keyword arg and consult `format-data.py` for cantrip pool and sample directory. Manabase color logic doesn't change (Scryfall `produced_mana` is universal).

**Verification gate:** every card name in `CANTRIP_POOLS` is a claim that gets re-verified via Scryfall live during analysis. The constants are starting points, not authoritative facts.

### Phase 6 — Mode B framework in `mtg-card-evaluation/SKILL.md`

Add a new section after the existing 5-lens framework (which becomes "Mode A — Card in Deck"). New section: "Mode B — Card in Meta".

**Mode B trigger:** user gives a card + format, but NO target deck. Question shape: "How does X fit in <format>?" / "What decks would play X?" / "Is X a meta staple?"

**Mode B output:** 6 lenses, each with an Evidence block (same Iron Law as Mode A):

| Lens | What it answers |
|---|---|
| B1: Role Identification | What role(s) does the card fill? Derive from Oracle text + categorize as aggressive / midrange / control / combo / hate |
| B2: Archetype Fit Candidates | Among top 5 format archetypes, which currently fill this role? With what card? Name the current best-in-role per archetype |
| B3: Targets / Enables | What does this card answer (for reactive cards) or enable (for proactive cards)? Cite meta-card counts — e.g., "counters Brainstorm in Dimir Tempo (4 copies in sample, fetch 2026-05-25)" |
| B4: Vulnerabilities | What removes / counters / blanks this card in the current meta? Cite meta-card counts |
| B5: Best Homes Top 3 | Rank the 3 most likely deck homes. For each, summary-apply Mode A's 5-lens scorecard (one-line evidence per lens) |
| B6: Meta Position | Composite verdict: Tier A (likely staple, 4-of in best home) / Tier B (situational include, 1-2 of) / Tier C (sideboard tech only) / Tier D (unplayable in current meta) — justified by Areas 1–5 |

**Mode B verdict is qualitative (Tier prediction), not numeric.** The score-sum approach of Mode A doesn't apply because there's no single deck to fit against.

**Mode B worked example to include in skill:** TBD — see Open Questions.

### Phase 7 — TDD verification

For each work item:

**Modern support — RED:** dispatch subagent on a Modern decklist analysis WITHOUT the Modern reference/samples. Capture failures: cites Brainstorm as Modern-legal (banned), wrong meta % (uses Legacy archetypes), misidentifies The One Ring's pre-Modern-print errata, etc.

**Modern support — GREEN:** re-test with Modern files populated. Verify Step 0 correctly identifies the format, samples/modern/ is consulted, reference-tables/modern.md is loaded.

**Mode B — RED:** dispatch subagent on a card-in-meta question (e.g., "evaluate Boseiju, Who Endures in Modern May 2026") WITHOUT Mode B section. Observe: agent likely defaults to Mode A and fails because no target deck is given.

**Mode B — GREEN:** with Mode B added, agent invokes Mode B path, produces 6 Evidence blocks + Tier verdict. Self-audit confirms ≥5 of 6 lenses fully evidenced.

### Phase 8 — Documentation + Commit

- Update `README.md` to mention multi-format support (table of supported formats, invocation examples for each)
- Bump version table: v4 → v5 (Modern + Mode B)
- Update `mtg-deck-analysis/SKILL.md` TDD Status with Modern entries
- Update `mtg-card-evaluation/SKILL.md` TDD Status with Mode B v3 entry
- Commit per-phase (Phase 1 = restructure; Phases 3-4 = Modern data; Phases 5-6 = code + Mode B; Phase 7 = TDD results; Phase 8 = docs)
- Each commit gets Signed-off-by trailer; no push (user's rule)

## 5. Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| mtgtop8 Cloudflare blocks Modern fetch | Medium | Serial fetches with backoff; User-Agent rotation; fall back to manual paste if needed |
| Modern banlist remembered wrong (e.g., Brainstorm assumed legal) | High if not verified | Iron Law: every cited card re-verified live via B&R fetch. format-data.py treated as starting hints not facts |
| Mode A worked examples become inconsistent with Mode B examples | Medium | Reuse the same archetypes (e.g., Blue Post for Legacy Mode A, then a Modern card for Mode B) |
| Format auto-detection misfires (Wasteland-less Legacy deck wrongly tagged Modern) | Low–Medium | Default to ASKING the user when ambiguous; never silently guess. Explicit "Legacy:" / "Modern:" prefix overrides detection |
| Modern Python validators diverge from Legacy in ways the spec missed | Medium | Treat format-data.py as a thin config layer; if validator logic truly needs to branch (not just data), add a `format` keyword arg, don't fork the function |
| GREEN test subagent doesn't see the format split and falls back to Legacy | Medium | Mode B test must be on a Modern card to force the format-aware path. Spec the test prompt to require "Modern: <card>" in the input |

## 6. Open questions — RESOLVED 2026-05-25

All five questions answered. Locked decisions below.

### Q1. Format detection default behavior — RESOLVED: heuristic + ask-if-ambiguous

Skill tries format-disjoint card detection first (Wasteland → Legacy, Ragavan/Wrenn-and-Six/Murktide → Modern). If detection is ambiguous (cards legal in both formats only, or no format-disjoint card found), ask the user before proceeding. Never silently guess.

Implementation note: detection runs in Step 0 (see Q3). Detection logic is small and lives inline in `SKILL.md` — no `format-detector.py` needed.

### Q2. Mode B worked-example card — RESOLVED: Boseiju, Who Endures in Modern

Verified Oracle text via Scryfall on plan day (2026-05-25):

```
Boseiju, Who Endures
Type: Legendary Land
MV: 0
Oracle:
  {T}: Add {G}.
  Channel — {1}{G}, Discard this card: Destroy target
  artifact, enchantment, or nonbasic land an opponent
  controls. That player may search their library for
  a land card with a basic land type, put it onto the
  battlefield, then shuffle.
  This ability costs {1} less to activate for each
  legendary creature you control.
```

Lessons-learned note: the FIRST DRAFT of this preview said "sorcery-speed nonbasic-hate" — **two errors traceable to recalling instead of fetching** (channel ability is instant-speed; effect hits 3 types not just lands). The Iron Law applies to the skill author too. The Mode B worked example must be built from verified Oracle text, full stop. Anyone editing this example later: re-fetch before changing.

### Q3. Step 0 placement — RESOLVED: new numbered mandatory Step 0

`mtg-deck-analysis/SKILL.md` workflow becomes Step 0 → Step 7 (plus 4b and 6b unchanged). Step 0 = identify the format. Skill refuses to proceed without it. Format is bound to the analysis for the rest of the run.

### Q4. `format-data.py` shape — RESOLVED: real file at `mtg-deck-analysis/format-data.py`

Importable Python module. Exports `CANTRIP_POOLS`, `WASTELAND_ANALOG`, `ARCHETYPE_SAMPLE_DIRS`, etc. Validators in SKILL.md tooling block import from it: `from format_data import CANTRIP_POOLS; pool = CANTRIP_POOLS[format]`. One source of truth per-format constant.

### Q5. Banlist verification approach — RESOLVED: live fetch every time, document the sources

User correction (2026-05-25): NO static "Cards That Look Banned But Aren't" subsection. Static caches go stale; static tables become a liability the moment WotC updates B&R. Instead, both reference tables (`legacy.md`, `modern.md`) carry a **Live Banlist Verification Sources** section that documents WHERE to fetch from — but no cached card list.

**Verified live fetch URLs (Scryfall, faster than HTML parsing of Wizards page):**

```bash
# Modern banlist (52 cards as of 2026-05-25 verification, includes joke entries)
curl -s -H "User-Agent: chinrw-mtg-skill/1.0" -H "Accept: application/json" \
  "https://api.scryfall.com/cards/search?q=banned%3Amodern&order=name"

# Legacy banlist (169 cards as of 2026-05-25 verification, includes silver-bordered)
curl -s -H "User-Agent: chinrw-mtg-skill/1.0" -H "Accept: application/json" \
  "https://api.scryfall.com/cards/search?q=banned%3Alegacy&order=name"
```

Returns paginated JSON with `data[]` array of full card objects. Parse with `python3 -c "import sys,json; print([c['name'] for c in json.load(sys.stdin)['data']])"`.

**Source authority precedence (per format):**
1. **Primary (parseable):** Scryfall API banlist endpoint (URL above). Returns clean JSON, parseable, includes Oracle text.
2. **Authoritative:** Wizards B&R page `https://magic.wizards.com/en/banned-restricted-list` — section per format. Use for tiebreaking on B&R-announcement-day where Scryfall may lag by hours.
3. **Date stamp:** every banlist citation must include the fetch date in the analysis output. If older than 24 hours, refetch.

**Phase 1 implementation:**
- `reference-tables/legacy.md` gets a "Live Banlist Verification Sources" section near the top with the Scryfall URL + Wizards URL + curl command for Legacy.
- `reference-tables/modern.md` gets the same section structure with the Modern URLs.
- Both reference the same Scryfall API and same Wizards page, just different format codes (`banned%3Alegacy` vs `banned%3Amodern`).
- `mtg-deck-analysis/SKILL.md` Step 3 (verify ban list) gets an update: prefer Scryfall API banlist endpoint (parseable JSON) over WebFetch of Wizards HTML. Cite both in the analysis output.
- **No** static "Looks Banned But Isn't" table. Period.

**Discipline:** the Iron Law of "no cached banlist in this skill" stays. The reference tables document HOW to fetch, never WHAT was last fetched. If a future maintainer is tempted to paste a cached list "for convenience", they should delete it instead.

## 7. GREEN test design (pre-commit, per phase)

| Phase | GREEN test description | Pass criterion |
|---|---|---|
| 1 (restructure) | Apply Mode A to a Legacy deck after the restructure | Skill loads `reference-tables/legacy.md` and `samples/legacy/*` correctly; no broken file paths |
| 2 (Step 0) | Paste a Modern decklist without naming the format | Step 0 identifies Modern via heuristic OR asks; doesn't silently default to Legacy |
| 3-4 (Modern data) | Apply Mode A to a Modern deck (e.g., UR Murktide) | Modern samples and reference table consulted; outputs cite Modern-specific cards (Ragavan, W6, Boseiju) correctly |
| 5 (format-data) | Run `archetype_similarity` on a Modern deck | Compares against `samples/modern/`, not `samples/legacy/` |
| 6 (Mode B) | Ask "evaluate Boseiju in Modern May 2026" | Mode B path triggers, 6 Evidence blocks produced, ≥ 5 of 6 fully evidenced per Iron Law |
| 7-8 (docs) | Fresh user reads README → can they invoke Modern analysis correctly? | Self-evident from doc test |

## 8. Estimated effort breakdown

| Phase | Estimate | Notes |
|---|---|---|
| 1. Restructure | 30 min | Mechanical file moves + path updates |
| 2. Step 0 | 1 hour | Workflow text + Step 0 examples |
| 3. Modern samples (8-10) | 2-3 hours | mtgtop8 fetch is the bottleneck |
| 4. Modern reference table | 2-3 hours | Live verification of each cited card |
| 5. format-data.py | 30-45 min | Small code surface |
| 6. Mode B framework | 1.5-2 hours | Skill text + worked example |
| 7. TDD verification (RED + GREEN per item) | 1.5 hours | Subagent dispatches |
| 8. README + commits | 30-45 min | |
| **Total** | **~9-13 hours** | Spread across 3-4 sessions probably |

## 9. Out of scope (explicitly NOT in this release)

- Pioneer, Pauper, Standard, Vintage, Commander
- Auto-format-detection from card-name OCR or images
- Cross-format conversion ("port this Legacy deck to Modern")
- New mtgtop8 sample auto-refresh scheduling
- Mode A's 5-lens framework changes — Mode A is frozen for this release
- The deterministic validators' core math — only the data they consult changes

## 10. Definition of done

- All commits made (not pushed — per user rule)
- `~/.claude/skills/mtg-deck-analysis/` and `~/.claude/skills/mtg-card-evaluation/` reflect the new structure
- A fresh subagent given a Modern question produces a verifiable analysis using Modern data
- A fresh subagent given a card-in-meta question produces a 6-lens Mode B scorecard with ≥ 5 fully-evidenced lenses
- README.md mentions Modern in its invocation table
- This plan file gets archived (moved into a `docs/` folder or deleted) once shipping is complete

---

**Next action:** Section 6 (Open Questions) is RESOLVED as of 2026-05-25. Phase 1 (restructure + legacy.md "Looks Banned" retrofit) starts on user's "go".
