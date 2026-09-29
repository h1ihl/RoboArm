# Calculations

`engineering_calcs.py` is a runnable, self-checking reproduction of every
number in `docs/actuator_selection.md`, `docs/mechanical_design.md` and
`docs/planning_guide.pdf` — mass budget, joint torque, servo safety factors,
gripper force, base tipping stability, and printed-link deflection.

```
python calculations/engineering_calcs.py
```

Runs a self-test against the published figures first (raises `AssertionError`
if something no longer matches), then prints a full report. Change a
geometry or mass constant at the top of the file and re-run to see how every
downstream number moves — this is the tool to reach for before committing to
a fallback configuration (`docs/requirements.md`).

**Verified 2026-09-18** against Python 3.12 — all figures match the
published docs within rounding tolerance. This run is also what caught two
rounding slips in the original hand-worked design review before they made
it into the docs: the ballasted tipping safety factor is **2.22**, not 2.26,
and the wrist-servo torque is **0.58 kg·cm** (SF 3.08), not 0.51 (SF 3.5) —
both now corrected everywhere in `docs/`.
