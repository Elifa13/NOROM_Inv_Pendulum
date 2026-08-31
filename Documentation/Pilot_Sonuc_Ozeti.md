# Pilot sonuç özeti

**Veri:** 12 katılımcı (P001–P012), tek oturum, 53 trial (3 practice + 50
measurement). Toplama 26–27 Ağustos 2026.
**Analiz:** `Notebooks/06_noise_decision.ipynb`, `src/decide.py`
(karar metrik seti `03_performance.ipynb`'te seçildi)
**Çıktılar:** `data/processed/karar/` — `decision_stats.csv`,
`decision_table.csv`

Daha önce bu belge acil sunum notebook'unun (`90_sunum.ipynb`) sayılarını
taşıyordu. 31 Ağustos'ta NB06 yazıldı ve sayılar zincirin kendi
çıktılarıyla değiştirildi. Tek farklılık düşüş metriğinde: sunum bütün
düşüşleri sayıyordu, karar seti **sadece açı kaynaklı** olanları sayıyor
(ray kaybı ayrı bir başarısızlık, bkz. `Yontem/03`).

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
| Mean absolute angle (°) | düşük iyi | 11.25 | **11.20** | 12.28 | 12.51 | 12.66 |
| Stabilizasyon (s / 20 s) | yüksek iyi | 18.37 | **18.49** | 18.05 | 18.08 | 18.09 |
| Açı kaynaklı düşüş / trial | düşük iyi | 1.60 | **1.47** | 1.78 | 1.70 | 2.00 |
| Control effort (RMS u) | belirsiz | 0.206 | 0.209 | 0.209 | 0.200 | 0.208 |
| Cart RMS (m) | belirsiz | 1.09 | 1.13 | 1.02 | 1.14 | 1.04 |

Koşul sıralaması (1 = en iyi, üç karar metriğinin ortalaması):
**N1 (1.0) → no_noise (2.0) → N3 (3.67) → N4 (4.33) → N2 (4.0)**.
N1 üç metrikte de sayısal olarak en iyi — ama aşağıdaki testlerde
baseline'dan ayırt edilemiyor.

Örüntü bütün metriklerde aynı: **no_noise ile N1 birbirine yapışık, N2'den
itibaren bozulma.**

## İstatistik

Friedman (5 koşul, n = 12), ardından baseline'a karşı Wilcoxon, Holm
düzeltmeli. Trend kontrastları ordinal pozisyon üzerinden.

| Metrik | Friedman p | Kendall's W | Lineer p | Kuadratik p |
|---|---|---|---|---|
| Mean absolute angle | **0.0014** | 0.37 | **0.00049** | 0.62 |
| Stabilizasyon süresi | **0.021** | 0.24 | **0.0049** | 0.57 |
| Açı kaynaklı düşüş | **0.0051** | 0.31 | **0.00098** | 0.58 |
| Control effort | 0.75 | 0.04 | 1.00 | 0.38 |
| Cart RMS | 0.13 | 0.15 | 0.68 | 1.00 |

Lineer kontrast `mae_angle_deg`'de **12 katılımcının 12'sinde** aynı yönde.

### Hangi seviye baseline'dan farklı

Eşleşmiş Wilcoxon, Holm düzeltmesi metrik içinde (dört karşılaştırma).

| Koşul | maPA fark | d<sub>z</sub> | p (Holm) | Aynı yönde |
|---|---|---|---|---|
| N1 | −0.05 | −0.03 | 0.91 | 6/12 |
| N2 | +1.03 | 1.18 | **0.015** | 11/12 |
| N3 | +1.26 | 1.17 | **0.014** | 11/12 |
| N4 | +1.41 | 0.96 | **0.019** | 11/12 |

Diğer iki metrikte Holm sonrası yalnız N4 ayakta kalıyor
(`falls_angle_per_trial` p = 0.039). Üç metrik birbiriyle güçlü ilişkili
(maPA–RMS r = 0.98), yani bağımsız kanıt değil; metrikler arası ek düzeltme
yapılmadı.

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
| N1 | P001, P004, P008, P009, P012 (5) |
| N2 | P006 (1) |

**Hiçbir katılımcının optimali N3 veya N4 değil.** 12 kişinin 11'inde
optimal ya no_noise ya N1 — yani "noise yok" ile "en düşük noise" arasında.
(Composite NB06'da z-skor üzerinden yeniden hesaplandı; sunum sürümünde
P004 beraberlikte kalmıştı, şimdi N1'e düşüyor.)

## Karar iki kontrole de dayanıyor

**(a) `valid_trial`.** Unity 600 measurement trial'ın 2'sini `paused` diye
işaretlemiş (P011 T030, T034); NB01'in kalite kontrolü o kolona bakmıyor, yani
ikisi de analize giriyor. Çıkarıldığında hiçbir p değeri oynamıyor
(lineer 0.00049 / 0.0049 / 0.00098, kuadratik 0.62 / 0.62 / 0.58) ve koşul
sıralaması aynı kalıyor.

**(b) Stabilizasyon eşiği.** 10°–45° arasında tarandı: **her eşikte lineer
anlamlı (p ≤ 0.0068), hiçbir eşikte kuadratik anlamlı değil** (p = 0.38–0.57).
En iyi koşul eşiğe göre no_noise ile N1 arasında gidip geliyor — ikisinin
ayırt edilemez olduğunun bir başka göstergesi.

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

## Ana deney için aday sıralaması

**1. aday — N1 (σ = 0.02).** Görsel noise var ama performansı ölçülebilir
şekilde bozmuyor (p ≈ 0.91, d<sub>z</sub> ≤ 0.20, 6/12). "Noise altında
öğrenme" sorusu, noise'un anlık performansı zaten yıkmadığı bir seviyede
sorulmalı; aksi halde öğrenme farkı ile performans bozulması birbirine
karışır.

**2. aday — N2 (σ = 0.05).** Etkisi ölçülebilir olan **en düşük** seviye
(d<sub>z</sub> = 1.18, 11/12). Soru "noise öğrenmeyi bozuyor mu" şeklinde
kurulursa tercih edilir, ama anlık performansı da bozduğu için iki etki
ayrışamayabilir.

**N3 ve N4 eleniyor.** N3 ile N4 arasında anlamlı fark yok, yani daha
yüksek noise ek bilgi getirmiyor; N4 zaten en kötü koşul.

### Sıralama bir soruya bağlı

Ana deney **tek noise seviyesi + no_noise kontrol grubu** mu kullanacak,
yoksa **herkes aynı noise'u** mu alacak? Ekibe soruldu, cevap gelmedi.

- **Kontrol grubu varsa:** N1 ile no_noise arasındaki fark bu pilotta
  saptanamayacak kadar küçük; böyle bir tasarımda muhtemelen null sonuç
  çıkar. Bu durumda N2 daha bilgilendirici.
- **Herkes aynı noise'u alıyorsa:** noise'un görevi öğrenmeyi ölçmeyi
  engellememek, yani N1.

Cevaba göre aday sırası **değişiyor**. NB06 her iki durum için gereken
sayıları üretti.
