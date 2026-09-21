# Pilot 1 results summary

**Data:** 12 participants (P001–P012), single session, 53 trials (3 practice +
50 measurement). Collected 26–27 August 2026.
**Analysis:** `Notebooks/pilot_noise/pilot1/06_noise_decision.ipynb`, `src/decide.py`
(the decision metric set was chosen in `03_performance.ipynb`)
**Outputs:** `data/pilot1/processed/karar/`: `decision_stats.csv`,
`decision_table.csv`

> This document describes **pilot 1**. For the second pilot (10 people,
> σ ≤ 0.02) see [Pilot2_Results_Summary.md](Pilot2_Results_Summary.md). The two sets'
> participant ids and condition labels overlap but do not mean the same thing.

This document used to carry the numbers of the emergency presentation
notebook (`90_sunum.ipynb`). On 31 August NB06 was written and the numbers
were replaced with the chain's own output. The only difference is in the
fall metric: the presentation counted all falls, the decision set counts
**only angle-caused** ones (track loss is a separate failure, see `Setup/03`).

This document does not replace `Pilot_Noise/archive/CartPole_VisualNoise_Pilot_Sunumu (1).pptx`
and `Kalibrasyon_Pilot_Calismasi_Veri_Ozeti (1).docx`, but it is **more up to
date** than them: both are dated 26 August, i.e. prepared before the
12-participant analysis, and their numbers are no longer valid.

---

## Result

**The stochastic resonance hypothesis is not supported in the pilot.** No
improvement at medium noise; performance degrades monotonically as noise increases.

The difference between the expected shape (the inverted U in Treviño 2016)
and the observed one shows directly in the statistics: the linear trend is
strong and significant in every metric, the quadratic trend in none.

## Condition × metric

Analysis unit participant × condition (mean of 10 trials), n = 12.

| Metric | Direction | no_noise | N1 (σ0.02) | N2 (σ0.05) | N3 (σ0.08) | N4 (σ0.25) |
|---|---|---|---|---|---|---|
| Mean absolute angle (°) | lower is better | 11.25 | **11.20** | 12.28 | 12.51 | 12.66 |
| Stabilization (s / 20 s) | higher is better | 18.37 | **18.49** | 18.05 | 18.08 | 18.09 |
| Angle-caused falls / trial | lower is better | 1.60 | **1.47** | 1.78 | 1.70 | 2.00 |
| Control effort (RMS u) | ambiguous | 0.206 | 0.209 | 0.209 | 0.200 | 0.208 |
| Cart RMS (m) | ambiguous | 1.09 | 1.13 | 1.02 | 1.14 | 1.04 |

Condition ranking (1 = best, mean of the three decision metrics):
**N1 (1.0) → no_noise (2.0) → N3 (3.67) → N2 (4.0) → N4 (4.33)**.
N1 is numerically best in all three metrics, but in the tests below it cannot
be distinguished from baseline.

The pattern is the same in all metrics: **no_noise and N1 together,
degradation from N2 on.**

## Statistics

Friedman (5 conditions, n = 12), then Wilcoxon against baseline with Holm
correction. Trend contrasts use ordinal position.

| Metric | Friedman p | Kendall's W | Linear p | Quadratic p |
|---|---|---|---|---|
| Mean absolute angle | **0.0014** | 0.37 | **0.00049** | 0.62 |
| Stabilization time | **0.021** | 0.24 | **0.0049** | 0.57 |
| Angle-caused falls | **0.0051** | 0.31 | **0.00098** | 0.58 |
| Control effort | 0.75 | 0.04 | 1.00 | 0.38 |
| Cart RMS | 0.13 | 0.15 | 0.68 | 1.00 |

The linear contrast for `mae_angle_deg` points the same way in **12 of 12**
participants.

### Which level differs from baseline

Paired Wilcoxon, Holm correction within metric (four comparisons).

| Condition | maPA difference | d<sub>z</sub> | p (Holm) | Same direction |
|---|---|---|---|---|
| N1 | −0.05 | −0.03 | 0.91 | 6/12 |
| N2 | +1.03 | 1.18 | **0.015** | 11/12 |
| N3 | +1.26 | 1.17 | **0.014** | 11/12 |
| N4 | +1.41 | 0.96 | **0.019** | 11/12 |

In the other two metrics only N4 survives Holm (`falls_angle_per_trial`
p = 0.039). The three metrics are strongly related (within-person centred:
maPA–stabilization r = −0.86, maPA–falls r = 0.42), so they are not fully
independent evidence; no extra correction across metrics was applied. It was
computed later and would not have changed anything: the linear contrast with
Holm across the three metrics is 0.0015 / 0.0049 / 0.0020, all three stay significant.

**The quadratic term is not significant in any metric.** An inverted U would
have shown up here.

Pairwise comparisons against baseline (maPA, after Holm): N1 p = 0.91 (no
difference), N2 p = 0.015, N3 p = 0.014, N4 p = 0.019, all three significantly **worse**.

## The threshold choice does not change the result

The "successful stabilization" threshold was swept from 5° to 45°. The
direction is the same at every threshold; the effect size is stronger at
narrow thresholds.

| Threshold | no_noise | N4 | dz | Same direction | Linear p |
|---|---|---|---|---|---|
| 5° | 7.16 | 6.10 | −1.34 | 10/12 | 0.00049 |
| 10° | 12.40 | 11.02 | −1.30 | 11/12 | 0.00049 |
| 15° | 15.03 | 13.95 | −1.08 | 11/12 | 0.00049 |
| 20° | 16.64 | 15.91 | −0.81 | 11/12 | 0.0024 |
| 25° | 17.73 | 17.19 | −0.65 | 10/12 | 0.00098 |
| 30° | 18.37 | 18.09 | −0.45 | 10/12 | 0.0049 |
| 45° | 19.49 | 19.38 | −0.51 | 8/12 | 0.0068 |

At wide thresholds a ceiling effect kicks in (at 45°, 97% of the time is
within the threshold), so the effect fades. The main figures use 30°.

## Personal optimal level

For each participant, the best condition in the composite ranking
(composite: maPA, stabilization time, fall count):

| Optimal | Participants |
|---|---|
| no_noise | P002, P003, P005, P007, P010, P011 (6) |
| N1 | P001, P004, P008, P009, P012 (5) |
| N2 | P006 (1) |

**No participant's optimum is N3 or N4.** For 11 of 12 people the optimum is
either no_noise or N1, i.e. between "no noise" and "lowest noise". (The
composite was recomputed in NB06 on z-scores; in the presentation version
P004 was tied, now it falls to N1.)

## The decision rests on both checks

**(a) `valid_trial`.** Unity marked 2 of 600 measurement trials as `paused`
(P011 T030, T034); NB01's quality control does not look at that column, so
both enter the analysis. Dropping them, the condition ranking stays the same
and one p moves: `stab_time_s` quadratic 0.57 → 0.62. The others are
unchanged (linear 0.00049 / 0.0049 / 0.00098, quadratic 0.62 / 0.62 / 0.58).
Both are far from the significance threshold; the result is unaffected.

**(b) Stabilization threshold.** Swept from 5° to 45°: **linear significant
at every threshold (p ≤ 0.0068), quadratic significant at none**
(p = 0.38–0.57). The best condition flips between no_noise and N1 depending
on the threshold, another sign that the two are indistinguishable.

## Raw data verification

Four metrics were recomputed independently from the raw CSVs and compared
with the result of the parquet chain (`presentation.raw_verification`). No
drift in the chain.

## Limitations

1. **Randomization depended on a fixed seed.** All participants saw the same
   condition order and the same noise pattern. Initial angles also came from
   a single fixed sequence. The effect was measured and is small
   (between-condition spread of initial |θ| 0.35°, correlation with outcome
   +0.066), and **its direction works against the finding**: the hardest
   starts are in no_noise. Details: `Recording_Requests.md`, item 1. Fixed before pilot 2.
2. **The pilot measures immediate performance, not learning.** Ludolph's
   finding points to these two being separable: a condition can be bad for
   immediate performance and good for learning. Writing two ranked candidates
   into the main experiment instead of a single level was a reasonable hedge.
3. **Transfer of SR to this task was an open question anyway.** Treviño's
   critical precondition was pushing the signal deliberately below threshold
   (low coherence + low luminance). The pole in the cart-pole is high-contrast
   and large, far above threshold. So the negative result may show not that
   SR is wrong but that it does not apply to this task.

## Candidate ranking for the main experiment

*Historical: the noise study was closed after pilot 2 and the main
experiment became GAP (see `Analysis_Log.md`, 2026-09-08).*

**Candidate 1: N1 (σ = 0.02).** Visual noise is present but does not
measurably degrade performance (p ≈ 0.91, d<sub>z</sub> ≤ 0.20, 6/12). The
"learning under noise" question should be asked at a level where noise does
not already wreck immediate performance; otherwise the learning difference
and the performance degradation get mixed up.

**Candidate 2: N2 (σ = 0.05).** The **lowest** level with a measurable
effect (d<sub>z</sub> = 1.18, 11/12). Preferred if the question is "does
noise impair learning", but since it also degrades immediate performance the
two effects may not be separable.

**N3 and N4 are dropped.** No significant difference between N3 and N4, so
higher noise brings no extra information; N4 is already the worst condition.

### The ranking depends on one question

Will the main experiment use **a single noise level + a no_noise control
group**, or will **everyone get the same noise**? The team was asked; no answer.

- **If there is a control group:** the difference between N1 and no_noise is
  too small to detect in this pilot; such a design would likely give a null
  result. In that case N2 is more informative.
- **If everyone gets the same noise:** the noise's job is not to prevent
  measuring learning, so N1.

The candidate order **changes** with the answer. NB06 produced the numbers
needed for both cases.
