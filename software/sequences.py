#!/usr/bin/env python3
"""Demo / test sequences built entirely on robot.arm.Arm's public API --
the same six calls the CLI and a future V2 agent use (docs/v2_ai_roadmap.md).

    python sequences.py wave              # simulated by default
    python sequences.py pick_place --port COM5
    python sequences.py thermal_soak --port COM5 --minutes 10

Referenced from docs/testing.md's payload and thermal-soak test procedures.
"""

from __future__ import annotations
import argparse
import time

from robot.arm import Arm

# Two points within the practical workspace (docs/kinematics.md: 130-290mm
# radius, z >= 10mm) used by the pick/place demos below. Adjust once the
# real arm exists and you have real desk coordinates to target.
PICK_XYZ = (0.220, 0.060, 0.015)
PLACE_XYZ = (0.180, -0.120, 0.015)


def wave(arm: Arm) -> None:
    """Simple range-of-motion demo -- sweeps base and gripper. Good first
    thing to run after Phase 5 firmware bring-up (docs/testing.md)."""
    arm.home()
    for base_deg in (-45, 45, -45, 0):
        arm.move_joints(base_deg, 70, -90)
        time.sleep(0.5)
    for pct in (100, 0, 100, 50):
        arm.grip(pct)
        time.sleep(0.3)
    arm.home()


def pick_and_place(arm: Arm, cycles: int = 1) -> None:
    """Move an object from PICK_XYZ to PLACE_XYZ and back, `cycles` times.
    This is the "picks and places a pen 10 times running" regression check
    in docs/testing.md when run with cycles=10 against a real object."""
    for i in range(cycles):
        print(f"cycle {i + 1}/{cycles}")
        arm.pickup(*PICK_XYZ)
        arm.place(*PLACE_XYZ)
        arm.pickup(*PLACE_XYZ)
        arm.place(*PICK_XYZ)
    arm.home()


def thermal_soak(arm: Arm, minutes: float = 10.0) -> None:
    """Repeated pick-and-place for a fixed duration -- docs/testing.md's
    thermal soak. Prints status() (current joint state) between cycles so
    a bench-supply ammeter reading can be correlated against arm pose by
    hand while it runs."""
    end_time = time.time() + minutes * 60
    cycle = 0
    while time.time() < end_time:
        cycle += 1
        remaining_min = (end_time - time.time()) / 60
        print(f"cycle {cycle}, {remaining_min:.1f} min remaining -- {arm.status()}")
        arm.pickup(*PICK_XYZ)
        arm.place(*PLACE_XYZ)
        arm.pickup(*PLACE_XYZ)
        arm.place(*PICK_XYZ)
    arm.home()
    print(f"thermal soak complete: {cycle} cycles")


SEQUENCES = {
    "wave": wave,
    "pick_place": pick_and_place,
    "thermal_soak": thermal_soak,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sequence", choices=SEQUENCES.keys())
    parser.add_argument("--port", default=None, help="serial port; omit to simulate")
    parser.add_argument("--cycles", type=int, default=1, help="for pick_place")
    parser.add_argument("--minutes", type=float, default=10.0, help="for thermal_soak")
    args = parser.parse_args()

    with Arm(port=args.port) as arm:
        if args.sequence == "wave":
            wave(arm)
        elif args.sequence == "pick_place":
            pick_and_place(arm, cycles=args.cycles)
        elif args.sequence == "thermal_soak":
            thermal_soak(arm, minutes=args.minutes)


if __name__ == "__main__":
    main()
