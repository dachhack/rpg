"""Render out/sprites/<anim>.png into an animated 4x preview GIF.

Usage: python3 tools/sprites/make_gif.py <anim>

Reads the raw sheet (4 facing rows x N frame columns of FRAME_W x FRAME_H),
lays the 4 facings side by side per frame, upscales 4x nearest-neighbor,
and writes out/preview/<anim>_4x.gif looping at the animation's FRAME_MS.
"""
import importlib
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "sprites"))

FRAME_W, FRAME_H = 32, 40
FACINGS = 4
SCALE = 4
GAP = 8
BG = (139, 133, 108, 255)  # matches preview contact sheets


def main(name: str) -> None:
    mod = importlib.import_module(f"anims.{name}")
    frame_ms = getattr(mod, "FRAME_MS", 180)

    sheet = Image.open(ROOT / "out" / "sprites" / f"{name}.png").convert("RGBA")
    n_frames = sheet.width // FRAME_W

    frames = []
    for f in range(n_frames):
        w = FACINGS * FRAME_W + (FACINGS - 1) * GAP // SCALE
        canvas = Image.new("RGBA", (w, FRAME_H), BG)
        for row in range(FACINGS):
            cell = sheet.crop((f * FRAME_W, row * FRAME_H, (f + 1) * FRAME_W, (row + 1) * FRAME_H))
            canvas.alpha_composite(cell, (row * (FRAME_W + GAP // SCALE), 0))
        canvas = canvas.resize((canvas.width * SCALE, canvas.height * SCALE), Image.NEAREST)
        frames.append(canvas.convert("P", palette=Image.ADAPTIVE))

    durations = frame_ms if isinstance(frame_ms, int) else list(frame_ms)
    out = ROOT / "out" / "preview" / f"{name}_4x.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=durations, loop=0, disposal=2)
    print(f"wrote {out} ({n_frames} frames)")


if __name__ == "__main__":
    main(sys.argv[1])
