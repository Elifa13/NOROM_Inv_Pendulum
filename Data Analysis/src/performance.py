"""NB03 - trial ve katilimci x kosul duzeyi performans metrikleri.

Girdi: NB02 ciktilari (samples_built, episodes) + NB01 ciktisi (trials_clean).
Cikti: trial_metrics.parquet, participant_condition.parquet.

Analiz birimi katilimci x kosul: 10 measurement trial'in ortalamasi. Trial
duzeyi tablo ara urun, NB04'un da isine yariyor.

Sample maskesi analysis_include (NB01 6): phase == "active" & practice == 0
& qc_pass & window_focused == 1. Reset frameleri tamamen disarida, yani her
measurement trial'da tam 1200 active sample var ve payda sabit -- cok dusen
bir katilimci reset sayesinde yapay olarak iyi gorunmuyor.

Bu modul istatistiksel test YAPMAZ. Friedman/Wilcoxon ve noise seviyesi
karari NB06'nin isi. Buradaki dz ve "kac katilimcida ayni yonde" sayilari
betimleyici etki buyuklugu, hipotez testi degil.
"""

from pathlib import Path

import numpy as np
import pandas as pd

CONDITION_ORDER = ["no_noise", "N1", "N2", "N3", "N4"]

# metrik -> (etiket, iyi yon)  +1 = buyuk iyi, -1 = kucuk iyi, 0 = belirsiz
METRIC_INFO = {
    "mae_angle_deg": ("Mean |theta| (deg)", -1),
    "rms_angle_deg": ("RMS theta (deg)", -1),
    "siqr_theta_deg": ("sIQR theta (deg)", -1),
    "siqr_omega_deg_s": ("sIQR omega (deg/s)", -1),
    "stab_time_s": ("Stabilizasyon suresi (s / 20 s)", +1),
    "falls_per_trial": ("Dusus / trial", -1),
    "falls_angle_per_trial": ("Aci kaynakli dusus / trial", -1),
    "falls_track_per_trial": ("Ray kaynakli dusus / trial", -1),
    "control_effort": ("Control effort (RMS u)", 0),
    "cart_rms_m": ("Cart RMS pozisyon (m)", 0),
    "mean_episode_s": ("Ortalama episode suresi (s)", +1),
    "mean_episode_s_done": ("Ortalama episode suresi, sansursuz (s)", +1),
    "mean_T_over_T0": ("Episode T/T0", +1),
    "mean_T_over_T0_done": ("Episode T/T0, sansursuz", +1),
}

# Sure adaylari: NB03 3'te bunlardan biri secilir.
DURATION_CANDIDATES = ["mean_episode_s", "mean_episode_s_done",
                       "mean_T_over_T0", "mean_T_over_T0_done"]

# 5 seviye icin ortogonal lineer kontrast (ordinal pozisyon uzerinden).
# sigma degerleri esit arali degil ve sifir icerdigi icin log alinamiyor.
_LINEAR = np.array([-2, -1, 0, 1, 2], dtype=float)


# --------------------------------------------------------------------------
# yukleme
# --------------------------------------------------------------------------

def load_built(interim_dir):
    """NB01/NB02 ciktilarini okur. Salt okuma."""
    interim_dir = Path(interim_dir)
    samples = pd.read_parquet(interim_dir / "samples_built.parquet")
    episodes = pd.read_parquet(interim_dir / "episodes.parquet")
    trials = pd.read_parquet(interim_dir / "trials_clean.parquet")
    return samples, episodes, trials


def condition_labels(trial_df):
    """noise_level_id -> 'N1 (sigma=0.02)', sigma veriden okunur."""
    sig = trial_df.groupby("noise_level_id")["noise_sigma"].first()
    return {c: "{} (σ={:.2f})".format(c, sig[c])
            for c in CONDITION_ORDER if c in sig.index}


def _as_condition(s):
    return pd.Categorical(s, CONDITION_ORDER, ordered=True)


# --------------------------------------------------------------------------
# trial duzeyi
# --------------------------------------------------------------------------

def _siqr(s):
    """Yari ceyrekler arasi acilim: (Q75 - Q25) / 2."""
    return (s.quantile(0.75) - s.quantile(0.25)) / 2.0


def _episode_trial_metrics(episodes):
    """Trial basina episode ozetleri ve sebebe gore dusus sayilari.

    Sansurlu episode: trial 20 s dolduğu icin kesilen, dususle bitmeyen.
    Sansurluler ortalamayi asagi ceker (kisa gorunurler) ama atmak da
    yanli: en iyi denemeler tam onlar. Bu yuzden iki surum de uretilir,
    hangisinin kullanilacagina NB03 3'te karar verilir.
    """
    e = episodes[(episodes["practice"] == 0) & episodes["qc_pass"]]
    keys = ["participant_id", "trial_id"]
    g = e.groupby(keys, observed=True)
    done = e[~e["censored"]].groupby(keys, observed=True)

    out = pd.DataFrame({
        "n_episodes": g.size(),
        "n_episodes_censored": g["censored"].sum(),
        "mean_episode_s": g["duration_s"].mean(),
        "mean_T_over_T0": g["duration_over_T0"].mean(),
        "n_episodes_done": done.size(),
        "mean_episode_s_done": done["duration_s"].mean(),
        "mean_T_over_T0_done": done["duration_over_T0"].mean(),
        "mean_theta0_abs_deg": g["theta0_deg"].apply(lambda s: s.abs().mean()),
    })

    cause = (e[e["ended_in_fall"]]
             .groupby(keys + ["fall_cause"], observed=True)
             .size().unstack("fall_cause"))
    for col, name in [("angle", "falls_angle_per_trial"),
                      ("track", "falls_track_per_trial")]:
        out[name] = cause[col] if col in cause.columns else 0.0

    fill = ["n_episodes_done", "falls_angle_per_trial", "falls_track_per_trial"]
    out[fill] = out[fill].fillna(0.0)
    return out.astype({"n_episodes": int, "n_episodes_censored": int})


def trial_metrics(samples, episodes, cfg):
    """Her measurement trial icin bir satir."""
    p = cfg["performance"]
    thr = p["stab_angle_deg"]

    a = samples[samples["analysis_include"]].copy()
    a["_abs_theta"] = a["pole_angle_deg"].abs()
    a["_within"] = (a["_abs_theta"] <= thr).astype(float)

    keys = ["participant_id", "noise_level_id", "noise_sigma",
            "trial_id", "trial_order", "round_index"]
    g = a.groupby(keys, observed=True)

    out = pd.DataFrame({
        "n_samples": g.size(),
        "mae_angle_deg": g["_abs_theta"].mean(),
        "rms_angle_deg": np.sqrt(g["pole_angle_deg"].apply(lambda s: (s ** 2).mean())),
        "max_abs_angle_deg": g["_abs_theta"].max(),
        "siqr_theta_deg": g["pole_angle_deg"].apply(_siqr),
        "siqr_omega_deg_s": g["pole_angular_velocity_deg_s"].apply(_siqr),
        "cart_rms_m": np.sqrt(g["cart_position_m"].apply(lambda s: (s ** 2).mean())),
        "control_effort": np.sqrt(g["input_applied"].apply(lambda s: (s ** 2).mean())),
        "falls_per_trial": g["fall_event"].sum().astype(float),
        "_within_n": g["_within"].sum(),
        "_dt": g["fixed_delta_time_s"].mean(),
    })
    out["active_s"] = out["n_samples"] * out["_dt"]
    out["stab_time_s"] = out["_within_n"] * out["_dt"]
    out["stab_pct"] = 100.0 * out["stab_time_s"] / p["trial_duration_s"]
    out = out.drop(columns=["_within_n", "_dt"]).reset_index()

    epi = _episode_trial_metrics(episodes).reset_index()
    out = out.merge(epi, on=["participant_id", "trial_id"], how="left")
    out["noise_level_id"] = _as_condition(out["noise_level_id"])
    return out.sort_values(["participant_id", "trial_order"]).reset_index(drop=True)


def check_fall_consistency(trial_df, trials_clean):
    """Sebebe gore ayrilan dususlerin toplami Unity'nin sayimini tutuyor mu."""
    t = trial_df.copy()
    t["_split_sum"] = t["falls_angle_per_trial"] + t["falls_track_per_trial"]
    ref = trials_clean[trials_clean["practice"] == 0][
        ["participant_id", "trial_id", "fall_count"]]
    m = t.merge(ref, on=["participant_id", "trial_id"], how="left")
    return pd.DataFrame([{
        "trial": len(m),
        "sample_toplami_vs_unity": int((m["falls_per_trial"] == m["fall_count"]).sum()),
        "sebep_toplami_vs_unity": int((m["_split_sum"] == m["fall_count"]).sum()),
        "unity_toplam": int(m["fall_count"].sum()),
        "aci": float(m["falls_angle_per_trial"].sum()),
        "ray": float(m["falls_track_per_trial"].sum()),
    }])


# --------------------------------------------------------------------------
# katilimci x kosul
# --------------------------------------------------------------------------

def participant_condition(trial_df, metrics=None):
    """Analiz birimi: katilimci x kosul, 10 trial'in ortalamasi + SEM."""
    metrics = list(METRIC_INFO) if metrics is None else list(metrics)
    metrics = [m for m in metrics if m in trial_df.columns]
    g = trial_df.groupby(["participant_id", "noise_level_id"], observed=True)

    pc = pd.concat([
        g[metrics].mean(),
        g[metrics].sem().add_suffix("_sem"),
        pd.DataFrame({
            "n_trials": g.size(),
            "noise_sigma": g["noise_sigma"].first(),
            "mean_theta0_abs_deg": g["mean_theta0_abs_deg"].mean(),
        }),
    ], axis=1).reset_index()

    pc["noise_level_id"] = _as_condition(pc["noise_level_id"])
    return pc.sort_values(["participant_id", "noise_level_id"]).reset_index(drop=True)


def condition_table(pc, metrics=None):
    """Kosul x metrik: katilimci ortalamalarinin ortalamasi + SEM."""
    metrics = list(METRIC_INFO) if metrics is None else list(metrics)
    metrics = [m for m in metrics if m in pc.columns]
    g = pc.groupby("noise_level_id", observed=True)
    mean = g[metrics].mean().T
    sem = g[metrics].sem().T
    out = mean.round(3).astype(str) + " ±" + sem.round(3).astype(str)
    out.insert(0, "yon", [METRIC_INFO.get(m, ("", 0))[1] for m in mean.index])
    return out


def _center_within(pc, col):
    """Katilimci ici merkezleme. Within-subject tasarimda dogru olcek."""
    return pc[col] - pc.groupby("participant_id")[col].transform("mean")


def baseline_agreement(pc, metric, cfg):
    """Her kosulun baseline'a gore within-subject farki.

    dz = mean(fark) / sd(fark), katilimci basina eslesmis fark uzerinden.
    n_kotu = kac katilimcida fark metrigin "kotu" yonunde. Ikisi de
    betimleyici; p degeri NB06'da hesaplanir.
    """
    base = cfg["performance"]["baseline_condition"]
    direction = METRIC_INFO.get(metric, ("", 0))[1]

    w = pc.pivot(index="participant_id", columns="noise_level_id",
                 values=metric)
    rows = []
    for cond in CONDITION_ORDER:
        if cond == base or cond not in w.columns:
            continue
        d = (w[cond] - w[base]).dropna()
        worse = int((d * direction < 0).sum()) if direction else np.nan
        rows.append({
            "kosul": cond,
            "baseline_farki": d.mean(),
            "dz": d.mean() / d.std(ddof=1) if d.std(ddof=1) > 0 else np.nan,
            "n_kotu": worse,
            "n": len(d),
        })
    return pd.DataFrame(rows).set_index("kosul").round(3)


# --------------------------------------------------------------------------
# 2. sIQR gereksiz mi
# --------------------------------------------------------------------------

def metric_correlations(pc, metrics, within=True):
    """Metrikler arasi korelasyon.

    within=True ise katilimci ici merkezlenmis degerler kullanilir --
    katilimcilar arasi seviye farki korelasyonu sisirdigi icin within
    surumu bu tasarimda dogru olan.
    """
    d = pd.DataFrame({m: (_center_within(pc, m) if within else pc[m])
                      for m in metrics if m in pc.columns})
    return d.corr().round(3)


def redundancy_check(pc, target, base, cfg):
    """target metrigi base'in kopyasi mi.

    target katilimci ici merkezlenip base uzerine regres edilir, sonra iki
    seye bakilir:

    - `r_within`  : ham ortusme
    - `korunan_trend` : kosul profilinin LINEER kontrastinin ne kadari
      artikta hayatta kaliyor. Asil soru bu -- metrigin ayri bir sey olcup
      olcmedigi degil, RMS'in gormedigi bir *noise trendi* gorup gormedigi.
      sIQR gibi bir metrik RMS'ten farkli bir konstrukt olabilir ama
      kosullari ayirt etmiyorsa NB06'nin metrik setine girmez.

    Doner: (ozet Series, kosul profili DataFrame)
    """
    r_thr = cfg["performance"]["redundancy_abs_r"]
    t_thr = cfg["performance"]["redundancy_retained_trend"]
    y = _center_within(pc, target)
    x = _center_within(pc, base)

    slope = np.polyfit(x, y, 1)[0]
    resid = y - slope * x
    r = float(np.corrcoef(x, y)[0, 1])

    prof = pd.DataFrame({
        "ham_profil": y.groupby(pc["noise_level_id"], observed=True).mean(),
        "artik_profil": resid.groupby(pc["noise_level_id"], observed=True).mean(),
    }).reindex(CONDITION_ORDER)

    raw_lin = float(prof["ham_profil"].values @ _LINEAR)
    res_lin = float(prof["artik_profil"].values @ _LINEAR)
    kept = abs(res_lin) / abs(raw_lin) if raw_lin else np.nan

    summary = pd.Series({
        "metrik": target,
        "referans": base,
        "r_within": round(r, 3),
        "ham_lineer_kontrast": round(raw_lin, 3),
        "artik_lineer_kontrast": round(res_lin, 3),
        "korunan_trend": round(kept, 3),
        "trend_esigi": t_thr,
        "gereksiz": bool(kept < t_thr or abs(r) >= r_thr),
    })
    return summary, prof.round(4)


# --------------------------------------------------------------------------
# 3. sure olcutu secimi
# --------------------------------------------------------------------------

def theta0_sensitivity(episodes):
    """Sure adaylarinin baslangic acisina duyarliligi (episode duzeyi).

    Iyi bir performans olcutu baslangic acisindan bagimsiz olmali:
    kolay bir baslangic acisi aldigi icin uzun dayanan katilimci daha iyi
    kontrol ediyor degil.
    """
    e = episodes[(episodes["practice"] == 0) & episodes["qc_pass"]]
    rows = []
    for label, sub in [("tum episode", e), ("sansursuz", e[~e["censored"]])]:
        a = sub["theta0_deg"].abs()
        for col in ["duration_s", "duration_over_T0"]:
            rows.append({
                "kume": label,
                "olcut": col,
                "n": len(sub),
                "corr_theta0": round(float(np.corrcoef(a, sub[col])[0, 1]), 3),
            })
    return pd.DataFrame(rows)


def duration_candidate_table(pc, cfg):
    """Sure adaylarini yan yana: kosul profili, N4 etkisi, theta0 kirliligi."""
    rows = []
    for cand in DURATION_CANDIDATES:
        if cand not in pc.columns:
            continue
        agree = baseline_agreement(pc, cand, cfg)
        y = _center_within(pc, cand)
        prof = y.groupby(pc["noise_level_id"], observed=True).mean()
        rows.append({
            "aday": cand,
            "kosul_acilimi": round(float(prof.max() - prof.min()), 4),
            "N4_dz": agree.loc["N4", "dz"] if "N4" in agree.index else np.nan,
            "N4_n_kotu": agree.loc["N4", "n_kotu"] if "N4" in agree.index else np.nan,
            "corr_theta0_pc": round(float(pd.concat(
                [_center_within(pc, "mean_theta0_abs_deg"), y],
                axis=1).dropna().corr().iloc[0, 1]), 3),
            "eksik_hucre": int(pc[cand].isna().sum()),
        })
    return pd.DataFrame(rows).set_index("aday")


# --------------------------------------------------------------------------
# cikti
# --------------------------------------------------------------------------

def save_outputs(trial_df, pc, interim_dir):
    interim_dir = Path(interim_dir)
    t = trial_df.copy()
    p = pc.copy()
    for d in (t, p):
        d["noise_level_id"] = d["noise_level_id"].astype(str)
    t.to_parquet(interim_dir / "trial_metrics.parquet", index=False)
    p.to_parquet(interim_dir / "participant_condition.parquet", index=False)
    return {"trial_metrics.parquet": len(t), "participant_condition.parquet": len(p)}
