"""Weapon / prop layer for the FFT-style sprite rig.

Importing this module registers every prop into composer.WEAPONS, so a
Pose can use them immediately:

    import props  # noqa: F401  (side-effect registration)
    Pose(weapon="broadsword")
    Pose(weapon="bow_nocked", shift=props.hint("bow_nocked", "SW"))
    Pose(weapon=("broadsword", "shield"))          # multiple props

Naming: "<prop>" is the idle-held orientation; "<prop>_raised" and
"<prop>_thrust" are the swing/wind-up and stab orientations. Every prop
has BOTH drawn views ("front" = SW, "back" = NW); SE/NE mirror for free.

Anchor points: grips are drawn through the held hand of the rest pose --
  front view: near-arm fist at frame (8-9, 23-24)
  back view:  far-arm fist at frame (23-24, 23-24)
Weapons draw with after="torso", i.e. BEHIND the arms, so the fist paints
over the grip and the weapon reads as held. after=None draws the prop
behind every body layer (used for the shield and raised blades seen from
the far side of the body in back view).

Orientations that move the hand (raised/thrust) expect the arm to shift
with them. hint(key, facing) returns the recommended Pose.shift for that;
animation builders can add their own motion on top.

Materials (resolved per-character via CharacterSpec):
  metal  m M N P p    blade steel        leather s S T U t   grips, wood
  accent j J K L k    gold trim, orbs    linen   q u v w e   string, shaft
Chunky FFT read: 2px blades + selective outline, 3-4 visible ramp steps,
light upper-left (P/p on the left face of vertical blades).
"""

try:
    import composer
except ImportError:
    from . import composer


def _views(front_anchor, front_grid, back_anchor, back_grid,
           front_after="torso", back_after="torso"):
    return {
        "front": {"anchor": front_anchor, "grid": front_grid,
                  "after": front_after},
        "back": {"anchor": back_anchor, "grid": back_grid,
                 "after": back_after},
    }


PROPS = {}


def _mirror(grid):
    """Geometric left-right mirror of a grid (for the back-view twin of a
    diagonal prop). Shading chars are kept -- at 2px blade width the
    swapped light side is imperceptible."""
    w = max(len(r) for r in grid)
    return [r.ljust(w, ".")[::-1] for r in grid]


# ------------------------------------------------------------ broadsword --
# Idle: blade angled out and up from the fist, drawn IN FRONT of the
# hanging arm (FFT layers idle weapons over the body side; behind the
# torso the blade would vanish under the arm).
_BROADSWORD_IDLE = [
    ".oo.....",
    ".oPPo...",
    ".oPNo...",
    "..oPNo..",
    "..oPNo..",
    "...oPNo.",
    "...oPNo.",
    "....oPNo",
    "....oPNo",
    "....oNNo",
    "...oMNMo",   # crossguard
    "....oUso",   # grip over the fist (8-9, 22-24)
    "....oUso",
]
PROPS["broadsword"] = _views((3, 11), _BROADSWORD_IDLE,
                             (21, 11), _mirror(_BROADSWORD_IDLE),
                             front_after="arm_near", back_after="arm_far")

# Raised: diagonal wind-up over the shoulder, drawn over the hair like
# the FFT attack frames (behind the body it would vanish under the big
# hair mass). Front sweeps up-right from the raised near fist; back
# sweeps up-right from the raised far fist, hugging the hair silhouette.
PROPS["broadsword_raised"] = _views(
    (9, 10), [
        "..........oo.",
        ".........oPPo",
        "........oPNo.",
        ".......oPNo..",
        "......oPNo...",
        ".....oPNo....",
        "....oPNo.....",
        "...oPNo......",
        "..oNMo.......",
        ".oMMo........",
        ".oUso........",
        "..oo.........",
    ],
    (22, 9), [
        "....oo..",
        "...oPPo.",
        "...oPNo.",
        "..oPNo..",
        "..oPNo..",
        "..oPNo..",
        ".oPNo...",
        ".oPNo...",
        ".oNNo...",
        "oMNMo...",
        ".oUso...",
        ".oUso...",
    ],
    front_after="hair", back_after="arm_far",
)

# Thrust: horizontal stab. Front stabs screen-left, back screen-right.
PROPS["broadsword_thrust"] = _views(
    (0, 19), [
        "......oo....",
        ".ooooooPoo..",
        "oPPPPPMPUso.",
        ".oNNNNMPUso.",
        "..oooooPoo..",
        "......oo....",
    ],
    (20, 19), [
        "....oo......",
        "..ooPoooooo.",
        ".osUPMPPPPPo",
        ".osUPMNNNNo.",
        "..ooPooooo..",
        "....oo......",
    ],
)

# ---------------------------------------------------------------- dagger --
# Same outward tilt and in-front layering as the broadsword, much shorter.
_DAGGER_IDLE = [
    ".oo....",
    ".oPPo..",
    ".oPNo..",
    "..oPNo.",
    "..oNMo.",
    "..oMMo.",   # small guard
    "..oUso.",   # grip over the fist
    "..oUso.",
]
PROPS["dagger"] = _views((5, 15), _DAGGER_IDLE,
                         (20, 15), _mirror(_DAGGER_IDLE),
                         front_after="arm_near", back_after="arm_far")

PROPS["dagger_thrust"] = _views(
    (2, 20), [
        ".ooooMoo..",
        "oPPPNMUso.",
        ".ooooMoo..",
    ],
    (21, 20), [
        "..ooMoooo.",
        ".osUMNPPPo",
        "..ooMooo..",
    ],
)

# ------------------------------------------------------------------- bow --
# Idle: tall stave held at the side, string on the inside. Stave is wood
# (leather ramp), string a single pale linen line between the tips.
PROPS["bow"] = _views(
    (5, 14), [
        "...oo.",
        "..oTUo",
        ".oTUoe",
        ".oTUoe",
        "oTUo.e",
        "oTUo.e",
        "oTUo.e",
        "osSo.e",   # grip wrap -- fist lands here
        "osSo.e",
        "oTUo.e",
        "oTUo.e",
        "oTUo.e",
        ".oTUoe",
        ".oTUoe",
        "..oTo.",
        "...o..",
    ],
    (21, 14), [
        ".oo...",
        "oUTo..",
        "eoUTo.",
        "eoUTo.",
        "e.oUTo",
        "e.oUTo",
        "e.oUTo",
        "e.oSso",
        "e.oSso",
        "e.oUTo",
        "e.oUTo",
        "e.oUTo",
        "eoUTo.",
        "eoUTo.",
        ".oTo..",
        "..o...",
    ],
)

# Nocked: bow held out, arrow level with the shoulders pointing at the
# target. Arrow: metal head, linen shaft, gold fletching at the fist.
PROPS["bow_nocked"] = _views(
    (0, 13), [
        ".....oo.....",
        "....oTUo....",
        "...oTUo.....",
        "..oTUoe.....",
        "..oTUo.e....",
        ".oTUo...e...",
        ".oTUo...e...",
        ".oTUo....e..",
        "oo.ooo....o.",
        "oNwwwwwwwoKo",   # arrow: head w, shaft, nock at fist
        "oo.ooo...oKo",
        ".oTUo....e..",
        ".oTUo...e...",
        ".oTUo...e...",
        "..oTUo.e....",
        "..oTUoe.....",
        "...oTUo.....",
        "....oTUo....",
        ".....oo.....",
    ],
    (20, 13), [
        ".....oo.....",
        "....oUTo....",
        ".....oUTo...",
        ".....eoUTo..",
        "....e.oUTo..",
        "...e...oUTo.",
        "...e...oUTo.",
        "..e....oUTo.",
        ".o....ooo.oo",
        "oKowwwwwwwNo",
        "oKo...ooo.oo",
        "..e....oUTo.",
        "...e...oUTo.",
        "...e...oUTo.",
        "....e.oUTo..",
        ".....eoUTo..",
        ".....oUTo...",
        "....oUTo....",
        ".....oo.....",
    ],
)

# ----------------------------------------------------------------- staff --
# Idle: planted mage staff, taller than the figure, held at a slight
# diagonal so the gold orb clears the hair silhouette while the shaft
# still passes through the fist (x8-9, y23) down to a heel by the boot.
_STAFF_IDLE = [
    "..ooo...",   # orb, up-left of the hair
    ".ojKko..",
    ".ojKLo..",
    "..ooo...",
    "..oNo...",   # metal collar
    "..oUo...",
    "..oUo...",
    "..oUo...",
    "..oUo...",
    "..oUo...",
    "...oUo..",
    "...oUo..",
    "...oUo..",
    "...oUo..",
    "...oUo..",
    "...oUo..",
    "....oUo.",
    "....oUo.",
    "....oUo.",
    "....oUo.",
    "....oTo.",
    "....oTo.",
    "....oTo.",   # fist lands here (y23-24)
    "....oTo.",
    "....oTo.",
    ".....oTo",
    ".....oTo",
    ".....oTo",
    ".....oTo",
    ".....oSo",
    ".....oSo",
    ".....oSo",
    ".....oSo",
    ".....oMo",   # metal heel by the boot
]
PROPS["staff"] = _views((3, 1), _STAFF_IDLE,
                        (21, 1), _mirror(_STAFF_IDLE))

# Raised: staff swung up diagonally for a cast, orb high and away from
# the head. Back view keeps the orb right of the hair silhouette so it
# stays visible.
PROPS["staff_raised"] = _views(
    (9, 6), [
        "..........ooo.",
        ".........oJKko",
        ".........oJKLo",
        ".........oNoo.",
        "........oUo...",
        ".......oUo....",
        "......oUo.....",
        ".....oUo......",
        "....oUo.......",
        "...oUo........",
        "..oUo.........",
        ".oTo..........",
        ".oTo..........",
        ".oSo..........",
        "..o...........",
    ],
    (22, 3), [
        "...ooo..",
        "..ojKko.",
        "..ojKLo.",
        "...ooo..",
        "...oNo..",
        "...oUo..",
        "...oUo..",
        "...oUo..",
        "..oUo...",
        "..oUo...",
        "..oUo...",
        "..oUo...",
        "..oUo...",
        ".oUo....",
        ".oTo....",
        ".oTo....",
        ".oTo....",
        ".oTo....",
        ".oSo....",
        "..o.....",
    ],
    back_after="arm_far",
)

# ---------------------------------------------------------------- shield --
# Heater shield strapped to the akimbo arm. Front view: covers the far
# forearm (drawn after it). Back view: the shield is on the body's far
# side, so it draws BEHIND everything and only its rim peeks out.
PROPS["shield"] = {
    "front": {
        "anchor": (18, 16),
        "after": "arm_far",
        "grid": [
            ".oooooo.",
            "opPNNNMo",
            "opPNNNMo",
            "oPNKNNMo",   # gold boss
            "oPNNNNMo",
            ".oPNNMo.",
            ".oPNMo..",
            "..oNMo..",
            "...oo...",
        ],
    },
    "back": {
        "anchor": (2, 18),
        "after": None,
        "grid": [
            ".oooooo.",
            "oMNNNNMo",
            "oMNNNNMo",
            "oMNNNNMo",
            "oMNNNNMo",
            ".oMNNMo.",
            ".oMNMo..",
            "..oMMo..",
            "...oo...",
        ],
    },
}

# ------------------------------------------------- registration + hints --
composer.WEAPONS.update(PROPS)

# Recommended arm shifts per orientation so the hand tracks the grip.
# Front view moves the near (hanging) arm, back view the far one.
HINTS = {
    "broadsword_raised": {"front": {"arm_near": (2, -3)},
                          "back": {"arm_far": (1, -3)}},
    "broadsword_thrust": {"front": {"arm_near": (0, -2)},
                          "back": {"arm_far": (0, -2)}},
    "dagger_thrust": {"front": {"arm_near": (0, -2)},
                      "back": {"arm_far": (0, -2)}},
    "bow_nocked": {"front": {"arm_near": (-2, -2)},
                   "back": {"arm_far": (2, -2)}},
    "staff_raised": {"front": {"arm_near": (2, -3)},
                     "back": {"arm_far": (1, -3)}},
}


def hint(key, facing="SW"):
    """Recommended Pose.shift for a prop orientation (copy, safe to edit)."""
    view = "front" if facing in ("SW", "SE") else "back"
    return dict(HINTS.get(key, {}).get(view, {}))
