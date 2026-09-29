# Assembly

This is a build-order checklist, not a substitute for the SolidWorks
assembly (`cad/assemblies/`) — follow the drawings for hole positions and
fit; this page is for sequencing, torque/adhesive notes, and the things that
are easy to get wrong in a way that's expensive to undo.

## Before you start

- Print the **tolerance coupon** first (see `docs/mechanical_design.md`)
  and confirm pins seat with light thumb pressure, not a mallet, before
  printing the real parts.
- Dry-fit every part against its mating part before adding hardware.
  Printed parts vary printer-to-printer; catch it now.
- Have the metal servo horns that shipped with each servo on hand — the
  design bolts to them rather than printing splines (see
  `docs/mechanical_design.md`, layer-orientation rule 3).

## Build order

1. **Base and turret**
   - Press the two 608ZZ bearings into the base plate and column.
   - Mount the base servo (MG90S) in its pocket; bolt its metal horn to the
     turret underside — do not glue.
   - Test-rotate the turret by hand through its full range before any other
     part goes on. It should turn freely with no bearing preload.
   - Bolt or press-fit the milled steel ballast block (400 g minimum,
     `docs/mechanical_design.md` §Ballast — see the stability calc in
     `docs/planning_guide.pdf` §6) into the cavity **before** closing the
     snap lid; secured, not loose, so it can't shift during base rotation.
     The robot will tip without it once the arm goes on.

2. **Shoulder**
   - Mount the shoulder servo (MG996R) to the shoulder bracket. Bracket
     should have printed flat per the layer-orientation rules — check the
     layer lines run parallel to the bolt line, not across it.
   - Bolt the bracket to the turret. This joint carries the highest static
     load in the machine (§4.51 kg·cm) — use nyloc nuts here, not plain
     nuts, and don't skip the fillet at the servo cutout if you added one
     after the FEA study.

3. **Upper arm and elbow**
   - Assemble the twin-plate upper-arm link on its spacers.
   - Mount the elbow servo (MG996R) to the elbow bracket, same
     flat-print/bolted-horn rules as the shoulder.
   - Bolt the upper-arm link between the shoulder horn and the elbow
     bracket.

4. **Forearm and wrist**
   - Assemble the twin-plate forearm link.
   - Mount the wrist servo (SG90) at the forearm's far end.
   - Bolt the forearm between the elbow horn and the wrist bracket.

5. **Gripper**
   - Assemble the two mirror-image jaws on their M3 pivot pins, checking the
     gear sectors mesh smoothly through the full open/close range by hand
     before the servo is connected.
   - Mount the MG90S gripper servo and its drive link.
   - Bolt the gripper assembly to the wrist mounting face (the same 24 × 24
     mm interface all three wrist options share — fixed bracket, SG90
     slave, or later a parallelogram linkage).

6. **Electronics**
   - Solder the perfboard: five 3-pin servo headers, barrel jack, 2×1000 µF
     caps, fuse holder, jumper wires to the ESP32's GPIO/GND header pins
     (see `docs/wiring_diagram.svg` for the full pin-out).
   - **Do not connect servos to the ESP32's 5V/VIN pin.** Servo V+ goes to
     the regulated 6 V rail; only GND is shared (`docs/power_system.md`).
   - Route servo signal wires away from the barrel-jack leads.
   - Mount the perfboard and ESP32 to the base plate, near the ballast
     cavity so cable runs to the base/shoulder servos stay short.

7. **Cable routing**
   - Dress the shoulder/elbow/wrist/gripper cables along the arm with cable
     clips (unloaded PLA parts), leaving enough slack at each joint for its
     full range of motion — pull the arm through HOME → full extension →
     folded and check nothing goes taut.

## Bring-up sequence (before Phase 6 kinematics work)

1. Power the perfboard from the **bench supply**, 6.0 V, 3 A current limit,
   ESP32 *not yet* connected to servos.
2. Flash `firmware/arm_firmware/arm_firmware.ino` (Arduino IDE with the
   `esp32` board package and `ESP32Servo` library installed — see
   `docs/electronics.md`), confirm `PING` → `OK ARM v1` over serial with
   servos disconnected.
3. Connect one servo at a time, re-test with a `J`/`G` command each, watching
   for jitter (§Controller in `docs/electronics.md` — add a level shifter on
   that signal line if it doesn't settle) and the bench supply's ammeter. A
   joint drawing current while holding still at a legal angle means a
   binding joint, not an electrical fault — recheck fit before going
   further.
4. Only once all five respond correctly individually, run `HOME` with all
   five connected.

## Calibration

Hobby servos vary — commanding 90° rarely lands exactly on the mechanical
90° you designed for. Per-servo calibration lives in
`software/robot/config.py` as a `(min_us, max_us, angle_offset)` triple per
channel:

1. With the arm mounted and `REL` sent (servos detached, movable by hand),
   position each joint at a known reference angle (e.g. shoulder
   horizontal — use a set square against the upper-arm link).
2. Command that joint via `US <ch> <µs>` starting from the servo's nominal
   center (1500 µs) and adjust until it matches the reference.
3. Record the µs value in `config.py` as that joint's zero offset. Repeat at
   one more angle near the opposite end of travel to get a two-point
   calibration (handles gear-train nonlinearity better than a single
   offset).
4. Re-run `software/robot/kinematics.py`'s self-test, then verify with a
   few `move_to()` calls against a ruler — this is what sets the ±5–8 mm
   repeatability figure in `docs/kinematics.md` as a measured number
   instead of a prediction.

This step is the one most likely to eat a whole evening (see
`docs/testing.md` and the Phase 5 timeline note in the planning guide) —
budget for it rather than being surprised by it.
