# Sample Decklists

Real Legacy decklists representative of the current meta (sampled 2026-05-25). Use these as test input when validating skill changes or as reference for current-meta interaction patterns.

| File | Archetype | Player / Source | Tournament | Fetched From |
|------|-----------|------------------|------------|--------------|
| Legacy_12_-_Post_by_sm294.txt | Cloudpost (Blue Post) | sm294 | User-submitted | (original) |
| Legacy_Trini_Tron_Karn_by_SinKarma.txt | Trini Tron / Artifact Karn | SinKarma | User-submitted | (original) |
| Legacy_UR_Tempo_by_silviawataru.txt | UR Tempo (UR Delver) | silviawataru | MTGO Challenge 32 (#12) | https://www.mtgtop8.com/event?e=85576&d=850019&f=LE |
| Legacy_Dimir_Tempo_by_kyataoka.txt | Dimir Tempo | kyataoka | MTGO Challenge 32 (#3-4) | https://www.mtgtop8.com/event?e=85576&d=850030&f=LE |
| Legacy_Eldrazi_Aggro_by_Schmeckles.txt | Eldrazi Aggro | Schmeckles | MTGO Challenge 32 (#5-8) | https://www.mtgtop8.com/event?e=85492&d=849381&f=LE |
| Legacy_UWx_Control_by_habsburger.txt | UWx Control | habsburger | MTGO Challenge 32 (#10) | https://www.mtgtop8.com/event?e=85576&d=850022&f=LE |
| Legacy_Lands_by_Lincerastas.txt | Lands (Mono-Green) | Lincerastas | Open Qualifier CDF @ Rennes, France (#3-4) | https://www.mtgtop8.com/event?e=85537&d=849686&f=LE |
| Legacy_Doomsday_by_Sinflower.txt | Doomsday (Tempo Flow) | Sinflower | Open Qualifier CDF @ Rennes, France (#2) | https://www.mtgtop8.com/event?e=85537&d=849685&f=LE |
| Legacy_Death_and_Taxes_by_l337erhosen.txt | Death & Taxes (Yorion 80-card) | l337erhosen | MTGO League (#3) | https://www.mtgtop8.com/event?e=85577&d=850037&f=LE |
| Legacy_Boros_Aggro_by_Mikebrav.txt | Boros Aggro | Mikebrav | MTGO Challenge 32 (#12) | https://www.mtgtop8.com/event?e=85491&d=849357&f=LE |

## Notes

- Decklists are point-in-time snapshots from mtgtop8 (`meta=338`, May 2026). Meta shifts; re-fetch if working on a different meta period.
- Each file is plain text: `<count> <card name>` per line, with `Sideboard` separating mainboard from sideboard.
- Cards inside each section are emitted in the order mtgtop8 renders them (typically by category: lands, creatures, non-creature spells). The order is preserved on purpose — it carries information about the deck's structure.
- **Death & Taxes is a Yorion 80-card companion deck** — 80 mainboard + 15 sideboard (Yorion, Sky Nomad is the first sideboard entry). This is the dominant current build of D&T in Legacy; all of the 16 most recent top-finishing D&T lists at the time of fetch were Yorion variants. Other archetype files are standard 60 + 15.
- Existing user-submitted files (`Legacy_12_-_Post_by_sm294.txt`, `Legacy_Trini_Tron_Karn_by_SinKarma.txt`) cover Cloudpost / Blue Post and Trini Tron / Artifact Karn ramp shells respectively, so those archetypes are not duplicated here.
- Eldrazi Aggro (Schmeckles) is the sole representative for the Eldrazi family — Eldrazi Stompy and other Eldrazi shells overlap heavily and are not separately included. Initiative Stompy and Mystic Forge are intentionally omitted (over-represented in any given week and overlapping with the artifact / Eldrazi shells already covered).
