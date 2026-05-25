---
name: mtg-card-evaluation
description: Use when deciding whether to add a specific Magic the Gathering card to a specific deck, whether one card is an upgrade over another in a deck, when evaluating new-set printings for inclusion in existing lists, for sideboard slot decisions, or for replacement choices after a ban. Apply specifically to card-deck-fit questions, not general deck analysis.
disable-model-invocation: true
---

# MTG Card Evaluation

## Overview

Card evaluation answers exactly one question: **"does card X belong in deck Y?"** It is **not** general deck analysis — that's `mtg-deck-analysis`. This skill is a five-lens scoring framework you apply *after* Oracle text, ban status, and current meta have been verified.

Core principle: **A card is a real upgrade only if it scores favorably on 3+ lenses AND doesn't fail any lens catastrophically.** Single-lens reasoning ("it's cheaper", "it's a Tier 1 staple", "the new set printed it") is the most common failure mode.

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

You MUST have completed these before applying the framework:

1. **Verified the card's Oracle text via Scryfall** (`curl` with `User-Agent` + `Accept: application/json` headers — `WebFetch` returns 403). Never reason from card name or memory.
2. **Verified the card is legal in the format** (live fetch from `https://magic.wizards.com/en/banned-restricted-list`, never cached).
3. **Identified the current top archetypes** (mtgtop8 with date noted).

If invoked from `mtg-deck-analysis`, Steps 1–3 are its responsibility. If invoked standalone, do them first — or refuse to evaluate.

## The Five-Lens Evaluation

Score the card on each lens independently. Sum the scores. **Decision table** is at the bottom.

### Lens 1: Role Replacement

What role does the card fill, and what does it displace?

- Identify the deck slot the card occupies (ramp / interaction / draw / threat / lock / utility).
- Identify which existing card it displaces (which card gets cut to make room).
- Compare directly: what does the displaced card give that the new card doesn't?

**Scoring:**
- Strict upgrade in role (same role, more value, no downside) → **+2**
- Lateral move (different shape, same role) → **0**
- Downgrade in core role for sidegrade in another → **−1**
- Adds a new role the deck currently lacks → **+1**

### Lens 2: Mana Curve Fit

Does the card fit the deck's curve and tempo?

- Where does the cost slot into the curve?
- Can the deck reliably cast it on-curve given its mana base? (For a verified answer, use `mtg-deck-analysis`'s `validate_manabase()` validator.)
- Does it require colored mana the deck doesn't have enough of?
- Does it compete for the same turn as more important plays?

**Scoring:**
- Fills a curve gap → **+2**
- Curve neutral → **0**
- Curve crowded — competes with existing plays at that mana point → **−1**

### Lens 3: Meta Fit

How does it perform against the current top 5 archetypes by meta share?

- Does this card improve the matchup? Through what specific mechanism?
- Does the meta have hate cards that punish this card specifically?
- Specific interactions to verify: Wasteland exposure, Bowmasters trigger, Chalice@N reach, common removal suite, common counter suite.

**Scoring:**
- Improves 2+ top matchups, no significant hate → **+2**
- Improves 1 matchup, neutral elsewhere → **+1**
- Targeted by significant meta hate → **−1**
- Both improves AND gets hated (cancels) → **0**

### Lens 4: Card Type and Synergy Math

Does the card interact correctly with the deck's existing engines AND the meta's anti-engine hate?

- Counts as the right type for in-deck triggers (instant for delirium, artifact for affinity, etc.).
- Triggers external hate (Bowmasters on draws, Mindbreak Trap on storm count, etc.).
- Fills card-type quotas (e.g., 4 types in graveyard for delirium).

For probability-fueled effects, use `mtg-deck-analysis`'s deterministic validators rather than estimation:
- Hypergeometric for "drawing N copies by turn K"
- `joint_n_cards()` for graveyard triggers ("drew AND cast AND resolved")
- `p_find_target_with_cantrips()` for combo-fetch reliability
- Do not claim "around X%" without computing.

**Scoring:**
- Enables a new engine in deck → **+2**
- Strengthens an existing engine → **+1**
- Neutral type → **0**
- Triggers opp's hate (e.g., Bowmasters on Brainstorm) → **−1**
- Disables an existing engine → **−2**

### Lens 5: Opportunity Cost

What else could fill the slot?

- Is there a strictly better alternative available?
- Could the slot go to a sideboard piece that addresses a specific matchup more directly?
- Does adding this card require cutting something load-bearing?

**Scoring:**
- No better alternative exists → **+1**
- Comparable alternatives — choice is mostly preference → **0**
- Strictly better alternative exists → **−2**

## Composite Decision

Sum the scores across all five lenses:

| Total | Action |
|---|---|
| ≥ +5 | Strong include — likely strict upgrade |
| +2 to +4 | Include 1–2 copies, test, iterate |
| 0 to +1 | Flex slot; depends on meta read |
| −1 to −2 | Don't include unless meta specifically calls for it |
| ≤ −3 | Don't include |

## Worked Example 1: Flow State in Blue Post (Legacy, May 2026)

**Card verified:** Flow State (Scryfall SOS #49). `{1}{U}` Sorcery. "Look at the top three cards of your library, then put one of them into your hand. (Or put two of them into your hand if there's both an instant card and a sorcery card in your graveyard.)"

**Deck context:** Blue Post has 14 instants and 4–6 sorceries (after proposed Flow State addition). Heavy on instants.

| Lens | Score | Reasoning |
|---|---|---|
| 1. Role Replacement | 0 | Would displace 1 Stock Up. Stock Up = guaranteed +1 card at 3 mana. Flow State = EV +0.4 card at 2 mana given low sorcery density. Lateral move at best |
| 2. Mana Curve | +1 | 2-mana slot is open on T1 after Ancient Tomb plays Chalice; Stock Up takes T2–T3 |
| 3. Meta Fit | +1 | Doesn't trigger Bowmasters (current Dimir Tempo Tier 1 threat). Same advantage as Stock Up though, so marginal lift |
| 4. Synergy Math | 0 | Delirium-light trigger only ~35–45% reliable given the deck has only 4–6 sorceries and 14 instants. The lopsided ratio makes the "2 of 3" mode unreliable |
| 5. Opportunity Cost | 0 | Stock Up is the better raw-value alternative; Chalice is a better meta-tech alternative for the same slot. Flow State has no clear "best fit" niche |

**Total: +2.** Verdict: Include 1 copy as flex / test. Don't go to 2–3 copies — the math doesn't support it.

## Worked Example 2: Tezzeret, Cruel Captain in Blue Post

**Card verified:** Tezzeret, Cruel Captain (Scryfall EOE #2). `{3}` Legendary Planeswalker with 4 starting loyalty. Triggers on artifact ETB (+1 loyalty). 0: untap target artifact or creature. −3: tutor a 0 or 1 MV artifact card from library.

**Deck context:** Blue Post mainboard has The One Ring (MV 4) and Chalice of the Void (MV varies, often 1–2) as artifacts. No 0–1 MV artifacts mainboard.

| Lens | Score | Reasoning |
|---|---|---|
| 1. Role Replacement | 0 | Would compete with Karn for the 3–4 mana planeswalker slot. Karn's −2 wishboard to fetch from sideboard is much stronger here |
| 2. Mana Curve | 0 | Same 3-mana slot as Karn, redundant |
| 3. Meta Fit | 0 | Doesn't specifically improve current matchups |
| 4. Synergy Math | −1 | Almost no valid −3 targets in this deck. Best targets are sideboard-only (Walking Ballista at MV 0, Tormod's Crypt at MV 0) — and Karn already does that better |
| 5. Opportunity Cost | −2 | Karn is strictly better for this deck's wishboard role |

**Total: −3.** Verdict: Don't include in Blue Post. (Note: Tezzeret SHINES in Trini Tron where Manifold Key, Voltaic Key, and Pithing Needle are all valid tutor targets, and the 0 ability untaps Grim Monolith for explosive ramp.)

## Worked Example 3: Chalice of the Void in Blue Post

**Card verified:** Chalice of the Void (Scryfall MRD #150). `{X}{X}` Artifact. Enters with X charge counters. Counters spells whose mana value equals the number of charge counters.

**Deck context:** Blue Post has Ancient Tomb for T1 2-mana plays. Current Legacy meta has heavy 1-MV staples in Dimir Tempo (Brainstorm, Ponder, Delver, DRC, Nethergoyf, and Bowmasters at MV 2 — so Chalice@2 catches it).

| Lens | Score | Reasoning |
|---|---|---|
| 1. Role Replacement | +1 | Adds a new role: hard lock on Tempo's cantrip engine |
| 2. Mana Curve | +1 | T1 from Ancient Tomb playable; doesn't compete with Karn / One Ring later |
| 3. Meta Fit | +2 | Chalice@1 blanks Brainstorm/Ponder/Delver/DRC/Nethergoyf/Aether Vial; Chalice@0 blanks Lotus Petal/Mox Diamond combo enablers. Two top archetypes (Dimir Tempo, Mystic Forge Combo) take significant hits |
| 4. Synergy Math | 0 | Blue Post doesn't have many 1-MV spells of its own — Stock Up is MV 3, Flow State MV 2, Kozilek's Command MV variable (X+CC). Minimal collateral damage |
| 5. Opportunity Cost | +1 | No other artifact does this role at this efficiency |

**Total: +5.** Verdict: Strong include at 2–3 copies mainboard, 1 in sideboard for flexibility.

## Pitfalls in Card Evaluation

| Pitfall | Why bad | Fix |
|---|---|---|
| "It's cheaper, so it's better" | Ignores card economy, triggers, and reliability | Score Lens 4 separately |
| "It's a Tier 1 staple" | Stale meta data; what was Tier 1 last month may have shifted | Verify Lens 3 against current meta |
| "Same effect, cheaper cost" | The cheaper version usually has activation conditions or downsides | Read both Oracle texts carefully and compare |
| "It's a new card so it's playable" | New ≠ good in this specific deck | Run all 5 lenses |
| "Other decks use it so I should too" | Different decks have different needs | Lens 1 — role in YOUR deck |
| Single lens dominates judgment | One lens isn't enough signal | Require 3+ favorable lenses for inclusion |
| Skipping the verification step | Building evaluation on faulty card knowledge | Re-verify the card via Scryfall (see Prerequisites) |
| Claiming win rates without data | "I think this improves the matchup by X%" without source | Label as inference; verify against aggregator if possible |
| Single deck cited for play rate | One sample is not a play-rate claim | Parse 2–3 decklists per archetype before claiming "deck X plays card Y" |

## Relationship to `mtg-deck-analysis`

This skill is callable in two ways:

1. **Standalone** — user invokes `/mtg-card-evaluation` directly with a card + deck context. You verify Prerequisites yourself.
2. **As sub-skill of `mtg-deck-analysis`** — when the parent skill encounters a card-deck-fit question during a broader analysis, it invokes you via the Skill tool. Steps 1–3 have already been done; you focus on the five-lens scoring.

In both cases, the output is the five-lens scorecard + composite verdict, with evidence labels (sourced fact / verified data / inference / recommendation) per claim.
