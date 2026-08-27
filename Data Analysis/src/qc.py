"""Kalite kontrol fonksiyonlari."""

import numpy as np
import pandas as pd


def check_structural_integrity(df_trials, metadata, config):
    """Trial sayilari, kosul dengesi, metadata alanlari kontrol et.

    Doner: [{participant_id, check, status, detail}, ...]
    """
    issues = []
    exp = config["experiment"]

    if df_trials.empty:
        return issues

    for pid in df_trials["participant_id"].unique():
        pt = df_trials[df_trials["participant_id"] == pid]

        n_prac = int((pt["practice"] == 1).sum())
        n_meas = int((pt["practice"] == 0).sum())

        if n_prac != exp["practice_trials"]:
            issues.append({
                "participant_id": pid,
                "check": "practice_count",
                "status": "WARN",
                "detail": f"beklenen {exp['practice_trials']}, bulunan {n_prac}",
            })

        if n_meas != exp["measurement_trials"]:
            issues.append({
                "participant_id": pid,
                "check": "measurement_count",
                "status": "WARN",
                "detail": f"beklenen {exp['measurement_trials']}, bulunan {n_meas}",
            })

        # kosul dengesi
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
                issues.append({
                    "participant_id": pid,
                    "check": f"balance_round_{r}",
                    "status": "WARN",
                    "detail": "; ".join(parts),
                })

        # sample_count
        expected_samples = exp["samples_per_trial"]
        bad = pt[pt["sample_count"] != expected_samples]
        if len(bad) > 0:
            issues.append({
                "participant_id": pid,
                "check": "sample_count",
                "status": "WARN",
                "detail": f"{len(bad)} trial'da sample_count != {expected_samples}",
            })

    # randomizasyon: katilimcilar ayni kosul sirasini paylasiyor mu
    if len(metadata) > 1:
        orders = {}
        seeds = {}
        for key, meta in metadata.items():
            pid = meta.get("participant_id", key.split("/")[0])
            order = tuple(meta.get("condition_order", []))
            if order:
                orders.setdefault(order, []).append(pid)
            seed = meta.get("config", {}).get("randomizationSeed")
            if seed is not None:
                seeds.setdefault(seed, []).append(pid)

        for order, pids in orders.items():
            if len(pids) > 1:
                issues.append({
                    "participant_id": ", ".join(sorted(pids)),
                    "check": "shared_condition_order",
                    "status": "FAIL",
                    "detail": f"{len(pids)} katilimci ayni kosul sirasini paylasiyor",
                })

        for seed, pids in seeds.items():
            if len(pids) > 1:
                issues.append({
                    "participant_id": ", ".join(sorted(pids)),
                    "check": "shared_randomization_seed",
                    "status": "FAIL",
                    "detail": f"randomizationSeed={seed}, {len(pids)} katilimcida ayni",
                })

    # metadata icindeki participantId gercek katilimci ile uyusuyor mu
    for key, meta in metadata.items():
        pid = meta.get("participant_id", key.split("/")[0])
        cfg_pid = meta.get("config", {}).get("participantId")
        if cfg_pid is not None and cfg_pid != pid:
            issues.append({
                "participant_id": pid,
                "check": "config_participant_id",
                "status": "WARN",
                "detail": f"config.participantId={cfg_pid}, klasor={pid}",
            })

    # metadata alan kontrolleri
    for key, meta in metadata.items():
        pid = meta.get("participant_id", key.split("/")[0])
        for field in config.get("metadata_required_fields", []):
            if field not in meta:
                issues.append({
                    "participant_id": pid,
                    "check": f"meta_{field}",
                    "status": "WARN",
                    "detail": f"alan eksik: {field}",
                })

    return issues


def check_timing(df_samples, config):
    """Trial basina zaman/ornekleme kalitesi.

    Doner: DataFrame (participant_id, trial_id, dt_mean, ...)
    """
    if df_samples.empty:
        return pd.DataFrame()

    expected_dt = 1.0 / config["experiment"]["sampling_rate_hz"]
    dt_tol = config["qc"]["dt_tolerance"]

    key_cols = [
        "pole_angle_deg",
        "pole_angular_velocity_deg_s",
        "cart_position_m",
        "cart_velocity_m_s",
        "input_raw",
        "input_applied",
        "applied_force_n",
    ]

    rows = []
    for (pid, tid), g in df_samples.groupby(["participant_id", "trial_id"]):
        t = g["t_trial_s"].values
        dt = np.diff(t)
        si = g["sample_index"].values
        si_diff = np.diff(si)

        has_dt = len(dt) > 0

        row = {
            "participant_id": pid,
            "trial_id": tid,
            "dt_mean": float(np.mean(dt)) if has_dt else np.nan,
            "dt_std": float(np.std(dt)) if has_dt else np.nan,
            "dt_max_dev": float(np.max(np.abs(dt - expected_dt))) if has_dt else np.nan,
            "has_time_reversal": bool(np.any(dt <= 0)) if has_dt else False,
            "has_gap": bool(np.any(dt > 2 * expected_dt + dt_tol)) if has_dt else False,
            "has_dup_index": bool(np.any(si_diff == 0)),
            "has_skip_index": bool(np.any(si_diff > 1)),
            "nan_count": int(g[key_cols].isna().sum().sum()),
            "angle_out_of_range": int(
                ((g["pole_angle_deg"] < -180) | (g["pole_angle_deg"] > 180)).sum()
            ),
        }
        rows.append(row)

    return pd.DataFrame(rows)


def _active_segments(g):
    """Trial'i kesintisiz active parcalara boler.

    Trial icinde dususten sonra 1 s'lik reset blogu var ve ardindan pole
    yeni bir baslangic acisiyla devam ediyor. phase=="active" satirlarini
    uc uca eklemek sahte sicramalar uretir; turev kontrolu bu yuzden her
    parcada ayri yapilir.
    """
    a = g[g["phase"] == "active"]
    if len(a) == 0:
        return []
    si = a["sample_index"].values
    breaks = np.where(np.diff(si) != 1)[0] + 1
    idx_groups = np.split(np.arange(len(a)), breaks)
    return [a.iloc[idx] for idx in idx_groups if len(idx) > 0]


def _corr_with_derivative(segments, pos_col, vel_col, dt):
    """Sayisal turev ile kayitli hiz arasindaki korelasyon.

    Her parcada gradient ayri hesaplanir, uc noktalar (tek yonlu fark)
    atilir, kalan ciftler havuzlanip tek korelasyon uretilir.
    """
    rec_all, num_all = [], []

    for seg in segments:
        if len(seg) < 5:
            continue
        pos = seg[pos_col].values.astype(float)
        rec = seg[vel_col].values.astype(float)
        num = np.gradient(pos, dt)
        rec_all.append(rec[1:-1])
        num_all.append(num[1:-1])

    if not rec_all:
        return np.nan

    rec = np.concatenate(rec_all)
    num = np.concatenate(num_all)
    mask = ~(np.isnan(rec) | np.isnan(num))
    if mask.sum() < 3:
        return np.nan
    if np.std(rec[mask]) == 0 or np.std(num[mask]) == 0:
        return np.nan
    return float(np.corrcoef(rec[mask], num[mask])[0, 1])


def check_signals(df_samples, config):
    """Trial basina sinyal tutarliligi.

    Doner: DataFrame (participant_id, trial_id, cart_vel_corr, ...)
    """
    if df_samples.empty:
        return pd.DataFrame()

    max_force = config["physics"]["max_force_n"]
    rows = []

    for (pid, tid), g in df_samples.groupby(["participant_id", "trial_id"]):
        g = g.sort_values("sample_index")
        dt_val = float(g["fixed_delta_time_s"].iloc[0])
        segments = _active_segments(g)

        cart_corr = _corr_with_derivative(
            segments, "cart_position_m", "cart_velocity_m_s", dt_val
        )
        omega_corr = _corr_with_derivative(
            segments, "pole_angle_deg", "pole_angular_velocity_deg_s", dt_val
        )

        # force tutarliligi (sadece active phase)
        active = g[g["phase"] == "active"]
        if len(active) > 0:
            diff = (active["applied_force_n"] - active["input_applied"] * max_force).abs()
            force_ok = bool(diff.max() < 0.01)
        else:
            force_ok = True

        # phase <-> is_resetting
        phase_reset_ok = bool(
            ((g["phase"] == "active") == (g["is_resetting"] == 0)).all()
        )

        rows.append({
            "participant_id": pid,
            "trial_id": tid,
            "n_segments": len(segments),
            "cart_vel_corr": cart_corr,
            "omega_corr": omega_corr,
            "force_ok": force_ok,
            "phase_reset_ok": phase_reset_ok,
        })

    return pd.DataFrame(rows)


def flag_trials(df_trials, df_samples, config):
    """qc_pass ve qc_flags kolonlarini ekler."""
    if df_trials.empty:
        return df_trials.copy()

    qc = config["qc"]
    flags = []

    # dead input
    threshold = qc.get("dead_input_threshold")
    if threshold is not None and not df_samples.empty:
        active = df_samples[df_samples["phase"] == "active"]
        if len(active) > 0:
            max_inp = (
                active
                .groupby(["participant_id", "trial_id"])["input_raw"]
                .agg(lambda x: x.abs().max())
            )
            for (pid, tid), val in max_inp.items():
                if val <= threshold:
                    flags.append({
                        "participant_id": pid,
                        "trial_id": tid,
                        "flag": "dead_input",
                    })

    # min fps
    fps_limit = qc.get("min_fps")
    if fps_limit is not None and "min_fps" in df_trials.columns:
        bad_fps = df_trials[df_trials["min_fps"] < fps_limit]
        for _, row in bad_fps.iterrows():
            flags.append({
                "participant_id": row["participant_id"],
                "trial_id": row["trial_id"],
                "flag": "low_fps",
            })

    # birlestir
    df = df_trials.copy()
    if flags:
        fdf = pd.DataFrame(flags)
        fdf = (
            fdf
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


def add_analysis_mask(df_samples, df_trials):
    """analysis_include kolonu ekler.

    Maske: phase=="active" & practice==0 & qc_pass & window_focused==1
    """
    if df_samples.empty:
        return df_samples.copy()

    df = df_samples.copy()

    if df_trials.empty or "qc_pass" not in df_trials.columns:
        df["analysis_include"] = False
        return df

    qc_map = df_trials[["participant_id", "trial_id", "qc_pass"]].copy()
    qc_map = qc_map.rename(columns={"qc_pass": "_qc"})
    df = df.merge(qc_map, on=["participant_id", "trial_id"], how="left")
    df["_qc"] = df["_qc"].fillna(False)

    df["analysis_include"] = (
        (df["phase"] == "active")
        & (df["practice"] == 0)
        & df["_qc"]
        & (df["window_focused"] == 1)
    )
    df = df.drop(columns=["_qc"])
    return df


def _collect_keys(obj):
    """Dict'in tum anahtar adlarini (ic ice dahil) toplar."""
    keys = set()
    for k, v in obj.items():
        keys.add(k)
        if isinstance(v, dict):
            keys.update(_collect_keys(v))
    return keys


def check_format_regression(metadata, config):
    """Istenen metadata alanlarinin hangisi mevcut."""
    requested = config.get("metadata_requested_fields", [])
    if not metadata:
        return []

    all_keys = set()
    for meta in metadata.values():
        all_keys.update(_collect_keys(meta))

    return [{"field": f, "present": f in all_keys} for f in requested]
