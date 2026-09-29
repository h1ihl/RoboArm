# Software

Python control layer -- kinematics, trajectory shaping, the serial
transport, and the public `Arm` API everything (CLI, demo sequences, and
eventually the V2 agent) is meant to call through. Architecture and the
V1/V2 boundary are in `docs/electronics.md` and `docs/v2_ai_roadmap.md`.

## Install

```bash
pip install -r requirements.txt
```

Only needed for real hardware (`pyserial`). Kinematics and the demo
sequences run against a simulated arm with no dependencies at all.

## Layout

```
robot/
├── config.py        geometry, joint limits, workspace bounds, servo calibration -- the one file to tune
├── kinematics.py     fk(), ik(), reachable(), path_safe() -- see docs/kinematics.md
├── trajectory.py      eased joint-space interpolation for Cartesian moves
├── transport.py        serial line protocol + a SimulatedTransport for hardware-free testing
└── arm.py              class Arm -- the public API (home, move_joints, move_to, grip, pickup, place)
cli.py                  interactive shell: python cli.py --port COM5
sequences.py             demo/test routines used in docs/testing.md
```

## Try it with no hardware attached

```bash
python -m robot.kinematics     # FK/IK self-test
python sequences.py wave       # runs against a simulated arm, prints every command
python cli.py                  # interactive shell, simulated
```

Once the arm is wired up (`docs/assembly.md`), add `--port COM5` (or
whatever the ESP32 enumerates as) to `cli.py` / `sequences.py`, or pass
`port="COM5"` to `Arm()` directly.
