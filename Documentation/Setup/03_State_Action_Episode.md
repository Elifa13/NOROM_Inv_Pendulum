# 03: State, action classes, episode and regime run

**Notebook:** `Data Analysis/Notebooks/pilot_noise/<dataset>/02_build.ipynb`
**Code:** `src/build.py`
**Config:** `config.yaml` → `build`, `input_events`
**Output:** `samples_built`, `episodes`, `regimes`, `input_events` parquet
**Source:** Park et al. 2025, *Exp Brain Res* 243:44 ([[Park_2025_ExpBrainRes]])

The numbers in this record are from pilot1 (12 participants) unless stated otherwise.

---

## 1. State: phase plane

Park's definition, taken as-is:

```
fall_state  = θ · ω > 0    # tilted and rotating toward the fall side
safe_state  = θ · ω < 0    # tilted but rotating back toward vertical
```

**Current distribution (active samples):** fall 63.5%, safe 36.5%.

Note: the "pole rotating downwards" condition Ludolph uses as an event filter
in his action timing analysis is **the same criterion** as Park's fall
quadrant. This is where the two papers connect.

## 2. Sign convention: verified from the data, not assumed

Park says "joystick sign **opposite** to θ = corrective". This **cannot be
transferred as-is**: in Park's VIP the joystick directly sets angular
acceleration, whereas in our cart-pole the force goes to the cart and its
effect on the pole is inverted.

**Measurement:**

- mean `dθ/dt = −21.0 °/s` when `F > 0`
- mean `dθ/dt = +25.6 °/s` when `F < 0`
- Participant behaviour points the same way: at θ = +2..+10°, mean input is +0.025

**Conclusion: the corrective force has the same sign as θ.** All action
classes are defined in this inverted convention.

This could not be taken from the literature as-is and had to be derived from
the data. Had it been taken wrong, the CR and D classes would have swapped.

## 3. Action classes

```
I  : |u| ≤ band              persistent input within the neutral band
CR : u·θ > 0                 corrective (Corrective Reaction), in every quadrant
A  : u·θ < 0  and  θ·ω < 0   braking the return to vertical (Anticipatory, safe only)
D  : u·θ < 0  and  θ·ω > 0   force toward the fall (Destabilizing, fall only)
X  : unclassified            transient pass through the band / degenerate sign
```

`u` = `input_applied`.

### Thresholds and rationale

| Threshold | Value | Rationale |
|---|---|---|
| `build.input_neutral_band` | 0.02 | **73.9% of samples are exactly zero**; the smallest non-zero value is 0.0153. Unity's deadzone is already applied; in practice the band means "exactly zero" |
| `build.neutral_transient_max_samples` | 3 | Park's footnote: values stuck in the band count as I; a quick pass through the band while the stick moves from left to right does not. Neutral runs shorter than this threshold between opposite-signed deviations are labelled X |

`input_raw` and `input_applied` are **identical** (maximum difference
0.000000); the two columns are redundant.

### Input device: analog stick

`metadata.input_device` = **`Xbox Controller`**, platform `WindowsPlayer`.
The data confirms it:

- **136 distinct** non-zero magnitudes, quantized in ~0.0098 steps (the
  resolution of the analog axis)
- smallest non-zero value 0.0153, the edge of the dead zone
- samples at saturation (|u| = 1.0) are only ~5% of non-zero samples

So the input is **graded**, not on/off. 73.9% being exactly zero comes from
the spring-loaded stick returning to centre and the dead zone clipping small
values; nothing odd.

This is good news for Ludolph's action timing method: it assumes "the mean
force curve draws a smooth S and crosses zero once", which is reasonable for
an analog stick. It still needed empirical confirmation (see
[05_Action_Timing.md](05_Action_Timing.md)).

### Current distribution (active samples)

```
I  74.5%    CR 22.5%    D 2.7%    A 0.30%    X 0.01%
```

**A is very rare (0.30%).** In Park it was a meaningful share. Likely reason:
63.5% of the time is spent in the fall quadrant; participants are fighting
falls, not fine-tuning around vertical. A finding, not a bug; whether it is
usable statistically at this rarity was to be decided in NB04.

The per-regime profile matches Park's qualitative pattern: D is highest in
Failed (26.5%) and CR lowest (19.0%); CR is highest in Safe (38.8%).

## 4. Episode and regime run are not the same thing

Keeping these two apart is critical. They serve different literatures.

| Unit | Definition | Count | Used for |
|---|---|---|---|
| **Episode** | reset to reset | 2,017 | T₀, duration (Ludolph) |
| **Regime run** | quadrant sequence; a new run starts when θ·ω changes sign | 18,891 | Safe/Saved/Failed (Park) |

On average 9.4 runs per episode. Runs do not cross episode boundaries.

### Episode (`segment_episodes`)

Each episode is a continuous active segment within a trial, between two
resets (or between trial start / trial end and a reset). Recorded: initial
angle and velocity, duration, maximum |θ|, whether it ended in a fall, fall
cause, whether censored, T₀ and T/T₀.

**Censored episode** = one that did not end in a fall and was cut because the
20 s trial ran out. **600 of 1,756** measurement episodes are censored
(34.2%). This share cannot be ignored; for how duration analysis handles it
see [04 §4](04_Performance_Metrics.md).

### Regime run (`segment_regimes`)

| Label | Definition | Share |
|---|---|---|
| `Safe` | run in the safe quadrant, returning to vertical | 45.4% |
| `Saved` | started in the fall quadrant, rescued before reaching the limit | 45.2% |
| `Failed` | run that reached the **angle** limit (±60°) | 6.6% |
| `censored` | last run in the fall quadrant, cut by the end of the trial | 2.1% |
| `TrackLoss` | run ending with the cart hitting the track limit | 0.7% |

`build.regime_min_samples` = 2. Runs shorter than this (135 of them) are
noted separately.

## 5. Fall cause splits in two

`fall_event` fires for two different reasons and **they must be separated**:

| Cause | n | Mean &#124;θ&#124; at fall |
|---|---|---|
| `angle`: pole reached ±60° | 1,241 | 61.0° |
| `track`: cart hit the ±5 m track limit | 140 | 21.3° |

Zero overlap, zero unexplained. One track-caused fall happened at **0.27°**:
the cart left the track while the pole was perfectly upright. **42 of the
140** were in the safe quadrant, i.e. while the pole was returning to vertical.

**Decision:** `Failed` is used only for angle-caused falls (that is what is
comparable with Park); track loss gets a separate `TrackLoss` label and is
excluded from Park comparisons. Park has no equivalent because his VIP has no
track.

## 6. Input events (`detect_input_events`)

**Note: these are NOT Ludolph's events.** The naming was split on 2026-08-31:
input-side events are `input_events`, Ludolph's state-side events are
`state_events` (produced in NB04).

The events in this table are defined **on the input side**:

| Event | Definition |
|---|---|
| `onset` | leaving the neutral band (`input_events.onset_min_samples` = 3 samples must stay outside the band) |
| `offset` | returning to the neutral band |
| `reversal` | force changes direction (neutral samples skipped) |
| `fall` | moment of the fall |

**Current counts:** onset 14,001, offset 13,288, reversal 6,849, fall 1,381.
The `fall` event count is identical to the sum of Unity's
`trial_summary.fall_count` (1,381), an independent check.

Events are searched **within episodes**. Reset rows are already excluded, so
no fake zero crossings appear between segments. This separation matters
because on reset rows `applied_force_n` is forced to zero while
`input_applied` keeps its last value (see `Pilot_Noise/Recording_Requests.md`,
item 2).

Ludolph's event, by contrast, is defined **on the state side**: the pole
passing a given integer angle while rotating downwards. How the two
definitions relate, and the action timing computation, are the subject of
[05_Action_Timing.md](05_Action_Timing.md).

These events are for **descriptive statistics and QC**; comparing the `fall`
count with Unity's `fall_count` is an independent check. Ludolph's action
timing does **not** use them (see [05](05_Action_Timing.md)).

The number of Ludolph-type events was measured (fall-direction crossings,
measurement + `analysis_include`):

| Angle range | Crossings | Per participant × condition |
|---|---|---|
| ±25° | 110,091 | ~1,835 |
| ±15° | 79,607 | ~1,327 |
| ±10° | 57,549 | ~959 |
| ±5° | 29,198 | ~487 |

More than enough to average in every range; the choice of range is a question
of interpretation, not feasibility.
