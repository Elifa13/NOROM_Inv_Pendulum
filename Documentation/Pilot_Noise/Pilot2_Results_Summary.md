# Pilot 2 sonuç özeti

**Veri:** 9 katılımcı (P001–P009), tek oturum, 53 trial (3 practice + 50
measurement). Toplama 2–3 Eylül 2026. Drive klasörü
`1oge-PfEM-ZOmmlpWoqIZF7P1yT3f-J3V`.
**Analiz:** `Notebooks/pilot2/` altındaki zincir (01 → 02 → 03 → 04 → 06) ve
izole taramalar (91, 92, 93). Kod pilot 1 ile **aynı** `src/` modülleri.
**Çıktılar:** `Data Analysis/data/pilot2/` — `interim/*.parquet`,
`processed/karar/decision_stats.csv`, `decision_table.csv`

> Pilot 1'in katılımcıları da P001… diye numaralanıyor ama **aynı kişiler
> değil**. Koşul etiketleri de (N1–N4) aynı ama **aynı sigma değil**. İki set
> hiçbir aşamada birleştirilmez; karşılaştırma yalnız sigma üzerinden yapılır.

---

## Sonuç

**Bu noise aralığında koşul etkisi yok.** Beş koşulun hiçbiri
no_noise'tan ayırt edilemiyor; ne lineer ne kuadratik trend anlamlı.

Bu, pilot 1'i tamamlıyor. Pilot 1'in merdiveni σ = 0.02 … 0.25 arasındaydı ve
"σ ≥ 0.05'ten itibaren performans monoton bozuluyor, σ = 0.02 baseline'dan
ayırt edilemiyor" sonucunu vermişti. Pilot 2'nin merdiveni tamamen o eşiğin
**altında** (σ ≤ 0.02) ve orada da hiçbir şey olmuyor — ne iyileşme ne bozulma.
İki pilot birlikte: **görsel noise σ ≈ 0.02'ye kadar performansı etkilemiyor,
üstünde bozuyor. Ters-U (stochastic resonance) hiçbir yerde görünmüyor.**

## Noise merdiveni

| Koşul | Pilot 2 σ | Pilot 1 σ |
|---|---|---|
| no_noise | 0.000 | 0.00 |
| N1 | 0.005 | 0.02 |
| N2 | 0.010 | 0.05 |
| N3 | 0.015 | 0.08 |
| N4 | 0.020 | 0.25 |

Pilot 2'nin en yüksek koşulu (N4, σ=0.020), pilot 1'in en düşük noise
koşuluna (N1, σ=0.02) eşit. İki sette de o seviye baseline'dan ayırt
edilemiyor — farklı 21 kişide birbirini doğrulayan tek örtüşme noktası.

## Koşul × metrik

Analiz birimi katılımcı × koşul (10 trial'ın ortalaması), n = 9.

| Metrik | Yön | no_noise | N1 (σ0.005) | N2 (σ0.010) | N3 (σ0.015) | N4 (σ0.020) |
|---|---|---|---|---|---|---|
| Mean absolute angle (°) | düşük iyi | 10.66 | **10.49** | 10.67 | 10.76 | 10.84 |
| Stabilizasyon (s / 20 s) | yüksek iyi | 18.54 | 18.55 | **18.60** | 18.54 | 18.46 |
| Açı kaynaklı düşüş / trial | düşük iyi | 1.46 | 1.37 | 1.48 | **1.30** | 1.43 |
| Control effort (RMS u) | belirsiz | 0.225 | 0.224 | 0.225 | 0.221 | 0.223 |
| Cart RMS (m) | belirsiz | 1.20 | 1.08 | 1.16 | 1.18 | 1.15 |

Üç karar metriğinde "en iyi" üç farklı koşula düşüyor (N1 / N2 / N3) ve
farklar yüzdenin altında. Sıralamanın kendisi gürültü.

## Testler

Bütün testler within-subject ve non-parametrik, n = 9.

| Metrik | Friedman p | Kendall W | Lineer p | Kuadratik p |
|---|---|---|---|---|
| `mae_angle_deg` | 0.73 | 0.06 | 0.50 (6/9) | 0.57 |
| `stab_time_s` | 0.41 | 0.11 | 0.73 (4/9) | 0.20 |
| `falls_angle_per_trial` | 0.16 | 0.18 | 0.98 (4/9) | 1.00 |
| `control_effort` | 0.96 | 0.02 | 0.73 | 0.91 |
| `cart_rms_m` | 0.38 | 0.12 | 1.00 | 0.43 |

Baseline'a karşı eşleşmiş karşılaştırmalarda hiçbir koşul Holm öncesinde
bile p < 0.16'nın altına inmiyor; en büyük etki `falls_angle_per_trial`'da
N3 (dz −0.57, 2/9 kötü) ve o da yönü "gürültü **iyileştiriyor**" tarafında,
yani tesadüfi.

**Duyarlılık.** `valid_trial = 0` işaretli trial yok (pilot 1'de P011'in iki
`paused` trial'ı vardı), o yüzden duyarlılık analizi 450 trial'ın hepsiyle
aynı sonucu veriyor. Stabilizasyon eşiği 10°–45° taramasında her eşikte hem
lineer hem kuadratik null.

## Kontrol mekanizması (NB04)

| Bulgu | Pilot 2 | Pilot 1 |
|---|---|---|
| Havuz eğrisi zero crossing (bant 10) | **−43.5 ms** (%95 CI −46.5…−39.7) | −52.6 ms (−55.6…−49.5) |
| Amplitude / standart hata | 128× | 154× |
| Kişiler arası yayılım | 138 ms | 269 ms |
| **Koşullar arası yayılım** | **19.6 ms** | 15 ms |
| Kişi içi, koşullar arası sd | 30.5 ms | 27.6 ms |
| Hücre (katılımcı × koşul) | 45/45 dolu, 44'ünde tek geçiş | 60/60, 59'unda tek geçiş |

Aynı sonuç: **action timing predictive** (negatif), ama koşula duyarlı değil —
koşul yayılımı kişi yayılımının yedide biri. Action timing pilot 2'de de karar
setine girmiyor.

Öğrenme kayması pilot 1'dekiyle aynı şekilde **sağlam çıkmıyor**: ham profilde
eğim −9.0 ms/pencere (dz −0.63, 7/9 kişide negatif) ama kompozisyon sabitlenip
sadece orta hız tabakasına bakılınca düzleşiyor (−1.2 ms, dz −0.065). Yani
kayma, geç denemelerde daha hızlı geçişlerin ölçüme girmesinden geliyor,
zamanlamanın kendisinden değil.

Action variability yine ayrı bilgi taşımıyor (N1 dz 0.40, N4 dz 0.24, hepsi
null yönünde ve genliğe bölününce dağılıyor).

## Varyans ve güvenilirlik (NB92, NB93)

| Ölçüt | kişi | koşul | artık | ICC |
|---|---|---|---|---|
| Ortalama \|θ\| | %96.0 | **%0.2** | %3.8 | 0.95 |
| Stabilizasyon süresi | %95.4 | **%0.2** | %4.4 | 0.95 |
| Açı kaynaklı düşüş | %97.3 | **%0.2** | %2.5 | 0.97 |
| Action timing | %65.1 | %2.4 | %32.5 | 0.58 |

Koşulun payı pilot 1'de %0.7–4.0 idi, pilot 2'de %0.2'ye iniyor — merdiven
daralınca beklenen sonuç.

**Kişiye özel optimum yine ölçülemiyor.** Split-half (10 deneme 5+5, 200
tekrar): kişinin genel seviyesi iki yarıda tutuyor (r = 0.97–0.99), koşul
sıralaması tutmuyor (rho = −0.08 / −0.17 / −0.16; aynı "en iyi" oranı
%16 / %15 / %22, şansa %20). Kişi başına "en iyi koşul" dağılımı
(3 no_noise, 2 N1, 2 N2, 2 N3) rastgelelikle tutarlı.

**Öğrenme var, koşuldan bağımsız.** Oturum boyunca ortalama −0.040
derece/deneme, 50 denemede −1.98°, 7/9 kişide iyileşme yönünde (Wilcoxon
p = 0.055). Blok bazında ilk 10 → son 10: 11.52° → 10.27°. Öğrenme eğimi
koşullar arasında farklı değil (Friedman p = 0.73, lineer p = 0.13) ve eğimin
kendisi güvenilir ölçülmüyor (split-half r = 0.31).

Trial düzeyi varyans ayrışımı: kişi %56, koşul %2.3, öğrenme %7.2, artık %34.
**Öğrenme koşul etkisinden üç kat büyük.** Pilot 1'de ikisi birbirine yakındı
(%6.2 koşul, %7.8 öğrenme); merdiven daralınca koşulun payı eridi, öğrenmeninki
aynı kaldı.

## Kontrol değişkenliği (NB91)

Dokuz ölçüt (medyan frekans, sample entropy, duty cycle, genlik, aksiyonlar
arası süre, onset rate) — Holm sonrası hiçbiri anlamlı değil, ham halde bile
en düşük p = 0.43. Pilot 1'de ham halde iki ölçüt p < 0.05 veriyordu ama
sağlamlık taramasını geçmiyordu; pilot 2'de o kadarı bile yok.

## Veri kalitesi

| Kontrol | Sonuç |
|---|---|
| Oturum | 9/9 tam, yarım oturum yok |
| Trial | 477 (9 × 53), QC FAIL 0 |
| Measurement trial | 450, hepsi analiz maskesine giriyor |
| Sample | 623.700; analiz maskesi 540.000 |
| `valid_trial = 0` | yok |
| Zaman/örnekleme | sorun yok (dt sapması ≤ 0.000067 s) |
| Hız–pozisyon tutarlılığı | bütün trial'larda r ≥ 0.99 |
| Force = input × 4 N | tutuyor |
| Fizik modeli | 8 parçada korelasyon 0.994–0.998 |
| T₀ doğrulaması | serbest düşüş episode'u 1 tane, `duration/T₀ = 1.0000` |
| Düşüş sayımı | üç kaynak (sample, sebep, Unity) 450/450 trial'da aynı |

**Randomizasyon sorunu düzelmiş.** Pilot 1'in en büyük veri sorunu
(`randomizationSeed` 12345'e sabitlenmiş, herkes aynı koşul sırasını, aynı
noise desenini ve aynı başlangıç açısı dizisini alıyor) pilot 2'de yok:

- metadata'da yeni `effective_randomization_seed` alanı var ve 9 katılımcıda
  9 farklı değer taşıyor (`config.randomizationSeed` hâlâ 12345 yazıyor, o
  yüzden `qc.check_randomization` artık önce etkili seed'e bakıyor)
- koşul sırası 9 katılımcıda 9 farklı dizi
- `noise_seed` dizileri 9 katılımcıda 9 farklı dizi
- başlangıç açıları hiçbir trial'da bütün katılımcılarda aynı değil

Koşul × trial_order dengesi de iyi: her koşulun ortalama sırası 25.3–25.7
(1–50 aralığında).

**Klasör yerleşimi.** Pilot 2 verisi Drive'da pilot 1'in `Pendulum_Data`
klasörünün içinde, `DataV2/` alt klasörü olarak duruyor. `drive_sync` eskiden
yolun son üç parçasını aldığı için pilot 1 çekildiğinde pilot 2'nin dosyaları
da pilot 1'in klasörüne iniyordu; katılımcı id'leri çakıştığından fark
edilmesi de zordu. 4 Eylül'de bir kez oldu, temizlendi ve `drive_sync` tam üç
parça şartına bağlandı. Pilot 1'in bütün sayıları temizlik sonrası birebir
aynı çıktı (oturum seçimi zaten kendi oturumlarını seçmişti).

**Düzelmeyenler.** `config.participantId` hâlâ bütün metadata'larda "P001"
(P002–P009'da yanlış; `participant_id` alanı doğru). Metadata'da istenen 24
ek alanın (ekran boyutu, izleme mesafesi, deadzone, noise texture
parametreleri…) hiçbiri hâlâ yok — bkz. `Veri_Kayit_Istekleri.md`.

## Ana deney için ne diyor

1. **σ ≤ 0.02 aralığında hangi seviyenin seçildiği performans açısından fark
   etmiyor.** Pilot 1'in "N1 (σ0.02) baseline'dan ayırt edilemiyor" bulgusu,
   altındaki dört seviyede de geçerli.
2. **Ölçülebilir etki isteniyorsa σ ≥ 0.05 gerekiyor** (pilot 1: N2'den
   itibaren monoton bozulma). Ama o bozulma, SR'nin aradığı iyileşme değil.
3. **Stochastic resonance iki pilotta da yok.** σ = 0 … 0.25 arası dokuz
   farklı seviye, 21 katılımcı, hiçbirinde ters-U yok. Treviño'nun ön koşulu
   (sinyal threshold altında) bu görevde sağlanmıyor: pole yüksek kontrastlı
   ve büyük.
4. **Güç uyarısı.** n = 9 ve gözlenen etkiler dz ≤ 0.2 — "fark yok" değil,
   "bu örneklemle saptanamaz". Eşleşmiş t-testi için dz = 0.2'yi n = 9 ile
   yakalama gücü %8, dz = 0.5'i %26, dz = 0.8'i %56. Yani pilot 1 büyüklüğünde
   bir etki (dz ≈ 1.0) burada görünürdü, küçük bir etki görünmezdi.
5. Öğrenme, koşul etkisinden büyük ve koşuldan bağımsız. Ana deney öğrenmeyi
   ölçecekse noise seviyesinin kendisi öğrenme eğrisini bozmuyor gibi
   görünüyor — bu, düşük noise'lu bir koşulun ana deneyde kullanılabilir
   olduğu yönünde bir kanıt.

## Kaynaklar

- Zincir: `Data Analysis/Notebooks/pilot2/`
- Yöntem gerekçeleri (iki pilot için de aynı): `Documentation/Yontem/`
- Pilot 1 karşılığı: `Documentation/Pilot_Sonuc_Ozeti.md`
