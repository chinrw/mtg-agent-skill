# Modern samples — STUB

This directory will be populated in **Phase 3** of `PLAN-modern-mode-b.md`.

## Planned contents

8–10 representative Modern decklists from mtgtop8, one per top-meta archetype as of the fetch date. Target archetypes (re-verify mtgtop8 Modern share on fetch day before committing):

- UR Murktide / UR Tempo
- Yawgmoth Pod
- Living End
- Eldrazi Tron (or Mono-Green Tron — pick the dominant variant on fetch day)
- Domain Zoo
- Boros Energy
- Hammer Time
- Amulet Titan
- Through the Breach Scapeshift OR Goryo's Vengeance combo
- A tier-2 deck for variety (Mill, UB Reanimator, etc.)

## File format

Same format as `../legacy/*.txt` files. Each file header:

```
# Format: Modern
# Archetype: <archetype name>
# Player: <player name>
# Tournament: <event name>
# Source: https://mtgtop8.com/event?e=<id>&d=<deck-id>
# Fetched: 2026-MM-DD

<count> <card name>
...
```

## How files get added

Use the mtgtop8 parser pattern documented in `../../SKILL.md` Tooling block. Always include the fetch date in the file header. Do NOT add a file without verifying the player/tournament/date via the mtgtop8 event page.

## Discipline

Samples are **examples at an explicit timestamp**, not authoritative facts about the current meta. Any analysis citing one of these files must also cite the fetch date and refetch live data if making meta-share claims.
