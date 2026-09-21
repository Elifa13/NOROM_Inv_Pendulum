---
title: "Noise Improves Visual Motion Discrimination via a Stochastic Resonance-Like Phenomenon"
authors: [Mario Treviño, Braniff De la Torre-Valdovinos, Elias Manjarrez]
year: 2016
venue: Frontiers in Human Neuroscience 10:572
doi: 10.3389/fnhum.2016.00572
pdf: "[[Trevino_2016_FrontHumNeurosci.pdf]]"
status: basis
used_in: [Pilot_Noise]
tags: [stochastic-resonance, visual-noise, random-dot-motion]
---

## Main finding

149 people discriminate motion direction in a random dot motion (RDM) task.
White pixel noise is added to the background. A medium level of noise
improves discrimination; performance follows an inverted U over noise.
Reaction times do not change. The effect also appears when stimulus and noise
are shown to different eyes. The authors suggest the effect arises in primary
visual cortex, where the two signals first converge.

## For us

- **What we have:** the noise pilots' hypothesis came from this paper
  (visual stochastic resonance). Two pilots, 22 participants, nine noise
  levels. No inverted U found (`Pilot_Noise/`).
- **How we applied it:** the noise in Unity is also uniformly distributed
  pixel noise refreshed every frame. Stimulus definition in `Unity/ABOUT.md`.
- **What doesn't fit us:** SR's precondition, a signal below threshold.
  Treviño uses low-coherence, low-luminance dots. Our pole is high-contrast
  and large. The pilot2 summary gives this as the likely reason SR did not appear.

## Taken as-is / not taken as-is

| Item | Status |
|---|---|
| Uniformly distributed pixel noise refreshed every frame | Taken |
| Noise element size | Changed: 1 × 1 pixel (0.04°) in Treviño, 4 px in ours |
| Task | Could not be taken: continuous balancing instead of RDM discrimination |
| Sub-threshold signal | Not met, rationale in `Pilot_Noise/Pilot2_Results_Summary.md` |

## Numbers

- n = 149 (p. 2)
- Noise: uniformly distributed intensity, 1 × 1 pixel, refreshed every frame,
  mean luminance user-controlled (p. 3)
- Screen 1024 × 768, 60 Hz, viewing distance 60 cm (pp. 2–3)
- Performance follows an inverted U over noise (pp. 1, 10)

## Citation

Treviño M, De la Torre-Valdovinos B, Manjarrez E (2016). Noise Improves
Visual Motion Discrimination via a Stochastic Resonance-Like Phenomenon.
*Frontiers in Human Neuroscience* 10:572. https://doi.org/10.3389/fnhum.2016.00572
