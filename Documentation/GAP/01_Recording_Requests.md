# GAP: Recording requests

rev 4, 2026-09-09. The random force arm is outside this document.

The full design is in [00_Design.md](00_Design.md). Which column feeds which
analysis is tabulated in [02_Modelling_Plan.md](02_Modelling_Plan.md).

**Changes in rev 3.** The eight-phase flow was settled, so the `phase_label`
list was rewritten. It was confirmed that the gravity increase follows a
fixed schedule rather than success, so `trial_success` moved from tier one to
tier two. Since the occlusion test structure is known, `occlusion_stimuli.csv`
moved up from tier three to tier two.

**Changes in rev 4.** It was clarified that the control group stays at
g = 1.0 for the whole session, and the column requests were updated
accordingly. It was confirmed that occlusion stimuli will be cut from the
pilot's no-noise trials and all will be at g = 1.0. It was confirmed that the
correct answer will not be shown. With these three answers the question list
went down to one.

The `trial_success` request was removed entirely. Since gravity no longer
depends on success, it was not a validity requirement for the analysis, and
with trials fixed at 20 seconds the definition of "successful" was unclear
anyway. We can derive the same information from `fall_event` ourselves, as
was done in the pilot.

## What I will do

I want to measure three things separately.

General learning, i.e. performance improving over the session.
The temporary degradation each time gravity increases, and the recovery after it.
How accurately the person predicts in the occlusion test.

All three happen in the same participant at the same time, and on a single
performance curve they look alike. Separating them requires recording which
gravity and which phase each trial belongs to.

---

## 1. Without these, no analysis is possible

### Balancing side

| Column | File | Type | Why I need it |
|---|---|---|---|
| `gravity` | trial_summary | float, m/s² | The gravity in effect during that trial. Without knowing at which gravity the behaviour was measured, neither learning nor adaptation analysis is possible |
| `phase_label` | trial_summary | string | Which phase the trial belongs to. Value list below. No free text; keep capitalization fixed |
| `block_id` | trial_summary | int | Block number |
| `stick_raw` | timeseries | float, [-1, 1] | The raw value read from the device, with no processing at all. Both current input columns are already processed, and three quarters of the samples are exactly zero. Some of those zeros are real absence of intervention, some are small movements below the threshold. I cannot tell them apart |
| `log_schema_version` | metadata | string | The logging code is being written this week and may change during collection. If I don't know which file was written with which column set, I end up silently with two formats. Increment it when a column is added |

### `phase_label` values

Each of the eight phases gets its own label. No values outside this list:

| Value | Phase | Note |
|---|---|---|
| `familiarization` | 1 | Not analysed, but labelled so it can be dropped |
| `baseline` | 2 | |
| `prediction_pre` | 3 | also this value in occlusion_responses.csv |
| `adaptation` | 4 | |
| `late_adaptation` | 5 | |
| `prediction_post` | 6 | also this value in occlusion_responses.csv |
| `readaptation` | 7 | |
| `washout` | 8 | |

This list is critical. Phases are separated from each other only by this
column. If a single label is missing or merged (e.g. adaptation and late
adaptation get the same label), those two phases cannot be separated in the
analysis, and there is no way back.

Phases 3 and 6 have no balancing trials. If trial_summary rows are still
written during those phases, label them as above; do not leave them empty.

**The control group uses the same eight labels.** That group spends the whole
session at g = 1.0, and phases 5, 7 and 8 have no separate meaning for it.
But the labels must be the same so trials can be matched between groups.
Otherwise "the gradual group's washout versus the control group's trials at
the same point" cannot be compared, and the aftereffect cannot be computed.

### Two notes on `stick_raw`

Do not round it when writing the CSV; at least 6 decimal places. Otherwise
the small values that are the point of this column turn into zero.

What I mean by "raw" needs to be spelled out, because there can be several
steps between reading and the applied value: deadzone, curve, clipping,
smoothing. I want the value read from the device recorded before any of
them. Also write in the metadata **in what order** these steps are applied
(`input_pipeline` below).

### Occlusion side

**`<pid>_<sid>_occlusion_responses.csv`**, one row = one occlusion trial.

`participant_id`, `session_id`, `occlusion_block_id`, `phase_label`,
`occlusion_trial_id`, `stimulus_id`, `stimulus_gravity`, `session_time_s`,
`observation_duration_s`, `occlusion_duration_s`,
`onset_pole_angle_deg`, `onset_pole_angular_velocity_deg_s`,
`onset_cart_position_m`, `onset_cart_velocity_m_s`,
`true_pole_angle_at_occlusion_end_deg`,
`response_option_index`, `response_angle_deg`, `response_rt_s`, `response_valid`,
`force_during_occlusion_n`

Notes:

The `onset_` columns are the true state **at the moment the pole is
hidden**. The whole analysis rests on them, because the correct answer
depends only on this state and on gravity.

`true_pole_angle_at_occlusion_end_deg` is the angle at the **end** of the
occlusion window, not at the moment of the response. That is why the name is
long, so they don't get confused.

`force_during_occlusion_n` should be zero by design. I want it to verify that.

`stimulus_id` is the link key between the two files. Presentation order
changes from person to person and block to block, so rows can only be
matched through it. Three conditions: the same stimulus carries the same id
in all participants, the same id in the pre and post tests, and the id is
identical to the one in `occlusion_stimuli.csv`. If this fails, no
within-stimulus comparison is possible.

`occlusion_trial_id` is the presentation order, i.e. the position of that
trial within its block. Needed to control order effects (fatigue or drifting
attention within a block) and to verify that randomization really differs
between people. The second is not a theoretical worry: in pilot 1 the seed
was fixed and all participants saw the same order; we only noticed from the data.

`stimulus_gravity` will be 1.0 for every stimulus, because stimuli are cut
from the pilot's no-noise trials. Write the column even though the value is
constant: the analysis computes the correct answer from this number, and if
stimuli from another gravity are added later the format will not have to change.

The correct answer will not be shown to the participant. This concerns the
application rather than the recording, but I write it here too, because in
Ludolph the group difference disappears completely in the blocks with feedback.

---

## 2. Cheap, not critical

| Field | File | Why I need it |
|---|---|---|
| `gravity_step_index` | trial_summary | Which step we are in, 1 to 10. Gravity does not change in the control group, but write the column anyway with the same numbering: that is the only way to match the two groups' trials |
| `trial_index_in_step` | trial_summary | Trial number within the step, 1 to 8. The early (1-3) and late (6-8) split comes directly from this column, so I don't have to reconstruct the order |
| `gravity_current` | timeseries | If gravity does not change within a trial, this column copies trial_summary. I still want it: if trial_summary is written when the trial ends, it might accidentally record the new gravity. With two sources I catch the inconsistency |
| `session_time_s` | trial_summary and occlusion_responses | Seconds since session start. To put balancing trials and occlusion trials on one timeline. I will also read from it how much time passes between phases 6 and 7 |
| `frame_time_s` | timeseries | `Time.realtimeSinceStartup`. The physics counter does not show real time; it advances the same even when the computer stalls. To find where the stalls are |
| `render_frame_count` | timeseries | Which render frame we are on when the row is written. Shows how many physics steps fall on the same render and the same stick reading. If the frame rate drops, the same stick value repeats over several rows, which gets confused with holding the stick still |
| `group_id` | metadata | Which group the person is in: gradual or constant |
| `gravity_schedule` | metadata | That person's phase-by-phase gravity plan. For the gradual group: starting value, step size, trials per step, ceiling; for the control group: constant 1.0. Since the increase follows a fixed schedule, no trigger criterion field is needed, but write the schedule itself. The two groups filling the same field differently is enough; no separate field needed |
| `input_device` | metadata | Name and model of the device used |
| `input_pipeline` | metadata | The steps from raw reading to applied value, **in order**. For example deadzone threshold, then curve type, then clipping. So the transformation between `stick_raw` and the existing column can be reproduced |
| `probe_config` | metadata | Number of blocks, trials per block, observation duration, occlusion duration, and **the list of response option angles**. I don't want to assume the options are evenly spaced; make it a list |
| display info | metadata | Resolution in px, screen size in cm, viewing distance in cm, refresh in Hz |

**`occlusion_stimuli.csv`**, one file per experiment, one row = one frame of
the shown trajectory.

`stimulus_id`, `sample_index`, `t_s`, `pole_angle_deg`,
`pole_angular_velocity_deg_s`, `cart_position_m`, `cart_velocity_m_s`,
`applied_force_n`, `gravity`

In rev 2 this file was in the "nice to have" tier; not any more. The reason
is the trial count: there are 2 blocks x 40 = 80 occlusion trials per person;
Ludolph used 440. With so few trials, per-person parameter estimation will be
strained, and bringing the observation phase into the model is the only
extra source of information we have.

Since stimuli are shared by everyone, the file is **one per experiment**,
not per participant. 40 stimuli, each 5.5 seconds (4.5 s observation + 1 s
zero force), 330 rows per stimulus at 60 Hz, about 13,200 rows in total. The
cost is writing it once.

**Use the same 40 stimuli in the pre and post tests.** With different sets,
a difference between the two tests cannot be attributed to the internal model
changing rather than the second set being harder. With the same set, stimulus
difficulty drops out completely and the comparison is both within-person and
within-stimulus. Since there is no feedback there is no risk of remembering
the correct answer; Ludolph also repeated the same 40 stimuli over eleven blocks.

---

## 3. Format rules

- The column always exists. If that condition does not apply in that trial,
  don't delete the column; write a constant value.
- No empty cells. Ids are integers, absence is -1. Flags are 0/1, not strings.
- `phase_label` only takes the eight values above; no free text.
- Decimal separator is a point. Do not round `stick_raw`.
- Do not change the names or order of existing columns; append new ones at the end.
- If the column set changes, increment `log_schema_version`.

---

## 4. Numbers

The trial counts of the eight phases are settled: familiarization 3, motor
baseline 8, adaptation 10 steps x 8, late adaptation 8, re-adaptation 8,
washout 8. 115 balancing trials in total. Prediction tests 40 trials each,
80 in total.

**All numbers are the same in both groups**; the only difference is gravity.
The control group does the same number of trials in every phase at g = 1.0.
The size of the aftereffect can only be computed if this match is kept.

I will derive the number of participants per group from a simulation-based
power analysis and send it separately.
