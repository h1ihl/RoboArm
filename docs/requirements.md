# Requirements — Phase 1

## Scope

V1: a mechanically and electronically functional 3-DOF arm, controlled
manually or programmatically from a PC over USB. No camera, no vision, no AI
agent — that's V2, and V1's software is only required not to block it.

## Degrees of freedom

1. **Base yaw** — rotates the whole arm about a vertical axis.
2. **Shoulder** — raises/lowers the upper arm in the vertical plane the base
   is currently pointed at.
3. **Elbow** — folds the forearm relative to the upper arm, same plane.
4. **Gripper** (not counted as a DOF for positioning) — opens/closes a
   two-finger claw.
5. **Wrist pitch** — present in hardware (an SG90) but *not* an independently
   commanded axis. Firmware slaves it to `−(θ₁+θ₂)` so the gripper stays level
   in every pose. See `docs/kinematics.md`.

This is a positioner with 3 controllable spatial DOF (x, y, z) plus grip —
exactly matching brief §5/§6, no more.

## Target dimensions

| Parameter | Target (brief) | Chosen |
|---|---|---|
| Base footprint | 150–200 mm | 180 × 180 mm |
| Reach | 250–350 mm | 315 mm (315 mm kinematic max, 290 mm practical/software limit) |
| Overall height | 250–400 mm | ~340 mm (arm vertical, incl. gripper) |

Link lengths: shoulder height `h₀ = 75 mm`, upper arm `L₁ = 120 mm`, forearm
`L₂ = 120 mm`, wrist→TCP `L₃ = 75 mm`. Equal `L₁ = L₂` was a deliberate
choice — see `docs/mechanical_design.md` §Geometry.

## Payload

**Design payload: 55 g** at full 315 mm reach — covers pens, small tools,
USB sticks, small project boxes, small electronics. Not sized for anything
heavier; see `docs/actuator_selection.md` for the torque math that sets this
number, and `docs/requirements.md` §Fallback below for what changes if it
needs to move.

## Workspace

Reachable TCP envelope (vertical half-plane, swept ±90° about the base axis):

| Bound | Value | Set by |
|---|---|---|
| Outer radius | 315 mm kinematic / 290 mm practical | Link length / IK conditioning near full extension |
| Inner radius | 130 mm | Forearm-to-turret collision |
| Floor | z = 10 mm | Jaw-to-table clearance, enforced in firmware |
| Ceiling | z = 315 mm | Arm vertical |
| Base sweep | ±90° | No slip ring in V1 — full 360° would need one |

Usable desk area: an annular sector, 130–290 mm radius, 180° — about
0.09 m² directly in front of the base.

## Budget

- Target personal spend: **CAD $50–70**
- Absolute maximum: **CAD $100**
- Actual (Configuration B, typical lab sourcing): **≈ $59**
- Actual if buying literally everything: **≈ $90** — still under the ceiling

Full breakdown in `docs/bill_of_materials.md`.

## Servo requirements (summary — full derivation in actuator_selection.md)

| Joint | Servo | Required torque | Rated (6 V) | Safety factor |
|---|---|---:|---:|---:|
| Base | MG90S | 0.30 kg·cm | 2.20 kg·cm | 7.3 |
| Shoulder | MG996R | 4.51 kg·cm | 11.00 kg·cm | 2.44 |
| Elbow | MG996R | 2.00 kg·cm | 11.00 kg·cm | 5.50 |
| Wrist (slaved) | SG90 | 0.58 kg·cm | 1.80 kg·cm | 3.08 |
| Gripper | MG90S | 0.82 kg·cm | 2.20 kg·cm | 2.7 |

Floor for every joint: SF ≥ 2.0 — roughly the point below which a hobby
servo holding a static pose runs hot rather than idling near stall current.

## Decision gate (answered)

The design review (see `docs/planning_guide.pdf` §14 and its footer) posed
four questions before implementation started. Recorded answers:

1. **Configuration B**, built up from A rather than starting at D.
2. **SG90 slaved wrist: in.** $3 and 17 g for level jaws in every pose.
3. **University sourcing:** assume lab-available — controller, power supply
   (bench PSU for bring-up), fasteners, wire, bearings, filament. Budget the
   MG996R pair and MG90S/SG90 as purchased.
4. **315 mm / 55 g is the right target** — no known heavier payload
   requirement.

## Fallback trigger conditions

Per brief §22–25, don't jump configurations speculatively. Re-open this
document and move to the next configuration only if one of these actually
happens during build/test:

- **A → B**: if $50–55 genuinely isn't obtainable (all-purchase, no lab
  access) — shrink to 275 mm reach / 30 g payload instead of upgrading
  actuators.
- **B → D**: only if a joint measures below SF 1.5 *after* assembly (not
  predicted — measured), or repeated stalls/overheating occur at rated
  payload after the compliant-jaw and slew-limit mitigations are in place.
- **Any → C**: whenever a lab visit confirms specific components are on the
  shelf; swap in, keep everything else.

See `docs/planning_guide.pdf` §15 (component fallbacks) and §14 (comparison
table + decision trail) for the full reasoning.
