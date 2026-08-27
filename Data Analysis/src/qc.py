"""Kalite kontrol: yapisal butunluk, zaman, sinyal, trial bayraklari."""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# 2. Yapisal butunluk
# ---------------------------------------------------------------------------


def check_structural_integrity(
    df_trials: pd.DataFrame,
    metadata: dict[str, dict],
    config: dict,
) -> list[dict]:
    """Trial sayilari, kosul dengesi, metadata alanlari.

    Doner: [{participant_id, check, status, detail}, ...]
    """
    exp = config["experiment"]
    issues: list[dict] = []

    for pid in df_trials["participant_id"].unique():
        pt = df_trials[df_trials["participant_id"] == pid]

        # -- trial sayilari --
        n_prac = int((pt["practice"] == 1).sum())
        n_meas = int((pt["practice"] == 0).sum())

        if n_prac != exp["practice_trials"]:
            issues.append(
                {
                    "participant_id": pid,
                    "check": "practice_count",
                    "status": "WARN",
                    "detail": f"beklenen {exp['practice_trials']}, bulunan {n_prac}",
                }
            )
        if n_meas != exp["measurement_trials"]:
            issues.append(
                {
                    "participant_id": pid,
                    "check": "measurement_count",
                    "status": "WARN",
                    "detail": f"beklenen {exp['measurement_trials']}, bulunan {n_meas}",
                }
            )

        # -- kosul dengesi (her turda 5 kosul x 1) --
        meas = pt[pt["practice"] == 0]
        expected_conds = set(exp["conditions"])
        for r in sorted(meas["round_index"].unique()):
            found = set(meas[meas["round_index"] == r]["noise_level_id"])
            if found != expected_conds:
                missing = expected_conds - found
                extra = found - expected_conds
                parts = []
                if missing:
                    parts.append(f"eksik {missing}")
                if extra:
                    parts.append(f"fazla {extra}")
                issues.append(
                    {
                        "participant_id": pid,
                        "check": f"balance_round_{r}",
                        "status": "WARN",
                        "detail": "; ".join(parts),
                    }
                )

        # -- sample_count tutarliligi --
        expected_samples = exp["samples_per_trial"]
        bad = pt[pt["sample_count"] != expected_samples]
        if len(bad) > 0:
            issues.append(
                {
                    "participant_id": pid,
                    "check": "sample_count",
                    "status": "WARN",
                    "detail": (
                        f"{len(bad)} trial'da sample_count != {expected_samples}"
                    ),
                }
            )

    # -- metadata alan kontrolleri --
    for key, meta in metadata.items():
        pid = meta.get("participant_id", key.split("/")[0])
        for field in config.get("metadata_required_fields", []):
            if field not in meta:
                issues.append(
                    {
                        "participant_id": pid,
                        "check": f"meta_{field}",
                        "status": "WARN",
                        "detail": f"alan eksik: {field}",
                    }
                )

    return issues


# ---------------------------------------------------------------------------
# 3. Zaman ve ornekleme
# ---------------------------------------------------------------------------


def check_timing(
    df_samples: pd.DataFrame,
    config: dict,
) -> pd.DataFrame:
    """Trial basina zaman/ornekleme kalitesi.

    Doner: participant_id, trial_id, dt_mean, dt_std, dt_max_dev,
           has_time_reversal, has_gap, has_dup_index, has_skip_index,
           nan_count, angle_out_of_range
    """
    expected_dt = 1.0 / config["experiment"]["sampling_rate_hz"]
    dt_tol = config["qc"]["dt_tolerance"]

    rows: list[dict] = []
    key_cols = [
        "pole_angle_deg",
        "pole_angular_velocity_deg_s",
        "cart_position_m",
        "cart_velocity_m_s",
        "input_raw",
        "input_applied",
        "applied_force_n",
    ]

    for (pid, tid), g in df_samples.groupby(["participant_id", "trial_id"]):
        t = g["t_trial_s"].values
        dt = np.diff(t)
        si = g["sample_index"].values
        si_diff = np.diff(si)

        rows.append(
            {
                "participant_id": pid,
                "trial_id": tid,
                "dt_mean": float(np.mean(dt)) if len(dt) else np.nan,
                "dt_std": float(np.std(dt)) if len(dt) else np.nan,
                "dt_max_dev": (
                    float(np.max(np.abs(dt - expected_dt)))
                    if len(dt)
                    else np.nan
                ),
                "has_time_reversal": bool(np.any(dt <= 0)) if len(dt) else False,
                "has_gap": (
                    bool(np.any(dt > 2 * expected_dt + dt_tol))
                    if len(dt)
                    else False
                ),
                "has_dup_index": bool(np.any(si_diff == 0)),
                "has_skip_index": bool(np.any(si_diff > 1)),
                "nan_count": int(g[key_cols].isna().sum().sum()),
                "angle_out_of_range": int(
                    ((g["pole_angle_deg"] < -180) | (g["pole_angle_deg"] > 180)).sum()
                ),
            }
        )

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 4. Sinyal akil sagligi
# ---------------------------------------------------------------------------


def _corr_with_derivative(
    values: np.ndarray,
    recorded: np.ndarray,
    dt: float,
) -> float:
    if len(values) < 3:
        return np.nan
    numerical = np.gradient(values, dt)
    mask = ~(np.isnan(numerical) | np.isnan(recorded))
    if mask.sum() < 3:
        return np.nan
    return float(np.corrcoef(recorded[mask], numerical[mask])[0, 1])


def check_signals(
    df_samples: pd.DataFrame,
    config: dict,
) -> pd.DataFrame:
    """Trial basina sinyal tutarliligi.

    Kontroller:
      - cart velocity vs d(position)/dt korelasyonu
      - angular velocity vs d(angle)/dt korelasyonu
      - applied_force_n == input_applied * max_force_n (active phase)
      - phase=="active" <=> is_resetting==0
    """
    max_force = config["physics"]["max_force_n"]
    rows: list[dict] = []

    for (pid, tid), g in df_samples.groupby(["participant_id", "trial_id"]):
        g = g.sort_values("sample_index")
        dt_val = float(g["fixed_delta_time_s"].iloc[0])

        cart_corr = _corr_with_derivative(
            g["cart_position_m"].values,
            g["cart_velocity_m_s"].values,
            dt_val,
        )
        omega_corr = _corr_with_derivative(
            g["pole_angle_deg"].values,
            g["pole_angular_velocity_deg_s"].values,
            dt_val,
        )

        # force tutarliligi (sadece active phase)
        active = g[g["phase"] == "active"]
        if len(active) > 0:
            diff = (
                active["applied_force_n"]
                - active["input_applied"] * max_force
            ).abs()
            force_ok = bool(diff.max() < 0.01)
        else:
            force_ok = True

        # phase <-> is_resetting
        phase_ok = bool(
            ((g["phase"] == "active") == (g["is_resetting"] == 0)).all()
        )

        rows.append(
            {
                "participant_id": pid,
                "trial_id": tid,
                "cart_velocity_corr": cart_corr,
                "omega_velocity_corr": omega_corr,
                "force_input_consistent": force_ok,
                "phase_reset_consistent": phase_ok,
            }
        )

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 5. Trial gecerliligi
# ---------------------------------------------------------------------------


def flag_trials(
    df_trials: pd.DataFrame,
    df_samples: pd.DataFrame,
    config: dict,
) -> pd.DataFrame:
    """qc_pass ve qc_flags kolonlarini ekler.

    Kurallar:
      - dead_input: active phase'de max(|input_raw|) == 0
      - min_fps: config'te null degilse, min_fps < esik
    """
    qc = config["qc"]
    flags: list[dict] = []

    # -- dead input --
    threshold = qc.get("dead_input_threshold")
    if threshold is not None:
        active = df_samples[df_samples["phase"] == "active"]
        if len(active) > 0:
            max_inp = active.groupby(["participant_id", "trial_id"])[
                "input_raw"
            ].agg(lambda x: x.abs().max())
            for (pid, tid), val in max_inp.items():
                if val <= threshold:
                    flags.append(
                        {
                            "participant_id": pid,
                            "trial_id": tid,
                            "flag": "dead_input",
                        }
                    )

    # -- min fps --
    fps_limit = qc.get("min_fps")
    if fps_limit is not None and "min_fps" in df_trials.columns:
        bad_fps = df_trials[df_trials["min_fps"] < fps_limit]
        for _, row in bad_fps.iterrows():
            flags.append(
                {
                    "participant_id": row["participant_id"],
                    "trial_id": row["trial_id"],
                    "flag": "low_fps",
                }
            )

    # birlestir
    df = df_trials.copy()
    if flags:
        fdf = (
            pd.DataFrame(flags)
            .groupby(["participant_id", "trial_id"])["flag"]
            .agg("|".join)
            .reset_index()
            .rename(columns={"flag": "qc_flags"})
        )
        df = df.merge(fdf, on=["participant_id", "trial_id"], how="left")
    else:
        df["qc_flags"] = ""

    df["qc_flags"] = df["qc_flags"].fillna("")
    df["qc_pass"] = df["qc_flags"] == ""
    return df


# ---------------------------------------------------------------------------
# 6. Sample maskesi
# ---------------------------------------------------------------------------


def add_analysis_mask(
    df_samples: pd.DataFrame,
    df_trials: pd.DataFrame,
) -> pd.DataFrame:
    """analysis_include kolonu ekler.

    Maske: phase=="active" & practice==0 & qc_pass & window_focused==1
    """
    df = df_samples.copy()

    qc_map = (
        df_trials[["participant_id", "trial_id", "qc_pass"]]
        .rename(columns={"qc_pass": "_qc"})
    )
    df = df.merge(qc_map, on=["participant_id", "trial_id"], how="left")
    df["_qc"] = df["_qc"].fillna(False)

    df["analysis_include"] = (
        (df["phase"] == "active")
        & (df["practice"] == 0)
        & df["_qc"]
        & (df["window_focused"] == 1)
    )
    df.drop(columns=["_qc"], inplace=True)
    return df


# ---------------------------------------------------------------------------
# 7. Format regresyon
# ---------------------------------------------------------------------------


def _collect_keys(obj: dict) -> set[str]:
    """Dict'in tum anahtar adlarini (ic ice dahil) toplar."""
    keys: set[str] = set()
    for k, v in obj.items():
        keys.add(k)
        if isinstance(v, dict):
            keys.update(_collect_keys(v))
    return keys


def check_format_regression(
    metadata: dict[str, dict],
    config: dict,
) -> list[dict]:
    """Veri_Kayit_Istekleri.md'deki istenen alanlarin hangisi mevcut."""
    requested = config.get("metadata_requested_fields", [])
    if not metadata:
        return []

    all_keys: set[str] = set()
    for meta in metadata.values():
        all_keys.update(_collect_keys(meta))

    return [{"field": f, "present": f in all_keys} for f in requested]
