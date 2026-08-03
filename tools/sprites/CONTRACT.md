# Sprite pipeline contract

FFT-style character sprites, built procedurally from a layered part rig.
Everything below is the stable API. Do not change frame size, facing order,
sheet layout, or the `Pose` fields without updating every consumer.

## Frame + sheet format

- Frame canvas: **32x40** px, RGBA, transparent background.
- Facings, always in this order: **SW, SE, NW, NE** (SW/SE face the camera,
  NW/NE face away; SE and NE are automatic mirrors — never draw them).
- Raw sheet `out/sprites/<anim>.png`: one **row per facing** (4 rows),
  one **column per frame**, 32x40 cells, no padding.
- Preview `out/preview/<anim>_4x.png`: labeled 4x nearest-neighbor contact
  sheet for eyeballing. Never shipped to the game.

## Adding a new animation (the whole job)

1. Create `tools/sprites/anims/<name>.py`:

   ```python
   from composer import Pose
   import props, bodies    # only if the anim uses props / body variants

   NAME = "<name>"
   FRAME_MS = 140            # per-frame duration hint

   def frames():             # -> list[Pose], one per frame
       return [
           Pose(),                                   # rest
           Pose(shift={"arms": (0, -1)}),            # move parts...
           Pose(shift={"arm_near": (-2, -3)},        # ...or one part
                weapon="broadsword"),
           Pose(hide=frozenset({"arm_far"})),        # or hide parts
           Pose(body="kneel"),                       # or swap the body
       ]
   ```

2. Build and eyeball it:

   ```
   python3 tools/sprites/build.py <name>
   ```

   Writes `out/sprites/<name>.png` + `out/preview/<name>_4x.png`.
   Also run `python3 tools/sprites/build.py --base` for the 4-facing still.

That is the entire surface area. A pose is *data*: pixel shifts, hidden
parts, an optional weapon. No pose ever plots pixels.

## Pose API (composer.py)

```python
Pose(shift={}, hide=frozenset(), weapon=None, body="stand")
compose(facing, pose=None, spec=DEFAULT_SPEC) -> 32x40 RGBA Image
```

- `shift`: `{part_or_group: (dx, dy)}` in pixels (+x right, +y down).
  Group and part shifts on the same part **add**.
- Parts: `leg_far, leg_near, torso, arm_far, arm_near, head, hair`
  (painted in that back-to-front order; `weapon` is a pseudo-part).
- Groups: `all, upper (torso+arms+head+hair), head (head+hair), arms, legs`.
- `weapon`: key into `composer.WEAPONS` — a string or a **tuple** of them
  (e.g. `("broadsword", "shield")`). `props.py` registers the armory on
  import; see below. Weapon entries are per-view `anchor`, `grid`, and
  `after` (the part they draw right after; `after=None` draws BEHIND the
  whole body). Shift a held prop with `shift={"weapon": (dx, dy)}`.
- `body`: key into `composer.BODIES` — `"stand"` (default), `"kneel"`,
  `"prone"` (registered by `bodies.py`). All parts/groups/hide/shift work
  identically on every body.
- "near" parts sit on the left of the drawn (SW/NW) views; mirrored
  facings swap them visually — that is correct FFT behavior.

Keep shifts small (1-3 px). The idle bob is `shift={"upper": (0, 1)}` —
that scale of movement is what reads well at 32x40.

## Props (props.py)

`import props` registers the armory into `composer.WEAPONS`:

| prop | orientations |
|---|---|
| `broadsword` | idle, `_raised` (windup), `_thrust` (stab) |
| `dagger` | idle, `_thrust` |
| `bow` | idle, `_nocked` (drawn, arrow level) |
| `staff` | idle (planted), `_raised` (cast) |
| `shield` | idle (strapped to the akimbo arm) |

Grips pass through the held hand: front view near fist `(8-9, 23-24)`,
back view far fist `(23-24, 23-24)`. Idle blades draw in front of the
arm; the back-view shield draws behind the whole body (`after=None`).
Orientations that move the hand ship a recommended arm shift:
`props.hint(key, facing)` returns a dict to merge into `Pose.shift`,
e.g. `Pose(weapon="bow_nocked", shift=props.hint("bow_nocked", "SW"))`.
When animating on a non-stand body, move the pseudo-part along:
`Pose(body="kneel", weapon="broadsword", shift={"weapon": (0, 6)})`.

## Body variants (bodies.py)

`import bodies` registers `kneel` and `prone` into `composer.BODIES`.

- `kneel`: critical / low-HP crouch. Reuses the standing hair/head/
  torso/arm grids **by reference** ~6px lower (art polish flows through);
  only the legs are new. Hands sit 6px lower than standing.
- `prone`: lying flat, head screen-left, one arm flung past the head —
  the FFT death slump. Front = face-up with closed eyes, back =
  face-down under splayed hair. Same seven part names, so per-part
  shifts still work (e.g. twitch `arm_near` for a death flourish).

## Classes & gear (classes.py)

A class is just a `CharacterSpec`: material-slot palette swaps plus
`overlays=(...)` — names into `composer.OVERLAYS` (helmet, hat_wizard,
hood, headband, pads_metal, pads_leather, robe_skirt). `import classes`
registers the overlays and exposes `classes.CLASSES` with presets:
`squire, knight, black_mage, white_mage, archer`.

```python
compose("SW", pose, spec=classes.CLASSES["knight"])
```

Overlay entries are per-view `anchor`/`grid` plus `after` (host part),
`attach` (part whose shift it follows, default = after), optional
`replaces` (part it suppresses — helmets replace `hair`), and `bodies`
(bodies it renders on, default `("stand",)` — so gear silently drops
off on kneel/prone until kneel-anchored variants are drawn).
`CharacterSpec.eye` overrides the eye RGB (black mage glow). New ramps
live at the bottom of `palette.py` (`steel_blue, cloth_navy, shadow,
straw`) — add more there, never edit the base ramps.

Check your work: `python3 tools/sprites/build.py --demo` writes
`out/preview/infra_demo_4x.png` — every prop in both drawn views, the
body variants, and all class presets.

## The idle rest pose is the anatomy baseline

The drawn rest pose is deliberately asymmetric — keep new animations
relative to it, do not "straighten" it:

- screen-right shoulder is 1px lower than the left;
- front view: the near (screen-left) arm hangs relaxed with a soft elbow
  bend, fist by the thigh; the far arm is akimbo — elbow out, fist planted
  ON the hip with a 1px negative-space window between forearm and waist;
- back view swaps the arms (it is the same body turned 180°): akimbo on
  screen-left, hanging on screen-right;
- the near leg is the straight weight leg, the far leg relaxes (knee 1px
  in, pants a shade darker).

## Editing the art itself (rarely needed)

- Part pixel grids live in `composer.PARTS["front"|"back"]` as strings;
  the character legend is at the top of `composer.py`. `o` = outline,
  `x` = eye, `.` = transparent; each material has 5 chars, dark -> light
  (e.g. hair `4 5 6 7 8`, skin `0 1 2 3 9`, tunic `a A B C c`).
- **Outlines are selective**: an `o` pixel is resolved at render time to
  `palette.outline_for(<material it touches>)` — hair rims deep brown,
  pants rim dark navy, boots rim deep rust. Never expect one global line
  color. Interior separations (arm against torso, folds, lock partings)
  use the material's darkest ramp char (`a`, `4`, `d`…), **not** `o`.
- Colors live in `palette.py` as **5-shade dark->light ramps** sampled from
  the reference sheet. Ramps hue-shift (shadows cool/teal or deep brown,
  lights warm toward amber). Never use pure black anywhere.
- Recolors (new characters/jobs) need **no grid edits**: pass a
  `CharacterSpec` to `compose`, e.g.
  `CharacterSpec(hair="hair_brown", tunic="cloth_red")`.

## Style rules (match the reference, public/images/dgnudjp-*.png)

- Head + hair ≈ 40-44% of total height; figure ≈ 36px tall, ≤21px wide.
- 4-5 shades visible per material + selective tinted outline; light source
  upper-left (left side gets the `c`/`9`/`8` highlights). Step through
  adjacent ramp indices at transitions (buffer pixels) — never jump 0→3.
- No pure black, no oversaturation, no pillow-shading.
- **Hair is 6-7 tapered spike clusters, never a blob.** Each cluster gets
  its own 4-step read: `8` highlight on its upper-left face, `7`/`6` body,
  `5` shaded rim, and a thin `4` core-shadow seam where it overlaps the
  next cluster. Seams run diagonally along cluster boundaries only —
  scattered darks read as dither noise, evenly spaced seams read as
  stripes. Silhouette tips are 1px points; fringe covers the forehead to
  just above the eyes with pointed notches. The away view is a flame-shaped
  mass of locks radiating from the crown to pointed nape tips — it must
  show the same cluster treatment, not one undifferentiated mass.
- Faces: bright skin base (`9`) with `3`/`2` side shading, a full `1`
  shadow row under the hairline, 1px dark blue `x` eyes 2px tall.
- Asymmetry keeps poses alive: never mirror left/right limbs exactly.
