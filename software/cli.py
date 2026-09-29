#!/usr/bin/env python3
"""Interactive control shell -- the manual-control half of
docs/electronics.md's "PC -> USB -> Microcontroller -> Servos" architecture
(brief section 11). Thin wrapper around robot.arm.Arm; every command here
maps to one of its six public calls plus a few bring-up/debug helpers.

    python cli.py --port COM5
    python cli.py                 # no --port: runs against a simulated arm

Type `help` at the prompt for the command list.
"""

from __future__ import annotations
import argparse
import cmd
import sys

from robot.arm import Arm
from robot.kinematics import UnreachableError
from robot.transport import TransportError


class ArmShell(cmd.Cmd):
    intro = "Desk Arm control shell. Type `help` for commands, `quit` to exit."
    prompt = "arm> "

    def __init__(self, arm: Arm):
        super().__init__()
        self.arm = arm

    # -- motion -----------------------------------------------------------
    def do_home(self, _arg):
        "home -- slew to the safe folded pose"
        self._try(self.arm.home)

    def do_j(self, arg):
        "j <base> <shoulder> <elbow> -- absolute joint angles, degrees"
        try:
            base, shoulder, elbow = (float(v) for v in arg.split())
        except ValueError:
            print("usage: j <base> <shoulder> <elbow>")
            return
        self._try(self.arm.move_joints, base, shoulder, elbow)

    def do_move(self, arg):
        "move <x_mm> <y_mm> <z_mm> -- Cartesian move, validated + interpolated"
        try:
            x, y, z = (float(v) / 1000.0 for v in arg.split())
        except ValueError:
            print("usage: move <x_mm> <y_mm> <z_mm>")
            return
        self._try(self.arm.move_to, x, y, z)

    def do_grip(self, arg):
        "grip <0-100> -- 0 closed, 100 open"
        try:
            pct = int(arg)
        except ValueError:
            print("usage: grip <0-100>")
            return
        self._try(self.arm.grip, pct)

    def do_pickup(self, arg):
        "pickup <x_mm> <y_mm> <z_mm> -- approach, descend, close, lift"
        try:
            x, y, z = (float(v) / 1000.0 for v in arg.split())
        except ValueError:
            print("usage: pickup <x_mm> <y_mm> <z_mm>")
            return
        self._try(self.arm.pickup, x, y, z)

    def do_place(self, arg):
        "place <x_mm> <y_mm> <z_mm> -- approach, descend, release, retreat"
        try:
            x, y, z = (float(v) / 1000.0 for v in arg.split())
        except ValueError:
            print("usage: place <x_mm> <y_mm> <z_mm>")
            return
        self._try(self.arm.place, x, y, z)

    # -- bring-up / debug (docs/assembly.md) ----------------------------
    def do_stop(self, _arg):
        "stop -- freeze at the current position"
        self._try(self.arm.stop)

    def do_release(self, _arg):
        "release -- detach all servos so the arm can be moved by hand"
        self._try(self.arm.release)

    def do_status(self, _arg):
        "status -- print the arm's current joint angles / pulse widths"
        self._try(lambda: print(self.arm.status()))

    def do_raw(self, arg):
        "raw <B|S|E|W|G> <microseconds> -- calibration-only raw pulse (docs/assembly.md)"
        try:
            ch, us = arg.split()
            us = int(us)
        except ValueError:
            print("usage: raw <B|S|E|W|G> <microseconds>")
            return
        self._try(self.arm.raw_pulse, ch, us)

    # -- shell plumbing ---------------------------------------------------
    def do_quit(self, _arg):
        "quit -- exit"
        return True

    do_exit = do_quit

    def _try(self, fn, *args):
        try:
            fn(*args)
            print("OK")
        except (UnreachableError, ValueError) as e:
            print(f"rejected: {e}")
        except TransportError as e:
            print(f"transport error: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", default=None,
                         help="serial port (e.g. COM5). Omit to run against a simulated arm.")
    parser.add_argument("--verbose", action="store_true",
                         help="print every command sent and reply received")
    args = parser.parse_args()

    arm = Arm(port=args.port, verbose=args.verbose)
    try:
        arm.connect()
    except TransportError as e:
        print(f"could not connect: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        ArmShell(arm).cmdloop()
    finally:
        arm.close()


if __name__ == "__main__":
    main()
