"""Color ramps for FFT-style sprites.

Every ramp is 5 shades ordered dark -> light, sampled from the reference
sheet (public/images/dgnudjp-*.png). Ramps hue-shift: shadows go cool/teal
or deep warm brown, lights warm toward amber. No pure black anywhere.
OUTLINE is the reference's exact dark warm (40, 40, 32).
"""

# ---------------------------------------------------------------- ramps ----
# index:        0 deep shadow   1 shadow      2 mid           3 light         4 highlight
RAMPS = {
    # warm peach skin (ref mid 200,128,88 / light 248,184,144)
    "skin":       [(100, 56, 40), (150, 88, 58), (200, 128, 88), (226, 158, 116), (248, 188, 146)],
    # golden blond hair (ref 104,64,24 / 160,96,40 / 232,168,72 / 248,208,120)
    "hair_gold":  [(88, 52, 20), (126, 76, 30), (170, 108, 44), (226, 164, 72), (250, 210, 124)],
    # chestnut brown hair (alt)
    "hair_brown": [(52, 32, 22), (88, 54, 34), (128, 82, 50), (170, 118, 72), (210, 162, 108)],
    # saturated warm blue cloth (ref pants 32,48,56 / 56,64,88 / 72,80,112
    # pushed one saturation step like the hqdefault battle blues). Shadows
    # stay warm -- the deep step leans violet-brown (red ~ green), mids and
    # lights carry a clear blue identity without going neon.
    "cloth_blue": [(46, 42, 62), (62, 62, 102), (80, 90, 140), (106, 120, 174), (146, 156, 206)],
    # muted warm red cloth
    "cloth_red":  [(70, 28, 24), (112, 40, 30), (156, 58, 36), (198, 94, 54), (228, 142, 94)],
    # moss green cloth
    "cloth_green": [(34, 48, 32), (54, 74, 42), (82, 104, 54), (118, 138, 74), (160, 176, 108)],
    # warm brown leather (belts, gloves)
    "leather":    [(56, 34, 20), (92, 56, 28), (134, 86, 44), (178, 124, 68), (216, 168, 108)],
    # hot rust boot/glove leather (ref 96,40,16 / 152,48,16 / 192,88,24)
    "boot_red":   [(74, 30, 14), (112, 42, 16), (152, 50, 16), (194, 90, 26), (226, 138, 66)],
    # warm grey metal (ref pauldron 80,64,48 / 136,120,96 / 224,200,168)
    "metal":      [(62, 52, 42), (98, 82, 64), (136, 120, 96), (180, 164, 136), (226, 202, 170)],
    # warm off-white linen (shirts, trousers)
    "linen":      [(104, 84, 64), (146, 122, 92), (184, 158, 122), (216, 192, 154), (244, 228, 196)],
    # gold accent (buckles, trim)
    "accent":     [(112, 64, 20), (158, 98, 30), (202, 138, 46), (234, 178, 76), (250, 214, 128)],
}

# dark warm outline -- never pure black (ref uses 40,40,32). This is only
# the *fallback*: real outlines are selective, derived per material via
# outline_for() so hair edges are deep brown, pants edges dark navy, etc.
OUTLINE = (40, 40, 32)


def outline_for(name):
    """Selective outline color for a material: its darkest ramp step pushed
    ~45% darker. Stays hue-tinted (FFT never uses one global black line)."""
    r, g, b = RAMPS[name][0]
    return (int(r * 0.55), int(g * 0.55), int(b * 0.55))
# eye pixel: dark blue-teal like the reference's big eye marks (32,48,56)
EYE = (32, 44, 58)
# ground / preview background, sampled from reference sheet background
PREVIEW_BG = (169, 162, 133)


def ramp(name):
    """Return the 5-shade ramp (dark -> light) for a named material."""
    return RAMPS[name]


# ------------------------------------------------------- added ramps -------
# Class-variant ramps (knight steel, mage robes...). Registered here at the
# end of the file, additively, so parallel edits to the base ramps above
# merge cleanly. Same rules: 5 shades dark -> light, hue-shifted shadows,
# no pure black.
RAMPS["steel_blue"] = [  # knight plate: cool steel, warm-drifting highlight
    (44, 50, 66), (72, 84, 106), (106, 122, 148), (150, 168, 192), (204, 216, 232)]
RAMPS["cloth_navy"] = [  # black-mage robe: deep indigo, sepia-shifted darks
    (36, 32, 50), (50, 48, 74), (68, 68, 102), (92, 96, 134), (124, 130, 168)]
RAMPS["shadow"] = [      # black-mage face-in-shadow "skin"
    (26, 26, 42), (36, 38, 58), (48, 52, 76), (62, 68, 96), (80, 88, 118)]
RAMPS["straw"] = [       # wizard-hat straw / pale gold, drier than accent
    (110, 78, 34), (150, 112, 48), (190, 150, 70), (220, 184, 100), (244, 216, 142)]
