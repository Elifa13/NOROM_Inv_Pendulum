"""Acil sunum (90_sunum.ipynb) icin metrik ve figur uretimi.

IZOLE MODUL. Zincirin geri kalani (NB01-NB06, build.py, physics.py, qc.py)
bunu import etmez. Sadece data/interim altindaki hazir ciktilari OKUR,
hicbir seyi uzerine yazmaz; tek yazdigi yer config.presentation.figure_dir.
Bu dosya ve 90_sunum.ipynb silinirse baska hicbir sey etkilenmez.

Analiz birimi: katilimci x kosul = 10 measurement trial'in ortalamasi.

Sample maskesi analysis_include (NB01 §6) kullanilir:
    phase == "active" & practice == 0 & qc_pass & window_focused == 1
Reset frameleri tamamen disarida. Her measurement trial'da tam 1200 active
sample (20.0 s) var, yani payda sabit -- cok dusen bir katilimci reset
sayesinde yapay olarak iyi gorunmuyor.

Metrikler:
    mae_angle_deg    mean(|theta|)                       dusuk iyi
    success_time_s   |theta| <= 30 deg olan sure, s/trial yuksek iyi
    falls_per_trial  fall_event toplami / trial           dusuk iyi
    cart_rms_m       sqrt(mean(x^2))                      YON BELIRSIZ

cart_rms_m composite'e girmez: dusuk cart salinimi hem "iyi kontrol" hem
"hic mudahale etmedi" anlamina gelebilir. Sadece incelemek icin cizilir.

fall_event sayimi dogrulandi: active frameler disinda hic tetiklenmiyor ve
sample toplami Unity'nin trial_summary.fall_count'uyla 600 trial'in
600'unde birebir ayni (toplam 1156). Dusus sebebi (aci vs ray) bu
notebook'ta ayrilmaz, toplam sayilir.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from scipy import stats

CONDITION_ORDER = ["no_noise", "N1", "N2", "N3", "N4"]

# metrik -> (etiket, iyi yon)  +1 = buyuk iyi, -1 = kucuk iyi, 0 = belirsiz
METRIC_INFO = {
    "mae_angle_deg": ("Mean absolute angle (deg)", -1),
    "success_time_s": ("Successful stabilization (s / 20 s)", +1),
    "falls_per_trial": ("Fall count (per trial)", -1),
    "cart_rms_m": ("Cart RMS position (m)", 0),
}

# Heatmap'te baseline farki hangi olcekte gosterilsin.
# falls_per_trial YUZDE OLAMAZ: bir katilimcinin (P009) no_noise'taki fall
# sayisi tam 0, yani payda sifir -> yuzde tanimsiz. Mutlak fark hem tanimli
# hem sunumda daha okunakli ("+0.5 dusus/trial"). success_time_s'te de
# saniye farki yuzdeden somut.
HEATMAP_SCALE = {
    "mae_angle_deg": ("pct", "% Δ"),
    "success_time_s": ("delta", "Δ s / 20 s"),
    "falls_per_trial": ("delta", "Δ dusus / trial"),
    "cart_rms_m": ("pct", "% Δ"),
}

# 5 seviye icin ortogonal polinom kontrastlari (ordinal pozisyon uzerinden).
# sigma degerleri esit arali degil (0, .02, .05, .08, .25) ve sifir icerdigi
# icin log alinamiyor; ordinal siralama en savunulabilir secim.
_LINEAR = np.array([-2, -1, 0, 1, 2], dtype=float)
_QUADRATIC = np.array([2, -1, -2, -1, 2], dtype=float)


# --------------------------------------------------------------------------
# yukleme ve metrikler
# --------------------------------------------------------------------------

def load_interim(interim_dir):
    """NB01 ciktilarini okur. Salt okuma."""
    interim_dir = Path(interim_dir)
    samples = pd.read_parquet(interim_dir / "samples_clean.parquet")
    trials = pd.read_parquet(interim_dir / "trials_clean.parquet")
    return samples, trials


def condition_labels(samples):
    """noise_level_id -> 'N1 (sigma=0.02)' etiketi, veriden okunur."""
    sig = (samples[samples["practice"] == 0]
           .groupby("noise_level_id")["noise_sigma"].first())
    # Sigma 2 haneye yuvarlaninca pilot2'nin .005/.010/.015'i ayni etikete
    # dusuyor; ayrima yeten en az hane secilir.
    vals = list(sig.values)
    dec = 4
    for d in (2, 3, 4):
        if len({round(float(v), d) for v in vals}) == len(set(vals)):
            dec = d
            break
    out = {}
    for cond in CONDITION_ORDER:
        if cond in sig.index:
            out[cond] = "{}\n(σ={:.{}f})".format(cond, sig[cond], dec)
    return out


def trial_metrics(samples, cfg):
    """Trial duzeyi metrikler. Her measurement trial icin bir satir."""
    p = cfg["presentation"]
    thr = p["success_angle_deg"]

    a = samples[samples["analysis_include"]].copy()
    a["_abs_theta"] = a["pole_angle_deg"].abs()
    a["_within"] = (a["_abs_theta"] <= thr).astype(float)
    a["_x2"] = a["cart_position_m"] ** 2

    keys = ["participant_id", "noise_level_id", "noise_sigma",
            "trial_id", "trial_order", "round_index"]
    g = a.groupby(keys, observed=True)

    out = pd.DataFrame({
        "mae_angle_deg": g["_abs_theta"].mean(),
        "falls_per_trial": g["fall_event"].sum().astype(float),
        "cart_rms_m": np.sqrt(g["_x2"].mean()),
        "n_samples": g.size(),
    })
    # active sure sabit degilse payda yine dogru kalsin diye dt'den gidilir
    dt = g["fixed_delta_time_s"].mean()
    out["active_s"] = out["n_samples"] * dt
    out["success_time_s"] = g["_within"].sum() * dt
    out["success_pct"] = 100.0 * out["success_time_s"] / p["trial_duration_s"]
    return out.reset_index()


def participant_condition_metrics(trial_df):
    """Analiz birimi: katilimci x kosul. 10 trial'in ortalamasi + SEM."""
    metrics = list(METRIC_INFO)
    g = trial_df.groupby(["participant_id", "noise_level_id"], observed=True)

    mean = g[metrics].mean()
    sem = g[metrics].sem().add_suffix("_sem")
    extra = pd.DataFrame({
        "n_trials": g.size(),
        "noise_sigma": g["noise_sigma"].first(),
        "success_pct": g["success_pct"].mean(),
    })

    pc = pd.concat([mean, sem, extra], axis=1).reset_index()
    pc["noise_level_id"] = pd.Categorical(
        pc["noise_level_id"], CONDITION_ORDER, ordered=True)
    return (pc.sort_values(["participant_id", "noise_level_id"])
              .reset_index(drop=True))


def baseline_delta(pc, cfg):
    """Her metrik icin baseline'a gore mutlak ve yuzde fark."""
    base_cond = cfg["presentation"]["baseline_condition"]
    out = pc.copy()
    for m in METRIC_INFO:
        base = (out[out["noise_level_id"] == base_cond]
                .set_index("participant_id")[m])
        b = out["participant_id"].map(base)
        out[m + "_delta"] = out[m] - b
        # baseline sifirsa yuzde tanimsiz -> inf degil NaN
        pct = 100.0 * (out[m] - b) / b.replace(0.0, np.nan)
        out[m + "_pct"] = pct.replace([np.inf, -np.inf], np.nan)
    return out


# --------------------------------------------------------------------------
# kisisel optimal noise
# --------------------------------------------------------------------------

def personal_best(pc, cfg):
    """Her katilimci icin en iyi noise seviyesi.

    Her metrik kendi icinde ayri ayri siralanir (1 = en iyi). Composite,
    yonu net olan metriklerin (config.presentation.composite_metrics) rank
    toplamidir. Minimum toplam birden fazla seviyede paylasiliyorsa
    "Belirsiz" yazilir -- 10 tekrarlik pilotta sahte kesinlik verilmez.
    """
    comp_metrics = cfg["presentation"]["composite_metrics"]
    rows = []

    for pid, d in pc.groupby("participant_id"):
        d = d.set_index("noise_level_id").reindex(CONDITION_ORDER)
        rec = {"participant_id": pid}
        ranks = {}
        for m, (_, direction) in METRIC_INFO.items():
            if direction == 0:
                rec["best_" + m] = None
                continue
            # her metrik "kucuk iyi" olacak sekilde cevrilir
            vals = d[m] if direction < 0 else -d[m]
            ranks[m] = vals.rank(method="min")
            rec["best_" + m] = str(vals.idxmin())

        total = sum(ranks[m] for m in comp_metrics)
        winners = list(total.index[total == total.min()])
        srt = np.sort(total.to_numpy(dtype=float))
        rec["composite_rank_min"] = float(srt[0])
        rec["margin"] = float(srt[1] - srt[0])
        rec["n_winners"] = len(winners)
        rec["optimal"] = winners[0] if len(winners) == 1 else "Belirsiz"
        rec["tied_with"] = ", ".join(winners) if len(winners) > 1 else ""
        for cond in CONDITION_ORDER:
            rec["rank_" + cond] = float(total.get(cond, np.nan))
        rows.append(rec)

    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# istatistik
# --------------------------------------------------------------------------

def _holm(pvals):
    """Holm-Bonferroni duzeltmesi."""
    p = np.asarray(pvals, dtype=float)
    order = np.argsort(p)
    n = len(p)
    adj = np.empty(n)
    running = 0.0
    for i, idx in enumerate(order):
        running = max(running, (n - i) * p[idx])
        adj[idx] = min(running, 1.0)
    return adj


def stats_table(pc, cfg):
    """Friedman + baseline'a karsi Wilcoxon (Holm) + lineer/kuadratik trend.

    Trend: her katilimcinin 5 kosul ortalamasina ortogonal polinom kontrasti
    uygulanir, sonra kontrast skorlari uzerinde tek orneklem Wilcoxon.
    Kuadratik terim "U sekli var mi" sorusunun dogrudan testi.
    """
    base_cond = cfg["presentation"]["baseline_condition"]
    rows = []

    for m, (label, direction) in METRIC_INFO.items():
        w = (pc.pivot(index="participant_id", columns="noise_level_id",
                      values=m)
               .reindex(columns=CONDITION_ORDER).dropna())
        arr = w.to_numpy(dtype=float)

        fr_stat, fr_p = stats.friedmanchisquare(*arr.T)

        others = [c for c in CONDITION_ORDER if c != base_cond]
        raw = []
        for c in others:
            try:
                _, p = stats.wilcoxon(w[c], w[base_cond])
            except ValueError:      # tum farklar sifir
                p = 1.0
            raw.append(float(p))
        holm = _holm(raw)

        lin = arr @ _LINEAR
        quad = arr @ _QUADRATIC
        _, p_lin = stats.wilcoxon(lin)
        _, p_quad = stats.wilcoxon(quad)

        row = {
            "metric": label, "n": int(len(w)), "direction": direction,
            "friedman_chi2": float(fr_stat), "friedman_p": float(fr_p),
            "linear_contrast": float(lin.mean()), "linear_p": float(p_lin),
            "quadratic_contrast": float(quad.mean()),
            "quadratic_p": float(p_quad),
        }
        for c, pr, ph in zip(others, raw, holm):
            row[c + "_vs_base_p"] = pr
            row[c + "_vs_base_p_holm"] = float(ph)
        rows.append(row)

    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# figurler
# --------------------------------------------------------------------------

def _save(fig, name, cfg, base_dir):
    out_dir = Path(base_dir) / cfg["presentation"]["figure_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / (name + ".png")
    fig.savefig(path, dpi=cfg["presentation"]["figure_dpi"],
                bbox_inches="tight", facecolor="white")
    return path


def _xticks(ax, labels):
    ax.set_xticks(range(len(CONDITION_ORDER)))
    ax.set_xticklabels([labels.get(c, c) for c in CONDITION_ORDER], fontsize=8)


def fig_metric(pc, metric, cfg, base_dir, labels, label_override=None,
               fname=None):
    """Sol: spaghetti + grup ortalamasi (SEM). Sag: katilimci basina grid.

    label_override / fname: ayni metrigin farkli bir parametreyle
    hesaplanmis halini cizmek icin (or. basari esigi 15 deg). Verilmezse
    METRIC_INFO'daki etiket ve "fig_<metric>" dosya adi kullanilir.
    """
    label, direction = METRIC_INFO[metric]
    if label_override is not None:
        label = label_override
    arrow = {1: "yuksek iyi", -1: "dusuk iyi", 0: "yon belirsiz"}[direction]

    w = (pc.pivot(index="participant_id", columns="noise_level_id",
                  values=metric).reindex(columns=CONDITION_ORDER))
    wsem = (pc.pivot(index="participant_id", columns="noise_level_id",
                     values=metric + "_sem").reindex(columns=CONDITION_ORDER))
    pids = list(w.index)
    x = np.arange(len(CONDITION_ORDER))

    n = len(pids)
    ncol = 4
    nrow = int(np.ceil(n / ncol))
    fig = plt.figure(figsize=(6.0 + 2.6 * ncol, max(4.4, 2.05 * nrow)))
    gs = fig.add_gridspec(nrow, ncol + 2,
                          width_ratios=[1.5, 1.5] + [1] * ncol,
                          wspace=0.35, hspace=0.6)

    # --- sol panel: grup ---
    ax = fig.add_subplot(gs[:, 0:2])
    for pid in pids:
        ax.plot(x, w.loc[pid], color="0.72", lw=1.0, marker="o", ms=2.5,
                zorder=1)
    ax.errorbar(x, w.mean(), yerr=w.sem(), color="#1f4e79", lw=2.6,
                marker="o", ms=6, capsize=4, zorder=3,
                label="Grup ortalamasi ± SEM (n={})".format(n))
    ax.set_ylabel(label)
    ax.set_title("{}\n({})".format(label, arrow), fontsize=11)
    _xticks(ax, labels)
    ax.legend(fontsize=8, loc="best")
    ax.grid(axis="y", alpha=0.3)

    # --- sag: katilimci basina, HER PANEL KENDI y ekseninde ---
    # Ortak eksen kullanilmiyor: katilimcilar arasi seviye farki cok buyuk
    # (or. fall count P005 ~0 vs P007 ~5-8) ve kisi-ici oruntuyu duz cizgiye
    # ceviriyor. Asil soru "bu kiside noise ne yapiyor" oldugu icin eksen
    # serbest birakilir; seviye bilgisi panel basligina yazilir.
    for i, pid in enumerate(pids):
        axp = fig.add_subplot(gs[i // ncol, 2 + i % ncol])
        y = w.loc[pid].to_numpy(dtype=float)
        e = np.nan_to_num(wsem.loc[pid].to_numpy(dtype=float))
        axp.errorbar(x, y, yerr=e, color="#1f4e79", lw=1.4, marker="o",
                     ms=3.5, capsize=2.5)
        if direction != 0:
            b = int(np.nanargmin(y) if direction < 0 else np.nanargmax(y))
            axp.plot(x[b], y[b], marker="*", ms=12, color="#c0392b",
                     zorder=5, lw=0)
        lo, hi = np.nanmin(y - e), np.nanmax(y + e)
        pad = 0.18 * ((hi - lo) or (abs(hi) * 0.1 or 1.0))
        axp.set_ylim(lo - pad, hi + pad)
        axp.set_title("{}  (ort. {:.2f})".format(pid, np.nanmean(y)),
                      fontsize=8)
        axp.set_xticks(x)
        axp.set_xticklabels(CONDITION_ORDER, fontsize=6, rotation=45)
        axp.tick_params(labelsize=6)
        axp.grid(axis="y", alpha=0.25)

    note = ("Sag panellerde hata cubugu = 10 measurement trial'in SEM'i. "
            "Kirmizi yildiz = o katilimcinin en iyi kosulu. DIKKAT: her "
            "panel kendi y ekseninde, paneller arasi yukseklik "
            "karsilastirilamaz -- seviye icin basliktaki ortalamaya bakin."
            if direction != 0 else
            "Sag panellerde hata cubugu = 10 measurement trial'in SEM'i. "
            "Her panel kendi y ekseninde. Yonu belirsiz oldugu icin en iyi "
            "kosul isaretlenmedi.")
    fig.suptitle("{} × noise seviyesi".format(label), fontsize=13,
                 y=1.005)
    fig.text(0.5, -0.02, note, ha="center", fontsize=8, color="0.35")
    return fig, _save(fig, fname or ("fig_" + metric), cfg, base_dir)


def fig_heatmap(pcd, cfg, base_dir, labels):
    """4 metrik x (katilimci x kosul), baseline'a gore yuzde degisim."""
    base_cond = cfg["presentation"]["baseline_condition"]
    metrics = list(METRIC_INFO)
    fig, axes = plt.subplots(1, len(metrics), figsize=(4.6 * len(metrics), 5.6))

    for ax, m in zip(np.atleast_1d(axes), metrics):
        label, direction = METRIC_INFO[m]
        scale, unit = HEATMAP_SCALE[m]
        w = (pcd.pivot(index="participant_id", columns="noise_level_id",
                       values=m + "_" + scale)
                .reindex(columns=CONDITION_ORDER))
        fmt = "{:+.0f}" if scale == "pct" else "{:+.2f}"
        # yesil = iyilesme; yonu ters olan metrikte isaret cevrilir
        signed = (w * (-1 if direction < 0 else 1)).to_numpy()
        finite = signed[np.isfinite(signed)]
        lim = (float(np.abs(finite).max()) if finite.size else 1.0) or 1.0
        im = ax.imshow(signed, cmap="RdYlGn", vmin=-lim, vmax=lim,
                       aspect="auto")
        vals = w.to_numpy()
        for i in range(vals.shape[0]):
            for j in range(vals.shape[1]):
                if np.isfinite(vals[i, j]):
                    ax.text(j, i, fmt.format(vals[i, j]), ha="center",
                            va="center", fontsize=7)
        ax.set_xticks(range(len(CONDITION_ORDER)))
        ax.set_xticklabels([labels.get(c, c) for c in CONDITION_ORDER],
                           fontsize=7)
        ax.set_yticks(range(vals.shape[0]))
        ax.set_yticklabels(w.index, fontsize=8)
        sub = "yon belirsiz" if direction == 0 else "yesil = iyilesme"
        ax.set_title("{}\n{} vs {} ({})".format(label, unit, base_cond, sub),
                     fontsize=9)
        fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)

    fig.suptitle("Katilimci × kosul: baseline'a ({}) gore degisim"
                 .format(base_cond), fontsize=13, y=1.02)
    fig.tight_layout()
    return fig, _save(fig, "fig_heatmap_delta", cfg, base_dir)


def fig_personal_best(best, cfg, base_dir, labels):
    """Her metrik icin ve composite icin kisisel optimal seviye sayimi."""
    metrics = [m for m, (_, d) in METRIC_INFO.items() if d != 0]
    cats = CONDITION_ORDER + ["Belirsiz"]
    fig, axes = plt.subplots(1, len(metrics) + 1,
                             figsize=(3.6 * (len(metrics) + 1), 4.4),
                             sharey=True)

    panels = [(best["best_" + m], METRIC_INFO[m][0]) for m in metrics]
    panels.append((best["optimal"], "COMPOSITE\n(3 metrigin rank toplami)"))

    for ax, (series, title) in zip(axes, panels):
        counts = series.value_counts().reindex(cats).fillna(0)
        colors = ["#1f4e79"] * len(CONDITION_ORDER) + ["0.65"]
        ax.bar(range(len(cats)), counts.to_numpy(), color=colors)
        for i, v in enumerate(counts.to_numpy()):
            if v:
                ax.text(i, v + 0.08, int(v), ha="center", fontsize=9)
        ax.set_xticks(range(len(cats)))
        ax.set_xticklabels([labels.get(c, c) for c in cats], fontsize=7,
                           rotation=45)
        ax.set_title(title, fontsize=9)
        ax.grid(axis="y", alpha=0.3)
        ax.set_ylim(0, max(3, counts.max() + 1))
    axes[0].set_ylabel("Bu seviyenin en iyi oldugu katilimci sayisi")

    fig.suptitle("Kisisel optimal noise seviyesi (n={})".format(len(best)),
                 fontsize=13, y=1.03)
    fig.tight_layout()
    return fig, _save(fig, "fig_personal_best", cfg, base_dir)


def fig_trial_order(trial_df, cfg, base_dir, labels):
    """Ogrenme confound kontrolu: trial sirasina karsi performans."""
    metrics = [m for m, (_, d) in METRIC_INFO.items() if d != 0]
    cmap = plt.get_cmap("viridis")
    colors = {c: cmap(i / (len(CONDITION_ORDER) - 1))
              for i, c in enumerate(CONDITION_ORDER)}

    fig, axes = plt.subplots(1, len(metrics) + 1,
                             figsize=(4.5 * (len(metrics) + 1), 4.0))

    for ax, m in zip(axes[:len(metrics)], metrics):
        # katilimci-ici merkezlenmis: kisiler arasi seviye farki egilimi
        # bogmasin
        d = trial_df.copy()
        d["_c"] = d[m] - d.groupby("participant_id")[m].transform("mean")
        for cond in CONDITION_ORDER:
            s = d[d["noise_level_id"] == cond]
            ax.scatter(s["trial_order"], s["_c"], s=6, alpha=0.28,
                       color=colors[cond])
        binned = d.groupby(pd.cut(d["trial_order"], 10),
                           observed=True)["_c"].mean()
        centers = [iv.mid for iv in binned.index]
        ax.plot(centers, binned.to_numpy(), color="black", lw=2, marker="o",
                ms=4)
        ax.axhline(0, color="0.5", lw=0.8, ls="--")
        ax.set_xlabel("Trial order (1-50)")
        ax.set_ylabel(METRIC_INFO[m][0] + "\n(katilimci-ici merkezlenmis)",
                      fontsize=8)
        ax.grid(alpha=0.3)

    # son panel: kosullarin trial sirasina dagilimi (randomizasyon kontrolu)
    ax = axes[-1]
    pos = trial_df.groupby("noise_level_id", observed=True)["trial_order"]
    present = [c for c in CONDITION_ORDER if c in pos.groups]
    ax.boxplot([pos.get_group(c).to_numpy() for c in present],
               tick_labels=present)
    ax.set_ylabel("Trial order")
    ax.set_title("Kosullarin trial sirasina dagilimi", fontsize=9)
    ax.tick_params(axis="x", labelsize=7, rotation=45)
    ax.grid(axis="y", alpha=0.3)

    handles = [Line2D([], [], marker="o", ls="", color=colors[c], label=c)
               for c in CONDITION_ORDER]
    handles.append(Line2D([], [], color="black", lw=2, label="10'lu blok ort."))
    axes[0].legend(handles=handles, fontsize=7, loc="best", ncol=2)
    fig.suptitle("Ogrenme / trial sirasi kontrolu", fontsize=13, y=1.04)
    fig.tight_layout()
    return fig, _save(fig, "fig_trial_order", cfg, base_dir)


# --------------------------------------------------------------------------
# bagimsiz dogrulama ve esik taramasi
# --------------------------------------------------------------------------

def raw_verification(raw_dir, cfg):
    """Dort metrigi HAM CSV'den yeniden hesaplar.

    Bu fonksiyon bilerek hicbir sey paylasmiyor: parquet okumuyor,
    loader.py / qc.py kullanmiyor, analysis_include kolonuna bakmiyor.
    Unity'nin yazdigi <pid>_<sid>_timeseries.csv dosyalarini dogrudan
    okuyup maskeyi sifirdan kuruyor. Amac sunum sayilarini bagimsiz
    teyit etmek -- ayni hatayi zincirin iki ucunda birden yapma
    ihtimalini dusurmek.

    Maske:
        practice == 0          3 practice trial disarida
        phase == "active"      RESET FRAMELERI DISARIDA
        window_focused == 1    pencere arkadayken toplananlar disarida

    Reset'in gercekten disarida kaldigi is_resetting kolonundan ikinci
    kez dogrulanir; trial basina active sure de raporlanir (hepsi 20.0 s
    ise payda sabit demektir, yani cok dusen biri reset sayesinde yapay
    olarak iyi gorunmuyor).
    """
    thr = cfg["presentation"]["success_angle_deg"]
    raw_dir = Path(raw_dir)
    rows, per_trial, problems = [], [], []

    files = sorted(raw_dir.glob("*/*/*_timeseries.csv"))
    if not files:
        raise FileNotFoundError("ham timeseries bulunamadi: " + str(raw_dir))

    for f in files:
        d = pd.read_csv(f)
        pid = d["participant_id"].iloc[0]
        m = d[(d["practice"] == 0) & (d["phase"] == "active") &
              (d["window_focused"] == 1)].copy()

        if not (m["is_resetting"] == 0).all():
            problems.append(pid + ": reset satiri active icinde sizmis")

        dt = m["fixed_delta_time_s"].mean()
        m["_abs"] = m["pole_angle_deg"].abs()
        g = m.groupby("trial_id")

        t = pd.DataFrame({
            "mae_angle_deg": g["_abs"].mean(),
            "falls_per_trial": g["fall_event"].sum().astype(float),
            "success_time_s": g["_abs"].apply(lambda x: (x <= thr).sum()) * dt,
            "cart_rms_m": np.sqrt(g["cart_position_m"]
                                  .apply(lambda x: (x ** 2).mean())),
            "active_s": g.size() * dt,
        })
        t["participant_id"] = pid
        t["noise_level_id"] = g["noise_level_id"].first()
        per_trial.append(t.reset_index())

        rows.append({
            "participant_id": pid,
            "n_trial": int(m["trial_id"].nunique()),
            "active_s_min": t["active_s"].min(),
            "active_s_max": t["active_s"].max(),
            "mae_angle_deg": t["mae_angle_deg"].mean(),
            "falls_per_trial": t["falls_per_trial"].mean(),
            "success_time_s": t["success_time_s"].mean(),
            "cart_rms_m": t["cart_rms_m"].mean(),
        })

    return (pd.DataFrame(rows).set_index("participant_id"),
            pd.concat(per_trial, ignore_index=True), problems)


def compare_raw_vs_pipeline(raw_trials, trial_df):
    """Ham CSV ile parquet zincirinin ayni trial'da farki.

    Ayni sayilar cikiyorsa fark float yuvarlama seviyesinde (~1e-14)
    kalir. Buyuk fark cikarsa zincirde bir yerde filtre ya da
    birlestirme hatasi var demektir.
    """
    metrics = list(METRIC_INFO)
    keys = ["participant_id", "trial_id"]
    j = (raw_trials.set_index(keys)[metrics]
         .join(trial_df.set_index(keys)[metrics],
               lsuffix="_raw", rsuffix="_pipe", how="outer"))

    out = []
    for m in metrics:
        diff = (j[m + "_raw"] - j[m + "_pipe"]).abs()
        out.append({
            "metric": METRIC_INFO[m][0],
            "eslesen_trial": int(diff.notna().sum()),
            "en_buyuk_fark": float(diff.max()),
            "birebir_ayni": bool(diff.max() < 1e-9),
        })
    return pd.DataFrame(out), j


def threshold_sweep(samples, cfg):
    """'Basarili dengeleme' esigini tarar.

    Neden gerekli: |theta| <= 30 deg esiginde active zamanin %91'i zaten
    "basarili" sayiliyor. Metrik tavana yapismis oluyor ve kosullar
    arasi fark dar bir araliga sikisiyor. Daha dar esikte ayni fark
    daha genis bir araliga yayiliyor, yani ayirt etme gucu artiyor.

    Her esik icin uretilenler:
        kosul ortalamalari, tavan (zamanin yuzde kaci "basarili"),
        Friedman p (5 kosul arasinda fark var mi), lineer trend p,
        dz (etki buyuklugu: son kosul ile baseline farkinin ortalamasi
        bolu bu farkin katilimcilar arasi standart sapmasi) ve farkin
        ayni yonde ciktigi katilimci sayisi.

    UYARI: esigi sonuca bakarak secmek p-hacking olur. Bu tablo esik
    SECMEK icin degil, sonucun esik secimine duyarli OLMADIGINI
    gostermek icin var.
    """
    base_cond = cfg["presentation"]["baseline_condition"]
    thresholds = cfg["presentation"]["threshold_sweep_deg"]
    trial_s = cfg["presentation"]["trial_duration_s"]

    a = samples[samples["analysis_include"]].copy()
    a["_abs"] = a["pole_angle_deg"].abs()
    dt = a["fixed_delta_time_s"].mean()
    last = CONDITION_ORDER[-1]

    rows = []
    for thr in thresholds:
        a["_ok"] = (a["_abs"] <= thr).astype(float)
        pc = (a.groupby(["participant_id", "noise_level_id", "trial_id"],
                        observed=True)["_ok"].sum().mul(dt)
              .groupby(["participant_id", "noise_level_id"], observed=True)
              .mean().unstack()[CONDITION_ORDER])
        arr = pc.to_numpy(dtype=float)

        _, fp = stats.friedmanchisquare(*arr.T)
        _, lp = stats.wilcoxon(arr @ _LINEAR)
        d = pc[last] - pc[base_cond]

        row = {"esik_deg": thr}
        for c in CONDITION_ORDER:
            row[c] = float(pc[c].mean())
        row.update({
            "tavan_pct": 100.0 * float(pc.to_numpy().mean()) / trial_s,
            "friedman_p": float(fp),
            "linear_p": float(lp),
            "dz": float(d.mean() / d.std(ddof=1)),
            "ayni_yonde_kisi": int((d < 0).sum()),
            "n": int(len(d)),
            "ort_fark_s": float(d.mean()),
        })
        rows.append(row)

    return pd.DataFrame(rows)


def fig_threshold_sweep(sweep, cfg, base_dir):
    """Esik taramasi: kosul egrileri, etki buyuklugu, tavan etkisi."""
    base_cond = cfg["presentation"]["baseline_condition"]
    used = cfg["presentation"]["success_angle_deg"]
    x = sweep["esik_deg"].to_numpy(dtype=float)

    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.6))
    cmap = plt.get_cmap("viridis")

    ax = axes[0]
    for i, c in enumerate(CONDITION_ORDER):
        ax.plot(x, sweep[c], marker="o", ms=4,
                color=cmap(i / (len(CONDITION_ORDER) - 1)), label=c)
    ax.axvline(used, color="0.5", ls="--", lw=1)
    ax.set_xlabel("Basari esigi |theta| (deg)")
    ax.set_ylabel("Successful stabilization (s / 20 s)")
    ax.set_title("Kosul ortalamalari", fontsize=10)
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)

    ax = axes[1]
    ax.plot(x, sweep["dz"].abs(), marker="o", color="#1f4e79", lw=2)
    ax.axvline(used, color="0.5", ls="--", lw=1)
    for lvl, txt in [(0.2, "kucuk"), (0.5, "orta"), (0.8, "buyuk")]:
        ax.axhline(lvl, color="0.75", lw=0.8, ls=":")
        ax.text(x.max(), lvl, " " + txt, fontsize=7, va="center", color="0.45")
    ax.set_xlabel("Basari esigi |theta| (deg)")
    ax.set_ylabel("|dz| (etki buyuklugu)")
    ax.set_title("{} ile {} arasindaki ayrim gucu".format(
        CONDITION_ORDER[-1], base_cond), fontsize=10)
    ax.grid(alpha=0.3)

    ax = axes[2]
    ax.plot(x, sweep["tavan_pct"], marker="o", color="#c0392b", lw=2)
    ax.axvline(used, color="0.5", ls="--", lw=1)
    ax.axhline(100, color="0.75", lw=0.8, ls=":")
    ax.set_xlabel("Basari esigi |theta| (deg)")
    ax.set_ylabel("Zamanin 'basarili' sayilan yuzdesi")
    ax.set_title("Tavan etkisi\n(%100'e yaklastikca ayrim gucu duser)",
                 fontsize=10)
    ax.grid(alpha=0.3)

    fig.suptitle("Basari esigi taramasi  (kesikli cizgi = kullanilan esik, "
                 "{:.0f} deg)".format(used), fontsize=13, y=1.03)
    fig.tight_layout()
    return fig, _save(fig, "fig_threshold_sweep", cfg, base_dir)


def success_at_threshold(samples, thr, cfg):
    """Verilen basari esiginde success_time'i katilimci x kosul duzeyinde uretir.

    Ana metrik fonksiyonlarindan ayri duruyor cunku burada esik degisken.
    Donen tablo fig_metric'in bekledigi bicimde: "success_time_s" ve
    "success_time_s_sem" kolonlari + noise_level_id kategorik.

    Payda yine sabit: maske analysis_include oldugu icin reset frameleri
    disarida ve her measurement trial 20 s active sample iceriyor.
    """
    a = samples[samples["analysis_include"]].copy()
    a["_ok"] = (a["pole_angle_deg"].abs() <= thr).astype(float)
    dt = a["fixed_delta_time_s"].mean()

    per_trial = (a.groupby(["participant_id", "noise_level_id", "trial_id"],
                           observed=True)["_ok"].sum().mul(dt)
                 .rename("success_time_s").reset_index())

    g = per_trial.groupby(["participant_id", "noise_level_id"], observed=True)
    pc = pd.DataFrame({
        "success_time_s": g["success_time_s"].mean(),
        "success_time_s_sem": g["success_time_s"].sem(),
        "n_trials": g.size(),
    }).reset_index()
    pc["noise_level_id"] = pd.Categorical(pc["noise_level_id"],
                                          CONDITION_ORDER, ordered=True)
    return (pc.sort_values(["participant_id", "noise_level_id"])
              .reset_index(drop=True), per_trial)


def fig_success_all_thresholds(samples, cfg, base_dir, labels):
    """Her basari esigi icin ayri bir tam figur uretir.

    fig_metric ile ayni duzen: solda grup (spaghetti + ortalama +- SEM),
    sagda katilimci basina panel. Tek fark etiket ve dosya adinda esigin
    yazili olmasi. Dosyalar: fig_success_thr05.png, fig_success_thr10.png ...
    """
    out = []
    for thr in cfg["presentation"]["threshold_sweep_deg"]:
        pc, _ = success_at_threshold(samples, thr, cfg)
        label = "Successful stabilization (s / 20 s), |θ| ≤ {:g}°".format(thr)
        fig, path = fig_metric(pc, "success_time_s", cfg, base_dir, labels,
                               label_override=label,
                               fname="fig_success_thr{:02d}".format(int(thr)))
        out.append((thr, fig, path))
    return out
