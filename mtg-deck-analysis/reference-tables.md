# MTG Deck Analysis — Reference Tables

Living reference for card-specific interactions and pitfalls discovered through real analysis. Always verify the current Oracle text on Scryfall before relying on any entry — printings change, errata happen, ban status shifts every few months.

## Card Name Pitfalls (Names That Mislead)

| Card | Wrong assumption | Reality |
|---|---|---|
| Petrified Hamlet | Locus (4th Cloudpost) | Hate land — names a card; shuts non-mana activated abilities of that name; itself taps for C |
| Sink into Stupor | Counterspell | Bounce (returns spell/nonland permanent to hand); back face Soporific Springs is a blue land |
| Planar Nexus | Vesuva-style copy land | IS every nonbasic subtype directly (Mine + Power-Plant + Tower + Locus + Urza's + Cave + Desert + Gate + Lair + Sphere). One Planar Nexus completes Tron with one real Tower |
| Urza's Workshop | Mishra's Workshop typo | Real BRC card; Land — Urza's; Metalcraft scaling C per Urza's land |
| Urza's Workshop's metalcraft | Counts all lands | Counts only Urza's-subtype lands |
| Grim Monolith + Voltaic Key | Infinite mana | NOT infinite alone (Monolith taps for 3, Key untaps for 1 mana → +5 net per turn, then everything tapped). Real infinite needs Power Artifact or Voltaic Construct |
| Lorien Revealed Islandcycling | Triggers Bowmasters | Doesn't — channel discards card and searches; no "draw" |
| Stock Up | Cantrip | Sorcery: look top 5, put 2 in hand, rest bottom. Does NOT trigger Bowmasters (no "draw") |
| Thundertrap Trainer | Just a beater | Otter Wizard 1/2 with ETB look 4, reveal 1 non-creature non-land, put into hand. Does NOT trigger Bowmasters |
| Flow State | Brainstorm-like | Sorcery: look top 3, put 1 in hand (or 2 if both an instant AND a sorcery in graveyard). Does NOT trigger Bowmasters |
| Tishana's Tidebinder | Just a counterspell creature | 2U 3/2 Merfolk Wizard with Flash. ETB counters activated/triggered ability AND the source permanently loses all abilities while Tidebinder is on the battlefield |
| Mishra's Workshop vs Urza's Workshop | Same card / interchangeable | DIFFERENT cards. **Mishra's Workshop is BANNED in Legacy** (Antiquities; {0} Land: T add {3} for artifact spells). Urza's Workshop (BRC, legal) is a separate Urza's-typed Land. Don't conflate when computing enabler pools |
| Tamiyo, Inquisitive Student | MV 2 (recall as 1U) | MV 1 ({U}). MDFC: front face is `{U}` Legendary Creature — Moonfolk Wizard 1/2; back face Tamiyo, Seasoned Scholar is a planeswalker. Caught by Chalice@1, NOT @2 |
| Counterspell as Legacy staple | Widely played in current Legacy | Almost never played. In a May 2026 mtgtop8 sample of 12 archetypes × 3 decks each, Counterspell appeared in 0. Tempo uses Daze/FoW; control uses FoW/FoN. Always verify play rate before citing |

## Mana Value vs Paid Cost

Mana value is determined by the printed mana cost. Alternative casts do NOT change mana value.

| Card | Mana value | Why this matters |
|---|---|---|
| Force of Will | 5 (always) | Chalice@5 catches it; Chalice@0 does NOT catch the alt cast |
| Force of Negation | 3 (always) | Same logic |
| Daze | 2 (always) | Chalice@2 catches it even when cast for free |
| Lotus Petal | 0 | Chalice@0 catches |
| Mox Diamond | 0 | Chalice@0 catches |
| Surgical Extraction | 1 (Phyrexian B counts as 1) | Chalice@1 catches even when paid with life |

## Chalice of the Void Reference

Chalice enters with X charge counters. It counters spells with mana value = X.

| Chalice X | Catches | Does NOT catch |
|---|---|---|
| 0 | Lotus Petal (MV 0), Mox Diamond (MV 0), Mishra's Bauble (MV 0) | FoW alt cast (MV 5), Daze alt (MV 2) |
| 1 | Brainstorm (U), Ponder (U), Delver of Secrets (front U), Dragon's Rage Channeler (R), Nethergoyf (B), Tamiyo Inquisitive Student (U; front face of MDFC), Aether Vial ({1}), Reanimate (B), Grindstone ({1}), Surgical Extraction (B/P), Swords to Plowshares (W), Path to Exile (W), Lightning Bolt (R), Thoughtseize (B), Duress (B), Nature's Claim (G) | Daze (MV 2), Counterspell (MV 2) |
| 2 | Daze (1U), Counterspell (UU), Stoneforge Mystic (1W), Thalia Guardian (1W), Orcish Bowmasters (1B), Flow State (1U) | Force of Negation (MV 3), Show and Tell (MV 3), Stock Up (MV 3), Tamiyo Inquisitive Student (MV 1 — caught by @1), Tishana's Tidebinder (MV 3 — caught by @3) |
| 3 | Show and Tell (2U), Doomsday (BBB), Karn the Great Creator (3), Force of Negation (1UU), Stock Up (2U), Endurance (1GG), Trinisphere (3) | The One Ring (MV 4), Sneak Attack (MV 4) |
| 4 | The One Ring ({4}), Sneak Attack (3R), Mystic Forge ({4}), Force of Vigor (2GG), Leyline of the Void (2BB) | Stoneforge Mystic (MV 2), Tron pieces (lands, not spells) |

Always verify the printed mana cost on Scryfall before applying Chalice tech.

### Permanents in play are immune to lock cards

Chalice only counters spells **as they are cast**. Once a spell resolves, the resulting permanent is immune. The same is true of Trinisphere, Thalia (Guardian of Thraben), Sphere of Resistance, Damping Sphere, and any "spells cost more / can't be cast" effect — they all tax/lock **future** casts, not what's already on the board.

Common error: claiming "my T2 Chalice@1 stops their Delver" when opp's Delver resolved on T1. It doesn't. Chalice@1 only blanks future MV-1 casts (additional cantrips, additional Delvers/DRCs). The body on the board keeps attacking.

When evaluating a lock card's matchup impact, compute **two** probabilities:
1. P(you assemble the lock on T1 — before opp deploys)
2. P(you assemble it later — only future copies matter)

The second number is usually much weaker than the first. See `tooling-notes.md` for the hypergeometric template that handles this asymmetry.

## Does It Trigger Orcish Bowmasters?

Bowmasters triggers when an opponent draws a card except the first one they draw in their draw step.

| Effect | Triggers Bowmasters? |
|---|---|
| "Draw three cards" (Brainstorm, Lorien Revealed cast, Ancestral Recall) | ✓ Yes |
| "Draw a card" (Ponder after shuffle, Preordain) | ✓ Yes |
| "Put into hand" from look-at-top (Stock Up, Flow State, Thundertrap Trainer ETB) | ✗ No |
| The One Ring with 2+ burden counters | ✓ Yes (every draw after the first that turn) |
| Islandcycling / typecycling (discard to search for land) | ✗ No |
| Cycling (pay cost, discard, draw a card) | ✓ Yes |
| Tutoring (search library, put into hand) | ✗ No |
| Surveil (look at top, may put in graveyard) | ✗ No |
| Discard then draw (Faithless Looting) | ✓ Yes |

The trigger condition is literally the word "draw" in the effect. Always read the exact text.

## Anti-Wasteland Tech

Wasteland's destroy is an activated ability (T, Sac: Destroy target nonbasic land). Not a spell.

| Card | Mechanism |
|---|---|
| Any basic land | Untargetable — Wasteland targets nonbasic |
| Petrified Hamlet | Names "Wasteland" on ETB; non-mana activations turn off |
| Disruptor Flute | Names "Wasteland"; same effect plus the spell tax |
| Tishana's Tidebinder | Flash; ETB counters the activation as it goes on stack |
| Boseiju, Who Endures | Channel: destroy nonbasic ahead of time |
| Stifle | Counters the activated ability on the stack |
| Force of Will / Force of Negation | DOES NOT catch Wasteland — they counter spells, not abilities |

## Locus Lands (as of 2026)

| Card | Effect | Set |
|---|---|---|
| Cloudpost | ETB tapped. T: Add C for each Locus on battlefield | Mirrodin |
| Glimmerpost | T: Add C. ETB: gain 1 life per Locus | Scars of Mirrodin |
| Trenchpost | T: Add C. 3,T: target player mills 1 per Locus you control | MH3 Commander |
| Planar Nexus | T: Add C. 1,T: Add 1 mana of any color. Land — every nonbasic subtype including Locus | MH3 Commander |

Petrified Hamlet, Vesuva, and other "post"-like names are NOT Locus. Always check the subtype line on Scryfall.

## Urza Tron Completion

Urza's Tower: "T: Add C. If you control Urza's Mine AND Urza's Power-Plant, add CCC instead."

| Configuration | Tower's mana |
|---|---|
| Tower alone | 1 (C) |
| Tower + Mine | 1 (still missing Power-Plant) |
| Tower + Power-Plant | 1 (still missing Mine) |
| Tower + Mine + Power-Plant | 3 (CCC) |
| Tower + Planar Nexus | 3 (Nexus has both Mine and Power-Plant subtypes) |
| Tower + Urza's Workshop only | 1 (Workshop is Urza's but NOT Mine or Power-Plant subtype) |
| Tower + Urza's Saga only | 1 (Saga is Urza's but NOT Mine or Power-Plant) |
| 2 Planar Nexus | 1 + 1 = 2 (no Tower in play, so no CCC bonus) |

One Planar Nexus collapses Tron completion from "need all 3 specific pieces" to "need 1 Tower + 1 Nexus."

---

# Format Ban Lists — Live Lookup Only

**Always fetch the live Wizards page before making any ban claim. No cached list lives in this file.**

- **B&R page (all formats):** https://magic.wizards.com/en/banned-restricted-list
- **Announcement archive (timeline of changes):** https://magic.wizards.com/en/news/announcements

Why no snapshot here: banlists drift every few months. Any in-file copy is wrong shortly after it's pasted. The skill enforces fetch-before-claim — there is intentionally no inline fallback to undermine that discipline.

When a deck analysis touches legality:
1. WebFetch the B&R URL above
2. Confirm the card's status for the relevant format (Legacy, Modern, Pioneer, Pauper, etc. each have their own list on the same page)
3. If the status changed recently, fetch the linked announcement for the rationale
4. Cite both the URL and the fetch date in the answer

If you can't reach the URL, say so explicitly and refuse to claim ban status — do NOT fall back to memory.

---

# Common Legacy Tech — Format Staples

These cards appear across many archetypes. Mana value is from printed cost (alt casts do not change MV).

## Free / cheap counters

| Card | Cost / MV | Effect |
|---|---|---|
| Force of Will | 3UU / MV 5 | Alt: exile blue card + pay 1 life. Counter target spell |
| Force of Negation | 1UU / MV 3 | Alt off-turn only: exile blue card. Counter target noncreature spell; exile it |
| Daze | 1U / MV 2 | Alt: return an Island. Counter target spell unless controller pays {1} |
| Spell Pierce | U / MV 1 | Counter target noncreature spell unless controller pays {2} |
| Mindbreak Trap | 2UU / MV 4 | Alt: free if an opp cast 3+ spells this turn. Exile any number of target spells |
| Stifle | U / MV 1 | Counter target activated or triggered ability (mana abilities can't be targeted) |

## Card selection / draw

| Card | Cost / MV | Effect | Bowmasters trigger? |
|---|---|---|---|
| Brainstorm | U / MV 1 | Draw 3, put 2 back on top | ✓ Yes |
| Ponder | U / MV 1 | Look top 3, rearrange or shuffle, then draw 1 | ✓ Yes |
| Stock Up | 2U / MV 3 | Look 5, put 2 in hand, rest bottom | ✗ No |
| Flow State | 1U / MV 2 | Look 3, put 1 in hand (or 2 with instant + sorcery in graveyard) | ✗ No |
| Thundertrap Trainer | 1U / MV 2 | Creature; ETB look 4, reveal 1 non-creature non-land, put into hand | ✗ No |
| Lorien Revealed | 3UU / MV 5 | Draw 3 OR Islandcycling {1} (discard to fetch Island; channel does NOT draw) | ✓ on cast / ✗ on channel |
| The One Ring | {4} / MV 4 | Indestructible. ETB if cast: protection from everything until next turn. T: +1 burden counter, draw N | ✓ at 2+ counters |

## Removal

| Card | Cost / MV | Effect |
|---|---|---|
| Swords to Plowshares | W / MV 1 | Exile target creature; controller gains life equal to its power |
| Path to Exile | W / MV 1 | Exile target creature; that player may search for a basic land |
| Lightning Bolt | R / MV 1 | 3 damage to any target |
| Prismatic Ending | X{W} / MV variable | Exile target nonland permanent with MV ≤ X |
| Kozilek's Command | XCC / MV X+2 | Modal four-mode Eldrazi instant (Spawn tokens / scry+draw / exile creature / exile graveyard) |

## Common threats across archetypes

| Card | Cost / MV | Role |
|---|---|---|
| Murktide Regent | 5UU / MV 7 (delve) | UR Tempo finisher; ETB +1/+1 per instant/sorcery exiled. Typical cast for 2-3 real mana |
| Delver of Secrets | U / MV 1 | 1/1 → 3/2 Flying when revealing top instant/sorcery |
| Dragon's Rage Channeler | R / MV 1 | 1/1; cast non-creature surveils; Delirium: +2/+2 flying must attack |
| Nethergoyf | B / MV 1 | */1+* by card types in graveyard; Escape {2}{B} with 4 card types exiled |
| Orcish Bowmasters | 1B / MV 2 | Flash. Pings on ETB + on opp's draws after first; amasses Orcs |
| Tamiyo, Inquisitive Student | 1U / MV 2 | MDFC creature → PW Tamiyo Seasoned Scholar after 3rd draw of turn |
| Tishana's Tidebinder | 2U / MV 3 | 3/2 Flash Wizard; ETB counters ability AND permanently disables source |

---

# Common Legacy Tech — Manabase Staples

## Fetch lands (Onslaught + Khans cycles)

All: pay 1 life, sac to find a land card with matching basic type, ETB untapped.

| Card | Fetches (basic types) |
|---|---|
| Polluted Delta | Island, Swamp |
| Flooded Strand | Plains, Island |
| Wooded Foothills | Mountain, Forest |
| Bloodstained Mire | Swamp, Mountain |
| Windswept Heath | Plains, Forest |
| Misty Rainforest | Island, Forest |
| Scalding Tarn | Island, Mountain |
| Verdant Catacombs | Swamp, Forest |
| Marsh Flats | Plains, Swamp |
| Arid Mesa | Plains, Mountain |

## Original dual lands (Revised + Eternal Masters / 30A reprints)

Each is "Land — [Type1] [Type2]" with no ETB drawback. Fetchable by basic-type fetches.

| Card | Basic types |
|---|---|
| Underground Sea | Island, Swamp |
| Volcanic Island | Island, Mountain |
| Tropical Island | Forest, Island |
| Tundra | Plains, Island |
| Bayou | Swamp, Forest |
| Badlands | Swamp, Mountain |
| Taiga | Mountain, Forest |
| Scrubland | Plains, Swamp |
| Plateau | Plains, Mountain |
| Savannah | Plains, Forest |

## Utility lands

| Card | Effect |
|---|---|
| Wasteland | T: Add C. T, Sac: Destroy target nonbasic land |
| Rishadan Port | T: Add C. {1}, T: Tap target land |
| Karakas | Legendary Land. T: Add W. T: Return target legendary creature to owner's hand |
| Cavern of Souls | On ETB, name a creature type. T: Add C. T: Add 1 of any color, spent only on a creature spell of the chosen type — that spell can't be countered |
| The Tabernacle at Pendrell Vale | Legendary Land. T: Add C. Creatures have "At your upkeep, sac unless controller pays {1}" |
| Boseiju, Who Endures | Legendary Land — Mountain. T: Add G. Channel {1}{G}, discard: Destroy target nonbasic land OR artifact OR enchantment opp controls; opp may find a basic |
| Mishra's Factory | T: Add C. {1}: Becomes 2/2 Assembly-Worker artifact creature until end of turn. {1}, T: Other Assembly-Workers get +1/+1 until end of turn |
| Ancient Tomb | T: Add CC. Deals 2 damage to you |
| City of Traitors | T: Add CC. When you play another land, sacrifice this |
| Dark Depths | Legendary Land. Comes with 10 ice counters. T, remove an ice counter: Add C. When it has none, sac and put a 20/20 flying indestructible Marit Lage token onto the battlefield |
| Thespian's Stage | T: Add C. {2}, T: Becomes a copy of target land (loses ability) — combos with Dark Depths to skip ice counters |

---

# Common Legacy Tech — Sideboard Staples

## Anti-blue / counter-mirror

| Card | Cost / MV | Use case |
|---|---|---|
| Red Elemental Blast (REB) | R / MV 1 | "Counter target blue spell OR destroy target blue permanent." Cheap, focused |
| Pyroblast | R / MV 1 | "Choose one — target spell becomes blue then counter it if it's blue / target permanent becomes blue then destroy it if blue." Can target non-blue for storm/prowess count |
| Hydroblast | U / MV 1 | Mirror against red |
| Flusterstorm | U / MV 1 | Counter target instant or sorcery; one copy per storm count |

## Graveyard hate

| Card | Cost / MV | Effect |
|---|---|---|
| Surgical Extraction | {B/P} / MV 1 | Choose graveyard card (not basic land); exile all copies from gy + hand + library |
| Endurance | 1GG / MV 3 | 3/4 Flash Reach. ETB: target player puts entire graveyard on bottom of library in random order. Evoke: exile a green card from hand to cast for free |
| Tormod's Crypt | 0 / MV 0 | T, Sac: Exile all cards from a graveyard |
| Leyline of the Void | 2BB / MV 4 | If in opening hand, may put onto battlefield untapped. Opp's cards go to exile instead of graveyard |
| Faerie Macabre | 2B / MV 3 | 2/1 Flying. Discard from hand: exile up to 2 graveyard cards |
| Soul-Guide Lantern | 1 / MV 1 | T: Exile target gy card, then draw if no cards left in opp gy. {2}, T, sac: Exile each graveyard |

## Artifact / enchantment removal

| Card | Cost / MV | Effect |
|---|---|---|
| Force of Vigor | 2GG / MV 4 | Alt off-turn: exile a green card. Destroy up to 2 target artifacts and/or enchantments |
| Nature's Claim | G / MV 1 | Destroy target artifact or enchantment; controller gains 4 life |
| Collector Ouphe | 1G / MV 2 | Activated abilities of artifacts can't be activated (mana abilities still work) |
| Null Rod | 2 / MV 2 | Same effect as Collector Ouphe in artifact form |
| Boseiju, Who Endures | Channel {1}{G}, discard | Also destroys artifacts / enchantments — listed in Manabase but doubles as SB tech |

## Discard / disruption

| Card | Cost / MV | Effect |
|---|---|---|
| Thoughtseize | B / MV 1 | Look at opp's hand. Choose a noncreature non-land card, exile. Lose 2 life |
| Duress | B / MV 1 | Look at opp's hand. Choose a noncreature non-land card, discard |
| Inquisition of Kozilek | B / MV 1 | Look at opp's hand. Choose a card with MV ≤ 3, discard |
| Veil of Summer | G / MV 1 | Until eot, draw on first blue/black spell opp casts; spells you cast can't be countered; you and your permanents have hexproof from blue and black |

---

# Common Legacy Tech — Combo and Lock Pieces

## Lock pieces

| Card | Cost / MV | Effect |
|---|---|---|
| Trinisphere | 3 / MV 3 | While untapped, each spell that would cost less than 3 mana costs 3 instead. Crushes Daze/FoW alt cost / Brainstorm |
| Chalice of the Void | XX / MV X×2 | Enters with X charge counters. Counter spells with MV = X |
| Sphere of Resistance | 2 / MV 2 | Spells cost {1} more to cast |
| Damping Sphere | 2 / MV 2 | Each spell beyond the first each turn costs {1} more; Tron-style "scaling" lands tap only for C |
| Thalia, Guardian of Thraben | 1W / MV 2 | Creature 2/1 first strike; noncreature spells cost {1} more |
| Blood Moon | 2R / MV 3 | All nonbasic lands are Mountains |
| Magus of the Moon | 2R / MV 3 | Creature version of Blood Moon |
| Back to Basics | 1UU / MV 3 | Nonbasic lands don't untap during their controllers' untap step |
| Ensnaring Bridge | 3 / MV 3 | Creatures with power greater than the number of cards in your hand can't attack |
| Null Rod | 2 / MV 2 | Activated abilities of artifacts can't be activated (mana abilities exempt) |
| Karn, the Great Creator | 3 / MV 3 | PW: opp's artifact activated abilities can't be activated; −2 fetches an artifact from outside the game |

## Combo enablers

| Card | Cost / MV | Combo role |
|---|---|---|
| Show and Tell | 2U / MV 3 | Each player puts an artifact/creature/enchantment/land from hand into play; pair with Emrakul / Omniscience |
| Sneak Attack | 3R / MV 4 | R: Put creature from hand into play with haste; sac at next end step |
| Reanimate | B / MV 1 | Put target creature card from any graveyard onto battlefield under your control; lose life = its MV |
| Exhume | 1B / MV 2 | Each player puts a creature card from their graveyard onto the battlefield |
| Animate Dead | 1B / MV 2 | Aura: enchant target creature card in a graveyard; return to battlefield with ETB triggers |
| Doomsday | BBB / MV 3 | Search lib + gy for 5 cards exile rest, lose half life. Stacks library for combo finish (often Thassa's Oracle) |
| Painter's Servant | 2 / MV 2 | Artifact creature 1/3; on ETB choose a color; all cards everywhere are that color in addition to other colors |
| Grindstone | 1 / MV 1 | {3}, T: Target player mills 2; if shared color, repeat. With Painter's Servant + Grindstone = mill entire library |
| Lotus Petal | 0 / MV 0 | T, sac: Add 1 mana of any color. Universal combo accelerant |
| Goblin Charbelcher | 4 / MV 4 | {3}, T: Reveal cards from top until non-land; deal damage equal to nonland count to any target |
| Mystic Forge | 4 / MV 4 | Look at top of library; may cast artifact / colorless spells from the top |
| Helm of Awakening | 1U / MV 2 | Spells cost {1} less to cast (storm enabler historically) |
| Thassa's Oracle | UU / MV 2 | Creature 1/3; ETB: look at top X; if your library has X or fewer cards, you win |

---

# Cards That Look Meta but Aren't (Verify Before Citing)

Cards that training data and casual reputation suggest are Legacy staples, but **decklist-verification in May 2026** shows are essentially absent. Always re-check play rates before treating any of these as live meta targets for interactions like "Chalice catches X" or "lock card stops X."

| Card | Reputation | May 2026 mtgtop8 sample (3 decks × 12 archetypes) | Notes |
|---|---|---|---|
| Counterspell ({U}{U}) | "Classic Legacy staple" | 0 / 36 sampled decks | Tempo runs Daze + FoW; control runs FoN + FoW. Counterspell is too slow / too restrictive |
| Lorien Revealed | "Universal blue draw" | 0 / 36 | Pushed out by Flow State (Bowmasters-safe, MV 2) and Stock Up |
| Show and Tell | "Combo enabler" | Tracked separately in dedicated archetype; not a splash card | Don't cite as a generic interaction target |
| Snapcaster Mage | "Blue tempo staple" | Single splash in UWx Control; not in any tempo deck | Largely replaced by Murktide / Cori-Steel Cutter |
| Mishra's Workshop | "Stax enabler" | BANNED in Legacy — fetched live, line "Mishra's Workshop" under Legacy Banned Cards | Use Urza's-typed lands (Urza's Saga / Workshop BRC) instead |

**Always run Step 4b** (decklist parser in `tooling-notes.md`) before listing what a lock card catches. Citing an obsolete card to justify a meta read invalidates the analysis.

# Common Mistakes Reference

| Mistake | Why bad | Fix |
|---|---|---|
| "I think card X does Y" | Recall is unreliable; cards get errata | Search Scryfall |
| "Probably the Meta is ~X%" | Meta shifts after bans/sets | Check mtgtop8 NOW |
| "Card X was banned" (or wasn't) | Ban list changes monthly | Verify against current B&R |
| "Daze is MV 0 because alt cost" | MV is from printed cost | Daze is MV 2 always |
| "Card X is a Locus" (from name) | Subtype ≠ name | Check Oracle subtype line |
| "Cloudpost is Modern-legal" | Banned in Modern since 2015 | Verify ban list per format |
| "Monolith + Key = infinite mana" | Not infinite alone | Need Power Artifact for true infinite |
| "FoW will counter Wasteland" | Wasteland's ability isn't a spell | Use Stifle/Tidebinder/Hamlet for abilities |
| Skipping graveyard-cast probability | Drawing ≠ casting ≠ resolved into graveyard | Compute joint probability |
| Mixing inference with sourced facts | Loses analyst credibility | Label each claim |
| Assuming a card from a recent set is good | New ≠ good in this specific deck | Apply the five-lens framework |
