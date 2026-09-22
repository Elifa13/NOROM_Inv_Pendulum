# Pilot 2 results summary

**Data:** 10 participants (P001–P010), single session, 53 trials (3 practice +
50 measurement). Collected 2–3 September 2026, P010 on 8 September 2026. The
chain was rerun with P010 on 14–15 September; this summary was updated to 10
people on 21 September. The result does not differ from the 9-person version.
Drive folder `1oge-PfEM-ZOmmlpWoqIZF7P1yT3f-J3V`.
**Analysis:** the chain under `Notebooks/pilot_noise/pilot2/` (01 → 02 → 03 → 04 → 06) and
the isolated scans (91, 92, 93). The code is the **same** `src/` modules as pilot 1.
**Outputs:** `Data Analysis/data/pilot2/`: `interim/*.parquet`,
`processed/karar/decision_stats.csv`, `decision_table.csv`

> Pilot 1's participants are also numbered P001…, but they are **not the
> same people**. The condition labels (N1–N4) are the same too, but **not
> the same sigma**. The two sets are never merged at any stage; they are
> compared only via sigma.

---

## Result

**No condition effect in this noise range.** None of the conditions can be
distinguished from no_noise; neither the linear nor the quadratic trend is significant.

This complements pilot 1. Pilot 1's ladder ran from σ = 0.02 to 0.25 and gave
"performance degrades monotonically from σ ≥ 0.05, σ = 0.02 cannot be
distinguished from baseline". Pilot 2's ladder is entirely **below** that
threshold (σ ≤ 0.02), and nothing happens there either: no improvement, no
degradation. Both pilots together: **visual noise does not affect
performance up to σ ≈ 0.02 and degrades it above. No inverted U
(stochastic resonance) anywhere.**

## Noise ladder

| Condition | Pilot 2 σ | Pilot 1 σ |
|---|---|---|
| no_noise | 0.000 | 0.00 |
| N1 | 0.005 | 0.02 |
| N2 | 0.010 | 0.05 |
| N3 | 0.015 | 0.08 |
| N4 | 0.020 | 0.25 |

Pilot 2's highest condition (N4, σ = 0.020) equals pilot 1's lowest noise
condition (N1, σ = 0.02). In both sets that level cannot be distinguished
from baseline: the single overlap point, confirmed in 22 different people.

## Condition × metric

Analysis unit participant × condition (mean of 10 trials), n = 10.

| Metric | Direction | no_noise | N1 (σ0.005) | N2 (σ0.010) | N3 (σ0.015) | N4 (σ0.020) |
|---|---|---|---|---|---|---|
| Mean absolute angle (°) | lower is better | 10.99 | **10.92** | 11.01 | 11.20 | 11.13 |
| Stabilization (s / 20 s) | higher is better | 18.45 | 18.40 | **18.48** | 18.39 | 18.32 |
| Angle-caused falls / trial | lower is better | 1.50 | 1.38 | 1.51 | **1.38** | 1.40 |
| Control effort (RMS u) | ambiguous | 0.221 | 0.220 | 0.222 | 0.219 | 0.218 |
| Cart RMS (m) | ambiguous | 1.22 | 1.11 | 1.18 | 1.19 | 1.16 |

The "best" in the three decision metrics falls on three different conditions
(N1 / N2 / N3), and the differences are under one percent. The ranking itself is noise.

## Tests

All tests are within-subject and non-parametric, n = 10.

| Metric | Friedman p | Kendall W | Linear p | Quadratic p |
|---|---|---|---|---|
| `mae_angle_deg` | 0.93 | 0.02 | 0.43 (7/10) | 0.92 |
| `stab_time_s` | 0.52 | 0.08 | 0.43 (5/10) | 0.38 |
| `falls_angle_per_trial` | 0.32 | 0.12 | 0.61 (5/10) | 0.77 |
| `control_effort` | 0.82 | 0.04 | 0.77 | 0.85 |
| `cart_rms_m` | 0.30 | 0.12 | 0.77 | 0.49 |

In paired comparisons against baseline, no condition goes below p < 0.29
even before Holm; the largest effect is N3 in `falls_angle_per_trial`
(dz −0.43, 3/10 worse), and its direction is "noise **improves**", i.e. by chance.

**Sensitivity.** No trials are marked `valid_trial = 0` (pilot 1 had P011's
two `paused` trials), so the sensitivity analysis gives the same result with
all 500 trials. In the 10°–45° stabilization threshold sweep, both linear
and quadratic are null at every threshold.

## Control mechanism (NB04)

| Finding | Pilot 2 | Pilot 1 |
|---|---|---|
| Pooled curve zero crossing (band 10) | **−45.8 ms** (95% CI −49.5…−42.4) | −52.6 ms (−55.6…−49.5) |
| Amplitude / standard error | 137× | 154× |
| Between-person spread | 138 ms | 269 ms |
| **Between-condition spread** | **15.7 ms** | 15 ms |
| Within-person, between-condition sd | 30.8 ms | 27.6 ms |
| Cells (participant × condition) | 50/50 filled, 49 with a single crossing | 60/60, 59 with a single crossing |

Same result: **action timing is predictive** (negative) but not sensitive to
condition; the condition spread is one ninth of the person spread. Action
timing does not enter the decision set in pilot 2 either.

As in pilot 1, the learning shift is **not robust**: in the raw profile the
slope is −8.2 ms/window (dz −0.61, negative in 8/10 people), but with
composition fixed, looking only at the mid velocity stratum, it flattens
(−1.0 ms, dz −0.06). So the shift comes from faster crossings entering the
measurement in later trials, not from the timing itself.

Action variability again carries no separate information. The largest
difference from baseline is at N1 (dz 0.28), N4 dz 0.25. Divided by
amplitude, N1 dz 0.46, the others below 0.18.

## Variance and reliability (NB92, NB93)

| Measure | person | condition | residual | ICC |
|---|---|---|---|---|
| Mean \|θ\| | 96.2% | **0.1%** | 3.7% | 0.95 |
| Stabilization time | 95.6% | **0.2%** | 4.2% | 0.95 |
| Angle-caused falls | 96.8% | **0.2%** | 3.1% | 0.96 |
| Action timing | 63.1% | 1.3% | 35.6% | 0.55 |
| Cart RMS | 80.3% | 1.9% | 17.8% | 0.77 |

Across the three decision metrics the condition share was 0.7–4.0% in pilot 1
and drops to 0.1–0.2% in pilot 2, as expected when the ladder narrows. (The
ICC here is ICC(3,1), even though the code calls it ICC(2,1); see
`Setup/06_Reliability.md`.)

Cart RMS was added later (2026-09-22, for the HCI-E abstract), computed the
same way on the same table. It separates people less sharply than the angle
measures: ICC 0.77 against 0.95–0.96, with a residual share of 17.8% against
their 3.1–4.2%. Its condition share (1.9%) is the largest in the table, but
at that ICC the share is not evidence of a condition effect.

**A personal optimum is again not measurable.** Split-half (10 trials 5+5,
200 repetitions): the person's overall level agrees between halves
(r = 0.97–0.99), the condition ranking does not (rho = −0.08 / −0.17 /
−0.10; same "best" rate 15% / 16% / 24%, chance 20%). The per-person "best
condition" distribution (3 no_noise, 2 N1, 2 N2, 2 N3, 1 N4) is consistent
with randomness.

**There is learning, independent of condition.** Mean −0.043 degrees/trial
over the session, −2.11° over 50 trials, improving in 8/10 people (Wilcoxon
p = 0.037; with 9 people it was p = 0.055). Block-wise first 10 → last 10:
11.90° → 10.49°. The learning slope does not differ across conditions
(Friedman p = 0.61, linear p = 0.064), and the slope itself is not measured
reliably (split-half r = 0.30).

Trial-level variance decomposition: person 57%, condition 2.3%, learning
6.9%, residual 33%. **Learning is three times larger than the condition
effect.** In pilot 1 the two were close (6.2% condition, 7.8% learning); as
the ladder narrowed, the condition share melted away and learning's stayed the same.

## Control variability (NB91)

13 measures (median frequency, sample entropy, duty cycle, amplitude,
inter-action interval and its variability, onset rate). None significant
after Holm. In the raw Friedman, two measures give p < 0.05: the median
frequency of cart position and of cart velocity (both p = 0.027, 0.35 after
Holm). No raw p < 0.05 in the linear or quadratic contrast. Median frequency
is at its resolution limit at this segment length, so these two raw p values
should not be given weight (see NB91 §5–6). In pilot 1 two measures also gave
raw p < 0.05 and failed the robustness scan.

## Data quality

| Check | Result |
|---|---|
| Sessions | 10/10 complete, no partial sessions |
| Trials | 530 (10 × 53), QC FAIL 0 |
| Measurement trials | 500, all enter the analysis mask |
| Samples | 693,600; analysis mask 600,000 |
| `valid_trial = 0` | none |
| Timing/sampling | no problems (dt deviation ≤ 0.000067 s) |
| Velocity–position consistency | r ≥ 0.99 in all trials |
| Force = input × 4 N | holds |
| Physics model | correlation 0.994–0.998 in 8 segments |
| T₀ validation | 2 free-fall episodes, both `duration/T₀ = 1.0000` |
| Fall count | three sources (sample, cause, Unity) agree in 500/500 trials |

**The randomization problem is fixed.** Pilot 1's biggest data problem
(`randomizationSeed` fixed at 12345, everyone getting the same condition
order, the same noise pattern and the same initial-angle sequence) is gone in pilot 2:

- the metadata has a new `effective_randomization_seed` field carrying 10
  different values in 10 participants (`config.randomizationSeed` still says
  12345, so `qc.check_randomization` now looks at the effective seed first)
- condition order: 10 different sequences in 10 participants
- `noise_seed` sequences: 10 different sequences in 10 participants
- initial angles are not the same across all participants in any trial

The condition × trial_order balance is also good: each condition's mean
position is 25.3–25.7 (range 1–50).

**Folder layout.** Pilot 2's data sits on Drive inside pilot 1's
`Pendulum_Data` folder, as a `DataV2/` subfolder. Because `drive_sync` used
to take the last three parts of the path, pulling pilot 1 also dropped pilot
2's files into pilot 1's folder, and since participant ids collide it was
hard to notice. It happened once on 4 September, was cleaned up, and
`drive_sync` now requires exactly three parts. All of pilot 1's numbers came
out identical after the cleanup (session selection had already picked its
own sessions).

**Not fixed.** `config.participantId` still says "P001" in all metadata
(wrong for P002–P010; the `participant_id` field is correct). None of the 24
extra metadata fields requested (screen size, viewing distance, deadzone,
noise texture parameters…) are present yet; see `Recording_Requests.md`.

## What it says for the main experiment

*Historical: the noise study was closed and the main experiment is GAP.*

1. **Within σ ≤ 0.02, which level is chosen makes no difference for
   performance.** Pilot 1's "N1 (σ0.02) is indistinguishable from baseline"
   holds for the four levels below it as well.
2. **A measurable effect requires σ ≥ 0.05** (pilot 1: monotonic degradation
   from N2 on). But that degradation is not the improvement SR is looking for.
3. **No stochastic resonance in either pilot.** Nine different levels from
   σ = 0 to 0.25, 22 participants, no inverted U in any of them. Treviño's
   precondition (signal below threshold) is not met in this task: the pole is
   high-contrast and large.
4. **Power caveat.** n = 10 and the observed effects are small (|dz| ≤ 0.43
   against baseline). That means "not detectable with this sample", not "no
   difference". For a paired t-test (α = 0.05, two-sided) the power to detect
   dz = 0.2 with n = 10 is 9%, dz = 0.5 29%, dz = 0.8 62%, dz = 1.0 80%. So an
   effect the size of pilot 1's (dz ≈ 1.0) would show here; a small effect would not.
5. Learning is larger than the condition effect and independent of
   condition. If the main experiment measures learning, the noise level
   itself does not seem to disturb the learning curve, which is evidence
   that a low-noise condition would be usable in the main experiment.

## References

- Chain: `Data Analysis/Notebooks/pilot_noise/pilot2/`
- Method rationale (same for both pilots): `Documentation/Setup/`
- Pilot 1 counterpart: `Documentation/Pilot_Noise/Pilot1_Results_Summary.md`
