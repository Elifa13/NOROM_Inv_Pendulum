---
title: "Exploring disturbance as a force for good in motor learning"
authors: [Jack Brookes, Faisal Mushtaq, Earle Jamieson, Aaron J. Fath, Geoffrey Bingham, Peter Culmer, Richard M. Wilkie, Mark Mon-Williams]
year: 2020
venue: PLOS ONE 15(5):e0224055
doi: 10.1371/journal.pone.0224055
pdf: "[[Brookes_2020_PLOSONE.pdf]]"
status: basis
used_in: []
tags: [disturbance, assistance, motor-learning, free-energy, information]
note: Suggested by Elif's teacher (2026-09-21)
---

## Main finding

Participants track a moving target with a HapticMASTER robot through an
invisible, novel 3D force field. During training the robot either assists,
does nothing, or amplifies the error (disturbance). Learning is measured as
the improvement between a pre- and post-test done without any manipulation.
In Experiment 1 the disturbance group learns most. In Experiment 2 the
condition that switches randomly between disturbance and assistance from
trial to trial learns most. The authors explain this with the Free Energy
Principle: disturbance exposes the person to more "surprise", i.e.
information. The amount of information experienced predicts learning.

## For us

- **What we have:** GAP has no disturbance or assistance manipulation. The
  paper is a framing source, not a method source.
- **How we could apply it:** [suggestion, not discussed]
  - Measuring learning with manipulation-free pre and post tests is the same
    question as GAP's learning-versus-performance distinction (Schmidt &
    Bjork 1992, in the reading list). GAP's washout phase and control group
    serve to make that distinction.
  - The "information / surprise" framing could be used in the paper's
    introduction and discussion to argue why gravity steps drive learning.
  - Splitting the movement space into voxels to measure information could be
    adapted to measure how much of the cart-pole state space (θ, ω) was visited.
- **What doesn't fit us:** the task. Tracking with robot forces, not
  cart-pole. The perturbation magnitudes (k = ±100 N/m) do not transfer to cart-pole.

## Taken as-is / not taken as-is

Nothing in the repo is taken from this paper yet.

## Numbers

- Experiment 1: n = 48 (Assistance 15, Active-Control 16, Disturbance 17),
  one withdrew (p. 4)
- Experiment 2: n = 46 (Adaptive 13, Adaptive-Disturbance 17, Random 16),
  one withdrew (pp. 4–5)
- 5 days, one session a day, ~15 min; sessions 1 and 5 baseline (3 × 10
  trials, no manipulation), sessions 2–4 training (4 × 10 trials) (p. 6)
- Disturbance: mass-spring-damper, m = 3 kg, c = 10 Ns/m; in Experiment 1
  k = +100 (assistance), 0, −100 N/m (disturbance). In Experiment 2 k changes
  every trial, clamped to [−100, 100] N/m (pp. 6–7)
- Experiment 1 learning: F(2,44) = 5.655, p = .0065; Disturbance 2.00,
  Assistance 0.595, Active-Control 0.744 (p. 11)
- Experiment 2 learning: F(2,42) = 4.541, p = .0164; Random 1.97, Adaptive
  0.672, Adaptive-Disturbance 0.726 (p. 13)
- Both experiments pooled, information → learning regression: n = 86,
  F(1,82) = 10.45, p = .0011, R² = 0.112 (p. 13). Note: with n = 86 a simple
  regression should have 84 denominator degrees of freedom; the paper says
  82. When citing, report the number as printed, do not reinterpret it
- Open data: https://osf.io/7c95b/ (p. 1)

## Citation

Brookes J, Mushtaq F, Jamieson E, Fath AJ, Bingham G, Culmer P, Wilkie RM,
Mon-Williams M (2020). Exploring disturbance as a force for good in motor
learning. *PLOS ONE* 15(5):e0224055. https://doi.org/10.1371/journal.pone.0224055
