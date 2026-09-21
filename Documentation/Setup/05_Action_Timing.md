# 05: Action timing (transfer from Ludolph)

**Notebook:** `04_control.ipynb`
**Code:** `src/timing.py`; thresholds in `config.yaml` → `timing`
**Output:** `state_events.parquet`, `timing_cells.parquet`
**Source:** Ludolph et al. 2017, *Sci Rep* 7:13191, p. 11 ([[Ludolph_2017_SciRep]])
**Status:** implemented (2026-08-31). Results in §5. The numbers here are from pilot1; pilot2 results are in `Pilot_Noise/Pilot2_Results_Summary.md`.

---

## 0. Terms

| Term | Meaning |
|---|---|
| **state event** | The moment the pole passes a given integer angle **while falling**. Defined on the state side; it happens even if the participant does nothing. |
| **input event** | Event defined on the input side: `onset` (leaving the neutral band), `offset` (returning to the band), `reversal` (force changes direction). NB02's `input_events` table. |
| **segment** | A ±0.5 s input window centred on a state event, 61 samples. |
| **event-triggered average** | The method: align segments to the event moment and average them. |
| **sign alignment** | Pooling segments of negative-angle events by flipping their sign, so the corrective direction is always positive. |
| **zero crossing** | The lag at which the mean segment curve crosses zero. **This number is the action timing.** Negative = predictive, positive = reactive. |
| **reversal** (curve level) | The mean curve actually changing sign (`mean_pre < 0 < mean_post`). Without it the zero crossing is undefined. |
| **amplitude** | Max − min of the mean curve. |
| **SEM** | Standard error of the mean. `amplitude / SEM` tells whether the shape stands out from noise. |
| **bootstrap CI** | Confidence interval from resampling segments (400 repetitions). |
| **velocity stratification** | Splitting events by \|ω\| at the event into `slow` / `mid` / `fast`. Boundaries at the 20% and 80% quantiles. |
| **angle band** | Pooling centre ± 2° instead of a single integer angle. Main band 10 ± 2. |
| **within-subject centering** | Subtracting each participant's own mean; condition differences only show up this way. |
| **d<sub>z</sub>** | Paired-difference effect size: mean difference ÷ sd of the differences. |
| **baseline** | The `no_noise` condition. |
| **confound** | A third variable mixed into what is measured (e.g. event composition changing over the session). |
| **regression to the mean** | A value that starts at an extreme moving toward the mean on the next measurement; can produce fake learning. |

## 1. What it measures

All metrics up to here asked "how well did they balance". Action timing asks
something else: **when does the person respond?**

Ludolph's finding: as people learn, their actions shift from happening
*after* the event to happening *before* it, a move from reflex to
anticipation. This is a mechanism layer the pilot's performance metrics
cannot see.

## 2. Ludolph's procedure

Four steps from the paper, as written:

1. **Event definition.** Integer angles from −25° to +25° (51 events). The
   crossing time of each event is found in every trial; moments between
   frames are estimated at sub-frame resolution by **linear interpolation**.
2. **Exclusion.** Crossings where the pole is rotating upwards are dropped
   (no counter-action needed). Crossings whose angular velocity falls outside
   the 20%–80% quantiles of velocities observed in a 2-minute sliding window
   are also dropped.
3. **Segment.** A **1-second** (±0.5 s) force segment centred on each event
   moment is extracted.
4. **Average and zero crossing.** Segments of the same event are averaged in
   a 2-minute sliding window; **the lag at which the mean segment crosses
   zero** is the action timing. Negative = predictive, positive = reactive.

**Action variability** = mean standard deviation of the force in a ±60 ms
window around the zero crossing.

Ludolph explicitly says he does not interpret this as reaction time.

## 3. Transfer decisions

Five points needed a decision. Four were closed, one was resolved with a
feasibility check.

### 3.1 Time axis: `trial_order` is used

Ludolph uses a 2-minute sliding window. We have **no** wall clock:
`t_trial_s` resets at the start of each trial and includes resets (max
34 s), and the metadata has no per-trial timestamp.

But none is needed. **`trial_order` already is a time axis**: fully recorded,
ordered, and proportional to elapsed time since trials run back to back.
Roughly: 53 × 20 s active + ~115 s reset + 53 × 1.5 s pause ≈ **a 21-minute
session**. Ludolph's 2-minute window ≈ 6 trials.

The window's real job is not tracking learning but **collecting enough
segments to average**; a single crossing yields no zero crossing. §4 measured
it: segments are plentiful, so the window length can be chosen freely.

### 3.2 Two axes at once

Action timing is examined **along both trial order and condition**:

- **Trial order**: the learning axis; is there a shift from reaction to anticipation
- **Condition**: does noise disrupt this timing

They are not alternatives. (The first draft proposed only the condition
axis; although the pilot's question was the choice of condition, action
timing is a motor learning measure and dropping the learning axis would have
been wrong.)

**Expectation caveat:** Ludolph measured learning in a task of more than an
hour with gradually increasing gravity. We have one session, 21 minutes,
fixed g = 1.0. If no learning signal appears, that may not mean "no
learning"; the task was not designed for it.

### 3.3 Velocity exclusion: stratification instead of dropping

**Why is there an exclusion?** The method stacks dozens of segments and
averages them. If the pole passes 10° slowly, the required correction is one
thing; if it swings through, it is another. If both go into the same average,
the curve blurs and the zero crossing stops describing anyone's behaviour.

**Decision:**

- The quantile band is computed **per participant, pooling all conditions**.
  Computed within condition, the exclusion adapts to the condition and the
  same velocity band is no longer compared; if noise changes the velocity
  distribution, that is a direct confound.
- Instead of dropping, **stratify**: separate action timing for slow / mid /
  fast bands. No data is lost, and a pattern like "reaction on fast falls,
  anticipation on slow ones" would become visible. Ludolph's exclusion may
  have been about the computing constraints of his time; we have no such
  constraint.

**Implementation note (NB04).** The quantile is computed within participant
× **angle level**, pooling conditions. Angle level must be fixed too, because
|ω| grows with angle (mean 42°/s at 5°, 64°/s at 20°); a single quantile band
applied to all angles would shift the strata with angle. The decision paid
off: stratification produced the strongest finding in §5.

### 3.4 Angle range: swept

Ludolph uses ±25°; in our data 87.1% of active time is within this range. But
instead of fixing one value, **±25 / ±15 / ±10 / ±5** are swept. In the
stabilization threshold sweep, narrow thresholds had also given stronger
effects.

Fall-direction crossing counts (measurement, `analysis_include`):

| Range | Crossings | Per participant × condition |
|---|---|---|
| ±25° | 110,091 | ~1,835 |
| ±15° | 79,607 | ~1,327 |
| ±10° | 57,549 | ~959 |
| ±5° | 29,198 | ~487 |

Feasibility is not an issue in any range.

**Final form in the implementation (NB04).** **Bands** were used instead of
ranges: centre ± 2°, centres 5 / 10 / 15 / 20. Reason in §4: at a single
integer angle the mean curve sometimes crossed zero more than once (3
crossings in P002); pooling a narrow band reduces this to one crossing. A
cumulative range (everything within ±25) would be meaningless because of §6:
different angles are different reference points and cannot be mixed.

The main analysis is **10 ± 2** (feasibility was verified there); the other
three bands are a robustness sweep. Thresholds in `config.yaml` →
`timing.band_centers_deg`, `timing.band_half_width_deg`,
`timing.main_band_center_deg`.

### 3.5 Segments crossing an episode boundary: dropped

The 1-second window spills into the reset block if the event is near the end
of an episode. On reset rows `applied_force_n` is forced to zero
(`Pilot_Noise/Recording_Requests.md`, item 2), so those values are fake and
would inject a fake reversal into the average.

**Decision:** segments crossing the boundary are not trimmed, they are
**dropped entirely**. Measured loss: ~300–390 segments per angle (12–25% of
candidates), acceptable.

### 3.6 Sign alignment

+10° and −10° mirror the same event: in one the corrective force is
positive, in the other negative (for the sign convention see
[03 §2](03_State_Action_Episode.md)). Ludolph counts each angle as a
separate event. We keep both but pool the negative-angle segments **with
their sign flipped**; the segment count doubles and the interpretation does
not change.

## 4. Feasibility check: the method works on our data

**What was the problem:** Ludolph's method rests on a silent assumption: the
mean segment draws a smooth S and crosses zero **once**. In our data 73.9% of
active samples are exactly zero (the spring-loaded analog stick returns to
centre). If the mean curve crawls around zero, the zero crossing becomes
unstable and the measure loses meaning.

**Test:** the procedure above was applied and the resulting mean curve inspected.

### Result: the assumption holds

For |θ| = 10°, mean of 4,553 sign-aligned segments:

```
  -500 ms   -0.104   ███████████████
  -417 ms   -0.115   █████████████████
  -333 ms   -0.106   ███████████████
  -250 ms   -0.079   ███████████
  -167 ms   -0.041   █████
   -83 ms   -0.012   █
    -0 ms   +0.035          █████
   +83 ms   +0.123          ██████████████████
  +167 ms   +0.169          ████████████████████████
  +250 ms   +0.176          █████████████████████████
  +333 ms   +0.165          ███████████████████████
  +500 ms   +0.130          ██████████████████
```

A clean sigmoid: starts negative, crosses zero once, saturates and eases back
slightly. Measured:

- **Single zero crossing**, at −53 ms
- Amplitude 0.297; standard error of the mean 0.0014–0.0043 → **signal/noise ~70×**
- Slope around zero +0.92 units/s; the crossing is sharp, no crawling

63% of the segments consist of exactly-zero samples, but **the mean is still
smooth**: the reversal happens at slightly different moments in different
segments, so averaging produces a continuous ramp. The worry was unfounded.

### It also works at the real granularity

In participant × condition cells (pooling the |θ| 8–12° band):

| | |
|---|---|
| Cells | 60 / 60 filled |
| Segments per cell | min 192, median 384, max 509 |
| **Cells with a single zero crossing** | **59 / 60** |
| No crossing found | 0 |
| More than one crossing | 1 |

Rule for multiple crossings: pick **the crossing with the steepest rise**.
Pooling a narrow band instead of a single angle already solves most of this:
P002 gave 3 crossings at a single angle and dropped to one (−88 ms) with the
band.

## 5. NB04 results (2026-08-31)

Main band |θ| = 10° ± 2, sign-aligned, 22,524 segments. All numbers are
`04_control.ipynb` output.

### 5.1 The measure works

| | |
|---|---|
| Events (4 bands total) | 91,165 |
| Segments (after dropping those crossing episode boundaries) | 76,888 |
| Dropped | 12.9% (band 10) to 23.8% (band 20) |
| Pooled curve zero crossing | **−52.6 ms**, bootstrap 95% CI −55.6…−49.5 |
| Number of crossings | 1 (single, rising) |
| Amplitude / standard error of the mean | 154× |
| Participant × condition cells | 60/60 filled, 59 with a single crossing, 60 with a real reversal |
| Segments per cell | min 192, median 384, max 509 |

### 5.2 Person differences swamp condition differences

| | ms |
|---|---|
| Range of person means | −143.3 … +126.0 |
| Between-person spread | **269.3** |
| Between-condition spread (centred) | **15.4** |
| Within-person, between-condition sd | 27.6 |

The condition spread is below even within-person noise. Paired differences
against baseline: N1 +6.5 ms (dz 0.17), N2 +15.4 (0.38), N3 +6.5 (0.16),
N4 +11.8 (0.26). All point toward "noise reduces anticipation", but with the
median the profile flattens (no_noise +1.1; N1 −9.4; N2 +6.4; N3 −0.3;
N4 +1.4) and it flips sign across angle bands (§5.5).

**Conclusion: no evidence that noise disrupts action timing.**

11 of 12 participants are negative (anticipatory). P007 is the only
exception (+126 ms), and it also stood out in the action distribution in
NB02 (D share 15.2%, ~2% in the others).

### 5.3 The learning shift is not robust

Window means (10 trials each, conditions pooled):

| | 1–10 | 11–20 | 21–30 | 31–40 | 41–50 |
|---|---|---|---|---|---|
| Mean | −39.0 | −59.3 | −76.0 | −92.6 | −84.2 |
| Median | −61.5 | −83.4 | −85.5 | −64.9 | −83.7 |

The mean shows the shift Ludolph expected. Two checks:

**Composition.** Participants balance better as they go on, and the share of
fast crossings drops from 18.1% to 11.1%. Since velocity strata give very
different timings (§5.4), this alone could produce a fake shift. Taking the
mid stratum alone, the shift persists (−73.2 → −110.5), so the effect is not
entirely composition.

**How many people show it.** This is the real test, and it fails. Two
people drive the mean, P007 and P012; both start the session positive
(reactive) and move negative. With them removed, the window means flatten:
−124.2 / −117.1 / −128.3 / −124.2 / −123.8. The median was flat from the
start. Per-person linear slope: mean −9.6 ms/window but median −5.5, sd 24.1,
negative in 7 of 12; excluding P007 and P012 the mean is −0.6.

Alternative explanation: these two started in an atypical place in their
first window and moved toward the group, regression to the mean. Within-cell
noise is also large (person × window sd ~100 ms).

The expectation caveat in §3.2 held: Ludolph measured learning in a task of
over an hour with gradually increasing gravity; we have one session, 21
minutes, fixed g = 1.0.

### 5.4 The measure is undefined for slow crossings: a methodological finding

Velocity stratification showed something unexpected:

| Stratum | n | Zero crossing | Amplitude | mean_pre | mean_post | Real reversal |
|---|---|---|---|---|---|---|
| slow | 4,828 | **none** | 0.057 | +0.002 | +0.046 | no |
| mid | 14,544 | −52.8 ms | 0.256 | −0.098 | +0.124 | yes |
| fast | 3,152 | −25.0 ms | 0.887 | −0.297 | +0.299 | yes |

**In the slow stratum the mean curve stays positive throughout.** When the
pole passes the angle slowly, the participant is already pushing in the
corrective direction; there is no separate reversal. So action timing is
**undefined** there; the measure only exists if there is a real reversal.

At cell level this is even clearer: only 2 of 12 cells in the slow stratum
have a real reversal. Yet the "find the zero crossing" code returns a number
every time, since the smallest wiggle on a flat curve looks like a crossing.
The resulting mean is −440 ms, completely meaningless.

**So `curve_stats` now produces two flags:**

- `reversal_ok`: does the mean curve go from negative to positive
- `guvenilir` ("reliable"): additionally, is the amplitude at least
  `timing.min_amp_sem_ratio` (= 10) times the standard error of the mean

Ludolph does not have this distinction because he dropped everything outside
20–80%; the decision to stratify instead of exclude (§3.3) made this finding
visible.

The fast stratum is interesting the other way: amplitude 3.5 times the mid
stratum; zero crossing closer to zero (−25 ms). A large, late but sharp
correction.

### 5.5 Angle band sweep

Pooled zero crossing: 5° → −12.9 ms, 10° → −52.6, 15° → −97.8, 20° → −145.6.
As explained in §6, this gradient is largely geometry and is not interpreted.

Condition pattern (cell means, ms):

| Band | no_noise | N1 | N2 | N3 | N4 |
|---|---|---|---|---|---|
| 5 | −9.5 | −11.0 | +5.3 | +2.4 | +2.6 |
| 10 | −70.5 | −64.0 | −55.1 | −64.0 | −58.7 |
| 15 | −128.7 | −104.5 | −118.3 | −133.4 | −128.4 |
| 20 | −164.4 | −169.8 | −187.3 | −190.0 | −181.1 |

In bands 5 and 10 no_noise is the most negative; in band 20 it is the most
positive. **The pattern does not replicate**; a real condition effect would
keep its direction.

The learning pattern points the same way in all four bands, but the "how
many people show it" check from §5.3 applies equally to each band.

### 5.6 Action variability carries no separate information

| Condition | variability | amplitude | var/amplitude |
|---|---|---|---|
| no_noise | 0.117 | 0.353 | 0.343 |
| N1 | 0.110 | 0.357 | 0.355 |
| N2 | 0.100 | 0.329 | 0.324 |
| N3 | 0.098 | 0.325 | 0.328 |
| N4 | 0.098 | 0.327 | 0.319 |

Raw variability falls steadily with noise (dz −0.77 at N4, in 8 of 12
people). But divided by amplitude the effect largely disappears (dz −0.27).
So under noise people do not behave more *consistently*, they just apply
smaller forces. Within-participant correlations confirm this:
variability–amplitude r = +0.64, variability–control_effort r = +0.40.

The zero crossing itself is unrelated to the NB03 metrics (r = +0.06 with
control_effort, −0.04 with maPA): action timing is not a copy of the
performance measures, it measures a separate construct.

## 6. Do not compare across angles

The zero crossing becomes more negative as the angle grows: −13 ms (5°), −53
(10°), −98 (15°), −145 (20°). **This does not mean "more anticipatory at
larger angles".**

A falling pole passes 5° first and 20° later. A single reversal, measured
against later and later reference points, naturally comes out more negative.

Measured: within the same fall, getting from 5° to 20° takes a median of
**256 ms** (n = 2,465, IQR 158–438). The zero-crossing difference is 132 ms.
So roughly **half of the gradient is geometry** and half is real: the action
does not happen at a fully fixed moment, it partly tracks the angle.

A rough decomposition (it compares a median crossing time with a difference
of mean curves, and the segment sets are not identical), but the practical
conclusion is clear: **fix the angle and compare along condition or trial
order.** Differences across angles are not interpreted.

## 7. What NB04 did

| Step | Where | Note |
|---|---|---|
| `state_events` generation, sub-frame interpolation | `timing.build_segments` | 91,165 events |
| Segment extraction, sign alignment, episode-boundary exclusion | same function | 76,888 segments |
| Velocity stratification | `timing.add_velocity_strata` | participant × angle-level quantile |
| Curve statistics and zero crossing | `timing.curve_stats`, `pick_crossing` | steepest rising crossing when multiple |
| Bootstrap CI | `timing.bootstrap_zc` | 400 repetitions |
| Cell tables | `timing.timing_cells` | keyed: condition / trial window / stratum |
| Learning axis | `timing.add_trial_window`, `window_profile`, `learning_slopes` | 10-trial windows |
| Band sweep | `timing.band_sweep` | 5 / 10 / 15 / 20 |
| Action variability | inside `curve_stats` | ±60 ms, also divided by amplitude |

**Not done:** how the I/CR/D/A distribution changes with condition. Left out
of scope (decision of 2026-08-31); the statistical usability of class A is
still open.

## 8. Open items

- **Class A is rare (0.30%).** It was a meaningful share in Park. The
  distribution by condition was not done in NB04; no decision yet.
- **Behaviour in the slow stratum is not described.** We know the measure is
  undefined there; what the participant does in that regime (continuous
  corrective pushing) needs a separate measure. Does not affect the pilot decision.
- **The learning question is not closed, it just cannot be answered with
  this data.** A single 21-minute session is not equivalent to Ludolph's
  design. If the main experiment has longer sessions, the same pipeline runs
  directly.
