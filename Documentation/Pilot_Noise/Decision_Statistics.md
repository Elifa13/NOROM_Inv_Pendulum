# Decision statistics (noise study)

**Notebook:** `06_noise_decision.ipynb`
**Code:** `src/decide.py`
**Output:** `data/<dataset>/processed/karar/decision_stats.csv`, `decision_table.csv`
**Status:** implemented (2026-08-31)

This record answers "which test did we use and why". The results themselves
are in [Pilot1_Results_Summary.md](Pilot1_Results_Summary.md) and
[Pilot2_Results_Summary.md](Pilot2_Results_Summary.md). The numbers below are from pilot1 (n = 12).

---

## 0. Terms

| Term | Meaning |
|---|---|
| **within-subject** | Every participant saw all conditions; the comparison is made within the person. This takes the huge between-person differences out of play. |
| **Friedman test** | The non-parametric (rank-based) omnibus test of "is there any difference among these k conditions" for repeated measures. The counterpart of ANOVA without its distributional assumption. |
| **Kendall's W** | Friedman's effect size. 0 = participants rank conditions randomly, 1 = all in the same order. `W = χ² / (n(k−1))`. |
| **Wilcoxon signed-rank** | Test of the difference between two paired measurements. The non-parametric counterpart of the paired t-test. Computed exactly at n = 12. |
| **Holm correction** | Controls the false-positive risk in multiple comparisons. A less conservative, step-down version of Bonferroni. |
| **orthogonal contrast** | Weighting the condition means to reduce them to a single score. If the weights are orthogonal, the linear and quadratic components are tested independently. |
| **rank-biserial correlation** | Effect size for paired Wilcoxon: in the ranking of \|d\| of non-zero differences, share of positives minus share of negatives, −1…+1. |
| **d<sub>z</sub>** | Paired-difference effect size: mean difference ÷ standard deviation of the differences. |

## 1. Analysis unit and why

**Participant × condition**, each cell the mean of that person's 10
measurement trials in that condition. 12 × 5 = 60 cells.

No tests at trial level, because the same person's trials are not
independent; counting 600 trials as independent observations produces false
positives. Cell level encloses that dependence within the participant.

## 2. Choice of tests

**n = 12.** All tests are rank-based.

**Implementation note (2026-09-02).** The first version of this section said
"at n = 12 the normality assumption cannot be tested; parametric tests are
risky". It was tested, and the rationale needs correcting.
`92_varyans_ayrisimi.ipynb` §1, on the same participant × condition table:

| Metric | Shapiro p | RM-ANOVA | Friedman |
|---|---|---|---|
| `mae_angle_deg` | 0.99 | F(4,44) = 6.71, p = 0.0003 | p = 0.0014 |
| `stab_time_s` | 0.15 | F(4,44) = 3.18, p = 0.022 | p = 0.021 |
| `falls_angle_per_trial` | **0.0009** | F(4,44) = 3.16, p = 0.023 | p = 0.0051 |

In the first two, normality is not rejected and the parametric test gives the
same result. In the third, normality is clearly rejected (expected, since it
is a count variable), and there Friedman comes out stronger than the
parametric test.

So the rank-based choice is **defensible**, but the reason is not "cannot be
tested": (a) one of the decision metrics really is not normal, (b) at n = 12
Shapiro has low power, so in the other two "not rejected" is not the same as
"normal", (c) staying in one test family for all three metrics is
consistent. No metric's result depends on the test family, so the decision
is unaffected.

| Question | Test | Why |
|---|---|---|
| Is there any difference among the five conditions | Friedman + Kendall's W | Repeated measures, non-parametric omnibus |
| Which level differs from baseline | Wilcoxon signed-rank + Holm | Paired, exact, corrected for multiple comparisons |
| **Shape: is there a U** | orthogonal contrast + one-sample Wilcoxon | Below |

## 3. The shape test: this notebook's real job

Stochastic resonance is a claim about a **U shape**: the ends are bad, the
middle is good. You cannot test it with "do the conditions differ";
monotonic degradation also produces differences. The shape has to be tested
separately.

Two orthogonal polynomial contrasts:

| Contrast | Weights | What it asks |
|---|---|---|
| linear | −2, −1, 0, +1, +2 | Is there a steady trend as noise increases |
| **quadratic** | +2, −1, −2, −1, +2 | **Is there a peak/trough in the middle: the SR test** |

Procedure: the weights are applied to each participant's five condition
values to get one score (`arr @ weights`), then a **one-sample Wilcoxon** on
the scores (H₀: median score is zero). I.e. "is this shape component
consistently different from zero across participants".

**Weights use ordinal position.** The σ values are not evenly spaced
(0, 0.02, 0.05, 0.08, 0.25) and include zero, so no log can be taken. An
ordinal contrast assumes "the next level in line"; the real intervals on the
σ scale are ignored. This is a limitation and stays on record.

## 4. A second check next to the quadratic contrast

The contrast test was not left alone, because a null quadratic is the
weakest way to say "no U". `decide.interior_optimum` looks directly:

- Which condition is best in the group mean, and is it an **interior** condition (N1/N2/N3)
- How many participants have an interior condition as their own best

This second check produced a nuance: **in the group mean the best condition
is N1 in all three metrics**, i.e. the numerical peak is at an interior
condition. But the N1–baseline difference is not significant in any metric
and the quadratic contrast is null. Interpretation: this is not a U; it is
no_noise and N1 being indistinguishable.

`decide.personal_best` composite: each metric is z-scored within
participant and signed by its direction, metrics are averaged, and the
highest-scoring condition is taken. Result 6 no_noise / 5 N1 / 1 N2; nobody's
best is N3 or N4.

## 5. Multiple comparisons: where corrected, where not

Holm was applied **within the four baseline comparisons of one metric**.

No extra correction across metrics **was applied**, because the three
decision metrics are not independent families.

**Correction (2026-09-02).** This rationale was first based on r = 0.98
between `mae_angle_deg` and `rms_angle_deg`. That is an invalid basis:
`rms_angle_deg` is not a decision metric, so that correlation says nothing
about the relation among the three decision metrics. The correct numbers, on
the within-person centred participant × condition table:

| | mae | stab | falls |
|---|---|---|---|
| `mae_angle_deg` | 1.00 | −0.86 | 0.42 |
| `stab_time_s` | −0.86 | 1.00 | −0.39 |
| `falls_angle_per_trial` | 0.42 | −0.39 | 1.00 |

mae and stab are almost copies of each other; `falls_angle_per_trial`
carries partly separate information (r ≈ 0.4). So "all three are the same
construct" is true for the first two and too strong for the third.

It does not change the result, because the correction was actually computed.
The linear contrast with Holm applied across the three metrics is
0.0015 / 0.0049 / 0.0020; all three stay significant. The quadratic is
corrected to 1.00 in all three anyway. The decision rests on the
linear/quadratic contrast, so it is unaffected.

## 6. Sensitivity checks

The decision could have been sensitive to two choices; both were tested.

**`valid_trial` (`decide.drop_invalid_trials`).** Unity marked 2 of 600
trials as `paused`; NB01 does not look at that column (known open item), so
both enter the analysis. Dropping them, the condition ranking stays the same
and one p value moves: `stab_time_s` quadratic 0.5693 → 0.6221. Both are far
from the significance threshold, so the result is unaffected. (The first
version said "no p value moves"; the list in §6 already showed 0.62, so the
sentence was too strong.) The rule should still be added to NB01, but the
decision does not depend on it.

**Stabilization threshold (`decide.threshold_sensitivity`).** `stab_time_s`
uses our own threshold (|θ| ≤ 30°, rationale in `Setup/04`). Since the
threshold is our choice, the result should not depend on it. 5°–45° sweep:
linear significant at every threshold (p ≤ 0.0068), quadratic significant at
none (p = 0.38–0.57).

## 7. What it feeds

The choice of noise level for the main experiment. The candidate ranking and
the question for the team are in [Pilot1_Results_Summary.md](Pilot1_Results_Summary.md),
section "Candidate ranking for the main experiment". (The noise study was
later closed; see `Analysis_Log.md`, 2026-09-08.)

## 8. Not in this record

- **No power analysis.** "How small an effect could this design detect" was
  NB05's job. N1 being null means "not detectable with this sample", not "no
  difference". Partly closed: `92_varyans_ayrisimi.ipynb` measured the
  variance decomposition and within-person reliability, which gives an
  order-of-magnitude estimate of the required trial count. A classical power
  analysis for pilot1 is still missing (pilot2's is in `Pilot2_Results_Summary.md`).
- **No Bayes factor.** That is what would be needed to present the null
  finding (N1 = baseline) as evidence; for now it is only "not distinguishable".
- **Action timing not included** (NB04). It did not separate conditions, so
  it did not enter the decision set.
