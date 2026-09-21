---
title: "Motor expertise facilitates the accuracy of state extrapolation in perception"
authors: [Nicolas Ludolph, Jannis Plöger, Martin A. Giese, Winfried Ilg]
year: 2017
venue: PLOS ONE 12(11):e0187666
doi: 10.1371/journal.pone.0187666
pdf: "[[Ludolph_2017_PLOSONE.pdf]]"
status: basis
used_in: [GAP]
tags: [cart-pole, occlusion, prediction, internal-model]
---

## Main finding

Participants watch a cart-pole recording, the pole is hidden for 900 ms, and
they then predict where the pole is. The group previously trained in
cart-pole balancing (MF, n = 10) is more accurate than the group that only
watched (VF, n = 10). Both groups systematically underestimate the fall.
When the correct answer is shown as feedback, the difference disappears. On
the model side, the difference is explained by how long the internal model
extrapolates correctly (extrapolation horizon h).

## For us

- **What we have:** GAP's perceptual test is identical to this procedure
  (`GAP/00_Design.md`, occlusion section).
- **How we apply it:** Ludolph kept g constant, so he fitted h. In GAP g
  changes, so the gravity carried by the internal model can be estimated
  directly (`GAP/02_Modelling_Plan.md` §D).
- **What doesn't fit us:** 440 trials. GAP has 80 occlusion trials. The
  response resolution is 130°/13 ≈ 10.8° and Ludolph's group difference was
  5.3°, i.e. half a step. That difference becomes visible when averaged over
  40 trials. How much power is left with 80 trials is the subject of the
  `GAP/02` power simulation.

## Taken as-is / not taken as-is

| Item | Status |
|---|---|
| Trial structure: 4.5 s observation, 1 s zero force (pole visible for first 100 ms), 900 ms occlusion | Taken as-is |
| 13 options, [−65°, +65°] | Taken as-is |
| No feedback | Taken as-is (Ludolph has none in the first blocks either; F1–F5 have it and it erases the group difference) |
| Number of blocks | Changed: 2 × 40 = 80 instead of 11 × 40 = 440 |
| Stimulus g value | Changed: 3.5 in Ludolph, 1.0 in GAP (from the pilot's no-noise trials). This difference turns the test into an aftereffect measurement |

## Numbers

- n = 20, 10 MF + 10 VF; mean 335 days (190–570) between MF's training and test (p. 3)
- 11 blocks × 40 trials, feedback in the last five blocks (F1–F5) (p. 3)
- Trial: 4.5 s observation, 900 ms occlusion, 13 options [−65°, +65°] (p. 5)
- Simulation g = 3.5 m/s² (p. 4)
- Error before feedback (T4): MF −9.6°, VF −14.9°, p < 0.01 Holm.
  After feedback (F5): MF −5.2°, VF −7.5°, p = 0.22 (p. 10)
- Median extrapolation horizon: MF 183.33 ms, VF 16.66 ms, p = 0.026,
  Wilcoxon (p. 11)

## Citation

Ludolph N, Plöger J, Giese MA, Ilg W (2017). Motor expertise facilitates the
accuracy of state extrapolation in perception. *PLOS ONE* 12(11):e0187666.
https://doi.org/10.1371/journal.pone.0187666
