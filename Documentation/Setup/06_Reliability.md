# 06: Variance decomposition and reliability (ICC, split-half)

**Notebook:** `92_varyans_ayrisimi.ipynb` (where it was written), pilot2 `91_control_variability.ipynb` (first to import it)
**Code:** `src/reliability.py`
**Config:** none. Constants are module parameters; defaults equal the values in NB92
**Output:** writes no files, returns tables

---

## 1. Why it exists

When a measure shows no condition effect, there are two explanations: there
is no effect, or the measurement is too noisy to see it. This module measures
the second.

The functions were first written in pilot1 NB92. When pilot2 NB91 needed the
same computation, they were moved to `src/reliability.py` instead of being
copied (2026-09-15). The module makes no decisions. ICC and split-half are
descriptive; which measure is reportable is judged in the notebook.

## 2. Definition

**`decompose(W)`**: in a balanced participant × condition table (n people, k
conditions, no NaN) the total sum of squares splits into three:

```
SS_total = SS_person + SS_condition + SS_residual
var_p = max((MS_person - MS_residual) / k, 0)
ICC   = var_p / (var_p + MS_residual)
```

The same sums of squares give two cross-checks: the condition F test of a
repeated-measures ANOVA (`F = MS_condition / MS_residual`) and a Friedman
test on the same table. Shapiro-Wilk is applied to the within-person centred
residuals.

**Note: the name is wrong.** The function's docstring and the notebooks call
this ICC(2,1). Algebraically the formula is `(MS_person − MS_residual) /
(MS_person + (k−1)·MS_residual)`, which in Shrout & Fleiss naming is
**ICC(3,1)**: two-way mixed, consistency, single measure. ICC(2,1) (absolute
agreement) would also include condition variance in the denominator. Because
the condition share is very small in this data the two values come out close,
but if ICC appears in a report or the paper it must be named ICC(3,1). NB92
does not say why this definition was chosen. The code was not changed; this
is only a naming note.

**`cell_table(df, metric, ...)`**: builds a participant × condition pivot
table from the trial table and drops any participant with a missing cell.

**`split_half(df, metric, seed, ...)`**: the trials in each participant ×
condition cell are split randomly into two halves (10 trials → 5 + 5),
giving two separate tables.

**`split_half_stats(df, metric, n_rep=200, sign=-1, seed=0, ...)`**: repeats
the split 200 times and returns four numbers:

| Column | What it measures |
|---|---|
| `genel_seviye_r` | does the person's mean over the five conditions agree between halves (Pearson) |
| `kosul_siralamasi_rho` | does the person's ranking of conditions agree between halves (Spearman per person, averaged) |
| `ayni_en_iyi_pct` | does the same condition come out "best" in both halves; chance is 20% (5 conditions) |
| `tanimsiz_pct` | share of cases where Spearman is undefined because all five values in a half are identical |

`sign` only affects `ayni_en_iyi_pct` (−1: lower is better). For measures
with no defined "good" direction (median frequency, entropy) that column is
meaningless.

## 3. Code reference

| Function | Defaults |
|---|---|
| `decompose` | none |
| `cell_table` | `index="participant_id"`, `col="noise_level_id"`, `cond=COND_DEFAULT` |
| `split_half` | same |
| `split_half_stats` | `n_rep=200`, `seed=0` |

`COND_DEFAULT = ["no_noise", "N1", "N2", "N3", "N4"]`. The defaults are for
the noise study. If used in another design (e.g. gravity steps in GAP), `col`
and `cond` must be passed explicitly.

## 4. Evidence: what it gave in both pilots

| | Pilot 1 (n = 12) | Pilot 2 (n = 10) |
|---|---|---|
| Person share | 89.4–96.8% | 95.6–96.8% |
| Condition share | 0.7–4.0% | 0.1–0.2% |
| ICC | 0.91–0.97 | 0.95–0.96 |
| Split-half overall level r | 0.97–0.99 | 0.97–0.99 |
| Split-half condition ranking rho | −0.02 … 0.15 | −0.17 … −0.08 |
| Same "best" rate (chance 20%) | 19–35% | 15–24% |

Ranges are over the three decision metrics (mean |θ|, stabilization time,
angle-caused falls).

The reading is the same in both pilots: the measurement separates people from
each other very reliably, but cannot separate one person's conditions. The
condition effect is smaller than trial-to-trial fluctuation. Numbers are
from the saved output of both pilots' NB92.

## 5. What it feeds

| Where | Status |
|---|---|
| pilot1 and pilot2 `92_varyans_ayrisimi.ipynb` | **Do not import** the module; they keep their own copy of the functions. The pilot notebooks are frozen (CLAUDE.md), so the copy was left alone. The module's defaults equal NB92's, so results do not change |
| pilot1 `91_control_variability.ipynb` | Does not use the module; has no reliability section |
| pilot2 `91_control_variability.ipynb` | Imports `decompose`, `cell_table`, `split_half_stats` |
| `Pilot_Noise/Pilot1_Results_Summary.md`, `Pilot2_Results_Summary.md` | Variance and reliability sections |
| `GAP/02_Modelling_Plan.md` §E | "Reliability gate": before E runs, the split-half reliability of both measures will be computed. This module is a candidate, but the split-half unit for GAP (which trials get split) is not defined yet |
