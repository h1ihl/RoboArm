"""Forward and inverse kinematics for the 3-DOF arm + slaved wrist.

Derivation and the reasoning behind every design choice here (why the
elbow-up root, why the wrist is slaved rather than commanded, why
validation runs in this exact order) is in docs/kinematics.md -- this file
is the implementation of that document, not an independent source of truth.

No hardware needed to use or test this module:

    python -m robot.kinematics

runs a self-test that round-trips fk(ik(target)) for several points across
the workspace and checks that the validation functions reject the cases
docs/kinematics.md says they should.
"""

from __future__ import annotations
from dataclasses import dataclass
from math import atan2, acos, sin, cos, sqrt, degrees, radians, isclose

from . import config


class UnreachableError(ValueError):
    """Raised by ik() when a target has no valid joint solution."""


@dataclass
class Pose:
    x: float
    y: float
    z: float


@dataclass
class Joints:
    base_deg: float
    shoulder_deg: float
    elbow_deg: float
    wrist_deg: float


# ---------------------------------------------------------------------------
# Forward kinematics
# ---------------------------------------------------------------------------

def fk(base_deg: float, shoulder_deg: float, elbow_deg: float) -> Pose:
    """Joint angles -> end-effector position. Wrist is always the slaved
    angle -(shoulder+elbow), so it contributes no separate trig term to r
    (docs/kinematics.md) -- L3 just adds directly to the radius."""
    t0, t1, t2 = radians(base_deg), radians(shoulder_deg), radians(elbow_deg)
    r = config.L1 * cos(t1) + config.L2 * cos(t1 + t2) + config.L3
    z = config.H0 + config.L1 * sin(t1) + config.L2 * sin(t1 + t2)
    x = r * cos(t0)
    y = r * sin(t0)
    return Pose(x, y, z)


def wrist_deg_for(shoulder_deg: float, elbow_deg: float) -> float:
    """The slaved wrist angle that keeps the gripper level. Firmware
    computes and clamps this independently as a safety net
    (firmware/arm_firmware/arm_firmware.ino); this is the same formula so
    software-side reachability checks agree with what the hardware will
    actually do."""
    w = -(shoulder_deg + elbow_deg)
    return max(config.WRIST_MIN_DEG, min(config.WRIST_MAX_DEG, w))


# ---------------------------------------------------------------------------
# Inverse kinematics
# ---------------------------------------------------------------------------

def ik(x: float, y: float, z: float) -> Joints:
    """Desired (x, y, z) -> joint angles. Raises UnreachableError with a
    specific reason rather than returning a best-effort answer -- callers
    (robot.arm.Arm) are expected to validate with reachable() first and
    treat this as a hard boundary, not something to catch-and-clamp."""
    base_deg = degrees(atan2(y, x))

    r_prime = sqrt(x * x + y * y) - config.L3
    z_prime = z - config.H0

    L1, L2 = config.L1, config.L2
    denom = 2 * L1 * L2
    if denom == 0:
        raise UnreachableError("degenerate link lengths")

    d = (r_prime**2 + z_prime**2 - L1**2 - L2**2) / denom
    if d < -1.0 or d > 1.0:
        raise UnreachableError(
            f"target ({x*1000:.0f}, {y*1000:.0f}, {z*1000:.0f}) mm is outside "
            f"the two-link reach envelope (|D|={d:.3f} > 1)"
        )

    elbow_rad = -acos(d)  # negative root = elbow-up (docs/kinematics.md)
    shoulder_rad = atan2(z_prime, r_prime) - atan2(
        L2 * sin(elbow_rad), L1 + L2 * cos(elbow_rad)
    )

    shoulder_deg = degrees(shoulder_rad)
    elbow_deg = degrees(elbow_rad)
    wrist_deg = wrist_deg_for(shoulder_deg, elbow_deg)

    return Joints(base_deg, shoulder_deg, elbow_deg, wrist_deg)


# ---------------------------------------------------------------------------
# Validation -- run in this order before anything moves (docs/kinematics.md)
# ---------------------------------------------------------------------------

def reachable(x: float, y: float, z: float) -> tuple[bool, str]:
    """1) Reachability, 2) joint limits, 3) table clearance. Returns
    (ok, reason) -- reason is "" when ok."""
    r = sqrt(x * x + y * y)
    if not (config.WORKSPACE_R_MIN <= r <= config.WORKSPACE_R_MAX):
        return False, (
            f"radius {r*1000:.0f} mm outside workspace "
            f"[{config.WORKSPACE_R_MIN*1000:.0f}, {config.WORKSPACE_R_MAX*1000:.0f}] mm"
        )

    if z < config.TABLE_CLEARANCE_Z:
        return False, f"z={z*1000:.1f} mm below table clearance floor ({config.TABLE_CLEARANCE_Z*1000:.0f} mm)"

    try:
        j = ik(x, y, z)
    except UnreachableError as e:
        return False, str(e)

    if not (config.BASE_MIN_DEG <= j.base_deg <= config.BASE_MAX_DEG):
        return False, f"base {j.base_deg:.1f} deg outside [{config.BASE_MIN_DEG}, {config.BASE_MAX_DEG}]"
    if not (config.SHOULDER_MIN_DEG <= j.shoulder_deg <= config.SHOULDER_MAX_DEG):
        return False, f"shoulder {j.shoulder_deg:.1f} deg outside [{config.SHOULDER_MIN_DEG}, {config.SHOULDER_MAX_DEG}]"
    if not (config.ELBOW_MIN_DEG <= j.elbow_deg <= config.ELBOW_MAX_DEG):
        return False, f"elbow {j.elbow_deg:.1f} deg outside [{config.ELBOW_MIN_DEG}, {config.ELBOW_MAX_DEG}]"

    return True, ""


def path_safe(p0: Pose, p1: Pose, steps: int = config.CARTESIAN_PATH_STEPS) -> tuple[bool, str]:
    """4) Path check: a straight line between two individually-legal poses
    can still pass through an illegal one (docs/kinematics.md) -- interpolate
    and validate every waypoint, not just the endpoints."""
    for i in range(steps + 1):
        t = i / steps
        x = p0.x + t * (p1.x - p0.x)
        y = p0.y + t * (p1.y - p0.y)
        z = p0.z + t * (p1.z - p0.z)
        ok, reason = reachable(x, y, z)
        if not ok:
            return False, f"waypoint {i}/{steps} at t={t:.2f}: {reason}"
    return True, ""


# ---------------------------------------------------------------------------
# Self-test -- no hardware required
# ---------------------------------------------------------------------------

def _self_test() -> None:
    print("=" * 72)
    print("KINEMATICS SELF-TEST")
    print("=" * 72)

    test_points = [
        (0.200, 0.000, 0.100),
        (0.150, 0.150, 0.150),
        (0.000, 0.220, 0.050),
        (0.150, -0.120, 0.180),  # base sweep is +/-90 deg (docs/requirements.md) -- x must stay positive
        (0.260, 0.000, 0.080),
    ]

    for x, y, z in test_points:
        ok, reason = reachable(x, y, z)
        assert ok, f"expected {(x, y, z)} reachable, got: {reason}"
        j = ik(x, y, z)
        p = fk(j.base_deg, j.shoulder_deg, j.elbow_deg)
        err_mm = sqrt((p.x - x) ** 2 + (p.y - y) ** 2 + (p.z - z) ** 2) * 1000
        assert err_mm < 0.5, f"round-trip error {err_mm:.3f} mm too large for {(x, y, z)}"
        print(f"  target ({x*1000:6.1f}, {y*1000:6.1f}, {z*1000:6.1f}) mm  ->  "
              f"base {j.base_deg:6.1f}  shoulder {j.shoulder_deg:6.1f}  "
              f"elbow {j.elbow_deg:6.1f}  wrist {j.wrist_deg:6.1f}  "
              f"(round-trip err {err_mm:.4f} mm)")

    # Rejection cases, one per validation stage in docs/kinematics.md
    ok, reason = reachable(0.500, 0.000, 0.100)
    assert not ok, "expected out-of-reach target to be rejected"
    print(f"  correctly rejected out-of-reach target: {reason}")

    ok, reason = reachable(0.050, 0.050, 0.100)
    assert not ok, "expected inner-boundary collision target to be rejected"
    print(f"  correctly rejected inner-collision target: {reason}")

    ok, reason = reachable(0.200, 0.000, 0.002)
    assert not ok, "expected below-table target to be rejected"
    print(f"  correctly rejected below-table target: {reason}")

    # Two individually-reachable endpoints (base +/-75 deg, same radius)
    # whose straight-line path swings past the base axis and crosses a
    # joint limit partway through -- exactly the case docs/kinematics.md
    # warns endpoint-only validation would miss.
    p0 = Pose(0.0388, 0.1449, 0.150)
    p1 = Pose(0.0388, -0.1449, 0.150)
    assert reachable(p0.x, p0.y, p0.z)[0], "test setup: p0 should itself be reachable"
    assert reachable(p1.x, p1.y, p1.z)[0], "test setup: p1 should itself be reachable"
    ok, reason = path_safe(p0, p1)
    assert not ok, "expected path through the inner-radius collision zone to be rejected"
    print(f"  correctly rejected unsafe path between two legal endpoints: {reason}")

    print("\nAll kinematics self-tests passed.")


if __name__ == "__main__":
    _self_test()
