# CLAUDE.md — Desk Arm project handoff

Read this first. It records what has been decided, what exists, how to work
in this repo, and what comes next. Last updated 2026-10-22.

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
README.md                      overview (its "Status" line is stale — see §9)
desktop_robot_arm_claude_prompt.md   original brief, do not edit
docs/                          requirements, actuators, mechanical, electronics,
                               power, kinematics, BOM, assembly, testing, V2,
                               planning_guide.tex/.pdf, and SVG drawings:
  wiring_diagram.svg           full electrical wiring (ESP32 pins, power, ground)
  arm_overview.svg             side view of the whole arm, numbered parts
  arm_joint_detail.svg         early joint concept — SUPERSEDED by horn_adapter.svg
  horn_adapter.svg             current shoulder joint, to scale from the CAD
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
| Elbow layout | **Option A — nested** (forearm plates sit inside the upper-arm gap, forearm gap ~10 mm) | Deferred; shoulder first. Means the forearm is NOT identical to the upper arm (own spacer length, own wrist end). |
| Horn adapter | **Bolts to plate 1** (the pin-side plate at the shoulder), not plate 2 | Servo case is 0.5 mm off plate 2's outer face and plate 2 turns under it — no bolt head fits there. |
| PCB | Considered (makerspace PCB mill), **not decided** | Perfboard is the documented default. |

Purchases: AliExpress order placed 2026-10-05 and **received 2026-10-22**:
2× MG996R (4.9★ "MG996R 13kg High Torque Metal Gear" listing — an IBUW
listing was rejected after a review reporting a fake, plastic-geared MG996R),
MG90S 2-pack (Dogmang Plus), 608ZZ 2-pack, ESP32 DevKitC CH340C.
SG90 and PSU come from the university; filament bought locally.
**The real MG996R matches the downloaded CAD model** (Haseeb confirmed).

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
- Before committing, check: 38 lines (as of now), BOM present, no `@`,
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
| `d_insert_m3`, `h_insert_m3` | 4.2, 6 | M3 heat-set insert hole — **check the insert maker's spec** |
| `x_adapter_bolt`, `y_adapter_bolt` | 6, 5 | Adapter bolts relative to the pin |
| `d_csk_m3` | 6.4 | 90° countersink for M3 flat heads in plate 1 |
| `h_pin_bore` | 10 | M4 pin depth in the adapter |

---

## 5. CAD state (SolidWorks 2026 Student, units mm)

### MG996R model (`cad/parts/MG996R Servo Motor/`, downloaded)
Licence unknown — the repo is public; flag if it must be removed.
Measured from the model: case 54 long (ear tip to tip) × 20 wide × 39 tall;
ear holes 4 × Ø3.0 at 51 × 15 mm spacing; ear thickness 2.3; ear top face
9.9 mm below the top of the output boss; shaft 10.45 off the case centre
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
2 insert holes Ø4.2 × 6 at (+6, ±5). Its **+X must point toward the arm's
middle** (that is where plate 1's holes are). Print with Z = 0 on the bed.
Torque path: horn → M2 screws → adapter → M3 countersunk screws → plate 1 →
spacers → plate 2.

### `MockShoulder.SLDASM` — checked
Two plates 20 mm apart (Z 0–3 and 23–26), 4 spacers, adapter, MG996R.
Servo shaft concentric with plate 2's Ø15 hole; servo lid 0.5 mm off
plate 2's outer face; horn disc Z 18.5–20.8 sitting on the pocket floor.
Interference check: **no collisions in our parts** (32 reported, all inside
the vendor servo model). **Open:** the horn is rotated ~29.5° vs the adapter
— add a concentric mate between an adapter screw hole and a horn hole.
On the real arm this angle is set at assembly; the arm's zero is then
trimmed by spline tooth choice (~14.4° steps) + `angle_offset` in
`software/robot/config.py`.

Assembly order at the shoulder: servo into bracket → plate 2 over the boss
(before the horn — Ø20 horn won't pass Ø15) → horn + centre screw →
adapter over horn, M2 screws from below → spacers + plate 1, M3 countersunk
screws → wall B + M4 pin.

Two-machine setup: laptop has the repo at
`C:\Users\hasee\OneDrive\Desktop\Robo Arm` (OneDrive) with SolidWorks and the
SolidWorks MCP server; the PC has a plain git clone (`Desktop\RoboArm`, no
OneDrive) and SolidWorks. **Sync only through git** (`git pull` before
work, push after). SolidWorks lock files (`~$*`) are git-ignored.

---

## 6. Next steps (in order)

1. **Check the real hardware:** caliper the output boss (update `d_boss` if
   not 13), confirm the horn type/material, and bench-test each servo on the
   ESP32 (`PING` → `OK ARM v1`, then `J`/`G`) per `docs/assembly.md` — watch
   for 3.3 V jitter.
2. **Print and test:** 2 plates, 4–8 spacers, 1 adapter (PLA, 4 perimeters,
   flat). Check the 120 mm pivot spacing with an M4 bolt (±0.2), spacer
   length, M3 fit, heat-set inserts, and the free-spin check for
   `c_fit_pivot`. Watch the plate's thin webs for cracks.
3. **Fix the horn mate** in MockShoulder.
4. **Shoulder bracket** (next real part, the FEA candidate): U-shape —
   wall A with a pocket for the servo body and the ear screws (ears rest on
   wall A's outer face; servo ear face is 8.4 mm from plate 2's outer face,
   so with a 4 mm wall there is 4.4 mm to plate 2), wall B carrying the fixed
   M4 pin coaxial with the servo shaft (≤0.2 mm), base bolting to the turret.
   One rigid printed part so the two walls stay aligned.
5. **M4 pin detail:** partially-threaded M4 so the smooth shank is the
   bearing; fix it in wall B (insert or tapped hole); plate 1 + adapter turn
   on it.
6. **Elbow + forearm** (layout A, nested): forearm plates inside the
   upper-arm gap, forearm gap ~10 mm, own spacer length, SG90 wrist end.
   Draw a section diagram first (as done for the shoulder).
7. **Base, column (2 × 608ZZ), turret**, ballast pocket for the steel block,
   V2 camera-mast bosses.
8. **Gripper** (PETG jaws, compliant tips, gear-sector mesh, MG90S).
9. Electronics (perfboard or PCB), firmware bring-up, calibration, testing
   per `docs/testing.md`.

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

## 8. Working with SolidWorks from Claude (laptop)

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
  `MG996R Servo Motor-1/` (the vendor model self-intersects).
- **Read only** unless Haseeb asks for changes; he models the parts himself.
  Report what was checked with real numbers, and say which numbers come from
  the downloaded model vs. measurements.

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
