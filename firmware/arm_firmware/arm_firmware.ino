// arm_firmware.ino -- Desk Arm V1 firmware (ESP32 DevKit)
//
// Owns safety (joint limits, slew rate); the PC (software/) owns
// intelligence (kinematics, sequencing, and eventually the V2 agent).
// See docs/electronics.md for the architecture and full protocol table,
// docs/power_system.md for wiring rules, docs/assembly.md for the
// bring-up and calibration sequence this firmware is meant to support.
//
// Requires the "ESP32Servo" library (madhephaestus/ESP32Servo) instead of
// the stock Arduino Servo library -- the ESP32 core has no Servo.h of its
// own, and ESP32Servo drives the same writeMicroseconds()/attach() API on
// top of the LEDC PWM peripheral. Install it from Library Manager before
// building. Board package: "esp32" by Espressif Systems.
//
// Serial: 115200 baud, one ASCII command per line (newline-terminated),
// every command answered on its own line.
//
//   PING                    -> OK ARM v1
//   J <base> <sh> <el>      -> OK | ERR LIMIT <joint>     (degrees; wrist follows automatically)
//   G <0-100>               -> OK                          (0 = closed, 100 = open)
//   US <ch> <us>             -> OK | ERR RANGE               (ch = B/S/E/W/G, calibration only)
//   HOME                     -> OK
//   STOP                     -> OK
//   REL                      -> OK                          (detach all servos)
//   STAT                     -> <base> <sh> <el> <wrist> <grip%>  <usB> <usS> <usE> <usW> <usG>

#include <ESP32Servo.h>
#include "limits.h"
#include "slew.h"

// ---- Pin assignment ---------------------------------------------------
// Five GPIOs, all general-purpose and LEDC-PWM-capable. Deliberately not
// using: 0/2/5/12/15 (boot-strapping pins -- a servo yanking one of these
// low/high at power-on can change boot mode), 34-39 (input-only, can't
// drive a servo), or 1/3 (UART0 -- reserved for the USB serial link to the
// PC). See docs/electronics.md for the pin-selection rationale and the
// wiring diagram (docs/wiring_diagram.svg). Keep signal wires away from
// the barrel-jack leads (docs/electronics.md wiring notes).
const uint8_t PIN_BASE     = 13;
const uint8_t PIN_SHOULDER = 14;
const uint8_t PIN_ELBOW    = 27;
const uint8_t PIN_WRIST    = 26;
const uint8_t PIN_GRIPPER  = 25;

Servo servoBase, servoShoulder, servoElbow, servoWrist, servoGripper;

// ---- HOME pose ----------------------------------------------------------
// Starting defaults for the safe folded pose -- tune these during the
// calibration procedure in docs/assembly.md once the physical arm exists;
// they are not load-bearing for anything else in the firmware.
const float HOME_BASE_DEG     = 0.0f;
const float HOME_SHOULDER_DEG = 60.0f;
const float HOME_ELBOW_DEG    = -90.0f;
const int   HOME_GRIPPER_PCT  = 50;

// ---- Live state -----------------------------------------------------------
float curBase = HOME_BASE_DEG,     targetBase     = HOME_BASE_DEG;
float curShoulder = HOME_SHOULDER_DEG, targetShoulder = HOME_SHOULDER_DEG;
float curElbow = HOME_ELBOW_DEG,   targetElbow    = HOME_ELBOW_DEG;
float curWrist = 0.0f,             targetWrist    = 0.0f;
int   curGripperPct = HOME_GRIPPER_PCT;
bool  released = false;

unsigned long lastTickMs = 0;
const unsigned long TICK_MS = (unsigned long)(1000.0f / UPDATE_HZ);

// ---- Angle <-> microsecond mapping (linear per joint) ----------------------
long angleToUs(float angleDeg, float aMin, float aMax, int usMin, int usMax) {
  float t = (angleDeg - aMin) / (aMax - aMin);
  if (t < 0) t = 0;
  if (t > 1) t = 1;
  return usMin + (long)(t * (usMax - usMin));
}

float usToAngle(long us, float aMin, float aMax, int usMin, int usMax) {
  float t = (float)(us - usMin) / (float)(usMax - usMin);
  return aMin + t * (aMax - aMin);
}

// ---- Wrist slaving --------------------------------------------------------
// Keeps the gripper level in every pose: theta3 = -(theta1 + theta2).
// See docs/kinematics.md. Clamped to the wrist's own mechanical limits --
// if the slaved angle would exceed them, the pose itself is unreachable
// with a level gripper and the PC-side kinematics layer should have
// rejected it before ever sending J; the clamp here is a last-resort
// safety net, not the primary check.
float computeWristTarget(float shoulderDeg, float elbowDeg) {
  float w = -(shoulderDeg + elbowDeg);
  if (w < WRIST_ANGLE_MIN) w = WRIST_ANGLE_MIN;
  if (w > WRIST_ANGLE_MAX) w = WRIST_ANGLE_MAX;
  return w;
}

// ---- Setup ------------------------------------------------------------
void setup() {
  Serial.begin(115200);
  // ESP32Servo multiplexes servos across a handful of LEDC timers rather
  // than a per-pin hardware timer the way AVR's Servo library does; grab
  // all four up front so attach() below never fails to find one.
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);
  attachAll();
  targetWrist = computeWristTarget(targetShoulder, targetElbow);
  curWrist = targetWrist;
  writeAll();
  lastTickMs = millis();
}

void attachAll() {
  // Pass each channel's real (min_us, max_us) explicitly -- ESP32Servo
  // defaults to clamping writeMicroseconds() to 544-2400us, which is
  // close but not identical to limits.h's per-joint ranges (e.g. shoulder
  // goes to 700-2400). Without this, out-of-band values silently clip
  // instead of reaching the servo, which is the opposite of what
  // limits.h's own range checks in handleLine() already guarantee.
  servoBase.setPeriodHertz(50);
  servoShoulder.setPeriodHertz(50);
  servoElbow.setPeriodHertz(50);
  servoWrist.setPeriodHertz(50);
  servoGripper.setPeriodHertz(50);
  servoBase.attach(PIN_BASE, BASE_US_MIN, BASE_US_MAX);
  servoShoulder.attach(PIN_SHOULDER, SHOULDER_US_MIN, SHOULDER_US_MAX);
  servoElbow.attach(PIN_ELBOW, ELBOW_US_MIN, ELBOW_US_MAX);
  servoWrist.attach(PIN_WRIST, WRIST_US_MIN, WRIST_US_MAX);
  servoGripper.attach(PIN_GRIPPER, GRIPPER_US_CLOSED, GRIPPER_US_OPEN);
  released = false;
}

void detachAll() {
  servoBase.detach();
  servoShoulder.detach();
  servoElbow.detach();
  servoWrist.detach();
  servoGripper.detach();
  released = true;
}

void writeAll() {
  if (released) return;
  servoBase.writeMicroseconds(angleToUs(curBase, BASE_ANGLE_MIN, BASE_ANGLE_MAX, BASE_US_MIN, BASE_US_MAX));
  servoShoulder.writeMicroseconds(angleToUs(curShoulder, SHOULDER_ANGLE_MIN, SHOULDER_ANGLE_MAX, SHOULDER_US_MIN, SHOULDER_US_MAX));
  servoElbow.writeMicroseconds(angleToUs(curElbow, ELBOW_ANGLE_MIN, ELBOW_ANGLE_MAX, ELBOW_US_MIN, ELBOW_US_MAX));
  servoWrist.writeMicroseconds(angleToUs(curWrist, WRIST_ANGLE_MIN, WRIST_ANGLE_MAX, WRIST_US_MIN, WRIST_US_MAX));
  long gUs = GRIPPER_US_CLOSED + (long)((curGripperPct / 100.0f) * (GRIPPER_US_OPEN - GRIPPER_US_CLOSED));
  servoGripper.writeMicroseconds(gUs);
}

// ---- Main loop --------------------------------------------------------
void loop() {
  pollSerial();

  unsigned long now = millis();
  if (now - lastTickMs >= TICK_MS) {
    lastTickMs = now;
    curBase     = slewStep(curBase, targetBase);
    curShoulder = slewStep(curShoulder, targetShoulder);
    curElbow    = slewStep(curElbow, targetElbow);
    curWrist    = slewStep(curWrist, targetWrist);
    writeAll();
  }
}

// ---- Serial command handling --------------------------------------------
void pollSerial() {
  static char buf[64];
  static uint8_t len = 0;

  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (len > 0) {
        buf[len] = '\0';
        handleLine(buf);
        len = 0;
      }
    } else if (len < sizeof(buf) - 1) {
      buf[len++] = c;
    }
  }
}

void handleLine(char *line) {
  char *cmd = strtok(line, " ");
  if (cmd == nullptr) return;

  if (strcmp(cmd, "PING") == 0) {
    Serial.println("OK ARM v1");

  } else if (strcmp(cmd, "J") == 0) {
    char *aBase = strtok(nullptr, " ");
    char *aSh   = strtok(nullptr, " ");
    char *aEl   = strtok(nullptr, " ");
    if (!aBase || !aSh || !aEl) { Serial.println("ERR ARGS"); return; }
    float b = atof(aBase), s = atof(aSh), e = atof(aEl);

    if (b < BASE_ANGLE_MIN || b > BASE_ANGLE_MAX)         { Serial.println("ERR LIMIT base"); return; }
    if (s < SHOULDER_ANGLE_MIN || s > SHOULDER_ANGLE_MAX) { Serial.println("ERR LIMIT shoulder"); return; }
    if (e < ELBOW_ANGLE_MIN || e > ELBOW_ANGLE_MAX)       { Serial.println("ERR LIMIT elbow"); return; }

    float w = computeWristTarget(s, e);
    if (released) attachAll();
    targetBase = b; targetShoulder = s; targetElbow = e; targetWrist = w;
    Serial.println("OK");

  } else if (strcmp(cmd, "G") == 0) {
    char *aPct = strtok(nullptr, " ");
    if (!aPct) { Serial.println("ERR ARGS"); return; }
    int pct = atoi(aPct);
    if (pct < 0 || pct > 100) { Serial.println("ERR RANGE"); return; }
    if (released) attachAll();
    curGripperPct = pct;
    writeAll();
    Serial.println("OK");

  } else if (strcmp(cmd, "US") == 0) {
    char *aCh = strtok(nullptr, " ");
    char *aUs = strtok(nullptr, " ");
    if (!aCh || !aUs) { Serial.println("ERR ARGS"); return; }
    char ch = aCh[0];
    long us = atol(aUs);
    if (released) attachAll();

    switch (ch) {
      case 'B':
        if (us < BASE_US_MIN || us > BASE_US_MAX) { Serial.println("ERR RANGE"); return; }
        servoBase.writeMicroseconds(us);
        curBase = targetBase = usToAngle(us, BASE_ANGLE_MIN, BASE_ANGLE_MAX, BASE_US_MIN, BASE_US_MAX);
        break;
      case 'S':
        if (us < SHOULDER_US_MIN || us > SHOULDER_US_MAX) { Serial.println("ERR RANGE"); return; }
        servoShoulder.writeMicroseconds(us);
        curShoulder = targetShoulder = usToAngle(us, SHOULDER_ANGLE_MIN, SHOULDER_ANGLE_MAX, SHOULDER_US_MIN, SHOULDER_US_MAX);
        break;
      case 'E':
        if (us < ELBOW_US_MIN || us > ELBOW_US_MAX) { Serial.println("ERR RANGE"); return; }
        servoElbow.writeMicroseconds(us);
        curElbow = targetElbow = usToAngle(us, ELBOW_ANGLE_MIN, ELBOW_ANGLE_MAX, ELBOW_US_MIN, ELBOW_US_MAX);
        break;
      case 'W':
        if (us < WRIST_US_MIN || us > WRIST_US_MAX) { Serial.println("ERR RANGE"); return; }
        servoWrist.writeMicroseconds(us);
        curWrist = targetWrist = usToAngle(us, WRIST_ANGLE_MIN, WRIST_ANGLE_MAX, WRIST_US_MIN, WRIST_US_MAX);
        break;
      case 'G':
        if (us < GRIPPER_US_CLOSED || us > GRIPPER_US_OPEN) { Serial.println("ERR RANGE"); return; }
        servoGripper.writeMicroseconds(us);
        curGripperPct = (int)(100.0f * (us - GRIPPER_US_CLOSED) / (float)(GRIPPER_US_OPEN - GRIPPER_US_CLOSED));
        break;
      default:
        Serial.println("ERR ARGS");
        return;
    }
    Serial.println("OK");

  } else if (strcmp(cmd, "HOME") == 0) {
    if (released) attachAll();
    targetBase = HOME_BASE_DEG;
    targetShoulder = HOME_SHOULDER_DEG;
    targetElbow = HOME_ELBOW_DEG;
    targetWrist = computeWristTarget(HOME_SHOULDER_DEG, HOME_ELBOW_DEG);
    curGripperPct = HOME_GRIPPER_PCT;
    Serial.println("OK");

  } else if (strcmp(cmd, "STOP") == 0) {
    targetBase = curBase;
    targetShoulder = curShoulder;
    targetElbow = curElbow;
    targetWrist = curWrist;
    Serial.println("OK");

  } else if (strcmp(cmd, "REL") == 0) {
    detachAll();
    Serial.println("OK");

  } else if (strcmp(cmd, "STAT") == 0) {
    long usB = angleToUs(curBase, BASE_ANGLE_MIN, BASE_ANGLE_MAX, BASE_US_MIN, BASE_US_MAX);
    long usS = angleToUs(curShoulder, SHOULDER_ANGLE_MIN, SHOULDER_ANGLE_MAX, SHOULDER_US_MIN, SHOULDER_US_MAX);
    long usE = angleToUs(curElbow, ELBOW_ANGLE_MIN, ELBOW_ANGLE_MAX, ELBOW_US_MIN, ELBOW_US_MAX);
    long usW = angleToUs(curWrist, WRIST_ANGLE_MIN, WRIST_ANGLE_MAX, WRIST_US_MIN, WRIST_US_MAX);
    long usG = GRIPPER_US_CLOSED + (long)((curGripperPct / 100.0f) * (GRIPPER_US_OPEN - GRIPPER_US_CLOSED));

    Serial.print(curBase, 1);     Serial.print(' ');
    Serial.print(curShoulder, 1); Serial.print(' ');
    Serial.print(curElbow, 1);    Serial.print(' ');
    Serial.print(curWrist, 1);    Serial.print(' ');
    Serial.print(curGripperPct);  Serial.print("  ");
    Serial.print(usB); Serial.print(' ');
    Serial.print(usS); Serial.print(' ');
    Serial.print(usE); Serial.print(' ');
    Serial.print(usW); Serial.print(' ');
    Serial.println(usG);

  } else {
    Serial.println("ERR UNKNOWN");
  }
}
