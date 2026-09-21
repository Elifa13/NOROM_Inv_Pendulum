# Analysis log

What was done when, what was decided. New entries go **on top**.

Purpose: months later, when someone asks "why is this number like this", the
answer and that day's rationale can be found. Method details are under
[Setup/](Setup/); this file only holds the chronology and decisions.

---

## 2026-09-21: Turkish file and folder names renamed to English

Renamed Turkish file/folder names to English, PDFs renamed to match their
notes, `Claude outputs/` removed. `Documentation/Duzenek/` became
`Documentation/Setup/`, `GAP/sekiller/` became `GAP/figures/`,
`Pilot_Noise/arsiv/` became `Pilot_Noise/archive/`. The twelve Turkish-named
md files under those folders, plus `Documentation/Analiz_Gunlugu.md` and
`Literature/_sablon.md`, took English names. Every reference in every md
file was updated, and `src/timing.py` was pointed at
`Documentation/Setup/05_Action_Timing.md`. Content did not change.

The six basis-paper PDFs in `Literature/` were renamed to match their notes
(`Ludolph_2017_SciRep.pdf`, `Ludolph_2017_PLOSONE.pdf`,
`Brookes_2020_PLOSONE.pdf`, `Cesonis_2019_EMBC.pdf`,
`Park_2025_ExpBrainRes.pdf`, `Trevino_2016_FrontHumNeurosci.pdf`) and the
`pdf:` line in each note follows. `.docx`/`.pptx` files, the frozen notebooks
and the `karar/` data folders kept their names.

---

## 2026-09-21: All md files translated to English

All md files in the repo were translated from Turkish to English, and
CLAUDE.md now states that all md files are written in English. The
"write in Turkish" line in the old CLAUDE.md was not Elif's rule. Content
was not changed; file names were kept so no links break. A few stale
cross-references found during translation were pointed to where the
content lives now (e.g. the old "CLAUDE.md → problems seen in the data §1"
now points to `Pilot_Noise/Recording_Requests.md`).

The noise stimulus definition verified from the Unity source on 2026-09-14
(uniform, not Gaussian; "σ" is a half-width; fixed 60 Hz refresh; equal mean
luminance) had only been kept in Claude's memory. It was moved into
`Unity/ABOUT.md`, which also corrects the old "refreshed every display frame".

---

## 2026-09-21: Documentation links updated after the reorganization

When the folders were split into `Setup/`, `GAP/` and `Pilot_Noise/`, the
links were not updated. Paths and stale sentences were fixed in 14 files;
content did not change. Old names map to:

| Old | Now |
|---|---|
| `Documentation/Yontem/` | `Documentation/Setup/` |
| `Pilot_Sonuc_Ozeti.md` | `Pilot_Noise/Pilot1_Results_Summary.md` |
| `Veri_Kayit_Istekleri.md` | `Pilot_Noise/Recording_Requests.md` |
| `Duzenek/06_Karar_Istatistigi.md` | `Pilot_Noise/Decision_Statistics.md` |

The `Now` column points at where each file lives today, not at the name it
got that day: the folder created by this split was called `Duzenek/` until
the rename entry above. Older entries in this log use the names of their
day. They are history and were not changed.

Pilot2 numbers were updated too. The documents had been written for 9
participants, but P010 (2026-09-08) entered the chain later and the chain
was rerun with 10 people on 14–15 September. The numbers were taken from
saved notebook outputs; nothing was rerun. Updated: `Pilot2_Results_Summary.md`,
the pilot2 and pilot1 notebook ABOUTs, `Data Analysis/ABOUT.md`, `Setup/01`
and `04`, the `config.yaml` label, CLAUDE.md.

The result did not change: no condition effect, no inverted U. Two
statements changed: the learning Wilcoxon is p = 0.037 with 10 people (0.055
with 9), and in NB91 two cart median-frequency measures give p = 0.027 in the
raw Friedman (0.35 after Holm). The power table was recomputed for n = 10
(9% / 29% / 62% / 80% for dz = 0.2 / 0.5 / 0.8 / 1.0).

A method record was opened for `src/reliability.py`: `Setup/06_Reliability.md`.
The module had been moved out of NB92 on 2026-09-15 but was not mentioned in
any document. While writing the record a naming error was found: the code
and notebooks call the measure ICC(2,1), but the formula is ICC(3,1)
(consistency). The code was not changed. If ICC appears in a report, it must
be named ICC(3,1).

---

## 2026-09-21: Literature notes and reading list

The repo will be opened as an Obsidian vault. `.obsidian/` was added to
`.gitignore`. `Literature/README.md` became the index; `Kaynak_Kaydi.docx`
remains as a historical record.

Full notes were written for the basis papers (`basis`): Ludolph 2017 Sci
Rep, Ludolph 2017 PLOS ONE, Park 2025, Treviño 2016, Česonis 2019 and
Brookes 2020. Brookes 2020 is the teacher's suggestion; its PDF was added on
this date. The notes were written from the PDFs, with page numbers next to
the numbers. Other papers are in the index as `to-read`: 25 from the old
source log and 17 new ones from the 2026-09-21 search. These have not been read.

---

## 2026-09-08: Repo restructured for the GAP study

*This entry was written afterwards, on 2026-09-21. No log entry was made on the day.*

GAP (Gravity Adaptation and Prediction) was the planned main study from the
start. The noise pilots were not the main decision; they were run to try out
the task and the analysis chain and to see what shows up in the data. After
two pilots the noise study was closed (no inverted U, see `Pilot_Noise/`).

On the same day the repo was reorganized on the `gap-yeniden-yapilandirma`
branch: method records moved under `Setup/`, GAP documents under `GAP/`,
noise documents under `Pilot_Noise/`. The notebooks' loop that searches for
the repo root was changed from a fixed depth to walking up until
`config.yaml` is found. The links were not fully updated that day; fixed on 2026-09-21.

---

## 2026-09-04: Second pilot: separate dataset, same chain

A new Drive folder arrived (`1oge-PfEM-ZOmmlpWoqIZF7P1yT3f-J3V`): 9
participants, sessions on 2–3 September, **different people**. Participant
ids again run P001…, so the two sets' files must never meet in the same folder.

**The separation was made at folder level.** A `datasets:` block was added to
`config.yaml`; each set has its own `data/<dataset>/{raw,interim,processed}`
tree; the old one moved under `data/pilot1/`. The active set is chosen with
the `DATASET` variable in a notebook's first cell; `src/dataset.load_config`
resolves the paths and writes them into `config["paths"]`, so the rest of the
notebooks ran without changing a line. `dataset.dirs` leaves a `.dataset`
stamp in the interim folder; if the wrong set tries to write to the wrong
folder it raises an error.

The chain was copied: 01–06 and 91–93 under `Notebooks/pilot2/`, the only
difference being `DATASET = "pilot2"` in the first cell. `src/` was not
duplicated at all; the analysis code already read sigma from the data, and
the condition labels are the same five names.

**A trap turned up: pilot2 sits inside pilot1 on Drive.** The link given
points directly to the `DataV2` folder, but that folder is a subfolder of
`Pendulum_Data`. `drive_sync._list_remote` took the **last three** parts of
the path, so `DataV2/P001/S.../file` and `P001/S.../file` looked the same:
when pilot1 was pulled, pilot2's 27 files also landed in pilot1's folder.
Since participant ids collide, it is hard to spot by eye. It happened once;
the 9 leaked sessions were deleted, `drive_sync` was fixed to require the
path to be **exactly three parts**, and it now prints skipped entries as a
warning. Pilot1 NB01 was rerun after the cleanup: all numbers identical
(session selection had already picked its own sessions; the leaked sessions
had fallen into the "partial" list). When a new dataset arrives, check the
warning line of `sync_data`.

**Three things fixed along the way** (all valid for both sets):

- `qc.check_randomization` now looks at `effective_randomization_seed` first.
  In pilot 2 `config.randomizationSeed` is still 12345 but the RNG is reseeded
  per session; the old check gave a false WARN.
- Sigma in the condition labels was rounded to 2 digits, so pilot 2's
  0.005/0.010/0.015 fell on the same label. The number of digits is now
  chosen to be enough to separate the conditions (pilot 1's labels did not change).
- In NB91 and NB93 the trial count was fixed at 600; it is now derived from
  the data. NB93's comparison line that printed pilot 1 numbers was
  generalized too; NB93 was rerun for pilot 1 and all numbers came out identical.

**Result: no condition effect on this ladder.** Pilot 2's noise levels are
0 / 0.005 / 0.010 / 0.015 / 0.020, all equal to or smaller than pilot 1's
lowest noise condition (N1, σ = 0.02). In all three decision metrics
Friedman is null (p = 0.16–0.73, W ≤ 0.18), linear and quadratic are null,
and no condition separates from baseline.

Read together, the two pilots complete the picture: **nothing happens up to
σ ≈ 0.02, performance degrades monotonically above it, no inverted U
anywhere.** The two sets' only overlap point is σ = 0.02, and there both say
"indistinguishable from baseline": the one comparison confirmed in 21
different people.

The other findings repeat pilot 1: action timing is predictive (−43.5 ms) but
insensitive to condition; none of the control variability measures is
significant; a personal optimum cannot be measured with this trial count
(condition ranking split-half rho ≈ 0); there is learning (−1.98°/50 trials)
and it is independent of condition.

**Good news on the data side:** pilot 1's number one problem (seed fixed at
12345, everyone the same condition order + same noise pattern + same
initial-angle sequence) is gone in pilot 2. Verified from the data: 9
different condition orders in 9 participants, 9 different `noise_seed`
sequences, no shared initial angle in any trial. Not fixed:
`config.participantId` still always "P001", none of the 24 requested
metadata fields arrive yet.

Details: [Pilot2_Results_Summary.md](Pilot_Noise/Pilot2_Results_Summary.md).

*(Later: P010 was added on 2026-09-08 and these numbers were updated to 10
people on 2026-09-21; see the entry above.)*

---

## 2026-09-02: Isolated exploration: control variability and variance decomposition

Two isolated notebooks were written and run: `91_control_variability.ipynb`
and `92_varyans_ayrisimi.ipynb`. Both read only `data/interim`, have no
`src/` module, and no part of the chain imports them. None of their results
enter the decision set.

**NB91: control variability.** Question: does noise change the person's
control behaviour? Frequency analysis (Welch, median frequency) and sample
entropy, on both the angle and the input signal; also duty cycle, amplitude
and inter-action interval. Nine measures, participant × condition unit.

**No condition effect.** Raw, two measures give p < 0.05 (`medfreq_angle` and
`sampen_angle`, both 0.021), but both fail the robustness scan: entropy does
not survive downsampling (significant at 60/30 Hz, not at 15/10 Hz), median
frequency does not survive changing the window length (at `nperseg=128` every
trial gives the same value, at `512` the effect disappears). Since nine
measures were tested, none survive Holm anyway. The quadratic is significant
in no measure.

**The real output is methodological.** Frequency analysis cannot be applied
to this data as it is: the pole's dominant oscillation period is ~4 s, the
median episode 4.3 s. A typical segment contains barely one cycle of
oscillation, which pushes spectral estimation to its resolution limit. Half
of the episodes are already below the 256-sample lower bound. A method that
answers the same question without a spectrum was suggested: Collins & De
Luca 1993 diffusion analysis.

**NB92: variance decomposition.** On the participant × condition table,
total variance was split into person / condition / residual, and ICC and
split-half reliability were computed.

| Measure | person | condition | residual | ICC |
|---|---|---|---|---|
| Mean \|θ\| | 89.4% | 4.0% | 6.6% | 0.91 |
| Stabilization time | 90.7% | 2.1% | 7.2% | 0.91 |
| Angle-caused falls | 96.8% | 0.7% | 2.5% | 0.97 |
| Action timing | 86.3% | 0.5% | 13.2% | 0.83 |

NB04's observation "between-condition spread 15 ms, between-person 269 ms"
was put into numbers for all measures. It also shows why the within-subject
design was necessary.

**A personal optimum cannot be measured.** Each person's 10 trials in a
condition were split randomly 5+5, repeated 200 times. The person's overall
level agrees between halves (r = 0.97–0.99), but the condition ranking does
not (rho = 0.15 / 0.04 / −0.02; same "best" rate 29% / 19% / 35%, chance
20%). By Spearman-Brown, usable reliability (rho ≥ 0.7) needs ~80 trials per
condition; there are 10 now. The pilot's personal bests (6 no_noise, 5 N1,
1 N2) are consistent with what randomness would produce.

**Learning was checked.** There is improvement over the session and it is
larger than the noise effect: mean −0.047 degrees/trial, −2.29 degrees over
50 trials, in 11/12 people (Wilcoxon p = 0.016); the noise effect is +1.41
degrees. Conditions are balanced over trial order, so they do not get mixed
(condition means 24.6–26.5). Removing the trend raises the reliability of the
condition ranking from 0.15 to 0.22, a real improvement but not enough; the
variance decomposition barely moves. Side result: learning is measurable in
50 trials, so what the main experiment wants to measure exists in this task.
Limitation: nobody reached a plateau; the pilot measured performance in the
middle of learning, not immediate performance. P007 is an outlier for the
third time (the only person who got worse, +0.078, p = 0.0005).

### Documentation corrections

NB92 §1 produced a cross-check and three documents were corrected:

1. **[Yontem/06](Pilot_Noise/Decision_Statistics.md) §2: rationale for the
   choice of tests.** It said "at n = 12 the normality assumption cannot be
   tested; parametric tests are risky". It can be tested: `mae_angle_deg`
   Shapiro p = 0.99, `stab_time_s` p = 0.15, and RM-ANOVA gives the same
   result as Friedman. But `falls_angle_per_trial` rejects normality with
   p = 0.0009 (count variable). The choice is defensible; the rationale was corrected.
2. **[Yontem/06](Pilot_Noise/Decision_Statistics.md) §5: multiple comparisons.**
   The reason for not correcting across metrics rested on
   `mae_angle_deg`–`rms_angle_deg` r = 0.98; `rms_angle_deg` is not a decision
   metric, so that basis was invalid. The correct numbers were put in
   (within-person: mae–stab −0.86, mae–falls 0.42) and the correction was
   actually computed: linear after Holm 0.0015 / 0.0049 / 0.0020, all three
   stay significant. The result does not change.
3. **Sensitivity sentence.** "No p value moves" was too strong: the
   `stab_time_s` quadratic moves 0.57 → 0.62. Both are far from significance.

Also corrected: the stabilization threshold sweep is **5°–45°**, not
10°–45° (wrong in three files); N2 and N4 had swapped places in the condition
ranking sentence; the initial |θ| spread is **0.35°**, not 0.32°; the data
layer chain in CLAUDE.md had not been updated for the 31 August `events` →
`input_events` rename and was missing the `state_events` layer; a scope label
was added to the fall count table (1,241 + 140 includes practice, 1,025 + 131
measurement only).

## 2026-08-31: NB06: decision made, SR not supported

> **Correction, 2026-09-02.** Two details in this entry were corrected later:
> the threshold sweep is 5°–45°, not 10°–45°, and "no p value moves" is not
> quite true (`stab_time_s` quadratic 0.57 → 0.62). The decision is
> unaffected. Details in the 2026-09-02 entry above.

`src/decide.py` + `06_noise_decision.ipynb`. Output
`data/processed/karar/decision_stats.csv` and `decision_table.csv`.
Method record: [Yontem/06](Pilot_Noise/Decision_Statistics.md), results
[Pilot_Sonuc_Ozeti.md](Pilot_Noise/Pilot1_Results_Summary.md).

**Result: stochastic resonance is not supported.** The quadratic contrast,
the direct test of the U shape, is null in all three decision metrics
(p = 0.57–0.62). The linear contrast is significant in all three
(p = 0.0005 / 0.0049 / 0.001) and points the same way in 12 of 12
participants for `mae_angle_deg`. There is steady degradation as noise
increases, no peak in the middle.

**N1 cannot be distinguished from baseline** (p ≈ 0.90 in all three metrics,
d<sub>z</sub> ≤ 0.20, 6/12). N2/N3/N4 are significant in `mae_angle_deg`
after Holm (d<sub>z</sub> 0.96–1.18, 11/12).

**A nuance worth recording:** in the group mean, the numerically best
condition is N1 in all three metrics. On the surface it looks like a U, but
the difference is within noise and the quadratic contrast is null.
`decide.interior_optimum` was written to put this check next to the
quadratic test, so as not to rest on a single null test. In the composite
nobody's best is N3/N4 (6 no_noise, 5 N1, 1 N2).

**Both sensitivity checks are clean.** Dropping P011's two `paused` trials,
no p value moves. In the 10°–45° stabilization threshold sweep, linear is
significant at every threshold and quadratic at none.

**The candidate ranking depends on the main experiment's design**, and this
is still an open question: with a control group, N2 (the N1–baseline
difference is too small to detect); if everyone gets the same noise, N1
(noise should not prevent measuring learning). NB06 produced the numbers for both cases.

**Note:** `Pilot_Sonuc_Ozeti.md` now carries the chain's numbers, not the
presentation notebook's. The only difference is in the fall metric: the
presentation counted all falls, the decision set only angle-caused ones.

---

## 2026-08-31: NB04 written: action timing measured, no condition effect

`src/timing.py` + `04_control.ipynb` + `config.yaml` → `timing` block.
Outputs `state_events.parquet` (91,165 events) and `timing_cells.parquet`.
All numbers and tables in [Yontem/05](Setup/05_Action_Timing.md) §5.

**Four findings, in order of importance:**

1. **No evidence that noise disrupts action timing.** Between-condition
   spread 15 ms, within-person between-condition sd 27.6 ms, between-person
   spread 269 ms. With the median the profile flattens, and it flips sign
   across angle bands. The pilot decision (NB06) will continue to be made
   with NB03's performance metrics.
2. **The measure is robust on this data.** Pooled curve −52.6 ms (bootstrap
   95% CI −55.6…−49.5), single crossing, amplitude/standard error 154×. All
   60 of 60 participant × condition cells filled. The 73.9% zero-input worry
   was completely unfounded.
3. **The learning shift is not robust.** Window means show −39 → −93 ms, but
   the shift flattens when P007 and P012 are removed, and the median is flat
   anyway. Both start the session reactive and move toward the group;
   regression to the mean alone explains it. The composition check (mid
   velocity stratum alone) partly preserves the shift; the person check does not.
4. **The measure is undefined for slow crossings: a methodological finding.**
   In the slow stratum the mean curve stays positive throughout, i.e. there
   is no reversal at all; the "zero crossing" is read from noise on a flat
   curve and produces meaningless values like −440 ms. As a result
   `reversal_ok` and `guvenilir` flags were added to `curve_stats`
   (`timing.min_amp_sem_ratio = 10`). This finding is invisible in Ludolph
   because he drops everything outside 20–80%; **the decision to stratify
   instead of exclude (05 §3.3) paid off.**

**Also:** action variability falls with noise (dz −0.77 at N4), but divided
by amplitude the effect disappears (dz −0.27); people do not behave more
consistently, they just apply less force. The zero crossing is unrelated to
the NB03 metrics (r ~ 0.06), so it is a separate construct.

**Not done:** how the I/CR/D/A distribution changes with condition was left
out of scope; the class A decision stays open.

**Scale decision:** same language as NB03: within-person centred profile,
dz, in how many people the direction is the same. No p values. Since action
timing is not in the decision metric set, it does not go to NB06 either; it
will be reported as a mechanism measure.

---

## 2026-08-31: `events` → `input_events` rename

The problem of using the same word for two different concepts was closed. In
NB04 two event tables would sit side by side; the risk of mixing them was real.

| Old | Now |
|---|---|
| `build.detect_events` | `build.detect_input_events` |
| `events.parquet` | `input_events.parquet` |
| config `events:` | config `input_events:` (the old key is read as a fallback) |
| NB02 §6 "Event" | "Input events" |

Ludolph's state-side events will be produced in NB04 as **`state_events`**.

**Meanwhile a wrong sentence was found in NB02 and corrected.** The §6
markdown said "`reversal` = the moment the force changes direction (Ludolph's
action timing uses this)". It does not: Ludolph's measure is the zero
crossing of the mean of force segments centred on state events, not our
`reversal` count. The sentence had been written when NB02 was created,
before the action timing procedure had been read.

NB02 was rerun, outputs identical (35,519 events, identical file size), the
old `events.parquet` deleted. The chain was verified: `detect_input_events`
imports, `performance.load_built` runs, the `fall` count still matches
Unity's `fall_count` exactly.

---

## 2026-08-30 (evening): Sigmoid feasibility check, `05_Action_Timing.md`

The one open item of action timing was closed: **Ludolph's method works on our data.**

**Test.** ±0.5 s input segments centred on fall-direction integer angle
crossings were extracted and averaged (with sub-frame interpolation,
dropping those crossing episode boundaries, pooling negative angles with
sign flipped).

**Result.** At |θ| = 10°, the mean of 4,553 segments is a clean sigmoid:
single zero crossing (−53 ms), amplitude 0.297, standard error of the mean
0.0014–0.0043 (signal/noise ~70×), slope around zero +0.92 units/s. Although
63% of segments consist of exactly-zero samples, the mean is smooth: the
reversal moment shifts a little between segments, so the mean produces a
continuous ramp. **The 74%-zero worry was unfounded.**

Robust at the real granularity too: all 60 of 60 participant × condition
cells filled (median 384 segments), 59 with a single zero crossing, 0 with no
crossing. Rule for multiple crossings: pick the crossing with the steepest
rise; pooling a narrow angle band already solves most of the problem.

### Preliminary observations (not NB04 results; the exclusion step was not yet applied)

- 11 of 12 participants are **anticipatory** in all conditions (mean ≈ −60 ms).
- **P007 is reactive in all five conditions** (+77…+177 ms). This matches
  their outlier status in the action distribution (D 15.2% vs ~2%). The same
  person standing out on two independent measures suggests the measure
  captures something real.
- **The condition effect is small:** within-participant profile −8.1 / −1.5 /
  +7.4 / −1.6 / +3.8 ms, spread ~15 ms. Between-person spread −180…+177 ms;
  individual differences are an order of magnitude larger.
- **No clear shift along the learning axis:** trial fifths −42.0 / −63.9 /
  −55.2 / −50.2 / −55.1 ms. A jump after the first ten trials, then flat.
  Consistent with the expectation caveat in §3.2.

### New rule: no comparisons across angles

The zero crossing becomes more negative as the angle grows
(−13/−53/−98/−145 ms). This is not "more anticipatory at larger angles":
since the pole passes 5° before 20°, the same reversal comes out more
negative against later references. We measured it: within the same fall,
getting from 5° to 20° takes a median of 256 ms, while the zero-crossing
difference is 132 ms. So roughly half of the gradient is geometry. **Fix the
angle and compare along condition/trial order.**

`Documentation/Yontem/05_Action_Timing.md` was written; what NB04 will do is
itemized there. The feasibility scripts are in the scratchpad; the code has
not been moved to `src/` yet.

---

## 2026-08-30: Documentation infrastructure

- `Documentation/Yontem/` was set up: data processing, physics/T₀,
  state-action-episode, performance metrics. Each record has definition, code
  reference, decision, evidence and what it feeds.
- `Pilot_Sonuc_Ozeti.md` was written; the presentation's result was recorded
  as text for the first time. Before, it existed only in `90_sunum.ipynb` and
  its HTML; the pptx/docx in the folder are dated 26 August and were prepared
  before the 12-participant analysis, so their numbers are invalid.
- `Veri_Kayit_Istekleri.md` was revised for 12 participants.
- Four placeholder `ABOUT.md` files were replaced with real content.
- **Action timing was not written**; method decisions come first. Ludolph's
  procedure was extracted and the points requiring decisions for the transfer
  were identified (below).

### Corrections and measurements prompted by questions

Questions about the explainer artifact (`Ters Sarkaç Analiz Rehberi`, the
inverted pendulum analysis guide) exposed several errors and gaps:

- **The input device is an `Xbox Controller`, not a keyboard.** I had
  inferred keyboard from the data pattern without looking at the metadata;
  that was wrong. It is an analog stick: 136 distinct non-zero magnitudes,
  ~0.0098 steps, saturated samples ~5% of non-zero ones. The input is graded.
  Good news for Ludolph's "mean force curve is a sigmoid" assumption: the
  action timing risk level dropped from "probably won't work" to "probably
  works, confirm".
- **"Correlation 0.988–0.997, model validated" was an incomplete statement.**
  Correlation is scale-free. With `l = 1.0` the correlation is almost the
  same (0.9884–0.9971), but the RMS error goes from 0.189 to 0.997. What pins
  `l = 0.5` is the RMS and the free-fall test. `l` = distance from pivot to
  centre of mass; the `4/3` factor comes from the rod's moment of inertia.
- **"Are 11 samples enough" was the wrong frame.** T₀ is not estimated, it is
  computed deterministically from the model; the 11 episodes are a test.
  With `l = 1.0` the ratio would come out ~0.71 every time. Limitation: the
  11 episodes cover T₀ = 2.20–3.38 s; the upper end (up to 9.68 s) is untested.
- **T₀'s remaining jobs were clarified:** validation (done), difficulty
  covariate, survival analysis. Not a performance metric.
- **Ludolph-type event counts were measured**, no feasibility problem:
  ±25° 110,091, ±15° 79,607, ±10° 57,549, ±5° 29,198 fall-direction crossings.

### Two corrections to the action timing frame

1. **No wall clock needed; `trial_order` already is a time axis.** Trials
   run back to back, the session is ~21 minutes (53 × 20 s active + ~115 s
   reset + 53 × 1.5 s pause). Ludolph's 2-minute window ≈ 6 trials. The
   window's real job is not tracking learning but collecting enough segments
   to average.
2. **Action timing will be examined along two axes at once:** trial order
   (learning, the shift from reaction to anticipation) and condition (does
   noise disrupt it). The earlier suggestion narrowed it to the condition
   axis only, which was wrong. Caveat: Ludolph measured learning in a task
   of over an hour with increasing difficulty; we have one session, 21
   minutes, fixed g, so no learning signal may not mean "no learning".

Also, for the velocity exclusion, **stratification instead of dropping** was
suggested (slow/mid/fast bands), and the angle range will be swept instead of
a single value (±25, ±15, ±10, ±5).

### Open: action timing transfer decisions

Ludolph's four steps (paper p. 11) were extracted: (i) integer angles
−25..+25° as events, sub-frame resolution by linear interpolation; (ii)
exclusion if the pole is rotating upward or angular velocity is outside the
20–80% quantiles; (iii) 1 s force segment centred on the event; (iv) average
in a 2-minute sliding window, zero crossing of the mean segment = action
timing. Variability = mean sd of force within ±60 ms of the zero crossing.

Five decisions had been opened; four were closed by the discussion above,
one stayed open.

1. ~~Aggregation unit~~ → **closed.** `trial_order` will be used as the time
   axis; action timing will be examined along both trial order and condition.
2. ~~Velocity quantile exclusion~~ → **closed.** The band will be computed
   per participant, pooling all conditions. And **stratification** will be
   preferred over dropping (slow/mid/fast). Rationale for the exclusion: the
   method stacks dozens of segments and averages them; putting crossings at
   very different velocities into the same average blurs the curve and makes
   the zero crossing meaningless.
3. ~~Event range~~ → **closed.** ±25 / ±15 / ±10 / ±5 will be swept instead
   of a single value. Event counts are sufficient in all.
4. ~~Segments crossing episode boundaries~~ → **closed.** Segments crossing
   the boundary will be dropped entirely, not trimmed (`applied_force_n` is
   fake on reset rows).
5. **Open: the sigmoid assumption.** Ludolph's method rests on "the mean
   segment is a sigmoid and crosses zero once". The analog stick supports
   this, but 73.9% of active samples are exactly zero. An empirical check at
   a single event angle will be done before writing code.

---

## 2026-08-28: NB02 rerun, NB03

- **NB02 was rerun with 12 participants.** Its outputs were still at 7
  participants (P008–P012 had arrived at 17:00 on 27 August; NB01 was rerun
  but NB02 was not). Result: 846,060 samples, 2,017 episodes, 18,891 regime
  runs, 35,519 events.
- All three validations held: physics model correlation 0.988–0.997; T₀
  free-fall test `duration/T₀ = 1.0000` in **11 of 11 episodes**; the `fall`
  event count matches Unity's `fall_count` exactly (1,381).
- **`check_angle_stream` was run with 12 participants.** P001–P007 still read
  from one shared angle sequence; P008–P012 fall into separate groups. This
  is not "a different seed": the metadata says 12345 for all, and none is at
  offset 0. The algorithm cannot see the chain because adjacent but
  non-overlapping slices cannot be matched. Practical consequence: the
  alignment across participants is partly broken, reducing the risk that the
  bias does not wash out. Initial |θ| spread 0.47° → 0.35°, `fall_count`
  correlation +0.14 → +0.066.
- **NB03 was written and run.** `src/performance.py` + `03_performance.ipynb`.
  Output: `trial_metrics.parquet` (600), `participant_condition.parquet` (60).

### Decisions

- **sIQR_theta and sIQR_omega do not enter the decision set.** The criterion
  was switched from correlation to trend: the real question is not whether
  the metric differs from RMS but whether it sees a noise trend RMS does not.
  sIQR_theta carries 9% of the trend, sIQR_omega 21% (opposite sign). maPA is
  also a copy of RMS (r = 0.98); only one of the two will be reported, maPA was chosen.
- **No separate duration metric; T/T₀ rejected.** `mean_episode_s` turned out
  to be a deterministic transform of fall count (`corr = 1.0000`, since the
  number of episodes = falls + 1 and the trial is a fixed 20 s). Dividing by
  T₀ increases contamination rather than reducing it (θ₀ correlation at
  participant × condition level 0.229 → 0.645). The uncensored versions carry
  survivorship bias. Ludolph's duration measure needs survival analysis; if
  needed, NB05.
- **Stabilization time with our own threshold.** Unity's
  `within_bounds_time_s` uses the failure limit, mean 19.97 s sd 0.04 over
  600 trials, stuck at the ceiling. With a 30° threshold: 18.22 s, sd 1.67.
- Statistical tests do **not** go in NB03; they are NB06's job. The
  presentation notebook merged the two because it was rushed; the chain was
  not left that way.

### New findings

- `valid_trial` is no longer always 1: P011's T030 and T034 are marked
  `invalid_reason = "paused"`. Our `flag_trials` does not look at this column,
  so both are `qc_pass`. Inspected, the data looks normal (1200 full samples,
  no focus loss). 2 in 600, low impact, but a rule should be added.
- `check_angle_stream` exists in `src/qc.py` but is not called in NB01 §7.
  CLAUDE.md said it was called; corrected.

---

## 2026-08-28 (morning): Presentation analysis

`90_sunum.ipynb` + `src/presentation.py` were written and run with 12
participants. Isolated module: the rest of the chain does not import it; it
only reads `data/interim`.

**Finding: no U shape, monotonic degradation.** Linear contrast on maPA
p = 0.0005, quadratic p = 0.62. N2/N3/N4 significantly worse than baseline
(after Holm), no difference at N1. Details:
[Pilot_Sonuc_Ozeti.md](Pilot_Noise/Pilot1_Results_Summary.md).

---

## 2026-08-27: NB01, NB02, data growth

- NB01 (load & QC) and NB02 (build) were written.
- During the day the number of participants went from 7 to 12; NB01 was rerun.
- The physics model was inferred from the data and validated; `l = 0.5`
  (half-length) was identified.
- It was measured that Park's sign convention **cannot be transferred
  as-is**: in our task the corrective force has the **same** sign as θ.
- It was found that there are two fall causes (`angle` / `track`); the
  `TrackLoss` label was added.
- The `randomizationSeed` problem was verified from the data.

---

## 2026-08-26: Setup

- Repo structure, pulling data from Drive with `drive_sync.py`.
- The first pilot data (P001, P002) was inspected; `Veri_Kayit_Istekleri.md`
  was written and sent to the team.
- Note: that day's P001/P002 were smoke-test data and were later deleted. The
  current P001/P002 are different, real participants.
