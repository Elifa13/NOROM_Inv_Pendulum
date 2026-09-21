# Pilot data: requests for the recording format

**Revision 2, 30.08.2026.** The first version (26.08.2026) was based on 106
trials from P001–P002 (smoke-test data at the time, later deleted). This
version is based on **636 trials from 12 real participants** (600
measurement). All numbers were re-measured; a few items got weaker, one was
dropped entirely, one got stronger.

*Status note (2026-09-21): items 1 (seed) was fixed before pilot2. See
`Pilot2_Results_Summary.md` for what changed and what did not.*

The recording mechanics are sound: sampling happens in FixedUpdate, every
measurement trial has exactly 1200 samples covering exactly 20 seconds, the
angle is within −180/+180 with upright at 0°, velocity columns are consistent
with the derivative of the positions, no NaN, no duplicates, the 10 rounds ×
5 conditions balance is complete, and the physics parameters match Ludolph.
We re-derived the physics model from the data and validated it: correlation
with observed angular acceleration 0.988–0.997.

The items below are concrete points where the analysis got stuck. For each I
wrote the evidence in the data and what is lost without it. **In order of
importance.**

---

## 1. Derive randomizationSeed from participant_id and reseed every session

**The most important item in this document. The evidence has grown much
stronger since the first version.**

**Now:** `randomizationSeed: 12345` fixed, in all 12 participants.

**What the data shows, three separate consequences:**

- **Identical condition order.** All 12 participants get the same 50-trial sequence.
- **Identical `noise_seed` sequence.** Everyone saw exactly the same noise pattern.
- **Initial angles also come from a single fixed list.** P001–P007 all read
  from the same angle sequence (100% alignment). Their entry points differ:
  P001/P002/P004/P006 offset 0, P003 76, P007 89, P005 253. The offsets match
  the session chain exactly: P002 made exactly 76 draws and P003 enters at
  76; P004 made exactly 253 and P005 enters at 253.

So **when the app is not closed between participants, the RNG stream
continues where it left off; when it is closed, it goes back to 0.** None of
P008–P012 is at offset 0 either (if they were, they would match P001's first
152 draws), so the app seems never to have been closed on the afternoon of
27 August.

Why the angles look independent from the outside: the cursor advances with
behaviour; every fall consumes a draw. Different fall counts → different
places in the same list. Trace: the −4.0469° P001 got in T002, P002 gets in T005.

**Why it matters:** the point of randomizing order is that if a participant
tires or learns, the effect is spread over different conditions in each
participant. If the order is the same for everyone, the condition at position
7 is the same condition for every participant. Also, since everyone saw the
same noise pattern, there is no way to tell if that one pattern happens to be unusual.

**Its current effect was measured and is small:** initial |θ| is balanced
across conditions (means 3.53–3.85°, spread 0.32°) and weakly correlated
with the outcome (r = +0.066 with fall count). On the condition order side,
it is reshuffled within each round; each condition's mean `trial_order` is
24.6–26.5 (range 1–50), so learning/fatigue is not confounded with condition.

**Without it:** adding participants produces no new information about
stimulus variety. Even with 20 people, they all saw the same pattern in the
same order. When conditions come out close to each other, this bias reaches
the same size as the effect being measured.

**Requested:** derive the seed from `participant_id` **and reseed the RNG at
the start of every session.** This solves all three problems.

**Note:** your own document's section 11 checklist, item 9, already asks for
this ("Do two different participants accidentally share the same noise
seed/order?").

---

## 2. Do not write 0 to applied_force_n on reset rows; leave it empty

**Now:** on `phase = reset` rows `applied_force_n` is forced to 0.0 (all
82,860 reset rows), but `input_applied` keeps the participant's last value:
non-zero in **35.8%** of reset rows.

**Why it matters:** action timing, Ludolph's main analysis, measures the
moment the force curve crosses zero. Writing a hard 0 into the force column
for 60 frames at every reset creates a direction change the participant
never made. There are **1,381 resets** in the data, i.e. 1,381 fake events.

We currently handle it on the analysis side with episode boundaries (events
are searched only within continuous active segments), but it is a trap that
needs attention again in every analysis.

**Without it:** action timing comes out wrong, and separating real crossings
from fake ones is constant extra work on the analysis side.

**Additional request:** a `bout_index` column (a counter within a trial that
increments at each fall). We currently derive it from `fall_event`; as a
column it would make it easier to be sure an analysis window does not
accidentally jump over a reset.

---

## 3. Reset velocities on reset

**Now:** after a reset the pole angle is correctly drawn from
U(−7.5°, +7.5°) and the cart returns to centre, but the velocities are not reset.

**What the data shows:** in **1,380 of the 1,381** within-trial restarts
there is residual angular velocity at the start, up to 13.7 °/s. (The first
version said "40 of 209 resets"; with more data it is clearly the rule, not
the exception.)

**Why it matters:** in Ludolph every trial starts from the same kind of
state: random angle, everything else zero. How long balance can be kept is
very sensitive to the initial state. If some trials start with the pole
already rotating, they are harder for a reason unrelated to condition. And
this residual velocity comes from the previous fall, so it is not even
random: a trial after a bad one systematically starts harder.

**Without it:** unexplained extra variance and initial conditions that are
not comparable with each other. The T₀ computation assumes ω = 0; with
ω ≠ 0, T₀ does not fully reflect the real difficulty.

---

## 4. Fields to add to the metadata

Listed in section 7 of your document but not present in `metadata.json`.
**All 24 of 24 fields are still missing.**

```
screen_width_px, screen_height_px, screen_physical_width_cm,
viewing_distance_cm, refresh_rate_hz, full_screen
input_axis_name, deadzone, sensitivity, invert_axis
noise: texture_width_px, texture_height_px, update_rate_hz,
       mean, clipping_method, monochrome_or_rgb, overlay_opacity
balance_angle_limit_deg, balance_cart_limit_m
experiment_version, build_id, scene_name, operating_system, session_start_utc
```

**The most critical is the screen and viewing distance group.** The
presentation says "1 virtual metre = 2.3 physical cm" and "the visual angle
of a noise element is 0.04°". Both are claims about the physical size of
objects on the retina. Verifying them requires the screen resolution, the
physical screen width and the viewing distance; none of the three is
recorded. `noise_element_size_px: 4` is recorded, but 4 pixels correspond to
a different visual angle on every monitor and at every distance.

Since the whole hypothesis is about visual noise, we currently cannot
express numerically what the participant actually saw. This is required for
comparison with Treviño (they state a 60 cm viewing distance and 2×2 pixels
≈ 0.08° of visual angle).

**Second priority is the input group.** `deadzone` and `sensitivity` are
unknown. From the data, the input ramps between −1..1 (186 distinct values,
smallest non-zero 0.0153) and 73.9% of samples are exactly zero, so a
deadzone is already applied but its value is not recorded.

**Minor note:** `noiseLevels[].sigma` is written as a float32 artifact
(`0.019999999552965164`, `0.05000000074505806`, `0.07999999821186066`).
Writing it as double or rounding it is enough. The `noise_sigma` column in
timeseries comes through clean; the issue is only in metadata.

---

## 5. Actual frame duration on every sample

**Now:** only `mean_fps`, `min_fps`, `dropped_frame_count` in the trial summary.

**What the data shows:** `mean_fps` 59.92–60.00, so the 60 Hz average is
fine. But in **53 of 636** trials `min_fps < 50`, the lowest 29.1. Total
`dropped_frame_count` 44. It also happens in no_noise trials, so it does not
come from noise rendering.

(The first version said "below 50 in 53/53 trials"; that was a property of
the smoke-test data. In the real data the rate is much lower: 8.3%.)

**Why it matters:** a frame lasting 34 ms instead of 16.7 ms is a moment
where the participant looks at an old image and the physics advances without
visual feedback. Exactly the kind of moment that will look like a control
error. Since sampling is in FixedUpdate there is no sample loss (every trial
has the full 1200), but what the participant **sees** is incomplete.

**Without it:** we cannot separate participant error from display stalls. In
an experiment about perceiving visual noise, render rate directly affects the
independent variable.

**Requested:** a per-sample `frame_time_ms` in timeseries (or a
`dropped_frame` flag). `window_focused` already exists and works; keep it.

---

## 6. Let the software record raw signals, not make the validity decision

**Now:** `valid_trial` is 1 in 634 of 636 trials. In two (P011 T030 and
T034) it is 0 with `invalid_reason = "paused"`. So the mechanism works, but
only for this one case.

The `device_disconnect`, `focus_lost`, `missing_samples` cases defined in the
document never trigger in practice. It may also be true that they really did
not happen in the current data: `window_focused` is 1 on every sample, there
are no dead-input trials, every trial has the full 1200 samples. So we see no
contradiction right now.

**My suggestion is still the same: don't let the software decide whether a
trial is valid.** Record the raw signals instead (`device_connected`,
`frame_time_ms`) and let us filter on the analysis side. Less work for you,
and thresholds can be changed later. The `paused` information is valuable,
keep it, but record the event itself (when, for how long it was paused)
rather than an "invalid" verdict.

**Small bug:** `config.participantId` is never updated; the metadata of all
12 participants says "P001". The top-level `participant_id` field is correct;
only the copy in the `config` block is wrong. Does not affect the analysis,
but invites confusion.

---

## Two design observations I also want to note

These are not recording format requests but observations from the analysis.
The decision is yours; I write them only for the record.

**The floor-effect concern has largely passed.** In the first version,
looking at the smoke-test data, I said "only 9 of 100 trials complete
without a fall, 3.4 falls per trial, median T/T₀ very close to 1, so
participants are at the level of *doing nothing*", and I found no
significant difference in any condition. **The real data looks different:**
**224 of 600** measurement trials (37.3%) complete without a fall, the mean
is 1.93 falls per trial, and the episode-level median T/T₀ is 1.52.
Participants are clearly above doing nothing. And significant differences
between conditions do appear. Task difficulty looks appropriate as it is.

**Signal strength is still an open question.** Treviño and colleagues'
stochastic resonance effect was observed when the signal was deliberately
pushed below threshold (by lowering coherence and luminance together), and
the paper notes performance saturates above 12% luminance. The pole here is
a high-contrast, large object on screen that tilts up to 60 degrees, clearly
far above threshold. Also, the sigma levels (0, 0.02, 0.05, 0.08, 0.25) are
nearly linearly spaced at the bottom and then jump by a factor of 3.1;
Treviño's levels are spaced on a logarithmic scale.

The pilot result supports this concern: no improvement at a middle level,
performance degrades monotonically as noise increases (see
[Pilot1_Results_Summary.md](Pilot1_Results_Summary.md)). So what we see looks like a
classic masking effect, not stochastic resonance.
