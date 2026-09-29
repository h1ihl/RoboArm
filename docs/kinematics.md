# Kinematics

No DH tables, no Jacobians, no numerical solver. Base rotation decouples
completely from shoulder/elbow, leaving a two-link planar problem with a
closed-form solution — implemented in full in
`software/robot/kinematics.py` (~40 lines including workspace checks, with a
self-test that reproduces every number below).

## Forward kinematics

```
r = L₁·cos θ₁ + L₂·cos(θ₁+θ₂) + L₃
z = h₀ + L₁·sin θ₁ + L₂·sin(θ₁+θ₂)
x = r·cos θ₀        y = r·sin θ₀
```

`L₃` adds directly to `r` with no trig term — that's the payoff of the
levelled wrist (`docs/requirements.md` — the SG90 slaved axis). Without it,
`L₃` would carry a `cos(θ₁+θ₂+θ₃)` factor and the inverse problem stops
being closed-form.

## Inverse kinematics

```
θ₀ = atan2(y, x)

r' = √(x²+y²) − L₃          # wrist-pivot radius
z' = z − h₀

D  = (r'² + z'² − L₁² − L₂²) / (2·L₁·L₂)
     # |D| > 1  →  target unreachable. Check before acos().

θ₂ = −acos(D)                                    # negative root = elbow-up
θ₁ = atan2(z', r') − atan2(L₂·sin θ₂, L₁ + L₂·cos θ₂)
θ₃ = −(θ₁ + θ₂)                                  # slaved wrist, jaws level
```

The two `acos` roots are elbow-up and elbow-down. Elbow-down puts the elbow
below the table on nearly every desk-height target, so the solver takes the
negative root unconditionally and never has to choose between them.

## Validation, in this order, before anything moves

1. **Reachability** — `|D| ≤ 1` and `130 ≤ √(x²+y²) ≤ 290` (mm).
2. **Joint limits** — every θ inside its mechanical range
   (`docs/requirements.md` §DOF / `firmware/arm_firmware/limits.h`).
3. **Table clearance** — `z ≥ 10 mm`, and the elbow itself above the table,
   which the elbow-up choice doesn't guarantee near the inner boundary.
4. **Path check** — for a Cartesian move, interpolate ~20 waypoints and
   validate each. A straight line between two legal poses can still pass
   through an illegal one.

`software/robot/kinematics.py` implements all four as `reachable()` and
`path_safe()`, called from `arm.py::move_to()` before any command reaches
the serial port.

## Accuracy limit: backlash, not mathematics

An MG996R has 1–2° of gear lash plus potentiometer deadband. At the 240 mm
shoulder+elbow lever, 1.5° is **6 mm at the gripper**. Expect **±5–8 mm**
repeatability and design around it, not against it:

- Approach every target from the same direction, so lash is always taken up
  the same way.
- Let the 55 mm jaw opening (and the gripper's compliant tip,
  `docs/actuator_selection.md`) absorb the rest.

No amount of IK precision buys back a millimetre of this — it's a mechanical
limit, not a software one.
