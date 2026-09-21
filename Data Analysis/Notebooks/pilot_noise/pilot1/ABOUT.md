# Notebooks / pilot1

The chain runs in order; each notebook reads the previous one's parquet
output. Notebooks are thin; the logic is under `../../../src/`.

**There are two copies.** The notebooks in this folder process the `pilot1`
data (12 participants); those under `../pilot2/` process `pilot2` (10
participants). The only difference is the `DATASET` variable in the first
cell; `src/` was not duplicated. The status column below is for pilot1.
Results (from repo root): pilot1 in `Documentation/Pilot_Noise/Pilot1_Results_Summary.md`,
pilot2 in `Documentation/Pilot_Noise/Pilot2_Results_Summary.md`.

| # | Notebook | Contents | Status |
|---|---|---|---|
| 01 | `01_load_qc.ipynb` | Pull from Drive, loading, structural integrity, timing/signal checks, QC flags, analysis mask, randomization check | ran, 12 participants |
| 02 | `02_build.ipynb` | Physics model validation, episode + regime run segmentation, state, action classes, T₀, event detection | ran, 12 participants |
| 03 | `03_performance.ipynb` | Trial-level metrics, choice of metric set, aggregation to the participant × condition unit | ran, 12 participants |
| 04 | `04_control.ipynb` | Action timing (Ludolph), velocity stratification, action variability, angle band sweep. The I/CR/D/A distribution was left out of scope | ran, 12 participants |
| 05 | Learning | Variance/power estimate for the pilot; NOT a comparison of learning across conditions | **not written** |
| 06 | `06_noise_decision.ipynb` | Friedman + Wilcoxon/Holm, linear and quadratic trend contrasts, U-shape check, sensitivity, candidate choice | ran, 12 participants |
| 90 | `90_sunum.ipynb` | Emergency presentation. **Isolated**: uses `presentation.py`, not part of the chain; deleting it would not affect the chain | ran, 12 participants |
| 91 | `91_control_variability.ipynb` | Control variability: Welch spectrum, sample entropy, action intervals. **Isolated**: self-contained, no `src/` module, not part of the chain | ran, no condition effect |
| 92 | `92_varyans_ayrisimi.ipynb` | Variance decomposition (person/condition/residual), ICC, split-half reliability, learning check. **Isolated**: self-contained, no `src/` module, not part of the chain | ran, 12 participants |
| 93 | `93_ogrenme_ve_varyans.ipynb` | Trial-level variance decomposition (person/condition/learning/residual), learning slope per condition and the slope's reliability. **Isolated** | ran, 12 participants |

## Chain logic

02 exists so that 03 and 04 don't do the same derivation twice. 04 comes
before 05 because the learning criterion uses action timing as input. (This
rationale is partly void after NB04: action timing did not separate
conditions and did not enter the decision set.)

The 90s series is isolated. No part of the chain reads them, and they only
read `data/interim`. 91 and 92 sit outside the repo rule (logic under
`src/`, notebooks thin): both are exploratory scans; if a result enters a
decision, the logic moves to `src/` and gets a record under
`Documentation/Setup/`. NB92's reliability functions moved to
`src/reliability.py` this way on 2026-09-15 (record:
`Setup/06_Reliability.md`). The NB92 here keeps using its own copy; it is frozen.

Pulling data from Drive is in NB01's first cell (`sync_data`); when a new
participant arrives, running that cell is enough, and existing files are not
downloaded again. Which Drive folder is pulled comes from the active `DATASET`.

## Running

The notebooks use the `.venv` kernel at the repo root. Packages are
installed with `%pip install` in each notebook's first cell, because
terminal pip can install into a different Python.

## Method records

Why a notebook computes things the way it does is under
`Documentation/Setup/` (from repo root). NB03's metric set decisions and
NB04's action timing transfer decisions are there.
