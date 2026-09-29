# Electronics

## Architecture

```
   PC ──USB──▶ ESP32 ──────5 × PWM signal──▶ servos
                    │                              ▲
                    └──── GND ═══════ common ══════╪═══ GND
                                                   │
    6 V 3 A supply ──fuse──┬── 2 × 1000 µF ────────┘
                           └── V+ rail to all five servos
```

Full pin-out and wiring shown in [`docs/wiring_diagram.svg`](wiring_diagram.svg)
— open it in a browser, no build step needed.

## Controller: ESP32 (DevKitC or equivalent)

**Revised from the original Arduino Nano choice** — see the reasoning below;
nothing else about the architecture changed. The ESP32 is 3.3 V logic where
the Nano was native 5 V, which is the one real trade-off:

- Hobby servos decode PWM through an analog RC input stage, and in
  practice a 3.3 V "high" clears that threshold on the SG90/MG90S/MG996R
  family used here — this is a well-worn combination, not a gamble. The
  documented failure mode is occasional jitter on a specific unit, not a
  hard incompatibility. **Test each servo before final assembly**; if one
  jitters, add a 74HCT125/74AHCT125 quad buffer (~$1, one chip covers all
  five signal lines) between the GPIO and that signal wire to get a clean
  5 V pulse. Not included in the base BOM because most builds won't need
  it — this is the documented fallback, not a default component.
- Requires the **ESP32Servo** library instead of the stock `Servo.h` (the
  ESP32 Arduino core doesn't ship one); API is functionally the same
  `attach()` / `writeMicroseconds()` pair, just backed by the chip's LEDC
  PWM peripheral instead of a hardware timer. See
  `firmware/arm_firmware/arm_firmware.ino` for the setup boilerplate this
  adds (timer allocation, per-channel pulse range).
- In exchange: a dual-core chip with far more flash/RAM/GPIO than this
  project needs, a similar street price to the Nano, and — unused in V1,
  but noted for `docs/v2_ai_roadmap.md` — Wi-Fi/BT already on the board if
  V2 ever wants the arm untethered from the PC.

| Board | Cost | Logic | Assessment |
|---|---:|---|---|
| **ESP32 DevKit (chosen)** | $12 | 3.3 V | `ESP32Servo` library, USB-serial via onboard CP2102/CH340 — install its driver before you need it. Test 3.3 V servo latching per-unit; level-shifter fallback above. |
| Arduino Nano | $9 | 5 V | Native servo levels, no latching question, stock `Servo.h`. The straightforward fallback if an ESP32 isn't available or a servo won't latch cleanly at 3.3 V even with a level shifter — same firmware minus the ESP32Servo-specific setup calls, same pin roles, same protocol. |
| Arduino Uno | — | 5 V | Electrically identical to the Nano, bulkier. Take this if the lab has one. |
| Raspberry Pi Pico | $7 | 3.3 V | Better PWM hardware, cheaper, MicroPython instead of Arduino C++. Same 3.3 V latching consideration as the ESP32. |

**Deliberately not included:**
- **PCA9685 driver board** — five servos fit on five ESP32 GPIOs with the
  `ESP32Servo` library. The board solves a problem (running out of timers)
  that starts around twelve servos. $6 and a whole I²C bus for nothing here.
- **Encoders / current sensing** — hobby servos have no position-feedback
  path to the MCU; external encoders would mean closing a loop the servo
  already closes internally. Real value, wrong project.
- **Limit switches** — servos are absolute-position devices; they know where
  they are at power-on. Homing switches solve a stepper problem this arm
  doesn't have.

Assembly is a small piece of perfboard on the base plate: five 3-pin servo
headers, a barrel jack, the bulk capacitors, a fuse, and jumper wires to the
ESP32's GPIO/GND header pins — under an hour of soldering.

### GPIO pin selection

`firmware/arm_firmware/arm_firmware.ino` uses GPIO13 (base), GPIO14
(shoulder), GPIO27 (elbow), GPIO26 (wrist), GPIO25 (gripper) — five
general-purpose, LEDC-PWM-capable pins, chosen to avoid:

- **GPIO 0, 2, 5, 12, 15** — boot-strapping pins. A servo signal wire
  yanking one of these during power-on can change the chip's boot mode.
- **GPIO 34–39** — input-only, can't drive a servo signal at all.
- **GPIO 1, 3** — UART0, i.e. the USB-serial link back to the PC.

Any other general-purpose GPIO works as a substitute if a specific board's
layout makes a different pin more convenient — there's nothing special
about this exact set beyond satisfying the three exclusions above.

## Serial protocol

ASCII, line-oriented, one command per line, every command answered.
Debuggable from a plain serial monitor with no tooling — which matters a
great deal on the first evening the arm doesn't move.

| Command | Reply | Purpose |
|---|---|---|
| `PING` | `OK ARM v1` | Port identification and liveness |
| `J <base> <sh> <el>` | `OK` \| `ERR LIMIT <joint>` | Absolute joint angles, degrees. Wrist follows automatically. |
| `G <0-100>` | `OK` | Gripper, 0 = closed, 100 = open |
| `US <ch> <µs>` | `OK` \| `ERR RANGE` | Raw pulse width — calibration only, still bounded by limits.h. `ch` is `B`/`S`/`E`/`W`/`G` (base/shoulder/elbow/wrist/gripper) |
| `HOME` | `OK` | Slew to the safe folded pose |
| `STOP` | `OK` | Freeze at the current position |
| `REL` | `OK` | Detach all servos — kills holding buzz, lets you move the arm by hand |
| `STAT` | `<angles> <µs>` | Current commanded state |

## Firmware structure

```
firmware/arm_firmware/
├── arm_firmware.ino   serial parser, 50 Hz update loop
├── limits.h           per-joint µs bounds — hard clamp, no override from the PC
└── slew.h             60°/s rate limiter, so nothing ever slams
```

The split is deliberate: **the firmware owns safety, the PC owns
intelligence.** Joint limits and slew limiting live on the ESP32 and can't be
bypassed by a buggy Python script — or, later, by a confused AI agent.
Everything else (kinematics, sequencing, the CLI) lives on the PC where it's
easy to change without re-flashing.

## Wiring notes

- Servo ground and ESP32 ground **must** be joined, or the PWM signal has no
  reference and servos twitch randomly.
- Never power the servo rail from the ESP32's 5V/VIN pin or its USB
  connection — see `docs/power_system.md` for why.
- Keep servo signal wires away from the barrel-jack input leads to avoid
  switching noise on the PWM lines.
- Full pin-out, colour-coded nets and this checklist as a picture:
  [`docs/wiring_diagram.svg`](wiring_diagram.svg).
