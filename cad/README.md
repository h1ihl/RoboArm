# CAD

No SolidWorks files exist yet — Phase 2 (Mechanical design) starts here.
SolidWorks files are proprietary binary formats this tool can't author, so
this folder currently documents the structure and naming convention to
build against, per `docs/mechanical_design.md`'s parametric strategy. Add
real `.SLDPRT` / `.SLDASM` files as they're modelled; keep this README's
part list in sync as the source of truth for what should exist.

## Layout

```
cad/
├── parts/            individual part files (.SLDPRT)
├── assemblies/        sub- and top-level assemblies (.SLDASM)
└── exports/           STEP/STL exports for printing and sharing
```

## Global parameters (one equations/variables file, referenced everywhere)

| Parameter | Symbol | Default (Config B) |
|---|---|---:|
| Shoulder height | `h0` | 75 mm |
| Upper arm length | `L1` | 120 mm |
| Forearm length | `L2` | 120 mm |
| Wrist→TCP length | `L3` | 75 mm |
| Link plate thickness | `t_link` | 3 mm |
| Bracket thickness | `t_bracket` | 4 mm |
| Pin diameter | `d_pin` | 4 mm (M4) |
| Nominal clearance | `c_fit` | 0.2 mm |

## Servo-pocket library feature (two-row design table)

| Row | Body (mm) | Mounting-ear span | Servos |
|---|---|---:|---|
| `standard` | 40.7 × 19.7 × 42.9 | 49.5 mm | MG996R, MG995, DS3218 |
| `micro` | 22.8 × 12.2 × 22.5 | 32 mm | MG90S, SG90, MG92B |

Every servo mount part references this feature and picks a row — swapping
an MG996R for an MG90S (or vice versa, per the fallback configurations in
`docs/requirements.md`) is then a design-table row change, not a redesign.

## Part list (target — Configuration B)

| Part | Qty | File (suggested) | Notes |
|---|---:|---|---|
| Base plate | 1 | `parts/base_plate.SLDPRT` | Includes ballast cavity + snap-lid feature, camera-mast mounting bosses for V2 |
| Ballast cavity lid | 1 | `parts/ballast_lid.SLDPRT` | Snap-fit |
| Column | 1 | `parts/column.SLDPRT` | Carries the two 608ZZ bearings |
| Turret | 1 | `parts/turret.SLDPRT` | Bolts to base-servo horn |
| Shoulder bracket | 1 | `parts/shoulder_bracket.SLDPRT` | Print flat — see mechanical_design.md rule 1. FEA candidate. |
| Elbow bracket | 1 | `parts/elbow_bracket.SLDPRT` | Print flat, same rule. |
| Upper-arm side plate | 2 | `parts/upper_arm_plate.SLDPRT` | Mirror pair; twin-plate box section |
| Forearm side plate | 2 | `parts/forearm_plate.SLDPRT` | Mirror pair; identical profile to upper-arm at `L2=L1` |
| Link spacers | qty per BOM | `parts/link_spacer.SLDPRT` | Parametric length |
| Servo-horn adapter | 3 | `parts/horn_adapter.SLDPRT` | Bolts to the servo's metal horn — never a printed spline |
| Wrist mounting face | 1 | `parts/wrist_face.SLDPRT` | Common 24×24 mm interface — fixed bracket / SG90 slave / future linkage all mount here |
| Fixed wrist bracket | 1 (alt.) | `parts/wrist_fixed.SLDPRT` | Configuration-A fallback |
| Gripper jaw | 2 | `parts/gripper_jaw.SLDPRT` | Mirror pair, meshed gear sectors, compliant tip |
| Gripper drive link | 1 | `parts/gripper_link.SLDPRT` | |
| Cable clip | qty as needed | `parts/cable_clip.SLDPRT` | Unloaded, PLA, print in whatever's on the machine |

## Configurations to define in the top-level assembly

| Configuration | `L2` | Notes |
|---|---:|---|
| `Config-A-Short` | 80 mm | Fallback geometry — see `docs/requirements.md` trigger conditions |
| `Config-B-Standard` | 120 mm | Default — matches the numbers throughout `docs/` |

## Before printing anything

Print the tolerance coupon described in `docs/mechanical_design.md` and
confirm `c_fit = 0.2 mm` is actually right for your printer before
committing it globally.
