// slew.h -- rate limiter, 60 deg/s per joint (docs/power_system.md /
// docs/mechanical_design.md stability note: fast direction reversals are
// the dynamic-loading case the static tipping calculation doesn't cover).
//
// Call slewStep() once per control-loop tick (50 Hz, see arm_firmware.ino)
// with the joint's current commanded angle and its target angle; it
// returns the next angle to actually send to the servo, moved at most
// MAX_DEG_PER_S / UPDATE_HZ degrees closer to the target.

#pragma once

#define UPDATE_HZ          50.0f
#define MAX_DEG_PER_S       60.0f
#define MAX_DEG_PER_TICK    (MAX_DEG_PER_S / UPDATE_HZ)  // 1.2 deg/tick

inline float slewStep(float current_deg, float target_deg) {
  float delta = target_deg - current_deg;
  if (delta > MAX_DEG_PER_TICK) delta = MAX_DEG_PER_TICK;
  if (delta < -MAX_DEG_PER_TICK) delta = -MAX_DEG_PER_TICK;
  return current_deg + delta;
}
