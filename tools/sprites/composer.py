"""Layered pixel rig for FFT-style character sprites.

A sprite frame is composed from named parts (grids of palette characters)
pasted at anchors onto a FRAME_W x FRAME_H canvas. A *pose* only moves,
hides, or augments parts -- it never plots pixels.

Facings:
    SW  toward camera (drawn)        SE  toward camera (mirror of SW)
    NW  away from camera (drawn)     NE  away from camera (mirror of NW)

Grid character legend (see CHARMAP). Every material ramp is 5 shades,
dark -> light:
    o outline   x eye        . transparent
    skin    0 1 2 3 9        hair    4 5 6 7 8
    tunic   a A B C c        pants   d D E F f
    boots   g G H I i        leather s S T U t
    accent  j J K L k        metal   m M N P p
    linen   q u v w e

Outlines are SELECTIVE: an 'o' pixel is resolved at render time to the
outline color of whichever material it touches (palette.outline_for), so
hair rims deep brown, pants rim dark navy, boots rim deep rust. Interior
separations between locks/folds are done with dark ramp steps, never 'o'.
"""

from dataclasses import dataclass, field
from PIL import Image

try:
    import palette
except ImportError:  # allow "from tools.sprites import composer"
    from . import palette

FRAME_W, FRAME_H = 32, 40

# char -> (material slot, ramp index 0..4). Slots are resolved per-character
# through CharacterSpec so recolors never touch the grids.
CHARMAP = {
    "0": ("skin", 0), "1": ("skin", 1), "2": ("skin", 2), "3": ("skin", 3), "9": ("skin", 4),
    "4": ("hair", 0), "5": ("hair", 1), "6": ("hair", 2), "7": ("hair", 3), "8": ("hair", 4),
    "a": ("tunic", 0), "A": ("tunic", 1), "B": ("tunic", 2), "C": ("tunic", 3), "c": ("tunic", 4),
    "d": ("pants", 0), "D": ("pants", 1), "E": ("pants", 2), "F": ("pants", 3), "f": ("pants", 4),
    "g": ("boots", 0), "G": ("boots", 1), "H": ("boots", 2), "I": ("boots", 3), "i": ("boots", 4),
    "s": ("leather", 0), "S": ("leather", 1), "T": ("leather", 2), "U": ("leather", 3), "t": ("leather", 4),
    "j": ("accent", 0), "J": ("accent", 1), "K": ("accent", 2), "L": ("accent", 3), "k": ("accent", 4),
    "m": ("metal", 0), "M": ("metal", 1), "N": ("metal", 2), "P": ("metal", 3), "p": ("metal", 4),
    "q": ("linen", 0), "u": ("linen", 1), "v": ("linen", 2), "w": ("linen", 3), "e": ("linen", 4),
}


@dataclass(frozen=True)
class CharacterSpec:
    """Maps material slots to palette ramp names."""
    skin: str = "skin"
    hair: str = "hair_gold"
    tunic: str = "cloth_blue"
    pants: str = "linen"
    boots: str = "boot_red"
    leather: str = "leather"
    accent: str = "accent"
    metal: str = "metal"
    linen: str = "linen"

    def color(self, char):
        if char == "x":
            return palette.EYE + (255,)
        slot, idx = CHARMAP[char]
        return palette.ramp(getattr(self, slot))[idx] + (255,)

    def outline(self, slot):
        if slot is None:
            return palette.OUTLINE + (255,)
        return palette.outline_for(getattr(self, slot)) + (255,)


DEFAULT_SPEC = CharacterSpec()

# ------------------------------------------------------------------ parts --
# Each part: {"anchor": (x, y), "grid": [row strings]}. Ragged rows are
# padded with '.'. Two drawn views: "front" (SW) and "back" (NW).
#
# Idle construction notes (kept deliberately asymmetric):
#   - screen-right shoulder sits 1px lower than the left
#   - front view: near (screen-left) arm hangs relaxed at the side with a
#     soft elbow bend; far arm is akimbo, fist planted ON the hip with a
#     1px negative-space window. Back view swaps them (same body turned).
#   - near leg is the weight leg (straight), far leg relaxes: knee shifts
#     1px inward and the pants sit a shade darker
#   - HAIR is 6-7 tapered spike clusters. Each cluster has its own mini
#     ramp read: 8 highlight on its upper-left face, 7/6 body, 5 on the
#     shaded side, and a '4' core-shadow seam where it overlaps the next
#     cluster. Silhouette tips are 1px points. No interior 'o' anywhere.

PARTS = {
    "front": {
        "hair": {
            "anchor": (6, 0),
            "grid": [
                ".........o.........",
                "...oo...o87o.......",
                "..o87o.o8876o.o7o..",
                ".o88774887764o776o.",
                "o8877748777647766o.",
                "o87776487766477650.".replace("0", "o"),
                "o877764877664676650".replace("0", "o"),
                "o77664777644767655o",
                "o7654877646654765o.",
                ".o765776646654765o.",
                ".o65o76o654o..o65o.",
                "..oo..4..4.....oo..",
            ],
        },
        "head": {
            "anchor": (11, 8),
            "grid": [
                "o1111111o",
                "o9933321o",
                "o9993321o",
                "o9x99x32o",
                "o9x99x32o",
                "o9999332o",
                ".o91332o.",
                "..o332o..",
            ],
        },
        "torso": {
            "anchor": (10, 15),
            "grid": [
                "....o22o....",
                ".occCBBBAo..",
                "ocCCBBBBAAao",
                "oCCBBBBBAAao",
                ".oCBBBBBAao.",
                ".oCBBBBAAao.",
                ".oCBBBAAAao.",
                ".oSTULSTSso.",
                ".oCBBBAAAao.",
                "oCBBBBBAAaao",
                ".oaAAAAAAao.",
            ],
        },
        # near arm: hangs relaxed, soft elbow bend, glove fist by the thigh.
        # Inner (torso-side) edge separates with dark tunic 'a', not outline.
        "arm_near": {
            "anchor": (7, 16),
            "grid": [
                ".occB.",
                "ocCBa.",
                "oCCBa.",
                "oCBBa.",
                "oCBa..",
                "oCBa..",
                ".oBAo.",
                ".oUTo.",
                ".oTSo.",
                "..oo..",
            ],
        },
        # far arm: akimbo, elbow out, fist planted on the hip
        "arm_far": {
            "anchor": (20, 17),
            "grid": [
                "aBAo..",
                "aBAAo.",
                ".oAAao",
                "..oAao",
                ".oUTo.",
                "oUTo..",
                "oTSo..",
                ".oo...",
            ],
        },
        "leg_near": {
            "anchor": (11, 23),
            "grid": [
                "ofFEo.",
                "ofFEo.",
                "oFFEo.",
                "oFEEo.",
                "oFEEo.",
                "oFEDo.",
                ".oEDo.",
                ".oEDo.",
                ".oIHo.",
                "oiIHGo",
                "oIIHGo",
                "oIHGGo",
                ".oooo.",
            ],
        },
        "leg_far": {
            "anchor": (16, 23),
            "grid": [
                "oEEDo.",
                "oEEDo.",
                "oEDDo.",
                "oEDDo.",
                ".oEDo.",
                ".oEDo.",
                ".oDDo.",
                ".oDdo.",
                ".oHGo.",
                ".oHGGo",
                ".oHHGo",
                ".oHGGo",
                "..oooo",
            ],
        },
    },
    "back": {
        # away-facing hair: flame-shaped mass of locks radiating from the
        # crown, split by '4' seams, tapering to pointed lock tips at the
        # nape. Crown highlight upper-left, core shadow at the neck.
        "hair": {
            "anchor": (6, 0),
            "grid": [
                ".........o.........",
                "...oo...o87o.......",
                "..o87o.o8876o.o7o..",
                ".o88774887764o776o.",
                "o8877748777647766o.",
                "o87776487766477650.".replace("0", "o"),
                "o87774777766647665o",
                "o7774777476664665o.",
                ".o764776466466465o.",
                ".o647664654654465o.",
                "..o54o765o654o65o..",
                "...o5o765o654o5o...",
                ".....o65o.o54o.....",
                "......o544o44o.....",
                ".......oo...o......",
            ],
        },
        "head": {
            "anchor": (13, 13),
            "grid": [
                ".o22o.",
                ".o32o.",
            ],
        },
        "torso": {
            "anchor": (10, 15),
            "grid": [
                "....o11o....",
                ".occBBBBAo..",
                "ocCBBBBBAAao",
                "oCBBABBBAAao",
                ".oCBABBBAao.",
                ".oCBABBAAao.",
                ".oCBABBAAao.",
                ".oSTSSSTSso.",
                ".oCBAABAAao.",
                "oCBBBBBAAaao",
                ".oaAAAAAAao.",
            ],
        },
        # back view: the akimbo arm is now on screen-left…
        "arm_near": {
            "anchor": (5, 17),
            "grid": [
                "..oCBa",
                ".oCCBa",
                "oCCBa.",
                "oCBo..",
                "oUTo..",
                ".oUTo.",
                ".oTSo.",
                "..oo..",
            ],
        },
        # …and the hanging arm on screen-right
        "arm_far": {
            "anchor": (21, 16),
            "grid": [
                "aBAo..",
                "aBAAo.",
                ".oBAo.",
                ".oBAo.",
                ".oAao.",
                ".oAao.",
                ".oTSo.",
                ".oSso.",
                "..oo..",
            ],
        },
        "leg_near": {
            "anchor": (11, 23),
            "grid": [
                "ofFEo.",
                "ofFEo.",
                "oFFEo.",
                "oFEEo.",
                "oFEEo.",
                "oFEDo.",
                ".oEDo.",
                ".oEDo.",
                ".oIHo.",
                "oIIHGo",
                "oIHHGo",
                "oIHGGo",
                ".oooo.",
            ],
        },
        "leg_far": {
            "anchor": (16, 23),
            "grid": [
                "oEEDo.",
                "oEEDo.",
                "oEDDo.",
                "oEDDo.",
                ".oEDo.",
                ".oEDo.",
                ".oDDo.",
                ".oDdo.",
                ".oHGo.",
                ".oHGGo",
                ".oHGGo",
                ".oGGGo",
                "..ooo.",
            ],
        },
    },
}

# Optional weapon layer: name -> per-view {"anchor", "grid", "after"} where
# "after" is the part it is drawn immediately after.
WEAPONS = {
    "sword": {
        "front": {
            "anchor": (7, 16),
            "after": "torso",
            "grid": [
                ".oPo.",
                ".oNPo",
                ".oNPo",
                ".oNPo",
                ".oNPo",
                "oMNMo",
                "..oSo",
                "..oTo",
            ],
        },
        "back": {
            "anchor": (7, 16),
            "after": "torso",
            "grid": [
                ".oPo.",
                ".oNPo",
                ".oNPo",
                ".oNPo",
                ".oNPo",
                "oMNMo",
                "..oSo",
                "..oTo",
            ],
        },
    },
}

# paint order, back to front
PART_ORDER = ["leg_far", "leg_near", "torso", "arm_far", "arm_near", "head", "hair"]

# group names usable in Pose.shift
GROUPS = {
    "all": list(PART_ORDER),
    "upper": ["torso", "arm_far", "arm_near", "head", "hair"],
    "head": ["head", "hair"],
    "arms": ["arm_far", "arm_near"],
    "legs": ["leg_far", "leg_near"],
}

FACINGS = ["SW", "SE", "NW", "NE"]
_VIEW = {"SW": ("front", False), "SE": ("front", True),
         "NW": ("back", False), "NE": ("back", True)}


@dataclass
class Pose:
    """A pose is data: per-part or per-group pixel shifts, hidden parts,
    and an optional weapon. Group shifts and part shifts add together."""
    shift: dict = field(default_factory=dict)   # name -> (dx, dy)
    hide: frozenset = frozenset()               # part names to skip
    weapon: str = None                          # key into WEAPONS


_NEIGHBORS = ((0, 1), (0, -1), (-1, 0), (1, 0),
              (1, 1), (-1, 1), (1, -1), (-1, -1))


def _part_image(part, spec):
    grid = part["grid"]
    w = max(len(r) for r in grid)
    h = len(grid)
    rows = [r.ljust(w, ".") for r in grid]
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "." or ch == "o":
                continue
            px[x, y] = spec.color(ch)
    # selective outlines: each 'o' takes the outline tint of the material
    # it touches (majority vote over the 8-neighborhood)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != "o":
                continue
            votes = {}
            for dx, dy in _NEIGHBORS:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    nc = rows[ny][nx]
                    if nc in CHARMAP:
                        slot = CHARMAP[nc][0]
                        votes[slot] = votes.get(slot, 0) + 1
            slot = max(votes, key=votes.get) if votes else None
            px[x, y] = spec.outline(slot)
    return img


def _total_shift(name, pose):
    dx = dy = 0
    for key, (sx, sy) in pose.shift.items():
        if key == name or name in GROUPS.get(key, ()):
            dx += sx
            dy += sy
    return dx, dy


def compose(facing, pose=None, spec=DEFAULT_SPEC):
    """Render one frame. Returns a FRAME_W x FRAME_H RGBA image."""
    pose = pose or Pose()
    view, mirrored = _VIEW[facing]
    canvas = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))

    weapon = WEAPONS.get(pose.weapon, {}).get(view) if pose.weapon else None

    def paste(entry, name):
        img = _part_image(entry, spec)
        ax, ay = entry["anchor"]
        dx, dy = _total_shift(name, pose)
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        layer.paste(img, (ax + dx, ay + dy), img)
        return Image.alpha_composite(canvas, layer)

    for name in PART_ORDER:
        if name in pose.hide:
            continue
        canvas = paste(PARTS[view][name], name)
        if weapon and weapon["after"] == name:
            canvas = paste(weapon, "weapon")

    if mirrored:
        canvas = canvas.transpose(Image.FLIP_LEFT_RIGHT)
    return canvas
