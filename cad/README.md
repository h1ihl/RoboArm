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
├── equations.txt     global variables, exported from SolidWorks — import into every new part
├── parts/            individual part files (.SLDPRT)
├── assemblies/        sub- and top-level assemblies (.SLDASM)
└── exports/           STEP/STL exports for printing and sharing
```

## Global parameters (one equations/variables file, referenced everywhere)

`equations.txt` is the exported copy of this table. Import it
(Tools > Equations > Import) into each new part; when a value changes,
change it once, re-export, and re-import into existing parts.

| Parameter | Symbol | Default (Config B) |
|---|---|---:|
| Shoulder height | `h0` | 75 mm |
| Upper arm length | `L1` | 120 mm |
| Forearm length | `L2` | 120 mm |
| Wrist→TCP length | `L3` | 75 mm |
| Link plate thickness | `t_link` | 3 mm |
| Link plate depth (bending direction) | `w_link` | 20 mm — matches the deflection calc in `calculations/engineering_calcs.py` |
| Twin-plate gap | `w_gap` | 20 mm — provisional, set by the elbow servo mount design |
| Servo output boss diameter | `d_boss` | 13 mm — from the downloaded MG996R model, verify with calipers |
| Boss radial clearance | `c_boss` | 1 mm |
| Plate hole for servo boss | `d_servo_hole` | `d_boss` + 2 × `c_boss` = 15 mm |
| Min rim around servo hole | `t_rim` | 9.5 mm — holds an M3 hole with about 3 mm of material on each side (7.5 mm was too little) |
| Link plate end width (servo end) | `w_link_end` | `d_servo_hole` + 2 × `t_rim` = 34 mm |
| M3 bolt clearance hole | `d_hole_m3` | `d_pin_gripper` + `c_fit` = 3.2 mm |
| M4 pivot hole (pin rotates) | `d_hole_pivot` | `d_pin` + `c_fit_pivot` = 4.25 mm |
| Horn disc diameter / thickness | `d_horn` / `t_horn` | 20 / 2.3 mm — from the MG996R model (circular horn) |
| Horn disc to plate 2 gap | `g_horn` | 2.2 mm — from MockShoulder |
| Adapter horn pocket | `d_horn_pocket` / `h_horn_pocket` | `d_horn` + `c_fit` = 20.2 / `g_horn` + `t_horn` = 4.5 mm |
| Horn centre-screw recess | `d_horn_screw_cb` / `h_horn_screw_cb` | 8.5 / 2.6 mm |
| Adapter diameter / length | `d_adapter` / `h_adapter` | 26 mm / `w_gap` = 20 mm |
| Adapter floor under horn | `t_adapter_floor` | 2 mm |
| Horn screw hole / radius | `d_horn_screw_hole` / `r_horn_screw` | 2.2 / 7 mm (M2 self-tappers, ≤6 mm) |
| Horn screw access bore | `d_access` | 4 mm, from the plate-1 side |
| M3 heat-set insert hole | `d_insert_m3` / `h_insert_m3` | 4.2 / 6 mm — check the insert maker's spec |
| Adapter bolt offset from pin | `x_adapter_bolt` / `y_adapter_bolt` | 6 mm along the arm, ±5 mm across |
| Plate 1 countersink (M3 flat head) | `d_csk_m3` | 6.4 mm, 90° |
| M4 pin depth in adapter | `h_pin_bore` | 10 mm |
| MG996R case length / width | `l_servo` / `w_servo` | 40.9 / 20 mm — from the model, without ears |
| Shaft to short / long end of case | `r_servo_short` / `r_servo_long` | 10 / `l_servo` − `r_servo_short` = 30.9 mm |
| MG996R ear hole spacing | `l_ear_holes` / `w_ear_holes` | 51 mm along × 15 mm across — from the model |
| Ear seating face to plate-2 outer face | `a_ear` | 8.4 mm — from MockShoulder |
| Bracket window clearance | `c_win` | 0.3 mm per side — starting value, tune after a test print |
| Bracket wall A window | `l_window` / `w_window` | `l_servo` + 2 × `c_win` = 41.5 / `w_servo` + 2 × `c_win` = 20.6 mm |
| Gap behind wall A to plate 2 | `g_wall_a` | `a_ear` − `t_bracket` = 4.4 mm — ear screw heads sit here |
| Plate 1 to wall B | `g_wall_b` | 1 mm — thrust washer |
| Shoulder axis to turret face | `d_axis_turret` | 34 mm — **placeholder** until the turret is designed |
| Bracket foot thickness / width | `t_foot` / `w_foot` | 6 / 50 mm |
| Wall A top above the axis | `h_wall_top` | 41.5 mm — long-end ear holes + 4 mm |
| Bracket wall width (A and B) | `w_wall` | 30 mm |
| Wall B pin boss | `t_boss_b` / `d_boss_b` | 4 mm extra thickness / Ø12 mm |

Bracket layout and dimensions: `docs/shoulder_bracket.svg`. As built in
`shoulder_bracket.SLDPRT`: foot 60 × 50 × 6 mm (overhangs wall A by 10.6 and
wall B by 10), 4 × Ø4.2 M3 insert holes on a 52 × 40 mm pattern, 4 mm from
each end of the foot; R4 fillets where the walls meet the foot.

The horn adapter bolts to plate 1 (the pin-side plate at the shoulder), not plate
2: the servo case sits 0.5 mm off plate 2 and plate 2 turns under it, so no bolt
head fits there. Layout and assembly order: `docs/horn_adapter.svg`.
| Bracket thickness | `t_bracket` | 4 mm |
| Pin diameter | `d_pin` | 4 mm (M4) |
| Gripper pivot pin diameter | `d_pin_gripper` | 3 mm (M3) |
| Nominal clearance | `c_fit` | 0.2 mm — **measured**, PLA (see below) |
| Gripper pivot clearance | `c_fit_pivot` | `c_fit` + 0.05 mm = 0.25 mm — chosen, not coupon-verified for free spin |

`c_fit` was confirmed with the tolerance coupon on 2026-10-01: Prusa
Core One, Prusament PLA, 0.4 mm nozzle, 0.2 mm layers — +0.20 mm gave the
best snug fit on both the M4 and M3 hole rows. PETG is still untested;
re-run the coupon in PETG before printing PETG parts (brackets, jaws, horn
adapters) and add a separate `c_fit_petg` if it lands somewhere else.
`c_fit_pivot` is the free-rotation clearance for the gripper jaw pins,
set to 0.25 mm (`c_fit` + 0.05 mm) — a chosen value between the snug 0.2 mm
fit and the original 0.3 mm estimate. Check a pin for free spin in the
printed 3.25 mm coupon hole before relying on it.

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
| Ballast block | 1 | `parts/ballast_block.SLDPRT` | Milled mild steel, not printed — size the cavity pocket to this part once it's cut (`docs/mechanical_design.md` §Ballast); bolt or press-fit, don't leave it loose |
| Column | 1 | `parts/column.SLDPRT` | Carries the two 608ZZ bearings |
| Turret | 1 | `parts/turret.SLDPRT` | Bolts to base-servo horn |
| Shoulder bracket | 1 | `parts/shoulder_bracket.SLDPRT` | Print flat — see mechanical_design.md rule 1. FEA candidate. |
| Elbow bracket | 1 | `parts/elbow_bracket.SLDPRT` | Print flat, same rule. |
| Upper-arm side plate | 2 | `parts/upper_arm_plate.SLDPRT` | Twin-plate box section; symmetric, so one part printed twice. Spec below. |
| Forearm side plate | 2 | `parts/forearm_plate.SLDPRT` | Save As from the upper-arm plate, `L1` → `L2`; keep as a separate file so Config-A-Short (`L2 = 80 mm`) works |
| Link spacers | 4 per link | `parts/upper_arm_spacer.SLDPRT` | Tube: Ø7 mm OD, bore `d_hole_m3`, length `w_gap`. Same part serves the forearm while its gap equals `w_gap`. Print standing up; M3×30 bolts with plain nuts (M3×35 with nyloc) |
| Servo-horn adapter | 3 | `parts/upper_arm_horn_adapter.SLDPRT` (shoulder) | Ø26 × 20 collar in the plate gap; horn screws in from below, 2 × M3 heat-set inserts take countersunk screws through plate 1. Layout: `docs/horn_adapter.svg`. Never a printed spline |
| Wrist mounting face | 1 | `parts/wrist_face.SLDPRT` | Common 24×24 mm interface — fixed bracket / SG90 slave / future linkage all mount here |
| Fixed wrist bracket | 1 (alt.) | `parts/wrist_fixed.SLDPRT` | Configuration-A fallback |
| Gripper jaw | 2 | `parts/gripper_jaw.SLDPRT` | Mirror pair, meshed gear sectors, compliant tip |
| Gripper drive link | 1 | `parts/gripper_link.SLDPRT` | |
| Cable clip | qty as needed | `parts/cable_clip.SLDPRT` | Unloaded, PLA, print in whatever's on the machine |

### Link side plate spec (upper arm; forearm identical with `L2`)

- Profile: `w_link` (20 mm) deep slot, both ends rounded at radius
  `w_link / 2`, concentric with the pivot holes. Overall ≈ 140 × 20 mm
  at `L1 = 120 mm`.
- Thickness `t_link` (3 mm), printed flat, hole axes normal to the bed.
- Two pivot holes, diameter `d_pin + c_fit` (4.2 mm), centre-to-centre
  `L1` — all driven from variables, nothing typed in.
- A few spacer-bolt holes along the plate; the gap between the twin
  plates is `w_gap`, which the servo mount design drives.
- Symmetric profile so one file prints twice with no mirrored copy.
- Check: print one plate, pass an M4 bolt through both pivot holes and
  caliper the centre distance — 120 ± 0.2 mm.

## Configurations to define in the top-level assembly

| Configuration | `L2` | Notes |
|---|---:|---|
| `Config-A-Short` | 80 mm | Fallback geometry — see `docs/requirements.md` trigger conditions |
| `Config-B-Standard` | 120 mm | Default — matches the numbers throughout `docs/` |

## Before printing anything

Done for PLA (see Global parameters above). For PETG parts, print the
tolerance coupon described in `docs/mechanical_design.md` in PETG and
confirm `c_fit = 0.2 mm` is actually right for that material before
committing it globally.
