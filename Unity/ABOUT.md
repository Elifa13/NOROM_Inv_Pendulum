# Unity

The Unity project that runs the experiment will go here. **Empty for now**:
the project is with the experiment team, not in this repo.

The analysis side connects to Unity only through the data it produces.
Recording format requests go to the team in separate documents:
[../Documentation/Pilot_Noise/Recording_Requests.md](../Documentation/Pilot_Noise/Recording_Requests.md)
(noise study) and [../Documentation/GAP/01_Recording_Requests.md](../Documentation/GAP/01_Recording_Requests.md) (GAP).

## Build information known from the data

| | |
|---|---|
| Unity version | 6000.3.11f1 (same for all 12 pilot1 participants) |
| Sampling | FixedUpdate, 60 Hz (`fixed_delta_time_s` = 1/60) |
| Noise | Full-screen uniform pixel noise behind the scene, mid-grey ± σ, element size 4 px. Refresh is fixed at 60 Hz in the code (the metadata's "refreshed every display frame" is incomplete; see below) |
| Trial | 20 s active + 1 s reset, 3 practice + 50 measurement |

The physics model is not written in the metadata; it was inferred from the
data and validated (see
[../Documentation/Setup/02_Physics_and_T0.md](../Documentation/Setup/02_Physics_and_T0.md)).
Standard cart-pole, uniform rod, RK4, Δt = 1/60. The dynamics use the
**half** pole length (0.5 m).

## Noise stimulus, verified from the Unity source

Checked on 2026-09-14 in the Unity project, which lives outside this repo
(`C:\Users\elifa\Documents\GitHub\PendulumExp`), files
`Assets/PendulumExp/Shaders/UniformNoise.shader` and
`Assets/PendulumExp/Scripts/Runtime/UniformNoiseBackground.cs`.

The shader's fragment:

```
float u = hash((uint)cell.x, (uint)cell.y, (uint)_Seed);   // uniform [0,1]
float v = 0.5 + _Amplitude * (2.0 * u - 1.0);              // mid-grey ± A
```

- **The noise is uniform, not Gaussian.** Pixel values are uniformly
  distributed in [0.5 − A, 0.5 + A].
- **"σ" is a half-width, not a standard deviation.** `_Amplitude` = A. The
  standard deviation of a uniform ±A distribution is A/√3 ≈ 0.577·A (A = 0.02 →
  SD ≈ 0.0115). The column and config name `noise_sigma` is kept for
  compatibility, but a report or paper must not call it a Gaussian SD.
- **Pilot 1 ladder 0 / 0.02 / 0.05 / 0.08 / 0.25.** The tooltip of
  `UniformNoiseBackground.noisePercent` says "Pilot conditions: 0/2/5/8/25",
  and `_Amplitude = noisePercent / 100`. Code, data and metadata agree.
- **Fixed 60 Hz refresh**, independent of frame rate (even with vsync at
  144 fps). The metadata says "refreshed every display frame"; the code limits
  it to 60 Hz.
- **Background only.** Noise is a full-screen background behind the scene; it
  is not added to the cart or pole.
- **Equal mean luminance across conditions.** The background is the same mid
  grey in every condition (code comment: otherwise brightness, not noise,
  would be measured). Conditions differ only in noise amplitude.
- The 4 px element size is linked to Treviño in the code (comment: "~0.04
  visual degrees reference", "Treviño adaptation").
- Values are generated in sRGB (gun value) space and converted with
  GammaToLinearSpace in linear colour space.

## Recording behaviours that affect the analysis

Details and rationale in `Documentation/Pilot_Noise/Recording_Requests.md`; here only as warnings:

- In pilot1 `randomizationSeed` was fixed at 12345: all participants got the
  same condition order, the same noise pattern and the same initial-angle
  sequence. Fixed before pilot2. `config.randomizationSeed` in the metadata
  still says 12345; the effective seed is in the `effective_randomization_seed` field
- On reset rows `applied_force_n` is forced to zero but `input_applied` keeps
  its last value → produces fake zero crossings
- Velocities are not reset on reset
- `config.participantId` is never updated; it says "P001" everywhere
