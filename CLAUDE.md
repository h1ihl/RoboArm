# CLAUDE.md — Desk Arm project handoff

Read this first. It records what has been decided, what exists, how to work
in this repo, and what comes next. Last updated 2026-10-23.

The owner is Haseeb (GitHub `h1ihl`), an engineering student at the
University of Calgary, with access to the Schulich makerspace (3D printers,
a mill he is trained on, a PCB mill). The repo is **public**:
https://github.com/h1ihl/RoboArm

---

## 1. What the project is

A small, cheap tabletop robot arm. The original brief is
`desktop_robot_arm_claude_prompt.md` — read it for the spirit: **low cost,
simple, actually buildable, no scope creep**. Budget target CAD $50–70,
hard cap $100.

- **V1** (current): 3-DOF arm — base yaw, shoulder pitch, elbow pitch — plus
  a two-finger gripper and an SG90 wrist servo slaved in firmware to keep the
  jaws level. PC → USB → ESP32 → servos.
- **V2** (not started): camera + vision + AI agent calling the same Python
  API. A separate, unscoped "payload upgrade" track (DC gearmotors +
  planetary gearboxes + encoders) is recorded in `docs/v2_ai_roadmap.md`.

Configuration B (the chosen one): reach 315 mm, payload 55 g,
`h0` 75 / `L1` 120 / `L2` 120 / `L3` 75 mm. Servos: MG996R shoulder and elbow,
MG90S base and gripper, SG90 wrist. Shoulder safety factor 2.44.

---

## 2. Where things are

```
CLAUDE.md                      this file
README.md                      overview (its "Status" line is stale — see §7)
desktop_robot_arm_claude_prompt.md   original brief, do not edit
docs/                          requirements, actuators, mechanical, electronics,
                               power, kinematics, BOM, assembly, testing, V2,
                               planning_guide.tex/.pdf, and SVG drawings:
  wiring_diagram.svg           full electrical wiring (ESP32 pins, power, ground)
  arm_overview.svg             side view of the whole arm, numbered parts
  arm_joint_detail.svg         early joint concept — SUPERSEDED by horn_adapter.svg
  horn_adapter.svg             current shoulder joint, to scale from the CAD
  shoulder_bracket.svg         shoulder bracket: section, wall A, foot (to scale)
cad/
  README.md                    parameter table + part list (source of truth for parts)
  equations.txt                SolidWorks global variables — see §4, handle with care
  parts/                       .SLDPRT / .SLDASM files (see §5)
firmware/arm_firmware/         ESP32 sketch (ESP32Servo), limits.h, slew.h
software/robot/                Python: config, kinematics (FK/IK), trajectory,
                               transport (serial + simulated), arm.py (public API)
calculations/engineering_calcs.py   torque/mass/stability self-checking script
artifacts/design_review.html   early design review page (historical record)
tools/latex/                   tectonic.exe to rebuild docs/planning_guide.pdf
```

Self-tests (no hardware needed), both should pass:
```
cd software && python -m robot.kinematics
python calculations/engineering_calcs.py
```
Rebuild the PDF after editing the .tex:
`./tools/latex/tectonic.exe docs/planning_guide.tex --outdir docs`
(baseline: a handful of small <6 pt overfull-hbox warnings are normal).

---

## 3. Decisions already made (do not reopen without a reason)

| Topic | Decision | Why / notes |
|---|---|---|
| Controller | **ESP32 DevKitC** (WROOM-32, CH340C), was Arduino Nano | Firmware uses `ESP32Servo`; pins GPIO13 base, 14 shoulder, 27 elbow, 26 wrist, 25 gripper (avoid strapping 0/2/5/12/15, input-only 34–39, UART0 1/3). 3.3 V signal: test each servo; 74HCT125 level shifter is the fallback, not in BOM. Nano is the documented fallback. |
| Power | University bench PSU at 6.0 V / 3 A | **4×AA rejected** (internal resistance sag) — recorded in `docs/power_system.md`. Never feed servos from the ESP32 5V/VIN pin; grounds must be common. |
| Ballast | **Milled mild steel block** ~60×60×15 mm (~424 g; ≥400 g required) | Bolted/press-fit, not loose. Size the base cavity to the real block. Haseeb is mill-trained. |
| Materials | **Prototype everything in PLA** except the **gripper jaws (PETG)** | Jaw compliant tips would crack in PLA. Upgrade other parts to PETG only on evidence (cracking/creep). PETG not yet tested for fit. |
| Gearboxes | **Not in V1** | No torque problem (SF 2.44); would eat servo travel and add backlash. Recorded as a separate V2 track. |
| Servo pocket library feature | **Skipped** | Haseeb designs servo mounts himself. |
| Metal U-brackets (AliExpress) | **Not used** | Only a possible fallback if the printed shoulder bracket fails. |
| Elbow layout | **Option A — nested, solid one-piece forearm** (2026-10-23) | 19 mm wide (0.5 mm each side) in the upper arm's 20 mm gap; its near face is its own horn adapter; 4 mm dowel turns in plate 2. Elbow servo sits outside plate 1. Any flare must start ≥35 mm from the elbow axis. See `docs/elbow_concept.svg`. |
| Horn adapter | **Bolts to plate 1** (the pin-side plate at the shoulder), not plate 2 | Servo case is 0.5 mm off plate 2's outer face and plate 2 turns under it — no bolt head fits there. |
| PCB | Considered (makerspace PCB mill), **not decided** | Perfboard is the documented default. |
| Shoulder servo orientation | **Short end down, long end up** in the bracket | The servo cable leaves from the short end, so it exits low toward the turret; keeps the bracket's lower half compact. |

Purchases: AliExpress order placed 2026-10-05 and **received 2026-10-22**:
2× MG996R (4.9★ "MG996R 13kg High Torque Metal Gear" listing — an IBUW
listing was rejected after a review reporting a fake, plastic-geared MG996R),
MG90S 2-pack (Dogmang Plus), 608ZZ 2-pack, ESP32 DevKitC CH340C.
SG90 and PSU come from the university; filament bought locally.
**The real MG996R matches the downloaded CAD model** (Haseeb confirmed,
caliper-verified 2026-10-23).

Not yet bought: servo extension cables (wrist/gripper leads are too short),
M2/M3/M4 screws incl. M3 countersunk (flat head) and nyloc nuts, M3 heat-set
inserts, aluminium 25T servo horns (optional upgrade — the servos ship with
**plastic** horns), rubber jaw-pad material. Check makerspace stock first.

---

## 4. `cad/equations.txt` — rules (this has broken twice)

It is the single source of SolidWorks global variables, imported into every
part. **SolidWorks' Export button has twice overwritten it** with only the
current part's variables (and once with part-specific `"D1@Sketch1"=...`
links). Both times it was restored from git.

- **Never use Export** in the SolidWorks equations dialog. Only **Import**,
  and leave "Link to external file" unticked (absolute paths break across the
  two machines; linking may also write back).
- To add/change a variable, edit the file as text and keep its exact format:
  UTF-8 **with BOM**, every line ends in **`\r\r\n`** (CR CR LF — SolidWorks'
  own output), lines look like `"name"= value'comment`, a variable may only
  reference variables defined on earlier lines, and **no `@` links**.
  Edit with a byte-level script (Python `rb`/`wb`), not a text editor that
  normalises line endings.
- Before committing, check: 79 lines (as of now), BOM present, no `@`,
  no forward references. If the working copy has fewer variables than HEAD,
  it was clobbered by an export — restore with `git checkout -- cad/equations.txt`
  (after confirming it adds nothing new).
- `cad/README.md`'s parameter table mirrors this file — keep them in sync.

Current variables (values in mm):

| Name | Value | Notes |
|---|---|---|
| `L1`, `L2`, `L3`, `h0` | 120, 120, 75, 75 | Link lengths / shoulder height |
| `t_link`, `t_bracket` | 3, 4 | Plate / bracket thickness |
| `d_pin`, `d_pin_gripper` | 4 (M4), 3 (M3) | |
| `c_fit` | 0.2 | **Measured** 2026-10-01 on Prusa Core One + Prusament PLA, 0.4 nozzle, 0.2 layers — best snug fit on both M4 and M3 coupon rows. PETG untested. |
| `c_fit_pivot` | `c_fit` + 0.05 = 0.25 | Rotating fit. **Chosen, not verified** — spin-test an M3/M4 in the coupon's 3.25/4.25 holes. |
| `w_link`, `w_gap` | 20, 20 | Plate depth; twin-plate gap (now set by the adapter length) |
| `d_boss`, `c_boss`, `d_servo_hole` | 13, 1, 15 | Servo output boss and plate clearance hole |
| `t_rim`, `w_link_end` | 9.5, 34 | Plate end material / width at the Ø15 end. 9.5 was raised for bolts at that end, which the adapter no longer needs — could return to 7.5 (saves ~0.7 g/plate); left as is. |
| `d_hole_m3`, `d_hole_pivot` | 3.2, 4.25 | M3 clearance; M4 rotating hole |
| `d_horn`, `t_horn`, `g_horn` | 20, 2.3, 2.2 | Horn disc and its gap to plate 2 (from the model) |
| `d_horn_pocket`, `h_horn_pocket` | 20.2, 4.5 | Adapter pocket |
| `d_horn_screw_cb`, `h_horn_screw_cb` | 8.5, 2.6 | Recess for the horn's M3 centre-screw head |
| `d_adapter`, `h_adapter` | 26, `w_gap` | Adapter collar |
| `t_adapter_floor`, `d_horn_screw_hole`, `r_horn_screw`, `d_access` | 2, 2.2, 7, 4 | Horn screws (M2 self-tappers, ≤6 mm) from below |
| `d_insert_m3`, `h_insert_m3` | 4.0, 6 | M3 heat-set insert hole. Inserts on hand: HZYUEGOU kit, M3 × 3/4/5/6/8 × **4.2 OD** — use **M3 × 5**. Hole changed 4.2 → 4.0 on 2026-10-23 (a 4.2 hole = OD gives no grip). Test one in a scrap print; open to 4.1 if too tight. Re-import into the adapter and bracket. |
| `x_adapter_bolt`, `y_adapter_bolt` | 6, 5 | Adapter bolts relative to the pin |
| `d_csk_m3` | 6.4 | 90° countersink for M3 flat heads in plate 1 |
| `h_pin_bore` | 10 | M4 pin depth in the adapter |
| `l_servo`, `w_servo`, `r_servo_short`, `r_servo_long` | 40.9, 20, 10, 30.9 | MG996R case (no ears) and shaft-to-end distances, from the model |
| `l_ear_holes`, `w_ear_holes`, `a_ear` | 48.6, 10, 8.2 | Ear hole spacing; ear seating face to plate-2 outer face |
| `c_win`, `l_window`, `w_window` | 0.3, 41.5, 20.6 | Bracket wall A window (clearance is a starting value) |
| `g_wall_a`, `g_wall_b` | 4.2, 1 | Wall A to plate 2 gap; plate 1 to wall B (washer) |
| `d_axis_turret`, `t_foot`, `w_foot`, `h_wall_top`, `w_wall` | 34, 6, 50, 41.5, 30 | Bracket envelope — `d_axis_turret` is a **placeholder** until the turret exists |
| `t_boss_b`, `d_boss_b` | 4, 12 | Pin boss on wall B |
| `r_wall_corner`, `r_foot_fillet` | 10, 4 | Wall A top corners; wall-to-foot fillets |
| `l_notch`, `w_notch` | 6.4, 1.66 | Ear rib notches past each end of the wall A window |
| `l_foot_back`, `l_foot_front` | 11.6, 11 | Foot overhang behind wall A / past wall B |
| `w_turret_holes`, `e_turret_hole` | 40, 4.8 | Turret bolt pattern across the foot; hole centre to foot end |
| `z_wall_b_out`, `z_turret_hole` | 39.2, 45.4 | Derived: wall B outer face; upper turret holes (lower pair mirrors about the foot centre) |
| `c_side`, `w_forearm`, `h_forearm` | 0.5, 19, 20 | Solid forearm nested in the 20 mm upper-arm gap |
| `h_horn_pocket_fa` | 4.0 | Elbow horn pocket depth (forearm reuses the adapter's other horn variables) |
| `h_dowel_fa`, `l_dowel_elbow` | 10, 13.5 | Elbow dowel: press-fit depth in the forearm (hole `d_pin`), length flush with plate 2 |
| `r_mount_bolt`, `h_standoff`, `d_standoff` | 30, 4.2, 7 | Elbow servo mount: standoffs on the upper-arm spacer holes 30 mm toward the shoulder |
| `e_mount`, `l_mount_back`, `l_mount_bolt` | 5, 35, 34.2 | Mount wall end past the bolts; wall end from the elbow axis; bolt grip → M3×40 + nut |

---

## 5. CAD state (SolidWorks 2026 Student, units mm)

### MG996R model (`cad/parts/MG996R Servo Motor/`, downloaded)
Licence unknown — the repo is public; flag if it must be removed.
Measured from the model: case 54 long (ear tip to tip) × 20 wide × 39 tall;
ear holes 4 × Ø4 keyhole slots (open to the ear tip, 2.4 wide) at
**48.6 × 10 mm** — the old "Ø3.0 at 51 × 15" was the ears' R1.5 corner
rounds, corrected 2026-10-23; Haseeb calipered the real servo's ear holes
the same day and they match; each ear has a centre rib 1 wide × up to 1.5
tall on its seating face (case X 20.45–26.8); ear thickness 2.3; ear seating
face 9.7 mm below the top of the output boss (9.9 was measured to the 0.2 mm
edge round — that error made `a_ear` 8.4 instead of 8.2); shaft 10.45 off the case centre
(16.55 from the nearer end); 25-tooth spline Ø5.8 with M3 centre hole;
output boss Ø13. Horn config used: **"Circular Horn"** — Ø20 × 2.3 disc,
Ø8.8 × 3.2 hub pointing toward the servo, 12 × Ø1.5 holes (4 at r = 7 on
the axes, 8 at (±7, ±3)/(±3, ±7)), centre Ø3.

### `upper_arm_plate.SLDPRT` — done (11.8 g PLA solid)
145 mm long, 3 thick. Big end R17 (34 wide) with Ø15 hole at x = −60;
pin end R10 (20 wide) with Ø4.25 hole at x = +60; tapered waist (20 mm).
4 spacer holes Ø3.2 at (±30, ±5) — symmetric under 180° rotation.
2 adapter holes Ø3.2 at (54, ±5) with a 90° Ø6.4 countersink on the part's
**Z = 3 face**. All dimensions are linked to variables.
Both upper-arm plates are this one file. In MockShoulder plate 1 is flipped
over, so the countersinks face outward (toward bracket wall B).

### `upper_arm_spacer.SLDPRT` — done (0.76 g)
Tube Ø7 OD × `w_gap` long, bore `d_hole_m3`. 4 per link. Print standing up.
M3×30 + plain nut (or M3×35 + nyloc). The forearm will need its own length.

### `upper_arm_horn_adapter.SLDPRT` — done (10.2 g solid)
Ø26 × 20 collar. Z = 0 is the plate-1 face, Z = 20 the plate-2 face.
Horn pocket Ø20.2 × 4.5 (Z 15.5–20); centre-screw recess Ø8.5 × 2.6;
pin bore Ø4.25 × 10 from Z = 0; 3 access bores Ø4 at r = 7 (angles 90°,
−90°, 180°) stopping 2 mm below the pocket floor, then Ø2.2 through;
2 insert holes `d_insert_m3` × 6 at (+6, ±5) (Ø4.2 in the saved part until
re-imported → 4.0). Its **+X must point toward the arm's
middle** (that is where plate 1's holes are). Print with Z = 0 on the bed.
Torque path: horn → M2 screws → adapter → M3 countersunk screws → plate 1 →
spacers → plate 2.

### `shoulder_bracket.SLDPRT` — done 2026-10-23 (35.5 g solid), checked in MockShoulder
One body. Origin on the shoulder axis; Front Plane = wall A's outer face
(the ear seating face); +Z toward the arm; +Y toward the servo's long end.
- Wall A: Z 0–4, 30 wide, Y −28 to +41.5, R10 top corners. Window 20.6 × 41.5
  (X ±10.3, Y −10.3 to 31.2) with 1.66-wide rib notches at both ends (to
  Y −16.7 and +37.6; 0.33 mm beside each ear rib). 4 × Ø3.2 ear holes at
  (±5, −13.85) and (±5, +34.75) — exactly on the servo slots. Only 1.95 mm
  of wall between the lower holes and the window: watch it on the test print.
- Wall B: Z 35.2–39.2 (after `a_ear` = 8.2 → exactly 1.0 to plate 1), R15
  top on the axis; boss Ø12 × 4 outside (to Z 43.2); Ø4 pin hole through
  boss + wall B (sized for a 4 mm press-fit dowel).
- Foot: Y −28 to −34, X ±25, Z −11.6 to 50.2 (61.8 × 50 × 6). 4 × M3
  heat-set insert holes (`d_insert_m3`) at X ±20, Z −6.8 / 45.4 (40 × 52.2
  pattern); screws come up from the turret. R4 wall-to-foot fillets. Foot
  extended 1 mm at each end on 2026-10-23 → **2.7 mm** of plastic outside
  each insert (was 1.7); **2.8 mm** once the holes are re-imported at 4.0
  (the saved part still has Ø4.2). The lower holes are dimensioned from the
  origin, not the foot edge; Sketch5's far end is set by its 61.8 length.
  Mass 35.5 g solid.
- `d_axis_turret` (34) is a **placeholder** — the turret sets it.
- Not yet: FEA, test print, pin hardware decision.

### `MockShoulder.SLDASM` — rebuilt around the bracket 2026-10-23, checked
The bracket is now the fixed base part (`shoulder_bracket-1` at the origin,
so assembly coords = bracket coords). Components: `MG996R Servo Motor-2`,
`upper_arm_plate-3` (plate 1) / `-4` (plate 2), `upper_arm_horn_adapter-2`,
4 spacers (`-9, -10, -12, -13`). Servo mates: shaft concentric with the
bracket's Ø4 pin hole, ear seating face coincident with wall A's outer face,
case side parallel to the window side. Stack along Z: plate 2 8.2–11.2,
adapter 11.2–31.2, plate 1 31.2–34.2 → 4.2 mm behind wall A (ear screw heads
get ~2.2 mm), 1.0 mm to wall B.
Interference check: 32 hits, all inside the vendor servo model; **0 in our
parts** (an earlier run found the two ear ribs, 4.32 mm³ each — fixed by the
notches). Re-run after the foot extension on 2026-10-23: still 0 in our parts. Horn mate re-checked after the rebuild: horn holes sit exactly on
the adapter's access bores (0.00° off). Final check 2026-10-23: all of the
above confirmed. On the real arm the horn angle is set at assembly; the arm's zero
is trimmed by spline tooth choice (~14.4° steps) + `angle_offset` in
`software/robot/config.py`.

Assembly order at the shoulder: servo into bracket → plate 2 over the boss
(before the horn — Ø20 horn won't pass Ø15) → horn + centre screw →
adapter over horn, M2 screws from below → spacers + plate 1, M3 countersunk
screws → wall B + shoulder pin (4 mm dowel recommended, see §6 step 2).
Servo into bracket: ear screws go in from the plate-2 side (heads in the
4.2 mm gap), nuts on top of the ears — so do it before plate 2 goes on.

Machines: laptop has the repo at **`D:\RoboArm`** (internal HDD, moved off
OneDrive on 2026-10-23 after OneDrive silently deleted the `docs/`,
`firmware/`, `software/`, `calculations/` and `tools/` folders — restored
from git) with SolidWorks and the full SolidWorks MCP server; a PC had a
plain clone at `Desktop\RoboArm`. Since 2026-10-22 there is also a new
computer with the repo at `C:\Users\hasee\Downloads\RoboArm` and
SolidWorks 2026 SP3.2 **running from the external drive `G:`** (Samsung SSD,
`G:\SOLIDWORKS\SLDWORKS.exe`, registered as the COM server — plug it in
first). Claude Code chats are local to each machine, so this file is the
only shared memory. **Sync only through git** (`git pull` before work, push
after). SolidWorks lock files (`~$*`) are git-ignored.

---

## 6. Next steps (in order)

1. ~~Close out the shoulder CAD~~ — **done 2026-10-23**: foot extended
   (2.7 mm at the inserts), real ear holes calipered (match 48.6 × 10),
   MockShoulder re-checked (0 interferences in our parts). Horn mate and the
   1.0 mm wall B gap were already done.
2. **Decide the shoulder pin:** recommended a 4 mm steel dowel (drill rod /
   silver steel, ~22 mm) pressed into wall B's Ø4 hole, running in the
   adapter's Ø4.25 bore. A partially-threaded M4 bolt doesn't work cleanly:
   its thread is at the tip, so the thread ends up in the bearing bore, and
   the bore can't be deepened (the horn pocket floor is in the way). Add a
   1 mm thrust washer between plate 1 and wall B.
3. **Print and test the shoulder set:** 2 plates, 4–8 spacers, 1 adapter,
   1 bracket (PLA, 4 perimeters). Bracket foot-down first (no supports); if
   wall A flexes, reprint on its side with support under wall B. Check:
   servo slides through the window (`c_win` 0.3), M3×10 ear screws + nuts,
   heat-set inserts (foot + adapter), the 1.95 mm bridge under the lower
   ear holes, 120 mm pivot spacing with an M4 bolt (±0.2), spacer length,
   free spin for `c_fit_pivot`, plate webs for cracks.
4. **Bench-test the servos** on the ESP32 (`PING` → `OK ARM v1`, then `J`/`G`)
   per `docs/assembly.md` — watch for 3.3 V jitter; confirm horn material.
5. **FEA on the bracket** (SolidWorks Simulation): servo stall-torque
   reaction through the ears + arm weight/payload through the pin.
6. **Elbow + forearm** (layout A, solid one-piece forearm, see
   `docs/elbow_concept.svg`; variables `c_side` … `l_dowel_elbow` added).
   Elbow servo mount decided 2026-10-23: servo long end points out past
   the elbow; mount = wall A copy whose lower end runs back to two 4.2 mm
   standoffs on the upper-arm spacer holes at 30 mm (M3×40 there). Standoffs
   around the Ø15 hole were rejected (they hit the servo case). Check the
   two-bolt cantilever in FEA. Next: model forearm + mount, SG90 wrist end.
7. **Base, column (2 × 608ZZ), turret**: sets `d_axis_turret`
   (= 75 − turret top height); must match the bracket's 52 × 40 M3 pattern;
   ballast pocket for the steel block; V2 camera-mast bosses.
8. **Gripper** (PETG jaws, compliant tips, gear-sector mesh, MG90S).
9. Electronics (perfboard or PCB), firmware bring-up, calibration, testing
   per `docs/testing.md`.

Also to buy: M3×10 screws + M3 nuts for the servo ears (4 per MG996R), a
4 mm steel dowel, 1 mm M4 thrust washers.

---

## 7. Known stale or wrong docs (fix when convenient)

- `README.md` status line still says "CAD not yet started".
- `cad/README.md` "Link side plate spec" describes the old plain 20 mm slot
  with 4.2 mm holes at both ends — the real plate is the tapered one in §5.
- `docs/mechanical_design.md`, `docs/assembly.md`, planning guide say to bolt
  "the metal horn that shipped with the servo" — the servos ship **plastic**
  horns.
- Docs say the forearm is identical to the upper arm — not true under
  elbow layout A.
- `w_gap`'s comment says it is set by the elbow servo mount — it is now set
  by the adapter.
- `docs/arm_joint_detail.svg` is superseded (exaggerated shaft, bolts in the
  wrong plate) — `docs/horn_adapter.svg` is current.
- An old `upper_arm_plate.STEP` sits on the laptop Desktop, not in the repo.

---

## 8. Working with SolidWorks from Claude

### Laptop
A SolidWorks MCP server is configured on the laptop
(`C:\Users\hasee\Downloads\solidworks-mcp`). Notes:
- `connect_solidworks` works. `list_open_documents` and `get_document_info`
  **error** — use `execute_python` instead (`sw` and `doc` are provided).
- In that Python, many COM members come back as **values, not callables**
  (e.g. `doc.GetTitle`, `doc.GetPathName`, `doc.GetType`, `f.GetSurface`,
  `s.IsCylinder`). A helper `val = lambda x: x() if callable(x) else x`
  handles both. Methods that take arguments are called normally:
  `doc.GetBodies2(0, False)`, `b.GetFaces()`, `c.GetBox(False, False)`,
  `b.GetMassProperties(1250.0)` (PLA density for mass).
- Component placement: `list(c.Transform2.ArrayData)` → rotation rows
  `[0:3],[3:6],[6:9]`, translation `[9:12]` in metres; a part point maps as
  `p*R + t` (row-vector convention).
- Equation links in a part: iterate `doc.GetEquationMgr` with
  `em.Equation(i)` / `em.Value(i)`; links look like `"D1@Sketch1"=...`.
- Interference: `mgr = doc.InterferenceDetectionManager`,
  `val(mgr.GetInterferences)`, each item's `val(it.Components)` and
  `val(it.Volume)` (m³), then `mgr.Done()`. Ignore pairs that are all inside
  `MG996R Servo Motor-*/` (the vendor model self-intersects — expect
  exactly 32 such hits; if a run reports 0 of those, the check didn't
  really run: rerun it).
- **Read only** unless Haseeb asks for changes; he models the parts himself.
  Report what was checked with real numbers, and say which numbers come from
  the downloaded model vs. measurements.

### New computer (Downloads\RoboArm, SolidWorks on G:)
- The SolidWorks MCP here is Sam-Of-The-Arth/SolidWorks-MCP, cloned to
  `C:\Users\hasee\mcp-servers\SolidWorks-MCP` (patched: logs to stderr,
  `mcp>=1.0,<2` — 2.x removed its decorator API). Registered as `solidworks`
  in `~/.claude.json` and in Claude Desktop's MSIX config
  (`%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json`).
  It only has sketch/extrude tools — **useless for inspection**.
- Inspect instead with read-only pywin32 scripts against the running
  SolidWorks (`GetActiveObject("SldWorks.Application")`). Run them with
  `C:\Python313\python.exe` (the `python` on Git Bash's PATH lacks pywin32)
  and **without `-I`** (pywin32 is in the user site-packages). Keep the
  scripts in the scratchpad, not the repo.
- Late-binding quirks here ("Member not found"): `doc.FirstFeature`,
  `doc.GetEquationMgr`, `feat.GetSpecificFeature2`, `comp.GetModelDoc2`,
  `face.GetSurface`. Workarounds: `doc.FeatureManager.GetFeatures(True)`;
  get part documents from `sw.GetDocuments` by title; infer geometry from
  `val(face.GetBox)` (a box flat in one axis = a plane; a hole shows as a
  curved face whose box is the hole's diameter wide). Child components'
  `Transform2` is in top-level assembly coordinates. Equation values can't
  be read here — trust the Σ dimensions in Haseeb's screenshots or check the
  resulting geometry.

---

## 9. How Haseeb likes to work

- Asks "what's next" often — answer with a short ordered list.
- Likes **visuals**: SVG diagrams saved in `docs/` and sent with
  SendUserFile. Draw to scale from the CAD when possible; check the render
  before sending.
- Wants Claude to **check SolidWorks directly** rather than ask for numbers.
- Commit/push only when asked ("push everything" is common). Stage with
  `git add -A` only after checking nothing odd is included; never commit
  `~$*` lock files. **Check `cad/equations.txt` before every commit** (§4).
- Commit messages: short and plain, his style — e.g. "Add upper arm spacer,
  update README spacer entry" — plus the Co-Authored-By trailer.
- Keep things simple and buildable; flag over-engineering. Push back
  honestly when something won't work (e.g. fake servos, AA batteries,
  printed splines), and own mistakes plainly.
