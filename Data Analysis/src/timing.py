"""NB04 - action timing (Ludolph transferi).

Girdi: NB02 ciktisi samples_built.parquet.
Cikti: state_events.parquet, timing_cells.parquet.

Iki olay tablosu var, karistirilmamali:

  input_events (NB02, build.detect_input_events)
      GIRDI tarafinda tanimli: notr banddan cikis (onset), banda donus
      (offset), kuvvetin yon degistirmesi (reversal). Katilimcinin elinden
      cikan olaylar.

  state_events (bu modul)
      DURUM tarafinda tanimli: pole belirli bir tamsayi aciyi DUSERKEN
      geciyor. Katilimci bir sey yapmasa da olur. Ludolph'un action timing
      olcumu bu olaya gore hizalaniyor.

Yontem kararlari ve gerekceler: Documentation/Yontem/05_Action_Timing.md

Bu modul istatistiksel test YAPMAZ. dz ve profiller betimleyici.
"""

from pathlib import Path

import numpy as np
import pandas as pd

try:
    from . import performance as perf
except ImportError:                                  # notebook disi calistirma
    import performance as perf

CONDITION_ORDER = perf.CONDITION_ORDER

DT = 1.0 / 60.0

# Bir hucrede sifir gecisi aranirken kabul edilen en az segment sayisi
# config'te; buradaki sadece geriye donuk uyum icin.
_DEFAULT_MIN_SEGMENTS = 30


# --------------------------------------------------------------------------
# yardimcilar
# --------------------------------------------------------------------------

def lag_axis(cfg):
    """Segment zaman ekseni: -half .. +half, frame adimiyla."""
    half = float(cfg["timing"]["segment_half_s"])
    return np.arange(-half, half + DT / 2, DT)


def band_levels(cfg):
    """band merkezi -> o banda giren tamsayi aci seviyeleri (pozitif).

    Ludolph her tamsayi aciyi ayri olay sayiyor. Biz merkez +- yariband
    havuzluyoruz: tek acida ortalama egri bazen sifiri birden fazla
    kesiyordu (05 4), dar bant bunu tek gecise dusuruyor.
    """
    t = cfg["timing"]
    hw = int(t["band_half_width_deg"])
    return {int(c): list(range(int(c) - hw, int(c) + hw + 1))
            for c in t["band_centers_deg"]}


def _level_to_band(cfg):
    return {lv: c for c, lvs in band_levels(cfg).items() for lv in lvs}


def _contiguous_runs(sample_index):
    """sample_index'te kopukluk varsa parcala.

    analysis_include focus kaybini da eliyor; ortasi delik bir episode'da
    zaman ekseni yaniltici olur. Kesintisiz parcalar ayri ele alinir.
    """
    brk = np.flatnonzero(np.diff(sample_index) != 1) + 1
    return np.split(np.arange(len(sample_index)), brk)


# --------------------------------------------------------------------------
# 1. state_events + segmentler
# --------------------------------------------------------------------------

_META_COLS = ["session_id", "trial_order", "round_index", "noise_level_id",
              "noise_sigma"]


def build_segments(samples, cfg, mask_col="analysis_include"):
    """Dusus yonlu tamsayi aci gecisleri ve olaya ortalanmis input segmentleri.

    Ludolph (2017) s.11, adim i ve iii:
      i.   olay = pole tamsayi aciyi geciyor, alt-frame cozunurluk lineer
           interpolasyonla. Pole yukari donuyorsa gecis atilir.
      iii. olaya ortalanmis +-0.5 s'lik input segmenti.

    Bizim iki eklememiz (05 3.5 ve 3.6):
      - segment kesintisiz aktif parcanin disina tasiyorsa TAMAMEN atilir
        (reset satirlarinda applied_force_n sifira zorlanmis, sahte).
      - negatif acilarin segmentleri isaret cevrilerek havuzlanir; +10 ile
        -10 ayni olayin aynasi.

    Doner: (events, X)
      events : olay basina satir; atilanlar dahil (segment_fits sutunu).
      X      : events[events.segment_fits] ile AYNI SIRADA, isaret
               hizalanmis segment matrisi (n_segment x len(lag_axis)).
    """
    lags = lag_axis(cfg)
    half = float(cfg["timing"]["segment_half_s"])
    lv2band = _level_to_band(cfg)
    levels = sorted(lv2band)
    levels = [s * lv for lv in levels for s in (+1, -1)]

    df = samples[samples[mask_col]] if mask_col else samples
    cols = ["sample_index", "t_trial_s", "pole_angle_deg",
            "pole_angular_velocity_deg_s", "input_applied"]

    rows, segs = [], []
    for (pid, tid, ep), g in df.groupby(["participant_id", "trial_id",
                                         "episode"], sort=False):
        si, t, th, om, u = (g[c].to_numpy() for c in cols)
        meta = {c: g[c].iloc[0] for c in _META_COLS}

        for run_no, r in enumerate(_contiguous_runs(si)):
            if r.size < 4:
                continue
            tr, thr, omr, ur = t[r], th[r], om[r], u[r]
            t0, t1 = tr[0], tr[-1]

            for L in levels:
                d = thr - L
                for i in np.flatnonzero(d[:-1] * d[1:] < 0):
                    frac = -d[i] / (d[i + 1] - d[i])
                    om_ev = omr[i] + frac * (omr[i + 1] - omr[i])
                    if L * om_ev <= 0:          # yukari donuyor, elenir
                        continue
                    t_ev = tr[i] + frac * (tr[i + 1] - tr[i])
                    fits = (t_ev - half >= t0) and (t_ev + half <= t1)
                    if fits:
                        segs.append(np.sign(L) *
                                    np.interp(t_ev + lags, tr, ur))
                    rows.append({
                        "participant_id": pid, "trial_id": tid, "episode": ep,
                        "run_index": run_no, **meta,
                        "angle_level": L, "abs_level": abs(L),
                        "band_center": lv2band[abs(L)],
                        "t_event_s": t_ev,
                        "omega_event": om_ev, "abs_omega_event": abs(om_ev),
                        "u_at_event": np.interp(t_ev, tr, ur) * np.sign(L),
                        "segment_fits": fits,
                    })

    events = pd.DataFrame(rows)
    if events.empty:
        return events, np.empty((0, lags.size), dtype=np.float32)
    events["noise_level_id"] = pd.Categorical(events["noise_level_id"],
                                              CONDITION_ORDER, ordered=True)
    X = np.asarray(segs, dtype=np.float32)
    return events, X


def segment_meta(events):
    """X ile ayni sirada, satir konumu = X satir konumu olan olay tablosu."""
    return events[events.segment_fits].reset_index(drop=True)


# --------------------------------------------------------------------------
# 2. hiz tabakalama
# --------------------------------------------------------------------------

def add_velocity_strata(events, cfg):
    """|omega| kuantillerine gore yavas / orta / hizli tabakalari.

    Ludolph %20-%80 disini ATIYOR. Biz atmiyoruz, tabakaliyoruz (05 3.3):
    orta bant onun sakladigi kume, diger ikisi ayrica raporlanabiliyor.

    Kuantil KATILIMCI x ACI SEVIYESI icinde, butun kosullar havuzlanarak
    hesaplanir. Kosul icinden hesaplansaydi eleme kosula uyarlanirdi ve
    artik ayni hiz bandi karsilastirilmazdi -- gurultu hiz dagilimini
    degistiriyorsa bu dogrudan confound olurdu.
    """
    q_lo, q_hi = cfg["timing"]["velocity_quantiles"]
    ev = events.copy()
    g = ev.groupby(["participant_id", "abs_level"], observed=True)["abs_omega_event"]
    lo = g.transform(lambda s: s.quantile(q_lo))
    hi = g.transform(lambda s: s.quantile(q_hi))
    ev["omega_q_lo"], ev["omega_q_hi"] = lo, hi
    ev["vel_stratum"] = np.where(ev.abs_omega_event < lo, "slow",
                          np.where(ev.abs_omega_event > hi, "fast", "mid"))
    ev["vel_stratum"] = pd.Categorical(ev["vel_stratum"],
                                       ["slow", "mid", "fast"], ordered=True)
    return ev


def velocity_by_condition(events, cfg=None):
    """Confound kontrolu: gurultu olay anindaki |omega| dagilimini degistiriyor mu.

    Degistiriyorsa tabakalar arasi karsilastirma da kosula bulasir.
    Katilimci ici merkezlenmis ortalama ile bakilir.
    """
    g = events.groupby(["participant_id", "noise_level_id"],
                       observed=True)["abs_omega_event"]
    pc = g.mean().rename("abs_omega").reset_index()
    pc["centered"] = pc["abs_omega"] - pc.groupby("participant_id")["abs_omega"].transform("mean")
    out = pc.groupby("noise_level_id", observed=True).agg(
        n_katilimci=("abs_omega", "size"),
        ortalama=("abs_omega", "mean"),
        merkezlenmis=("centered", "mean"),
    )
    return out.round(3)


# --------------------------------------------------------------------------
# 3. egri istatistikleri
# --------------------------------------------------------------------------

def zero_crossings(y, lags):
    """(lag, egim) ciftleri. Lineer interpolasyonla alt-frame."""
    s = np.sign(y)
    out = []
    for i in np.flatnonzero(s[:-1] * s[1:] < 0):
        step = lags[i + 1] - lags[i]
        out.append((lags[i] + step * (-y[i] / (y[i + 1] - y[i])),
                    (y[i + 1] - y[i]) / step))
    return out


def pick_crossing(y, lags):
    """Action timing olarak hangi gecis alinir.

    Isaret hizalandigi icin duzeltici kuvvet negatiften pozitife gecer;
    yani aranan gecis YUKSELEN olan. Birden fazla varsa EN DIK yukselen
    secilir (05 4). Hic yukselen yoksa NaN doner.
    """
    zcs = zero_crossings(y, lags)
    rising = [z for z in zcs if z[1] > 0]
    if not rising:
        return np.nan, len(zcs), 0, np.nan
    z, slope = max(rising, key=lambda p: p[1])
    return z, len(zcs), len(rising), slope


def curve_stats(S, cfg, lags=None):
    """Bir segment kumesinin ortalama egrisinden action timing olcutleri."""
    lags = lag_axis(cfg) if lags is None else lags
    n = S.shape[0]
    out = {"n_segment": n, "zc_ms": np.nan, "n_crossing": np.nan,
           "n_rising": np.nan, "slope": np.nan, "amplitude": np.nan,
           "sem_max": np.nan, "amp_over_sem": np.nan, "variability": np.nan,
           "var_norm": np.nan, "mean_pre": np.nan, "mean_post": np.nan,
           "zero_frac": np.nan, "reversal_ok": False, "guvenilir": False}
    if n == 0:
        return out

    m = S.mean(axis=0)
    z, n_cross, n_rise, slope = pick_crossing(m, lags)
    sd = S.std(axis=0, ddof=1) if n > 1 else np.zeros_like(m)
    amp = float(m.max() - m.min())
    sem_max = float((sd / np.sqrt(n)).max()) if n > 1 else np.nan

    out.update(zc_ms=z * 1000 if np.isfinite(z) else np.nan,
               n_crossing=n_cross, n_rising=n_rise, slope=slope,
               amplitude=amp, sem_max=sem_max,
               amp_over_sem=amp / sem_max if sem_max else np.nan,
               mean_pre=float(m[0]), mean_post=float(m[-1]),
               zero_frac=float((S == 0).mean()),
               reversal_ok=bool(m[0] < 0 < m[-1]))

    # action variability: sifir gecisi cevresinde +-w icinde, segmentler
    # arasi standart sapmanin ortalamasi (Ludolph, s.11).
    if np.isfinite(z) and n > 1:
        w = float(cfg["timing"]["variability_window_s"])
        sel = np.abs(lags - z) <= w
        if sel.any():
            out["variability"] = float(sd[sel].mean())
            out["var_norm"] = out["variability"] / amp if amp else np.nan

    # Olcut sadece gercek bir yon degistirme varsa tanimli. Yavas gecis
    # tabakasinda ortalama egri bastan sona pozitif kaliyor (NB04 6):
    # orada "sifir gecisi" sadece duz egrinin gurultusu olur.
    out["guvenilir"] = bool(out["reversal_ok"] and np.isfinite(out["zc_ms"])
                            and out["amp_over_sem"] >=
                            float(cfg["timing"]["min_amp_sem_ratio"]))
    return out


def bootstrap_zc(S, cfg, n_boot=None, seed=0, lags=None):
    """Sifir gecisinin segment orneklemesine duyarliligi (yuzdelik CI)."""
    lags = lag_axis(cfg) if lags is None else lags
    n_boot = int(cfg["timing"]["bootstrap_n"] if n_boot is None else n_boot)
    n = S.shape[0]
    if n < 2 or n_boot < 1:
        return {"zc_lo_ms": np.nan, "zc_hi_ms": np.nan, "n_boot_ok": 0}
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(n_boot):
        z, *_ = pick_crossing(S[rng.integers(0, n, n)].mean(axis=0), lags)
        if np.isfinite(z):
            vals.append(z * 1000)
    if not vals:
        return {"zc_lo_ms": np.nan, "zc_hi_ms": np.nan, "n_boot_ok": 0}
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return {"zc_lo_ms": float(lo), "zc_hi_ms": float(hi), "n_boot_ok": len(vals)}


# --------------------------------------------------------------------------
# 4. hucre tablolari
# --------------------------------------------------------------------------

def timing_cells(meta, X, keys, cfg, min_segments=None):
    """Verilen anahtarlara gore hucre hucre action timing.

    keys ornek: ["participant_id", "noise_level_id"] ya da
    ["participant_id", "trial_window"]. meta, segment_meta() ciktisi
    olmali -- satir konumu X'in satir konumuyla ayni.
    """
    lags = lag_axis(cfg)
    if min_segments is None:
        min_segments = int(cfg["timing"].get("min_segments",
                                             _DEFAULT_MIN_SEGMENTS))
    keys = list(keys)
    rows = []
    for k, sub in meta.groupby(keys, observed=True, sort=True):
        k = k if isinstance(k, tuple) else (k,)
        pos = sub.index.to_numpy()
        if pos.size < min_segments:
            rows.append({**dict(zip(keys, k)), "n_segment": pos.size,
                         "yetersiz": True})
            continue
        st = curve_stats(X[pos], cfg, lags)
        rows.append({**dict(zip(keys, k)), **st, "yetersiz": False})
    out = pd.DataFrame(rows)
    if "noise_level_id" in out.columns:
        out["noise_level_id"] = pd.Categorical(out["noise_level_id"],
                                               CONDITION_ORDER, ordered=True)
    return out


def add_trial_window(meta, cfg):
    """Ogrenme ekseni: trial_order'i esit pencerelere boler.

    Duvar saati yok (05 3.1); trial_order zaten sirali bir zaman ekseni.
    Ludolph'un 2 dakikalik penceresi bizde ~6 denemeye denk geliyor.
    """
    size = int(cfg["timing"]["trial_window_size"])
    m = meta.copy()
    first = int(m["trial_order"].min())
    idx = ((m["trial_order"] - first) // size).astype(int)
    lo = first + idx * size
    m["trial_window"] = pd.Categorical(
        [f"{a}-{a + size - 1}" for a in lo],
        [f"{a}-{a + size - 1}" for a in sorted(lo.unique())], ordered=True)
    return m


def window_profile(cells, value_col="zc_ms"):
    """Ogrenme ekseni profili. Ortalama VE medyan.

    Medyan onemli: ortalama, birkac kisinin buyuk kaymasiyla surukleniyor
    olabilir (NB04 5'te tam da bu oldu).
    """
    c = cells.dropna(subset=[value_col])
    return c.groupby("trial_window", observed=True).agg(
        n_katilimci=(value_col, "size"),
        segment=("n_segment", "mean"),
        ortalama=(value_col, "mean"),
        medyan=(value_col, "median"),
        sd=(value_col, "std"),
    ).round(2)


def learning_slopes(cells, value_col="zc_ms"):
    """Katilimci basina pencereler boyunca dogrusal egim (ms / pencere).

    Ilk-son farki en gurultulu ozet; butun pencereleri kullanan egim daha
    saglam. Doner: (kisi basina egim tablosu, ozet Series).
    """
    w = cells.pivot(index="participant_id", columns="trial_window",
                    values=value_col)
    x = np.arange(w.shape[1], dtype=float)
    x -= x.mean()
    rows = []
    for p, r in w.iterrows():
        y = r.to_numpy(dtype=float)
        ok = np.isfinite(y)
        if ok.sum() < 3:
            continue
        rows.append({"participant_id": p,
                     "egim_ms_pencere": np.polyfit(x[ok], y[ok], 1)[0],
                     "ilk": y[ok][0], "son": y[ok][-1]})
    s = pd.DataFrame(rows).set_index("participant_id")
    d = s["egim_ms_pencere"]
    ozet = pd.Series({
        "ortalama_egim": d.mean(), "medyan_egim": d.median(),
        "sd": d.std(ddof=1), "dz": d.mean() / d.std(ddof=1),
        "negatif_yonde": int((d < 0).sum()), "n": len(d),
    }).round(3)
    return s.round(1), ozet


def event_context(samples, event, n=4, mask_col="analysis_include"):
    """Bir state_event'in cevresindeki ham satirlar -- olayin ne oldugunu gormek icin."""
    df = samples[samples[mask_col]] if mask_col else samples
    g = df[(df.participant_id == event.participant_id)
           & (df.trial_id == event.trial_id)
           & (df.episode == event.episode)]
    i = int(np.argmin(np.abs(g["t_trial_s"].to_numpy() - event.t_event_s)))
    sl = g.iloc[max(0, i - n): i + n + 1]
    out = sl[["sample_index", "t_trial_s", "pole_angle_deg",
              "pole_angular_velocity_deg_s", "input_applied", "action"]].copy()
    out["olaya_gore_ms"] = ((out["t_trial_s"] - event.t_event_s) * 1000).round(1)
    return out.round(3)


def band_sweep(meta, X, keys, cfg, value_col="zc_ms"):
    """Ayni analizi her aci bandinda tekrarlar.

    Aci sabitlenmeden karsilastirma yapilmaz (05 6): bantlar arasi DEGER
    farki geometri, yorumlanmaz. Bakilan sey, kosul/deneme ORUNTUSUNUN
    bantlar arasinda tekrarlayip tekrarlamadigi.
    """
    rows = []
    for c in cfg["timing"]["band_centers_deg"]:
        mb = meta[meta.band_center == c]
        Xb = X[mb.index.to_numpy()]
        cells = timing_cells(mb.reset_index(drop=True), Xb, keys, cfg)
        prof = cells.groupby(keys[-1], observed=True)[value_col].mean()
        rows.append({"bant": c, "segment": Xb.shape[0],
                     "havuz_zc_ms": curve_stats(Xb, cfg)["zc_ms"],
                     **{str(k): v for k, v in prof.items()}})
    return pd.DataFrame(rows).set_index("bant").round(1)


def condition_profile(cells, value_col="zc_ms"):
    """Kosul profili, katilimci ici merkezlenmis (NB03 ile ayni olcek)."""
    c = cells.dropna(subset=[value_col]).copy()
    c["centered"] = c[value_col] - c.groupby("participant_id")[value_col].transform("mean")
    out = c.groupby("noise_level_id", observed=True).agg(
        n_katilimci=(value_col, "size"),
        ham=(value_col, "mean"),
        merkezlenmis=("centered", "mean"),
        sem=("centered", "sem"),
        segment=("n_segment", "sum"),
    )
    return out.round(3)


def spread_comparison(cells, value_col="zc_ms"):
    """Kosul yayilimi mi kisi yayilimi mi buyuk.

    05 5'teki gozlem: bireysel farklar kosul farkindan bir mertebe buyuk.
    Bu tabloyu sayiyla kurmak icin.
    """
    c = cells.dropna(subset=[value_col])
    per_p = c.groupby("participant_id", observed=True)[value_col].mean()
    prof = condition_profile(c, value_col)["merkezlenmis"]
    return pd.Series({
        "kisi_ortalamasi_min": per_p.min(),
        "kisi_ortalamasi_max": per_p.max(),
        "kisi_yayilimi": per_p.max() - per_p.min(),
        "kisi_sd": per_p.std(ddof=1),
        "kosul_yayilimi": prof.max() - prof.min(),
        "kosul_sd": prof.std(ddof=1),
    }).round(2)


# --------------------------------------------------------------------------
# cikti
# --------------------------------------------------------------------------

def save_outputs(events, cells, interim_dir):
    interim_dir = Path(interim_dir)
    e = events.copy()
    c = cells.copy()
    for d in (e, c):
        for col in ("noise_level_id", "vel_stratum", "trial_window"):
            if col in d.columns:
                d[col] = d[col].astype(str)
    e.to_parquet(interim_dir / "state_events.parquet", index=False)
    c.to_parquet(interim_dir / "timing_cells.parquet", index=False)
    return {"state_events.parquet": len(e), "timing_cells.parquet": len(c)}
