# Actuator selection

## Method

Static gravity-holding torque at the worst-case pose (fully extended,
horizontal — also the normal working pose for a desk arm reaching across the
table). Dynamic/inertial terms are small at the speeds this arm moves at
(under 10% of the gravity term at the 60°/s slew limit firmware enforces) and
are absorbed by the safety-factor floor rather than modelled explicitly.

Target safety factor: **≥ 2.0**, evaluated at 6.0 V rated torque. This isn't
extra conservatism on top of a passing design — hobby servos publish *stall*
torque, and a servo held near stall runs hot and wears out fast. SF 2.0 is
roughly where a servo can hold a static pose indefinitely without cooking.

## Mass budget (inputs to the torque calc)

Horizontal distance from the shoulder axis, arm fully extended — the
worst case for every load in the chain:

| Item | Mass | Distance | Moment (g·mm) |
|---|---:|---:|---:|
| Upper-arm link pair + spacers | 30 g | 60 mm | 1,800 |
| Elbow servo (MG996R) + bracket | 65 g | 120 mm | 7,800 |
| Forearm link pair + spacers | 25 g | 180 mm | 4,500 |
| Wrist servo (SG90) + bracket | 17 g | 250 mm | 4,250 |
| Gripper assembly (MG90S + jaws) | 32 g | 285 mm | 9,120 |
| Design payload | 55 g | 320 mm | 17,600 |
| **Moving assembly total** | **224 g** | CoM 201 mm | **45,070 g·mm** |

Below the shoulder (drives base stability, not shoulder torque): base plate
100 g, column + turret 60 g, base servo 14 g, shoulder servo 55 g, hardware
40 g → **269 g**.

The elbow servo alone is 29% of the moving mass, at the point in the chain
where moving it costs the most shoulder torque. If shoulder margin ever
becomes a real problem, relocating that servo to the turret behind a
linkage is the highest-leverage fix available (~1.4 kg·cm) — noted here,
not implemented in V1.

## Torque calculations

```
Shoulder, arm horizontal at full extension:
  τ₁ = g · Σ(mᵢdᵢ) = 9.81 × 0.04507 kg·m = 0.442 N·m = 4.51 kg·cm

Elbow, moments about the elbow axis:
  τ₂ = 9.81 × (0.025×0.060 + 0.017×0.130 + 0.032×0.165 + 0.055×0.200)
     = 9.81 × 0.01999 = 0.196 N·m = 2.00 kg·cm

Base yaw — no gravity term, inertia + bearing drag only:
  I ≈ 0.0056 kg·m², α = 3.5 rad/s² → τ = 0.020 N·m, + drag ≈ 0.30 kg·cm
```

These are reproduced (and checkable) in `calculations/engineering_calcs.py`.

## Servo table

| Joint | Servo | Required | Target ×2 | Rated @6V | Actual SF | Verdict |
|---|---|---:|---:|---:|---:|---|
| Base | MG90S | 0.30 | 0.60 | 2.20 | 7.3 | ample |
| **Shoulder** | **MG996R** | **4.51** | **9.02** | **11.00** | **2.44** | sizing joint |
| Elbow | MG996R | 2.00 | 4.00 | 11.00 | 5.50 | pass |
| Wrist (slave) | SG90 | 0.58 | 1.17 | 1.80 | 3.08 | pass |
| Gripper | MG90S | 0.82 | 1.64 | 2.20 | 2.7 | pass |

All kg·cm, generic MG996R/MG90S/SG90 published specs at 6.0 V. On a 5 V
supply the MG996R drops to ~9.4 kg·cm and shoulder SF falls to 2.08 — still
acceptable, which is why a 5 V/3 A phone charger is a legitimate power
fallback (see `docs/power_system.md`).

**Why the elbow is over-specified (5.50), deliberately:** it needs 2.00
kg·cm, so at SF 2 it needs 4.0. The MG90S tops out at 2.2 and fails. The
next rung up, an MG92B at 3.5 kg·cm (~$8), still gives only SF 1.75 — and
costs more than an MG996R. There's nothing worth buying between them, so the
MG996R wins by default and the extra margin is free.

## Gripper: SG90 vs MG90S

Required clamp force for a 55 g object against gravity, μ = 0.5 (rubber pad,
conservative): `mg / 2μ = 0.54 N`. Design target: **4 N per jaw** — about 7×
the physics minimum, because real grips are off-centre and objects get
bumped.

```
Jaw tip force        F = 4.0 N at 30 mm from the jaw pivot
Jaw pivot torque      0.12 N·m
Drive reduction       1.5:1 (12 mm servo crank → 18 mm jaw crank)
Servo torque          0.080 N·m = 0.82 kg·cm

MG90S @ 6 V   2.2 kg·cm → SF 2.7
SG90  @ 4.8 V 1.6 kg·cm → SF 2.0
```

**Both pass on torque.** The decision is about what happens the twentieth
time the gripper closes on something it can't close on:

| | SG90 | MG90S (chosen) |
|---|---|---|
| Mass / cost | 9 g / ~$2 | 13.4 g / ~$6 |
| Gears | Nylon — strips on a hard stall or side impact | Metal — survives stalls and knocks |
| Footprint | 22.8 × 12.2 × 22.5 mm, 32 mm hole spacing | **Identical** — drop-in either way |

The identical footprint means the mount is one printed part regardless of
which servo goes in it. MG90S chosen; SG90 is the documented fallback if
gripper cost needs to drop (Configuration A).

**Mechanism:** two mirror-image printed jaws on M3 pins with meshed gear
sectors (module 1.5, ~10 teeth engaged) at their pivots. One servo drives one
jaw through a short link; the sectors force the other to mirror it — self
-centring, can't desync. Jaw faces carry a 90° V-groove (self-centres pens
and shafts) plus a glued rubber pad.

**Compliance matters more than gear material:** thin the last 12 mm of each
jaw to 1.6 mm so it flexes ~1 mm under load. One commanded "closed" angle
then grips a range of object sizes without ever driving the servo into a
hard stall — this detail does more for gripper longevity than metal vs.
nylon gears.
