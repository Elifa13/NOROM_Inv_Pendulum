"""NB06 - noise seviyesi karari.

Girdi: NB03 ciktilari (trial_metrics.parquet, participant_condition.parquet)
       + esik duyarliligi icin samples_built / episodes.
Cikti: decision_stats.csv, decision_table.csv.

NB03 betimleyiciydi (profil, dz, kac katilimcida ayni yon). Test bu modulde.
Analiz birimi katilimci x kosul; butun testler within-subject ve
parametrik degil (n = 12).

presentation.py'de benzer bir stats_table var; o IZOLE sunum notebook'una
ait ve butun metrikleri dolasir. Buradaki karar metrik setiyle sinirli,
etki buyuklugu ve duyarlilik kontrolleri ekli.

Stochastic resonance testi = KUADRATIK kontrast. Lineer kontrast "gurultu
arttikca duzenli bir gidis var mi", kuadratik "ortada tepe/cukur var mi"
sorusudur; SR hipotezi ikincisinde gorunurdu.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

try:
    from . import performance as perf
except ImportError:                                  # notebook disi calistirma
    import performance as perf

CONDITION_ORDER = perf.CONDITION_ORDER
METRIC_INFO = perf.METRIC_INFO

# NB03'un sectigi karar seti. Yon: -1 kucuk iyi, +1 buyuk iyi, 0 belirsiz.
DECISION_METRICS = ["mae_angle_deg", "stab_time_s", "falls_angle_per_trial"]
TIEBREAK_METRICS = ["control_effort", "cart_rms_m"]

# 5 seviye icin ortogonal polinom kontrastlari (ordinal pozisyon uzerinden;
# sigma degerleri esit arali degil ve sifir icerdigi icin log alinamiyor).
_LINEAR = np.array([-2, -1, 0, 1, 2], dtype=float)
_QUADRATIC = np.array([2, -1, -2, -1, 2], dtype=float)


# --------------------------------------------------------------------------
# yardimcilar
# --------------------------------------------------------------------------

def _wide(pc, metric):
    """katilimci x kosul matrisi, kosul sirasi sabit, eksigi olan satir atilir."""
    return (pc.pivot(index="participant_id", columns="noise_level_id",
                     values=metric)
              .reindex(columns=CONDITION_ORDER)
              .dropna())


def _holm(pvals):
    """Holm-Bonferroni duzeltmesi. Aile = bir metrigin baseline karsilastirmalari."""
    p = np.asarray(pvals, dtype=float)
    order = np.argsort(p)
    m = len(p)
    adj = np.empty(m)
    running = 0.0
    for i, idx in enumerate(order):
        running = max(running, (m - i) * p[idx])
        adj[idx] = min(running, 1.0)
    return adj


def kendall_w(chi2, n, k):
    """Friedman etki buyuklugu: 0 = uyum yok, 1 = tam uyum."""
    return float(chi2 / (n * (k - 1)))


def rank_biserial(d):
    """Eslesmis Wilcoxon icin etki buyuklugu.

    Sifir olmayan farklarin |d| siralamasinda pozitiflerin payi eksi
    negatiflerin payi. -1..+1; isaret farkin yonunu verir.
    """
    d = np.asarray(d, dtype=float)
    d = d[d != 0]
    if d.size == 0:
        return np.nan
    r = stats.rankdata(np.abs(d))
    total = r.sum()
    return float((r[d > 0].sum() - r[d < 0].sum()) / total)


def _wilcoxon_p(x, y=None):
    try:
        return float(stats.wilcoxon(x, y).pvalue)
    except ValueError:                               # butun farklar sifir
        return 1.0


# --------------------------------------------------------------------------
# 1. omnibus + baseline karsilastirmalari
# --------------------------------------------------------------------------

def omnibus_table(pc, metrics=None):
    """Friedman: bes kosul arasinda herhangi bir fark var mi."""
    metrics = DECISION_METRICS + TIEBREAK_METRICS if metrics is None else metrics
    rows = []
    for m in metrics:
        w = _wide(pc, m)
        arr = w.to_numpy(dtype=float)
        chi2, p = stats.friedmanchisquare(*arr.T)
        rows.append({
            "metrik": METRIC_INFO.get(m, (m, 0))[0],
            "kolon": m,
            "n": len(w),
            "friedman_chi2": round(float(chi2), 3),
            "p": float(p),
            "kendall_W": round(kendall_w(chi2, len(w), arr.shape[1]), 3),
        })
    return pd.DataFrame(rows).set_index("kolon")


def baseline_tests(pc, metric, cfg):
    """Her noise kosulu baseline'a karsi: Wilcoxon + Holm + etki buyuklugu."""
    base = cfg["performance"]["baseline_condition"]
    direction = METRIC_INFO.get(metric, ("", 0))[1]
    w = _wide(pc, metric)
    others = [c for c in CONDITION_ORDER if c != base]

    raw, rows = [], []
    for c in others:
        d = (w[c] - w[base]).to_numpy(dtype=float)
        p = _wilcoxon_p(w[c], w[base])
        raw.append(p)
        sd = d.std(ddof=1)
        rows.append({
            "kosul": c,
            "fark": round(float(d.mean()), 4),
            "dz": round(float(d.mean() / sd), 3) if sd > 0 else np.nan,
            "rank_biserial": round(rank_biserial(d), 3),
            "n_kotu": int((d * direction < 0).sum()) if direction else np.nan,
            "p": p,
        })
    out = pd.DataFrame(rows)
    out["p_holm"] = _holm(raw)
    return out.set_index("kosul")


# --------------------------------------------------------------------------
# 2. trend kontrastlari -- SR testi burada
# --------------------------------------------------------------------------

def contrast_tests(pc, metrics=None):
    """Lineer ve kuadratik ortogonal kontrast.

    Her katilimcinin bes kosul degerine kontrast agirliklari uygulanip tek
    bir skor cikariliyor, sonra skorlar uzerinde tek orneklem Wilcoxon.
    Kuadratik = U/ters-U testi = stochastic resonance testi.
    """
    metrics = DECISION_METRICS + TIEBREAK_METRICS if metrics is None else metrics
    rows = []
    for m in metrics:
        w = _wide(pc, m)
        arr = w.to_numpy(dtype=float)
        lin, quad = arr @ _LINEAR, arr @ _QUADRATIC
        rows.append({
            "metrik": METRIC_INFO.get(m, (m, 0))[0],
            "kolon": m,
            "yon": METRIC_INFO.get(m, ("", 0))[1],
            "lineer": round(float(lin.mean()), 4),
            "lineer_p": _wilcoxon_p(lin),
            "lineer_n_ayni_yon": int((np.sign(lin) == np.sign(lin.mean())).sum()),
            "kuadratik": round(float(quad.mean()), 4),
            "kuadratik_p": _wilcoxon_p(quad),
            "n": len(w),
        })
    return pd.DataFrame(rows).set_index("kolon")


# --------------------------------------------------------------------------
# 3. U sekli: kuadratik testin yaninda dogrudan kontrol
# --------------------------------------------------------------------------

def interior_optimum(pc, metrics=None, cfg=None):
    """Kontrast testinden bagimsiz, dogrudan bakis: en iyi kosul icerde mi.

    Stochastic resonance ic kosullardan birinin (N1..N3) baseline'dan da
    N4'ten de iyi olmasini gerektirir. Iki sey sayiliyor:
      - grup ortalamasinda en iyi kosul hangisi
      - kac katilimcinin kendi en iyisi bir IC kosul
    """
    metrics = DECISION_METRICS if metrics is None else metrics
    interior = ["N1", "N2", "N3"]
    rows = []
    for m in metrics:
        direction = METRIC_INFO.get(m, ("", 0))[1]
        w = _wide(pc, m)
        means = w.mean()
        best = means.idxmax() if direction > 0 else means.idxmin()
        per_p = w.idxmax(axis=1) if direction > 0 else w.idxmin(axis=1)
        rows.append({
            "metrik": METRIC_INFO.get(m, (m, 0))[0],
            "kolon": m,
            "grup_en_iyi": best,
            "grup_en_iyi_ic_mi": best in interior,
            "kisi_en_iyisi_ic": int(per_p.isin(interior).sum()),
            "n": len(w),
            "kisi_dagilimi": ", ".join(f"{k}:{v}" for k, v in
                                       per_p.value_counts().items()),
        })
    return pd.DataFrame(rows).set_index("kolon")


def personal_best(pc, metrics=None, cfg=None):
    """Katilimci basina composite en iyi kosul.

    Her metrik katilimci icinde z-skora cevrilip yonune gore isaretleniyor,
    sonra metrikler ortalanip en yuksek skorlu kosul aliniyor.
    """
    metrics = DECISION_METRICS if metrics is None else metrics
    parts = []
    for m in metrics:
        w = _wide(pc, m)
        z = w.sub(w.mean(axis=1), axis=0).div(w.std(axis=1, ddof=1), axis=0)
        parts.append(z * METRIC_INFO.get(m, ("", 0))[1])
    comp = sum(parts) / len(parts)
    best = comp.idxmax(axis=1)
    out = comp.round(3)
    out["en_iyi"] = best
    return out


# --------------------------------------------------------------------------
# 4. karar tablosu
# --------------------------------------------------------------------------

def decision_table(pc, metrics=None):
    """Kosul x metrik: katilimci ortalamalarinin ortalamasi +- SEM."""
    metrics = DECISION_METRICS + TIEBREAK_METRICS if metrics is None else metrics
    g = pc.groupby("noise_level_id", observed=True)
    mean, sem = g[metrics].mean().T, g[metrics].sem().T
    out = mean.round(3).astype(str) + " ±" + sem.round(3).astype(str)
    out.insert(0, "yon", [METRIC_INFO.get(m, ("", 0))[1] for m in mean.index])
    out.index = [METRIC_INFO.get(m, (m, 0))[0] for m in mean.index]
    return out


def condition_ranks(pc, metrics=None):
    """Her metrikte kosullari 1 (en iyi) .. 5 (en kotu) diye siralar."""
    metrics = DECISION_METRICS if metrics is None else metrics
    rows = {}
    for m in metrics:
        means = _wide(pc, m).mean()
        asc = METRIC_INFO.get(m, ("", 0))[1] < 0        # kucuk iyi -> artan
        rows[METRIC_INFO.get(m, (m, 0))[0]] = means.rank(ascending=asc)
    out = pd.DataFrame(rows).T
    out.loc["ortalama sira"] = out.mean()
    return out.round(2)


# --------------------------------------------------------------------------
# 5. duyarlilik kontrolleri
# --------------------------------------------------------------------------

def drop_invalid_trials(trial_df, trials_clean):
    """Unity'nin valid_trial == 0 dedigi trial'lari cikarir.

    NB01'in `flag_trials`'i bu kolona bakmiyor (bilinen acik, madde 4);
    600 trial'in 2'si etkileniyor (P011 T030, T034, "paused"). Burada
    karar bu iki trial'a duyarli mi diye bakiliyor.
    """
    bad = trials_clean.loc[trials_clean["valid_trial"] == 0,
                           ["participant_id", "trial_id"]]
    key = set(map(tuple, bad.to_numpy()))
    mask = [tuple(r) not in key for r in
            trial_df[["participant_id", "trial_id"]].to_numpy()]
    return trial_df[mask].reset_index(drop=True), len(bad)


def stab_time_at(samples, threshold_deg, trial_duration_s):
    """Verilen esikle trial basina stabilizasyon suresi (saniye)."""
    a = samples[samples["analysis_include"]]
    keys = ["participant_id", "noise_level_id", "trial_id"]
    g = a.assign(_w=(a["pole_angle_deg"].abs() <= threshold_deg).astype(float)
                 ).groupby(keys, observed=True)
    out = (g["_w"].sum() * g["fixed_delta_time_s"].mean()).rename("stab_time_s")
    return out.reset_index()


def threshold_sensitivity(samples, cfg, thresholds):
    """Karar, stabilizasyon esigi secimine duyarli mi.

    Esik bizim kararimiz (kayittaki within_bounds_time_s tavana yapisik,
    bkz. NB03). Farkli esiklerde kosul sirasi ve trend testleri degisiyorsa
    metrigin kendisi kirilgan demektir.
    """
    rows = []
    for thr in thresholds:
        st = stab_time_at(samples, thr, cfg["performance"]["trial_duration_s"])
        pcx = (st.groupby(["participant_id", "noise_level_id"], observed=True)
                 ["stab_time_s"].mean().reset_index())
        w = _wide(pcx, "stab_time_s")
        arr = w.to_numpy(dtype=float)
        lin, quad = arr @ _LINEAR, arr @ _QUADRATIC
        means = w.mean()
        rows.append({
            "esik_deg": thr,
            "ortalama_s": round(float(means.mean()), 2),
            "en_iyi_kosul": means.idxmax(),
            "lineer": round(float(lin.mean()), 3),
            "lineer_p": _wilcoxon_p(lin),
            "kuadratik_p": _wilcoxon_p(quad),
        })
    return pd.DataFrame(rows).set_index("esik_deg")


# --------------------------------------------------------------------------
# cikti
# --------------------------------------------------------------------------

def save_outputs(stats_df, table_df, interim_dir, processed_dir=None):
    out_dir = Path(processed_dir if processed_dir else interim_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stats_df.to_csv(out_dir / "decision_stats.csv", encoding="utf-8")
    table_df.to_csv(out_dir / "decision_table.csv", encoding="utf-8")
    return {"decision_stats.csv": len(stats_df),
            "decision_table.csv": len(table_df),
            "dizin": str(out_dir)}
