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
    # gear overlays: names into composer.OVERLAYS (see classes.py), drawn
    # on top of / instead of body parts. A class preset is just a spec.
    overlays: tuple = ()
    # optional eye RGB override (e.g. black mage glow); None = palette.EYE
    eye: tuple = None

    def color(self, char):
        if char == "x":
            return (self.eye or palette.EYE) + (255,)
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
        # FRONT HAIR -- 9 explicit wedge clusters (frame coords, col = x-6):
        #   C1 crown spike   base (13-17,4)  tip (16,0)   vertical, leans right
        #   C2 left spike    base ( 9-11,5)  tip ( 7,2)   45 deg up-left
        #   C3 right low     base (20-22,5)  tip (25,4)   near-horizontal right
        #   C4 right small   base (18-19,3)  tip (20,1)   short jab upward
        #   C5 fringe L      base y6         tip (12,10)  points down over brow
        #   C6 fringe M      base y6         tip (15, 9)  shortest notch
        #   C7 fringe R      base y6         tip (17,10)  sweeps to temple x19
        #   C8 side lock L   (9-10, 6)       tip ( 9,12)  LONG lock by the ear
        #   C9 side lock R   (20-21,6)       tip (20,10)  short -- unequal to C8
        # Silhouette tips land at y0/y1/y2/y4: four different heights, one
        # spike on the left vs two on the right = deliberate asymmetry.
        # Each wedge: 8 highlight upper-left face, 7/6 body, 5 shade,
        # '4' seam only along cluster boundaries (diagonal, staggered).
        "hair": {
            "anchor": (6, 0),
            "grid": [
                "..........o..........",  # y0  C1 tip
                ".........o8o..o......",  # y1  C1 neck; C4 tip
                ".o......o887476o.....",  # y2  C2 tip; C1 body; C4 wedge
                ".o876o.o8877476o.....",  # y3  C2 wedge / gap / C1+C4
                "..o87748877766547766o",  # y4  C2 base; crown; C3 spike->tip
                "..o8774877766654765o.",  # y5  crown full; C3 base
                "..o87488764776 56o...".replace(" ", "5"),  # y6 locks+fringe
                "..o76487764766465o...",  # y7  fringe solid over brow
                "..o65487647656565o...",  # y8  fringe solid, shade lower
                "..o65.876.765..54....",  # y9  1px notch gaps open
                "...5..5....5...4.....",  # y10 C5/C7/C9 tips touch brow
                "...5.................",  # y11 C8 continues alone
                "...4.................",  # y12 C8 tip (longest lock)
            ],
        },
        # Face: full-height FFT face -- hairline shadow row, two bright brow
        # rows, then 2x2 dark eyes on bright 9-skin, two jaw rows to a chin.
        "head": {
            "anchor": (11, 7),
            "grid": [
                "o9999321o",
                "o1111111o",
                "o9993321o",
                "o9993321o",
                "o9x99x32o",
                "o9x99x32o",
                "o9919332o",
                ".o93332o.",
                "..o332o..",
            ],
        },
        # contrapposto: screen-left shoulder caps a row early (right sits
        # 1px lower), and below the belt the hips swing 1px toward the
        # screen-left weight leg
        "torso": {
            "anchor": (10, 15),
            "grid": [
                "....o22o....",
                ".occCBBAo...",
                "ocCCBBBBAao.",
                "oCCBBBBBAAao",
                ".oCBBBBBAAo.",
                ".oCBBABBAao.",
                ".oCBBBAAAao.",
                ".oSTULSTSso.",
                "oCBBBAAAao..",
                "oCBBBBBAAo..",
                ".oaAAAAAao..",
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
        # far arm: akimbo, elbow out, fist planted on the hip (hangs off the
        # lowered screen-right shoulder, hence 1 row below arm_near)
        "arm_far": {
            "anchor": (20, 18),
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
        # relaxed leg: knee tucks 1px inward, shin angles back out, foot
        # planted a shade wider -- the counterpose to the straight near leg
        "leg_far": {
            "anchor": (16, 23),
            "grid": [
                "oEEDo..",
                "oEDDo..",
                ".oEDo..",
                ".oEDo..",
                ".oEDDo.",
                ".oEDDo.",
                "..oEDo.",
                "..oDdo.",
                "..oHGo.",
                "..oHGGo",
                ".oHHGGo",
                ".oHGGGo",
                "..ooooo",
            ],
        },
    },
    "back": {
        # BACK HAIR -- same skull turned 180 deg, so the top silhouette is
        # the front's mirrored (screen left/right swap) but RE-SHADED: light
        # stays upper-left in screen space. Clusters (frame coords):
        #   B1 crown spike   tip (15,0)   vertical (mirror of C1)
        #   B2 right long    tip (24,2)   45 deg up-right (mirror of C2)
        #   B3 left low      tip ( 6,4)   near-horizontal left (mirror of C3)
        #   B4 left small    tip (11,1)   short jab (mirror of C4)
        #   B5-B8 nape locks radiating from the crown whorl (15,4), split by
        #   diagonal '4' seams, tapering to UNEQUAL pointed tips:
        #   (10,11) (12,13) (15,12) (17,14) (19,12) (21,11) -- neck skin
        #   shows in the notches between tips (head part behind).
        "hair": {
            "anchor": (6, 0),
            "grid": [
                ".........o...........",  # y0  B1 tip
                ".....o..o8o..........",  # y1  B4 tip; B1 neck
                "....o876488o......o..",  # y2  B4 wedge; B1; B2 tip
                "....o87487770.o776o..".replace("0", "o"),  # y3
                "o87648877777654766o..",  # y4  B3 tip+wedge; crown; B2 base
                ".o8748777766654765o..",  # y5  crown full
                "..o877487776466565o..",  # y6  mass; seams radiate from crown
                "..o874776766646555o..",  # y7  left seam drifts in, right out
                "..o76476646656465o...",  # y8  seams keep drifting (no stripes)
                "..o6476654655545o....",  # y9  narrowing
                "...o46656545545o.....",  # y10
                "....o554.655.54......",  # y11 tips split; skin gaps open
                ".....54..54..5.......",  # y12 three nape locks stand
                "......4..4...4.......",  # y13 tips at x12 x15 x19
                ".............4.......",  # y14 lowest nape tip (x19)
            ],
        },
        # nape + narrow neck; skin shows only in notches between lock tips
        "head": {
            "anchor": (13, 11),
            "grid": [
                "o2221o",
                "o2221o",
                "o2221o",
                ".o21o.",
            ],
        },
        # same contrapposto read from behind: screen-right shoulder 1px
        # lower, hips swung 1px toward the screen-left weight leg
        "torso": {
            "anchor": (10, 15),
            "grid": [
                "....o11o....",
                ".occBBBAo...",
                "ocCBBBBBAao.",
                "oCBBABBBAAao",
                ".oCBABBBAAo.",
                ".oCBABBAAao.",
                ".oCBABBAAao.",
                ".oSTSSSTSso.",
                "oCBAABAAao..",
                "oCBBBBBAAo..",
                ".oaAAAAAao..",
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
        # …and the hanging arm on screen-right, off the lowered shoulder
        "arm_far": {
            "anchor": (21, 17),
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
        # relaxed leg from behind: same knee-in / calf-out counterpose
        "leg_far": {
            "anchor": (16, 23),
            "grid": [
                "oEEDo..",
                "oEDDo..",
                ".oEDo..",
                ".oEDo..",
                ".oEDDo.",
                ".oEDDo.",
                "..oEDo.",
                "..oDdo.",
                "..oHGo.",
                "..oHGGo",
                ".oHGGGo",
                ".oGGGGo",
                "..oooo.",
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

# ---------------------------------------------------------- registries ----
# Alternate body part sets, selectable via Pose(body=...). Extra bodies
# (kneel, prone) register themselves here on import -- see bodies.py.
BODIES = {"stand": PARTS}

# Gear overlays (helmets, hats, robe skirts, pauldrons...), activated per
# character via CharacterSpec.overlays. Populated by classes.py. Each entry:
#   name -> {"front"|"back": {"anchor", "grid", "after": part it is drawn
#            right after, "attach": part whose Pose shift it follows
#            (defaults to "after"), "replaces": optional part to suppress
#            (e.g. a helmet replaces "hair"), "bodies": body names it is
#            valid for (defaults to ("stand",))}}
OVERLAYS = {}

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
    an optional weapon (or tuple of weapons/props), and a body variant."""
    shift: dict = field(default_factory=dict)   # name -> (dx, dy)
    hide: frozenset = frozenset()               # part names to skip
    weapon: str = None                          # key into WEAPONS, or tuple
    body: str = "stand"                         # key into BODIES


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

    parts = BODIES[getattr(pose, "body", "stand")][view]
    body_name = getattr(pose, "body", "stand")

    # weapons / props: a single key or a tuple of keys into WEAPONS.
    wkeys = pose.weapon
    if wkeys is None:
        wkeys = ()
    elif isinstance(wkeys, str):
        wkeys = (wkeys,)
    weapons = [WEAPONS[k][view] for k in wkeys if view in WEAPONS[k]]

    # gear overlays from the character spec (helmets, skirts, pauldrons)
    overlays = []
    suppressed = set(pose.hide)
    for oname in getattr(spec, "overlays", ()):
        ov = OVERLAYS[oname].get(view)
        if not ov or body_name not in ov.get("bodies", ("stand",)):
            continue
        overlays.append(ov)
        if ov.get("replaces"):
            suppressed.add(ov["replaces"])

    def paste(entry, name):
        img = _part_image(entry, spec)
        ax, ay = entry["anchor"]
        dx, dy = _total_shift(name, pose)
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        layer.paste(img, (ax + dx, ay + dy), img)
        return Image.alpha_composite(canvas, layer)

    # props with after=None draw BEHIND every body layer (e.g. a shield
    # seen from the far side of the body)
    for w in weapons:
        if w["after"] is None:
            canvas = paste(w, "weapon")

    for name in PART_ORDER:
        if name not in suppressed and name in parts:
            canvas = paste(parts[name], name)
        # overlays draw right after their host part even if it is hidden,
        # so a helmet still lands when it *replaces* the hair
        for ov in overlays:
            if ov["after"] == name:
                canvas = paste(ov, ov.get("attach", name))
        for w in weapons:
            if w["after"] == name:
                canvas = paste(w, "weapon")

    if mirrored:
        canvas = canvas.transpose(Image.FLIP_LEFT_RIGHT)
    return canvas
