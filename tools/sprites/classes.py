"""Gear overlays + the five job-class presets.

Importing this module registers the overlay parts into composer.OVERLAYS.
A class is nothing but a CharacterSpec: palette swaps on the material
slots plus a tuple of overlay names. Use them like:

    import classes  # noqa: F401  (registers overlays)
    compose("SW", pose, spec=classes.CLASSES["knight"])

Overlay entry format (per drawn view):
    {"anchor", "grid", "after": part drawn just before it,
     "attach": part whose Pose shift it follows (default = after),
     "replaces": optional part it suppresses (helmet -> hair),
     "bodies": body names it renders on (default ("stand",))}

Overlays use the same CHARMAP material chars as body parts, so they recolor
through the spec too (the white mage's robe trim is 'K' accent chars
with accent="cloth_red"; on another spec the same grid would be gold).
"""

try:
    import composer
    from composer import CharacterSpec
except ImportError:
    from . import composer
    from .composer import CharacterSpec

O = composer.OVERLAYS

# ------------------------------------------------------------- overlays ---
# Rounded steel cap with cheek guards; replaces the hair outright.
O["helmet"] = {
    "front": {
        "anchor": (9, 2), "after": "hair", "attach": "head",
        "replaces": "hair",
        "grid": [
            "...ooooo...",
            "..opPPNNo..",
            ".opPPNNNMo.",
            ".oPPNNNNMo.",
            "opPNNNNNNMo",
            "oPNNNNNNMMo",
            "omMNNNNMMmo",
            ".oMo...oMo.",
            ".oMo...oMo.",
            "..o.....o..",
        ],
    },
    "back": {
        "anchor": (9, 6), "after": "hair", "attach": "head",
        "replaces": "hair",
        "grid": [
            "...ooooo...",
            "..opPPNNo..",
            ".opPPNNNMo.",
            ".oPPNNNNMo.",
            "opPNNNNNNMo",
            "oPNNNNNNMMo",
            "oPNNNNNMMMo",
            "omMNNNNMMmo",
            ".oMMNNMMMo.",
            "..ooooooo..",
        ],
    },
}

# Big soft wizard hat: wide brim over the brow, tall crown flopping right.
# Straw-gold via accent chars (black mage sets accent="straw").
O["hat_wizard"] = {
    "front": {
        "anchor": (4, 0), "after": "hair", "attach": "head",
        "replaces": "hair",
        "grid": [
            "..............ooo.....",
            ".............oKLko....",
            "...........ooKLLo.....",
            ".........ooKLLLo......",
            "*......ooKLLLLko......".replace("*", "."),
            ".....ooKLLLLLLo.......",
            "....oKLLLLLLLKo.......",
            ".ooooKLLLLLLLKoooo....",
            "oKKLLLLLkkLLLLLLKJo...",
            ".oojjjjjjjjjjjjjoo....",
            "...o..........o.......",
        ],
    },
    "back": {
        "anchor": (4, 0), "after": "hair", "attach": "head",
        "replaces": "hair",
        "grid": [
            ".....ooo..............",
            "....oKLko.............",
            ".....oLLKoo...........",
            "......oLLLKoo.........",
            "......okLLLLKoo.......",
            ".......oLLLLLLKoo.....",
            ".......oKLLLLLLLKo....",
            "....ooooKLLLLLLLKooo..",
            "...oJKKLLLLLkkLLLLKKo.",
            "....oojjjjjjjjjjjjoo..",
            "......o..........o....",
        ],
    },
}

# Linen hood/wimple draped to the shoulders; trim row recolors via accent.
O["hood"] = {
    "front": {
        "anchor": (9, 2), "after": "hair", "attach": "head",
        "replaces": "hair",
        "grid": [
            "...ooooo...",
            "..oewwwvo..",
            ".oewwwvvvo.",
            ".oewwvvvvo.",
            "oeKKKKKKKvo",
            "oewo...owvo",
            "oewo...owvo",
            "oevo...ovuo",
            ".ouo...ouo.",
            ".ouo...ouo.",
            "..o.....o..",
        ],
    },
    "back": {
        "anchor": (9, 6), "after": "hair", "attach": "head",
        "replaces": "hair",
        "grid": [
            "...ooooo...",
            "..oewwwvo..",
            ".oewwwvvvo.",
            ".oewwvvvvo.",
            "oewwwvvvvuo",
            "oewwvvvvuuo",
            "oewvvvvuuuo",
            "oeKKKKKKKuo",
            ".owvvvuuuo.",
            "..ooooooo..",
        ],
    },
}

# Thin cloth band across the fringe with a knot tail on the right.
O["headband"] = {
    "front": {
        "anchor": (8, 6), "after": "hair", "attach": "head",
        "grid": [
            "oKLLKKLLKKKo..",
            ".ooooooooooKo.",
            "...........oo.",
        ],
    },
    "back": {
        "anchor": (8, 8), "after": "hair", "attach": "head",
        "grid": [
            "oKKLLKLLKKLo..",
            ".ooooooooooKo.",
            "...........oo.",
        ],
    },
}

# Shoulder pads, both shoulders in one grid (screen-right sits 1px lower,
# matching the rig's dropped shoulder). Metal and leather variants.
def _pads(chars):
    a, b, c = chars  # dark, mid, light
    g_front = [
        f".ooooo........ooooo.",
        f"o{c}{b}{b}{a}o........o{b}{b}{a}{a}o",
        f"o{b}{b}{a}{a}o.......o{c}{b}{b}{a}{a}o",
        f".oooo.........ooooo.",
    ]
    return {
        "front": {"anchor": (6, 14), "after": "arm_near", "attach": "torso",
                  "grid": g_front},
        "back": {"anchor": (6, 14), "after": "arm_near", "attach": "torso",
                 "grid": g_front},
    }


O["pads_metal"] = _pads(("M", "N", "P"))
O["pads_leather"] = _pads(("S", "T", "U"))

# Robe skirt: flares from the belt to the ankles, covers most of the legs.
# Tunic chars, so it matches whatever the robe color is.
_SKIRT_FRONT = [
    ".oCBBBBBAAo..",
    ".oCBBBBBAAo..",
    "oCCBBBBBAAAo.",
    "oCBBBABBAAAo.",
    "oCBBBABBAAAo.",
    "oCBBBABBAAAo.",
    "oCBBBABBAAAAo",
    "ocCBBABBBAAAo",
    "oaaAAaAAAaaao",
    ".ooooooooooo.",
]
_SKIRT_BACK = [
    ".oCBBBBBAAo..",
    ".oCBBBBBAAo..",
    "oCCBBBBBAAAo.",
    "oCBABBBBAAAo.",
    "oCBABBBBAAAo.",
    "oCBABBBBAAAo.",
    "oCBABBBBAAAAo",
    "ocCABBBBBAAAo",
    "oaaAAaAAAaaao",
    ".ooooooooooo.",
]
O["robe_skirt"] = {
    "front": {"anchor": (9, 24), "after": "torso", "attach": "torso",
              "grid": _SKIRT_FRONT},
    "back": {"anchor": (9, 24), "after": "torso", "attach": "torso",
             "grid": _SKIRT_BACK},
}

# ------------------------------------------------------- class presets ----
CLASSES = {
    # plain fighting clothes + leather shoulder pads
    "squire": CharacterSpec(
        tunic="cloth_green", overlays=("pads_leather",)),
    # steel plate read: armored torso ramp + helmet + metal pauldrons
    "knight": CharacterSpec(
        tunic="steel_blue", pants="cloth_navy", hair="hair_brown",
        overlays=("helmet", "pads_metal")),
    # face in shadow, glowing eyes, straw hat, long navy robe
    "black_mage": CharacterSpec(
        tunic="cloth_navy", pants="cloth_navy", skin="shadow",
        accent="straw", boots="leather", eye=(250, 214, 128),
        overlays=("hat_wizard", "robe_skirt")),
    # white linen robe with red trim (accent slot -> red)
    "white_mage": CharacterSpec(
        tunic="linen", pants="linen", accent="cloth_red",
        boots="leather", overlays=("hood", "robe_skirt")),
    # leather vest, green trousers, cloth headband
    "archer": CharacterSpec(
        tunic="leather", pants="cloth_green", hair="hair_brown",
        overlays=("headband",)),
}
