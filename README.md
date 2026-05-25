# mtg-agent-skill

Two Claude Code [Agent Skills](https://agentskills.io) for rigorous Magic: The Gathering analysis. Both enforce a verification-first workflow that prevents the most common failure modes when LLMs reason about MTG: stale card text from training data, outdated ban lists, hallucinated meta percentages, and lock-piece interactions that ignore the resolved-permanent rule.

**Status:** v5 multi-format (Legacy + Modern) + Mode B card-in-meta release shipped 2026-05-25. `PLAN-modern-mode-b.md` will be archived in a future cleanup commit.

## Skills in this repo

| Skill | Folder | Formats | What it answers |
|---|---|---|---|
| [`mtg-deck-analysis`](./mtg-deck-analysis) | `mtg-deck-analysis/` | Legacy, Modern | Decklist evaluation, matchup prediction, probability math, meta positioning |
| [`mtg-card-evaluation`](./mtg-card-evaluation) | `mtg-card-evaluation/` | Legacy, Modern | Mode A: "Does card X belong in deck Y?" (five-lens scorecard). Mode B: "How does card X fit in the current format meta?" (six-lens card-in-meta positioning with Tier verdict) |

Both skills are configured with `disable-model-invocation: true`. They do not auto-load into context. Invoke them explicitly:

```
/mtg-deck-analysis analyze the current Legacy meta against Death & Taxes
/mtg-deck-analysis Modern: how does Boros Aggro race Ruby Storm game 1?
/mtg-card-evaluation should I add Chalice of the Void to my Blue Post list?
/mtg-card-evaluation evaluate Boseiju, Who Endures in Modern May 2026
```

`mtg-deck-analysis` invokes `mtg-card-evaluation` automatically (via the Skill tool) when a deck-analysis run hits an inclusion question. You don't need to chain them by hand.

## What `mtg-deck-analysis` does

When you invoke it, Claude runs an 8-step main workflow plus 2 sub-step validators (10 entries total) on any MTG decklist or meta question (Legacy or Modern):

0. **Identify the format** (MANDATORY). Honor explicit `Legacy:` or `Modern:` prefix. If neither is given, ASK the user — never silently default. The skill currently supports Legacy and Modern only. The bound format string drives every subsequent path: `reference-tables/<format>.md`, `samples/<format>/`, mtgtop8 format code (`LE` vs `MO`), B&R section.
1. **Read literally** — note every card name; flag any you're not 100% sure of
2. **Verify Oracle text via Scryfall API** — actual `curl` commands with proper headers (the API rejects unidentified bot traffic)
3. **Verify the format ban list** — prefer the **Scryfall API banlist endpoint** (`?q=banned%3A<format>`, parseable JSON) over WebFetch of the Wizards B&R HTML page; cite both. Never cached.
4. **Verify current meta archetypes** — pulled from tournament aggregators (mtgtop8 `f=LE` for Legacy, `f=MO` for Modern)
4b. **Verify deck PRESENCE, not just card existence** — parse 2–3 real decklists per top archetype from `samples/<format>/` and live mtgtop8; "card legal" ≠ "card played"
5. **Identify critical interactions** — subtypes, mana value vs paid cost, MDFC semantics, channel-instant-speed (e.g., Boseiju), the "resolved permanents are immune to lock cards" rule
6. **Compute probabilities in Python** — hypergeometric via `math.comb`, never "approximately X%"
6b. **Run deterministic validators on the parsed decklist** — mana-base color check + 4-of legality at minimum; archetype similarity, devotion, joint-N-card, cantrip-depth when relevant. Quote validator output verbatim.
7. **Label evidence types** — sourced fact / verified data / inference / recommendation, never mixed

The full workflow, exact `curl` commands, mtgtop8 decklist parser, and Python deterministic validators (manabase legality, 4-of check, archetype similarity, joint-probability, cantrip-depth) live inline in `mtg-deck-analysis/SKILL.md`. Per-format constants (cantrip pools, Wasteland analog, archetype sample directories, format codes) live in `mtg-deck-analysis/format_data.py`. Two probability validators (`cantrip_depth`, `p_find_target_with_cantrips`) accept a `format=` keyword arg and consult `format_data.py.CANTRIP_POOLS[format]` to filter cantrip counts to format-legal cards. The other validators (`validate_manabase`, `check_four_of`, `archetype_similarity`, `joint_n_cards`, `devotion`) are format-agnostic — callers pass format-specific inputs (e.g., `archetype_similarity` receives the per-format sample-files glob from `ARCHETYPE_SAMPLE_DIRS[format]`).

## What `mtg-card-evaluation` does

Two question shapes, two modes. The skill picks the mode based on what the user provides (card + deck vs. card + format).

### Mode A — Card in Deck (five-lens scorecard)

For inclusion / swap / sideboard / replacement-after-ban decisions where a **target deck is given**. Five lenses scored independently from −2 to +2, then summed into one of five verdicts ranging from "strong include" to "don't include":

| Lens | What it checks |
|---|---|
| 1. Role Replacement | What deck slot the card fills, what existing card it displaces |
| 2. Mana Curve Fit | Castability given the deck's mana base and turn-by-turn plan |
| 3. Meta Fit | Performance against the top 5 archetypes by meta share |
| 4. Synergy Math | Card-type triggers, opponent hate-card exposure, probability-fueled engines |
| 5. Opportunity Cost | Whether a strictly better alternative exists |

Mode A ships three worked examples — Flow State in Blue Post, Tezzeret Cruel Captain in Blue Post, and Chalice of the Void in Blue Post — that show how scoring resolves real inclusion debates.

### Mode B — Card in Meta (six-lens card-in-meta positioning)

For "where does this card fit?" / "what decks would play it?" / "is it a meta staple?" questions where a **card and a format are given but NO target deck**. Six lenses, each with the same Iron Law Evidence block as Mode A, but the verdict is **qualitative** (a meta-position Tier) rather than a numeric sum, because there is no single deck to fit against:

| Lens | What it answers |
|---|---|
| B1. Role Identification | What role(s) the card fills, derived from verified Oracle text |
| B2. Archetype Fit Candidates | Which top-format archetypes currently fill that role, and with what card |
| B3. Targets / Enables | What this card answers (reactive) or enables (proactive), with meta-card counts |
| B4. Vulnerabilities | What removes / counters / blanks this card in the current meta |
| B5. Best Homes (Top 3) | Three most likely deck homes, each with a one-line Mode A summary scorecard |
| B6. Meta Position | Composite verdict: **Tier A** (likely staple, 4-of in best home) / **Tier B** (situational, 1–2 of) / **Tier C** (sideboard tech only) / **Tier D** (unplayable in current meta) |

Mode B ships a worked example: **Boseiju, Who Endures in Modern (May 2026)** — verified Oracle text, Tier B verdict overall, Tier A inside Amulet Titan, six Evidence blocks, archetype-by-archetype Best-Home analysis.

## Why this exists

LLM reasoning about MTG fails in characteristic ways. Each rule across both skills maps to a real failure observed during development:

| Failure | Skill rule |
|---|---|
| Cited a banned card (Mishra's Workshop) as a probability enabler | Iron Law applies to every card cited, including math inputs |
| Said "Chalice@2 catches Counterspell" — 0/12 sampled archetypes actually play Counterspell | Step 4b: verify deck presence, not card existence |
| Wrote "approximately 65%" when the actual hypergeometric was 24% | Step 6: Python `math.comb`, never inference |
| Treated Chalice as if it removed resolved permanents | Step 5: permanents in play are immune to lock cards |
| `WebFetch` returned 403 on `api.scryfall.com` | Tooling block: use `curl` with `User-Agent` + `Accept` headers |
| Tamiyo, Inq. Student listed as MV 2 in cached reference table | Iron Law: even the skill's own references must be re-verified |
| "Flow State will trigger 70% of the time" inferred without computing | Lens 4 of card-evaluation: use `joint_n_cards`, not estimation |
| First Mode B preview called Boseiju "sorcery-speed nonbasic-hate" — channel is instant-speed, and the effect hits artifact/enchantment/nonbasic land (not just lands) | Mode B Iron Law: Oracle text must be **fetched live**, not recalled; applies even to the skill author writing the worked example |
| Assumed Modern top-10 archetypes were Yawgmoth Pod / Hammer Time / Murktide; live mtgtop8 fetch on 2026-05-25 returned Boros Aggro / Affinity / Blink / Ruby Storm / Eldrazi Ramp / UR Aggro / UrzaTron / Living End / Amulet Titan / UW Control instead | Step 4: meta is **fetched on the day of analysis**, never recalled; sample directories are point-in-time snapshots and must be re-fetched when the meta shifts |

Both skills are built TDD-style: every rule has a concrete past failure behind it.

## Installation

Skills are per-user in Claude Code. Drop each skill folder into `~/.claude/skills/`:

```bash
git clone git@github.com:chinrw/mtg-agent-skill.git /tmp/mtg-agent-skill
ln -s /tmp/mtg-agent-skill/mtg-deck-analysis   ~/.claude/skills/mtg-deck-analysis
ln -s /tmp/mtg-agent-skill/mtg-card-evaluation ~/.claude/skills/mtg-card-evaluation
```

Or copy in place if you prefer non-symlinked installs:

```bash
git clone git@github.com:chinrw/mtg-agent-skill.git /tmp/mtg-agent-skill
cp -r /tmp/mtg-agent-skill/mtg-deck-analysis   ~/.claude/skills/
cp -r /tmp/mtg-agent-skill/mtg-card-evaluation ~/.claude/skills/
```

The directory names `mtg-deck-analysis` and `mtg-card-evaluation` must match the `name:` field inside each `SKILL.md` — keep them consistent or Claude Code won't pick up the skills.

### Nix home-manager

If you manage Claude Code via Nix, declare this repo as a flake input with `flake = false`, then map each skill subfolder to its install location. Example fragment for `home.file`:

```nix
home.file.".claude/skills/mtg-deck-analysis" = {
  source = "${inputs.mtg-agent-skill}/mtg-deck-analysis";
  recursive = true;
};
home.file.".claude/skills/mtg-card-evaluation" = {
  source = "${inputs.mtg-agent-skill}/mtg-card-evaluation";
  recursive = true;
};
```

## How invocation works

Both skills are `disable-model-invocation: true`, so Claude never auto-loads them. You invoke them explicitly with the slash command for the skill name. Within a `/mtg-deck-analysis` run, an inclusion question triggers an automatic `Skill` tool invocation of `mtg-card-evaluation` — that's the supported cross-skill pattern. You can also invoke `/mtg-card-evaluation` standalone.

This design trade-off keeps the larger reference content (~4500 words for deck-analysis, ~1700 for card-evaluation) out of every conversation's context budget. They load only when explicitly asked.

To make either skill auto-load instead, remove `disable-model-invocation: true` from its frontmatter and let Claude pick it up based on the `description:` field.

## File layout

```
mtg-agent-skill/
├── README.md                                  # this file
├── PLAN-modern-mode-b.md                      # v5 implementation plan (shipped; will be archived)
├── mtg-deck-analysis/                         # deck-level workflow skill (format-aware)
│   ├── SKILL.md                               # Step 0 (format ID) → Step 7 + tooling + deterministic validators
│   ├── format_data.py                         # per-format constants: CANTRIP_POOLS, WASTELAND_ANALOG, ARCHETYPE_SAMPLE_DIRS, FORMAT_CODES, etc.
│   ├── reference-tables/                      # split per-format
│   │   ├── legacy.md                          # Legacy pitfalls / staples / manabase + Live Banlist Verification (Scryfall API + Wizards)
│   │   └── modern.md                          # Modern pitfalls / staples / manabase + Live Banlist Verification (Scryfall API + Wizards)
│   └── samples/                               # split per-format
│       ├── legacy/                            # 10 real Legacy decklists + README index
│       │   ├── README.md                      # index — archetype, player, tournament, source URL per file
│       │   ├── Legacy_12_-_Post_by_sm294.txt              # Cloudpost / Blue Post (user-submitted)
│       │   ├── Legacy_Trini_Tron_Karn_by_SinKarma.txt     # Trini Tron / Artifact Karn (user-submitted)
│       │   ├── Legacy_UR_Tempo_by_silviawataru.txt        # UR Delver / Tempo
│       │   ├── Legacy_Dimir_Tempo_by_kyataoka.txt         # Dimir Tempo
│       │   ├── Legacy_Eldrazi_Aggro_by_Schmeckles.txt     # Eldrazi Aggro
│       │   ├── Legacy_UWx_Control_by_habsburger.txt       # UWx Control
│       │   ├── Legacy_Lands_by_Lincerastas.txt            # Lands (Mono-Green)
│       │   ├── Legacy_Doomsday_by_Sinflower.txt           # Doomsday (Tempo Flow)
│       │   ├── Legacy_Death_and_Taxes_by_l337erhosen.txt  # Death & Taxes (Yorion 80-card)
│       │   └── Legacy_Boros_Aggro_by_Mikebrav.txt         # Boros Aggro
│       └── modern/                            # 10 real Modern decklists + README index (fetched 2026-05-25)
│           ├── README.md                      # index — archetype, meta share, player, tournament per file
│           ├── Modern_Boros_Aggro_by_BigDadChad.txt       # Boros Aggro
│           ├── Modern_Affinity_by_Tommaso_Ciampolini.txt  # Affinity
│           ├── Modern_Blink_by_Barneygumbal.txt           # Blink (Esper variant)
│           ├── Modern_UR_Aggro_by_Eggybenny.txt           # UR Aggro (Cutter Prowess variant)
│           ├── Modern_UrzaTron_by_Evan_Johnson.txt        # UrzaTron
│           ├── Modern_Ruby_Storm_by_Bernastorres.txt      # Ruby Storm
│           ├── Modern_Eldrazi_Ramp_by_Mickael_Gervais.txt # Eldrazi Ramp (RG variant)
│           ├── Modern_UW_Control_by_Bigatti.txt           # UW Control
│           ├── Modern_Living_End_by_Lorenzo_Paolini.txt   # Living End
│           └── Modern_Amulet_Titan_by_HouseOfManaMTG.txt  # Amulet Titan
└── mtg-card-evaluation/                       # inclusion-question + card-in-meta skill
    └── SKILL.md                               # Mode A (5-lens, deck given) + Mode B (6-lens, meta given)
```

`SKILL.md` is what Claude Code loads when the skill is invoked. Other markdown files load via `Read` only when an analysis actually needs them, to keep context lean. Format-specific files (`reference-tables/<format>.md`, `samples/<format>/`) are selected based on the format identified at Step 0 of the analysis.

## Sample input

`mtg-deck-analysis/samples/legacy/` contains 10 real Legacy decklists used as test input when validating skill changes. See `samples/legacy/README.md` for the full index with archetype, player, tournament, and mtgtop8 source URL per file. The two original user-submitted lists (`Legacy_12_-_Post_by_sm294.txt`, `Legacy_Trini_Tron_Karn_by_SinKarma.txt`) motivated the skill — the original analysis of them surfaced most of the failure modes the skills now prevent. The remaining eight files cover one representative recent decklist per top-meta Legacy archetype (UR Tempo, Dimir Tempo, Eldrazi Aggro, UWx Control, Lands, Doomsday, Death & Taxes, Boros Aggro), fetched from mtgtop8 in May 2026.

`mtg-deck-analysis/samples/modern/` contains 10 real Modern decklists fetched live from mtgtop8 on 2026-05-25 — one per top-meta archetype as of fetch day: Boros Aggro, Affinity, Blink (Esper variant), UR Aggro, UrzaTron, Ruby Storm, Eldrazi Ramp, UW Control, Living End, Amulet Titan. See `samples/modern/README.md` for meta share, player, tournament, and date per file. Note that the actual May-2026 Modern top 10 looked nothing like the archetypes commonly associated with the format in training data (no Yawgmoth, no Hammer Time, no Murktide UR Tempo) — a reminder that meta is fetched, never recalled.

Both sample directories are **point-in-time snapshots**. The meta shifts; re-fetch when working on a different period. Each file is plain text (`<count> <card name>` per line, `Sideboard` separates mainboard from sideboard) and carries a comment header with archetype, player, tournament, and source URL.

`mtg-card-evaluation` doesn't ship its own samples — Mode A worked examples reference the Legacy lists by archetype, and the Mode B worked example (Boseiju, Who Endures in Modern) is evidenced against the Modern lists.

## Versions

- **v1** — initial 7-step workflow + reference tables, addressing failures around Petrified Hamlet, Sink into Stupor, Tron probabilities, Monolith+Key combo, Sowing Mycospawn ban, Flow State trigger rates.
- **v2** — added Step 4b (deck-presence verification), strengthened Step 6 (Python required), added permanent-immunity caveat, inlined Scryfall API tooling.
- **v3** — consolidated `tooling-notes.md` into `SKILL.md` since the skill is manual-invoke; updated reference tables for Workshop/Tamiyo/Counterspell corrections; added 8 mtgtop8 sample decklists + Step 6b deterministic validators (manabase, 4-of, devotion, archetype-similarity, joint-N-cards, cantrip-depth); GREEN-verified by subagent on Trinisphere meta question and Doomsday validator scenarios.
- **v4** — repo restructured to one folder per skill at repo root. Card-evaluation framework split out as its own skill (`mtg-card-evaluation`) callable standalone or as sub-skill via Skill tool; `mtg-deck-analysis` retains samples + reference-tables. Motivates from name-folder correspondence and reusability of the five-lens framework outside a full deck-analysis run.
- **v4.1** (`mtg-card-evaluation` v2, 2026-05-25) — added Iron Law: no lens score without evidence. Each lens output now requires an Evidence block citing Scryfall / mtgtop8 / Python output / named alternative. Worked examples rewritten with concrete citations and Python computations.
- **v5** (2026-05-25, **shipped**) — multi-format (Legacy + Modern) support in `mtg-deck-analysis` and Mode B (card-in-meta) framework in `mtg-card-evaluation`. Per `PLAN-modern-mode-b.md`. Delivered in six commits:
  - *Phase 1:* restructure `reference-tables.md` → `reference-tables/{legacy,modern}.md` and `samples/` → `samples/{legacy,modern}/`; add "Live Banlist Verification Sources" section to both reference tables (Scryfall API banlist endpoint `?q=banned%3A<format>` preferred over Wizards HTML fetch).
  - *Phase 2:* mandatory Step 0 (format identification) added to `mtg-deck-analysis/SKILL.md`. Honor explicit `Legacy:` / `Modern:` prefix; otherwise ASK the user (with an optional one-line hint citing format-disjoint cards like Wasteland or Ragavan/W6 when present — never auto-inferred). Format is bound for the rest of the analysis run; refuses to proceed without it.
  - *Phase 3:* 10 Modern sample decklists fetched live from mtgtop8 on 2026-05-25 (`f=MO`, `meta=54`) — Boros Aggro, Affinity, Blink, UR Aggro, UrzaTron, Ruby Storm, Eldrazi Ramp, UW Control, Living End, Amulet Titan.
  - *Phase 4:* `reference-tables/modern.md` populated with Scryfall-verified Modern staples, manabase patterns (fetchlands + shocks + Triomes + MDFCs, no Wasteland), Modern interaction pitfalls (evoke-pitch elementals MV 5 not 0, channel-instant-speed, etc.), and "Looks Modern but isn't" notes — no static banlist cached.
  - *Phase 5:* `format_data.py` module exporting `CANTRIP_POOLS`, `WASTELAND_ANALOG`, `ARCHETYPE_SAMPLE_DIRS`, `FORMAT_CODES`. Two probability validators (`cantrip_depth`, `p_find_target_with_cantrips`) accept a `format=` keyword arg and consult `format_data.py.CANTRIP_POOLS[format]` to filter cantrip counts to format-legal cards. The other validators (`validate_manabase`, `check_four_of`, `archetype_similarity`, `joint_n_cards`, `devotion`) are format-agnostic — callers pass format-specific inputs (e.g., `archetype_similarity` receives the per-format sample-files glob from `ARCHETYPE_SAMPLE_DIRS[format]`); manabase color logic stays format-agnostic.
  - *Phase 6:* Mode B (six-lens card-in-meta positioning) added to `mtg-card-evaluation/SKILL.md`. Same Iron Law as Mode A, qualitative Tier verdict (A/B/C/D) instead of numeric sum. Worked example: Boseiju, Who Endures in Modern May 2026.

  Phase 7 (TDD verification) was rolled into per-phase GREEN tests at commit time; Phase 8 = this README update.

See the `## TDD Status` section at the bottom of each `SKILL.md` for the running RED-failure log for that skill.

## License

MIT.

## Contributing

The skills follow a TDD-for-documentation discipline (inspired by the [superpowers writing-skills](https://github.com/obra/superpowers) methodology): no rule is added without a concrete failure that motivated it. If you find a case where either skill produces wrong analysis, file an issue with:

1. The question that triggered the failure
2. The Claude output
3. The actual correct answer (with Scryfall / mtgtop8 / Wizards B&R citations)

That's the RED phase. The fix gets added to the relevant skill, then GREEN-verified by a subagent test on a fresh-but-analogous scenario.

## Built with

- [Claude Code](https://claude.com/claude-code) — Agent Skills support
- [Anthropic Skills spec](https://agentskills.io/specification)
- [Scryfall API](https://scryfall.com/docs/api) — card data
- [mtgtop8](https://www.mtgtop8.com/) — tournament metagame
- [Wizards B&R](https://magic.wizards.com/en/banned-restricted-list) — live ban list

---

Maintained by [@chinrw](https://github.com/chinrw).
