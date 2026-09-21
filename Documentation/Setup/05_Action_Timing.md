# 05 — Action timing (Ludolph transferi)

**Notebook:** `04_control.ipynb`
**Kod:** `src/timing.py`; eşikler `config.yaml` → `timing`
**Çıktı:** `state_events.parquet`, `timing_cells.parquet`
**Kaynak:** Ludolph et al. 2017, *Sci Rep* 7:13191, s. 11
**Durum:** uygulandı (2026-08-31). Sonuçlar §5'te.

---

## 0. Terimler

Bu kayıtta geçen İngilizce terimlerin karşılığı. Türkçeye çevrilmiyorlar
(CLAUDE.md → çalışma kuralları).

| Terim | Ne demek |
|---|---|
| **state event** | Pole belirli bir tamsayı açıyı **düşerken** geçtiği an. Durum tarafında tanımlı; katılımcı hiçbir şey yapmasa da olur. |
| **input event** | Girdi tarafında tanımlı olay: `onset` (nötr banddan çıkış), `offset` (banda dönüş), `reversal` (kuvvetin yön değiştirmesi). NB02'nin `input_events` tablosu. |
| **segment** | Bir state event'e ortalanmış ±0.5 s'lik input penceresi, 61 örnek. |
| **event-triggered average** | Yöntemin adı: segmentleri olay anına hizalayıp ortalamak. |
| **sign alignment** | Negatif açılı olayların segmentlerini işaret çevirerek havuzlamak; düzeltici yön hep + tarafta olur. |
| **zero crossing** | Ortalama segment eğrisinin sıfırı kestiği lag. **Action timing bu sayıdır.** Negatif = predictive, pozitif = reactive. |
| **reversal** (eğri düzeyinde) | Ortalama eğrinin gerçekten işaret değiştirmesi (`mean_pre < 0 < mean_post`). Yoksa zero crossing tanımsız. |
| **amplitude** | Ortalama eğrinin max − min farkı. |
| **SEM** | Standard error of the mean. `amplitude / SEM` şeklin gürültüden ayrışıp ayrışmadığını verir. |
| **bootstrap CI** | Segmentleri yeniden örnekleyerek elde edilen güven aralığı (400 tekrar). |
| **velocity stratification** | Olayları olay anındaki \|ω\|'ya göre `slow` / `mid` / `fast` diye ayırmak. Sınırlar %20 ve %80 kuantilleri. |
| **angle band** | Tek tamsayı açı yerine merkez ± 2° havuzlamak. Ana bant 10 ± 2. |
| **within-subject centering** | Her katılımcının kendi ortalamasını çıkarmak; koşul farkı ancak böyle görünüyor. |
| **d<sub>z</sub>** | Eşleşmiş fark etki büyüklüğü: ortalama fark ÷ farkların sd'si. |
| **baseline** | `no_noise` koşulu. |
| **confound** | Ölçülen şeyle karışan üçüncü değişken (ör. seans boyunca olay kompozisyonunun değişmesi). |
| **regression to the mean** | Uçta başlayan bir değerin sonraki ölçümde ortalamaya yaklaşması; sahte öğrenme üretebilir. |

## 1. Ne ölçüyor

Buraya kadarki bütün metrikler "ne kadar iyi dengeledi" sorusuydu. Action
timing farklı bir şey soruyor: **kişi ne zaman tepki veriyor?**

Ludolph'un bulgusu, insanlar öğrendikçe eylemlerinin olaydan *sonra* olmaktan
çıkıp olaydan *önce* olmaya kayması — refleksten öngörüye geçiş. Bu, pilotun
performans metriklerinin göremediği bir mekanizma katmanı.

## 2. Ludolph'un prosedürü

Makaleden dört adım, aynen:

1. **Olay tanımı.** −25° ile +25° arasındaki tamsayı açılar (51 olay). Her
   trial'da her olayın geçiş anı bulunur; frame'ler arası anlar **lineer
   interpolasyonla** alt-frame çözünürlükte kestirilir.
2. **Eleme.** Pole yukarı dönüyorsa geçiş atılır (karşı-aksiyon gerekmiyor).
   Ayrıca açısal hızı, 2 dakikalık kayan pencerede gözlenen hızların
   %20–%80 kuantilleri dışında kalan geçişler atılır.
3. **Segment.** Her olay anına ortalanmış **1 saniyelik** (±0.5 s) force
   segmenti çıkarılır.
4. **Ortalama ve zero crossing.** Aynı olaya ait segmentler 2 dakikalık kayan
   pencerede ortalanır; ortalama segmentin **sıfırı kestiği lag** action
   timing'dir. Negatif = predictive, pozitif = reactive.

**Action variability** = zero crossing çevresinde ±60 ms'lik pencerede force'un
ortalama standart sapması.

Ludolph bunu tepki süresi olarak yorumlamadığını açıkça belirtiyor.

## 3. Transfer kararları

Beş noktada karar gerekti. Dördü kapandı, biri fizibilite kontrolüyle çözüldü.

### 3.1 Zaman ekseni — `trial_order` kullanılacak

Ludolph 2 dakikalık kayan pencere kullanıyor. Bizde duvar saati **yok**:
`t_trial_s` her trial başında sıfırlanıyor, reset'leri içeriyor (max 34 s),
ve metadata'da trial başına zaman damgası yok.

Ama gerek de yok. **`trial_order` zaten bir zaman ekseni** — tam kayıtlı,
sıralı, ve denemeler arka arkaya yapıldığı için geçen süreyle orantılı.
Kabaca: 53 × 20 s aktif + ~115 s reset + 53 × 1.5 s ara ≈ **21 dakikalık
oturum**. Ludolph'un 2 dakikalık penceresi ≈ 6 deneme.

Pencerenin asıl işi öğrenmeyi izlemek değil, **ortalama alacak kadar segment
toplamak** — tek bir geçişten sıfır kesişimi çıkmaz. §4'te ölçüldü, segment
bolluğu var, o yüzden pencere boyu serbestçe seçilebilir.

### 3.2 İki eksen birden

Action timing **hem deneme sırasına hem koşula** göre incelenecek:

- **Deneme sırası** — öğrenme ekseni; tepkiden öngörüye geçiş var mı
- **Koşul** — gürültü bu zamanlamayı bozuyor mu

İkisi birbirinin alternatifi değil. (İlk taslakta sadece koşul ekseni
önerilmişti; pilotun sorusu koşul seçimi olsa da action timing bir motor
öğrenme ölçütü ve öğrenme eksenini atmak yanlış olurdu.)

**Beklenti uyarısı:** Ludolph bir saatten uzun, yerçekimi kademeli artan bir
görevde öğrenme ölçtü. Bizde tek oturum, 21 dakika, sabit g = 1.0. Öğrenme
sinyali çıkmazsa bu "öğrenme yok" demek olmayabilir — görev buna göre
tasarlanmamış.

### 3.3 Hız elemesi — atmak yerine stratification

**Neden eleme var?** Yöntem onlarca segmenti üst üste bindirip ortalıyor.
Pole 10°'den yavaşça geçiyorsa gereken düzeltme başka, savrularak geçiyorsa
başka. İkisi aynı ortalamaya girerse eğri bulanıklaşır ve zero crossing
kimsenin davranışı olmaktan çıkar.

**Karar:**

- Kuantil bandı **katılımcı başına, bütün koşullar havuzlanarak** hesaplanır.
  Koşul içinden hesaplanırsa eleme koşula uyarlanır ve artık aynı hız bandı
  karşılaştırılmaz — gürültü hız dağılımını değiştiriyorsa doğrudan confound.
- Atmak yerine **stratify edilir**: yavaş / orta / hızlı bantlar için ayrı action
  timing. Veri kaybetmiyoruz ve "hızlı düşüşlerde tepki, yavaşlarda öngörü"
  gibi bir örüntü varsa görünür. Ludolph'un elemesi 2016 koşullarının hesap
  kısıtıyla ilgili olabilir; bizde öyle bir kısıt yok.

**Uygulama notu (NB04).** Kuantil katılımcı × **açı seviyesi** içinde
hesaplanıyor, koşullar havuzlanarak. Açı seviyesi de sabitlenmeli çünkü
|ω| açıyla birlikte büyüyor (5°'de ort. 42°/s, 20°'de 64°/s); tek bir
kuantil bandı bütün açılara uygulansaydı stratum'lar açıya göre kayardı.
Kararın karşılığını verdi: stratification §5'teki en güçlü bulguyu üretti.

### 3.4 Açı aralığı — taranacak

Ludolph ±25° kullanıyor; bizde aktif zamanın %87.1'i bu aralıkta. Ama tek
değere bağlanmak yerine **±25 / ±15 / ±10 / ±5** taranacak. Stabilizasyon
eşiği taramasında da dar eşikler daha güçlü etki vermişti.

Düşüş yönlü geçiş sayıları (measurement, `analysis_include`):

| Aralık | Geçiş | Katılımcı × koşul başına |
|---|---|---|
| ±25° | 110.091 | ~1.835 |
| ±15° | 79.607 | ~1.327 |
| ±10° | 57.549 | ~959 |
| ±5° | 29.198 | ~487 |

Fizibilite hiçbir aralıkta sorun değil.

**Uygulamada kesinleşen hali (NB04).** "Aralık" değil **bant** kullanıldı:
merkez ± 2°, merkezler 5 / 10 / 15 / 20. Sebep §4'te: tek bir tamsayı açıda
ortalama eğri bazen sıfırı birden fazla kesiyordu (P002'de 3 geçiş), dar
bant havuzlaması bunu tek geçişe indiriyor. Kümülatif aralık (±25 içindeki
her şey) ise §6 yüzünden anlamsız olurdu — farklı açılar farklı referans
noktaları, karıştırılamaz.

Ana analiz **10 ± 2** (fizibilite orada doğrulandı), diğer üç bant sağlamlık
taraması. Eşikler `config.yaml` → `timing.band_centers_deg`,
`timing.band_half_width_deg`, `timing.main_band_center_deg`.

### 3.5 Episode sınırını aşan segmentler — atılır

1 saniyelik pencere, olay episode sonuna yakınsa reset bloğuna taşar. Reset
satırlarında `applied_force_n` sıfıra zorlanıyor (`Veri_Kayit_Istekleri.md`
madde 2), yani oradaki değerler sahte ve ortalamaya sahte bir reversal
sokar.

**Karar:** sınırı aşan segmentler kırpılmaz, **tamamen atılır**. Ölçülen
kayıp açı başına ~300–390 segment (adayların %12–25'i), kabul edilebilir.

### 3.6 İşaret hizalama

+10° ve −10° aynı olayın aynası: birinde düzeltici kuvvet pozitif, diğerinde
negatif (işaret konvansiyonu için bkz.
[03 §2](03_Durum_Aksiyon_Episode.md#2-işaret-konvansiyonu--veriden-doğrulandı-varsayılmadı)).
Ludolph her açıyı ayrı olay sayıyor. Biz ikisini de tutuyoruz ama negatif
açıların segmentlerini **işaret çevirerek** havuzluyoruz — segment sayısı
ikiye katlanıyor, yorum değişmiyor.

## 4. Fizibilite kontrolü — yöntem bizde çalışıyor

**Sorun neydi:** Ludolph'un yöntemi sessiz bir varsayıma dayanıyor — ortalama
segment düzgün bir S çizer ve sıfırı **bir kez** keser. Bizde aktif
örneklerin %73.9'u tam sıfır (yaylı analog kol merkeze dönüyor). Ortalama
eğri sıfır civarında sürünürse zero crossing kararsız hale gelir ve ölçü
anlamını kaybeder.

**Test:** yukarıdaki prosedür uygulanıp ortaya çıkan ortalama eğriye bakıldı.

### Sonuç: varsayım tutuyor

|θ| = 10° için, işaret hizalanmış 4.553 segmentin ortalaması:

```
  -500 ms   -0.104   ███████████████
  -417 ms   -0.115   █████████████████
  -333 ms   -0.106   ███████████████
  -250 ms   -0.079   ███████████
  -167 ms   -0.041   █████
   -83 ms   -0.012   █
    -0 ms   +0.035          █████
   +83 ms   +0.123          ██████████████████
  +167 ms   +0.169          ████████████████████████
  +250 ms   +0.176          █████████████████████████
  +333 ms   +0.165          ███████████████████████
  +500 ms   +0.130          ██████████████████
```

Temiz bir sigmoid: negatiften başlıyor, tek seferde sıfırı kesiyor, doyuma
gidiyor ve hafifçe geriliyor. Ölçülenler:

- **Zero crossing tek**, −53 ms'de
- Amplitude 0.297; ortalamanın standart hatası 0.0014–0.0043 → **sinyal/gürültü ~70×**
- Sıfır civarı eğim +0.92 birim/s — geçiş keskin, sürünme yok

Segmentlerin %63'ü tam sıfır örneklerden oluşuyor ama **ortalama yine de
pürüzsüz**: farklı segmentlerde reversal anı biraz farklı yerde olduğu
için ortalama alınca sürekli bir rampa çıkıyor. Endişe boşa çıktı.

### Asıl granülaritede de çalışıyor

Katılımcı × koşul hücresinde (|θ| 8–12° bandı havuzlanarak):

| | |
|---|---|
| Hücre | 60 / 60 dolu |
| Hücre başına segment | min 192, medyan 384, max 509 |
| **Tek zero crossing'li hücre** | **59 / 60** |
| Geçiş bulunamayan | 0 |
| Birden fazla geçişli | 1 |

Çoklu geçiş için kural: **en dik yükselişin olduğu geçiş** seçilir. Tek
açı yerine dar bir bant havuzlamak bu sorunu zaten büyük ölçüde çözüyor —
P002 tek açıda 3 geçiş veriyordu, bantla tek geçişe (−88 ms) düştü.

## 5. NB04 sonuçları (2026-08-31)

Ana bant |θ| = 10° ± 2, işaret hizalanmış, 22.524 segment. Bütün sayılar
`04_control.ipynb` çıktısı.

### 5.1 Ölçüt çalışıyor

| | |
|---|---|
| Olay (4 bant toplam) | 91.165 |
| Segment (episode sınırını aşanlar atıldıktan sonra) | 76.888 |
| Atılan | %12,9 (bant 10) — %23,8 (bant 20) |
| Havuz eğrisi zero crossing | **−52,6 ms**, bootstrap %95 CI −55,6…−49,5 |
| Geçiş sayısı | 1 (tek, yükselen) |
| Amplitude / ortalamanın standart hatası | 154× |
| Katılımcı × koşul hücresi | 60/60 dolu, 59'unda tek geçiş, 60'ında gerçek reversal |
| Hücre başına segment | min 192, medyan 384, max 509 |

### 5.2 Kişi farkı koşul farkını eziyor

| | ms |
|---|---|
| Kişi ortalaması aralığı | −143,3 … +126,0 |
| Kişiler arası yayılım | **269,3** |
| Koşullar arası yayılım (merkezlenmiş) | **15,4** |
| Kişi içi, koşullar arası sd | 27,6 |

Koşul yayılımı kişi içi gürültünün bile altında. Baseline'a göre eşleşmiş
farklar: N1 +6,5 ms (dz 0,17), N2 +15,4 (0,38), N3 +6,5 (0,16),
N4 +11,8 (0,26) — hepsi "gürültü öngörüyü azaltıyor" yönünde ama medyanla
bakınca profil düzleşiyor (no_noise +1,1; N1 −9,4; N2 +6,4; N3 −0,3;
N4 +1,4) ve açı bantları arasında işaret değiştiriyor (§5.5).

**Sonuç: gürültünün action timing'i bozduğuna dair kanıt yok.**

12 kişinin 11'i negatif (öngörülü). P007 tek istisna (+126 ms), ve NB02'de
aksiyon dağılımında da ayrışıyordu (D oranı %15,2, diğerlerinde ~%2).

### 5.3 Öğrenme kayması sağlam değil

Pencere ortalamaları (10'ar deneme, koşullar havuzlanmış):

| | 1–10 | 11–20 | 21–30 | 31–40 | 41–50 |
|---|---|---|---|---|---|
| Ortalama | −39,0 | −59,3 | −76,0 | −92,6 | −84,2 |
| Medyan | −61,5 | −83,4 | −85,5 | −64,9 | −83,7 |

Ortalamada Ludolph'un beklediği kayma görünüyor. İki kontrol:

**Kompozisyon.** Katılımcılar ilerledikçe daha iyi dengeliyor, hızlı
geçişlerin payı %18,1 → %11,1'e düşüyor. Hız stratum'ları çok farklı
zamanlama verdiği için (§5.4) bu tek başına sahte bir kayma üretebilirdi.
Orta stratum tek başına alındığında kayma duruyor (−73,2 → −110,5), yani
etki tamamen kompozisyon değil.

**Kaç kişide var.** Asıl sınav bu ve geçilemiyor. Ortalamayı sürükleyen
iki kişi P007 ve P012; ikisi de seansa pozitif (reaktif) başlayıp negatife
kayıyor. Onlar çıkarılınca pencere ortalamaları düzleşiyor:
−124,2 / −117,1 / −128,3 / −124,2 / −123,8. Medyan zaten baştan düz.
Kişi başına doğrusal eğim: ortalama −9,6 ms/pencere ama medyan −5,5,
sd 24,1, 12 kişinin 7'sinde negatif; P007 ve P012 hariç ortalama −0,6.

Alternatif açıklama: bu iki kişi ilk penceresinde atipik bir yerde başladı
ve gruba yaklaştı — regression to the mean. Hücre içi gürültü de büyük
(kişi × pencere sd ~100 ms).

§3.2'deki beklenti uyarısı tuttu: Ludolph bir saatten uzun, yerçekimi
kademeli artan bir görevde öğrenme ölçmüştü; bizde tek oturum, 21 dakika,
sabit g = 1,0.

### 5.4 Yavaş geçişlerde ölçüt tanımsız — yöntemsel bulgu

Velocity stratification beklenmedik bir şey gösterdi:

| Stratum | n | Zero crossing | Amplitude | mean_pre | mean_post | Gerçek reversal |
|---|---|---|---|---|---|---|
| slow | 4.828 | **yok** | 0,057 | +0,002 | +0,046 | hayır |
| mid | 14.544 | −52,8 ms | 0,256 | −0,098 | +0,124 | evet |
| fast | 3.152 | −25,0 ms | 0,887 | −0,297 | +0,299 | evet |

**slow stratum'da ortalama eğri baştan sona pozitif kalıyor.** Katılımcı
pole yavaşça açıyı geçerken zaten düzeltici yönde itiyor; ayrıca bir
reversal olmuyor. Yani orada action timing **tanımsız** — ölçüt ancak
gerçek bir reversal varsa var.

Hücre düzeyinde bakıldığında bu daha da net: slow stratum'da 12 hücrenin
sadece 2'sinde gerçek reversal var. Buna rağmen "zero crossing'i bul" kodu
her seferinde bir sayı döndürüyor — düz bir eğrideki en ufak dalgalanma bile
sıfırı kesiyor gibi görünüyor. Çıkan ortalama −440 ms; tamamen anlamsız.

**Bunun üzerine `curve_stats` iki bayrak üretiyor:**

- `reversal_ok` — ortalama eğri negatiften pozitife geçiyor mu
- `guvenilir` — bunun yanında amplitude, ortalamanın standart hatasının en az
  `timing.min_amp_sem_ratio` (= 10) katı mı

Ludolph'ta bu ayrım yok çünkü o zaten %20–80 dışını atıyordu; eleme yerine
stratification kararı (§3.3) bu bulguyu görünür kıldı.

fast stratum tersi yönde ilginç: amplitude, mid stratum'un 3,5 katı; zero
crossing sıfıra daha yakın (−25 ms). Büyük, geç ama sert düzeltme.

### 5.5 Açı bandı taraması

Havuz zero crossing: 5° → −12,9 ms, 10° → −52,6, 15° → −97,8, 20° → −145,6.
Bu gradyan §6'da açıklandığı gibi büyük ölçüde geometri, yorumlanmaz.

Koşul örüntüsü (hücre ortalamaları, ms):

| Bant | no_noise | N1 | N2 | N3 | N4 |
|---|---|---|---|---|---|
| 5 | −9,5 | −11,0 | +5,3 | +2,4 | +2,6 |
| 10 | −70,5 | −64,0 | −55,1 | −64,0 | −58,7 |
| 15 | −128,7 | −104,5 | −118,3 | −133,4 | −128,4 |
| 20 | −164,4 | −169,8 | −187,3 | −190,0 | −181,1 |

Bant 5 ve 10'da no_noise en negatif, bant 20'de en pozitif. **Örüntü
tekrarlamıyor** — gerçek bir koşul etkisi olsaydı yön korunurdu.

Öğrenme örüntüsü dört bantta da aynı yönde, ama §5.3'teki "kaç kişide var"
kontrolü her bant için aynı şekilde geçerli.

### 5.6 Action variability ayrı bilgi taşımıyor

| Koşul | variability | amplitude | var/amplitude |
|---|---|---|---|
| no_noise | 0,117 | 0,353 | 0,343 |
| N1 | 0,110 | 0,357 | 0,355 |
| N2 | 0,100 | 0,329 | 0,324 |
| N3 | 0,098 | 0,325 | 0,328 |
| N4 | 0,098 | 0,327 | 0,319 |

Ham variability gürültüyle düzenli düşüyor (N4'te dz −0,77, 12 kişinin
8'inde). Ama amplitude'a bölününce etki büyük ölçüde kayboluyor (dz −0,27).
Yani gürültüde insanlar daha *tutarlı* davranmıyor, sadece daha küçük
kuvvet uyguluyor. Katılımcı içi korelasyonlar bunu doğruluyor:
variability–amplitude r = +0,64, variability–control_effort r = +0,40.

Zero crossingnin kendisi NB03 metrikleriyle ilişkisiz (control_effort ile
r = +0,06, maPA ile −0,04) — action timing performans ölçülerinin kopyası
değil, ayrı bir konstrukt ölçüyor.

## 6. Açılar arası karşılaştırma yapılmamalı

Zero crossing açı büyüdükçe negatifleşiyor: −13 ms (5°), −53 (10°), −98 (15°),
−145 (20°). **Bu "büyük açılarda daha öngörülü" demek değil.**

Pole düşerken önce 5°'yi, sonra 20°'yi geçiyor. Tek bir reversal
olayı, gitgide daha geç referans noktalarına göre ölçüldüğünde doğal olarak
daha negatif çıkar.

Ölçtük: aynı düşüşte 5°'den 20°'ye geçiş medyan **256 ms** sürüyor (n = 2.465,
IQR 158–438). Zero crossing farkı ise 132 ms. Yani gradyanın kabaca **yarısı
geometri**, yarısı gerçek — eylem tamamen sabit bir anda değil, kısmen açıyı
takip ederek gerçekleşiyor.

Kaba bir ayrıştırma (medyan geçiş süresi ile ortalama eğri farkını
karşılaştırıyor, segment kümeleri de birebir aynı değil), ama pratik sonuç
net: **açı sabitlenip koşul veya deneme sırası boyunca karşılaştırılır.**
Açılar arası fark yorumlanmaz.

## 7. NB04 ne yaptı

| Adım | Nerede | Not |
|---|---|---|
| `state_events` üretimi, alt-frame interpolasyon | `timing.build_segments` | 91.165 olay |
| Segment çıkarma, işaret hizalama, episode sınırı elemesi | aynı fonksiyon | 76.888 segment |
| Velocity stratification | `timing.add_velocity_strata` | katılımcı × açı seviyesi kuantili |
| Eğri istatistikleri ve zero crossing | `timing.curve_stats`, `pick_crossing` | çoklu geçişte en dik yükselen |
| Bootstrap CI | `timing.bootstrap_zc` | 400 tekrar |
| Hücre tabloları | `timing.timing_cells` | keyed: koşul / deneme penceresi / stratum |
| Öğrenme ekseni | `timing.add_trial_window`, `window_profile`, `learning_slopes` | 10'luk pencere |
| Bant taraması | `timing.band_sweep` | 5 / 10 / 15 / 20 |
| Action variability | `curve_stats` içinde | ±60 ms, ayrıca amplitude'a bölünmüş |

**Yapılmadı:** I/CR/D/A dağılımının koşula göre değişimi. Öncelik dışı
bırakıldı (2026-08-31 kararı); A sınıfının istatistiksel kullanılabilirliği
hâlâ açık.

## 8. Açık kalanlar

- **A sınıfı seyrek (%0,30).** Park'ta anlamlı bir orandı. Koşula göre
  dağılım NB04'te yapılmadı, karar hâlâ verilmedi.
- **Yavaş stratum'daki davranış tarif edilmedi.** Ölçütün orada tanımsız
  olduğunu biliyoruz; katılımcının o rejimde ne yaptığı (sürekli düzeltici
  itiş) ayrı bir ölçü ister. Pilot kararını etkilemiyor.
- **Öğrenme sorusu kapanmadı, sadece bu veride cevaplanamıyor.** 21 dakikalık
  tek oturum Ludolph'un tasarımına denk değil. Ana deneyde oturum uzarsa
  aynı boru hattı doğrudan çalışır.
