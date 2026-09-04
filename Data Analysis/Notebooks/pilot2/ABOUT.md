# Notebooks / pilot2

Bir üst klasördeki zincirin **pilot2** verisi için kopyası. 9 katılımcı
(P001–P009), 2–3 Eylül 2026, noise σ 0 / .005 / .010 / .015 / .020.

Tek yapısal fark ilk hücredeki `DATASET = "pilot2"`. Mantık gene `../../src/`
altında, hiçbir modül çoğaltılmadı — analiz kodu sigmayı veriden okuyor,
koşul etiketleri iki sette de aynı beş isim.

| # | Notebook | Durum |
|---|---|---|
| 01 | `01_load_qc.ipynb` | çalıştı — 9 oturum, 477 trial, QC FAIL 0 |
| 02 | `02_build.ipynb` | çalıştı — 1.332 episode, 15.133 regime run, T₀ doğrulandı |
| 03 | `03_performance.ipynb` | çalıştı — 450 measurement trial, 45 hücre |
| 04 | `04_control.ipynb` | çalıştı — zero crossing −43.5 ms, koşul etkisi yok |
| 06 | `06_noise_decision.ipynb` | çalıştı — bütün testler null |
| 91 | `91_control_variability.ipynb` | çalıştı — koşul etkisi yok |
| 92 | `92_varyans_ayrisimi.ipynb` | çalıştı — koşulun payı %0.2 |
| 93 | `93_ogrenme_ve_varyans.ipynb` | çalıştı — öğrenme var, koşuldan bağımsız |

90 (sunum) kopyalanmadı.

**İki koda özel fark** (pilot1 kopyasında yok):

- NB04'te öğrenme kaymasının aykırı kişi kontrolü. Pilot1'de liste elle
  `["P007", "P012"]` yazılmıştı; burada ortalama zero crossing'i medyandan
  en çok sapan iki kişi veriden seçiliyor (pilot2'de P002 ve P001).

Sonuçların yorumu: `../../../Documentation/Pilot2_Sonuc_Ozeti.md`.
Yöntem gerekçeleri (iki set için de aynı): `../../../Documentation/Yontem/`.

**Uyarı.** Pilot1 ile pilot2 katılımcı id'leri çakışıyor (ikisinde de P001…)
ama aynı kişiler değil; koşul etiketleri de aynı ama sigmalar farklı. İki
setin tabloları hiçbir yerde birleştirilmez.
