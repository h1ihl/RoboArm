"""Eased interpolation between two joint poses, for robot.arm.move_to()'s
Cartesian moves. Firmware already slew-limits each joint
(firmware/arm_firmware/slew.h) -- this module is about the *shape* of the
motion the PC asks for, not a second safety layer; use robot.kinematics's
reachable()/path_safe() for safety checks.
"""

from __future__ import annotations
from typing import Callable, Iterator
from .kinematics import Joints


def ease_in_out(t: float) -> float:
    """Smoothstep easing, t in [0, 1] -> eased t in [0, 1]. Gentler start
    and stop than a linear ramp -- matters for a desk arm because a linear
    ramp's velocity is discontinuous at both ends, which is exactly what
    the firmware slew limiter has to clip, producing a small jerk."""
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def interpolate_joints(j0: Joints, j1: Joints, steps: int,
                        easing: Callable[[float], float] = ease_in_out) -> Iterator[Joints]:
    """Yield `steps + 1` Joints from j0 to j1 inclusive, eased in the
    joint-angle domain (simple and sufficient at this arm's speeds -- see
    docs/kinematics.md on why dynamics are not modelled explicitly)."""
    for i in range(steps + 1):
        t = easing(i / steps) if steps > 0 else 1.0
        yield Joints(
            base_deg=j0.base_deg + t * (j1.base_deg - j0.base_deg),
            shoulder_deg=j0.shoulder_deg + t * (j1.shoulder_deg - j0.shoulder_deg),
            elbow_deg=j0.elbow_deg + t * (j1.elbow_deg - j0.elbow_deg),
            wrist_deg=j0.wrist_deg + t * (j1.wrist_deg - j0.wrist_deg),
        )
