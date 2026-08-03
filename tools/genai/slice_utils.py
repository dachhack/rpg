#!/usr/bin/env python3
"""Consistency probe: one Gemini call -> 4-frame walk strip -> slice, normalize, gif."""
import base64, json, os, ssl, urllib.request
from pathlib import Path
from PIL import Image

SCRATCH = Path(__file__).parent
REPO = Path("/home/user/rpg")
REF_SHEET = REPO / "public/images/dgnudjp-6322d794-f22f-4521-9329-bf015b08c1ea.png"
CHAR_REF = SCRATCH / "gen_raw.png"  # smoke-test character = identity anchor

API_KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-2.5-flash-image"

PROMPT = """Create a pixel art sprite sheet strip: a 4-frame WALKING animation cycle of the EXACT character shown in the second reference image (same spiky blond hair shape, same blue tunic, same belt, same cream pants, same rust-orange boots, same proportions, same scale in every frame).

Style must match the first reference image: tactical RPG sprite sheet, chibi proportions, soft warm palette, selective dark-warm outlines, crisp square pixels.

The character walks toward the viewer's lower-left at the tactical RPG three-quarter top-down angle. The 4 frames left to right: (1) right foot forward mid-stride, (2) feet passing under body, (3) left foot forward mid-stride, (4) feet passing under body. Arms swing opposite to legs, subtle 1-pixel body bob on passing frames.

Rules: exactly 4 full-body sprites in ONE horizontal row, evenly spaced with clear gaps, identical character in every frame, plain solid bright green background (#00FF00), no anti-aliasing, no text, no grid lines, no shadows."""


def call_gemini():
    def b64(p):
        return base64.b64encode(Path(p).read_bytes()).decode()
    body = {"contents": [{"parts": [
        {"text": PROMPT},
        {"inline_data": {"mime_type": "image/png", "data": b64(REF_SHEET)}},
        {"inline_data": {"mime_type": "image/png", "data": b64(CHAR_REF)}},
    ]}]}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": API_KEY})
    ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
    with urllib.request.urlopen(req, context=ctx, timeout=180) as r:
        resp = json.load(r)
    for part in resp["candidates"][0]["content"]["parts"]:
        if "inlineData" in part:
            return base64.b64decode(part["inlineData"]["data"])
    raise RuntimeError(f"no image: {json.dumps(resp)[:400]}")


def key_out(img):
    rgb = img.convert("RGB")
    px = rgb.load()
    corners = [px[0, 0], px[rgb.width - 1, 0], px[0, rgb.height - 1], px[rgb.width - 1, rgb.height - 1]]
    key = max(set(corners), key=corners.count)
    rgba = rgb.convert("RGBA")
    pa = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            if sum((a - b) ** 2 for a, b in zip(pa[x, y][:3], key)) < 60 ** 2:
                pa[x, y] = (0, 0, 0, 0)
    return rgba


def slice_strip(rgba):
    """Split a horizontal strip into cells via empty-column gaps."""
    alpha = rgba.getchannel("A")
    W, H = rgba.size
    col_has = [False] * W
    ap = alpha.load()
    for x in range(W):
        for y in range(H):
            if ap[x, y] > 32:
                col_has[x] = True
                break
    cells, start = [], None
    for x, has in enumerate(col_has + [False]):
        if has and start is None:
            start = x
        elif not has and start is not None:
            if x - start > 8:  # ignore specks
                cells.append((start, x))
            start = None
    out = []
    for x0, x1 in cells:
        cell = rgba.crop((x0, 0, x1, H))
        bbox = cell.getbbox()
        out.append(cell.crop(bbox))
    return out


def normalize(cells, w=32, h=40):
    """Shared scale, bottom-center anchor, shared 16-color palette."""
    scale = min(min(w / c.width, h / c.height) for c in cells)
    small = [c.resize((max(1, round(c.width * scale)), max(1, round(c.height * scale))), Image.NEAREST) for c in cells]
    # shared palette: quantize all frames together
    total_w = sum(s.width for s in small)
    strip = Image.new("RGB", (total_w, h), (0, 255, 0))
    x = 0
    for s in small:
        strip.paste(s.convert("RGB"), (x, h - s.height), s.getchannel("A").point(lambda a: 255 if a > 128 else 0))
        x += s.width
    q = strip.quantize(17, method=Image.MEDIANCUT).convert("RGB")
    frames, x = [], 0
    for s in small:
        f = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ox, oy = (w - s.width) // 2, h - s.height
        for yy in range(s.height):
            for xx in range(s.width):
                if s.getpixel((xx, yy))[3] > 128:
                    f.putpixel((ox + xx, oy + yy), (*q.getpixel((x + xx, h - s.height + yy)), 255))
        frames.append(f)
        x += s.width
    return frames


def main():
    raw = call_gemini()
    (SCRATCH / "probe_raw.png").write_bytes(raw)
    print(f"got {len(raw)//1024} KB strip")

    rgba = key_out(Image.open(SCRATCH / "probe_raw.png"))
    cells = slice_strip(rgba)
    print(f"sliced {len(cells)} cells: {[c.size for c in cells]}")
    frames = normalize(cells)

    BG = (139, 133, 108, 255)
    S = 8
    sheet = Image.new("RGBA", (len(frames) * (32 * S + 8) + 8, 40 * S + 16), BG)
    gif_frames = []
    for i, f in enumerate(frames):
        big = f.resize((32 * S, 40 * S), Image.NEAREST)
        sheet.alpha_composite(big, (8 + i * (32 * S + 8), 8))
        gf = Image.new("RGBA", (32 * S, 40 * S), BG)
        gf.alpha_composite(big)
        gif_frames.append(gf.convert("P", palette=Image.ADAPTIVE))
    sheet.convert("RGB").save(SCRATCH / "probe_frames_8x.png")
    if len(gif_frames) > 1:
        gif_frames[0].save(SCRATCH / "probe_walk_8x.gif", save_all=True,
                           append_images=gif_frames[1:], duration=140, loop=0, disposal=2)
    print("wrote probe_raw.png, probe_frames_8x.png, probe_walk_8x.gif")


if __name__ == "__main__":
    main()
