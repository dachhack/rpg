"""Sprite sheet builder.

Usage:
    python3 tools/sprites/build.py <anim>     # e.g. idle
    python3 tools/sprites/build.py --base     # 4-facing still of the idle pose
    python3 tools/sprites/build.py --demo     # props/bodies/classes contact sheet

Outputs (relative to repo root):
    out/sprites/<anim>.png       raw sheet: one row per facing (SW,SE,NW,NE),
                                 frames left to right, 32x40 cells, transparent bg
    out/preview/<anim>_4x.png    labeled 4x nearest-neighbor contact sheet
    out/preview/base_4x.png      (--base) idle frame 0 in all 4 facings
    out/preview/infra_demo_4x.png (--demo) every prop both drawn views,
                                 kneel/prone bodies, all class presets
"""

import importlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parent.parent

import composer  # noqa: E402
import palette   # noqa: E402

FW, FH = composer.FRAME_W, composer.FRAME_H


def load_anim(name):
    return importlib.import_module(f"anims.{name}")


def build_sheet(anim):
    poses = anim.frames()
    sheet = Image.new("RGBA", (FW * len(poses), FH * len(composer.FACINGS)),
                      (0, 0, 0, 0))
    for row, facing in enumerate(composer.FACINGS):
        for col, pose in enumerate(poses):
            sheet.paste(composer.compose(facing, pose), (col * FW, row * FH))
    return sheet, poses


def preview(sheet, n_frames, title, scale=4, pad=6):
    """Nearest-neighbor upscale on the reference-toned background,
    with facing labels down the left edge."""
    label_w = 26
    w = label_w + n_frames * FW * scale + pad * 2
    h = len(composer.FACINGS) * FH * scale + pad * 2 + 14
    img = Image.new("RGB", (w, h), palette.PREVIEW_BG)
    big = sheet.resize((sheet.width * scale, sheet.height * scale),
                       Image.NEAREST)
    img.paste(big, (label_w + pad, pad + 14), big)
    d = ImageDraw.Draw(img)
    d.text((pad, 2), title, fill=(60, 55, 40))
    for i, facing in enumerate(composer.FACINGS):
        d.text((pad, pad + 14 + i * FH * scale + FH * scale // 2 - 4),
               facing, fill=(60, 55, 40))
    return img


def build_base(scale=4, pad=6):
    """Idle rest pose, all 4 facings side by side."""
    img = Image.new("RGB",
                    (pad * 2 + 4 * FW * scale, pad * 2 + FH * scale + 14),
                    palette.PREVIEW_BG)
    d = ImageDraw.Draw(img)
    for i, facing in enumerate(composer.FACINGS):
        frame = composer.compose(facing)
        big = frame.resize((FW * scale, FH * scale), Image.NEAREST)
        img.paste(big, (pad + i * FW * scale, pad + 14), big)
        d.text((pad + i * FW * scale + 4, 2), facing, fill=(60, 55, 40))
    return img


def build_demo(scale=4, pad=8):
    """Infrastructure demo sheet: every prop in both drawn facings, the
    kneel/prone body variants, and the five class presets."""
    import props    # noqa: F401  registers WEAPONS
    import bodies   # noqa: F401  registers BODIES
    import classes  # registers OVERLAYS + CLASSES

    Pose = composer.Pose

    def wcell(key, facing):
        return (key, facing,
                composer.Pose(weapon=key, shift=props.hint(key, facing)),
                composer.DEFAULT_SPEC)

    prop_keys = ["broadsword", "broadsword_raised", "broadsword_thrust",
                 "dagger", "dagger_thrust", "bow", "bow_nocked",
                 "staff", "staff_raised", "shield"]

    sections = [
        ("props, front (SW)", [wcell(k, "SW") for k in prop_keys]),
        ("props, back (NW)", [wcell(k, "NW") for k in prop_keys]),
        ("body variants", [
            ("kneel SW", "SW", Pose(body="kneel"), composer.DEFAULT_SPEC),
            ("kneel NW", "NW", Pose(body="kneel"), composer.DEFAULT_SPEC),
            ("prone SW", "SW", Pose(body="prone"), composer.DEFAULT_SPEC),
            ("prone NW", "NW", Pose(body="prone"), composer.DEFAULT_SPEC),
            ("kneel+sword", "SW",
             Pose(body="kneel", weapon="broadsword",
                  shift={"weapon": (0, 6)}),
             composer.DEFAULT_SPEC),
        ]),
        ("class presets, idle (SW)", [
            (name, "SW", Pose(), spec)
            for name, spec in classes.CLASSES.items()
        ]),
    ]

    cw, ch = FW * scale, FH * scale
    label_h = 12
    head_h = 14
    n_cols = max(len(cells) for _, cells in sections)
    w = pad * 2 + n_cols * (cw + pad)
    h = pad + sum(head_h + ch + label_h + pad for _ in sections)
    img = Image.new("RGB", (w, h), palette.PREVIEW_BG)
    d = ImageDraw.Draw(img)

    y = pad
    for title, cells in sections:
        d.text((pad, y), title, fill=(60, 55, 40))
        y += head_h
        for i, (label, facing, pose, spec) in enumerate(cells):
            x = pad + i * (cw + pad)
            frame = composer.compose(facing, pose, spec)
            big = frame.resize((cw, ch), Image.NEAREST)
            img.paste(big, (x, y), big)
            d.text((x + 1, y + ch), label, fill=(60, 55, 40))
        y += ch + label_h + pad
    return img


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    out_sprites = ROOT / "out" / "sprites"
    out_preview = ROOT / "out" / "preview"
    out_sprites.mkdir(parents=True, exist_ok=True)
    out_preview.mkdir(parents=True, exist_ok=True)

    if sys.argv[1] == "--demo":
        path = out_preview / "infra_demo_4x.png"
        build_demo().save(path)
        print(f"wrote {path}")
        return

    if sys.argv[1] == "--base":
        path = out_preview / "base_4x.png"
        build_base().save(path)
        print(f"wrote {path}")
        return

    name = sys.argv[1]
    anim = load_anim(name)
    sheet, poses = build_sheet(anim)
    raw = out_sprites / f"{name}.png"
    sheet.save(raw)
    pv = out_preview / f"{name}_4x.png"
    preview(sheet, len(poses), f"{name}  ({len(poses)} frames x 4 facings, "
            f"{FW}x{FH})").save(pv)
    print(f"wrote {raw}")
    print(f"wrote {pv}")


if __name__ == "__main__":
    main()
