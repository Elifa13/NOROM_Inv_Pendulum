"""Episode / regime segmentasyonu, state ve action siniflandirmasi.

NB03 (performans) ve NB04 (kontrol mekanizmasi) ayni turetmeyi iki kere
yapmasin diye burada bir kez uretilir.

Iki ayri birim var, karistirilmamali:

  Episode     reset'ten reset'e. Bir dususten sonraki dususe kadar.
              T0 / sure analizi icin (Ludolph tarafi).
  Regime run  kuadran dizisi. theta*omega isaret degistirdiginde yeni
              run baslar. Park'in Safe / Saved / Failed rejimleri bu
              birimde tanimli. Episode basina ortalama ~8.5 run dusuyor.

Isaret notu: Park "joystick isareti theta'nin tersi = CR" diyor ama onun
VIP'inde joystick dogrudan acisal ivme veriyor. Bizim cart-pole'da kuvvet
cart'a gidiyor ve isaret ters cevriliyor. Veriden dogrulandi: F > 0 iken
ortalama d(theta)/dt = -21 deg/s, yani duzeltici kuvvet theta ile AYNI
isaretli. Asagidaki kurallar bu cevrilmis konvansiyonda yazilmistir.

Dusus sebebi iki tanedir ve ayirt edilir: pole aci limitine (+-60 deg)
varabilir, ya da cart ray limitine (+-5 m) carpabilir. Mevcut veride
906 dususun 814'u aci, 92'si ray kaynakli, ortusme yok. Ray kaynakli
dususlerin 29'u SAFE kuadraninda oluyor -- pole dikeye donerken cart
raydan cikiyor. Park'in taksonomisinde bunun karsiligi yok, o yuzden
ayri etiket (TrackLoss) verilir ve Failed sadece aci kaynakli kalir.
"""

import numpy as np
import pandas as pd

try:
    from .physics import params_from_config, T0_for_angles
except ImportError:  # dogrudan calistirma
    from physics import params_from_config, T0_for_angles

# action etiketleri
I_, CR_, A_, D_, X_ = "I", "CR", "A", "D", "X"


def _episode_bounds(active):
    """Kesintisiz active parcalarin (baslangic, bitis) indeksleri."""
    si = active["sample_index"].values
    starts = np.concatenate(([0], np.where(np.diff(si) != 1)[0] + 1))
    ends = np.concatenate((starts[1:], [len(active)]))
    return list(zip(starts, ends))


def add_state(df_samples):
    """Kuadran bilgisi ekler.

    falling  theta * omega > 0   egik ve dusecegi yone doniyor
    safe     theta * omega < 0   egik ama dikeye doniyor

    Carpim tam sifir olan ornekler (theta veya omega sifir) dejenere;
    state_defined False isaretlenir, siniflandirmada X'e duser.
    """
    if df_samples.empty:
        return df_samples.copy()

    df = df_samples.copy()
    prod = df["pole_angle_deg"].values * df["pole_angular_velocity_deg_s"].values
    df["state_defined"] = prod != 0
    df["falling"] = prod > 0
    df["quadrant"] = np.where(
        df["pole_angle_deg"] >= 0,
        np.where(df["pole_angular_velocity_deg_s"] >= 0, "Q1", "Q2"),
        np.where(df["pole_angular_velocity_deg_s"] < 0, "Q3", "Q4"),
    )
    return df


def _neutral_transients(neutral, sign_u, max_len):
    """Zit isaretli sapmalar arasindaki kisa notr dizileri isaretler.

    Park footnote: joystick soldan saga gecerken banddan hizli gecis
    inaktivite sayilmaz. Ayni isarete geri donen duraklamalar I kalir.
    """
    out = np.zeros(len(neutral), dtype=bool)
    if not max_len or max_len <= 0 or len(neutral) == 0:
        return out

    idx = np.flatnonzero(neutral)
    if len(idx) == 0:
        return out

    breaks = np.where(np.diff(idx) != 1)[0] + 1
    for grp in np.split(idx, breaks):
        b, e = grp[0], grp[-1] + 1
        if len(grp) > max_len or b == 0 or e >= len(neutral):
            continue
        if sign_u[b - 1] != 0 and sign_u[e] != 0 and sign_u[b - 1] != sign_u[e]:
            out[b:e] = True
    return out


def classify_actions(df_samples, config):
    """Ornek basina Park action sinifi ekler.

    I   notr banddaki kalici girdi
    CR  u * theta > 0            duzeltici, her kuadranda
    A   u * theta < 0, safe      dikeye donusu frenleme (anticipatory)
    D   u * theta < 0, fall      dusus yonune kuvvet (destabilizing)
    X   siniflandirilmayan: banddan gecici gecis ya da dejenere isaret
    """
    if df_samples.empty:
        return df_samples.copy()

    cfg = config.get("build", {})
    band = float(cfg.get("input_neutral_band", 0.0))
    max_len = cfg.get("neutral_transient_max_samples", 0)

    df = df_samples if "falling" in df_samples.columns else add_state(df_samples)
    df = df.copy()

    u = df["input_applied"].values
    th = df["pole_angle_deg"].values
    neutral = np.abs(u) <= band
    sign_u = np.sign(u)
    sign_u[neutral] = 0

    # gecici gecisler trial bazinda aranir, trial'lar arasinda tasmasin
    transient = np.zeros(len(df), dtype=bool)
    pos_all = np.arange(len(df))
    keys = pd.MultiIndex.from_arrays(
        [df["participant_id"].values, df["trial_id"].values]
    )
    for _, pos in pd.Series(pos_all).groupby(keys):
        p = pos.values
        p = p[np.argsort(df["sample_index"].values[p], kind="stable")]
        transient[p] = _neutral_transients(neutral[p], sign_u[p], max_len)

    corrective = (u * th) > 0
    degenerate = (~df["state_defined"].values) | (np.sign(th) == 0)

    action = np.full(len(df), X_, dtype=object)
    action[neutral & ~transient] = I_
    live = ~neutral & ~degenerate
    action[live & corrective] = CR_
    action[live & ~corrective & ~df["falling"].values] = A_
    action[live & ~corrective & df["falling"].values] = D_

    reason = np.full(len(df), "", dtype=object)
    reason[transient] = "transient_neutral"
    reason[~neutral & degenerate] = "degenerate_sign"

    df["action"] = action
    df["action_excluded_reason"] = reason
    return df


def add_episode_index(df_samples):
    """Active satirlara episode indeksi ekler (0 tabanli, trial icinde).

    Reset satirlarinda NaN kalir. NB03/NB04 sample'lari episode tablosuna
    bu kolonla birlestirir.
    """
    if df_samples.empty:
        return df_samples.copy()

    df = df_samples.copy()
    df["episode"] = np.nan

    a = df[df["phase"] == "active"].sort_values(
        ["participant_id", "trial_id", "sample_index"]
    )
    if len(a) == 0:
        return df

    new_trial = (
        (a["participant_id"] != a["participant_id"].shift())
        | (a["trial_id"] != a["trial_id"].shift())
    )
    gap = a["sample_index"].diff() != 1
    start = (new_trial | gap).astype(int)
    epi = start.groupby([a["participant_id"], a["trial_id"]]).cumsum() - 1
    df.loc[a.index, "episode"] = epi.values
    return df


def validate_T0_freefall(df_built, episodes):
    """T0'i ampirik olarak dogrular.

    Katilimcinin hic girdi vermedigi (tum ornekler I) ve aci limitiyle
    biten episode'lar tanim geregi serbest dususturler. Bu episodelarda
    gozlenen sure T0'a esit olmali. Model, RK4 adimi, T0 hesabi ve
    episode segmentasyonu zincirinin tamamini tek seferde test eder.

    Doner: DataFrame. .attrs["n"], .attrs["mean_ratio"], .attrs["max_dev"]
    """
    empty = pd.DataFrame()
    if df_built.empty or episodes.empty:
        return empty
    if "episode" not in df_built.columns or "action" not in df_built.columns:
        return empty

    a = df_built[(df_built["phase"] == "active") & df_built["episode"].notna()]
    if len(a) == 0:
        return empty

    keys = ["participant_id", "trial_id", "episode"]
    pct_i = (
        a.assign(_i=(a["action"] == I_).astype(float))
        .groupby(keys)["_i"]
        .mean()
        .mul(100.0)
        .rename("pct_I")
        .reset_index()
    )

    ep = episodes.copy()
    ep["episode"] = ep["episode"].astype(float)
    m = ep.merge(pct_i, on=keys, how="inner")
    pure = m[
        (m["pct_I"] >= 100.0)
        & m["ended_in_fall"]
        & (m["fall_cause"] == "angle")
    ].copy()

    if pure.empty:
        out = empty.copy()
        out.attrs["n"] = 0
        return out

    cols = [
        "participant_id", "trial_id", "episode", "theta0_deg",
        "omega0_deg_s", "duration_s", "T0_s", "duration_over_T0",
    ]
    out = pure[cols].reset_index(drop=True)
    out.attrs["n"] = len(out)
    out.attrs["mean_ratio"] = float(out["duration_over_T0"].mean())
    out.attrs["max_dev"] = float((out["duration_over_T0"] - 1.0).abs().max())
    return out


def segment_episodes(df_samples, config, df_trials=None):
    """Reset'ten reset'e episode tablosu.

    Doner: DataFrame - her satir bir episode. T0, baslangic acisi,
    sure, dususle mi bitti, sansurlu mu.
    """
    if df_samples.empty:
        return pd.DataFrame()

    p = params_from_config(config)
    limit = p["angle_limit_deg"]
    carry = [
        "noise_level_id", "noise_sigma", "practice", "round_index",
        "trial_order", "condition_order_in_round", "session_id",
    ]

    rows = []
    for (pid, tid), g in df_samples.groupby(["participant_id", "trial_id"]):
        g = g.sort_values("sample_index")
        active = g[g["phase"] == "active"]
        if len(active) == 0:
            continue
        dt = float(active["fixed_delta_time_s"].iloc[0])

        for k, (b, e) in enumerate(_episode_bounds(active)):
            ep = active.iloc[b:e]
            th = ep["pole_angle_deg"].values
            fall_idx = np.flatnonzero(ep["fall_event"].values == 1)
            fell = len(fall_idx) > 0
            if fell:
                cause = (
                    "angle"
                    if abs(th[fall_idx[-1]]) >= limit
                    else "track"
                )
            else:
                cause = None
            row = {
                "participant_id": pid,
                "trial_id": tid,
                "episode": k,
                "start_sample_index": int(ep["sample_index"].iloc[0]),
                "n_samples": len(ep),
                "duration_s": round(len(ep) * dt, 4),
                "theta0_deg": float(th[0]),
                "omega0_deg_s": float(ep["pole_angular_velocity_deg_s"].iloc[0]),
                "max_abs_theta_deg": float(np.abs(th).max()),
                "ended_in_fall": fell,
                "fall_cause": cause,
                "censored": bool(not fell and e == len(active)),
                "unfocused_frac": round(
                    float((ep["window_focused"] == 0).mean()), 4
                ),
            }
            for c in carry:
                if c in ep.columns:
                    row[c] = ep[c].iloc[0]
            rows.append(row)

    ep_df = pd.DataFrame(rows)
    if ep_df.empty:
        return ep_df

    ep_df["T0_s"] = T0_for_angles(ep_df["theta0_deg"].values, p).values
    ep_df["duration_over_T0"] = ep_df["duration_s"] / ep_df["T0_s"]
    ep_df["reached_limit"] = ep_df["max_abs_theta_deg"] >= limit

    if df_trials is not None and not df_trials.empty:
        cols = ["participant_id", "trial_id"]
        extra = [c for c in ("qc_pass", "qc_flags") if c in df_trials.columns]
        if extra:
            ep_df = ep_df.merge(df_trials[cols + extra], on=cols, how="left")
    return ep_df


def segment_regimes(df_samples, config):
    """Kuadran run'lari ve Park rejim etiketleri.

    Safe       safe kuadranindaki run, dikeye donuyor
    Saved      fall kuadraninda basladi, sinira varmadan kurtuldu
    Failed     aci limitine (+-60 deg) varan run. Park ile karsilastirilabilir
               olan tek "basarisiz" etiketi budur.
    TrackLoss  cart ray limitine carpmasiyla biten run. Kuadrandan bagimsiz;
               mevcut veride 140 ray dususunun 42'si safe kuadraninda
               oluyor. Park'ta karsiligi yok, Park karsilastirmalarindan
               cikarilmali.
    censored   fall kuadranindaki son run, trial bitisiyle kesildi

    Run'lar episode sinirini asmaz.
    """
    if df_samples.empty:
        return pd.DataFrame()

    p = params_from_config(config)
    limit = p["angle_limit_deg"]
    df = df_samples if "falling" in df_samples.columns else add_state(df_samples)
    has_action = "action" in df.columns

    rows = []
    for (pid, tid), g in df.groupby(["participant_id", "trial_id"]):
        g = g.sort_values("sample_index")
        active = g[g["phase"] == "active"]
        if len(active) == 0:
            continue
        dt = float(active["fixed_delta_time_s"].iloc[0])

        for k, (b, e) in enumerate(_episode_bounds(active)):
            ep = active.iloc[b:e]
            falling = ep["falling"].values
            th = ep["pole_angle_deg"].values
            fall_flag = ep["fall_event"].values == 1
            ep_fell = bool(fall_flag.any())
            cuts = np.concatenate((
                [0], np.where(np.diff(falling.astype(int)) != 0)[0] + 1, [len(ep)]
            ))

            for r in range(len(cuts) - 1):
                rb, re_ = cuts[r], cuts[r + 1]
                run = ep.iloc[rb:re_]
                is_fall = bool(falling[rb])
                peak = float(np.abs(th[rb:re_]).max())
                is_last = re_ == len(ep)

                run_fall = np.flatnonzero(fall_flag[rb:re_])
                if len(run_fall):
                    cause = (
                        "angle"
                        if abs(th[rb + run_fall[-1]]) >= limit
                        else "track"
                    )
                    regime = "Failed" if cause == "angle" else "TrackLoss"
                else:
                    cause = None
                    if not is_fall:
                        regime = "Safe"
                    elif is_last and not ep_fell:
                        regime = "censored"
                    else:
                        regime = "Saved"

                row = {
                    "participant_id": pid,
                    "trial_id": tid,
                    "episode": k,
                    "run": r,
                    "regime": regime,
                    "quadrant_type": "fall" if is_fall else "safe",
                    "ended_in_fall": bool(len(run_fall)),
                    "fall_cause": cause,
                    "n_samples": len(run),
                    "duration_s": round(len(run) * dt, 4),
                    "theta_start_deg": float(th[rb]),
                    "theta_end_deg": float(th[re_ - 1]),
                    "max_abs_theta_deg": peak,
                    "noise_level_id": run["noise_level_id"].iloc[0],
                    "practice": run["practice"].iloc[0],
                }
                if has_action:
                    vc = run["action"].value_counts()
                    for lbl in (I_, CR_, A_, D_, X_):
                        row[f"pct_{lbl}"] = round(
                            100.0 * vc.get(lbl, 0) / len(run), 2
                        )
                rows.append(row)

    return pd.DataFrame(rows)


def detect_input_events(df_samples, config):
    """GIRDI tarafinda tanimli olaylar: banddan cikis, yon degistirme, dusus.

    DIKKAT -- bunlar Ludolph'un event'leri DEGIL. Ludolph'un action timing
    analizinde olay DURUM tarafinda tanimli: pole belirli bir tamsayi aciyi
    duserken geciyor. Ikisi farkli kavram; ayrimi icin bkz.
    Documentation/Yontem/05_Action_Timing.md.

    Buradaki olaylar tanimlayici istatistik ve QC icin (dusus sayisinin
    bagimsiz dogrulanmasi dahil). Olaylar episode icinde aranir; reset
    satirlari zaten disarida oldugu icin parcalar arasi sahte zero-crossing
    olusmaz. (Reset satirlarinda applied_force_n sifira zorlanip
    input_applied son degerinde kaldigi icin bu ayrim onemli.)
    """
    if df_samples.empty:
        return pd.DataFrame()

    band = float(config.get("build", {}).get("input_neutral_band", 0.0))
    ev_cfg = config.get("input_events", config.get("events", {}))
    min_on = int(ev_cfg.get("onset_min_samples", 1))

    rows = []
    for (pid, tid), g in df_samples.groupby(["participant_id", "trial_id"]):
        g = g.sort_values("sample_index")
        active = g[g["phase"] == "active"]
        if len(active) == 0:
            continue

        for k, (b, e) in enumerate(_episode_bounds(active)):
            ep = active.iloc[b:e]
            u = ep["input_applied"].values
            neutral = np.abs(u) <= band
            sign_u = np.sign(u)
            sign_u[neutral] = 0
            si = ep["sample_index"].values
            tt = ep["t_trial_s"].values
            ang = ep["pole_angle_deg"].values
            omg = ep["pole_angular_velocity_deg_s"].values
            nz = ep["noise_level_id"].iloc[0]
            pr = ep["practice"].iloc[0]

            def _rec(i, kind, direction):
                rows.append({
                    "participant_id": pid, "trial_id": tid, "episode": k,
                    "event": kind,
                    "sample_index": int(si[i]),
                    "t_trial_s": float(tt[i]),
                    "pole_angle_deg": float(ang[i]),
                    "pole_angular_velocity_deg_s": float(omg[i]),
                    "input_applied": float(u[i]),
                    "direction": direction,
                    "noise_level_id": nz,
                    "practice": pr,
                })

            for i in range(1, len(ep)):
                if neutral[i - 1] and not neutral[i]:
                    if bool(np.all(~neutral[i:i + min_on])):
                        _rec(i, "onset", float(sign_u[i]))
                elif not neutral[i - 1] and neutral[i]:
                    _rec(i, "offset", float(sign_u[i - 1]))

            # yon degistirme: notr ornekler atlanarak
            live = np.flatnonzero(sign_u != 0)
            if len(live) > 1:
                sl = sign_u[live]
                for j in np.flatnonzero(np.diff(sl) != 0) + 1:
                    _rec(int(live[j]), "reversal", float(sl[j]))

            for i in np.flatnonzero(ep["fall_event"].values == 1):
                _rec(int(i), "fall", np.nan)

    return pd.DataFrame(rows)


def build_all(df_samples, df_trials, config):
    """Tum turetmeleri sirayla uygular.

    Doner: (df_built, episodes, regimes, input_events)
    """
    df = add_state(df_samples)
    df = classify_actions(df, config)
    df = add_episode_index(df)
    episodes = segment_episodes(df, config, df_trials)
    regimes = segment_regimes(df, config)
    input_events = detect_input_events(df, config)
    return df, episodes, regimes, input_events
