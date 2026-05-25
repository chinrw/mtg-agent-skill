# Modern Reference Tables

Living reference for Modern card-specific interactions and pitfalls. Always verify the current Oracle text on Scryfall before relying on any entry — printings change, errata happen, ban status shifts every few months. Entries were last verified live via Scryfall on **2026-05-25** during the v5 Phase 4 build.

## Card Name Pitfalls (Modern Names That Mislead)

| Card | Wrong assumption | Reality (Scryfall verified 2026-05-25) |
|---|---|---|
| Boseiju, Who Endures | Sorcery-speed, hits only nonbasic lands | Legendary Land. Channel ability is **instant-speed**, hits **artifact OR enchantment OR nonbasic land**. `{1}{G}` channel cost; reduces by `{1}` per legendary creature you control |
| Otawara, Soaring City | Wasteland analog | Legendary Land. Channel `{2}{U}` is instant-speed; bounces target nonland permanent. Does NOT destroy lands. Modern has no Wasteland-equivalent |
| Urza's Saga | Just a Tron piece | `Enchantment Land — Urza's Saga` (typed BOTH). Sage Saga (chapter II tutors construct, chapter III sacrifices to tutor MV-1 artifact). Tutors only MV-1 artifacts, not arbitrary artifacts |
| Solitude / Subtlety / Endurance | MV 0 when evoke-pitched | MV is **the printed cost**: Solitude MV 5, Subtlety MV 4, Endurance MV 3 (all `Creature — Elemental Incarnation`). Evoke-pitch pays {0} mana but Chalice@5 still catches Solitude, Chalice@4 catches Subtlety, Chalice@3 catches Endurance. Mana value never changes |
| Force of Negation | Just a Force of Will | MV 3 (NOT 5 — Force of Will is MV 5 in Legacy). Pitch alt-cast off-turn requires blue card exile. Chalice@3 catches it always |
| Phelia, Exuberant Shepherd | A token-maker | MV 2 Legendary Creature — Dog with Flash. Whenever it attacks, exiles a nonland permanent until end step; if that card entered under your control, +1/+1 counter on Phelia. Critical Modern blink/Boros anchor |
| Mishra's Bauble | Cantrip | MV 0 Artifact. `{T}, Sacrifice this artifact: Look at the top card of target player's library. Draw a card at the beginning of the next turn's upkeep.` The DRAW happens — so it triggers Bowmasters next upkeep. The "look" itself doesn't |
| Ragavan, Nimble Pilferer | Legal in both formats | Legal in **Modern only** (`legacy=banned`). Hard Modern signal in Step 0. The "Treasure tokens + impulse-draw" trigger fires on combat damage to a player |
| Ajani, Nacatl Pariah | Just a creature | MDFC (modal double-faced card). Front: Legendary Creature — Cat Warrior (MV 2). Back: Legendary Planeswalker — Ajani (Ajani, Nacatl Avenger). Boros Aggro anchor |
| Ral, Monsoon Mage | Just a Ruby Storm card | MDFC. Front: Legendary Creature — Human Wizard (MV 2). Back: Legendary Planeswalker — Ral (Ral, Leyline Prodigy). Ruby Storm engine |
| Cori-Steel Cutter | Like a Sword card | MV 2 `Artifact — Equipment`. Equip {1}{R}, +1/+1 + trample + haste. Flurry trigger: when you cast your 2nd spell each turn, create a 1/1 white Monk prowess token AND may attach this Equipment to it. UR Aggro / "Cori Prowess" engine |
| Sowing Mycospawn | Like Sowing Salt | MV 4 `Creature — Eldrazi Fungus`. Devoid + Kicker `{1}{C}`. Cast trigger: search library for a land, put onto battlefield. Kicker trigger: exile target opp land. **Legal in Modern**, **banned in Legacy** — different from how it'd be classified in Legacy lists |
| Karn, the Great Creator | Lock + tutor | MV 4 Legendary Planeswalker. Static: opp's artifact activated abilities can't activate. +1: noncreature artifact becomes creature with P/T = MV until your next turn. −2: reveal artifact from sideboard/exile and put into hand. The wishboard is the bulk of the deck's mainboard value |
| Ugin's Labyrinth | Tron piece | NOT a Tron piece — it's a Land that imprints a colorless MV ≥ 7 card from hand when it enters; taps for {C} (or {C}{C} if imprinted); second activated returns the imprinted card to hand. Eldrazi-Ramp / UrzaTron utility |

## Mana Value vs Paid Cost (Modern)

Mana value is the printed mana cost. Alternative casts do NOT change mana value. This trips up Modern analysis most for evoke-pitch incantations from Modern Horizons.

| Card | MV | Alt cast | Chalice@N catches |
|---|---|---|---|
| Solitude | 5 | Evoke `{1}{W}` OR pitch a white card and pay {0} | Chalice@5 (always) |
| Subtlety | 4 | Evoke `{2}{U}` OR pitch a blue card and pay {0} | Chalice@4 (always) |
| Endurance | 3 | Evoke `{1}{G}` OR pitch a green card and pay {0} | Chalice@3 (always) |
| Force of Negation | 3 | Alt-cast off-turn for {0} pitching a blue card | Chalice@3 (always) |
| Karn, the Great Creator | 4 | None — always {4} | Chalice@4 |
| Mishra's Bauble | 0 | None | Chalice@0 |
| Mox Opal | 0 | None | Chalice@0 |
| Ragavan, Nimble Pilferer | 1 | Dash `{2}{R}` | Chalice@1 catches the normal cast; dash cost is `{2}{R}` paid cost but MV remains 1 |
| Vexing Bauble | 0 | None | Chalice@0; Vexing Bauble also affects opp's MV-0 spells |
| Cori-Steel Cutter | 2 | None | Chalice@2 |

## Top Staples by Archetype (Modern, May 2026)

Per-archetype anchor card sets observed in the 10 samples at `../samples/modern/`. Verify each card via Scryfall before citing — the meta moves.

### Boros Aggro (12% — RW Energy / Cat Tribal variant)

```
4 Ragavan, Nimble Pilferer       1 R, Legendary Creature — Monkey Pirate
4 Ajani, Nacatl Pariah           MDFC, MV 2 front (Cat Warrior) → planeswalker back
4 Guide of Souls                 angel-energy ramp
4 Ocelot Pride                   cat tribal anchor
4 Galvanic Discharge             energy burn
```

### Affinity (12% — Modern artifact deck)

```
4 Mox Opal                       MV 0 (Chalice@0 catches)
4 Kappa Cannoneer                affinity-style cost reduction
4 Pinnacle Emissary              Modern Affinity engine
4 Engineered Explosives          flexible removal artifact
4 Weapons Manufacturing          affinity payoff
4 Tormod's Crypt                 graveyard hate, MV 0
4 Urza's Saga                    construct generator + MV-1 artifact tutor
```

### Blink (7% — Esper Blink)

```
4 Solitude                       MV 5 evoke-pitch white
4 Overlord of the Balemurk       Esper Blink anchor
4 Quantum Riddler                ETB value
4 Phelia, Exuberant Shepherd     MV 2 flash blink-attacker
4 Fatal Push                     black removal
4 Thoughtseize                   discard
4 Prismatic Ending               flex removal
3 Teferi, Time Raveler           static "can only cast on your turn" lock
```

### UR Aggro (4% — Cori Prowess)

```
4 Ragavan, Nimble Pilferer       Modern-banned-in-Legacy hard signal
4 Dragon's Rage Channeler        delirium creature
4 Monastery Swiftspear           1 R hasty prowess
4 Slickshot Show-Off             MV 1 prowess
4 Cori-Steel Cutter              MV 2 Equipment + Flurry token engine
4 Expressive Iteration           Modern-banned-in-Legacy hard signal
4 Lightning Bolt                 1 R 3 damage
4 Lava Dart                      free 1 damage + flashback
```

### UrzaTron (4%)

```
4 Urza's Mine + Urza's Power Plant + Urza's Tower    "Tron" — all 3 add {C}{C} / {C}{C}{C} when complete
4 Expedition Map                 tutor for any land (MV 1)
4 Karn, the Great Creator        MV 4 wishboard planeswalker
4 Thought-Knot Seer              Eldrazi MV 4 ETB-discard
4 Talisman of Resilience         2-color ramp artifact MV 2
+ Eldrazi shell (Sowing Mycospawn, Devourer of Destiny, Ulgin's Labyrinth)
```

### Ruby Storm (4% — UR ritual storm)

```
4 Ral, Monsoon Mage              MDFC, MV 2 front → planeswalker back
4 Ruby Medallion                 R cost reduction by 1
4 Desperate Ritual                MV 2, splice {2}{R} R ritual
4 Pyretic Ritual                  MV 2 R ritual
4 Manamorphose                    MV 2 cantrip ritual
4 Reckless Impulse                MV 2 impulse draw
4 Wrenn's Resolve                 MV 2 impulse draw
```

### Eldrazi Ramp (3%)

```
4 Talisman of Impulse             MV 2 UR ramp
4 Malevolent Rumble              {1}{G} mill-self for big mana fix
4 Utopia Sprawl                   1 G enchant land for ramp
+ Eldrazi shell (Eldrazi Temple, Ugin's Labyrinth, Sowing Mycospawn, Devourer of Destiny, Kozilek's Command)
```

### UW Control (3%)

```
4 Counterspell                   2 U hardcounter (Modern-legal, played mainboard here)
4 Orim's Chant                   W "opp can't cast spells this turn"
4 Consult the Star Charts        MV 1 cantrip-tutor (verify)
4 Solitude                       white evoke-pitch removal
4 Teferi, Time Raveler           3-mana planeswalker, static instant-speed restriction on opp
+ Removal + counter package
```

### Living End (3% — cascade cycling reanimator)

```
4 Curator of Mysteries           cycling sphinx
4 Generous Ent                   cycling land enabler
4 Shardless Agent                cascade enabler
4 Street Wraith                  free cycling for graveyard fuel
4 Subtlety                       MV 4 evoke-pitch blue, cascade-disruptor
4 Force of Negation              MV 3 pitch counter
4 Violent Outburst               cascade {2}{R}{R} → Living End
```

### Amulet Titan (3% — bounceland combo)

```
4 Amulet of Vigor                {1} artifact, ETB-tapped lands untap
4 Spelunking                    "lands ETB untapped"
4 Arboreal Grazer                1 G ramp creature
4 Green Sun's Zenith             X G G tutor
+ Bounce-land manabase (Simic Growth Chamber, Gruul Turf, Crumbling Vestige)
+ Primeval Titan finisher
```

## Modern Manabase Patterns

Modern's mana base differs from Legacy in several ways. None of these are subtle, but all are easy to miss when reasoning from Legacy memory.

### Fetchland + shockland engine

- **Fetchlands** (Onslaught + Zendikar cycles, both legal in Modern AND Legacy): Polluted Delta, Bloodstained Mire, Wooded Foothills, Flooded Strand, Windswept Heath, Misty Rainforest, Scalding Tarn, Marsh Flats, Verdant Catacombs, Arid Mesa. `{1}, T, Sac: search library for Plains/Island/Swamp/Mountain/Forest card`. Critically, fetchlands can grab **shocklands** (which DO have basic land types).
- **Shocklands** (Ravnica cycles): legal in BOTH Modern and Legacy. Steam Vents (Mountain Island), Sacred Foundry (Mountain Plains), Hallowed Fountain (Plains Island), Breeding Pool (Forest Island), Stomping Ground (Mountain Forest), etc. ETB tapped unless you pay 2 life. Found by fetchlands (have basic land types). Modern decks lean on shocks heavily; Legacy uses them alongside original duals.
- **Original duals** (Volcanic Island, Tundra, etc.): legal in Legacy ONLY, NOT in Modern. If you see one of these in a deck, it's a hard Legacy signal.

### Surveil lands ("Watcher" lands from MKM cycle, Modern-legal)

Verified on samples: Commercial District (UR Surveil), Elegant Parlor (UR Surveil), Meticulous Archive (UW Surveil), Thundering Falls (UR Surveil). Each ETBs tapped, gives 1 surveil 1, taps for 2-color mana. **Not in Legacy** (verify before claiming).

### Triomes (3-color ETB-tapped lands)

Indatha Triome, Ketria Triome, Raugrin Triome, Savai Triome, Zagoth Triome, etc. ETB tapped, gives all 3 colors. Can be fetched by fetchlands (because they have basic land types like "Forest Plains Island"). Legal in Modern. Less commonly played in Legacy.

### Utility lands (Modern's signature category)

- **Boseiju, Who Endures** (Kamigawa NEO): MV 0 Legendary Land, taps for G. **Channel `{1}{G}`, discard: destroy target artifact/enchantment/nonbasic land an opponent controls.** Cost reduces by {1} per legendary creature controlled. Instant-speed.
- **Otawara, Soaring City**: MV 0 Legendary Land, taps for U. Channel `{2}{U}`, discard: bounce target nonland permanent.
- **Urza's Saga**: Enchantment Land, NOT Legendary. Sage saga chapters; III sacrifices for MV-1 artifact tutor. Tutorable by Karn the Great Creator (artifact tutor — no, Karn fetches from outside the game).

### Tron pieces

Three Urza's-typed lands needed for "Tron":

```
Urza's Mine — Land — Urza's Mine. {T}: Add {C}. With Tower + Power Plant → {C}{C}.
Urza's Power Plant — Land — Urza's Power-Plant (note hyphen in typeline). With Mine + Tower → {C}{C}.
Urza's Tower — Land — Urza's Tower. With Mine + Power Plant → {C}{C}{C}.
```

Total: 7 colorless mana on turn 3 if you assemble all three. **Eldrazi Temple is NOT a Tron piece** — it's just `Land`, gives {C}{C} for colorless Eldrazi spells/abilities. Used alongside Tron pieces in Eldrazi Tron variants.

### Modal DFCs (MDFCs)

Cards with two faces — one a spell, one a land. Front face is canonical for MV. Examples in Modern: Sea Gate Stormcaller, Glasspool Mimic, Valakut Awakening, etc. Modern manabases often run 1-3 MDFCs as flexible "spell or land" slots.

## Format-Specific Interaction Pitfalls (Modern)

### Force of Negation vs Force of Will

Two different cards, different formats, different costs:

| Card | Format | Cost | Alt cast | MV |
|---|---|---|---|---|
| Force of Will | Legacy / Vintage / Commander only (NOT Modern) | `{3}{U}{U}` | Exile blue card pitching | 5 |
| Force of Negation | Modern / Legacy / Vintage / Pioneer | `{1}{U}{U}` | Exile blue card pitching ON OPP'S TURN ONLY | 3 |

Critical: Force of Negation's alt-cast is **only off-turn** (when it's not your turn). On your own turn you must pay full {1}{U}{U}. Force of Will has no off-turn restriction.

### Evoke-pitch Elementals — MV is the printed cost

This trips up Chalice math.

```
Chalice@3 catches:  Endurance, Force of Negation (always — MV is 3, regardless of pitch alt-cast)
Chalice@4 catches:  Subtlety, Karn (always — MV is 4)
Chalice@5 catches:  Solitude (always — MV is 5)
```

A common (wrong) belief: "I cast Solitude for {0} via evoke pitch, so Chalice@0 should counter it." That's wrong — MV is determined by the printed mana cost, and the cast is at MV 5 even when paid {0}.

### Triome ETB-tapped affects T1 plays

Triomes always ETB tapped. If your only way to cast a T1 spell is a Triome, the T1 cast is impossible. This matters for archetype shape:
- Domain Zoo / Domain Aggro: often runs Triomes for the 5-color count, accepting T1 tapped lands.
- UR Aggro: typically avoids Triomes — would slow T1 Ragavan / Slickshot Show-Off / DRC plays.

### Karn the Great Creator wishboards

Karn fetches from "outside the game" — in tournament Modern, that means the sideboard. UrzaTron, Eldrazi-Tron, and Boros decks running Karn use sideboard as a tutorable artifact toolbox. Sideboard count of artifacts matters more than mainboard for Karn-running decks.

### Cori-Steel Cutter Flurry trigger

Flurry: "When you cast your second spell each turn". Cast triggers on the *cast event*, not on resolution. So Cori-Steel Cutter's token creation happens before the second spell resolves. With Bowmasters in the meta, the Modern-prowess shells of 2026 deliberately avoid drawing on the second-cast turn.

### Cascade interactions (Living End, Cascade Crash)

Cascade exiles cards from the top of library until a card with lower MV is hit, then casts it. Modern restricts cascade interactions:
- Cascade triggers find the first lower-MV spell, NOT a spell you choose.
- Living End is MV 3 (`{2}{B}` — verify) and is the typical cascade target.
- Banlist watches: cards like Tibalt's Trickery and Crashing Footfalls have had B&R action historically; verify current legality before recommending cascade plans.

## Cards That Look Played But Aren't (Modern, May 2026)

Modern's meta turns over fast. Cards I expected to see in the top 10 but did NOT find in the May 2026 samples:

| Card | Why expected | What's there instead |
|---|---|---|
| Wrenn and Six | Legacy-banned, Modern-played fixture for years | Not in any of the top 10 samples; possibly displaced by newer cards or shifted to non-top-10 archetypes |
| Murktide Regent | UR Tempo finisher | UR Tempo decks now run Slickshot Show-Off + Cori-Steel Cutter shells instead |
| Yawgmoth, Thran Physician | "Yawgmoth Pod" archetype | Plan assumed this would be a top archetype; not in current top 10 |
| Hammer Time / Sigarda's Aid + Colossus Hammer | A staple from 2022-2024 | Not in current top 10 |
| Domain Zoo (Leyline Binding, Tribal Flames) | Recent strong deck | Not in current top 10 |
| Lurrus of the Dream-Den | Companion-era staple | Verify B&R status live — has bounced between banned/legal |

**Discipline note:** Don't cite these cards as "Modern staples" without re-verifying current play rate via mtgtop8. Meta knowledge from training data is stale by the time you read it.

## "Looks Modern But Isn't" (Verified Banlist State 2026-05-25)

Per Scryfall verification on the build day:

- **Brainstorm, Ponder, Daze, Force of Will** — `not_legal` in Modern (never been in Modern's card pool — they predate Modern's start point).
- **All original-dual lands** (Volcanic Island, Underground Sea, Tundra, Tropical Island, Bayou, Plateau, Savannah, Scrubland, Badlands, Taiga) — `not_legal` in Modern.

Notably **legal-in-Modern as of 2026-05-25 verification** despite past B&R drama:
- Mox Opal — `modern=legal`, played 4-of in the current Affinity sample (verify status before any analysis day).
- Lurrus of the Dream-Den — historically bounced between banned/unbanned; **always re-verify live via the banlist endpoint below** before citing.

**Live verification commands:** see the "Live Banlist Verification Sources (Modern)" section at the bottom of this file. Don't trust this paragraph beyond 2026-05-25 — Modern B&R changes every few months.

---

# Live Banlist Verification Sources (Modern) — CANONICAL

**The Iron Law:** never cite Modern legality from this file or from memory. Always fetch live.

## Primary: Scryfall API (parseable JSON)

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

## Secondary: Wizards B&R page (authoritative on announcement day)

```bash
curl -s -H "User-Agent: chinrw-mtg-skill/1.0" \
  "https://magic.wizards.com/en/banned-restricted-list" \
  | grep -A 1000 "Modern" | head -200
```

Wizards page is canonical on B&R announcement days (Scryfall may lag by a few hours). Use this for tiebreaking. The page section header is `Modern` — grep from there.

## Citation discipline

Every Modern legality claim in an analysis output must include:
- The fetch date of the banlist consulted
- Source: `Scryfall API banned:modern` OR `Wizards B&R - Modern section`
- If older than 24 hours, refetch before citing

Do NOT paste a cached banlist into this file. Reference tables document HOW to fetch, never WHAT was last fetched.
