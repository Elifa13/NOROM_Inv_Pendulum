# Method records

This folder answers "what did we compute and how". The goal: months later,
when someone looks at a number, it is written down where it came from, which
decision made it so, and which result it feeds.

## Rule

If a metric feeds a decision, it goes here. Every record contains:

1. **Definition**: formula or procedure, clear enough to leave no ambiguity
2. **Code reference**: which file, which function
3. **Decision**: which options existed, which was chosen and why
4. **Evidence**: the number that supports the choice, measured from the data
5. **What it feeds**: which notebook, which result

Anything not taken as-is from the literature is also marked: why it could not
be taken as-is, and what replaced it.

## Contents

| File | Scope | Notebook |
|---|---|---|
| [01_Data_Processing.md](01_Data_Processing.md) | Source, loading, QC rules, analysis mask | NB01 |
| [02_Physics_and_T0.md](02_Physics_and_T0.md) | Cart-pole model, its validation, T₀ | NB02 |
| [03_State_Action_Episode.md](03_State_Action_Episode.md) | Park state/action, sign convention, episode and regime run | NB02 |
| [04_Performance_Metrics.md](04_Performance_Metrics.md) | Trial metrics, choice of metric set | NB03 |
| [05_Action_Timing.md](05_Action_Timing.md) | Ludolph's event-triggered averaging; transfer decisions, feasibility and NB04 results | NB04 |
| [06_Reliability.md](06_Reliability.md) | Variance decomposition, ICC, split-half reliability (`src/reliability.py`) | NB92, pilot2 NB91 |

## Related documents

- [../Analysis_Log.md](../Analysis_Log.md): dated analysis log, what was decided when
- [../Pilot_Noise/Decision_Statistics.md](../Pilot_Noise/Decision_Statistics.md): decision statistics of the noise study (used to live here as 06)
- [../Pilot_Noise/Pilot1_Results_Summary.md](../Pilot_Noise/Pilot1_Results_Summary.md), [../Pilot_Noise/Pilot2_Results_Summary.md](../Pilot_Noise/Pilot2_Results_Summary.md): findings of both pilots
- [../Pilot_Noise/Recording_Requests.md](../Pilot_Noise/Recording_Requests.md): recording requests sent to the Unity team during the noise study
- [../GAP/01_Recording_Requests.md](../GAP/01_Recording_Requests.md): recording requests for GAP
- `../../CLAUDE.md`: working context and current numbers; a complement to this folder, not a summary of it
