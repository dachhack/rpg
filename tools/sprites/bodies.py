"""Alternate body part sets: kneel and prone.

Importing this module registers them into composer.BODIES, so a Pose can
select them immediately:

    import bodies  # noqa: F401  (side-effect registration)
    Pose(body="kneel")     # critical / low-HP kneel, damage crouch
    Pose(body="prone")     # lying flat: death, damage knockdown end

Both variants exist for the drawn "front" (SW) and "back" (NW) views;
SE/NE mirror for free, exactly like the standing body.

KNEEL reuses the standing hair/head/torso/arm grids BY REFERENCE (only
re-anchored ~6px lower), so any polish to the standing art flows through
automatically. Only the legs are new: near leg folded up with the foot
planted, far knee on the ground with the boot trailing behind -- the
classic FFT critical kneel.

PRONE is a fully separate horizontal figure (head screen-left, feet
screen-right, one arm flung out past the head -- the FFT death slump).
It keeps the same seven part names so Pose.shift / hide / groups all
still work per-part.
"""

try:
    import composer
except ImportError:
    from . import composer

_P = composer.PARTS


def _re(view, part, anchor):
    """Standing part grid, shared by reference, at a new anchor."""
    return {"anchor": anchor, "grid": _P[view][part]["grid"]}


# ------------------------------------------------------------------ kneel --
KNEEL = {
    "front": {
        # upper body: the standing rig dropped 6px, weight sunk
        "hair": _re("front", "hair", (6, 6)),
        "head": _re("front", "head", (11, 13)),
        "torso": _re("front", "torso", (10, 21)),
        "arm_near": _re("front", "arm_near", (7, 22)),
        "arm_far": _re("front", "arm_far", (20, 24)),
        # near leg: knee up, foot planted forward
        "leg_near": {
            "anchor": (8, 28),
            "grid": [
                "ofFEo.",
                "ofFEEo",
                "oFEEo.",
                "oFEo..",
                "oFDo..",
                "oIHo..",
                "oiIHGo",
                ".oooo.",
            ],
        },
        # far leg: kneeling -- thigh drops to a grounded knee, shin folds
        # back, boot toe trails on the ground behind
        "leg_far": {
            "anchor": (15, 29),
            "grid": [
                ".oEDo...",
                ".oEDo...",
                "oEEDo...",
                "oEDDoGGo",
                "oEDDHHGo",
                ".ooooooo",
            ],
        },
    },
    "back": {
        "hair": _re("back", "hair", (6, 6)),
        "head": _re("back", "head", (13, 17)),
        "torso": _re("back", "torso", (10, 21)),
        "arm_near": _re("back", "arm_near", (5, 23)),
        "arm_far": _re("back", "arm_far", (21, 23)),
        # from behind: planted shin on screen-left...
        "leg_near": {
            "anchor": (10, 28),
            "grid": [
                "oFEo..",
                "oFEEo.",
                "oFEo..",
                "oFDo..",
                "oIHo..",
                "oIHGo.",
                ".ooo..",
            ],
        },
        # ...and the folded far leg shows its boot sole tipped up
        "leg_far": {
            "anchor": (15, 29),
            "grid": [
                ".oEDo...",
                ".oEDDo..",
                "oEDDoGgo",
                "oEDDHGgo",
                ".ooooooo",
            ],
        },
    },
}

# ------------------------------------------------------------------ prone --
# Lying flat along the ground line, ~29px long, in the bottom third of the
# frame. Front view = fallen face-up (eyes closed, drawn as skin-shadow
# dashes); back view = fallen face-down (only splayed hair, no face).
PRONE = {
    "front": {
        # far leg lies behind/above the near one
        "leg_far": {
            "anchor": (19, 27),
            "grid": [
                ".oEEEDDDoo.",
                "oEEEDDDHGGo",
                ".ooooooooo.",
            ],
        },
        "leg_near": {
            "anchor": (18, 30),
            "grid": [
                ".oFFEEEDooo.",
                "oFFEEEDIHGGo",
                ".oooooooooo.",
            ],
        },
        # torso on its back, belt visible
        "torso": {
            "anchor": (10, 27),
            "grid": [
                ".ooooooooo.",
                "ocCBBBBAAao",
                "oCBBBSBBAAo",
                "ocBBBTBBAao",
                ".oABBSBAAo.",
                "..ooooooo..",
            ],
        },
        # far arm folded across the chest
        "arm_far": {
            "anchor": (13, 29),
            "grid": [
                ".oBAo.",
                "oBAUTo",
                ".ooooo",
            ],
        },
        # near arm flung out past the head -- the FFT death arm. Runs
        # ABOVE the hair so both silhouettes stay readable.
        "arm_near": {
            "anchor": (1, 22),
            "grid": [
                ".oo........",
                "oTSoo......",
                "oUTABo.....",
                ".oooBBAo...",
                "....oBBAo..",
                ".....oooo..",
            ],
        },
        # head tipped back, face up, eyes closed ('1' dashes, no 'x')
        "head": {
            "anchor": (5, 27),
            "grid": [
                ".ooooo..",
                "o99999o.",
                "o911911o",
                "o999993o",
                ".o39932o",
                "..ooooo.",
            ],
        },
        # hair splays along the ground past the crown, left of the face
        # (kept inside x0-6 so the face stays readable)
        "hair": {
            "anchor": (0, 26),
            "grid": [
                ".o55o..",
                "o56876o",
                "o45786o",
                "o46776o",
                "o45776o",
                ".o4565o",
                "..o454o",
                "...oo..",
            ],
        },
    },
    "back": {
        # same slump seen from the other side: face-down, hair covers the
        # head, the flung arm shows its back/glove
        "leg_far": {
            "anchor": (19, 27),
            "grid": [
                ".oEEEDDDoo.",
                "oEEEDDDGGHo",
                ".ooooooooo.",
            ],
        },
        "leg_near": {
            "anchor": (18, 30),
            "grid": [
                ".oFFEEEDooo.",
                "oFFEEEDGHIHo",
                ".oooooooooo.",
            ],
        },
        "torso": {
            "anchor": (10, 27),
            "grid": [
                ".ooooooooo.",
                "ocCBBBBBAao",
                "oCBABBBBAAo",
                "ocBABBBBAao",
                ".oABBBBAAo.",
                "..ooooooo..",
            ],
        },
        "arm_far": {
            "anchor": (13, 29),
            "grid": [
                ".oBAo.",
                "oBAUTo",
                ".ooooo",
            ],
        },
        "arm_near": {
            "anchor": (1, 22),
            "grid": [
                ".oo........",
                "oSToo......",
                "oTUABo.....",
                ".oooBBAo...",
                "....oBBAo..",
                ".....oooo..",
            ],
        },
        # face-down: a sliver of neck only
        "head": {
            "anchor": (6, 30),
            "grid": [
                "o221o",
                ".ooo.",
            ],
        },
        # face-down hair: flattened spike mass splaying left along the
        # ground, notched left edge so it reads as locks, not a ball
        "hair": {
            "anchor": (0, 26),
            "grid": [
                "...o555o..",
                ".o556786o.",
                "o45578876o",
                ".oo457767o",
                "o4457667o.",
                ".o445565o.",
                "...o4454o.",
                ".....ooo..",
            ],
        },
    },
}

composer.BODIES["kneel"] = KNEEL
composer.BODIES["prone"] = PRONE
