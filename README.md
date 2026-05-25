# mtg-agent-skill

Two Claude Code [Agent Skills](https://agentskills.io) for rigorous Magic: The Gathering analysis. Both enforce a verification-first workflow that prevents the most common failure modes when LLMs reason about MTG: stale card text from training data, outdated ban lists, hallucinated meta percentages, and lock-piece interactions that ignore the resolved-permanent rule.

## Skills in this repo

| Skill | Folder | What it answers |
|---|---|---|
| [`mtg-deck-analysis`](./mtg-deck-analysis) | `mtg-deck-analysis/` | Decklist evaluation, matchup prediction, probability math, meta positioning |
| [`mtg-card-evaluation`](./mtg-card-evaluation) | `mtg-card-evaluation/` | "Does card X belong in deck Y?" — five-lens scoring framework for inclusion/replacement/sideboard slot decisions |

Both skills are configured with `disable-model-invocation: true`. They do not auto-load into context. Invoke them explicitly:

```
/mtg-deck-analysis analyze the current Legacy meta against Death & Taxes
/mtg-card-evaluation should I add Chalice of the Void to my Blue Post list?
```

`mtg-deck-analysis` invokes `mtg-card-evaluation` automatically (via the Skill tool) when a deck-analysis run hits an inclusion question. You don't need to chain them by hand.

## What `mtg-deck-analysis` does

When you invoke it, Claude runs a 7-step workflow on any MTG decklist or meta question:

1. **Read literally** — flag every uncertain card
2. **Verify Oracle text via Scryfall API** — actual `curl` commands with proper headers (the API rejects unidentified bot traffic)
3. **Verify the format ban list** — live fetch from Wizards, never cached
4. **Verify current meta archetypes** — pulled from tournament aggregators
5. **Verify deck PRESENCE, not just card existence** — parse 2–3 real decklists per top archetype; "card legal" ≠ "card played"
6. **Identify critical interactions** — subtypes, mana value vs paid cost, MDFC semantics, the "resolved permanents are immune to lock cards" rule
7. **Compute probabilities in Python** — hypergeometric via `math.comb`, never "approximately X%"
8. **Label evidence types** — sourced fact / verified data / inference / recommendation, never mixed

The full workflow, exact `curl` commands, mtgtop8 decklist parser, and Python deterministic validators (manabase legality, 4-of check, archetype similarity, joint-probability, cantrip-depth) all live inline in `mtg-deck-analysis/SKILL.md`.

## What `mtg-card-evaluation` does

A five-lens scorecard for inclusion questions, scored independently then summed for a verdict:

| Lens | What it checks |
|---|---|
| 1. Role Replacement | What deck slot the card fills, what existing card it displaces |
| 2. Mana Curve Fit | Castability given the deck's mana base and turn-by-turn plan |
| 3. Meta Fit | Performance against the top 5 archetypes by meta share |
| 4. Synergy Math | Card-type triggers, opponent hate-card exposure, probability-fueled engines |
| 5. Opportunity Cost | Whether a strictly better alternative exists |

Each lens scores −2 to +2; the sum maps to one of five verdicts ranging from "strong include" to "don't include." `mtg-card-evaluation/SKILL.md` ships three worked examples — Flow State in Blue Post, Tezzeret Cruel Captain in Blue Post, and Chalice of the Void in Blue Post — that show how scoring resolves real inclusion debates.

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
├── PLAN-modern-mode-b.md                      # multi-format + Mode B implementation plan (active)
├── mtg-deck-analysis/                         # deck-level workflow skill (format-aware)
│   ├── SKILL.md                               # 7-step workflow + tooling + deterministic validators
│   ├── reference-tables/                      # split per-format
│   │   ├── legacy.md                          # Legacy pitfalls/staples/manabase + Live Banlist Verification (Scryfall API + Wizards)
│   │   └── modern.md                          # Modern Live Banlist Verification canonical; rest TODO Phase 4
│   └── samples/                               # split per-format
│       ├── legacy/                            # real Legacy decklists used as skill test input
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
│       └── modern/                            # populated in Phase 3 of PLAN-modern-mode-b.md
│           └── README.md                      # stub explaining target archetypes + file format
└── mtg-card-evaluation/                       # inclusion-question + (Phase 6) card-in-meta skill
    └── SKILL.md                               # five-lens Mode A; Mode B added in Phase 6
```

`SKILL.md` is what Claude Code loads when the skill is invoked. Other markdown files load via `Read` only when an analysis actually needs them, to keep context lean. Format-specific files (`reference-tables/<format>.md`, `samples/<format>/`) are selected based on the format identified at the start of the analysis.

## Sample input

`mtg-deck-analysis/samples/legacy/` contains real Legacy decklists used as test input when validating skill changes. See `samples/legacy/README.md` for the full index with archetype, player, tournament, and mtgtop8 source URL per file. The two original user-submitted lists (`Legacy_12_-_Post_by_sm294.txt`, `Legacy_Trini_Tron_Karn_by_SinKarma.txt`) motivated the skill — the original analysis of them surfaced most of the failure modes the skills now prevent. The remaining eight files cover one representative recent decklist per top-meta Legacy archetype (UR Tempo, Dimir Tempo, Eldrazi Aggro, UWx Control, Lands, Doomsday, Death & Taxes, Boros Aggro), fetched from mtgtop8 in May 2026.

`mtg-deck-analysis/samples/modern/` is stubbed for Phase 3 of `PLAN-modern-mode-b.md` (will hold 8–10 Modern decklists matching the top-meta Modern archetypes as of fetch date).

`mtg-card-evaluation` doesn't ship its own samples — its worked examples reference these same lists by archetype.

## Versions

- **v1** — initial 7-step workflow + reference tables, addressing failures around Petrified Hamlet, Sink into Stupor, Tron probabilities, Monolith+Key combo, Sowing Mycospawn ban, Flow State trigger rates.
- **v2** — added Step 4b (deck-presence verification), strengthened Step 6 (Python required), added permanent-immunity caveat, inlined Scryfall API tooling.
- **v3** — consolidated `tooling-notes.md` into `SKILL.md` since the skill is manual-invoke; updated reference tables for Workshop/Tamiyo/Counterspell corrections; added 8 mtgtop8 sample decklists + Step 6b deterministic validators (manabase, 4-of, devotion, archetype-similarity, joint-N-cards, cantrip-depth); GREEN-verified by subagent on Trinisphere meta question and Doomsday validator scenarios.
- **v4** — repo restructured to one folder per skill at repo root. Card-evaluation framework split out as its own skill (`mtg-card-evaluation`) callable standalone or as sub-skill via Skill tool; `mtg-deck-analysis` retains samples + reference-tables. Motivates from name-folder correspondence and reusability of the five-lens framework outside a full deck-analysis run.
- **v4.1** (`mtg-card-evaluation` v2, 2026-05-25) — added Iron Law: no lens score without evidence. Each lens output now requires an Evidence block citing Scryfall / mtgtop8 / Python output / named alternative. Worked examples rewritten with concrete citations and Python computations.
- **v5 Phase 1** (in progress) — multi-format restructure groundwork. Per `PLAN-modern-mode-b.md`. `reference-tables.md` → `reference-tables/{legacy,modern}.md`; `samples/` → `samples/{legacy,modern}/`. Modern stubs created. Both reference tables now carry "Live Banlist Verification Sources" sections documenting the Scryfall API banlist endpoint (`?q=banned%3A<format>`) alongside the Wizards B&R URL. Skill is fully functional for Legacy after Phase 1; Modern data populates in Phases 3–4, mandatory Step 0 format-identification in Phase 2, Mode B card-in-meta in Phase 6.

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
