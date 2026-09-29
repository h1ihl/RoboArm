"""Single place to tune the robot: link lengths, joint limits, workspace
bounds, and per-servo calibration. Everything else in software/ imports
from here rather than hard-coding numbers, so Configurations A/B/C/D
(docs/requirements.md) differ by editing this file, not by editing code.

Values below are Configuration B (docs/requirements.md), and mirror the
constants in firmware/arm_firmware/limits.h -- if you change a range here,
change it there too, and vice versa. The firmware's copy is authoritative
for what the hardware will actually accept; this copy lets software reject
bad targets before anything reaches the serial port (docs/kinematics.md
validation order).
"""

from __future__ import annotations
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Geometry, metres (docs/requirements.md / docs/kinematics.md)
# ---------------------------------------------------------------------------
L1 = 0.120   # upper arm
L2 = 0.120   # forearm
L3 = 0.075   # wrist -> TCP
H0 = 0.075   # shoulder height above the table


# ---------------------------------------------------------------------------
# Joint limits, degrees (must match firmware/arm_firmware/limits.h)
# ---------------------------------------------------------------------------
BASE_MIN_DEG, BASE_MAX_DEG = -90.0, 90.0
SHOULDER_MIN_DEG, SHOULDER_MAX_DEG = 0.0, 110.0
ELBOW_MIN_DEG, ELBOW_MAX_DEG = -130.0, 0.0
WRIST_MIN_DEG, WRIST_MAX_DEG = -120.0, 30.0

# Safe folded pose -- must match HOME_*_DEG in
# firmware/arm_firmware/arm_firmware.ino. robot.arm.Arm assumes the
# physical (or simulated) arm starts here until the first STAT reply is
# read back, since the ESP32 doesn't report its pose on connect.
HOME_BASE_DEG = 0.0
HOME_SHOULDER_DEG = 60.0
HOME_ELBOW_DEG = -90.0


# ---------------------------------------------------------------------------
# Workspace bounds, metres (docs/kinematics.md / docs/requirements.md)
# ---------------------------------------------------------------------------
WORKSPACE_R_MIN = 0.130   # forearm-to-turret collision boundary
WORKSPACE_R_MAX = 0.290   # practical outer limit (290mm; kinematic max is 315mm --
                           # the last 25mm is a near-singularity, see docs/kinematics.md)
TABLE_CLEARANCE_Z = 0.010  # minimum jaw height above the table


# ---------------------------------------------------------------------------
# Motion
# ---------------------------------------------------------------------------
MAX_SLEW_DEG_S = 60.0          # must match firmware/arm_firmware/slew.h
CARTESIAN_PATH_STEPS = 20      # waypoints checked per move_to() (docs/kinematics.md)


# ---------------------------------------------------------------------------
# Per-servo calibration -- fill in during docs/assembly.md's calibration
# step. (min_us, max_us) is that channel's usable pulse range; angle_offset_deg
# is added to the *commanded* angle before it's sent, to correct for the
# servo not landing exactly where the geometry says 0 degrees should be.
# Defaults below are uncalibrated placeholders -- the wide-open
# 500-2500us range and zero offset -- and MUST be replaced with real
# measurements before trusting move_to() accuracy.
# ---------------------------------------------------------------------------

@dataclass
class ServoCal:
    channel: str          # matches firmware US <ch> codes: B/S/E/W/G
    min_us: int
    max_us: int
    angle_offset_deg: float = 0.0


SERVO_CAL = {
    "base":     ServoCal("B", 900, 2100),
    "shoulder": ServoCal("S", 700, 2400),
    "elbow":    ServoCal("E", 700, 2400),
    "wrist":    ServoCal("W", 900, 2100),
    "gripper":  ServoCal("G", 1000, 1900),
}


# ---------------------------------------------------------------------------
# Transport defaults
# ---------------------------------------------------------------------------
DEFAULT_BAUD = 115200
DEFAULT_TIMEOUT_S = 2.0
