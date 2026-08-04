# Sprite Sheet Bake-off — Gemini 2.5 Flash Image vs gpt-image-1

Identical brief, references, and pose guides (see tools/genai/bakeoff.py).
Blind-judged (random A/B labels) by a fresh-context critic against the FFT reference bar.

- Sheet A = bake_gemini.png -> 7/10. All 8 poses present in FFT-faithful style; shipped 12 cells instead of 8, walk-cycle selection ambiguous, facing commitment soft, faint grid lines.
- Sheet B = bake_openai.png -> 3/10. Perfect 2x4 layout and margins, but no broadsword in the attack cell, spellcast rendered as a facepalm, flinch as a sky-point, heavy uniform near-black outlines off-style.

WINNER: Gemini (decisive). Gemini's misses are packaging (crop/reorder/regenerate select cells); gpt-image-1's are content (missing prop, wrong poses, off-style outlines).
