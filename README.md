# mtg-agent-skill

A Claude Code [Agent Skill](https://agentskills.io) for rigorous Magic: The Gathering deck analysis. Enforces a verification-first workflow that prevents the most common failure modes when LLMs reason about MTG: stale card text from training data, outdated ban lists, hallucinated meta percentages, and lock-piece interactions that ignore the resolved-permanent rule.

## What this skill does

When you invoke it, Claude runs a 7-step workflow on any MTG decklist or meta question:

1. **Read literally** — flag every uncertain card
2. **Verify Oracle text via Scryfall API** — actual `curl` commands with proper headers (the API rejects unidentified bot traffic)
3. **Verify the format ban list** — live fetch from Wizards, never cached
4. **Verify current meta archetypes** — pulled from tournament aggregators
5. **Verify deck PRESENCE, not just card existence** — parse 2–3 real decklists per top archetype; "card legal" ≠ "card played"
6. **Identify critical interactions** — subtypes, mana value vs paid cost, MDFC semantics, the "resolved permanents are immune to lock cards" rule
7. **Compute probabilities in Python** — hypergeometric via `math.comb`, never "approximately X%"
8. **Label evidence types** — sourced fact / verified data / inference / recommendation, never mixed

The full workflow, exact `curl` commands, mtgtop8 decklist parser, and Python probability template all live inline in `SKILL.md`.

## Why this exists

LLM reasoning about MTG fails in characteristic ways. Each rule in this skill maps to a real failure observed during development:

| Failure | Skill rule |
|---|---|
| Cited a banned card (Mishra's Workshop) as a probability enabler | Iron Law applies to every card cited, including math inputs |
| Said "Chalice@2 catches Counterspell" — 0/12 sampled archetypes actually play Counterspell | Step 4b: verify deck presence, not card existence |
| Wrote "approximately 65%" when the actual hypergeometric was 24% | Step 6: Python `math.comb`, never inference |
| Treated Chalice as if it removed resolved permanents | Step 5: permanents in play are immune to lock cards |
| `WebFetch` returned 403 on `api.scryfall.com` | Tooling block: use `curl` with `User-Agent` + `Accept` headers |
| Tamiyo, Inq. Student listed as MV 2 in cached reference table | Iron Law: even the skill's own references must be re-verified |

The skill is built TDD-style: every rule has a concrete past failure behind it.

## Installation

Skills are per-user in Claude Code. Drop the directory under `~/.claude/skills/`:

```bash
git clone git@github.com:chinrw/mtg-agent-skill.git ~/.claude/skills/mtg-deck-analysis
```

Or, if you keep a working copy elsewhere, symlink it:

```bash
ln -s /path/to/mtg-agent-skill ~/.claude/skills/mtg-deck-analysis
```

The directory name `mtg-deck-analysis` matches the `name:` field in `SKILL.md` — keep them consistent or Claude Code won't pick up the skill.

### Nix home-manager

If you manage Claude Code via Nix, point a `home.file` entry at this directory using `mkOutOfStoreSymlink` for a live link, or add it as a flake input with `flake = false`.

## How to invoke

This skill is configured with `disable-model-invocation: true`, so Claude never auto-loads it. You invoke it explicitly:

```
/mtg-deck-analysis analyze the current Legacy meta against Death & Taxes
```

This design trade-off keeps the skill (with its ~2200-word `SKILL.md`) out of every conversation's context budget. It only loads when you ask for it.

To make it auto-load instead, remove `disable-model-invocation: true` from the frontmatter and let Claude pick it up based on the `description:` field.

## File layout

```
mtg-agent-skill/
├── SKILL.md                # main workflow + all tooling commands inline
├── reference-tables.md     # heavy lookup data — card pitfalls, manabase, sideboard, combo tables
├── mtg-card-evaluation.md  # five-lens framework for "does card X fit deck Y"
└── samples/                # real Legacy decklists used as skill test input
    ├── README.md           # index — archetype, player, tournament, source URL per file
    ├── Legacy_12_-_Post_by_sm294.txt              # Cloudpost / Blue Post (user-submitted)
    ├── Legacy_Trini_Tron_Karn_by_SinKarma.txt     # Trini Tron / Artifact Karn (user-submitted)
    ├── Legacy_UR_Tempo_by_silviawataru.txt        # UR Delver / Tempo
    ├── Legacy_Dimir_Tempo_by_kyataoka.txt         # Dimir Tempo
    ├── Legacy_Eldrazi_Aggro_by_Schmeckles.txt     # Eldrazi Aggro
    ├── Legacy_UWx_Control_by_habsburger.txt       # UWx Control
    ├── Legacy_Lands_by_Lincerastas.txt            # Lands (Mono-Green)
    ├── Legacy_Doomsday_by_Sinflower.txt           # Doomsday (Tempo Flow)
    ├── Legacy_Death_and_Taxes_by_l337erhosen.txt  # Death & Taxes (Yorion 80-card)
    └── Legacy_Boros_Aggro_by_Mikebrav.txt         # Boros Aggro
```

`SKILL.md` loads when the skill is invoked. The other markdown files load via `Read` only when an analysis actually needs them, to keep context lean.

## Sample input

`samples/` contains real Legacy decklists used as test input when validating skill changes. See `samples/README.md` for the full index with archetype, player, tournament, and mtgtop8 source URL per file. The two original user-submitted lists (`Legacy_12_-_Post_by_sm294.txt`, `Legacy_Trini_Tron_Karn_by_SinKarma.txt`) motivated the skill — the original analysis of them surfaced most of the failure modes the skill now prevents. The remaining eight files cover one representative recent decklist per top-meta Legacy archetype (UR Tempo, Dimir Tempo, Eldrazi Aggro, UWx Control, Lands, Doomsday, Death & Taxes, Boros Aggro), fetched from mtgtop8 in May 2026.

## Versions

- **v1** — initial 7-step workflow + reference tables, addressing failures around Petrified Hamlet, Sink into Stupor, Tron probabilities, Monolith+Key combo, Sowing Mycospawn ban, Flow State trigger rates.
- **v2** — added Step 4b (deck-presence verification), strengthened Step 6 (Python required), added permanent-immunity caveat, inlined Scryfall API tooling.
- **v3** — consolidated `tooling-notes.md` into `SKILL.md` since the skill is manual-invoke; updated reference tables for Workshop/Tamiyo/Counterspell corrections; GREEN-verified by subagent on a fresh Trinisphere meta question.

See the `## TDD Status` section at the bottom of `SKILL.md` for the running RED-failure log.

## License

MIT.

## Contributing

The skill follows a TDD-for-documentation discipline (inspired by the [superpowers writing-skills](https://github.com/obra/superpowers) methodology): no rule is added without a concrete failure that motivated it. If you find a case where the skill produces wrong analysis, file an issue with:

1. The question that triggered the failure
2. The Claude output
3. The actual correct answer (with Scryfall / mtgtop8 / Wizards B&R citations)

That's the RED phase. The fix gets added to the skill, then GREEN-verified by a subagent test on a fresh-but-analogous scenario.

## Built with

- [Claude Code](https://claude.com/claude-code) — Agent Skills support
- [Anthropic Skills spec](https://agentskills.io/specification)
- [Scryfall API](https://scryfall.com/docs/api) — card data
- [mtgtop8](https://www.mtgtop8.com/) — tournament metagame
- [Wizards B&R](https://magic.wizards.com/en/banned-restricted-list) — live ban list

---

Maintained by [@chinrw](https://github.com/chinrw).
