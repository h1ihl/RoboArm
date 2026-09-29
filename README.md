# Desk Arm — Low-Cost 3-DOF Desktop Robot Arm

A small tabletop 3-DOF robot arm (base yaw, shoulder, elbow, plus a two-finger
gripper), 3D-printed and built on hobby servos, aimed at CAD $50–70 and hard
capped at $100. V1 is a manually/programmatically controlled physical arm.
V2 (not started) adds a camera, object detection and an AI agent on top of the
same control API.

**Status: Phase 0 (Requirements) complete — design review signed off, CAD not
yet started.** See [`docs/requirements.md`](docs/requirements.md) for the
decision gate and [`docs/planning_guide.pdf`](docs/planning_guide.pdf) for the
full write-up.

## Chosen configuration — Configuration B

| | |
|---|---|
| Reach | 315 mm |
| Payload | 55 g |
| Base / Shoulder / Elbow | MG90S / MG996R / MG996R |
| Wrist (slaved, keeps jaws level) | SG90 |
| Gripper | MG90S, two-finger compliant jaws |
| Controller | ESP32 DevKit, USB serial |
| Power | 6 V 3 A regulated, separate from MCU 5 V rail |
| Shoulder safety factor | 2.44 |
| Purchase cost | ≈ CAD $59 (typical lab sourcing) |

Fallback Configurations A (ultra-budget, $48–55), C (university-sourced,
$17–35) and D (stronger, $85–95) share the same CAD, firmware and software —
see §14 of the planning guide.

## Repository layout

```
README.md                    you are here
docs/                         requirements, calculations, BOM, procedures, wiring diagram, the LaTeX planning guide + PDF
firmware/arm_firmware/        ESP32 sketch — servo control, joint limits, slew limiting, serial protocol
software/                     Python control layer — kinematics, trajectory, transport, CLI
cad/                           SolidWorks project layout, parametric strategy, part/config naming (files added as they're modelled)
calculations/                  the torque/mass/stability numbers as a runnable, checkable script
artifacts/                     saved copies of design artifacts (e.g. the interactive design-review page)
tools/latex/                   self-contained LaTeX engine used to build docs/planning_guide.pdf
```

## Documentation map

| Doc | Covers |
|---|---|
| [`docs/requirements.md`](docs/requirements.md) | DOFs, dimensions, payload, workspace, budget, the decision gate |
| [`docs/actuator_selection.md`](docs/actuator_selection.md) | Torque calculations, servo table, SG90 vs MG90S gripper decision |
| [`docs/mechanical_design.md`](docs/mechanical_design.md) | Geometry, mass budget, material assignment, print orientation rules, SolidWorks parametric strategy |
| [`docs/electronics.md`](docs/electronics.md) | Controller choice, wiring, serial protocol |
| [`docs/wiring_diagram.svg`](docs/wiring_diagram.svg) | Full wiring diagram — pin-out, power rail, grounding |
| [`docs/power_system.md`](docs/power_system.md) | Current budget, supply spec, brownout protection |
| [`docs/kinematics.md`](docs/kinematics.md) | Forward/inverse kinematics derivation, validation order |
| [`docs/bill_of_materials.md`](docs/bill_of_materials.md) | BOM A (purchase) and BOM B (university-sourced) |
| [`docs/assembly.md`](docs/assembly.md) | Build order, torque/adhesive notes, calibration procedure |
| [`docs/testing.md`](docs/testing.md) | Per-phase test plan, acceptance criteria |
| [`docs/v2_ai_roadmap.md`](docs/v2_ai_roadmap.md) | What V2 adds and why V1's API doesn't need to change |
| [`docs/planning_guide.pdf`](docs/planning_guide.pdf) | All of the above, consolidated into one LaTeX-typeset document |

## Software quick start

```bash
cd software
python -m robot.kinematics        # runs the FK/IK self-test, no hardware needed
python cli.py --port COM5         # interactive control, once the arm is wired up
```

`software/robot/arm.py` exposes the six calls everything else — including the
future V2 agent — is meant to use: `home()`, `move_joints()`, `move_to()`,
`grip()`, `pickup()`, `place()`.

## Firmware quick start

Install the `esp32` board package (Boards Manager) and the `ESP32Servo`
library (Library Manager) in the Arduino IDE, open
`firmware/arm_firmware/arm_firmware.ino`, select your ESP32 board (e.g.
"ESP32 Dev Module"), upload, then talk to it at 115200 baud — `PING` should
answer `OK ARM v1`. Full command reference in `docs/electronics.md`.

## Build a fresh PDF

```powershell
.\tools\latex\tectonic.exe docs\planning_guide.tex --outdir docs
```

See `tools/latex/README.md` for details.
