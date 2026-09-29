# Mechanical design

## Geometry

Equal-length links: `L₁ = L₂ = 120 mm`. Deliberate, not arbitrary — equal
lengths (a) make the printed parts nearly identical, so it's one parametric
sketch with two configurations rather than two separate designs, (b)
maximise the folded-to-extended reach ratio, and (c) put the workspace's
inner boundary where the turret already is instead of leaving dead space.
`h₀ = 75 mm` (shoulder height) is the minimum that lets the elbow fold
without hitting the turret; `L₃ = 75 mm` (wrist→TCP) covers jaw depth plus
clearance to grip a 30 mm object. Every dimension traces back to the torque
budget in `docs/actuator_selection.md` — none were picked for looks.

| Parameter | Value |
|---|---|
| Shoulder height h₀ | 75 mm |
| Upper arm L₁ | 120 mm |
| Forearm L₂ | 120 mm |
| Wrist→TCP L₃ | 75 mm |
| Max TCP reach | 315 mm |
| Base footprint | 180 × 180 mm |
| Jaw opening | 0–55 mm |

## Structure: twin side plates

Links are two printed side plates on printed spacers — a box section that's
stiff in bending, prints flat with no supports, and puts every bolt in
double shear. Roughly 14 unique parts / 20 printed pieces / ~300 g of
filament / 18–22 h print time total for the arm.

## Material assignment

| Part | Material | Why |
|---|---|---|
| Base plate, column, turret | PLA | Stiffness and flatness; nothing here is impact-loaded |
| Upper arm, forearm links | PLA | E ≈ 3.5 GPa vs. PETG's 2.0 — 75% stiffer per section; deflection is what matters in a link |
| Shoulder and elbow brackets | PETG | Highest bending stress in the machine, and bending is where poor layer adhesion shows up first |
| Servo horn adapters | PETG | Small, bolted, loaded in a direction that wants to peel layers apart |
| Gripper jaws | PETG | Designed to flex (see compliant tip, actuator_selection.md); PLA would snap at the flex section |
| Spacers, clips, tray | PLA | Unloaded — print in whatever's on the machine |
| Ballast block | Mild steel, milled | Not printed — see Ballast below |

## Ballast

A solid milled block, not loose fill (sand, washers, etc.) — a fixed,
known mass at a fixed position matches the stability calc's assumption
exactly, and doesn't shift the CoM as the base rotates the way loose fill
can.

**Mild steel, ~50–55 cm³ for the 400 g target** (density ≈ 7.85 g/cm³):
a 60 × 60 × 15 mm block is ≈424 g, comfortably clearing the minimum with
margin to spare for the mass the stability calc doesn't otherwise account
for (hardware, wiring, ballast-cavity lid). Steel over aluminium here
specifically for the footprint: at the same mass, aluminium
(≈2.70 g/cm³) needs ~3× the volume, and the ballast cavity is already
competing for space with the column and base-servo mount inside the
180 × 180 mm base. Weigh the actual cut block before final install and
trim (or pick a slightly larger blank) to clear 400 g — mild steel density
varies enough between alloys (7.75–7.87 g/cm³) that this is a
measure-don't-assume step, consistent with the rest of this project's
philosophy on anything safety-factor-adjacent.

**Bolt or press-fit it into the cavity** — don't let it sit loose. A block
free to slide during the base's rotation defeats the fixed-CoM assumption
above, and turns a designed-in stability margin into an unmeasured one.

Design the ballast cavity pocket to the block's actual milled dimensions
once cut, not the other way around — CAD (Phase 2) hasn't started yet, so
there's no existing pocket geometry to retrofit.

Print settings throughout: 0.4 mm nozzle, 0.2 mm layers, **4 perimeters**,
30% gyroid infill, 5 top/bottom layers. Perimeter count dominates strength in
a thin printed part — 4 walls at 20% infill beats 2 walls at 60%, and weighs
less.

## Layer orientation — the three rules that decide whether this works

1. **Print brackets flat, never standing up.** A shoulder bracket printed
   upright has its layer planes perpendicular to the bending stress, so the
   load tries to peel layers apart — roughly 40–60% of in-plane strength.
   Printed flat, the same stress runs along continuous extrusions instead.
2. **Every bolt hole axis is normal to the build plate.** Bolts then clamp
   *across* layers in compression, which printed plastic handles well,
   instead of trying to split them apart.
3. **Never print a servo spline.** A printed 25-tooth spline will round off —
   not might, will. Bolt the metal horn that came with the servo to the
   printed part with 2–3 M2 screws and let the horn take the torque. This is
   the single most common failure mode in printed arms, and it's designed
   out from part one rather than discovered after a reprint.

## Where SolidWorks Simulation earns its time — and where it doesn't

**Worth running (2 studies):**
- **Shoulder bracket** — 0.44 N·m through a bolted interface with a stress
  concentration at the servo cutout. The one part where intuition is
  unreliable.
- **Upper-arm link** — check the elbow-servo pocket; expect the answer to be
  "add a 3 mm fillet."

**Not worth running:** everything else. The hand calculation below already
answers the question, and running FEA on a part that's obviously fine just
burns an afternoon.

```
Upper-arm tip deflection, 1.3 N at 120 mm, twin 20 × 3 mm plates:
  I = 2 × (3 × 20³)/12 = 4000 mm⁴
  δ = FL³/(3EI) = 1.3 × 120³ / (3 × 2500 × 4000) = 0.075 mm
```

**Seventy-five microns.** The structure is ~80× stiffer than the servo
backlash it's bolted to (see `docs/kinematics.md` — repeatability is
backlash-limited to ±5–8 mm). **Do not thicken these links.** Every gram
added buys nothing measurable and costs shoulder safety factor directly —
this is the one place in the project where "more robust" would make the
robot objectively worse.

If FEA is run on either study, use orthotropic material properties (printed
plastic is not isotropic) and treat the result as a comparison between two
design variants, not an absolute number.

## Parametric strategy for SolidWorks

- **One global variable/equations file** driving `L1`, `L2`, `L3`, `h0`,
  plate thickness and pin diameter across every part.
- **A servo-pocket library feature with a two-row design table** — standard
  (MG996R: 40.7 × 19.7 × 42.9 mm body, 49.5 mm mounting-ear span) and micro
  (MG90S/SG90: 22.8 × 12.2 × 22.5 mm, 32 mm span). Every servo mount
  references it, so swapping an MG996R for an MG90S is a configuration
  change, not a redesign. This is what makes Configurations A–D one robot
  instead of four (brief §28).
- **Assembly mated to reference planes and axes**, never face-to-face
  between links, so changing `L1` rebuilds the assembly instead of
  erroring it out.
- **Configurations**: `Config-A-Short` (`L2 = 80 mm`) and
  `Config-B-Standard` (`L2 = 120 mm`) from the same part files.
- **0.2 mm nominal clearance** on every pin and pocket. Print a tolerance
  coupon first (a small test part with a few pin/hole pairs at different
  clearances) and adjust once, globally, via the variables file — cheaper
  than reprinting full parts to find the right fit.

## Suggested file layout (see `cad/README.md`)

```
cad/
├── parts/            individual SolidWorks part files (.SLDPRT)
├── assemblies/        sub- and top-level assemblies (.SLDASM)
└── exports/           STEP/STL exports for printing and sharing
```

No SolidWorks files exist yet — Phase 2 (Mechanical design) starts here.
`cad/README.md` has the part list, naming convention and design-table spec
to build against.
