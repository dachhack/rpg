#!/usr/bin/env python3
"""Bake-off: Gemini vs gpt-image-1 on the same 8-cell sprite sheet task.

Same prompt, same 3 reference images (FFT style sheet, identity anchor, pose guides).
Usage: python3 bakeoff.py [gemini|openai|both]
"""
import base64, json, os, ssl, subprocess, sys, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw

SCRATCH = Path(__file__).resolve().parents[2] / "out" / "genai"
REPO = Path("/home/user/rpg")
REF_SHEET = REPO / "public/images/dgnudjp-6322d794-f22f-4521-9329-bf015b08c1ea.png"
CHAR_REF = Path(__file__).parent / "refs" / "identity.png"
GUIDES = SCRATCH / "bakeoff_guides.png"

CELL_W, CELL_H, LINE = 200, 360, 7

PROMPT = """Create a pixel art sprite sheet: 8 sprites of the EXACT character shown in the second reference image (same spiky blond hair, blue tunic with brown suspenders and belt, cream pants, rust-orange boots, same chibi proportions, same scale in all 8 sprites). Ignore that reference's standing pose.

Style must match the first reference image: tactical RPG sprite sheet, chibi proportions with the head about one third of total height, soft warm palette, selective dark-warm outlines, crisp square pixels.

Layout: 2 rows x 4 columns, evenly spaced with clear green gaps. The third reference image is a stick-figure pose guide with the same 2x4 layout — match each figure's limb positions precisely, one sprite per guide cell, same order.

ROW 1 — walk cycle, character walking toward the viewer's lower-left at a tactical RPG three-quarter top-down angle, face, both eyes and both boot toes toward the viewer's lower-left in ALL FOUR frames: (1) right leg planted forward mid-stride, left arm swinging forward; (2) feet passing under the body, body slightly higher; (3) left leg planted forward mid-stride, right arm swinging forward; (4) passing again, arms slightly different from frame 2.

ROW 2 — action poses, same facing (three-quarter toward viewer's lower-left): (5) relaxed battle idle, weight on one leg; (6) melee attack: broadsword swung overhead mid-strike, body leaning into the blow; (7) spellcast: both arms raised above the head, palms open, chanting; (8) damage flinch: body recoiling backward, arms thrown up, hair swept forward.

Rules: exactly 8 full-body sprites, plain solid bright green background (#00FF00), every sprite fully inside its cell with green margins on all sides, no anti-aliasing, no blur, no text, no grid lines, no shadows, no stick figures in the output."""


def draw_pose(d, ox, oy, arms, legs, bob=0):
    cx = ox + CELL_W // 2
    head_c = (cx, oy + 80 + bob)
    d.ellipse([head_c[0] - 48, head_c[1] - 48, head_c[0] + 48, head_c[1] + 48], outline="black", width=LINE)
    sh = (cx, oy + 140 + bob)
    hip = (cx, oy + 225 + bob)
    d.line([sh, hip], fill="black", width=LINE)
    for (hx, hy) in arms:
        d.line([sh, (cx + hx, sh[1] + hy)], fill="black", width=LINE)
    for (knee, foot) in legs:
        d.line([hip, (cx + knee[0], hip[1] + knee[1])], fill="black", width=LINE)
        d.line([(cx + knee[0], hip[1] + knee[1]), (cx + foot[0], hip[1] + foot[1])], fill="black", width=LINE)


def make_guides():
    img = Image.new("RGB", (CELL_W * 4, CELL_H * 2), "white")
    d = ImageDraw.Draw(img)
    for i in range(1, 4):
        d.line([(CELL_W * i, 0), (CELL_W * i, CELL_H * 2)], fill=(200, 200, 200), width=2)
    d.line([(0, CELL_H), (CELL_W * 4, CELL_H)], fill=(200, 200, 200), width=2)
    # row 1: walk
    draw_pose(d, 0, 0, arms=[(-42, 55), (40, 60)], legs=[((-25, 55), (-42, 108)), ((22, 50), (40, 100))])
    draw_pose(d, CELL_W, 0, arms=[(-30, 65), (30, 65)], legs=[((-8, 55), (-10, 105)), ((10, 52), (8, 100))], bob=-8)
    draw_pose(d, CELL_W * 2, 0, arms=[(40, 55), (-42, 60)], legs=[((25, 55), (42, 108)), ((-22, 50), (-40, 100))])
    draw_pose(d, CELL_W * 3, 0, arms=[(-25, 68), (25, 68)], legs=[((-8, 55), (-10, 105)), ((10, 52), (8, 100))], bob=-8)
    # row 2: idle, attack overhead, cast arms-up, flinch
    draw_pose(d, 0, CELL_H, arms=[(-35, 62), (32, 64)], legs=[((-14, 55), (-18, 105)), ((14, 53), (18, 103))])
    draw_pose(d, CELL_W, CELL_H, arms=[(-30, 62), (55, -70)], legs=[((-20, 55), (-35, 105)), ((18, 52), (32, 100))])
    draw_pose(d, CELL_W * 2, CELL_H, arms=[(-48, -75), (48, -75)], legs=[((-12, 55), (-14, 105)), ((12, 53), (14, 103))])
    draw_pose(d, CELL_W * 3, CELL_H, arms=[(-45, -20), (-38, -35)], legs=[((20, 55), (35, 106)), ((-15, 50), (-28, 98))])
    img.save(GUIDES)


def b64(p):
    return base64.b64encode(Path(p).read_bytes()).decode()


def call_gemini(out_path):
    body = {"contents": [{"parts": [
        {"text": PROMPT},
        {"inline_data": {"mime_type": "image/png", "data": b64(REF_SHEET)}},
        {"inline_data": {"mime_type": "image/png", "data": b64(CHAR_REF)}},
        {"inline_data": {"mime_type": "image/png", "data": b64(GUIDES)}},
    ]}]}
    req = urllib.request.Request(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"]})
    ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
    with urllib.request.urlopen(req, context=ctx, timeout=240) as r:
        resp = json.load(r)
    for part in resp["candidates"][0]["content"]["parts"]:
        if "inlineData" in part:
            Path(out_path).write_bytes(base64.b64decode(part["inlineData"]["data"]))
            return
    raise RuntimeError(f"gemini: no image: {json.dumps(resp)[:400]}")


def call_openai(out_path):
    # gpt-image-1 edits endpoint: reference images + prompt, landscape, high quality
    cmd = [
        "curl", "-sS", "https://api.openai.com/v1/images/edits",
        "-H", f"Authorization: Bearer {os.environ['OPENAI_API_KEY']}",
        "-F", "model=gpt-image-1",
        "-F", f"image[]=@{REF_SHEET}",
        "-F", f"image[]=@{CHAR_REF}",
        "-F", f"image[]=@{GUIDES}",
        "-F", f"prompt={PROMPT}",
        "-F", "size=1536x1024",
        "-F", "quality=high",
        "-F", "n=1",
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    resp = json.loads(out.stdout)
    if "error" in resp:
        raise RuntimeError(f"openai: {resp['error']}")
    Path(out_path).write_bytes(base64.b64decode(resp["data"][0]["b64_json"]))


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    make_guides()
    if which in ("gemini", "both"):
        print("calling gemini ...")
        call_gemini(SCRATCH / "bake_gemini.png")
        print("  wrote bake_gemini.png")
    if which in ("openai", "both"):
        print("calling gpt-image-1 ...")
        call_openai(SCRATCH / "bake_openai.png")
        print("  wrote bake_openai.png")


if __name__ == "__main__":
    main()
