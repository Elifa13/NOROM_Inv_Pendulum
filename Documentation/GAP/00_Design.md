# GAP: Experiment design

**GAP = Gravity Adaptation and Prediction.**
rev 2, 2026-09-09. Source: the handwritten flow note of 2026-09-08 and later
clarifications.

The design belongs to the experiment team; I cannot change it. This
document's job is to record the design completely, separate what comes from
Ludolph from what does not, and clearly mark what is not decided yet.
Recording requests in [01_Recording_Requests.md](01_Recording_Requests.md),
analysis plan in [02_Modelling_Plan.md](02_Modelling_Plan.md).

## Question

When a person adapts to a system that gets gradually harder, does their
internal model change, and does that change show up both in motor behaviour
and in a perceptual test?

The measurement comes from two independent places. On the motor side, the
person's control policy and its timing; on the perceptual side, prediction
accuracy in the occlusion test. Both try to measure the same latent variable:
the gravity the person assumes.

## Groups

| Group | Gravity | n |
|---|---|---|
| Gradual gravity (GG) | gradually from 1.0 to 3.5, then back to 1.0 | not decided |
| Constant gravity (CG), control | **1.0 for the whole session** | not decided |

The control group never sees 3.5. Trial counts and session length match the
gradual group; the only difference is that gravity stays constant. So CG is a
time and practice control: same duration, same number of trials, no change
in dynamics.

**This is not Ludolph's control group.** In Ludolph the constant arm was at
3.5 and both groups ended at the same difficulty; his question was "is
gradual training better than sudden training". Here the control group stays
at 1.0. The consequences are below, under "What this design can and cannot ask".

## Flow

| # | Phase | Trials | GG | CG |
|---|---|---|---|---|
| 1 | Familiarization | 3 x 20 s | 1.0 | 1.0 |
| 2 | Motor baseline | 8 x 20 s | 1.0 | 1.0 |
| 3 | Prediction pre-test | 40 trials | stimuli at 1.0 | same |
| 4 | Stepped gradual adaptation | 10 steps x 8 trials x 20 s | 1.0 → 3.5, +0.25 per step | same number of trials at 1.0 |
| 5 | Late adaptation | 8 x 20 s | extra practice at 3.5 | 8 trials at 1.0 |
| 6 | Prediction post-test | 40 trials | stimuli at 1.0 | same |
| 7 | Re-adaptation | 8 x 20 s | reminder at 3.5 | 8 trials at 1.0 |
| 8 | Washout | 8 x 20 s | 1.0, aftereffect | 8 trials at 1.0 |

115 balancing trials and 80 occlusion trials in total. Trial counts are
identical in both groups; the only difference is gravity.

### 2. Motor baseline

Six of the eight trials, i.e. 6 x 20 = 120 seconds, are set aside as the
analysis window for action timing. This is an analysis decision, not a
recording setting: Ludolph's action timing measure pools events in a
two-minute window ([Setup/05_Action_Timing.md](../Setup/05_Action_Timing.md)).

There are enough events. The pilot was collected at g = 1.0 and produced
91,165 state events across 12 participants, roughly seven and a half events
per second per person. A 120-second window gives this measure enough material.

This phase is the comparison point for the aftereffect. Phase 8 is read
against it; both are at g = 1.0 and in the same person.

### 3 and 6. Prediction test

Identical to Ludolph's PLOS ONE procedure. A single trial works like this:

1. 4.5 seconds of observation. A sequence cut from someone else's balancing
   recording is played, and the applied force is shown with a red arrow.
2. The force is set to zero and the system is simulated for another second.
   The pole stays visible for the first 100 ms.
3. For the remaining 900 ms the pole is hidden and the cart visible. Since
   the force is zero, the outcome depends only on the state at occlusion and
   on gravity.
4. Response: one of 13 options evenly spaced over [-65, +65] degrees.

40 trials per block, two blocks per person (pre and post), 80 trials in
total. The participant does not play; stimuli are shared by everyone, one file.

**Stimuli are cut from the pilot's no-noise trials, all at g = 1.0.**
Decided. **The correct answer is not shown**, no feedback. In Ludolph, the
group difference disappears completely in the blocks where the correct answer
is shown, so this is required.

### 4. Stepped gradual adaptation

For GG, g starts at 1.0 and rises to 3.5 in steps of 0.25. Ten levels, 8
trials per level, 80 trials in total.

**The increase does not depend on success.** Whether or not the person
succeeds, g goes up one level after 8 trials. This is the most important
difference from Ludolph; consequences below.

Within-step split: trials 1-3 early, trials 6-8 late. This corresponds to
Ludolph's P1,g and P2,g definition, which compares the first and last third
of each gravity step.

CG does the same 80 trials at g = 1.0. It has no steps, but the
`gravity_step_index` column is still written so trials can be matched.

### 5, 7 and 8. Late adaptation, re-adaptation, washout

Phase 7 exists because of phase 6. The prediction post-test takes about five
minutes, during which the person does no balancing and adaptation partly
decays. Re-adaptation gives a reminder at 3.5 and starts the washout from a
proper starting point. The design saw this problem and solved it.

The aftereffect is largest in the **first trials** of phase 8 and decays in
the following ones. So phase 8 is not a single number but a decay curve. A
block mean erases the aftereffect because the first and last trials are
opposites. This block will be analysed at trial level.

Eight trials are enough for this. To see the decay curve, the decay has to
complete; three or four trials show that an aftereffect exists but not its
rate. Eight trials also equal the step length in phase 4, so they can be
compared directly with within-step recovery curves. The same split applies:
trials 1-3 early, 6-8 late.

For CG, phases 7 and 8 have no separate meaning; that group never left 1.0.
Its trials there serve as time and practice control, and their number must
match GG. If they do not match, the size of the aftereffect cannot be interpreted.

## What this design can and cannot ask

**It cannot ask Ludolph's gradual-versus-sudden question.** The two groups
never balance at the same gravity except at the start. At the end of the
session one is at 3.5, the other at 1.0. A performance difference at that
point is a difficulty difference, not a learning difference. The sentence
"the gradual group learned better" cannot be supported by this design. That
would require the control group to be at 3.5.

**It can ask the aftereffect question.** After adapting to 3.5, does the
person start mispredicting the physics of 1.0, and does this show up both in
motor behaviour and in the perceptual test? This is exactly what Ludolph
left as an open question in his Conclusions.

This is where the comparison is built. The difference between GG's phase 8
and phase 2 contains two things: the aftereffect, plus general improvement
from practising throughout the session. CG gives the same two points without
any adaptation, i.e. a measure of that general improvement. Subtracting CG's
difference from GG's leaves the pure aftereffect. That is the control group's
real job.

The same logic applies on the perceptual side: is prediction post-test minus
pre-test different in GG than in CG?

**Stimuli at g = 1.0 work in our favour here.** The test world is the
control group's world. GG is the side that moves away from it, so any effect
found is found despite a home advantage for the other group. The confound
works against the hypothesis, which is the desired direction.

## From Ludolph and not from Ludolph

| Item | Status |
|---|---|
| Physics parameters, ±60° angle and ±5 m track limits, ±4 N force | Taken as-is |
| The whole occlusion test: 4.5 s, 100 ms, 900 ms, 13 options, [-65, +65], no feedback | Taken as-is |
| g range 1.0 → 3.5 | Taken as-is |
| Control group gravity | **Changed.** Ludolph: 3.5 (second arm ending at the same difficulty); ours: 1.0 (time and practice control) |
| g increase rule | **Changed.** Ludolph: +0.1 after every successful trial, success = 30 s balanced without falling, 25 increases. Ours: fixed schedule, +0.25 every 8 trials, 10 increases |
| Trial duration | **Changed.** Ludolph: 30 s maximum and the trial ends at a fall. Ours: fixed 20 s, reset and continue after a fall |
| Session structure | **Changed.** Ludolph: time limit (90 min), free number of trials. Ours: fixed number of trials |
| Number of occlusion blocks | **Changed.** Ludolph: 11 blocks x 40 = 440 trials. Ours: 2 blocks x 40 = 80 trials |
| Gravity of the occlusion stimuli | Ludolph: 3.5, the same as where training ended. Ours: 1.0, which is different for GG. This difference turns the design into an aftereffect experiment |
| Phases 5, 7 and 8 (late adaptation, re-adaptation, washout) | **Not in Ludolph.** The paper's Conclusions list them as open questions: is there an after-effect in timing when g is lowered again, is there a retention difference between gradual and sudden |

## Effect of the fixed schedule on the analysis

In Ludolph, g rises after a successful trial, so it cannot be separated how
much of the post-step performance drop comes from gravity and how much from
regression to the mean. The trial before a step is by definition a good
trial, and a natural regression is expected after it. Ludolph did not
address this.

In our design g rises independently of success, so this confound does not
exist. Consequences:

- The post-step degradation can be interpreted directly, no correction needed.
- The `trial_success` column was removed from the recording requests entirely.
  With no flag triggering the increase it is unnecessary, and in a fixed 20 s
  trial "successful" is ill-defined anyway. The performance measure is
  derived from `fall_event`.

A second effect: since every participant does the same 8 trials at the same
10 levels, the design is balanced and within-subject. Same shape as the
pilot's participant × condition structure, with gravity step in place of
condition. Most of the existing analysis code can be reused along this axis.

## Duration

| Phase | Duration |
|---|---|
| 1. Familiarization | 1 min |
| 2. Motor baseline | 3 min |
| 3. Prediction pre-test | ~5 min |
| 4. Adaptation | ~27 min |
| 5. Late adaptation | 3 min |
| 6. Prediction post-test | ~5 min |
| 7. Re-adaptation | 3 min |
| 8. Washout | 3 min |
| **Total** | **~49 min** |

This is pure balancing and test time. Adding the 1-second reset per trial
gives about 2 more minutes for 115 trials. With instructions, breaks and
transitions, the session realistically takes an hour.

## The one thing not decided

Number of participants per group. I will derive it from a simulation-based
power analysis; it does not go to the team as a question. The computation
will say whether the 80 occlusion trials are enough for person-level
parameter estimation and will give the minimum group size required.

## References

- Ludolph N, Giese MA, Ilg W (2017). Interacting Learning Processes during
  Skill Acquisition. *Scientific Reports* 7:13191. ([[Ludolph_2017_SciRep]])
- Ludolph N, Plöger J, Giese MA, Ilg W (2017). Motor expertise facilitates the
  accuracy of state extrapolation in perception. *PLOS ONE* 12(11):e0187666.
  ([[Ludolph_2017_PLOSONE]])
