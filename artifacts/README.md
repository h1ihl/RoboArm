# Artifacts

`design_review.html` is a saved copy of the interactive design-review page
published earlier in this project
(https://claude.ai/code/artifact/120ad4c1-6e6d-4bc8-b303-615aa0728409) --
open it directly in a browser, no server needed. It was the first pass
through the numbers, before they were re-derived as runnable code.

**Two figures in it are superseded.** `calculations/engineering_calcs.py`
(run against real Python, not hand-arithmetic) caught two rounding slips
that made it into this page but not into `docs/`:

| Figure | This page says | Corrected (docs/, planning_guide.pdf) |
|---|---|---|
| Base tipping safety factor, ballasted | 2.26 | **2.22** |
| Wrist-servo required torque / SF | 0.51 kg·cm / SF 3.5 | **0.58 kg·cm / SF 3.08** |

Neither changes any design decision (both still clear their safety-factor
floors comfortably) -- treat `docs/` and `docs/planning_guide.pdf` as
authoritative; keep this page as the design-review record, not as the
current numbers.
