// limits.h -- per-joint hard bounds. The firmware owns safety
// (docs/electronics.md); these limits apply no matter what the PC sends,
// and are never overridden by a "US" raw-pulse command either.
//
// Pulse widths are in microseconds. Ranges come from docs/requirements.md
// (mechanical/joint ranges) mapped through each servo's calibrated travel;
// the *_ANGLE_MIN/MAX pairs are the degree limits used by the J command,
// the *_US_MIN/MAX pairs are the absolute microsecond floor/ceiling no
// pulse is ever allowed outside of, even during calibration.

#pragma once

// ---- Base yaw (MG90S) -----------------------------------------------------
#define BASE_ANGLE_MIN     -90.0f
#define BASE_ANGLE_MAX      90.0f
#define BASE_US_MIN          900
#define BASE_US_MAX          2100

// ---- Shoulder (MG996R) -----------------------------------------------------
#define SHOULDER_ANGLE_MIN    0.0f
#define SHOULDER_ANGLE_MAX   110.0f
#define SHOULDER_US_MIN       700
#define SHOULDER_US_MAX       2400

// ---- Elbow (MG996R) --------------------------------------------------------
#define ELBOW_ANGLE_MIN     -130.0f
#define ELBOW_ANGLE_MAX        0.0f
#define ELBOW_US_MIN           700
#define ELBOW_US_MAX          2400

// ---- Wrist pitch (SG90, slaved -- firmware still clamps it) ---------------
#define WRIST_ANGLE_MIN     -120.0f
#define WRIST_ANGLE_MAX        30.0f
#define WRIST_US_MIN           900
#define WRIST_US_MAX          2100

// ---- Gripper (MG90S, 0=closed .. 100=open) ---------------------------------
#define GRIPPER_US_CLOSED     1000
#define GRIPPER_US_OPEN       1900

// Any command outside these ranges is rejected with "ERR LIMIT <joint>" or
// "ERR RANGE" -- see arm_firmware.ino. There is deliberately no override
// path: table clearance (z >= 10 mm) and joint range are enforced here,
// not trusted to the PC side, so a bug in software/ or a future V2 agent
// cannot command the arm into the table or past a mechanical stop.
