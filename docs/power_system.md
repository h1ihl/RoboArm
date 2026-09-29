# Power system

## Current budget

| Servo | Qty | Idle | Moving | Stall |
|---|---:|---:|---:|---:|
| MG996R | 2 | 0.17 A | 0.6–0.9 A | 2.5 A |
| MG90S | 2 | 0.08 A | 0.2–0.4 A | 0.7 A |
| SG90 | 1 | 0.06 A | 0.2 A | 0.65 A |
| **Rail total** | 5 | **0.56 A** | **1.2–1.8 A** | **7.05 A** |

The 7.05 A all-stall figure isn't a design case — it requires every joint
jammed simultaneously, which on a desk arm means something has already gone
wrong. The design case is **1.8 A continuous, ~3.5 A transient** at
direction reversals.

## Supply specification

**6.0 V, 3 A regulated (18 W), barrel jack, 3 A fuse.**

6.0 V because MG996R torque is quoted at 6 V; at 5 V you lose ~15% and
shoulder safety factor falls from 2.44 to 2.08 (see
`docs/actuator_selection.md`). The 4.8–6.6 V window covers all five servos.

Bulk capacitance: 2 × 1000 µF across the rail, placed physically at the
servo headers (not just at the supply) to actually damp the local transient.

```
Capacitor hold time: C·ΔV/I = 2000 µF × 0.5 V / 2 A = 0.5 ms
```

Be honest about what the capacitors do: two thousand microfarads hold a 2 A
surge for half a millisecond before the rail sags half a volt. They kill the
switching spike that would otherwise reset the MCU; they are **not** a
substitute for a supply that can actually source the current. Don't let a
capacitor talk you into a 1 A adapter.

## Sourcing options

| Option | Notes |
|---|---|
| **Bench supply** (use for bring-up) | Set 6.0 V with a 3 A current limit. The ammeter is genuinely diagnostic — a joint drawing 1.5 A while holding still is a joint fighting its own mechanical limit, and you'll see it before you smell it. Use for the whole of Phase 7 (testing). |
| **6 V 3 A adapter (primary purchase)** | ~$14. Doubles as ballast on the base plate — see `docs/mechanical_design.md` / stability calc in the planning guide §6. |
| **5 V 3 A phone charger (fallback)** | Free if you already own a USB-C PD or old 5 V/3 A brick. Costs ~15% of torque; shoulder SF 2.08 — acceptable, not comfortable. |
| **4×AA batteries (rejected)** | Nominal voltage is fine — 4 fresh alkaline cells land around 6.4 V, inside the 4.8–6.6 V window. The problem is internal resistance, not voltage: alkaline AAs run ~0.15–0.3 Ω each, so ~0.6–1.2 Ω for the pack. At the 1.8 A design-case draw that's 1.1–2.2 V of sag before the 3.5 A transient case makes it worse — the same failure mode as the capacitor note above, a source that can't hold voltage under real load. Expect soft/inconsistent moves or brownouts, not a clean fault. NiMH cells have lower internal resistance and are the better chemistry *if* a battery pack is ever used for real, but even then treat it as good for a single-joint bench check, not for running the assembled arm. |

## Three rules, each of which has ended someone's project

1. **Never feed the servo rail from the ESP32's 5V/VIN pin or USB.** That
   pin sits upstream of the board's own 3.3 V logic regulator and reflects
   whatever the USB port can source — typically 500 mA; five servos will
   brown it out and reset the board mid-move.
2. **Servo ground and ESP32 ground must be joined.** Otherwise the PWM has no
   common reference and servos twitch randomly.
3. **No 7.4 V LiPo direct to the rail.** It will destroy the MG90S and SG90
   within minutes — they're rated to 6.6 V, not 7.4 V.
