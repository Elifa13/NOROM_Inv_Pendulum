# Pilot sonuç özeti

**Veri:** 12 katılımcı (P001–P012), tek oturum, 53 trial (3 practice + 50
measurement). Toplama 26–27 Ağustos 2026.
**Analiz:** `Data Analysis/Notebooks/90_sunum.ipynb`, `src/presentation.py`
**Çıktılar:** `data/processed/sunum/` — HTML rapor, 15 figür, CSV tablolar

Bu belge `Documentation/CartPole_VisualNoise_Pilot_Sunumu (1).pptx` ve
`Kalibrasyon_Pilot_Calismasi_Veri_Ozeti (1).docx` dosyalarının yerine
geçmez ama onlardan **daha güncel**: ikisi de 26 Ağustos tarihli, yani
12 katılımcılık analizden önce hazırlanmış, içlerindeki sayılar artık
geçerli değil.

---

## Sonuç

**Stochastic resonance hipotezi pilotta desteklenmiyor.** Orta düzey noise'ta
iyileşme yok; performans noise arttıkça monoton olarak bozuluyor.

Beklenen şekil (Treviño 2016'daki ters-U) ile gözlenen şekil arasındaki fark,
istatistikte doğrudan görünüyor: lineer trend her metrikte güçlü ve anlamlı,
kuadratik trend hiçbirinde anlamlı değil.

## Koşul × metrik

Analiz birimi katılımcı × koşul (10 trial'ın ortalaması), n = 12.

| Metrik | Yön | no_noise | N1 (σ0.02) | N2 (σ0.05) | N3 (σ0.08) | N4 (σ0.25) |
|---|---|---|---|---|---|---|
| Mean absolute angle (°) | düşük iyi | 11.25 | 11.20 | 12.28 | 12.51 | 12.66 |
| Stabilizasyon (s / 20 s) | yüksek iyi | 18.37 | 18.49 | 18.05 | 18.08 | 18.09 |
| Düşüş / trial | düşük iyi | 1.83 | 1.71 | 1.98 | 1.92 | 2.21 |
| Cart RMS (m) | belirsiz | 1.09 | 1.13 | 1.02 | 1.14 | 1.04 |

Örüntü bütün metriklerde aynı: **no_noise ile N1 birbirine yapışık, N2'den
itibaren bozulma.**

## İstatistik

Friedman (5 koşul, n = 12), ardından baseline'a karşı Wilcoxon, Holm
düzeltmeli. Trend kontrastları ordinal pozisyon üzerinden.

| Metrik | Friedman p | Lineer p | Kuadratik p |
|---|---|---|---|
| Mean absolute angle | **0.0014** | **0.00049** | 0.62 |
| Stabilizasyon süresi | **0.021** | **0.0049** | 0.57 |
| Düşüş sayısı | **0.0076** | **0.00098** | 0.31 |
| Cart RMS | 0.13 | 0.68 | 1.00 |

**Kuadratik terim hiçbir metrikte anlamlı değil.** Ters-U olsaydı burada
görünürdü.

Baseline'a karşı ikili karşılaştırmalar (maPA, Holm sonrası): N1 p = 0.91
(fark yok), N2 p = 0.015, N3 p = 0.014, N4 p = 0.019 — üçü de anlamlı
şekilde **kötü**.

## Eşik seçimi sonucu değiştirmiyor

"Başarılı stabilizasyon" eşiği 5°–45° arasında tarandı. Yön bütün eşiklerde
aynı; etki büyüklüğü dar eşiklerde daha güçlü.

| Eşik | no_noise | N4 | dz | Aynı yönde kişi | Lineer p |
|---|---|---|---|---|---|
| 5° | 7.16 | 6.10 | −1.34 | 10/12 | 0.00049 |
| 10° | 12.40 | 11.02 | −1.30 | 11/12 | 0.00049 |
| 15° | 15.03 | 13.95 | −1.08 | 11/12 | 0.00049 |
| 20° | 16.64 | 15.91 | −0.81 | 11/12 | 0.0024 |
| 25° | 17.73 | 17.19 | −0.65 | 10/12 | 0.00098 |
| 30° | 18.37 | 18.09 | −0.45 | 10/12 | 0.0049 |
| 45° | 19.49 | 19.38 | −0.51 | 8/12 | 0.0068 |

Geniş eşiklerde tavan etkisi devreye giriyor (45°'de zamanın %97'si eşik
içinde), o yüzden etki sönüyor. Ana figürler 30° ile çizildi.

## Kişisel optimal seviye

Her katılımcı için composite sıralamada en iyi koşul (composite: maPA,
stabilizasyon süresi, düşüş sayısı):

| Optimal | Katılımcı |
|---|---|
| no_noise | P002, P003, P005, P007, P010, P011 (6) |
| N1 | P001, P008, P009, P012 (4) |
| N2 | P006 (1) |
| Belirsiz (beraberlik) | P004 (1) |

**Hiçbir katılımcının optimali N3 veya N4 değil.** 12 kişinin 10'unda
optimal ya no_noise ya N1 — yani "noise yok" ile "en düşük noise" arasında.

## Ham veri doğrulaması

Dört metrik ham CSV'lerden bağımsız olarak yeniden hesaplandı ve parquet
zincirinin sonucuyla karşılaştırıldı (`presentation.raw_verification`).
Zincirde bir kayma yok.

## Sınırlar

1. **Randomizasyon sabit seed'e bağlı.** Bütün katılımcılar aynı koşul
   sırasını ve aynı noise desenini görüyor. Başlangıç açıları da tek bir
   sabit diziden geliyor. Etkisi ölçüldü ve küçük (koşullar arası başlangıç
   |θ| yayılımı 0.32°, sonuçla korelasyon +0.066) ve **yönü bulgunun
   aleyhine** — en zor başlangıçlar no_noise'da. Ayrıntı: `CLAUDE.md` →
   "Veride görülen sorunlar" §1.
2. **Pilot anlık performansı ölçüyor, öğrenmeyi değil.** Ludolph'un bulgusu
   bu ikisinin ayrışabileceği yönünde: bir koşul anlık performansta kötü
   olup öğrenmede iyi olabilir. Ana deneye tek seviye yerine sıralı iki
   aday yazmak makul bir hedge.
3. **SR'nin bu göreve transferi zaten açık bir soru.** Treviño'nun kritik ön
   koşulu sinyalin kasıtlı olarak eşiğin altına indirilmesiydi (düşük
   coherence + düşük luminance). Cart-pole'daki pole yüksek kontrastlı ve
   büyük — eşiğin çok üzerinde. Yani negatif sonuç, SR'nin yanlış olduğunu
   değil, bu görevde uygulanabilir olmadığını gösteriyor olabilir.

## Ana deney için ne diyor

Eğer amaç "noise performansı bozmasın" ise: **N1 (σ = 0.02)**. Baseline'dan
ayırt edilemiyor (p = 0.91) ve 4 katılımcının optimali.

Eğer amaç bir etki göstermekse: N4 (σ = 0.25) en güçlü ve en tutarlı bozulma
etkisini veriyor — ama bu SR hipotezinin testi değil, sadece "çok noise
işi zorlaştırır" bulgusu.

Formal seçim prosedürü NB06'nın işi; bu belge sunum için üretilen aceleci
analizi kaydediyor.
