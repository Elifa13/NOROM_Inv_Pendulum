# GAP: Modelling plan

rev 4, 2026-09-09. The random force arm is outside this document.

This document is my working plan. The document that goes to the meeting is
[01_Recording_Requests.md](01_Recording_Requests.md). Every analysis here is the
justification for a recording request there. Full design in [00_Design.md](00_Design.md).

**Changes in rev 3.** Since the gravity increase was tied to a fixed
schedule, the regression-to-the-mean discussion in analysis C became
unnecessary. On the other hand, the number of occlusion trials became known,
and it is small: 80 per person, versus 440 in Ludolph. Whether D and E can be
done at person level became an open question, and the simulation-based power
analysis moved up in priority.

**Changes in rev 4.** It was clarified that the control group stays at
g = 1.0 for the whole session. This changes the frame of the plan. The group
comparison is no longer "who is better at the same difficulty" but "who
shifted how much between the same two points". All main analyses were
rebuilt as difference-in-differences. It was confirmed that all occlusion
stimuli are at g = 1.0, and since this turns the confound I was worried about
against the hypothesis, it stopped being a problem.

---

## Why we build models

None of the three things we want to measure is observed directly.

How much the person learned is not observed; their performance is.
The gravity in the person's head is not observed; the force they apply is.
The person's internal model is not observed; their prediction is.

All three are latent variables. They have to be inferred back from observed
behaviour. This is a system identification problem and it is not solved with
trial averages.

---

## Three rules for all analyses

**Groups are compared only at g = 1.0.** The control group spends the whole
session at 1.0; the gradual group is there only in phases 1, 2, 3 and 8.
Everywhere else the two groups do different tasks at different gravities,
and a performance difference between them is a difficulty difference, not a
learning difference. So every group comparison is built on these four phases.

The natural consequence is that the main analyses are
difference-in-differences. The gradual group's phase 8 minus phase 2 contains
two things: the aftereffect, plus general improvement from practising over
the session. The control group gives the same two points without any
adaptation, i.e. a measure of that general improvement. The difference of
the two differences is the pure aftereffect. The same structure applies on
the perceptual side: is post-test minus pre-test different in the gradual
group than in the control group?

**This design cannot ask Ludolph's question.** His constant arm was at 3.5
and both groups ended at the same difficulty, so "is gradual training better"
could be asked. There is no such point here. This claim will not be made
when writing up.

**The constant group has no gravity steps.** The sample for step-based
analyses (B and C) is a single group, the gradual group. The control group is
not in them.

**On the occlusion side the main quantity is within-person change.** We have
two measurement points, in the same person, with the same stimuli. The
within-person difference removes person-level noise (general attention, task
understanding, baseline bias). Ludolph could not do this, because his motor
group had been trained 335 days earlier and there was one measurement point.
This is what partly compensates for the small number of trials.

---

## Analyses

There are seven analyses. A and D are the foundations; the others build on them.

---

### A. Controller identification

**Goal.** Extract the person's control policy as a function, and see how that
function changes as gravity increases.

**Data.** `timeseries.csv`, active samples only. Inputs: `pole_angle_deg`,
`pole_angular_velocity_deg_s`, `cart_position_m`, `cart_velocity_m_s` and the
previous input. Target: `stick_raw`. For splitting: `gravity_step_index` and
`phase_label`. For timing: `frame_time_s` and `render_frame_count`.

**Method.** A two-stage model, because the input distribution is
zero-inflated. In the pilot, 73.9% of samples are exactly zero. A plain
regression would keep predicting near zero on this data and learn nothing.

1. Is there an intervention or not. Binary classification.
2. If so, how large and with what sign. Regression.

Delay is not assumed, it is fitted. The state is read at time t minus d; d is
swept from 0 to 400 ms and the value that maximizes held-out likelihood is
chosen. d itself is also a result.

Model ladder: ridge, then LightGBM, a small MLP if needed. Moving up a rung
requires a real held-out gain.

**Splitting, simplified in rev 3.** In rev 2 I planned to merge steps because
"too few trials may fall in each step for the fit to settle". That concern is
void: the design is balanced, every step has exactly 8 trials of 20 seconds.
That is 8 x 20 x 60 = 9,600 samples per step, more than enough for a ridge
fit. So the policy can be fitted **step by step**, ten separate fits. Merging
ranges, if done, would be a simplification choice, not a necessity.

**Critical methodological point.** At 60 Hz consecutive samples are near
copies of each other. Cross-validation is never done by splitting samples at
random; whole trials or blocks are always held out. Otherwise everything
comes out significant and all of it is fake.

The analysis will be repeated on a second unit: the input event. The state at
onset is the input, the event's amplitude and duration are the output. This
solves the autocorrelation problem at the root. The sample model for detail,
the event model for decisions.

**Internal control.** To verify that the policy really changes, we will try
to predict gravity from the person's input alone. The subtlety matters: the
model is not given the state. If it were, it would read gravity directly from
the physics rather than from the person's behaviour, because the pole's
acceleration is already a function of gravity. Then what you measure is a
physics detector with nothing to do with the human. That is why this is a
control, not a separate finding.

**Output.** For each (person × step): gain vector, delay, held-out score.

**Related requests.** `gravity`, `gravity_step_index`, `stick_raw`,
`frame_time_s`, `render_frame_count`.

---

### B. Policy drift

**Goal.** Measure the speed of adaptation without interpreting any parameter.

**Data.** A's fitted models.

**Method.** Test the model fitted at step k on step j's data. Do it for all
pairs. With ten steps this gives a 10 x 10 loss matrix. The rate of
degradation away from the diagonal gives how fast the policy changes.

**Output.** One matrix per person and a single drift-rate number derived from it.

**Why a model is needed.** No functional-form assumption. It shows the
policy changed without getting into a "did the gain go up" debate.

**Sample.** Gradual group only.

---

### C. Response to gravity steps

**Goal.** Measure the degradation each time gravity increases, and the recovery.

**Data.** `trial_summary` performance metrics, A's delay output,
`gravity_step_index`, `trial_index_in_step`. The success measure does not
come from the recording; we define it ourselves from `fall_event` (as in the
pilot: fall count and `falls_angle_per_trial`).

**The rev 2 problem is gone.** In Ludolph, gravity rises after a successful
trial, so a step does not arrive at random; it follows good performance. How
much of the post-step drop comes from gravity and how much from regression to
the mean cannot be separated. Ludolph did not address this, and in rev 2 I
planned to use the constant group as a control to correct it. In this design
the increase follows a fixed schedule, so there is no problem: a step comes
every eight trials, independent of performance. The post-step degradation can
be interpreted directly.

**Method.** Ludolph's definition applies directly. For each step, the first
three trials (`trial_index_in_step` 1-3) and the last three (6-8) are
averaged. Within-step improvement is last three minus first three; between-step
degradation is the next step's first three minus this step's last three. The
same computation is done separately for trial length, action timing and
action variability.

Since there are few trials per step, single-step fits will be noisy. A
hierarchical model will be used, so each step's curve borrows from the
person's and the group's mean.

**Output.** For each (person × step): size of the degradation and recovery
time constant.

**The real question.** Does the time constant shrink as steps go on? That is,
does the person learn not just the task but also how to adapt?

**Let's be honest about power, and the arithmetic changed.** Ludolph had 25
steps per person, each 0.1 m/s². We have 10 steps, each 0.25 m/s². The two
changes work in opposite directions: steps are two and a half times larger,
so the expected effect per step grows, but the number of steps to average
over dropped by more than half. In Ludolph's own data single-step effects were
noisy and only significant on average; for the variability effect they even
had to drop the first three steps. Larger steps may make this easier for us,
but averaging over 10 steps is noisier than averaging over 25. The direction
of the net effect is unclear; simulation will tell.

The correct statement: repeated within-subject events give a mixed model far
more support than the difference of two points. But an analysis that treats
them as independent repetitions would be wrong.

**Sample.** Gradual group. The control group is not in this analysis, since
it has no steps.

**The motor aftereffect is not a separate item; it continues C.** Phase 8 is
at g = 1.0, and the aftereffect is largest in the first trials and decays
after. So phase 8 is not a single mean but a decay curve, with the same
mathematical form as C's within-step recovery curve. It will be fitted with
the same hierarchical model; the only difference is the sign of the
perturbation. The comparison point is phase 2; the correction is the control
group's same two points.

---

### D. Decomposing the occlusion error and internal gravity

**Goal.** Find out why the error in the occlusion test changes, and turn the
gravity in the person's head into a number.

**Data.** `occlusion_responses.csv`, especially the `onset_` columns and
`stimulus_gravity`. If `occlusion_stimuli.csv` is available, the observation
phase can be modelled too.

The occlusion test is a separate block. The participant does not play; they
watch other people's recordings, and stimuli are shared by everyone. Both are
good news for the analysis: the person's own behaviour does not affect the
correct answer, and people are compared on the same stimuli.

**Method.** For each trial:

1. Start from the stimulus state at the moment of occlusion.
2. Simulate forward for the occlusion duration with an assumed gravity value,
   under zero force. This is exactly the same computation as the RK4 in our
   `src/physics.py`.
3. Round the resulting angle to the nearest response option.
4. Compare with the observed answer.

Two free parameters are found by maximum likelihood: the gravity the person
assumes, and the size of the noise in their answer. Since the force is zero
during occlusion, the outcome is only a function of the initial state and
gravity. That is what makes the parameter identifiable.

**Why a model is needed.** The mean error is a single number and mixes two
different things. If the bias shrank, the person learned the system's
physics. If only the noise shrank, the person got used to the task but their
internal model did not change. Both produce the same drop in mean error.

**The main constraint, the most important item of rev 3.** There are 2 blocks
x 40 = 80 occlusion trials per person. Ludolph used 11 blocks x 40 = 440, and
the group difference he found was 5.3 degrees, while the response resolution
is 10.8 degrees. So the effect is half a response step in size and only
becomes visible when averaged over many trials. We have the same 40 trials
per block but one fifth of the blocks.

This does not kill D entirely, but it sets its scale. There are three
scenarios, and simulation will say which holds:

| Scenario | What can be done |
|---|---|
| 40 trials are enough for a per-person parameter | D and E are done in full |
| 40 are not enough but 80 are | The parameter is estimated once per person (merging the two blocks). Pre-post change cannot be measured at person level, only at group level |
| 80 are not enough either | The parameter is estimated only at group level with a hierarchical model. Analysis E is dropped |

The risk of the two parameters getting confused is here too: the answers of a
very noisy person are spread out, which can look as if they assume a small
gravity. Whether the likelihood surface really separates the two will be
checked with the same simulation.

**Gravity of the stimuli: decided, and in our favour.** All stimuli are cut
from the pilot's no-noise trials, all at g = 1.0. So the test world is the
control group's world. Had the stimuli been cut from 3.5, the confound would
work in favour of the hypothesis, because the expected result is a shift in
the gradual group and that group would have lived close to the test. As it
is, the opposite: the gradual group is the side moving away, so any effect is
found despite a home advantage for the other group.

Staying at a single gravity does not prevent estimating internal gravity.
Stimuli start from different initial angles and velocities, and that variety
is enough to determine the parameter. What we lose is seeing whether the
person's internal model is right across the whole range or only at one point.
That would be possible with stimuli spread over the range, but the design
decision has been made.

**The direction of interpretation is reversed; don't forget this when
writing.** Both groups are tested at low gravity, and the gradual group
arrives adapted to high gravity. A person whose internal model went up will
predict the fall at g = 1.0 as faster than it is. So what is expected in the
gradual group is not "more accurate prediction" but "prediction shifted
upward". That is a perceptual aftereffect.

There is a trap here. In Ludolph everyone systematically underestimates the
fall; the mean error is negative. An upward shift of the internal model
pushes the error in the positive direction, i.e. toward zero. Getting used to
the task and truly improving pushes the same way. They cannot be separated by
looking at the mean error. The only way to separate them is the
two-parameter fit: if internal gravity comes up from below 1.0 to 1.0, that
is improvement; if it passes 1.0 and goes higher, that is an aftereffect.
This is the real reason D builds a model.

**Output.** For each (person × block): two numbers, internal gravity and
response noise. The quantity I care most about is the difference between
them, i.e. the change from pre to post.

**Note.** Ludolph parametrized the same skeleton differently. Since he could
not manipulate gravity, he fitted a "how many milliseconds does the internal
model stay accurate" parameter. That can also be fitted with the same
skeleton and compared.

---

### E. Comparing two independent measures of internal gravity

**Goal.** The gravity in the person's head is measured in two separate
places. Do they agree?

**Data.** D's output (perceptual measure) and the motor measure derived from
A and the existing action timing code.

**Why this is the most ambitious item.** The two measures are fully
independent. One comes from a perceptual task, the other from motor
behaviour. If they agree across people, we have shown that motor learning and
the perceptual internal model share the same representation. Ludolph
discusses this but cannot show it, because he ran the two experiments
separately and the motor group had been trained 335 days earlier.

**Three weaknesses, all to be accepted up front.**

The gravity estimate on the motor side is not well defined. A person applying
force early comes either from a good internal model or from being cautious.
So the motor measure is confounded with how aggressive the policy is. This
does not apply to the perceptual side, where the person's behaviour does not
affect the correct answer.

If both measures are noisy, the correlation between them is attenuated. With
noise on both axes, the true relationship cannot be found unless it is large.
And a null result says nothing, because "no relationship" and "could not
measure it" cannot be told apart.

The third was added in rev 3: the perceptual measure rests on one fifth of
Ludolph's trial count. If the third row of D's scenario table holds, E drops
out automatically.

**An opportunity the design missed.** The most direct way to show that the
two aftereffects share one representation would have been to see whether
they decay together. That would have needed another short prediction block
after washout. The current design does not have it, so we cannot ask the
question with a within-person contrast and are left with E's weak route,
between-person correlation. This limits how strongly E can be written up.

**Reliability gate.** Before E is run, the split-half reliability of both
measures will be computed. If reliability is low, E will not be done and
will not be reported. This is a precondition, not an excuse found
afterwards. If reliability is sufficient, the correlation will be reported
corrected for attenuation. (Candidate implementation: `src/reliability.py`,
see `Setup/06_Reliability.md`.)

**Risk management.** If E fails, the other six analyses are unaffected; each
stands on its own.

---

### F. Learning curves

**Goal.** Measure learning as a curve instead of a difference of two points.

**Data.** `trial_summary`, by trial order.

**Method.** An exponential or power-law curve per person, within a
hierarchical model.

**Output.** Three parameters per person: initial level, learning rate,
asymptote. Group differences are looked for in these parameters, not in the mean.

**Why a model is needed.** Two people can reach the same final performance by
different routes. One learns fast and plateaus, the other improves slowly but
steadily. The mean curve shows them as the same. Also, a curve parameter is a
less noisy number than a before-after difference.

**Caveat, eased in rev 3.** In the gradual group gravity increases over time,
so the raw performance curve is the sum of learning and increasing
difficulty. Without separating the two, groups cannot be compared. Ludolph
solved this by normalizing. In our design gravity is a known, fixed function
of time that is the same for all participants, so it can go into the model
directly as an explicit term. In Ludolph each person had their own gravity
profile; we have a single profile.

---

### G. Variability decomposition

**Goal.** Measure motor variability more cleanly than the raw standard deviation.

**Data.** A's residuals.

**Method.** Split input variance into three: the part explained by the
state, the part explained by the context, and the residual. The residual is
motor noise.

**Why a model is needed.** Raw variability is confounded with how hard the
person is struggling. In a hard situation everyone moves a lot. What remains
after removing the part the model explains is the part that is really noise.

**Secondary question, exploratory.** Does residual variability in early steps
predict that person's later learning rate? This is Wu and colleagues' 2014
claim. But we are looking for a correlation between two noisy person-level
estimates, and the third-variable risk is high: skill, motivation,
alertness. If something shows up, it will be written as an observation, not a
claim.

**Related request.** `stick_raw`. The deadzone erases small movements, so this
analysis cannot be done with the existing columns.

---

## Work to do before data arrives: simulation-based power analysis

In rev 2 this was "nice to have". In rev 3 it is the precondition that
decides whether D and E can be done. The trial count is now known, and it is small.

We have the physics code. The work:

1. Generate a stimulus set similar to Ludolph's, with varied initial angles
   and velocities. Set up two scenarios for stimulus gravity: all at 3.5, and
   spread over the range.
2. Generate fake participants with a known internal gravity and a known
   response noise.
3. Recover the parameters from this fake data.
4. Try trial counts of 20, 40, 80 and 440 separately.

Three outputs. How precise the per-person parameter estimate is at 40 and 80
trials, whether the two parameters get confused, and how much spreading the
stimuli over the range improves the estimate. All three are concrete numbers
that can go to the team, and all three say which row of D's scenario table holds.

The same simulation will be set up for C: compare the power to detect the
step effect with 10 steps x 0.25 versus 25 steps x 0.1.

---

## Which column for which analysis

| Column | Analyses | What happens without it |
|---|---|---|
| `gravity` (trial_summary) | A, B, C, F | It is unknown at which gravity the policy was measured. Learning and increasing difficulty cannot be separated |
| `phase_label` | A, C, D, F | It is unknown which trial belongs to which phase. The eight phases cannot be separated |
| `stick_raw` | A, B, E, G | Small movements are lost. G dies completely, A weakens |
| `log_schema_version` | all | A format change during collection goes unnoticed |
| `occlusion_responses.csv` | D, E | The prediction measure cannot be done at all |
| `frame_time_s`, `render_frame_count` | A, E | The delay estimate is biased and by how much is unknown |
| `gravity_step_index` | A, B, C | The step unit is rebuilt by hand, with room for error |
| `trial_index_in_step` | C | The early/late split is built by hand; C's main computation rests on it |
| `gravity_current` (timeseries) | validation | A wrongly written trial-level gravity cannot be caught |
| `session_time_s` | C, D | Balancing and occlusion cannot be put on one timeline. The time between phases 6 and 7 is unknown |
| `probe_config` | D | It has to be assumed that options are evenly spaced |
| `input_pipeline` | A, G | The transformation between `stick_raw` and the applied value cannot be reproduced |
| `occlusion_stimuli.csv` | D | The observation phase cannot be modelled. With few trials this extra information is valuable |

---

## Order

1. Simulation-based power analysis. It does not wait for data, can be done
   this week, and decides the fate of D and E.
2. A, because B, E and G build on it.
3. F and C, independent of each other, can be done as soon as data arrives.
4. D, when the occlusion files arrive. Does not depend on A.
5. B, after A is done.
6. G, when A's residuals are ready.
7. E last, and only if it passes the reliability gate.

---

## Computational cost

No GPU needed.

Per person 115 balancing trials, 20 seconds, 60 Hz, i.e. 138,000 rows. The
number of participants is not decided yet; in a 40-person scenario that is
5.5 million rows in total, under half a gigabyte as float32 parquet.
Processing person by person, RAM is not an issue.

Ridge fits take milliseconds. The delay sweep a few minutes. LightGBM a few
seconds per person. The transfer matrix minutes. Occlusion fits are small
data, seconds.

The real cost is the bootstrap. Confidence intervals come from block-level
bootstrap, and 500 to 1000 repetitions multiply everything by that much. The
fix is to apply the bootstrap only to final quantities and parallelize across
cores. Worst case is an overnight job.

---

## Left out of this plan

- A deep network predicting the condition label.
- Unsupervised clustering of participants into strategy groups.
- A sequence model predicting performance from time.
- A model decoding gravity from the state. This is no longer a separate
  analysis but a control inside A. The reason is written under A above.

---

## References

- Ludolph N, Giese MA, Ilg W (2017). Interacting Learning Processes during Skill
  Acquisition. *Scientific Reports* 7:13191. ([[Ludolph_2017_SciRep]])
- Ludolph N, Plöger J, Giese MA, Ilg W (2017). Motor expertise facilitates the
  accuracy of state extrapolation in perception. *PLOS ONE* 12(11):e0187666.
  ([[Ludolph_2017_PLOSONE]])
- Wu HG, Miyamoto YR, Gonzalez Castro LN, Ölveczky BP, Smith MA (2014). Temporal
  structure of motor variability is dynamically regulated and predicts motor
  learning ability. *Nature Neuroscience* 17:312-321.
