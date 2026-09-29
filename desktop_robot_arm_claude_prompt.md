# Project: Low-Cost 3-DOF Desktop AI Robot Arm

I want to design and build a **small tabletop 3-DOF robotic arm** as a personal engineering/hobby project.

The eventual goal is to turn it into a **tabletop AI assistant** that can interact with objects on my desk. For example, an AI agent could eventually tell the arm to pick up an item I need, move something out of the way, bring an object closer, etc.

However, the project must be developed in two versions:

- **V1 — Basic robotic arm:** mechanically and electronically functional arm that I can control manually/programmatically.
- **V2 — AI assistant:** add a camera, computer vision, AI agent, object detection, and higher-level control.

**Do NOT start with the AI system. V1 is purely about building a functional physical robot.**

---

# 1. PROJECT CONSTRAINTS

This is intentionally a **small, inexpensive tabletop hobby robot**.

Target personal spending:

**CAD $50–70**

Absolute maximum:

**CAD $100**

Do not turn this into a $200–500 robotics project.

The goal is to learn from the mechanical, electrical, and software design while actually being able to build the robot.

Prioritize:

1. Low cost
2. Simplicity
3. Reliability
4. Ease of fabrication
5. Adequate performance
6. Expandability toward V2

---

# 2. UNIVERSITY RESOURCES AVAILABLE

I am an engineering student and have access to a university engineering environment with **a variety of motors, electronics, components, tools, and equipment**.

I may be able to obtain or borrow things such as:

- Hobby servos
- DC motors
- Stepper motors
- Brushless motors
- Microcontrollers
- Sensors
- Wiring
- Breadboards
- Connectors
- Fasteners
- Bearings
- Power supplies
- Motor drivers
- Miscellaneous electronics

Therefore:

**DO NOT automatically include every component in the purchase budget.**

If a component is something that I could reasonably source from the university, identify it as:

> **Potentially university-sourced**

rather than assuming I need to buy it.

However, do not assume that I have a specific component unless the design can reasonably work with common university lab equipment.

For components where a specific model is important, give me a recommended inexpensive option to purchase as a fallback.

The CAD $50–70 budget should primarily represent the **things I realistically need to purchase myself**.

---

# 3. FABRICATION / CAD

I will be **3D printing essentially all of the mechanical components**.

Available printing materials:

- PLA
- PETG

I will design the mechanical components in:

**SolidWorks**

Design the robot specifically with this manufacturing method in mind.

The mechanical design should consist primarily of:

- 3D-printed parts
- Standard screws/bolts/nuts
- Cheap bearings or bushings where appropriate
- Hobby servos
- Simple shafts/pins
- Minimal purchased hardware

Do not design parts that require CNC machining, machining-grade tolerances, aluminum fabrication, carbon fiber, or other expensive manufacturing unless there is a compelling reason.

If a component can be redesigned as a simple 3D-printed part, prefer that solution.

---

# 4. 3D PRINTING DESIGN PHILOSOPHY

Design for easy printing and assembly.

Use sensible:

- Wall thicknesses
- Fillets
- Print orientations
- Infill
- Layer directions
- Bolt locations
- Servo mounting patterns

Pay attention to **3D-printing-specific strength**.

For example, consider whether a joint is likely to fail because of layer separation rather than simply assuming isotropic material strength.

For high-load components such as:

- Shoulder brackets
- Elbow brackets
- Base
- Servo mounts

consider the direction of loading relative to the print layers.

Recommend PLA vs PETG where appropriate.

Do not over-engineer the printed components.

---

# 5. ROBOT ARCHITECTURE

Design a **3-DOF tabletop robot arm**.

The baseline concept should be:

1. Base rotation
2. Shoulder
3. Elbow

Plus:

4. Servo-powered gripper

The arm should be capable of:

- Rotating around the base
- Reaching across a desk
- Moving the end effector vertically
- Opening/closing the gripper
- Picking up lightweight objects
- Moving objects short distances
- Placing objects back down

The intended payload is lightweight desk objects.

Examples:

- Pens
- Small tools
- Small boxes
- Lightweight containers
- Small electronics
- Other objects of similar size/weight

Do not optimize for heavy payloads.

---

# 6. ACTUATOR SELECTION

Research inexpensive servo options.

Potential candidates include:

- SG90
- MG90S
- MG996R
- MG995
- DS3218
- Other inexpensive hobby servos

But don't simply choose the largest servo.

Calculate the approximate torque requirements based on:

- Arm length
- Link mass
- Payload
- Joint geometry
- Worst-case position
- Safety factor

Then select the cheapest actuator that provides sufficient performance.

Pay particular attention to the shoulder joint because it will likely experience the highest torque.

Compare the options in a table.

For example:

| Joint | Servo | Required Torque | Rated Torque | Safety Factor |
|---|---|---:|---:|---:|
| Base | ??? | ??? | ??? | ??? |
| Shoulder | ??? | ??? | ??? | ??? |
| Elbow | ??? | ??? | ??? | ??? |
| Gripper | ??? | ??? | ??? | ??? |

For the gripper specifically, compare:

**SG90 vs MG90S**

and explain which makes more sense.

If university-sourced servos make more sense than purchasing cheap servos, account for that as an alternative.

---

# 7. ARM DIMENSIONS

Keep the arm genuinely small.

Target approximately:

- Base: 150–200 mm footprint
- Reach: 250–350 mm
- Overall height: 250–400 mm

These are starting targets rather than strict requirements.

Use the torque calculations to determine the final dimensions.

If reducing arm length substantially allows us to use cheaper servos, consider doing that.

Do not make the arm larger just because it looks more impressive.

---

# 8. GRIPPER

V1 must include a basic claw.

Use either:

- SG90
- MG90S

depending on the engineering analysis and price.

The gripper should be:

- 3D printable
- Simple
- Lightweight
- Easy to replace
- Capable of gripping small desk objects

Do not design an elaborate multi-finger gripper.

A simple two-finger claw is preferred.

Consider whether the gripper should use:

- Direct servo actuation
- Simple linkage
- Gear mechanism

Choose the simplest reliable option.

---

# 9. ELECTRONICS

V1 should have simple electronics.

Potential microcontrollers:

- Arduino Nano
- ESP32
- Raspberry Pi Pico
- Similar inexpensive board

Choose based on cost and simplicity.

The controller needs to:

- Control all servos
- Enforce joint limits
- Receive movement commands
- Execute predefined positions
- Execute movement sequences

A PC connection would be useful because the PC can eventually become the interface for V2.

Do not add unnecessary sensors or electronics.

---

# 10. POWER

Design a proper servo power system.

Do not power multiple servos directly from a microcontroller's 5V pin if the current requirements make that unsafe.

Calculate approximately:

- Servo current
- Peak current
- Supply voltage
- Required power

Then recommend a cheap power source.

If I can source an appropriate supply from the university, identify that as a possible way to reduce cost.

---

# 11. V1 CONTROL

V1 should allow manual/programmatic control.

A good architecture would be:

**PC → USB → Microcontroller → Servos**

Create simple commands such as:

```text
BASE 90
SHOULDER 60
ELBOW 120
GRIP OPEN
GRIP CLOSE
```

and/or higher-level commands such as:

```text
MOVE X Y Z
PICKUP
RELEASE
HOME
```

Implement a simple Python program if practical.

Do not introduce ROS or a complicated robotics framework.

---

# 12. KINEMATICS

Implement basic robot-arm kinematics.

For a 3-DOF arm, support:

### Forward kinematics

Joint angles → end-effector position

and ideally:

### Inverse kinematics

Desired X/Y/Z → joint angles

Use the simplest mathematical model appropriate for the arm.

Document the equations clearly.

Account for:

- Servo limits
- Mechanical limits
- Reachable workspace
- Collision possibilities
- Ground/table clearance

Do not turn this into an advanced robotics research project.

---

# 13. MECHANICAL ENGINEERING

Since this is an engineering project, include reasonable engineering calculations.

At minimum calculate:

### Joint torque

For example:

\[
\tau = Fd
\]

and account for the mass of downstream links and payload.

### Safety factor

Compare calculated torque against servo torque.

### Base stability

Estimate whether the arm could tip over in a worst-case configuration.

### Structural strength

Identify high-stress printed components.

If useful, I can perform FEA in SolidWorks, so identify components where SolidWorks Simulation would actually be useful.

Do not require FEA for every single part.

Use engineering analysis where it provides useful information.

---

# 14. SOLIDWORKS DESIGN

The CAD should be organized like a real engineering project.

Use sensible:

- Part files
- Assemblies
- Configurations where useful
- Mates
- Reference geometry
- Design tables only if actually necessary

The assembly should make it easy to modify:

- Arm length
- Servo locations
- Joint positions
- Gripper
- Base dimensions

Consider designing the servo mounts parametrically so different inexpensive servos can be accommodated without redesigning the entire arm.

---

# 15. V1 SOFTWARE ARCHITECTURE

Keep the software modular enough that V2 can build on it.

For example:

```text
PC
 │
 ▼
Python Control Layer
 │
 ├── Manual Control
 ├── Position Commands
 ├── Kinematics
 └── Future AI Agent
 │
 ▼
Microcontroller
 │
 ├── Servo Control
 ├── Joint Limits
 └── Safety Logic
 │
 ▼
Robot Arm
```

The future AI agent should eventually be able to call the same movement functions used by the V1 control system.

---

# 16. V2 — AI TABLETOP ASSISTANT

After V1 is proven functional, V2 can add:

### Hardware

- Camera
- Computer
- Optional additional sensors

### Software

- Computer vision
- Object detection
- Object localization
- AI agent
- Natural-language commands
- High-level task planning

Eventually I want to be able to say something like:

> "Pick up my screwdriver and put it beside my laptop."

The eventual system could:

1. Understand the command
2. Identify the screwdriver
3. Locate it on the desk
4. Convert camera coordinates into robot coordinates
5. Calculate arm movement
6. Move the gripper to the screwdriver
7. Close the gripper
8. Move the object
9. Release it

But:

**DO NOT IMPLEMENT THIS IN V1.**

Only create the architecture so that V2 can be added later without rebuilding the entire project.

---

# 17. BUDGET

Create two BOMs.

### BOM A — Things I need to purchase

Target:

**CAD $50–70**

Maximum:

**CAD $100**

### BOM B — Potentially university-sourced

List things that could reasonably be obtained from university labs/workshops.

Example:

| Component | Purchase Cost | University Alternative |
|---|---:|---|
| Microcontroller | $X | Arduino/ESP32/Pico |
| Servos | $X | Existing hobby servos |
| Bearings | $X | Lab stock |
| Power supply | $X | Lab supply |
| Wiring | $X | Lab stock |
| Hardware | $X | Workshop stock |

Do not artificially inflate the project cost by assuming I have to purchase everything.

---

# 18. PROJECT PHASES

Structure the project as:

## Phase 1 — Requirements

Determine:

- DOFs
- Dimensions
- Payload
- Workspace
- Servo requirements
- Budget

## Phase 2 — Mechanical design

Design the complete arm in SolidWorks.

## Phase 3 — Prototype

3D print the components in PLA/PETG.

## Phase 4 — Electronics

Connect:

- Microcontroller
- Servo power
- Servos

## Phase 5 — Firmware

Implement:

- Servo control
- Joint limits
- Home position
- Basic movement commands

## Phase 6 — Kinematics

Implement:

- Forward kinematics
- Inverse kinematics
- Cartesian movement

## Phase 7 — Testing

Test:

- Individual joints
- Full arm
- Gripper
- Payload
- Repeatability
- Stability
- Servo heating/current

## Phase 8 — V2

Only after V1 works:

- Camera
- Vision
- AI agent
- Object manipulation

---

# 19. DOCUMENTATION

Create useful documentation, but **do not over-document just for the sake of having documentation.**

I want documentation that helps me actually build and understand the project.

Include:

```text
README.md
docs/
├── requirements.md
├── mechanical_design.md
├── actuator_selection.md
├── electronics.md
├── power_system.md
├── kinematics.md
├── bill_of_materials.md
├── assembly.md
├── testing.md
└── v2_ai_roadmap.md

firmware/
software/
cad/
calculations/
```

Modify the structure if necessary.

---

# 20. IMPORTANT — NO SCOPE CREEP

This is probably the most important instruction.

I want a robot that I can **actually finish**.

Do NOT turn this into:

- A 6-DOF industrial arm
- A $500 robot
- A ROS project
- An autonomous research robot
- A precision CNC machine
- A complicated computer-vision system
- An over-engineered mechanical system

The project should feel like:

> **"An engineering student built a small, cheap, clever desktop robot arm using 3D printing and readily available electronics."**

Not:

> **"A startup spent six months developing an industrial robotic manipulator."**

If you find yourself adding a component or feature, ask:

**"Does V1 genuinely need this?"**

If not, leave it for V2 or omit it.

---

# 21. FINAL DESIGN REVIEW

Before generating the detailed design, provide me with:

1. Recommended robot architecture
2. Recommended 3 DOFs
3. Recommended arm dimensions
4. Recommended servo for each joint
5. SG90 vs MG90S gripper decision
6. Estimated payload
7. Estimated workspace
8. Servo torque calculations
9. Base stability calculation
10. Recommended microcontroller
11. Recommended power system
12. Purchase BOM
13. University-sourced BOM
14. Estimated total personal cost
15. Mechanical design concept
16. Electronics architecture
17. Software architecture
18. Kinematics approach
19. Main design risks
20. V1 → V2 roadmap
21. Realistic build timeline

**Do not begin with implementation before presenting the proposed architecture and cost.**

If the proposed design exceeds **CAD $100**, redesign it.

The guiding principle is:

> **Simple system, thoughtful engineering, actually buildable.**

I want to learn robotics, mechanical design, electronics, embedded programming, kinematics, and eventually AI integration — but I want to do it by building a small project that I can realistically finish.

---

# 22. FALLBACK V1 CONFIGURATIONS

Design V1 around a **primary configuration**, but also define fallback configurations in case certain components are unavailable, too expensive, or don't provide enough torque.

The purpose of these fallbacks is to prevent the project from getting stuck because of one component.

Do NOT immediately jump to a more expensive configuration. Always try the cheapest viable option first.

## Configuration A — Ultra-Budget

**Target personal cost: CAD $50–60**

Use the cheapest reasonable components.

Example architecture:

- 3 × inexpensive hobby servos
- 1 × SG90 or MG90S gripper servo
- Arduino Nano / Pico / similar
- Basic 5–6 V servo power supply
- 3D-printed PLA/PETG structure
- Minimal bearings/hardware

Target:

- Lightweight arm
- ~200–300 mm reach
- Very light payload
- Simple two-finger gripper

This configuration should be considered the **minimum viable robot**.

The goal is simply:

> It moves reliably, the joints work, and it can pick up lightweight objects.

Do not expect high precision or large payload capacity.

---

## Configuration B — Recommended V1

**Target personal cost: CAD $60–80**

Use slightly stronger actuators where they provide meaningful benefits.

Potential architecture:

- Stronger servo for shoulder
- Medium servo for elbow
- Smaller/medium servo for base
- MG90S for gripper
- Arduino Nano / ESP32 / Pico
- Proper external servo power
- PLA/PETG printed structure
- Cheap bearings/bushings where useful

Target:

- ~250–350 mm reach
- Lightweight desk-object manipulation
- Better repeatability
- Better structural rigidity
- Enough torque to make the arm useful rather than merely demonstrational

This should be the **default design target** if the budget allows it.

---

## Configuration C — University-Sourced

**Target personal cost: CAD $50–70 or less**

Take advantage of the university resources I have access to.

If suitable components are available through the university, use them instead of purchasing new components.

Potentially use:

- Existing servos
- Existing microcontroller
- Existing bearings
- Existing power supply
- Existing wiring/connectors
- Existing fasteners
- Existing sensors

However, do not use an unusual component simply because it is available.

The component still needs to be appropriate for the design.

Clearly document:

**University-sourced component → equivalent inexpensive purchased component**

so that the design remains reproducible.

---

## Configuration D — Stronger V1

**Target maximum personal cost: CAD $80–100**

Only use this configuration if the torque calculations show that the cheaper configurations cannot provide adequate performance.

Possible changes:

- Stronger digital servo for shoulder
- Stronger digital servo for elbow
- Better base servo
- MG90S gripper
- Slightly stronger printed structural components
- Better bearings at high-load joints

The purpose of this configuration is **not to increase payload dramatically**.

It exists to provide additional torque margin and improve reliability.

Do not add unnecessary features just because the budget permits them.

---

# 23. FALLBACK DECISION TREE

Use this decision process:

```text
                     START
                       │
                       ▼
              Can the cheapest
              configuration meet
               torque requirements?
                    /     \
                  YES      NO
                   │        │
                   ▼        ▼
             CONFIG A   Can university
                        components solve it?
                          /      \
                        YES      NO
                         │        │
                         ▼        ▼
                      CONFIG C   CONFIG B
                                  │
                                  ▼
                         Still insufficient?
                               /     \
                             NO       YES
                              │         │
                              ▼         ▼
                           CONFIG B   CONFIG D
```

The actual decision should be based on the torque calculations and component availability rather than arbitrary preference.

---

# 24. COMPONENT FALLBACKS

For each critical component, define at least one fallback.

Example:

### Shoulder Servo

Primary:
- Recommended servo

Fallback 1:
- Cheaper servo if payload/reach is reduced

Fallback 2:
- University-sourced equivalent

Fallback 3:
- Stronger servo if torque margin is insufficient

Do the same for:

- Base servo
- Elbow servo
- Gripper servo
- Microcontroller
- Power supply
- Bearings
- Fasteners

---

# 25. GEOMETRY FALLBACK

The arm dimensions should also have a fallback.

If the selected servos cannot handle the initial arm geometry:

### First solution:
Reduce payload.

### Second solution:
Reduce arm/link length.

### Third solution:
Reduce printed-part mass.

### Fourth solution:
Use a stronger servo.

Do NOT immediately increase the budget.

For example, if a 350 mm arm requires an expensive servo but a 275 mm arm works with a $10 servo, prefer the shorter arm for V1.

---

# 26. GRIPPER FALLBACK

Primary:

**MG90S + simple 3D-printed two-finger gripper**

Fallback:

**SG90 + lighter/smaller gripper**

If neither is available:

Use another small hobby servo with similar torque and dimensions.

The gripper should remain mechanically simple.

---

# 27. V1 CONFIGURATION COMPARISON

At the end of the design analysis, provide a table like:

| | Config A | Config B | Config C | Config D |
|---|---|---|---|---|
| Approx. cost | $50–60 | $60–80 | $50–70 | $80–100 |
| Reach | | | | |
| Payload | | | | |
| Base servo | | | | |
| Shoulder servo | | | | |
| Elbow servo | | | | |
| Gripper | | | | |
| Controller | | | | |
| University components | Minimal | Minimal | High | Optional |
| Difficulty | | | | |
| Main advantage | | | | |

Do not rank these configurations as "best" or "worst."

Instead, explain the **trade-offs** and what conditions would make each configuration appropriate.

The default starting point should be the **lowest-cost configuration that satisfies the engineering requirements**.

---

# 28. IMPORTANT

Do not design four completely different robots.

All fallback configurations should share as much as possible:

- Same general arm geometry
- Same SolidWorks assembly structure
- Same mounting strategy
- Same software
- Same control architecture
- Same gripper interface where possible

Ideally, changing from one configuration to another should require only swapping:

- Servos
- Power supply
- Minor mounting adapters

This way I can start with the cheapest configuration and upgrade individual components later without redesigning the entire robot.
