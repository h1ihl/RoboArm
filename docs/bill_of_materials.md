# Bill of materials

Prices in CAD, estimated from typical Amazon.ca listings. AliExpress runs
roughly 40% cheaper with a ~3-week wait — worth it for the servos if you're
not in a hurry, not worth splitting an order over for everything else.

## BOM A — purchase

| Item | Qty | Cost | Likely in a uni lab? | Note |
|---|---:|---:|---|---|
| MG996R servo | 2 | $17 | Unlikely | Shoulder, elbow. Sold as a 2-pack; a 4-pack at $26 buys spares, and you will want one. |
| MG90S servo | 2 | $13 | Maybe | Base, gripper. |
| SG90 servo | 1 | $3 | Likely | Wrist leveller — lab drawers are usually full of these. |
| 6 V 3 A adapter + barrel jack | 1 | $14 | Likely | A bench supply substitutes entirely for bring-up. |
| ESP32 DevKit (CP2102/CH340) | 1 | $12 | Maybe | Less universal in older teaching labs than a Nano/Uno; a Nano works as a straight fallback (`docs/electronics.md`) at $9 if one's on hand instead. |
| 1000 µF 16 V electrolytic ×2 | 1 | $3 | Very likely | Any parts bin has these. |
| 608ZZ bearing ×2 | 1 | $4 | Likely | From a 10-pack, or a dead skateboard. |
| M3 screw/nyloc assortment | 1 kit | $11 | Very likely | M3×10/12/16/25. Workshop stock. |
| Dupont wire + perfboard | 1 | $8 | Very likely | Lab stock. |
| PLA + PETG filament (~300 g) | — | $8 | Likely | Share of a $25 spool. |
| **Buy absolutely everything** | | **$93** | | Under the $100 ceiling |

**Optional, not in the total above:** a 74HCT125/74AHCT125 level shifter
(~$1) if any servo turns out to jitter on the ESP32's 3.3 V signal — see
`docs/electronics.md`. Most builds won't need it.

## BOM B — university-sourced, with purchased equivalents

| Component | University alternative | Saves | Substitution risk |
|---|---|---:|---|
| Microcontroller | Any ESP32 dev board in the lab, or a Nano/Uno/Mega/Pico (`docs/electronics.md` fallback) | $12 | Low — confirm servo signal quality on whichever board turns up, ESP32 or 5 V AVR |
| Power supply | Bench PSU at 6.0 V / 3 A limit | $14 | None — better than the adapter for testing |
| Fasteners | Workshop M3 stock | $11 | None |
| Wiring, headers, perfboard | Electronics lab stock | $8 | None |
| Bearings | Mechanism-lab 608 or 625 stock | $4 | Low — 625ZZ works with a bore change |
| Filament | Makerspace PLA/PETG | $8 | None |
| Capacitors | Any parts bin | $3 | None |
| Micro servos | SG90/MG90S from teaching kits | $16 | Check — test for stripped gears first |
| **MG996R × 2** | Unlikely to be in a drawer; usually issued per-project | $17 | Plan to buy |
| Ballast stock (mild steel bar/plate, milled to size — `docs/mechanical_design.md` §Ballast) | Metal-shop remnant bin | ~$5–8 | Low — any mild steel blank ≥55 cm³ works, exact stock shape doesn't matter |

## Cost summary

| Scenario | Cost |
|---|---:|
| Buy everything (worst case) | $93 |
| **Typical student (servos + supply + filament, rest sourced)** | **$59** |
| Well-stocked lab (MG996R + MG90S only) | $33 |
| AliExpress route (buy-everything, 3-week wait) | $42 |

**The realistic number is $59** — buy the servos, the power supply and
filament; source the controller, fasteners, wire, bearings and capacitors
from the lab. Lands in the middle of the $50–70 target with the $100 ceiling
never in sight, and is unaffected by the ESP32 swap since the controller is
lab-sourced in this scenario either way. The AliExpress figure moves by only
$1 despite the $3 Amazon.ca delta — ESP32 dev boards are inexpensive there
too, often $5–6, close to what a Nano clone costs.

## Configuration deltas (see `docs/requirements.md` for trigger conditions)

| | A — Ultra-budget | B — Recommended (this BOM) | C — University | D — Stronger |
|---|---:|---:|---:|---:|
| Purchase cost | $48–55 | $55–65 | $17–35 | $85–95 |
| Delta from B | Elbow MG90S instead of MG996R, forearm 80 mm not 120 mm, base/gripper SG90 | — | Swap purchased servos for lab stock where available | Shoulder DS3218 (20 kg·cm) instead of MG996R |
