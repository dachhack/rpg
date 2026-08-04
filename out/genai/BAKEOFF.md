# Sprite-sheet bake-off: Gemini 2.5 Flash Image vs gpt-image-1

Identical brief for both models (`tools/genai/bakeoff.py`): 8 sprites of the blond
FFT-style character in a 2×4 grid on solid green — a 4-frame lower-left walk cycle
plus idle / overhead sword attack / spellcast / damage flinch — with the same three
reference images (FFT style sheet, identity anchor, stick-figure pose guides).

Judged blind by a fresh-context critic: sheets labeled A/B at random, references
attached, model names withheld until after scoring.

## Verdict: Gemini wins, 6/10 vs 2/10

| | Gemini (`bake_gemini.png`, Sheet A) | gpt-image-1 (`bake_openai.png`, Sheet B) |
|---|---|---|
| Score | **6/10** | **2/10** |
| Grid | 3×4 (12 cells — 4 extra) | 2×3 (6 cells — 2 missing) |
| Coverage | All 8 briefed poses present | No sword attack; walk cycle absent |
| Biggest gap | Ignored the 2×4 spec: a redundant middle row of idle-fidget frames and a mushy walk cycle whose phases barely differ — needs surgery, not just cropping | Only delivered six of eight sprites and omitted the sword attack entirely, so the sheet cannot be completed by cropping |

**Gemini** — strong identity consistency across all cells; the action row (overhead
sword, arms-up spellcast with flourish, backward flinch) lands close to brief; crisp
pixels and selective outlines. Held back by the off-spec 12-cell layout, near-duplicate
walk phases with chest-clasped arms instead of counter-swing, soft drop shadows
smearing into the green, and a front-facing spellcast.

**gpt-image-1** — actually the closest palette/outline match to the reference bar
(chunky warm golds, muted blue tunic, confident dark-brown selective outlines), but
it failed the brief structurally: six near-identical standing/mime poses, no walk
phases, no attack, wobbly cell and pixel sizes with upscaling blur that would make
clean crops and palette-keying painful.

**Critic's rationale:** Gemini over-delivers cells where gpt-image-1 under-delivers
poses — Gemini is salvageable with cropping and shadow cleanup; gpt-image-1 would
need a third of the sheet regenerated before it could even be evaluated as an
animation set.
