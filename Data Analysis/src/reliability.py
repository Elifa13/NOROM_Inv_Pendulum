"""Kisi ici guvenilirlik: varyans ayrisimi, ICC(2,1) ve split-half.

Girdi: katilimci x kosul tablosu (decompose) ya da trial duzeyi tablo
(split_half). Bu modul veri okumaz, dosya yazmaz; verilen tabloyu hesaplar.

Kaynak: bu fonksiyonlar 92_varyans_ayrisimi.ipynb icinde yazildi. NB91 de
ayni hesaba ihtiyac duyunca kopyalamak yerine buraya tasindi. NB92'deki
global sabitler (COND, SEED, N_SPLIT, LABEL) burada acik parametre; hepsinin
varsayilani NB92'deki degerin aynisi, yani NB92'nin sonuclari degismez.

Bu modul istatistiksel karar VERMEZ. ICC ve split-half betimleyici; hangi
olcutun raporlanabilir oldugu notebook'ta degerlendirilir.
"""

import warnings

import numpy as np
import pandas as pd
from scipy import stats

# NB92'deki global sabitlerin aynisi.
COND_DEFAULT = ["no_noise", "N1", "N2", "N3", "N4"]
N_SPLIT_DEFAULT = 200          # split-half tekrar sayisi
SEED_DEFAULT = 0


def decompose(W):
    """Dengeli kisi x kosul tablosunda varyans ayrisimi + ICC(2,1).

    W: satir = katilimci, sutun = kosul, NaN icermeyen pivot tablo.
    """
    X = W.values.astype(float)
    n, k = X.shape
    g = X.mean()
    SSp = k * ((X.mean(axis=1) - g) ** 2).sum()
    SSc = n * ((X.mean(axis=0) - g) ** 2).sum()
    SSt = ((X - g) ** 2).sum()
    SSr = SSt - SSp - SSc

    MSp = SSp / (n - 1)
    MSc = SSc / (k - 1)
    MSr = SSr / ((n - 1) * (k - 1))
    var_p = max((MSp - MSr) / k, 0.0)
    icc = var_p / (var_p + MSr) if (var_p + MSr) > 0 else np.nan

    # Ayni kareler toplamindan repeated-measures ANOVA'nin kosul F testi cikar.
    F = MSc / MSr if MSr > 0 else np.nan
    p_anova = float(stats.f.sf(F, k - 1, (n - 1) * (k - 1))) if np.isfinite(F) else np.nan
    # Friedman: karsilastirma icin, ayni tablo uzerinde
    p_fried = float(stats.friedmanchisquare(*X.T).pvalue)
    # normallik: kisi ici merkezlenmis artiklar
    resid = (X - X.mean(axis=1, keepdims=True)).ravel()
    p_shapiro = float(stats.shapiro(resid).pvalue)

    return dict(kisi_pct=100 * SSp / SSt, kosul_pct=100 * SSc / SSt,
                artik_pct=100 * SSr / SSt, ICC=icc,
                F_anova=F, p_anova=p_anova, p_friedman=p_fried,
                p_shapiro=p_shapiro, n=n, k=k)


def cell_table(df, metric, index="participant_id", col="noise_level_id",
               cond=None):
    cond = COND_DEFAULT if cond is None else cond
    return df.pivot(index=index, columns=col, values=metric)[cond].dropna()


def split_half(df, metric, seed, cond=None, index="participant_id",
               col="noise_level_id"):
    """Her kisi x kosul hucresindeki trial'lari rastgele iki yariya bol.

    Iki yarinin ortalamalarindan iki ayri kisi x kosul tablosu dondurur.
    """
    cond = COND_DEFAULT if cond is None else cond
    r = np.random.default_rng(seed)
    A, B = {}, {}
    for (p, c), g in df.groupby([index, col]):
        v = g[metric].values
        idx = r.permutation(len(v))
        h = len(v) // 2
        A[(p, c)] = v[idx[:h]].mean()
        B[(p, c)] = v[idx[h:2 * h]].mean()
    a = pd.Series(A).unstack()[cond]
    b = pd.Series(B).unstack()[cond]
    return a, b


def split_half_stats(df, metric, n_rep=N_SPLIT_DEFAULT, sign=-1,
                     seed=SEED_DEFAULT, cond=None, label=None,
                     index="participant_id", col="noise_level_id"):
    """sign=-1: dusuk deger iyi (en iyi = argmin). sign=+1: yuksek deger iyi.

    Bir kisinin bir yaridaki 5 kosul degeri tamamen ayni cikarsa Spearman
    tanimsiz olur (ornegin dusus sayisi hepsinde 0). O kisi o tekrarda
    siralama hesabindan dusulur; tanimsiz_pct bunun ne siklikta oldugunu sayar.

    label verilmezse olcut adi oldugu gibi kullanilir. sign sadece
    ayni_en_iyi_pct'yi etkiler; olcutun "iyi" yonu tanimsizsa o kolon
    anlamsizdir, digerleri etkilenmez.
    """
    cond = COND_DEFAULT if cond is None else cond
    same, rho, rp, nan_n, tot_n = [], [], [], 0, 0
    best = np.argmin if sign < 0 else np.argmax
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for s in range(n_rep):
            a, b = split_half(df, metric, seed + s, cond=cond,
                              index=index, col=col)
            same.append((best(a.values, axis=1) == best(b.values, axis=1)).mean())
            r = np.array([stats.spearmanr(a.values[i], b.values[i]).statistic
                          for i in range(len(a))])
            nan_n += int(np.isnan(r).sum())
            tot_n += len(r)
            rho.append(np.nanmean(r) if np.isfinite(r).any() else np.nan)
            rp.append(stats.pearsonr(a.mean(axis=1), b.mean(axis=1)).statistic)
    return dict(olcut=metric if label is None else label,
                genel_seviye_r=np.nanmean(rp),
                kosul_siralamasi_rho=np.nanmean(rho),
                ayni_en_iyi_pct=100 * np.mean(same),
                tanimsiz_pct=100 * nan_n / tot_n)
