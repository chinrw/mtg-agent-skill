# Modern samples — index

10 representative Modern decklists for skill test input. Fetched from mtgtop8 on **2026-05-25** with `?f=MO` and `meta=54`. Each file is one most-recent decklist per top-meta archetype as of fetch day.

| File | Archetype | Meta share | Player | Tournament | Tournament date | MB / SB |
|---|---|---|---|---|---|---|
| `Modern_Boros_Aggro_by_BigDadChad.txt` | Boros Aggro | 12% | BigDadChad | MTGO League | 2026-05-24 | 60 / 15 |
| `Modern_Affinity_by_Tommaso_Ciampolini.txt` | Affinity | 12% | Tommaso Ciampolini | RCQ @ Magic Maze (Prato, Italy) | 2026-05-24 | 60 / 15 |
| `Modern_Blink_by_Barneygumbal.txt` | Blink (Esper variant) | 7% | Barneygumbal | MTGO Challenge 32 | 2026-05-24 | 60 / 15 |
| `Modern_UR_Aggro_by_Eggybenny.txt` | UR Aggro (Cutter Prowess variant) | 4% | Eggybenny | MTGO Challenge 32 | 2026-05-24 | 60 / 15 |
| `Modern_UrzaTron_by_Evan_Johnson.txt` | UrzaTron | 4% | Evan Johnson | RCQ @ The Mighty Meeple (Concord, NC) | 2026-05-23 | 60 / 15 |
| `Modern_Ruby_Storm_by_Bernastorres.txt` | Ruby Storm | 4% | Bernastorres | MTGO Challenge 32 | 2026-05-24 | 60 / 15 |
| `Modern_Eldrazi_Ramp_by_Mickael_Gervais.txt` | Eldrazi Ramp (RG variant) | 3% | Mickael Gervais | RCQ @ Magiccorporation (Paris, France) | 2026-05-23 | 60 / 15 |
| `Modern_UW_Control_by_Bigatti.txt` | UW Control | 3% | Bigatti | (event title not extracted) | (date pending) | 60 / **14** |
| `Modern_Living_End_by_Lorenzo_Paolini.txt` | Living End | 3% | Lorenzo Paolini | RCQ @ Magic Maze (Prato, Italy) | 2026-05-24 | 60 / 15 |
| `Modern_Amulet_Titan_by_HouseOfManaMTG.txt` | Amulet Titan | 3% | HouseOfManaMTG | MTGO Challenge 32 | 2026-05-23 | 60 / 15 |

**Coverage by play pattern:**
- Aggro: Boros Aggro, Affinity, UR Aggro
- Midrange / Toolbox: Blink (Esper variant), UW Control
- Big mana / Ramp: UrzaTron, Eldrazi Ramp, Amulet Titan
- Combo: Ruby Storm, Living End

**Note on UW Control sideboard size:** the player ran a 14-card sideboard (4 Consign to Memory + 2 High Noon + 3 Mystical Dispute + 1 Surgical Extraction + 2 Vexing Bauble + 2 Wrath of the Skies). This is unusual but legal — Modern sideboards are `≤ 15`, not `= 15`. Don't treat the 14-card count as a parse error.

## Format-specific notes

These are Modern decklists. The skill's `validate_manabase`, `archetype_similarity`, `joint_n_cards`, etc. all work format-agnostically — the data here just needs `format=modern` passed through (see Step 0 in parent `SKILL.md` for the binding).

## Fetch reproducibility

Same `curl` pattern as Legacy samples — see `../../SKILL.md` Tooling block. For Modern:

```
https://www.mtgtop8.com/format?f=MO              # format page
https://www.mtgtop8.com/archetype?a=NNN&meta=54&f=MO   # archetype page
https://www.mtgtop8.com/event?e=NNN&d=NNN&f=MO   # individual deck page
```

Mtgtop8's `meta` code changes per period. `meta=54` was current as of 2026-05-25. Refetch using the format page's current code on later days.

## Discipline

Samples are **examples at an explicit timestamp**, not authoritative facts about the current meta. Any analysis citing one of these files must also cite the fetch date and refetch live data if making meta-share claims. See `../../SKILL.md` **Using Sample Decklists** for the full staleness rules.
