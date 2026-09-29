# Testing

Test plan by phase, with concrete acceptance criteria rather than "works
fine" — each one is checkable against a number already committed to
elsewhere in the docs.

## Individual joints (after Phase 5 firmware, before Phase 6 kinematics)

| Test | Method | Acceptance |
|---|---|---|
| Full range of motion | `J`/`G` sweep from one limit to the other, by hand-verify against `firmware/arm_firmware/limits.h` | No binding anywhere in range; firmware rejects out-of-range commands with `ERR LIMIT` |
| Slew limiting | Command a large step change, time it | Matches the 60°/s cap — protects against the tipping/inertia case in the stability calc |
| Holding current | Bench-supply ammeter, joint at rest at a legal angle | Reads near the "idle" column in `docs/power_system.md`'s current table, not "moving" or "stall" |
| Detach | `REL`, then move joint by hand | Moves freely, no resistance beyond gear friction |

## Full arm

| Test | Method | Acceptance |
|---|---|---|
| HOME | `HOME` from an arbitrary pose | Reaches the folded pose without collision, arm clears the table |
| Workspace boundary | `move_to()` at the documented inner/outer radius (130 / 290 mm) and just outside it | Inside: succeeds. Outside: rejected before any servo moves (`docs/kinematics.md` validation order) |
| Table clearance | `move_to()` targeting `z` below 10 mm | Rejected by the software floor, not just the firmware — both layers should refuse it |
| Path safety | A Cartesian move whose straight-line path dips through an illegal region | Rejected, even though start and end poses are individually legal |
| Repeatability | `move_to()` the same target 10× from the same approach direction, measure with a ruler | Within ±5–8 mm (the backlash-limited figure in `docs/kinematics.md`) — if it's worse, recheck calibration before assuming a mechanical fault |

## Gripper

| Test | Method | Acceptance |
|---|---|---|
| Jaw opening | `G 0` → `G 100` | 0–55 mm as designed |
| Grip force | Compliant-tip jaw closes on a range of object widths at one commanded angle | Holds a 55 g object at full reach without the servo audibly stalling |
| Stall behaviour | Command `G 0` (closed) on an object too large to fully close on | Servo current rises but the compliant jaw tip flexes rather than the servo grinding at stall indefinitely — send `REL` if holding for more than a few seconds |

## Payload

- Sweep the design payload (55 g) through the full workspace at several
  representative points (near, far, left, right of centre).
- Confirm no joint's holding current approaches its stall figure
  (`docs/power_system.md`) at any tested point — if one does, that's the
  "measured, not predicted" trigger for the B→D fallback in
  `docs/requirements.md`.
- Repeat at 0 g (no payload) to get a baseline — the difference isolates
  payload-driven current from friction/binding.

## Stability

- With the base ballasted per `docs/mechanical_design.md`, extend the arm to
  full reach horizontally with the design payload and check the base does
  not lift at the front edge.
- Repeat during a fast HOME→extended move (the dynamic case the static
  calculation doesn't cover) — this is why the slew limit exists; if the
  base rocks noticeably, the 60°/s cap may need to come down for large
  moves specifically.

## Servo heating / current (thermal soak)

- Run a 10-minute repeated pick-and-place sequence (`software/sequences.py`)
  at the design payload.
- Check each servo case temperature by hand periodically — warm is normal,
  too hot to touch briefly is not.
- Log current draw over the run if the bench supply supports it; a rising
  idle-current trend at a fixed pose usually means a joint is being asked to
  hold against a growing mechanical bind (heat-related dimensional
  creep in a printed part is the usual cause) rather than an electrical
  fault.

## Regression checklist before calling V1 done

- [ ] All individual-joint tests pass
- [ ] `move_to()` repeatability measured and recorded (update
      `docs/kinematics.md` with the actual number if it differs materially
      from the ±5–8 mm estimate)
- [ ] Picks and places a pen 10 times running without a failed grip
- [ ] Stability check passes with ballast in place
- [ ] 10-minute thermal soak completes with no servo uncomfortably hot
- [ ] `docs/requirements.md` fallback triggers reviewed — confirm none of
      them fired during testing, or record which configuration change they
      led to
