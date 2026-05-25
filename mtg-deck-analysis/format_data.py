"""
Per-format constants for mtg-deck-analysis validators.

This module is imported by the deterministic validators documented in
SKILL.md's "Deterministic Validators" block. It centralizes data that
differs between Legacy and Modern so each validator can take a single
`format=` keyword argument and look up the right values here.

DESIGN INTENT (per PLAN-modern-mode-b.md Phase 5):
  - This file holds CONSTANTS used as starting hints, NOT authoritative facts.
  - Every card name listed here is a claim that must be re-verifiable via
    Scryfall live. The constants speed up validators by giving them a
    candidate list to intersect against the user's decklist — they do not
    replace verification.
  - Format strings are exactly "legacy" or "modern" — matching the result
    of SKILL.md Step 0 (format identification).
  - If a card moves between formats via B&R, update this file AND verify
    the constants haven't drifted. Don't trust constants older than 6 months
    without a re-verification pass.

Last verified via Scryfall cards/collection endpoint: 2026-05-25.
"""

# ---------------------------------------------------------------------------
# CANTRIP_POOLS
# ---------------------------------------------------------------------------
# Cards that let you see additional cards (draw / scry / surveil / impulse-draw /
# look-and-take). Used by p_find_target_with_cantrips() to compute effective
# look-depth when searching for a target card.
#
# Each card listed must satisfy:
#   1. legal in its format (Scryfall legality lookup), AND
#   2. provides a card-quality / dig effect (look-at-top, scry, surveil,
#      draw, impulse-exile-then-cast), AND
#   3. is actually played in the format (per recent samples/<format>/* lists
#      or top mtgtop8 archetypes).
#
# Notes on what's INTENTIONALLY excluded:
#   - Pure draw without filtering (e.g., a card that just draws 1 with no
#     selection) — those increase hand size but don't increase effective
#     look-depth. Treat them with a normal hypergeometric on the relevant
#     turn count instead.
#   - Tutors (Demonic Tutor, Vampiric Tutor) — those find a specific card,
#     not increase look-depth probabilistically. Different math.

CANTRIP_POOLS = {
    "legacy": [
        # Verified Scryfall 2026-05-25: legal in legacy, draw/filter effect
        "Brainstorm",       # MV 1, draw 3 + put 2 back on top
        "Ponder",           # MV 1, look 3 + may shuffle + draw 1
        "Preordain",        # MV 1, scry 2 + draw 1
        "Opt",              # MV 1, scry 1 + draw 1
        "Consider",         # MV 1, surveil 1 + draw 1
        "Mishra's Bauble",  # MV 0, look at top of any library; draw next upkeep
        "Stock Up",         # MV 3, look 5 + take 2 (NOT a cheap cantrip but is in the family)
        "Flow State",       # MV 2, look 3 + take 1 (or 2 with delirium-light)
    ],
    "modern": [
        # Verified Scryfall 2026-05-25: legal in modern, draw/filter effect
        # NOTE: Brainstorm and Ponder are NOT here — `not_legal` and `banned`
        # in Modern respectively. Verified.
        "Consider",                 # MV 1, surveil 1 + draw 1
        "Preordain",                # MV 1, scry 2 + draw 1
        "Opt",                      # MV 1, scry 1 + draw 1
        "Mishra's Bauble",          # MV 0, see-top + delayed draw
        "Otherworldly Gaze",        # MV 1, surveil 3 (no draw, but big filter)
        "Stock Up",                 # MV 3, look 5 + take 2
        "Flow State",               # MV 2, look 3 + take 1 (also Modern-legal)
        "Expressive Iteration",     # MV 2, impulse draw (Modern-only — Legacy-banned)
        "Reckless Impulse",         # MV 2, impulse draw
        "Wrenn's Resolve",          # MV 2, impulse draw
        "Manamorphose",             # MV 2, ritual + draw 1
    ],
}


# ---------------------------------------------------------------------------
# ARCHETYPE_SAMPLE_DIRS
# ---------------------------------------------------------------------------
# Per-format directory containing the canonical sample decklists used by
# archetype_similarity() for Jaccard comparison.
#
# Paths are relative to the skill root (mtg-deck-analysis/).

ARCHETYPE_SAMPLE_DIRS = {
    "legacy": "samples/legacy",
    "modern": "samples/modern",
}


# ---------------------------------------------------------------------------
# WASTELAND_ANALOG
# ---------------------------------------------------------------------------
# Cards that destroy lands at low mana cost. Used by validators that flag
# manabase weakness (e.g., "this deck only has 4 nonbasic lands — vulnerable
# to Wasteland in Legacy / no Wasteland in Modern").
#
# Modern has no Wasteland equivalent; Field of Ruin and Boseiju are the
# closest functional analogs (4-mana for Field of Ruin, channel-cost for
# Boseiju), but they hit different targets and aren't the same threat as
# Wasteland's `{T}` activation.

WASTELAND_ANALOG = {
    "legacy": ["Wasteland"],
    "modern": [],  # No true Wasteland-class card; Field of Ruin / Boseiju are nearest
}


# ---------------------------------------------------------------------------
# CHALICE_VULNERABILITY
# ---------------------------------------------------------------------------
# For decks that play Chalice of the Void (legal both formats), this maps
# format → list of common low-MV staples that get blanked at common Chalice
# settings. Used in Step 5 interaction analysis to estimate Chalice's impact.
#
# Only includes cards verified present in 2+ samples for that format.

CHALICE_VULNERABILITY = {
    "legacy": {
        1: ["Brainstorm", "Ponder", "Preordain", "Lightning Bolt", "Daze",
            "Delver of Secrets", "Dragon's Rage Channeler", "Aether Vial",
            "Wasteland (NO — MV 0)"],  # marked for spot-check
        0: ["Lotus Petal", "Mox Diamond", "Mox Opal", "Mishra's Bauble"],
        2: ["Bowmasters", "Force of Negation", "Snapcaster Mage",
            "Murktide Regent (MV varies — verify)", "Counterspell"],
    },
    "modern": {
        1: ["Lightning Bolt", "Ragavan, Nimble Pilferer", "Galvanic Discharge",
            "Slickshot Show-Off", "Monastery Swiftspear", "Dragon's Rage Channeler"],
        0: ["Mox Opal", "Mishra's Bauble", "Vexing Bauble"],
        2: ["Cori-Steel Cutter", "Phelia, Exuberant Shepherd", "Counterspell",
            "Expressive Iteration", "Talisman of Resilience"],
    },
}


# ---------------------------------------------------------------------------
# FORMAT_CODES
# ---------------------------------------------------------------------------
# Maps to URL parameters used by external data sources.

FORMAT_CODES = {
    "legacy": {
        "mtgtop8_f": "LE",
        "scryfall_banned_query": "banned%3Alegacy",
        "wizards_section_anchor": "Legacy",
    },
    "modern": {
        "mtgtop8_f": "MO",
        "scryfall_banned_query": "banned%3Amodern",
        "wizards_section_anchor": "Modern",
    },
}


# ---------------------------------------------------------------------------
# Module self-check (run with: python3 format-data.py)
# ---------------------------------------------------------------------------

def _self_check() -> None:
    """Sanity checks on the constants — run before relying on this file."""
    # All format dicts use the same keys
    expected = {"legacy", "modern"}
    for name, d in [
        ("CANTRIP_POOLS", CANTRIP_POOLS),
        ("ARCHETYPE_SAMPLE_DIRS", ARCHETYPE_SAMPLE_DIRS),
        ("WASTELAND_ANALOG", WASTELAND_ANALOG),
        ("CHALICE_VULNERABILITY", CHALICE_VULNERABILITY),
        ("FORMAT_CODES", FORMAT_CODES),
    ]:
        assert set(d.keys()) == expected, f"{name} keys != {expected}"

    # Cantrip pools have no duplicates
    for fmt, pool in CANTRIP_POOLS.items():
        assert len(pool) == len(set(pool)), f"CANTRIP_POOLS[{fmt}] has duplicates"

    # FORMAT_CODES has the expected inner keys
    for fmt, codes in FORMAT_CODES.items():
        assert set(codes.keys()) == {"mtgtop8_f", "scryfall_banned_query",
                                      "wizards_section_anchor"}, \
            f"FORMAT_CODES[{fmt}] missing expected keys"

    print(f"format-data.py self-check OK")
    print(f"  Legacy cantrips:  {len(CANTRIP_POOLS['legacy'])}")
    print(f"  Modern cantrips:  {len(CANTRIP_POOLS['modern'])}")
    print(f"  Sample dirs:      {ARCHETYPE_SAMPLE_DIRS}")
    print(f"  Format codes:     legacy={FORMAT_CODES['legacy']['mtgtop8_f']}, "
          f"modern={FORMAT_CODES['modern']['mtgtop8_f']}")


if __name__ == "__main__":
    _self_check()
