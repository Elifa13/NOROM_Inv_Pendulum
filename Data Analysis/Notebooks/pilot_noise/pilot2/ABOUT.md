# Notebooks / pilot2

A copy of the pilot1 chain (`../pilot1/`) for the **pilot2** data. 10
participants (P001–P010), 2–3 September 2026 and P010 on 8 September 2026,
noise σ 0 / .005 / .010 / .015 / .020.

The only structural difference is `DATASET = "pilot2"` in the first cell. The
logic is still under `../../../src/`; no module was duplicated. The analysis
code reads sigma from the data, and the condition labels are the same five
names in both sets.

| # | Notebook | Status |
|---|---|---|
| 01 | `01_load_qc.ipynb` | ran: 10 sessions, 530 trials, QC FAIL 0 |
| 02 | `02_build.ipynb` | ran: 1,490 episodes, 16,443 regime runs, T₀ validated |
| 03 | `03_performance.ipynb` | ran: 500 measurement trials, 50 cells |
| 04 | `04_control.ipynb` | ran: zero crossing −45.8 ms, no condition effect |
| 06 | `06_noise_decision.ipynb` | ran: all tests null |
| 91 | `91_control_variability.ipynb` | ran: no condition effect |
| 92 | `92_varyans_ayrisimi.ipynb` | ran: condition share 0.1–0.2% |
| 93 | `93_ogrenme_ve_varyans.ipynb` | ran: learning present, independent of condition |

90 (presentation) was not copied.

**Two code-level differences** (not in the pilot1 copy):

- In NB04, the outlier-person check for the learning shift. In pilot1 the
  list was hard-coded as `["P007", "P012"]`; here the two people whose mean
  zero crossing deviates most from the median are chosen from the data (P002
  and P001 in pilot2).
- In NB91, a measure-reliability section (ICC and split-half). The functions
  are imported from `src/reliability.py`; record in
  `Documentation/Setup/06_Reliability.md`. (NB91's markdown still says
  "12 scores" in one place, left over from pilot1.)

Interpretation of results: `Documentation/Pilot_Noise/Pilot2_Results_Summary.md` (from repo root).
Method rationale (same for both sets): `Documentation/Setup/` (from repo root).

**Warning.** Pilot1 and pilot2 participant ids collide (P001… in both) but
they are different people; the condition labels are the same too but the
sigmas differ. The two sets' tables are never merged anywhere.
