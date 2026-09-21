# Data Analysis

The analysis chain for the pilot data. Logic becomes a module under `src/`;
notebooks stay thin. Thresholds live in `config.yaml`, not in code.

## Structure

```
config.yaml       all thresholds and parameters + datasets block
src/              analysis logic (dataset-independent)
Notebooks/pilot_noise/pilot1/  pilot1 chain (closed study, frozen)
Notebooks/pilot_noise/pilot2/  pilot2 chain, the only difference is DATASET in the first cell
data/
  pilot1/         12 participants, noise σ 0 .02 .05 .08 .25
  pilot2/         10 participants, noise σ 0 .005 .010 .015 .020
    raw/          raw data downloaded from Drive (not in git)
    interim/      intermediate outputs, parquet (not in git)
    processed/    figures and report outputs
```

**The two datasets never mix.** Participant ids run P001… in both sets but
they are different people; the condition labels are the same too but the
sigmas differ. The separation is at folder level: the active set is the
`DATASET` variable in a notebook's first cell, and `src/dataset.load_config`
resolves the paths. `dataset.dirs` leaves a `.dataset` stamp in interim and
raises an error if the wrong set tries to write to the wrong folder.

## Modules

| File | Job |
|---|---|
| `dataset.py` | Dataset selection, path resolution, mix-up protection |
| `drive_sync.py` | Pulling data from Drive; copy semantics, skips existing files. The path must be exactly three parts; nested folders (another dataset) are not downloaded, skipped entries are reported |
| `loader.py` | Finding sessions, reading the three files, producing two tables |
| `qc.py` | Structural integrity, timing, signals, trial flags, analysis mask, randomization |
| `physics.py` | Cart-pole model, its validation, T₀ |
| `build.py` | Episode and regime run segmentation, state, action classes, input event detection (`input_events`) |
| `performance.py` | Trial and participant × condition level metrics, choice of metric set |
| `timing.py` | Ludolph action timing: state events (`state_events`), segment extraction, velocity stratification, zero crossing |
| `decide.py` | NB06 decision statistics: Friedman, Wilcoxon/Holm, trend contrasts, sensitivity |
| `reliability.py` | Variance decomposition, ICC, split-half reliability. Reads no data, writes no files. Record: `Documentation/Setup/06_Reliability.md` |
| `presentation.py` | **Isolated.** For the presentation notebook; the rest of the chain does not import it |

## Data layers

```
Raw Sample (one FixedUpdate row)
  → Clean Sample (passed QC, masked)
  → Input event (onset / offset / reversal)  |  State event (angle crossing)
  → Regime run (Safe / Saved / Failed / TrackLoss)
  → Episode (reset to reset)
  → Trial
  → Participant × Condition   ← analysis unit
```

Episode and regime run are **not the same thing**: the first serves
Ludolph's duration analysis, the second Park's regime classification.
Details: `../Documentation/Setup/03_State_Action_Episode.md`.

## Method records

The definition, rationale and evidence for every computation are under
`../Documentation/Setup/`. Looking there before reading code is usually faster.
