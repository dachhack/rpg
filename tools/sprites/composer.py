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
        # FRONT HAIR -- ONE heavy mass swept screen-right, built from
        # overlapping tapered spikes (frame coords, col = x-6):
        #   W4 DOMINANT blade  root (18,4) -> tip (25,3)  long swept spike,
        #                      ~30%+ longer than every other spike; grows out
        #                      of the mass over a '4' root crease, never a gap
        #   P1 twin peak       base (11-13,3) -> tip (12,0) tallest, leans left
        #   P2 twin peak       base (15-17,3) -> tip (15,1) '4' seam splits P1/P2
        #   jabs               left tip (9,2), right tip (17,1) -- unequal
        #   fringe             solid y7-8, notches y9, tips y10 over the brow
        #   side locks         left (10, ->12) LONG, right (18, ->10) short
        # The mass is SOLID from y3 down -- sky notches only nick the top
        # two rows, so it reads as one swept mound, not separated tufts.
        # Clustered '4' warm-brown root cores converge on the crown along
        # y4-y6. The dominant tip lands far right while the tallest peak
        # sits left of center: the top silhouette is strongly directional,
        # so SW and its SE mirror read as two different crowns.
        # Each spike: 8 highlight upper-left face, 7/6 body, 5 shade,
        # '4' seam only along cluster boundaries (diagonal, staggered).
        "hair": {
            "anchor": (6, 0),
            "grid": [
                "......o..............",  # y0  P1 twin-peak tip
                ".....o8o.o.o.........",  # y1  P1 neck; P2 tip; jab tip
                "...o.8874877o........",  # y2  left jab tip; P1+P2 chunky wedges
                "..o8788747765457766o.",  # y3  mass closes; W4 blade grows out of
                                          #     the mass over a '4' root crease
                "..o87787466567766o...",  # y4  ONE heavy mass; W4 blade underside
                "..o774776645665o.....",  # y5  '4' root cores converge on crown
                "..o47764665455o......",  # y6  dark warm roots over the fringe
                "...o6766465545o......",  # y7  fringe solid over brow
                "...o566545544o.......",  # y8  fringe shaded lower
                "...o5.65.54.4o.......",  # y9  1px notch gaps open
                "....5..5..4.4........",  # y10 fringe tips + short right lock
                "....5................",  # y11 left side lock continues alone
                "....4................",  # y12 left lock tip (longest)
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
        # near arm: hangs relaxed and CLOSE to the body -- a straight drop
        # with a soft elbow tuck, glove fist low by the thigh. Deliberately
        # narrow so it cannot read as a second akimbo arm (the far arm owns
        # that shape). Inner edge separates with dark tunic 'a', not outline.
        "arm_near": {
            "anchor": (8, 16),
            "grid": [
                ".occ.",
                "ocCa.",
                "oCBa.",
                "oCBa.",
                ".oCa.",
                ".oBa.",
                ".oAo.",
                ".oUTo",
                ".oTSo",
                "..oo.",
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
        # planted a shade wider -- the counterpose to the straight near leg.
        # Anchored 1px wider and 1px higher than the weight leg: the far
        # foot rests a step back in iso space, so the stance never mirrors.
        "leg_far": {
            "anchor": (17, 22),
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
        # BACK HAIR -- same skull turned 180 deg: the swept mass now points
        # screen-LEFT (the front sweeps screen-right), RE-SHADED so light
        # stays upper-left in screen space. Spikes (frame coords):
        #   W4' DOMINANT blade root (11,4) -> tip (6,3)   long swept spike,
        #                      merged over a '4' root crease like the front
        #   P1' twin peak      base (18-20,3) -> tip (19,0) tallest, off-center
        #   P2' twin peak      base (14-16,3) -> tip (16,1) '4' seam splits them
        #   jabs               right tip (22,2), left tip (14,1) -- unequal
        #   nape locks radiating from the crown whorl, split by diagonal '4'
        #   seams, solid to y10, tapering to UNEQUAL pointed tips at
        #   (12,12) (15,13) (19,12) -- neck skin shows in the notches
        #   (head part behind). '4' root cores cluster along y4-y6 exactly
        #   like the front so both views read as the same single mass.
        "hair": {
            "anchor": (6, 0),
            "grid": [
                ".............o.......",  # y0  P1' twin-peak tip (off-center)
                "........o.o.o8o......",  # y1  jab tip; P2' tip; P1' neck
                ".......o8764886.o....",  # y2  P2'+P1' chunky wedges; right jab tip
                "o8776547776488765o...",  # y3  W4' blade grows out of the mass
                                          #     over a '4' root crease, tip far L
                "..o87776566477665o...",  # y4  ONE heavy mass; W4' blade underside
                "....o877466566455o...",  # y5  '4' root cores converge on crown
                ".....o76466545554o...",  # y6  seams radiate from the whorl
                "......o645645545o....",  # y7  seams drift (no stripes)
                ".....o546554545o.....",  # y8  narrowing nape, still one mass
                ".....o55465445o......",  # y9
                "......o5455454o......",  # y10 hugs the skull to the collar
                "......54.54.44.......",  # y11 skin notches open
                "......4..5...4.......",  # y12 nape locks stand, unequal
                ".........4...........",  # y13 lowest nape tip (x15)
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
        # relaxed leg from behind: same knee-in / calf-out counterpose,
        # same 1px wider / 1px higher stagger as the front view
        "leg_far": {
            "anchor": (17, 22),
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
