# V2 — AI tabletop assistant roadmap

Nothing here gets built now. It's recorded so V1's decisions don't
accidentally close a door V2 needs open.

This covers two decoupled tracks: the AI/vision stages below (2.1–2.4,
added on top of an *unchanged* V1 chassis — the original scope), and a
separate payload/actuator upgrade path (§Payload upgrade path) that's a
different axis entirely and not implied by "V2."

## Stages

| Stage | Adds | Cost | Touches V1? |
|---|---|---:|---|
| 2.1 Eyes | USB webcam on a printed overhead mast, bolted to the base plate | $0–15 | One new printed part. No electronics change. |
| 2.2 Desk-plane calibration | Four-point homography: camera pixels → desk coordinates | $0 | New module. This is the whole of the coordinate problem — a desk is flat, so a 3×3 matrix is all that's needed. No depth camera, no stereo. |
| 2.3 Detection | YOLO or a colour/contour detector returning object centroids | $0 | New module, feeds (u, v) into 2.2. |
| 2.4 Agent | A language model with `arm.pickup()` / `arm.place()` exposed as tools | $0 | Nothing — the agent calls the same six methods the CLI calls. |

## The three decisions V1 makes on V2's behalf

Each costs nothing now and would be expensive to retrofit later:

1. **The PC holds the intelligence, the MCU holds the safety.** Joint limits
   and slew limiting live in firmware (`docs/electronics.md`), so the agent
   physically cannot exceed a joint limit no matter what it decides to do.
2. **The arm's public API is Cartesian** (`arm.move_to(x, y, z)`,
   `arm.pickup(x, y, z)`, `arm.place(x, y, z)` — see `software/robot/arm.py`).
   Vision output plugs straight into it; nothing about the API needs to
   change when a camera is added.
3. **The base plate has mounting provision for a camera mast** (see
   `cad/README.md`), so the camera-to-robot transform can be calibrated once
   and stays valid — the mast doesn't move relative to the base yaw axis.

Incidental to the V1→ESP32 swap (`docs/electronics.md`): the controller now
has Wi-Fi/BT on board, unused in V1 and not a reason to change anything
here — the PC↔arm link stays USB serial. If V2 ever wants the arm
untethered, that option now exists without a controller swap; it is not
otherwise part of this plan.

## Payload upgrade path — gearmotors + encoders

A different axis from 2.1–2.4 above: actuation/payload, not perception.
Not part of "V2" as the original brief scoped it (camera/vision/AI on an
*unchanged* chassis) — recorded here as its own track so it isn't implied
by, or confused with, the AI stages.

**What changes vs V1:**

- **Actuator.** Hobby servo (closed-loop internally, absolute position at
  power-on) → DC gearmotor + planetary gearbox (open-loop mechanically,
  needs external position feedback). This is the whole reason it's a
  bigger step than it looks: servos hide their control loop from you,
  gearmotors don't.
- **Firmware.** Needs an encoder-read + PID position loop per joint,
  replacing the current angle → microsecond → `Servo`/`ESP32Servo` mapping.
  Genuinely new firmware, not a config change.
- **Homing.** Motors don't know where they are at power-on the way servos
  do. Needs a homing routine (limit switch or encoder index pulse) — this
  reverses the "servos are absolute-position devices, so we don't need
  limit switches" decision in `docs/electronics.md`. A motor-based build
  does need them.
- **Driver hardware.** PWM-to-servo-signal wiring is replaced by a motor
  driver (H-bridge) per joint — new electronics, and the current budget in
  `docs/power_system.md` needs redoing from scratch; gearmotors under load
  pull meaningfully more than the current 1.8 A design case.
- **Mechanical.** Gearmotors + planetary stages are much bigger and
  heavier than micro servos — a new mechanical design, not a bracket swap.
  Mass budget, torque calcs, and print-orientation rules all get redone
  for the new actuator envelope.
- **Protocol.** The low-level serial commands (`J`, `US`) are
  servo-microsecond-specific and would need a new command set (target
  angle/velocity through the PID loop).

**What doesn't change:** `robot.arm.Arm`'s six public calls
(`home`, `move_joints`, `move_to`, `grip`, `pickup`, `place`) and the
Cartesian API contract — that boundary was deliberately drawn
actuator-agnostic (see "The three decisions V1 makes on V2's behalf"
above), so this upgrade plugs into the same PC-side software. The
"firmware owns safety, PC owns intelligence" split also holds, though the
safety firmware itself gets substantially more complex.

**Not scoped or budgeted yet.** Servo/motor selection, gear ratio, encoder
choice, driver IC, and a new power budget all need their own design
review before this is a real plan — the same gate V1 went through in
`docs/requirements.md`, not an assumption to build against yet.

## Worked example

"Pick up my screwdriver and put it beside my laptop" resolves to:

```
detect (2.3) → centroid (u, v) → homography (2.2) → (x, y, z)
  → arm.pickup(x, y, z)                                  [unchanged from V1]
  → agent picks a target (x', y', z') beside the laptop
  → arm.place(x', y', z')                                [unchanged from V1]
```

Every step after the homography is V1 code that already works. V2's actual
new code is stages 2.1–2.3; stage 2.4 is wiring, not development — see
`software/robot/arm.py` for the exact six calls it's built to expose.

## Explicitly out of scope, even for V2 planning purposes

Per brief §20/§16 — do not let V2 planning smuggle these back in:

- ROS or any robotics middleware/message bus
- A depth camera or stereo rig — the desk is flat; homography is enough
- Multi-object tracking, grasp planning, or anything resembling
  manipulation research
- Autonomous operation without a human-issued command
