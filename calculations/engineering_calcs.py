#!/usr/bin/env python3
"""
Engineering calculations for the desk arm (Configuration B).

Reproduces, and lets you re-check, every number quoted in docs/
actuator_selection.md, docs/mechanical_design.md and docs/planning_guide.pdf:
mass budget -> joint torque -> servo safety factors -> gripper force ->
base tipping stability -> printed-link deflection.

Run directly to print a full report:

    python calculations/engineering_calcs.py

Change a geometry/mass constant below and re-run to see how every
downstream number moves -- this is the "does the math still work" check
before committing to a fallback configuration (see docs/requirements.md).
"""

from __future__ import annotations
from dataclasses import dataclass
from math import isclose

G = 9.81              # m/s^2
NM_TO_KGCM = 10.1972  # 1 N*m = 10.1972 kgf*cm


def nm_to_kgcm(nm: float) -> float:
    return nm * NM_TO_KGCM


# ---------------------------------------------------------------------------
# Geometry (Configuration B -- see docs/requirements.md / cad/README.md)
# ---------------------------------------------------------------------------

L1 = 0.120   # upper arm, m
L2 = 0.120   # forearm, m
L3 = 0.075   # wrist -> TCP, m
H0 = 0.075   # shoulder height, m


# ---------------------------------------------------------------------------
# Mass budget -- horizontal distance from the SHOULDER axis, arm fully
# extended (worst case for every downstream load). Distances double as the
# "from shoulder" column; the elbow-torque calc re-expresses them relative
# to the elbow axis by subtracting L1.
# ---------------------------------------------------------------------------

@dataclass
class MassItem:
    name: str
    mass_kg: float
    dist_from_shoulder_m: float


MOVING_ASSEMBLY = [
    MassItem("Upper-arm link pair + spacers", 0.030, 0.060),
    MassItem("Elbow servo (MG996R) + bracket", 0.065, 0.120),
    MassItem("Forearm link pair + spacers", 0.025, 0.180),
    MassItem("Wrist servo (SG90) + bracket", 0.017, 0.250),
    MassItem("Gripper assembly (MG90S + jaws)", 0.032, 0.285),
    MassItem("Design payload", 0.055, 0.320),
]

BASE_ASSEMBLY_MASS_KG = (
    0.100    # base plate
    + 0.060  # column + turret
    + 0.014  # base servo
    + 0.055  # shoulder servo
    + 0.040  # hardware
)  # = 0.269 kg, EXCLUDES ballast


def mass_budget_report():
    print("=" * 72)
    print("MASS BUDGET  (distances from shoulder axis, arm fully extended)")
    print("=" * 72)
    total_mass = 0.0
    total_moment = 0.0
    for item in MOVING_ASSEMBLY:
        moment_g_mm = item.mass_kg * 1000 * item.dist_from_shoulder_m * 1000
        total_mass += item.mass_kg
        total_moment += moment_g_mm
        print(f"  {item.name:<36s} {item.mass_kg*1000:6.0f} g  "
              f"{item.dist_from_shoulder_m*1000:6.0f} mm  "
              f"{moment_g_mm:8.0f} g*mm")
    com_mm = total_moment / (total_mass * 1000)
    print("-" * 72)
    print(f"  {'Moving assembly total':<36s} {total_mass*1000:6.0f} g  "
          f"CoM {com_mm:5.1f} mm  {total_moment:8.0f} g*mm")
    print(f"  Base assembly (excl. ballast): {BASE_ASSEMBLY_MASS_KG*1000:.0f} g")
    print()
    return total_mass, total_moment / 1000  # kg, kg*mm


# ---------------------------------------------------------------------------
# Joint torque
# ---------------------------------------------------------------------------

def shoulder_torque_nm() -> float:
    """Static holding torque, arm horizontal at full extension."""
    return G * sum(item.mass_kg * item.dist_from_shoulder_m
                   for item in MOVING_ASSEMBLY)


def elbow_torque_nm() -> float:
    """Static holding torque about the elbow axis (subtract L1 from each
    shoulder-referenced distance; the upper-arm link itself contributes
    ~0 net moment about the elbow by symmetry and is omitted, matching
    docs/actuator_selection.md)."""
    contributions = {
        "Forearm link pair + spacers": (0.025, 0.180 - L1),
        "Wrist servo (SG90) + bracket": (0.017, 0.250 - L1),
        "Gripper assembly (MG90S + jaws)": (0.032, 0.285 - L1),
        "Design payload": (0.055, 0.320 - L1),
    }
    return G * sum(m * d for m, d in contributions.values())


def base_yaw_torque_nm(inertia_kgm2: float = 0.0056,
                        alpha_rad_s2: float = 3.5,
                        drag_margin_kgcm: float = 0.10) -> float:
    """Inertial + bearing-drag estimate (no gravity term for a vertical
    axis). drag_margin is an engineering allowance, not derived."""
    accel_torque = inertia_kgm2 * alpha_rad_s2
    return accel_torque + drag_margin_kgcm / NM_TO_KGCM


def wrist_torque_nm() -> float:
    """Slaved wrist servo -- static holding torque about the wrist pivot
    (at L1+L2 = 240 mm from the shoulder), same method as shoulder/elbow:
    mass x horizontal distance from the joint axis. Matches the 0.58 kg*cm
    figure in docs/actuator_selection.md."""
    wrist_pivot_from_shoulder_m = L1 + L2
    contributions = {
        "Gripper assembly (MG90S + jaws)": (0.032, 0.285 - wrist_pivot_from_shoulder_m),
        "Design payload": (0.055, 0.320 - wrist_pivot_from_shoulder_m),
    }
    return G * sum(m * d for m, d in contributions.values())


@dataclass
class ServoSpec:
    name: str
    rated_kgcm_6v: float


SERVOS = {
    "base": ServoSpec("MG90S", 2.20),
    "shoulder": ServoSpec("MG996R", 11.00),
    "elbow": ServoSpec("MG996R", 11.00),
    "wrist": ServoSpec("SG90", 1.80),
    "gripper": ServoSpec("MG90S", 2.20),
}


def gripper_servo_torque_nm() -> float:
    jaw_torque_nm = JAW_FORCE_N * JAW_PIVOT_ARM_M
    return jaw_torque_nm / DRIVE_REDUCTION


def torque_report():
    print("=" * 72)
    print("JOINT TORQUE AND SAFETY FACTOR  (6.0 V rated)")
    print("=" * 72)
    required = {
        "base": base_yaw_torque_nm(),
        "shoulder": shoulder_torque_nm(),
        "elbow": elbow_torque_nm(),
        "wrist": wrist_torque_nm(),
        "gripper": gripper_servo_torque_nm(),
    }
    for joint, nm in required.items():
        spec = SERVOS[joint]
        req_kgcm = nm_to_kgcm(nm)
        sf = spec.rated_kgcm_6v / req_kgcm
        floor_flag = "OK" if sf >= 2.0 else "BELOW SF 2.0 FLOOR"
        print(f"  {joint:<10s} {spec.name:<8s} req {req_kgcm:5.2f} kg*cm  "
              f"rated {spec.rated_kgcm_6v:5.2f} kg*cm  SF {sf:4.2f}  {floor_flag}")
    print()


# ---------------------------------------------------------------------------
# Gripper
# ---------------------------------------------------------------------------

JAW_FORCE_N = 4.0
JAW_PIVOT_ARM_M = 0.030
DRIVE_REDUCTION = 1.5  # jaw crank (18mm) : servo crank (12mm)


def min_grip_force_report():
    mu = 0.5
    payload_kg = 0.055
    f_min = payload_kg * G / (2 * mu)
    print("=" * 72)
    print("GRIPPER FORCE")
    print("=" * 72)
    print(f"  Minimum clamp force (mu={mu}, {payload_kg*1000:.0f} g payload): "
          f"{f_min:.2f} N")
    print(f"  Design target: {JAW_FORCE_N:.1f} N per jaw "
          f"({JAW_FORCE_N/f_min:.1f}x the physics minimum)")
    print(f"  Servo torque required: {nm_to_kgcm(gripper_servo_torque_nm()):.2f} kg*cm")
    print()


# ---------------------------------------------------------------------------
# Base stability (tipping)
# ---------------------------------------------------------------------------

TIP_EDGE_FROM_BASE_AXIS_M = 0.090
SHOULDER_OFFSET_FROM_BASE_AXIS_M = 0.010
BALLAST_KG = 0.400


def stability_report():
    print("=" * 72)
    print("BASE STABILITY (tipping about the front edge)")
    print("=" * 72)
    moving_mass_kg = sum(i.mass_kg for i in MOVING_ASSEMBLY)
    com_from_shoulder_m = (
        sum(i.mass_kg * i.dist_from_shoulder_m for i in MOVING_ASSEMBLY)
        / moving_mass_kg
    )
    com_from_base_axis_m = com_from_shoulder_m + SHOULDER_OFFSET_FROM_BASE_AXIS_M

    m_over = moving_mass_kg * G * (com_from_base_axis_m - TIP_EDGE_FROM_BASE_AXIS_M)
    print(f"  Moving assembly: {moving_mass_kg*1000:.0f} g at "
          f"{com_from_base_axis_m*1000:.0f} mm from base axis")
    print(f"  Overturning moment: {m_over:.3f} N*m")

    for ballast_kg, label in [(0.0, "no ballast"), (BALLAST_KG, "with ballast")]:
        base_mass = BASE_ASSEMBLY_MASS_KG + ballast_kg
        m_rest = base_mass * G * TIP_EDGE_FROM_BASE_AXIS_M
        sf = m_rest / m_over
        verdict = "OK" if sf >= 1.0 else "TIPS"
        print(f"  {label:<14s} base mass {base_mass*1000:5.0f} g  "
              f"restoring {m_rest:.3f} N*m  SF {sf:4.2f}  {verdict}")
    print()


# ---------------------------------------------------------------------------
# Printed-link deflection (upper arm, twin 20 x 3 mm plates)
# ---------------------------------------------------------------------------

def link_deflection_mm(force_n: float = 1.3, length_mm: float = 120,
                        plate_depth_mm: float = 20, plate_thickness_mm: float = 3,
                        n_plates: int = 2, e_mpa: float = 2500) -> tuple[float, float]:
    """Twin plates on edge: plate_depth_mm (20 mm) is the beam's depth IN
    THE BENDING DIRECTION (cubed in I), plate_thickness_mm (3 mm) is the
    width perpendicular to bending. E is a de-rated effective modulus for
    a printed part (bulk PLA is ~3.5 GPa; 2.5 GPa accounts for layer
    adhesion / infill, matching docs/mechanical_design.md)."""
    i_mm4 = n_plates * (plate_thickness_mm * plate_depth_mm ** 3) / 12
    deflection_mm = (force_n * length_mm ** 3) / (3 * e_mpa * i_mm4)
    return deflection_mm, i_mm4


def deflection_report():
    print("=" * 72)
    print("UPPER-ARM LINK DEFLECTION")
    print("=" * 72)
    deflection_mm, i_mm4 = link_deflection_mm()
    print(f"  Second moment of area I = {i_mm4:.0f} mm^4")
    print(f"  Tip deflection at 1.3 N tip load, 120 mm span: {deflection_mm:.3f} mm")
    print("  (For reference: MG996R gear backlash is ~1.5 deg, or roughly")
    print("   6 mm at the gripper on a 240 mm shoulder+elbow lever -- the")
    print("   structure is far stiffer than the servos it is bolted to.)")
    print()


# ---------------------------------------------------------------------------
# Self-checks against the numbers published in docs/
# ---------------------------------------------------------------------------

def self_test():
    assert isclose(nm_to_kgcm(shoulder_torque_nm()), 4.51, abs_tol=0.02), \
        f"shoulder torque {nm_to_kgcm(shoulder_torque_nm()):.3f} != 4.51 kg*cm"
    assert isclose(nm_to_kgcm(elbow_torque_nm()), 2.00, abs_tol=0.02), \
        f"elbow torque {nm_to_kgcm(elbow_torque_nm()):.3f} != 2.00 kg*cm"
    assert isclose(nm_to_kgcm(wrist_torque_nm()), 0.58, abs_tol=0.02), \
        f"wrist torque {nm_to_kgcm(wrist_torque_nm()):.3f} != 0.58 kg*cm"
    assert isclose(nm_to_kgcm(gripper_servo_torque_nm()), 0.82, abs_tol=0.02), \
        f"gripper torque {nm_to_kgcm(gripper_servo_torque_nm()):.3f} != 0.82 kg*cm"
    d, _ = link_deflection_mm()
    assert isclose(d, 0.075, abs_tol=0.002), f"deflection {d:.4f} != 0.075 mm"

    moving_mass_kg = sum(i.mass_kg for i in MOVING_ASSEMBLY)
    com_from_base_axis_m = (
        sum(i.mass_kg * i.dist_from_shoulder_m for i in MOVING_ASSEMBLY)
        / moving_mass_kg
    ) + SHOULDER_OFFSET_FROM_BASE_AXIS_M
    m_over = moving_mass_kg * G * (com_from_base_axis_m - TIP_EDGE_FROM_BASE_AXIS_M)
    m_rest = (BASE_ASSEMBLY_MASS_KG + BALLAST_KG) * G * TIP_EDGE_FROM_BASE_AXIS_M
    tip_sf = m_rest / m_over
    assert isclose(tip_sf, 2.22, abs_tol=0.02), f"tipping SF {tip_sf:.3f} != 2.22"

    print("Self-test: all figures match docs/actuator_selection.md and")
    print("docs/mechanical_design.md within rounding tolerance.\n")


if __name__ == "__main__":
    self_test()
    mass_budget_report()
    torque_report()
    min_grip_force_report()
    stability_report()
    deflection_report()
