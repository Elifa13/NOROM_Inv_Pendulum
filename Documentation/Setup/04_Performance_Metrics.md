# 04: Performance metrics and choice of metric set

**Notebook:** `Data Analysis/Notebooks/pilot_noise/<dataset>/03_performance.ipynb`
**Code:** `src/performance.py`
**Config:** `config.yaml` → `performance`
**Output:** `data/<dataset>/interim/trial_metrics.parquet`, `participant_condition.parquet` (pilot1: 600 trials / 60 cells, pilot2: 500 / 50)

The numbers in this record are from pilot1 unless stated otherwise.

---

## 1. Analysis unit and denominator

**Analysis unit: participant × condition.** Each cell is the mean of 10
measurement trials. 12 participants × 5 conditions = 60 cells. The trial-level
table is an intermediate product (NB04 uses it too).

Mask: `analysis_include` (see [01 §3.5](01_Data_Processing.md)). Reset frames are
fully excluded, and every measurement trial has exactly 1200 active samples,
so **the denominator is constant**.

This is easy to miss but important: if reset frames were included, the "bad"
time of a participant who falls a lot would be diluted by resets and they
would look artificially good.

## 2. Trial-level metrics

`u` = `input_applied`, `θ` = `pole_angle_deg`, `x` = `cart_position_m`.

| Metric | Formula | Direction |
|---|---|---|
| `mae_angle_deg` | mean(&#124;θ&#124;) | lower is better |
| `rms_angle_deg` | sqrt(mean(θ²)) | lower is better |
| `siqr_theta_deg` | (Q75(θ) − Q25(θ)) / 2 | lower is better |
| `siqr_omega_deg_s` | same for ω | lower is better |
| `max_abs_angle_deg` | max(&#124;θ&#124;) | lower is better |
| `stab_time_s` | time with &#124;θ&#124; ≤ threshold | higher is better |
| `falls_per_trial` | sum of `fall_event` | lower is better |
| `falls_angle_per_trial` | falls with cause `angle` | lower is better |
| `falls_track_per_trial` | falls with cause `track` | lower is better |
| `control_effort` | sqrt(mean(u²)) | ambiguous |
| `cart_rms_m` | sqrt(mean(x²)) | ambiguous |

Episode-derived (per trial): `n_episodes`, `n_episodes_censored`,
`mean_episode_s`, `mean_T_over_T0` and their uncensored versions,
`mean_theta0_abs_deg`.

### Why `control_effort` and `cart_rms_m` are "ambiguous"

In both, a low value can mean two different things: good control, or not
intervening at all. On their own they do not say good or bad; they are only
used as tie-breakers.

### Stabilization time uses our own threshold

Unity's `within_bounds_time_s` column uses the **failure limit** (60° / 5 m)
as its threshold. Result: mean **19.97 s** over 600 trials, sd 0.04. It sits
at the ceiling and cannot separate conditions.

Our threshold is `performance.stab_angle_deg` = **30°**. With it: mean
18.22 s, sd 1.67.

The threshold itself is a choice. The presentation notebook swept 5°–45°,
and the direction of the result was the same at every threshold (see
[../Pilot_Noise/Pilot1_Results_Summary.md](../Pilot_Noise/Pilot1_Results_Summary.md)).

### Fall counts agree across three sources

In **600 of 600** measurement trials all three agree: the sample-level sum of
`fall_event`, the total split by cause (angle 1,025 + track 131), and Unity's
`fall_count` (1,156).

## 3. Is sIQR redundant? Checked; neither enters the decision set

### Why we asked

The original rationale: two participants can have the same maPA, but one
mostly sits at ±5° and occasionally swings to ±50°, while the other stays at
±15°. RMS penalizes the first disproportionately. sIQR captures that
difference.

### Criterion: switched from correlation to trend

The first criterion was "if correlation with RMS > 0.9, it is a copy". That
is **the wrong question**: even if a metric measures something different from
RMS, if it *does not separate conditions* it should not enter the decision
set.

Criterion applied (`performance.redundancy_check`):

1. Target metric and RMS are **centred within participant**. That is the
   right scale for a within-subject design; between-participant level
   differences inflate the correlation
2. The target is regressed on RMS
3. How much of the **linear contrast** in the residual's condition profile survives

Contrast weights by ordinal position: `[−2, −1, 0, +1, +2]`. The σ values
(0, 0.02, 0.05, 0.08, 0.25) are not evenly spaced and include zero, so no log
can be taken; ordinal ranking is the most defensible choice.

Thresholds: `redundancy_abs_r` = 0.9, `redundancy_retained_trend` = 0.25. If
either triggers, the metric counts as redundant.

### Result

| Metric | r (within) | Raw linear contrast | Residual | Retained trend | Decision |
|---|---|---|---|---|---|
| `siqr_theta_deg` | 0.848 | +3.082 | +0.282 | **9%** | redundant |
| `siqr_omega_deg_s` | 0.597 | +2.695 | −0.576 | **21%** | redundant |
| `mae_angle_deg` | 0.982 | +4.130 | +0.232 | **6%** | copy of RMS |

- **sIQR_theta** is almost a copy of RMS and carries 9% of the noise trend.
- **sIQR_omega** is a separate construct (r = 0.60; the expectation of
  "oscillation independent of angle magnitude" held), but RMS still explains
  79% of the noise trend, and the remaining 21% has **the opposite sign**,
  i.e. it is irregular.
- **maPA and RMS** are copies of each other; only one should be reported.
  maPA was chosen, it is easier to read.

All three remain in `trial_metrics.parquet`. sIQR_omega can be used in NB04
to describe the control mechanism, just not as a **decision metric**.

## 4. Duration measure: all candidates rejected

Ludolph's T/T₀ is meaningless at trial level (see
[02 §6](02_Physics_and_T0.md)). Four candidates were tried at episode level; all
were rejected.

### 4.1 `mean_episode_s`: a deterministic transform of fall count

Episodes cover the trial completely (20 s in total) and every fall is an
episode boundary. Therefore:

```
n_episodes  = falls + 1          (verified in 600 of 600 trials)
mean_episode_s = 20 / (falls + 1)
```

`corr(mean_episode_s, 20/(falls+1)) = 1.0000`. **It carries no new
information**; it is `falls_per_trial` rewritten.

### 4.2 `mean_T_over_T0`: dividing by T₀ over-corrects

T₀ decreases as θ₀ grows. Dividing duration by T₀ ≈ multiplying by 1/T₀, so it
**increases** the θ₀ dependence instead of reducing it:

| Level | Raw duration | Divided by T₀ |
|---|---|---|
| Episode | −0.075 | +0.141 |
| Participant × condition | +0.229 | **+0.645** |

Ludolph's normalization works backwards in our design.

### 4.3 Uncensored versions: survivorship bias

A censored episode means "did not fall until the end of the trial", i.e.
**the best attempts**. Dropping them:

- the no_noise mean falls from 12.10 s to 7.38 s and becomes the **lowest**
  condition, an absurd result
- the N4 effect flips sign: dz −1.03 → +0.25

600 of 1,756 episodes are censored (34.2%), not a negligible share.

### 4.4 Decision

**No separate duration metric is used; `falls_angle_per_trial` is a
sufficient statistic.**

Using Ludolph's duration-based measure properly would require survival
analysis that handles right-censoring (Kaplan-Meier / Cox). Out of NB03's
scope; if needed, it goes in NB05.

## 5. Decision metric set (goes to NB06)

| Metric | Direction | Note |
|---|---|---|
| `mae_angle_deg` | lower is better | r = 0.98 with RMS, use one of the two |
| `stab_time_s` | higher is better | our own threshold, 30° |
| `falls_angle_per_trial` | lower is better | the one comparable with Park's Failed |
| `control_effort` | ambiguous | tie-breaker |
| `cart_rms_m` | ambiguous | tie-breaker |

**Excluded:** the sIQRs (§3), duration metrics (§4), `falls_track_per_trial`
(looks unrelated to condition, dz within ±0.12; it is excluded from the Park
comparison anyway).

## 6. Descriptive effect sizes

This notebook **does not run statistical tests**. Friedman / Wilcoxon and the
noise-level decision are NB06's job.

Reported:

- `baseline_farki` = condition − no_noise, paired difference per participant
- `dz` = mean(difference) / sd(difference)
- `n_kotu` = in how many of the 12 participants the difference is in the metric's bad direction

**maPA result:** no difference at N1 (dz −0.03, 6/12). At N2, N3, N4,
**11/12** participants are worse than baseline (dz 0.96–1.18).

The same shape in all main metrics: no_noise and N1 together, monotonic
degradation from N2 on. **No U shape.**

## 7. Initial-angle contamination

`mean_theta0_abs_deg` at participant × condition level ranges 3.53–3.85°
(spread 0.32°); at trial level 3.43–3.78°, spread 0.35°, within-trial sd
2.11°. Correlation with `fall_count` +0.066.

The direction **works against the finding**: the hardest starts (3.85°) are
in no_noise, so the bias cannot have inflated the observed degradation.

For the randomization problem itself (fixed seed in pilot1) see
`../Pilot_Noise/Recording_Requests.md` and `Unity/ABOUT.md`.
