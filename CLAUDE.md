# CLAUDE.md

This file is a router, not a knowledge store. It only holds what spans all
studies: the setup, the data format, the repo map and the working rules. A
number or finding that belongs to one study lives in that study's folder, not
here. The rule is below, under "Where things go".

## Project

Motor learning and internal models in a cart-pole (inverted pendulum)
balancing task. The setup is identical to Ludolph 2017: no virtual reality, a
screen and an analog stick.

**Active study: GAP (Gravity Adaptation and Prediction).** How a person's
control policy changes while gravity is stepped from 1.0 to 3.5 m/s², and
whether that change shows up in an occlusion-based perceptual test. Two
groups: gradual gravity and constant gravity (control). Eight-phase session.
Full design in `Documentation/GAP/00_Design.md`.

**Closed study: visual noise / stochastic resonance.** Two pilots, 22
participants, nine noise levels. No inverted U, hypothesis not supported,
study closed. Summary and carried-over decisions in `Documentation/Pilot_Noise/`.

## My role

I analyse the data. I do not run the experiment and cannot change the design.
On the recording side I can only ask "please also record this field". So a
"let's also measure X" proposal is only feasible if X can be derived from
existing or requested columns.

## Repo map

| Location | Contents |
|---|---|
| `Documentation/Setup/` | Method records for the setup, valid in every study: data processing and QC, physics model and T₀, state/action/episode definitions, performance metrics, action timing, reliability |
| `Documentation/GAP/` | Active study: design, recording requests, modelling plan |
| `Documentation/Pilot_Noise/` | Closed study: both pilot summaries, decision statistics, recording requests of that period, old Office documents under `archive/` |
| `Documentation/Analysis_Log.md` | Dated analysis log, newest entry on top. What was decided when |
| `Data Analysis/ABOUT.md` | Entry point for the analysis side: folder layout, what each `src/` module does, data layers |
| `Data Analysis/src/` | Analysis logic. Notebooks stay thin, the logic lives here |
| `Data Analysis/Notebooks/pilot_noise/` | The closed study's two chains, frozen |
| `Data Analysis/data/` | Raw and derived data. Not in git, source is Google Drive |
| `Literature/` | Papers, notes on the basis papers and the reading list. Index: `Literature/README.md` |
| `Unity/` | The project that runs the experiment. Only `ABOUT.md` for now; the project itself is with the experiment team |

## Setup

Physics parameters are the same as Ludolph 2017. The physics never changes;
the only things that differ between studies are gravity and session structure.

| Parameter | Value |
|---|---|
| Cart mass | 0.40 kg |
| Pole mass | 0.08 kg |
| Pole length | 1.00 m (the dynamics use the half-length, 0.5 m) |
| Force limit | ±4 N |
| Track limit | ±5 m |
| Angle limit (fall) | ±60° |
| Initial angle | U(−7.5°, +7.5°) |
| Integration | RK4, Δt = 1/60 s |
| Sampling | FixedUpdate, 60 Hz |
| Gravity | depends on the study |

The model was validated against the data: correlation with observed angular
acceleration 0.989–0.997. Derivation, validation and T₀ in
`Documentation/Setup/02_Physics_and_T0.md`.

## Data

Source is Google Drive; the folder is public to anyone with the link, no
authentication. `src/drive_sync.py` pulls with `gdown`, does not re-download
existing files, and does not delete local files missing remotely. Data is
never committed.

Folder structure is `<participant_id>/<session_id>/` with three files:
`metadata.json` (once per session), `timeseries.csv` (one row per
FixedUpdate), `trial_summary.csv` (one row at the end of each trial). Column
lists are in each study's recording requests document.

Data layers:

```
Raw Sample → Clean Sample (passed QC, masked)
  → Input event (onset / offset / reversal)  |  State event (angle crossing)
  → Regime run (Safe / Saved / Failed / TrackLoss)
  → Episode (reset to reset)
  → Trial
  → Analysis unit (per study: participant × condition, participant × gravity step)
```

Episode and regime run are not the same thing. The first serves Ludolph's
duration analysis, the second Park's regime classification. Details in
`Documentation/Setup/03_State_Action_Episode.md`.

### Datasets

Datasets are never merged at any stage; the separation is at folder level.
Participant ids run P001… in every set, but they are different people.

| Set | Study | Status |
|---|---|---|
| `pilot1` | noise | 12 participants, August 2026, closed |
| `pilot2` | noise | 10 participants, September 2026, closed |
| `gap` | GAP | no data yet |

The active set is the `DATASET` variable in a notebook's first cell.
`src/dataset.load_config` resolves the paths; `dataset.dirs` leaves a
`.dataset` stamp in interim and raises an error if the wrong set tries to
write to the wrong folder.

### Known recording behaviours

Reported to the team, and they affect the analysis: on reset rows
`applied_force_n` is forced to zero but `input_applied` keeps its last value
(creates fake zero crossings); velocities are not reset on reset; the
`valid_trial` column cannot be trusted; the seed was fixed in pilot1 and fixed
before pilot2. Details in `Unity/ABOUT.md` and
`Documentation/Pilot_Noise/Recording_Requests.md`.

## Where things go

This is why the repo broke before, so the rule is explicit:

- If a computation is done the same way in every study, its record goes under
  `Documentation/Setup/`. Each record has: definition, code reference, which
  options existed and why this one was chosen, evidence, and what it feeds.
- A number, finding or decision that belongs to one study goes in that study's
  folder, not here.
- When a new analysis decision is made, add an entry to
  `Documentation/Analysis_Log.md` and update the relevant method record.
- Anything not taken as-is from the literature is marked: why it could not be
  taken as-is, and what replaced it.
- New papers go into `Literature/README.md`; basis papers get a note from
  `Literature/_template.md`.

## Working rules

- Ask before writing code. Say what you will write, get approval, then write.
- Check the repo and project files before anything else. Do not search the web
  without asking Elif first.
- Never state a fact about a paper, dataset or library that has not been read
  in the current session.
- At every completed milestone and at the start of every new project, ask Elif
  whether any md files need updating, and agree together what to keep.
- Do not chase things outside the goal. If a data quality detail does not
  change the decision at hand, leave it. If you think it matters, say how much
  first.
- Do not give flat lists where everything looks equally urgent; order by impact.
- Thresholds live in `config.yaml`, not in code.
- Logic becomes a module under `src/`; notebooks stay thin.
- Keep it short. Plain discussion, not report or slide format.
- **All md files in this repo are written in English.**
