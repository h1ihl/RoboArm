"""robot.arm.Arm -- the six calls everything else is meant to use.

This is the V1 <-> V2 contract (docs/v2_ai_roadmap.md): the CLI
(software/cli.py), the demo sequences (software/sequences.py), and
eventually a V2 agent all drive the robot through this class and nothing
lower-level. If V2 ever needs to reach past this API to work, that's a
sign the API was drawn in the wrong place -- not a reason to add a
backdoor.

    from robot.arm import Arm

    with Arm(port="COM5") as arm:
        arm.home()
        arm.pickup(0.200, 0.050, 0.015)
        arm.place(0.150, -0.100, 0.015)

Pass port=None to run against a SimulatedTransport (see robot.transport) --
useful for exercising sequences before any hardware is wired up.
"""

from __future__ import annotations
import time
from typing import Optional

from . import config
from .kinematics import Joints, Pose, fk, ik, reachable, path_safe, UnreachableError
from .trajectory import interpolate_joints
from .transport import SerialTransport, SimulatedTransport, TransportError


class Arm:
    def __init__(self, port: Optional[str] = None, verbose: bool = False):
        self._verbose = verbose
        self._transport = SerialTransport(port) if port else SimulatedTransport()
        # Assumed starting pose -- the ESP32 doesn't report position on
        # connect, so this matches its HOME_*_DEG defaults (config.py /
        # firmware/arm_firmware/arm_firmware.ino) until the first move.
        self._current = Joints(config.HOME_BASE_DEG, config.HOME_SHOULDER_DEG,
                                config.HOME_ELBOW_DEG, 0.0)

    # -- lifecycle ------------------------------------------------------
    def connect(self) -> None:
        self._transport.connect()

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> "Arm":
        self.connect()
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # -- the six public calls --------------------------------------------
    def home(self) -> None:
        """Slew to the safe folded pose (firmware-defined -- see
        firmware/arm_firmware/arm_firmware.ino HOME_*_DEG)."""
        self._send("HOME")
        self._current = Joints(config.HOME_BASE_DEG, config.HOME_SHOULDER_DEG,
                                config.HOME_ELBOW_DEG, 0.0)

    def move_joints(self, base_deg: float, shoulder_deg: float, elbow_deg: float) -> None:
        """Absolute joint command. Firmware computes and clamps the slaved
        wrist angle itself; software validates against the same limits
        first so a bad call fails locally instead of round-tripping to
        the ESP32 to find out."""
        self._check_joint_limits(base_deg, shoulder_deg, elbow_deg)
        self._send(f"J {base_deg:.1f} {shoulder_deg:.1f} {elbow_deg:.1f}")
        self._current = Joints(base_deg, shoulder_deg, elbow_deg,
                                -(shoulder_deg + elbow_deg))

    def move_to(self, x: float, y: float, z: float, steps: int = config.CARTESIAN_PATH_STEPS) -> None:
        """Cartesian move, fully validated before a single servo moves
        (docs/kinematics.md's four-stage check) and interpolated in joint
        space with easing (robot.trajectory) rather than jumping straight
        to the target."""
        ok, reason = reachable(x, y, z)
        if not ok:
            raise UnreachableError(reason)

        target = ik(x, y, z)
        current_pose = fk(self._current.base_deg, self._current.shoulder_deg, self._current.elbow_deg)
        path_ok, path_reason = path_safe(current_pose, Pose(x, y, z), steps=steps)
        if not path_ok:
            raise UnreachableError(f"path rejected: {path_reason}")

        for waypoint in interpolate_joints(self._current, target, steps):
            self.move_joints(waypoint.base_deg, waypoint.shoulder_deg, waypoint.elbow_deg)

    def grip(self, percent: int) -> None:
        """0 = closed, 100 = open."""
        if not (0 <= percent <= 100):
            raise ValueError(f"grip percent {percent} outside [0, 100]")
        self._send(f"G {percent}")

    def pickup(self, x: float, y: float, z: float,
               approach_height: float = 0.040, settle_s: float = 0.3) -> None:
        """Approach from above, descend, close, lift -- see
        docs/v2_ai_roadmap.md for why this shape (rather than a direct
        move-and-close) is what a future vision-driven pick also wants:
        the approach point only needs an (x, y) from a camera plus a
        fixed height, sidestepping most depth-estimation error."""
        self.grip(100)
        self.move_to(x, y, z + approach_height)
        self.move_to(x, y, z)
        time.sleep(settle_s)
        self.grip(0)
        time.sleep(settle_s)
        self.move_to(x, y, z + approach_height)

    def place(self, x: float, y: float, z: float,
              approach_height: float = 0.040, settle_s: float = 0.3) -> None:
        """Mirror of pickup(): approach from above, descend, release, retreat."""
        self.move_to(x, y, z + approach_height)
        self.move_to(x, y, z)
        time.sleep(settle_s)
        self.grip(100)
        time.sleep(settle_s)
        self.move_to(x, y, z + approach_height)

    # -- lower-level, used by the CLI for bring-up/debugging ------------------
    def stop(self) -> None:
        self._send("STOP")

    def release(self) -> None:
        """Detach all servos -- lets the arm be moved by hand
        (docs/assembly.md calibration procedure)."""
        self._send("REL")

    def status(self) -> str:
        return self._send("STAT")

    def raw_pulse(self, channel: str, microseconds: int) -> None:
        """Calibration-only escape hatch -- still bounded by
        firmware/arm_firmware/limits.h on the hardware side regardless of
        what's sent here."""
        self._send(f"US {channel} {microseconds}")

    # -- internals --------------------------------------------------------
    def _check_joint_limits(self, base_deg: float, shoulder_deg: float, elbow_deg: float) -> None:
        if not (config.BASE_MIN_DEG <= base_deg <= config.BASE_MAX_DEG):
            raise ValueError(f"base {base_deg} outside [{config.BASE_MIN_DEG}, {config.BASE_MAX_DEG}]")
        if not (config.SHOULDER_MIN_DEG <= shoulder_deg <= config.SHOULDER_MAX_DEG):
            raise ValueError(f"shoulder {shoulder_deg} outside [{config.SHOULDER_MIN_DEG}, {config.SHOULDER_MAX_DEG}]")
        if not (config.ELBOW_MIN_DEG <= elbow_deg <= config.ELBOW_MAX_DEG):
            raise ValueError(f"elbow {elbow_deg} outside [{config.ELBOW_MIN_DEG}, {config.ELBOW_MAX_DEG}]")

    def _send(self, line: str) -> str:
        if self._verbose:
            print(f">> {line}")
        try:
            reply = self._transport.send(line)
        except TransportError:
            raise
        if self._verbose:
            print(f"<< {reply}")
        return reply
