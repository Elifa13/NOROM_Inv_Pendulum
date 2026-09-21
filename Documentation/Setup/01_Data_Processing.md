# 01: Data processing, QC and analysis mask

**Notebook:** `Data Analysis/Notebooks/pilot_noise/<dataset>/01_load_qc.ipynb`
**Code:** `src/drive_sync.py`, `src/loader.py`, `src/qc.py`
**Output:** `data/<dataset>/interim/samples_clean.parquet`, `.../trials_clean.parquet`
**Last run:** pilot1 2026-08-27 (12 participants); pilot2 2026-09-14 (10 participants)

---

## 1. Source and download

Google Drive folder `Pendulum_Data`, id `1iDMZt3iUN-mHaemXXI_qNA9GkYUMf5t6`.
The folder is shared as "anyone with the link", so there is no
authentication: no API key, OAuth, `client_secrets.json` or `rclone config`.

`sync_data(folder_id, RAW_DIR)` lists the folder with `gdown` and downloads
only the three expected file types. **Copy semantics, not sync:** an existing
file is not downloaded again, and nothing that exists locally but not on
Drive is deleted. Data is not committed; anyone running the code can download
the same data to their own disk, so there is no point keeping it in git.

Folder structure is `<root>/<participant_id>/<session_id>/` with three files:
`<pid>_<sid>_metadata.json`, `_timeseries.csv`, `_trial_summary.csv`. Local
target is `Data Analysis/data/<dataset>/raw/` (for the active set see
CLAUDE.md, "Datasets").

**The path must be exactly three parts** (added 2026-09-04). gdown returns
paths relative to the requested folder; a deeper path means **another
dataset** placed inside. Previously the last three parts were taken, and
pilot2's `DataV2/` subfolder landed in pilot1's folder when pilot1 was
pulled. Because participant ids collide, the mix was silent. Now any entry
not matching `P\d+/S\d{8}_\d{6}/<pid>_<sid>_*` is not downloaded, and the
skipped entries are printed with a count. When pulling pilot1, a warning that
28 entries were skipped is expected behaviour.

**Status:** pilot1 12 participants × 3 files = 36 files (26–27 August 2026);
pilot2 10 participants × 3 files = 30 files (2–3 September 2026, P010 on
8 September).

## 2. Loading

`loader.load_all` finds sessions, reads the three files and produces two
tables: sample level (timeseries) and trial level (trial_summary), with
metadata in a separate dict.

**Decision: if there is more than one session folder.** The session with the
most measurement trials is taken; the others appear as "partial" in the
report. They are not merged: when the app restarts it begins again at trial 1
with the same `condition_order`, so trials repeat, and concatenating two
sessions would count the same condition twice.

## 3. QC checks

Six groups in `src/qc.py`. None of them change the data; all produce reports.

### 3.1 Structural integrity (`check_structural_integrity`)

File presence, trial counts (3 practice + 50 measurement expected), condition
balance (5 conditions × 1 per round), required metadata fields.

Persistent WARNs from this check (pilot1):

- `shared_condition_order`: all participants get the same 50-trial condition sequence
- `shared_randomization_seed`: `12345` in all metadata
- `config_participant_id`: `config.participantId` is never updated and reads
  "P001" in every metadata file. The `participant_id` field is correct; only
  the copy in the `config` block is wrong.

The first two were fixed before pilot2; the third still occurs. For details
and impact see [the randomization section](#4-randomization-check).

### 3.2 Timing and sampling (`check_timing`)

`dt` agrees with `fixed_delta_time_s` (tolerance `qc.dt_tolerance` = 0.001),
no time going backwards, no gaps, no `sample_index` skips, no duplicates, no
NaN, angle within −180°..+180°.

### 3.3 Signal sanity (`check_signals`)

- Do velocities match the derivative of position (warning threshold `qc.velocity_correlation_warn` = 0.99)
- Is `applied_force_n` = `input_applied` × `max_force_n`
- Is `fall_event` marked only on the first step of a fall
- Are `phase` and `is_resetting` consistent

**Decision: the derivative check runs on continuous segments.** When a fall
happens within a trial, a 1-second reset block follows and the pole continues
from a new initial angle. Concatenating `phase == "active"` rows produces
fake jumps at reset boundaries and lowers the correlation. `_active_segments`
separates continuous active segments, and the correlation is computed per
segment.

### 3.4 Trial validity (`flag_trials`)

**Unity's `valid_trial` column is not trusted**; we produce our own `qc_pass`
/ `qc_flags` flag.

The only rule currently applied is **dead input**: if
`max(|input_raw|) == 0` over a trial, it gets the `dead_input` flag.
Threshold `qc.dead_input_threshold` = 0.0.

`qc.min_fps` and `qc.low_activity_threshold` are `null` in config. If a value
is null the code skips that rule. This was left deliberately so no threshold
is invented before real data exists.

**Decision: a trial that fails QC is removed on its own; the session is not
dropped.** The report warns above a threshold.

**Result on pilot1:** none of the 636 trials were flagged, `qc_pass`
636/636. No dead-input trials remain (there were 5 in the P001/P002 period;
that data was deleted). Pilot2: 530/530 pass.

### 3.5 Sample mask (`add_analysis_mask`)

```
analysis_include = (phase == "active") & (practice == 0) & qc_pass & (window_focused == 1)
```

An `is_resetting == 0` condition is redundant; it gives exactly the same
result as `phase == "active"`.

**On pilot1:** 720,000 samples = 600 measurement trials × exactly 1200
samples. No focus loss, no QC drops. This means **the denominator is
constant** in rate computations: a participant who falls a lot does not look
artificially good thanks to resets, because reset frames are already outside
the mask. Pilot2: 600,000 samples = 500 × 1200.

### 3.6 Format regression tracking (`check_format_regression`)

Checks whether the fields requested in `Pilot_Noise/Recording_Requests.md` have
arrived. The list is under `config.metadata_requested_fields`.

**Status:** all 24 requested fields are still missing.

## 4. Randomization check

`check_randomization` compares the metadata's `condition_order` claim with
trial_summary and measures, **from the data**, how identical participants are.

Results and their effect on the pilot decision: `Pilot_Noise/Recording_Requests.md`
and `Pilot_Noise/Pilot1_Results_Summary.md`. Summary for pilot1: condition order
and the `noise_seed` sequence are identical in all 12 participants; initial
angles are read from a single fixed RNG stream. In pilot2 all three differ
between participants.

`check_angle_stream` aligns this stream across participant pairs and assigns
each participant an entry point in the shared list. **This function is not
called in NB01**; it lives in `src/qc.py` and is run by hand when the stream
table is needed. Thresholds are under `qc.angle_stream_*`.

Known limitation: it cannot match adjacent but non-overlapping slices. That
is why P008–P012 fall into separate groups; it does not mean "different seed".

## 5. Known gaps

In order of importance.

1. **Trials with `valid_trial == 0` enter the mask.** P011's T030 and T034
   (pilot1) are marked `invalid_reason = "paused"`, but our `flag_trials`
   does not look at this column, so both are `qc_pass`. Inspected: both have
   1200 full active samples, no focus loss, normal behaviour (maPA 10.1° and
   6.0°, one fall each). 2 of 600 trials, low impact. A rule should still be
   added: at least a flag when `invalid_reason` is set.
2. **No fps threshold.** 54 trials have `min_fps < 55`, 47 have `< 45`, the
   lowest is 29.1 (pilot1). `mean_fps` is ~60 in every trial. Momentary drops
   do not cause sample loss (every trial has the full 1200 samples) because
   sampling is in FixedUpdate, independent of rendering. Still, in an
   experiment about perceiving visual noise, render rate directly affects the
   independent variable. Whether to set a threshold has not been decided.
3. **No sample-level frame timing.** Low priority.
