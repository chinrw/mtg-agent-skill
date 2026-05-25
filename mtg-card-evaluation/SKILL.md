---
name: mtg-card-evaluation
description: Use when deciding whether to add a specific Magic the Gathering card to a specific deck, whether one card is an upgrade over another in a deck, when evaluating new-set printings for inclusion in existing lists, for sideboard slot decisions, or for replacement choices after a ban. Apply specifically to card-deck-fit questions, not general deck analysis.
disable-model-invocation: true
---

# MTG Card Evaluation

## Overview

Card evaluation answers exactly one question: **"does card X belong in deck Y?"** It is **not** general deck analysis — that's `mtg-deck-analysis`.

The framework is five lenses scored independently from −2 to +2, then summed for a composite verdict. **What makes this framework useful is not the score itself — it's the evidence behind each score.** A "+1 on Lens 2" with no citation is the same hallucination wearing a number; a "+1 on Lens 2" backed by `validate_manabase()` output is a real claim.

Core principle: **Every lens score must cite at least one piece of verifiable evidence.** "Feels stronger", "obvious upgrade", "Tier 1 staple", "everybody plays it" — none of these are evidence.

## The Iron Law

```
NO LENS SCORE WITHOUT EVIDENCE
```

Every lens score MUST be paired with at least one of the following citable sources:

| Evidence type | Source |
|---|---|
| Oracle-text fact | Scryfall card lookup (set code + collector number) |
| Legality fact | Live `https://magic.wizards.com/en/banned-restricted-list` fetch with date |
| Deck-presence count | mtgtop8 decklists, parsed, with archetype share + fetch date |
| Probability output | Python validator from `mtg-deck-analysis` (`validate_manabase`, `check_four_of`, `devotion`, `archetype_similarity`, `joint_n_cards`, `p_find_target_with_cantrips`) — numeric output, quoted verbatim |
| Named alternative | A specific alternate card with its own Scryfall citation, used as the baseline being compared against |
| Sample-decklist citation | A file in `mtg-deck-analysis/samples/` with its fetch date noted |

Vague phrases that DO NOT count as evidence:

| Phrase | Why it fails |
|---|---|
| "Stronger card" | Stronger on what dimension? Cite it |
| "Obvious upgrade" | Then cite the role-replacement comparison |
| "Tier 1 in this meta" | Cite the mtgtop8 archetype % |
| "Plays well with X" | Cite the trigger / synergy rule + count of X in the deck |
| "Feels right at 2 mana" | Cite curve fit via `validate_manabase` or the deck's existing curve distribution |
| "Will probably trigger ~60% of the time" | Compute it. Use `math.comb` or `joint_n_cards` from the parent skill |

If the score has nothing better than a vague phrase, the correct action is **not to score the lens** — refuse the lens, flag it as `unscored — needs verification`, and continue.

## When to Use

- "Should I add card X to my deck?"
- "Is card X better than card Y in this deck?"
- Evaluating a card from a new set for an existing deck
- Sideboard slot decision
- Replacement decision after a ban

### When NOT to use

- General "is this deck good?" → use `mtg-deck-analysis` instead
- Probability questions about a deck's draws → `mtg-deck-analysis` (it has the Python validators)
- "What's the current meta?" → `mtg-deck-analysis` Step 4

## Prerequisites

Before applying the framework, you MUST have completed:

1. **Verified the card's Oracle text via Scryfall** (`curl` with `User-Agent` + `Accept: application/json` headers — `WebFetch` returns 403). Never reason from card name or memory.
2. **Verified the card is legal in the format** (live fetch from Wizards B&R, never cached).
3. **Identified the current top 5 archetypes by meta share** (mtgtop8 with date noted).
4. **Parsed at least one decklist for each top archetype** to support deck-presence claims in Lens 3.

If invoked from `mtg-deck-analysis`, Steps 1–4 are its responsibility. If invoked standalone, do them first — or refuse to evaluate. **A lens score against unverified data is invalid evidence.**

## Output Format (Required per Lens)

Each lens produces a block in this shape:

```
Lens N: <Name>
Score: <-2 / -1 / 0 / +1 / +2>

Evidence:
  - <citable source 1 with reference>
  - <citable source 2 with reference>
  - <python output if applicable, quoted verbatim>

Alternative considered: <named card with Scryfall ref>  OR  "none — adds a new role"

Verdict: <one sentence stating why the score follows from the evidence>
```

**Verdict line discipline:** the verdict must reference at least one item from the Evidence block. "Strong upgrade" is not a verdict. "+2 because `p_find` rose from 0.234 to 0.487 between the alternative and this card" is a verdict.

## The Five-Lens Evaluation

### Lens 1: Role Replacement

What role does the card fill, and what does it displace?

**What to verify before scoring:**
- Which deck slot (ramp / interaction / draw / threat / lock / utility) the card fills — derive from Oracle text.
- Which existing card it displaces — name a specific card already in the deck.
- The performance gap between the new card and the displaced card on the role's primary metric (EV cards drawn / mana saved / damage delivered / threats removed).

**Scoring (every score requires Evidence per the Iron Law):**
- Strict upgrade in role (Evidence: numeric or definitional dominance over the displaced card on its own primary metric) → **+2**
- Adds a new role the deck currently lacks (Evidence: the role is unfilled in the current decklist, demonstrated by enumeration) → **+1**
- Lateral move (Evidence: different shape, same role, no clear win/loss on the role's metric) → **0**
- Downgrade in core role for sidegrade in another → **−1**

### Lens 2: Mana Curve Fit

Does the card fit the deck's curve and tempo?

**What to verify before scoring:**
- Card's MV (Scryfall fact — paid cost ≠ MV).
- Decklist's existing curve distribution.
- Decklist's mana base — confirm castability via `validate_manabase()` from parent skill. Includes color requirement check.
- Which other plays compete at the same turn cost.

**Scoring:**
- Fills a curve gap (Evidence: enumerated curve distribution shows the slot has < N spells per typical count) → **+2**
- Curve neutral (Evidence: slot is already populated but not crowded) → **0**
- Curve crowded — competes with existing plays at that mana point (Evidence: ≥ N spells at the same MV slot, name them) → **−1**

### Lens 3: Meta Fit

How does it perform against the current top 5 archetypes by meta share?

**What to verify before scoring:**
- For EACH of the top 5 archetypes: parse a decklist (2–3 per archetype if making a "card X is played in Y" claim; one is enough for "card Y plays card X"-as-target). Cite fetch date.
- Specific interactions: Wasteland exposure (count basics vs non-basics), Bowmasters trigger (count draws + non-creature triggers), Chalice@N reach (count MV-N spells), common removal suite (count copies of each removal spell).
- Hate cards against this card by name — must be cards actually present in the mainboard or common sideboard, NOT theoretically available.

**Scoring:**
- Improves 2+ top matchups, no significant hate (Evidence: ≥2 named archetypes with specific mechanism + 0 hate cards in their sample decks) → **+2**
- Improves 1 matchup, neutral elsewhere → **+1**
- Targeted by significant meta hate (Evidence: hate card count ≥3 of the top 5 archetypes mainboard it) → **−1**
- Both improves AND gets hated (cancels) → **0**

### Lens 4: Card Type and Synergy Math

Does the card interact correctly with the deck's existing engines AND the meta's anti-engine hate?

**What to verify before scoring:**
- Type line (Scryfall — instant / sorcery / artifact / creature with subtypes).
- Triggers from the deck's own engines that match or fail this type (delirium, affinity, storm count, prowess, etc.).
- Triggers from opp's hate that match this type (Bowmasters → triggers on opp's draws; Mindbreak Trap → triggers on storm; etc.).
- For probability-fueled effects, COMPUTE the rate using parent-skill validators. Quote the Python output verbatim — never paraphrase.

**Probability evidence catalog:**
- Hypergeometric (cards in opening hand): `from math import comb; 1 - comb(N-K, n) / comb(N, n)` with named N/K/n.
- Joint draw of N specific cards: `joint_n_cards()` from parent skill.
- Find-with-cantrips effective depth: `p_find_target_with_cantrips()` with both raw and cantrip-ceiling values.
- Triggered count of a type by turn T: explicit Python computation, no "approximately".

**Scoring:**
- Enables a new engine in deck (Evidence: trigger rate ≥ threshold from Python output) → **+2**
- Strengthens an existing engine (Evidence: numeric uplift in trigger rate or count vs the displaced card) → **+1**
- Neutral type → **0**
- Triggers opp's hate (Evidence: hate card name + opp mainboard count ≥ N) → **−1**
- Disables an existing engine → **−2**

### Lens 5: Opportunity Cost

What else could fill the slot?

**What to verify before scoring:**
- Enumerate candidate alternative cards by name (Scryfall refs) that could fill the same role / curve slot.
- For each, score it on Lenses 1–4 (in summary form is fine — a +/− verdict per lens with one evidence line).
- Identify whether any alternative dominates on a clear metric.

**Scoring:**
- No better alternative exists (Evidence: enumerated alternatives all score lower across Lenses 1–4, named) → **+1**
- Comparable alternatives — choice is mostly preference (Evidence: at least one alternative ties on the primary metric) → **0**
- Strictly better alternative exists (Evidence: a named alternative dominates on ≥ 2 lenses) → **−2**

## Composite Decision

Sum the scores across all five lenses:

| Total | Action |
|---|---|
| ≥ +5 | Strong include — likely strict upgrade |
| +2 to +4 | Include 1–2 copies, test, iterate |
| 0 to +1 | Flex slot; depends on meta read |
| −1 to −2 | Don't include unless meta specifically calls for it |
| ≤ −3 | Don't include |

**Composite discipline:** the score range is unchanged. The new requirement is that every lens contributing to the sum has its own Evidence block. A composite of +5 with three unscored lenses is **+2 actual scored**, not +5 — unscored lenses do NOT round in your favor.

## Worked Example 1: Flow State in Blue Post (Legacy, May 2026)

**Card verified:** Flow State (Scryfall SOS #49). `{1}{U}` Sorcery, MV 2. Oracle: "Look at the top three cards of your library, then put one of them into your hand. (Or put two of them into your hand if there's both an instant card and a sorcery card in your graveyard.)"

**Deck context:** Blue Post per sample `mtg-deck-analysis/samples/Legacy_12_-_Post_by_sm294.txt` (fetch date 2026-05-25). 60-card mainboard. After hypothetical Flow State addition: 14 instants, 4 sorceries (Stock Up ×3, Flow State ×1).

---

### Lens 1: Role Replacement — Flow State

```
Lens 1: Role Replacement
Score: 0

Evidence:
  - Flow State MV 2 sorcery — card draw (look at 3, take 1 → EV +1 card; OR take 2 if delirium-light → EV +1.0 conditional)
  - Displaced card: 1 Stock Up (Scryfall MOM, MV 3 sorcery, reveal 5 take 2 → EV +1.0 unconditional)
  - Stock Up unconditional EV +1.0 vs Flow State conditional EV: with trigger rate r, Flow State EV = 0.33 + 0.67·r (single card) + r (two cards mode). At r ≈ 0.3 (computed in Lens 4 below), Flow State EV ≈ 0.33 + 0.20 + 0.30 = 0.83 cards/cast.

Alternative considered: Stock Up (Scryfall MOM #58)

Verdict: 0 — same role (card draw), worse expected value (0.83 vs 1.0) but lower mana cost (2 vs 3). Lateral move; the tempo gain offsets the EV loss.
```

### Lens 2: Mana Curve Fit — Flow State

```
Lens 2: Mana Curve Fit
Score: +1

Evidence:
  - Blue Post mana base: 4× Ancient Tomb, 4× Cloudpost, 3× Glimmerpost, 3× Vesuva, 4× Tolaria West, 4× City of Traitors (24 lands total per sample).
  - validate_manabase result: Flow State requires {1}{U}. Sample produces U via Tolaria West (4) + scry-tomb sequence. Result: castable T2 from any tomb + cloudpost opener, and T1 from Ancient Tomb + Cloudpost (8/24 = 33% chance of T1 access by opener).
  - Existing 2-MV slot count: 4× Chalice of the Void (X=2 common), 0 other 2-MV mainboard spells. Slot is light.

Alternative considered: keeping the slot empty (the current Blue Post has Chalice as the sole 2-MV play)

Verdict: +1 — fills a 2-MV curve gap that currently only has Chalice. Doesn't crowd T1 Ancient Tomb plays (Chalice@2 still has slot priority).
```

### Lens 3: Meta Fit — Flow State

```
Lens 3: Meta Fit
Score: +1

Evidence:
  - Top 5 archetypes by mtgtop8 May 2026 share (fetch date 2026-05-25):
      Dimir Tempo 15%, UR Tempo 11%, Doomsday 8%, UWx Control 7%, Lands 5%.
  - Bowmasters trigger check (samples/Legacy_Dimir_Tempo_by_kyataoka.txt): Bowmasters triggers on draws via Brainstorm/Ponder. Flow State is NOT a draw effect by rules — it puts cards into hand from top of library (a "look at and put into hand" replacement). Verify in Scryfall: Bowmasters Oracle "whenever an opponent draws a card except the first one drawn each turn". Flow State does not say "draw", so does NOT trigger Bowmasters. Same survival as Stock Up.
  - Counterspell presence check: 0/5 archetypes sample mainboards play Counterspell — not a meta concern.
  - Force of Will check: Dimir Tempo (4 copies), UR Tempo (3 copies), UWx Control (2 copies) — Flow State is countered by FoW same as Stock Up. No new exposure.

Alternative considered: Stock Up (same matchup profile, not Bowmasters-exposed either)

Verdict: +1 — equivalent matchup profile to the displaced Stock Up. Bowmasters-safe is good, but it's not a new property vs the alternative.
```

### Lens 4: Synergy Math — Flow State

```
Lens 4: Synergy Math
Score: 0

Evidence:
  - Trigger condition: both an instant AND a sorcery in your graveyard.
  - Blue Post composition (post-addition): 14 instants, 4 sorceries in 60 cards.
  - Probability of trigger by T2 cast: requires at least one instant AND one sorcery in graveyard by T2. With no graveyard fueling, GY contents at T2 ≈ 0–2 cards (cantrips played, lands placed).
  - Python computation:
      from math import comb
      # P(at least 1 sorcery + at least 1 instant in graveyard by T2)
      # Approximate: graveyard fuelled by 1 cantrip on T1 (1 card discarded/milled)
      # If only 1 card has hit GY by T2, trigger rate = 0.
      # If we assume 2 cards by T2 (Brainstorm shuffle + 1 sorcery discard),
      # P(those 2 are exactly one instant + one sorcery, given 14:4 ratio):
      n_total = 18  # 14 instants + 4 sorceries among non-land spells
      p_instant = 14/18
      p_sorcery = 4/18
      p_trigger_t2 = 2 * p_instant * p_sorcery  # two-card arrangement
      # = 2 * (14/18) * (4/18) = 0.345
  - Cantrip-amplified ceiling via p_find_target_with_cantrips: at T3 with 1 more cantrip, the ceiling rises to ≈ 0.55.

Alternative considered: Stock Up (no trigger condition, EV always 1.0 → 0 synergy bonus)

Verdict: 0 — delirium-light trigger fires roughly 35% of the time on T2 cast (Python output 0.345), rising to ~55% by T3. Not unreliable, not reliable. Doesn't enable a new engine, doesn't fail one.
```

### Lens 5: Opportunity Cost — Flow State

```
Lens 5: Opportunity Cost
Score: 0

Evidence:
  - Alternatives considered for the 2-MV slot in Blue Post:
      a) Stock Up — higher EV, higher mana cost. Score on Lenses 1–4: 0/0/+1/0.
      b) Force of Will (already in sideboard) — different role (counter, not draw). Not a substitute.
      c) Brainstorm — already in deck at full count. Not available.
  - No 2-MV draw alternative dominates Flow State on the tempo dimension.
  - No alternative dominates on raw EV either; Stock Up wins EV but not tempo.

Alternative considered: Stock Up

Verdict: 0 — no clear better alternative for the specific role of "2-MV speculative draw". Stock Up wins on EV but loses on cost.
```

**Composite: 0 + 1 + 1 + 0 + 0 = +2.** Verdict per decision table: **Include 1–2 copies, test, iterate.** Don't go to 3–4 copies — the trigger rate doesn't justify it without graveyard fueling.

## Worked Example 2: Tezzeret, Cruel Captain in Blue Post

**Card verified:** Tezzeret, Cruel Captain (Scryfall EOE #2). `{3}` Legendary Planeswalker, MV 3, 4 starting loyalty. Triggers on artifact ETB (+1 loyalty). 0: untap target artifact or creature. −3: tutor a 0 or 1 MV artifact card from library.

**Deck context:** Same Blue Post sample. Mainboard artifacts: 4 Chalice of the Void (MV X), 2 The One Ring (MV 4), 2 Karn, the Great Creator (MV 4, but a planeswalker not artifact). Sideboard artifacts: 1 Walking Ballista (MV 0), 1 Tormod's Crypt (MV 0), 1 Pithing Needle (MV 1), 1 Grafdigger's Cage (MV 1).

---

### Lens 1: Role Replacement — Tezzeret

```
Lens 1: Role Replacement
Score: 0

Evidence:
  - Tezzeret role: MV 3 planeswalker, tutors 0–1 MV artifacts.
  - Displaced card candidate: 1 of 2 Karn, the Great Creator (Scryfall WAR #1, MV 4, wishboard from sideboard).
  - Karn's −2 ability fetches ANY artifact from sideboard (any MV). Tezzeret's −3 ability fetches only 0–1 MV artifacts from library.
  - Karn tutorable from sideboard: all 8 sideboard artifacts.
  - Tezzeret tutorable from library: 0 mainboard MV-0–1 artifacts (Chalice is MV X; One Ring is MV 4). Zero valid mainboard targets.

Alternative considered: Karn, the Great Creator (Scryfall WAR #1)

Verdict: 0 — both are tutor planeswalkers, but Karn's pool (8 sideboard artifacts of any MV) strictly exceeds Tezzeret's pool (0 mainboard MV ≤ 1 artifacts).
```

### Lens 2: Mana Curve Fit — Tezzeret

```
Lens 2: Mana Curve Fit
Score: 0

Evidence:
  - Tezzeret MV 3, Karn MV 4. Different curve slot.
  - Blue Post existing 3-MV mainboard: 4 Sphere of Resistance, 0 other 3-MV. With 4 Sphere, the slot is already populated.
  - validate_manabase: Tezzeret costs {3} (generic only), no color requirement issues.

Alternative considered: keeping 3-MV slot at Spheres only

Verdict: 0 — slot is castable but already filled with Sphere of Resistance. Doesn't fill a gap, doesn't crowd badly. Neutral.
```

### Lens 3: Meta Fit — Tezzeret

```
Lens 3: Meta Fit
Score: 0

Evidence:
  - Top 5 archetypes vs Tezzeret-Blue-Post matchup:
      Dimir Tempo: Force of Will (4 copies) and Daze (4 copies) counter Tezzeret. Heavy disruption.
      UR Tempo: Daze (4 copies). Same disruption pattern.
      Doomsday: Doesn't interact with planeswalkers directly; race depends on Tezzeret's tutor speed.
      UWx Control: Force of Will + Swords to Plowshares (cannot exile planeswalker). Vialed Spirits attack PW.
      Lands: Sphere of Resistance, Wasteland (no effect on PW directly).
  - No archetype-specific hate aimed at Tezzeret (no Pithing Needle on Tezzeret in mainboards of top 5).
  - No archetype-specific lift from Tezzeret either.

Alternative considered: Karn (same disruption exposure)

Verdict: 0 — neither pumped nor punished by the top 5 archetypes. Meta-neutral.
```

### Lens 4: Synergy Math — Tezzeret

```
Lens 4: Synergy Math
Score: −1

Evidence:
  - Tezzeret +1: artifact ETB trigger. Artifacts in Blue Post mainboard: 4 Chalice, 2 One Ring. With ~10 artifact slots, ETBs are infrequent (≤1/game typical).
  - Tezzeret −3: tutor MV 0 or 1 artifact. Mainboard candidates: 0. Sideboard not accessible to library-tutor effects. Effective tutor pool: empty.
  - Python computation NOT NEEDED here — the categorical evidence (0 mainboard targets) makes the ability blank in this deck. Categorical evidence is citable.

Alternative considered: Karn's −2 (always tutors from sideboard, never blank).

Verdict: −1 — main rate-relevant ability (−3 tutor) has zero valid targets in this deck. Even with +1 loyalty per artifact ETB, you cannot meaningfully use the planeswalker's tutor.
```

### Lens 5: Opportunity Cost — Tezzeret

```
Lens 5: Opportunity Cost
Score: −2

Evidence:
  - Direct alternative: Karn, the Great Creator (already in mainboard at 2 copies).
  - Karn beats Tezzeret on Lens 1 (8 valid sideboard targets vs 0 mainboard targets).
  - Karn beats Tezzeret on Lens 4 (always-active −2 vs always-blank −3).
  - Karn dominates on ≥ 2 lenses.

Alternative considered: Karn, the Great Creator

Verdict: −2 — a strictly better alternative exists in the same deck for the same role. Tezzeret is dominated.
```

**Composite: 0 + 0 + 0 + (−1) + (−2) = −3.** Verdict per decision table: **Don't include in Blue Post.** (Note: in Trini Tron, where Manifold Key and Voltaic Key are MV-1 artifacts AND the 0 ability untaps Grim Monolith, Tezzeret would score very differently — apply this skill separately to that deck.)

## Worked Example 3: Chalice of the Void in Blue Post

**Card verified:** Chalice of the Void (Scryfall MRD #150). `{X}{X}` Artifact, MV variable. Oracle: "Chalice of the Void enters the battlefield with X charge counters on it. Whenever a player casts a spell with mana value equal to the number of charge counters on Chalice of the Void, counter that spell."

**Deck context:** Same Blue Post sample. Currently 0 Chalice mainboard hypothetically — the question is whether to add 3.

---

### Lens 1: Role Replacement — Chalice

```
Lens 1: Role Replacement
Score: +1

Evidence:
  - Chalice role: hard lock on cast events of specific MV. Specifically blanks 1-MV cantrips and 2-MV creature cantrips depending on X.
  - Blue Post has no existing "lock-on-cast" effect mainboard.
  - Sphere of Resistance taxes (does not lock), Trinisphere taxes more aggressively but doesn't counter outright.
  - Chalice@1 vs Sphere of Resistance: Chalice@1 counters Brainstorm; Sphere makes Brainstorm cost {1}{U} → still castable.

Alternative considered: Trinisphere (related lock role, MV 3, doesn't counter spells outright)

Verdict: +1 — adds a new role (hard counter on cast). Trinisphere taxes but doesn't lock; Chalice locks. Genuinely new capability.
```

### Lens 2: Mana Curve Fit — Chalice

```
Lens 2: Mana Curve Fit
Score: +1

Evidence:
  - Chalice MV is X (paid cost {X}{X}). The relevant cast costs in Blue Post: X=0, X=1, X=2 are most common.
  - validate_manabase for {0}{0}: trivially castable T0 / T1.
  - For {1}{1}: castable T1 via Ancient Tomb + Cloudpost (8/24 = 33% opening hand have it).
  - For {2}{2}: castable T2 standardly.
  - The deck has 4× Ancient Tomb → fast Chalice deployment is real.
  - Doesn't compete with One Ring (T4) or Karn (T4). Doesn't compete with Spheres (T3).

Alternative considered: leaving slot empty (no other 0-2 MV artifact lock available)

Verdict: +1 — Ancient Tomb-fueled T1 Chalice@1 is a real line. Mana base supports it on 33%+ of openers.
```

### Lens 3: Meta Fit — Chalice

```
Lens 3: Meta Fit
Score: +2

Evidence:
  - Top 5 archetypes vs Chalice@1 (1-MV spell count from samples):
      Dimir Tempo (samples/Legacy_Dimir_Tempo_by_kyataoka.txt fetch 2026-05-25):
        Brainstorm 4, Ponder 4, Aether Vial 0, Daze 4, Force of Will 4 (but FoW is MV 5 — Chalice@1 doesn't catch).
        1-MV cast count in their typical opener: 4+4+4 = 12 cards out of 60 → expected 1.4 of these in opening 7. Chalice@1 hits 1-2 plays in many games.
      UR Tempo (samples/Legacy_UR_Tempo_by_silviawataru.txt): similar 1-MV cantrip density (Brainstorm 4, Ponder 4, Delver 4, Daze 4).
      Doomsday (samples/Legacy_Doomsday_by_Sinflower.txt): Brainstorm 4, Ponder 4, Preordain 4, Lotus Petal 4 (MV 0 — Chalice@0 catches THIS instead).
      UWx Control (samples/Legacy_UWx_Control_by_habsburger.txt): Brainstorm 4, Ponder 2, Swords to Plowshares 4 (MV 1).
      Lands (samples/Legacy_Lands_by_Lincerastas.txt): Mox Diamond 4 (MV 0 — Chalice@0), Crop Rotation 4 (MV 1), Gamble 4 (MV 1).
  - Hate against Chalice in mainboards: 0 archetypes mainboard Echoing Truth, Disenchant, or Pithing Needle on Chalice. (Sideboard hate exists but is reactive, not Game-1 active.)

Alternative considered: Trinisphere (taxes everything ≥ MV 4 to MV 4, fewer hard locks)

Verdict: +2 — Chalice@1 hits the cast engine of 4 of the top 5 archetypes (Dimir Tempo, UR Tempo, Doomsday, UWx Control, Lands all run 4+ 1-MV staples). Chalice@0 hits Lotus Petal/Mox Diamond combo accelerants. No mainboard hate in current top 5.
```

### Lens 4: Synergy Math — Chalice

```
Lens 4: Synergy Math
Score: 0

Evidence:
  - Type: artifact. Triggers nothing in Blue Post (no artifact-count synergies in this deck).
  - Self-damage check: Blue Post mainboard 1-MV cards: 0. Chalice@1 doesn't blank any of YOUR own spells.
  - Stock Up (MV 3), Flow State (MV 2 if added), Kozilek's Command (variable X+CC), One Ring (MV 4), Karn (MV 4), Trinisphere (MV 3), Sphere of Resistance (MV 3), Tolaria West (channel ability MV 1 — Chalice@1 catches your own channel!).
  - WAIT: Tolaria West "channel — discard this land, pay {U}{U} — tutor for a 0-MV permanent" is itself an activated ability at MV 1? No — channel abilities are activated abilities, NOT cast events. Chalice counters CAST spells. Channel is activated. Not affected. Verify: Scryfall Oracle text confirms "channel" works as an activated ability that doesn't trigger cast-replacement effects.
  - Conclusion: zero collateral self-damage from Chalice@1.

Alternative considered: not applicable (we're evaluating Chalice itself, not against an alternative for this lens — Lens 5 handles that)

Verdict: 0 — neutral type. No engine enabled, no engine disabled, no self-damage. Chalice@1 doesn't catch any Blue Post spell because the deck's lowest MV mainboard spell is MV 2 (Flow State if added, otherwise Chalice itself).
```

### Lens 5: Opportunity Cost — Chalice

```
Lens 5: Opportunity Cost
Score: +1

Evidence:
  - Alternatives for the "T1-T2 lock-effect" slot:
      Trinisphere — taxes only, doesn't counter. Lens 1 verdict above shows Chalice strictly dominates here.
      Defense Grid — anti-counterspell tax, only helps on your turn. Lens 3 weaker (helps in 2 of 5 matchups, not 4).
      Ensnaring Bridge — anti-creature lock, completely different role.
  - No artifact at MV 0-2 fills the same hard-lock-on-cast role as Chalice.

Alternative considered: Trinisphere

Verdict: +1 — no better alternative exists at this slot for the specific role. Trinisphere taxes but doesn't lock.
```

**Composite: +1 + 1 + 2 + 0 + 1 = +5.** Verdict per decision table: **Strong include — likely strict upgrade.** Run 2–3 copies mainboard, 1 in sideboard.

## Pitfalls in Card Evaluation

| Pitfall | Why bad | Fix |
|---|---|---|
| Score without Evidence block | A score with no citation is just inference | Refuse to score the lens; mark `unscored — needs verification` |
| "It's cheaper, so it's better" | Ignores card economy, triggers, and reliability | Score Lens 4 separately with `joint_n_cards` output |
| "It's a Tier 1 staple" | Stale meta data; what was Tier 1 last month may have shifted | Verify Lens 3 against mtgtop8 archetype % with fetch date |
| "Same effect, cheaper cost" | The cheaper version usually has activation conditions or downsides | Read both Oracle texts carefully — quote each in Evidence block |
| "It's a new card so it's playable" | New ≠ good in this specific deck | Run all 5 lenses with Evidence required |
| "Other decks use it so I should too" | Different decks have different needs | Lens 1 — role in YOUR deck, citing the specific displaced card |
| Single lens dominates judgment | One lens isn't enough signal | Require 3+ favorable scored lenses for composite ≥ +2 |
| Skipping the verification step | Building evaluation on faulty card knowledge | Re-verify the card via Scryfall (see Prerequisites) |
| Claiming win rates without data | "I think this improves the matchup by X%" without source | Compute via parent-skill validators OR label as inference and refuse the score |
| Single deck cited for play rate | One sample is not a play-rate claim | Parse 2–3 decklists per archetype before claiming "deck X plays card Y" |
| Aggregating unscored lenses as 0 | Treats "unverified" the same as "verified neutral" | Unscored lenses do not contribute to the sum. Composite is over SCORED lenses only |
| Treating sample as live data | Samples have fetch dates that go stale | Cite sample's fetch date; if older than a B&R announcement, refetch live |

## Red Flags — STOP Before Scoring

| Thought / Action | Reality |
|---|---|
| "Score should be +1, that feels right" | Feels right is not evidence. Cite or refuse |
| "Stock Up vs Flow State, Flow State is cheaper so +1 Lens 2" | "Cheaper" doesn't establish curve-fit. Show the curve distribution |
| "Lens 3 is +2 because the meta loves this card" | Cite mtgtop8 archetype % per matchup |
| "Lens 4 is +1, I'm confident on the synergy" | Compute the rate. Quote Python output verbatim |
| "No real alternative comes to mind" | Enumerate alternatives explicitly. Even 3 alternatives with brief evidence is required for Lens 5 |
| "All 5 lenses are +1 to +2" | Suspicious — if every lens scores positive without specific evidence, you're confabulating. Demand the evidence per lens |

## Relationship to `mtg-deck-analysis`

This skill is callable in two ways:

1. **Standalone** — user invokes `/mtg-card-evaluation` directly with a card + deck context. You verify Prerequisites yourself, including running validators like `validate_manabase` and any probability calls cited in Evidence blocks.
2. **As sub-skill of `mtg-deck-analysis`** — when the parent skill encounters a card-deck-fit question, it invokes you via the Skill tool. Prerequisites 1–4 have already been done; validator outputs may already be in the conversation context.

In both cases, the output is **five per-lens Evidence blocks + composite scorecard + verdict**, with each lens score traceable to its Evidence block.

## TDD Status

- **v1** (2026-05-25): split from `mtg-deck-analysis` supporting file (`mtg-card-evaluation.md`) into a standalone skill (`mtg-card-evaluation/SKILL.md`), invokable independently or via Skill tool.
- **v2** (2026-05-25): added the Iron Law (no lens score without evidence). Each lens now requires a per-lens Evidence block citing Scryfall / mtgtop8 / Python output / named alternatives. Worked examples rewritten in this format with concrete citations (Python computations for trigger rates, decklist sample references with fetch dates, named alternative cards with Scryfall set codes). Motivation: previous 5-point lens scoring without required evidence let "feels stronger" pass as analysis — promoting it to a percentage scale would have made hallucination worse, not better. Detail is added through evidence depth, not score granularity.

RED failures that motivated v2:
- Flow State scored as "+1 Lens 4 — trigger rate around 35-45%" without a computation. Demand: cite the Python output.
- Chalice scored as "+2 Lens 3 — meta is full of 1-MV cantrips" without counting them in actual decklists. Demand: cite samples with fetch date.
- Tezzeret rejected as "Lens 5 −2, Karn is obviously better" without enumeration. Demand: name the alternative and its dominance on specific lenses.

GREEN check: any fresh card+deck pair, applied through the framework, must produce 5 Evidence blocks. If a lens produces only a score and no Evidence, the framework has been used incorrectly.
