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
            # Pilot 2'den itibaren metadata'da effective_randomization_seed
            # var: config.randomizationSeed sabit kalsa da RNG oturum basina
            # yeniden tohumlaniyor. Varsa etkili olan odur.
            seed = meta.get("effective_randomization_seed")
            if seed is None:
                seed = meta.get("config", {}).get("randomizationSeed")
            if seed is not None:
                seeds.setdefault(seed, []).append(pid)

        for order, pids in orders.items():
            if len(pids) > 1:
                issues.append({
                    "participant_id": ", ".join(sorted(pids)),
                    "check": "shared_condition_order",
                    "status": "WARN",
                    "detail": f"{len(pids)} katilimci ayni kosul sirasini paylasiyor",
                })

        for seed, pids in seeds.items():
            if len(pids) > 1:
                issues.append({
                    "participant_id": ", ".join(sorted(pids)),
                    "check": "shared_randomization_seed",
                    "status": "WARN",
                    "detail": f"etkili seed={seed}, {len(pids)} katilimcida ayni",
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


def _first_active_angles(df_samples):
    """Her trial'in ilk active ornegindeki pole acisi."""
    a = df_samples[df_samples["phase"] == "active"]
    if a.empty:
        return pd.DataFrame()
    a = a.sort_values(["participant_id", "trial_id", "sample_index"])
    return (
        a.groupby(["participant_id", "trial_id"])["pole_angle_deg"]
        .first()
        .reset_index()
    )


def _angle_draws(df_samples):
    """Katilimci basina cizilen tum baslangic acilari, kronolojik sirada.

    Her trial'in basinda bir aci cekiliyor, trial ici her dususten sonra
    bir tane daha. Kayittaki deger cekilisten bir fizik adimi sonrasi,
    o yuzden karsilastirmalar toleransli yapilir.
    """
    out = {}
    for pid, gp in df_samples.groupby("participant_id"):
        vals = []
        for tid in sorted(gp["trial_id"].unique()):
            g = gp[gp["trial_id"] == tid].sort_values("sample_index")
            a = g[g["phase"] == "active"]
            if len(a) == 0:
                continue
            si = a["sample_index"].values
            starts = np.concatenate(([0], np.where(np.diff(si) != 1)[0] + 1))
            vals.extend(a["pole_angle_deg"].values[starts])
        out[pid] = np.asarray(vals, dtype=float)
    return out


def _best_offset(a, b, tol, min_overlap):
    """b dizisinin a'ya gore en iyi kaymasi (start_b = start_a + offset).

    Kapsama degil kismi ortusme aranir: offset negatif de olabilir, yani
    b, a'dan once baslamis olabilir. Aday offsetler once ortak degerler
    uzerinden bulunur, sonra dogrulanir; tum kaymalari taramaktan hizli.
    """
    cands = set()
    for j in range(min(5, len(b))):
        for i in np.where(np.abs(a - b[j]) < tol)[0]:
            cands.add(int(i) - j)
    for i in range(min(5, len(a))):
        for j in np.where(np.abs(b - a[i]) < tol)[0]:
            cands.add(i - int(j))

    best_rate, best_off = 0.0, None
    for off in cands:
        ia = max(0, off)
        ib = max(0, -off)
        n = min(len(a) - ia, len(b) - ib)
        if n < min_overlap:
            continue
        rate = float(np.mean(np.abs(a[ia:ia + n] - b[ib:ib + n]) < tol))
        if rate > best_rate:
            best_rate, best_off = rate, off
    return best_rate, best_off


def check_angle_stream(df_samples, config):
    """Baslangic acilari ortak bir RNG dizisinden mi geliyor.

    Seed sabitse tek bir aci listesi uretilir ve her katilimci ondan okur.
    Imlec davranisa gore ilerledigi icin (her dusus bir cekilis tuketir)
    aciar disaridan bagimsizmis gibi gorunur.

    Her katilimci ciftinde "b, a'nin icinde hangi kaydirmada oturuyor"
    aranir; eslesen ciftler birlestirilip her katilimciya ortak listede
    bir baslangic pozisyonu atanir.

    Doner: DataFrame (participant_id, n_draws, stream_group,
                      start_offset, match_rate)
    """
    if df_samples.empty:
        return pd.DataFrame()

    qc = config.get("qc", {})
    tol = qc.get("angle_stream_tolerance_deg", 0.3)
    min_overlap = qc.get("angle_stream_min_overlap", 30)
    hit = qc.get("angle_stream_match_rate", 0.9)

    draws = {k: v for k, v in _angle_draws(df_samples).items() if len(v) > 0}
    if len(draws) < 2:
        return pd.DataFrame()

    pids = sorted(draws, key=lambda k: -len(draws[k]))

    # a -> b kenari: start_b = start_a + off (off negatif olabilir)
    edges = {}
    rates = {p_: np.nan for p_ in pids}
    for ia, a in enumerate(pids):
        for b in pids[ia + 1:]:
            rate, off = _best_offset(draws[a], draws[b], tol, min_overlap)
            if rate >= hit and off is not None:
                edges.setdefault(a, []).append((b, off))
                edges.setdefault(b, []).append((a, -off))
                for x in (a, b):
                    rates[x] = rate if np.isnan(rates[x]) else max(rates[x], rate)

    # bagli bilesenler + ortak listede baslangic pozisyonu
    start = {}
    group = {}
    gid = 0
    for root in pids:
        if root in start:
            continue
        gid += 1
        start[root], group[root] = 0, gid
        stack = [root]
        while stack:
            a = stack.pop()
            for b, off in edges.get(a, []):
                pos = start[a] + off
                if b not in start:
                    start[b], group[b] = pos, gid
                    stack.append(b)

    # pozisyonlari grup icinde 0'dan baslat
    base = {}
    for p_ in start:
        g = group[p_]
        base[g] = min(base.get(g, start[p_]), start[p_])

    rows = []
    for p_ in sorted(draws):
        rows.append({
            "participant_id": p_,
            "n_draws": len(draws[p_]),
            "stream_group": group.get(p_),
            "start_offset": start.get(p_, 0) - base.get(group.get(p_), 0),
            "match_rate": (
                np.nan if np.isnan(rates.get(p_, np.nan))
                else round(rates[p_], 3)
            ),
        })
    return pd.DataFrame(rows)


def check_randomization(df_trials, df_samples, metadata, config):
    """Randomizasyonu metadata'ya bakmadan veriden dogrular.

    metadata'daki condition_order bir iddia; burada trial_summary ve
    timeseries'ten okunan gercek diziyle karsilastirilir, sonra
    katilimcilar arasi ozdeslik olculur.

    Doner: dict
        metadata_vs_data    metadata condition_order trial_summary ile uyusuyor mu
        across_participants katilimcilar arasi ozdeslik ozeti
        position_table      kosul x tur ici pozisyon sayimi (betimleyici)
        trial_order_table   kosul x trial_order (ogrenme/yorgunluk dengesi)
    """
    out = {
        "metadata_vs_data": pd.DataFrame(),
        "across_participants": pd.DataFrame(),
        "position_table": pd.DataFrame(),
        "trial_order_table": pd.DataFrame(),
        "initial_angle_balance": pd.DataFrame(),
        "initial_angle_effect": pd.Series(dtype=float),
    }
    if df_trials.empty:
        return out

    # --- metadata iddiasi vs trial_summary gercegi ---
    # trial_order practice triallarda 0'a esit (uc trial da 0), bu yuzden
    # siralama trial_id uzerinden yapilir.
    rows = []
    for key, meta in metadata.items():
        pid = meta.get("participant_id", key.split("/")[0])
        claimed = [c.split(":")[-1] for c in meta.get("condition_order", [])]
        actual = list(
            df_trials[df_trials["participant_id"] == pid]
            .sort_values("trial_id")["noise_level_id"]
        )
        if not claimed:
            rows.append({
                "participant_id": pid, "n_metadata": 0, "n_data": len(actual),
                "match": False, "detail": "condition_order metadata'da yok",
            })
            continue
        same_len = len(claimed) == len(actual)
        n_diff = (
            sum(c != a for c, a in zip(claimed, actual)) if same_len else -1
        )
        rows.append({
            "participant_id": pid,
            "n_metadata": len(claimed),
            "n_data": len(actual),
            "match": bool(same_len and n_diff == 0),
            "detail": "" if same_len else "uzunluklar farkli",
        })
    out["metadata_vs_data"] = pd.DataFrame(rows)

    meas = df_trials[df_trials["practice"] == 0]
    if meas.empty:
        return out

    pids = sorted(meas["participant_id"].unique())
    n_pid = len(pids)

    def _seq(pid, col):
        return tuple(meas[meas["participant_id"] == pid].sort_values("trial_order")[col])

    checks = [
        ("kosul sirasi", {_seq(p, "noise_level_id") for p in pids}),
        ("noise_seed dizisi", {_seq(p, "noise_seed") for p in pids}),
    ]

    angles = _first_active_angles(df_samples)
    if not angles.empty and n_pid > 1:
        piv = angles.pivot(
            index="trial_id", columns="participant_id", values="pole_angle_deg"
        )
        piv = piv.dropna()
        n_same = int((piv.nunique(axis=1) == 1).sum()) if len(piv) else 0
        angle_detail = f"{n_same}/{len(piv)} trial'da tum katilimcilarda ayni"
        angle_identical = bool(len(piv) > 0 and n_same == len(piv))
    else:
        angle_detail = "hesaplanamadi"
        angle_identical = False

    summary = [
        {
            "olcut": name,
            "farkli_dizi_sayisi": len(distinct),
            "tum_katilimcilarda_ozdes": len(distinct) == 1,
            "detay": f"{n_pid} katilimci",
        }
        for name, distinct in checks
    ]
    summary.append({
        "olcut": "baslangic acisi",
        "farkli_dizi_sayisi": np.nan,
        "tum_katilimcilarda_ozdes": angle_identical,
        "detay": angle_detail,
    })
    out["across_participants"] = pd.DataFrame(summary)

    # --- betimleyici tablolar ---
    # Tur ici pozisyon dagilimi. Bu bir kusur testi DEGIL: tur sayisi az,
    # hucre basina beklenen sayi dusuk, sapmalar tek bir cekiliste sansa girer.
    # Katilimcilar ayni diziyi paylasiyorsa havuzlamak sayilari n kati
    # gosterir; o durumda tek katilimci uzerinden hesaplanir.
    order_identical = len({_seq(p_, "noise_level_id") for p_ in pids}) == 1
    pos_src = meas[meas["participant_id"] == pids[0]] if order_identical else meas
    pos = pd.crosstab(pos_src["noise_level_id"], pos_src["condition_order_in_round"])
    pos.columns = [f"poz_{c}" for c in pos.columns]
    pos.attrs["basis"] = (
        f"tek katilimci ({pids[0]}); {n_pid} katilimcinin dizisi ozdes"
        if order_identical else f"{n_pid} katilimci havuzlanmis"
    )
    out["position_table"] = pos

    out["trial_order_table"] = (
        meas.groupby("noise_level_id")["trial_order"]
        .agg(["mean", "min", "max"])
        .round(1)
    )

    # Baslangic acisi kosullar arasinda dengeli mi ve sonucu etkiliyor mu.
    # Asil soru bu: aci listesi ortak olsa bile kosul karsilastirmasini
    # ancak kosullar arasi dengesizlik + sonuca etki birlikte bozar.
    ang = _first_active_angles(df_samples)
    if not ang.empty:
        d = meas.merge(ang, on=["participant_id", "trial_id"], how="inner")
        if not d.empty:
            d = d.assign(abs_init=d["pole_angle_deg"].abs())
            bal = (
                d.groupby("noise_level_id")["abs_init"]
                .agg(["mean", "std", "count"])
                .round(3)
            )
            bal.attrs["spread"] = float(bal["mean"].max() - bal["mean"].min())
            bal.attrs["within_sd"] = float(d["abs_init"].std())
            out["initial_angle_balance"] = bal

            corr = {}
            for m in ["fall_count", "mean_abs_pole_angle_deg",
                      "rms_pole_angle_deg", "within_bounds_time_s"]:
                if m in d.columns:
                    corr[m] = round(float(d["abs_init"].corr(d[m])), 3)
            out["initial_angle_effect"] = pd.Series(corr, name="corr_abs_init")

    return out


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
