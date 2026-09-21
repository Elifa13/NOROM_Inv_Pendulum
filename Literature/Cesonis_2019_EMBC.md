---
title: "Controller Gains of an Inverted Pendulum are Influenced by the Visual Feedback Position"
authors: [Justinas Česonis, Raz Leib, Sae Franklin, David W. Franklin]
year: 2019
venue: 41st Annual International Conference of the IEEE EMBS (EMBC 2019)
doi: ""
pdf: "[[Cesonis_2019_EMBC.pdf]]"
status: basis
used_in: []
tags: [inverted-pendulum, visual-feedback, controller-model]
---

## Main finding

Six people balance an inverted pendulum with a robotic manipulandum. The
pendulum's dynamic length (L = 1 m and 4 m) and the position on the pendulum
where visual feedback is shown are varied independently. A family of linear
models is fitted to the participants' control input (cart velocity). Control
is well described as the sum of proportional error correction and a term
inversely proportional to visual feedback gain. The model is tested by
predicting the input for L = 2 m.

## For us

- **What we have:** no repo document cites this paper yet.
- **How we could apply it:** an example for `GAP/02_Modelling_Plan.md` §A
  (controller identification) of fitting a family of linear models to human
  control and testing the model by prediction in a new condition.
  [suggestion, not discussed]
- **What doesn't fit us:** the control input. Here the participant sets cart
  velocity directly; ours applies force. We also have no manipulation of
  visual feedback position; the whole pole is visible. n = 6.

## Taken as-is / not taken as-is

Nothing in the repo is taken from this paper.

## Numbers

- n = 6, participants experienced from earlier pendulum studies (p. 1)
- L = 1 m and 4 m tested, L = 2 m prediction condition (pp. 1–2)
- Manipulandum channel: stiffness 4000 N/m, damping 2 Ns/m, max 25 N; data at 1 kHz (p. 2)
- 0.01 rad/s perturbation to the pendulum at trial start (p. 2)

## Citation

Česonis J, Leib R, Franklin S, Franklin DW (2019). Controller Gains of an
Inverted Pendulum are Influenced by the Visual Feedback Position. *41st
Annual International Conference of the IEEE Engineering in Medicine and
Biology Society (EMBC)*. The PDF gives no DOI; it needs to be added.
