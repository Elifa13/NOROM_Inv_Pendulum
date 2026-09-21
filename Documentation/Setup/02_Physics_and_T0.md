# 02: Physics model and T₀

**Notebook:** `Data Analysis/Notebooks/pilot_noise/<dataset>/02_build.ipynb` §1, §2b
**Code:** `src/physics.py`
**Config:** `config.yaml` → `physics`, `t0`

---

## 1. Why we need a physics model

For T₀. T₀ = "how many seconds the pole would take to reach the fall limit if
the participant did nothing". It cannot be measured, it has to be simulated,
and simulating it requires knowing the dynamics Unity uses. If the model is
wrong, T₀ is wrong, and everything derived from T/T₀ collapses.

The model is not written in the metadata; it was inferred from the data and
validated.

## 2. Model

Standard cart-pole (uniform rod, 4/3 inertia factor):

```
temp = (F + m_p · l · ω² · sinθ) / (m_c + m_p)
θ''  = (g · sinθ − cosθ · temp) / (l · (4/3 − m_p · cos²θ / (m_c + m_p)))
x''  = temp − m_p · l · θ'' · cosθ / (m_c + m_p)
```

| Parameter | Value | Note |
|---|---|---|
| `m_c` cart mass | 0.40 kg | Ludolph |
| `m_p` pole mass | 0.08 kg | Ludolph |
| `l` | **0.5 m** | **Half-length.** The full pole is 1.0 m; the dynamics use half of it |
| `g` | 1.00 m/s² | Ludolph's starting level, constant in the pilot |
| `F` | `applied_force_n` | Same sign directly, no force delay, no damping |
| Fall limit | ±60° | Ludolph |
| Track limit | ±5 m | Ludolph |
| Integration | RK4, Δt = 1/60 s | |

The `l = 0.5` distinction matters and is easy to miss. `config.yaml` has both
`pole_length_m: 1.0` and `pole_half_length_m: 0.5`; the code uses the second.

**Deviation from Ludolph:** in Ludolph, gravity rose to 3.5 m/s² depending on
performance (gradual gravity condition). The pilot kept g at 1.0 to isolate
the noise effect. This means the pilot cannot be compared directly with
Ludolph's learning finding.

## 3. Model validation

**Method** (`physics.verify_model`): on continuous active segments, the model
predicts the angular acceleration from the measured state (θ, ω, x, v, F),
and this is compared with the observed angular acceleration. The observed
acceleration is the numerical derivative of the
`pole_angular_velocity_deg_s` column.

The segments must be continuous; a window crossing a reset boundary produces
a fake acceleration.

**Result:** 8 long segments, correlation **0.9884–0.9972**.

**But correlation alone is not enough, and this matters.** Correlation is
scale-free: it validates the *shape* of the curve, not its *magnitude*. We
reran with `l = 1.0`:

| | correlation | mean RMS error |
|---|---|---|
| `l = 0.5` | 0.9884–0.9972 | **0.189** |
| `l = 1.0` | 0.9884–0.9971 | 0.997 |

The correlation barely changes, the RMS error goes up fivefold. So what pins
down `l` is not the correlation but the RMS and the free-fall test below.
"Correlation 0.988–0.997, model validated" is an incomplete statement.

## 4. Computing T₀

**Definition:** the time from (θ₀, ω = 0), with **zero force**, until
|θ| = 60°.

With F = 0 the dynamics are closed in (θ, ω); x and v do not feed back. So
**T₀ is a function of θ₀ alone.** This makes it cacheable (`T0_for_angles`,
since the same angles repeat).

| θ₀ | 0.5° | 1° | 2° | 3° | 4° | 5° | 6° | 7° | 7.5° |
|---|---|---|---|---|---|---|---|---|---|
| T₀ | 4.23 s | 3.70 | 3.18 | 2.87 | 2.65 | 2.48 | 2.33 | 2.22 | 2.17 |

In real episodes: mean 2.93 s, range 2.17–9.68 s.

The initial angle distribution is U(−7.5°, +7.5°), same as Ludolph.

## 5. Empirical validation of T₀

**Idea:** an episode in which the participant gave no input and which ended
at the angle limit is by definition free fall. Its duration **must equal**
T₀. This single test validates the physics model, the RK4 step, the T₀
computation and the episode segmentation at once.

**Code:** `build.validate_T0_freefall`

**Result (pilot1, 12 participants):** there are 11 such episodes, and **all
11 have `duration/T₀ = 1.0000`**, maximum deviation from 1.0 of 0.0000.
Pilot2 has 2 such episodes, both 1.0000.

**"Isn't 11 too few?" Sampling logic does not apply here.** T₀ is not
estimated, it is computed deterministically from the model. This is not a
parameter estimate, it is a *test*. A wrong model does not give 1.0000: with
`l = 1.0`, T₀(7.5°) would be 3.07 s (instead of 2.17), so the ratio would come
out around 0.71 every time. Zero deviation at 11 different initial angles
cannot be chance.

**Real limitation: coverage.** These 11 episodes cover θ₀ = 1.52°–7.25°,
i.e. T₀ = 2.20–3.38 s. Across all episodes T₀ ranges 2.17–9.68 s; the upper
end (starts very close to vertical) is untested. Low risk, since the model
equation is angle-independent, but it is written down.

The whole chain (physics model, RK4 step, T₀ computation, episode
segmentation) is validated by one test.

## 5b. What T₀ is used for from here on

It is **not** used as a performance metric (§6 and
[04 §4](04_Performance_Metrics.md)). Its three remaining jobs:

1. **Validation**: the test above. Done, one-off.
2. **Difficulty variable**: since T₀ is fully a function of θ₀, it is the
   one-number summary of "how hard an angle this episode started from". The
   natural covariate when checking randomization bias.
3. **If survival analysis is done**, it enters as a covariate.

Beyond these, T₀ was scaffolding: it served to build and prove the model.

## 6. Ludolph's T/T₀ cannot be transferred as-is

**In Ludolph:** a trial **ends** at a fall. T (actual trial length) varies,
and T/T₀ means "how much better/worse than doing nothing".

**In our data:** a trial is a fixed 20 s; after a fall it resets and
continues. T is always ≈20 s, so T/T₀ = 20/T₀, i.e. **a pure function of
θ₀**. Measured: `corr(|θ₀|, trial-level T/T₀) = +0.972`. It does not measure
performance.

**The right equivalent is episode level:** each episode starts from its own
initial angle (trial start or restart after a fall) and lasts until a fall or
the end of the trial.

| Measure | corr(&#124;θ₀&#124;, measure) |
|---|---|
| Trial-level T/T₀ | +0.972 |
| Episode-level T_ep/T₀ | +0.128 |
| Episode duration (raw) | −0.078 |

For the rest of this table and **why T/T₀ is rejected at episode level too**,
see [04_Performance_Metrics.md §4](04_Performance_Metrics.md). In short:
dividing by T₀ increases contamination rather than reducing it.
