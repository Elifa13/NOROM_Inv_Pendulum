---
title: "In a visual inverted pendulum balancing task avoiding impending falls gets harder as we age"
authors: [Hannah E. Park, Avijit Bakshi, James R. Lackner, Paul DiZio]
year: 2025
venue: Experimental Brain Research 243:44
doi: 10.1007/s00221-025-06997-x
pdf: "[[Park_2025_ExpBrainRes.pdf]]"
status: basis
used_in: [Setup, Pilot_Noise]
tags: [inverted-pendulum, phase-plane, regime, action-class, aging]
---

## Main finding

Younger (n = 30) and older (n = 26) adults balance a visual inverted pendulum
with a joystick. The phase plane is split into four quadrants: Safe if the
pole is returning to vertical, Fall if it is rotating toward a fall.
Sequences in the Fall quadrant are Saved if rescued and Failed if they end in
a fall. Joystick commands are classed as inactive (I), corrective (CR),
anticipatory (A) and destabilizing (D). Older adults make fewer CR and more D
commands only when a fall is near. Command shares as a function of time left
to fall are explained with a logistic model.

## For us

- **What we have:** the state definition (sign of θ·ω), regime runs
  (Safe / Saved / Failed) and action classes come from here
  (`Setup/03_State_Action_Episode.md`).
- **How we apply it:** Park's fall quadrant is the same criterion as
  Ludolph's "pole rotating downwards" event filter. This is where the two
  papers connect.
- **What doesn't fit us:** the sign convention. In Park the joystick sets
  angular acceleration directly; in ours the force goes to the cart. The
  corrective direction was verified from the data: in our task the
  corrective force has the same sign as θ. Park also has no track limit,
  which is why we have a separate `TrackLoss` label.

## Taken as-is / not taken as-is

| Item | Status |
|---|---|
| Safe / Fall quadrants (θ·ω) | Taken as-is |
| Safe / Saved / Failed regimes | Taken as-is, `TrackLoss` added for track loss |
| I / CR / A / D classes | Definitions taken, sign convention inverted based on the data |
| Neutral band (±1° joystick) | Changed: ours is `input_neutral_band` = 0.02, Unity's deadzone already applied |
| Transient passes through the band not counted as I (footnote) | Taken as-is: `neutral_transient_max_samples` = 3 |

## Numbers

- 30 younger (18–29) and 27 older (60–78), one older participant excluded,
  26 analysed (p. 3)
- Dynamics: θ̈ = K_P sinθ + K_J φ; K_P = 171.9°/s² (0.27 Hz) (p. 3)
- Joystick gain 9.5 and 19.1 s⁻², added delay 0, 30, 60 ms; 18 trials × 30 s;
  fall boundary ±60° (pp. 3–4)
- Neutral band: joystick ±1° (p. 4)

## Citation

Park HE, Bakshi A, Lackner JR, DiZio P (2025). In a visual inverted pendulum
balancing task avoiding impending falls gets harder as we age. *Experimental
Brain Research* 243:44. https://doi.org/10.1007/s00221-025-06997-x
