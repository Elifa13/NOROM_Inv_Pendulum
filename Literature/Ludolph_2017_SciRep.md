---
title: "Interacting Learning Processes during Skill Acquisition: Learning to control with gradually changing system dynamics"
authors: [Nicolas Ludolph, Martin A. Giese, Winfried Ilg]
year: 2017
venue: Scientific Reports 7:13191
doi: 10.1038/s41598-017-13510-0
pdf: "[[Ludolph_2017_SciRep.pdf]]"
status: basis
used_in: [Setup, GAP, Pilot_Noise]
tags: [cart-pole, gradual-gravity, adaptation, action-timing]
---

## Main finding

30 people learn to balance a cart-pole. In the gradual gravity (GG) group, g
starts at 1.0 and rises by 0.1 m/s² after every successful trial, up to 3.5.
The constant gravity (CG) group is at 3.5 from the start. GG learns faster
(median time to first success GG 2.8 min, CG 24.2 min). But every increase in
g briefly degrades performance and makes action timing more reactive. The
authors' interpretation: after g rises, the pole's acceleration is
underestimated; the internal model lags behind.

## For us

- **What we have:** our setup is identical to this paper. Physics
  parameters, ±60° and ±5 m limits, ±4 N, RK4 and Δt = 1/60 come from here
  (`Setup/02_Physics_and_T0.md`). The action timing method (event-triggered
  averaging, events at −25…+25°) was adapted from here (`Setup/05_Action_Timing.md`).
- **How we apply it:** GAP's adaptation half is derived from this
  experiment. The differences are in the "From Ludolph and not from Ludolph"
  table in `GAP/00_Design.md`. The washout phase answers the question the
  authors left open: "is there an after-effect when g is lowered again".
- **What doesn't fit us:** the T/T₀ measure. In Ludolph a trial ends at a
  fall; ours is a fixed 20 s with resets. In our data T/T₀ turns into a pure
  function of the initial angle (`Setup/02` §6).

## Taken as-is / not taken as-is

| Item | Status |
|---|---|
| Physics, limits, force, integration | Taken as-is |
| g range 1.0 → 3.5 | Taken as-is (GAP) |
| g increase rule | Changed: fixed schedule, +0.25 every 8 trials, instead of +0.1 per success |
| Trial structure | Changed: fixed 20 s with reset instead of 30 s maximum ending at a fall |
| Input device | Changed: Xbox analog stick instead of SpaceMouse Pro |
| Control group | Changed: CG at 1.0 instead of 3.5 |
| T/T₀ | Could not be taken, rationale in `Setup/02` §6 |

## Numbers

- n = 30, 15 GG + 15 CG, age 18–30 (p. 9)
- g increase: 0.1 m/s² after every successful trial, g_max = 3.5 (p. 3)
- Successful trial = 30 s balanced without violating a constraint; session
  90 min, number of trials free (pp. 3, 10)
- Median time to first success: GG 2.8 min, CG 24.2 min, Wilcoxon p < 0.001 (p. 4)
- Pole 1 m, pole 0.08 kg, cart 0.4 kg, no friction; ±4 N; SpaceMouse
  ±1.5 mm, 7.4 N restoring force at full displacement (pp. 9–10)
- Action variability: standard deviation of force in a 120 ms window around
  the zero crossing (p. 11)
- Open questions: after-effect when g is lowered again, retention difference
  between gradual and sudden, optimal increase schedule (p. 9)

## Citation

Ludolph N, Giese MA, Ilg W (2017). Interacting Learning Processes during
Skill Acquisition: Learning to control with gradually changing system
dynamics. *Scientific Reports* 7:13191. https://doi.org/10.1038/s41598-017-13510-0
