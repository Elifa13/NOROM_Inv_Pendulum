# Analiz günlüğü

Ne zaman ne yapıldı, ne karara bağlandı. Yeni giriş **üste** eklenir.

Kayıt tutma amacı: aylar sonra "bu sayı neden böyle" diye sorulduğunda
cevabın ve o günkü gerekçenin bulunabilmesi. Yöntem ayrıntıları
[Yontem/](Yontem/) altında, bu dosya sadece kronoloji ve kararlar.

---

## 2026-09-04 — İkinci pilot: ayrı veri seti, aynı zincir

Yeni bir Drive klasörü geldi (`1oge-PfEM-ZOmmlpWoqIZF7P1yT3f-J3V`): 9 katılımcı,
2–3 Eylül oturumları, **başka kişiler**. Katılımcı id'leri gene P001… diye
gidiyor, yani iki setin dosyaları asla aynı klasörde buluşmamalı.

**Ayrım klasör düzeyinde yapıldı.** `config.yaml`'a `datasets:` bloğu eklendi,
her setin kendi `data/<dataset>/{raw,interim,processed}` ağacı var; eskisi
`data/pilot1/` altına taşındı. Aktif set notebook'un ilk hücresindeki `DATASET`
değişkeniyle seçiliyor, yolları `src/dataset.load_config` çözüyor ve
`config["paths"]` içine yazıyor — böylece notebook'ların geri kalanı tek satır
değişmeden çalıştı. `dataset.dirs` interim klasörüne bir `.dataset` damgası
bırakıyor; yanlış set yanlış klasöre yazmaya kalkarsa hata veriyor.

Zincir kopyalandı: `Notebooks/pilot2/` altında 01–06 ve 91–93, tek fark ilk
hücredeki `DATASET = "pilot2"`. `src/` hiç çoğaltılmadı — analiz kodu zaten
sigmayı veriden okuyordu, koşul etiketleri de aynı beş isim.

**Bir tuzak çıktı: pilot2 Drive'da pilot1'in içinde.** Verilen link doğrudan
`DataV2` klasörüne işaret ediyor ama o klasör `Pendulum_Data`'nın alt klasörü.
`drive_sync._list_remote` yolun **son üç** parçasını alıyordu, yani
`DataV2/P001/S.../dosya` ile `P001/S.../dosya` aynı görünüyordu: pilot1
çekildiğinde pilot2'nin 27 dosyası da pilot1'in klasörüne indi. Katılımcı
id'leri çakıştığı için gözle de fark edilmesi zor. Bir kez oldu, sızan 9
oturum silindi, `drive_sync` yolun **tam üç parça** olmasını şart koşacak
şekilde düzeltildi ve atladığı girdileri artık uyarı olarak basıyor. Pilot1
NB01 temizlik sonrası yeniden çalıştırıldı: bütün sayılar birebir aynı
(oturum seçimi zaten kendi oturumlarını seçmişti, sızan oturumlar "yarım"
listesine düşmüştü). Yeni bir veri seti geldiğinde `sync_data`'nın uyarı
satırına bakmak gerekiyor.

**Yol boyunca düzeltilen üç şey** (üçü de iki sette de geçerli):

- `qc.check_randomization` artık önce `effective_randomization_seed`'e bakıyor.
  Pilot 2'de `config.randomizationSeed` hâlâ 12345 ama RNG oturum başına
  yeniden tohumlanıyor; eski kontrol yanlış WARN veriyordu.
- Koşul etiketlerindeki sigma 2 haneye yuvarlanıyordu, pilot 2'nin
  0.005/0.010/0.015'i aynı etikete düşüyordu. Hane sayısı artık koşulları
  ayırmaya yetecek kadar seçiliyor (pilot 1'in etiketleri değişmedi).
- NB91 ve NB93'te trial sayısı 600'e sabitlenmişti, veriden türetiliyor.
  NB93'ün pilot 1 sayılarını basan karşılaştırma satırı da genelleştirildi;
  NB93 pilot 1 için yeniden çalıştırıldı, bütün sayılar birebir aynı çıktı.

**Sonuç: bu merdivende koşul etkisi yok.** Pilot 2'nin noise seviyeleri
0 / 0.005 / 0.010 / 0.015 / 0.020 — hepsi pilot 1'in en düşük noise koşuluna
(N1, σ=0.02) eşit ya da ondan küçük. Üç karar metriğinde de Friedman null
(p = 0.16–0.73, W ≤ 0.18), lineer de kuadratik de null, hiçbir koşul
baseline'dan ayrılmıyor.

İki pilot birlikte okununca tablo tamamlanıyor: **σ ≈ 0.02'ye kadar hiçbir şey
olmuyor, üstünde performans monoton bozuluyor, ters-U hiçbir yerde yok.**
İki setin tek örtüşme noktası σ = 0.02 ve orada ikisi de "baseline'dan ayırt
edilemiyor" diyor — 21 farklı kişide birbirini doğrulayan tek karşılaştırma.

Diğer bulgular pilot 1'i tekrarlıyor: action timing predictive (−43.5 ms) ama
koşula duyarsız; kontrol değişkenliği ölçütlerinin hiçbiri anlamlı değil;
kişiye özel optimum bu deneme sayısıyla ölçülemiyor (koşul sıralaması
split-half rho ≈ 0); öğrenme var (−1.98°/50 deneme) ve koşuldan bağımsız.

**Veri tarafında iyi haber:** pilot 1'in bir numaralı sorunu (seed 12345'e
sabit, herkes aynı koşul sırası + aynı noise deseni + aynı başlangıç açısı
dizisi) pilot 2'de yok. Veriden doğrulandı: 9 katılımcıda 9 farklı koşul
sırası, 9 farklı `noise_seed` dizisi, hiçbir trial'da ortak başlangıç açısı.
Düzelmeyenler: `config.participantId` hâlâ hep "P001", istenen 24 metadata
alanının hiçbiri hâlâ gelmiyor.

Ayrıntı: [Pilot2_Sonuc_Ozeti.md](Pilot2_Sonuc_Ozeti.md).

---

## 2026-09-02 — İzole keşif: kontrol değişkenliği ve varyans ayrışımı

İki izole notebook yazıldı ve çalıştırıldı: `91_control_variability.ipynb` ve
`92_varyans_ayrisimi.ipynb`. İkisi de sadece `data/interim` okuyor, `src/`
modülü yok, zincirin hiçbir parçası import etmiyor. Hiçbir sonucu karar
setine girmiyor.

**NB91 — kontrol değişkenliği.** Soru: gürültü kişinin kontrol davranışını
değiştiriyor mu. Frequency analysis (Welch, medyan frekans) ve sample entropy,
hem açı hem girdi sinyalinde; ayrıca duty cycle, genlik ve aksiyonlar arası
süre. Dokuz ölçüt, koşul başına katılımcı × koşul birimi.

**Koşul etkisi yok.** Ham halde iki ölçüt p < 0.05 veriyor (`medfreq_angle` ve
`sampen_angle`, ikisi de 0.021) ama ikisi de sağlamlık taramasını geçemiyor:
entropy alt örneklemeye dayanmıyor (60/30 Hz'de anlamlı, 15/10 Hz'de değil),
medyan frekans pencere boyuna dayanmıyor (`nperseg=128`'de bütün trial'lar aynı
değeri veriyor, `512`'de etki kayboluyor). Dokuz ölçüt sınandığı için Holm
sonrası zaten hiçbiri ayakta kalmıyor. Kuadratik hiçbir ölçütte anlamlı değil.

**Asıl çıktı yöntemsel.** Frekans analizi bu veriye bu haliyle uygulanamıyor:
çubuğun baskın salınım periyodu ~4 s, episode'ların medyanı 4.3 s. Tipik bir
segmentte salınımın ancak bir dönüşü var, bu da spektrum kestirimini çözünürlük
sınırına itiyor. Episode'ların yarısı zaten 256 örneklik alt sınırın altında.
Aynı soruya spektrum gerektirmeden cevap veren yöntem önerildi: Collins & De
Luca 1993 diffusion analizi.

**NB92 — varyans ayrışımı.** Katılımcı × koşul tablosunda toplam varyans
kişi / koşul / artık diye ayrıldı, ICC ve split-half güvenilirlik hesaplandı.

| Ölçüt | kişi | koşul | artık | ICC |
|---|---|---|---|---|
| Ortalama \|θ\| | %89.4 | %4.0 | %6.6 | 0.91 |
| Stabilizasyon süresi | %90.7 | %2.1 | %7.2 | 0.91 |
| Açı kaynaklı düşüş | %96.8 | %0.7 | %2.5 | 0.97 |
| Action timing | %86.3 | %0.5 | %13.2 | 0.83 |

NB04'teki "koşullar arası yayılım 15 ms, kişiler arası 269 ms" gözlemi bütün
ölçütler için sayıya döküldü. Within-subject tasarımın neden zorunlu olduğu
da buradan görünüyor.

**Kişiye özel optimum ölçülemiyor.** Her kişinin bir koşuldaki 10 denemesi
rastgele 5+5 bölünüp 200 kez tekrarlandı. Kişinin genel seviyesi iki yarıda
tutuyor (r = 0.97–0.99) ama koşul sıralaması tutmuyor (rho = 0.15 / 0.04 /
−0.02; aynı "en iyi" oranı %29 / %19 / %35, şansa %20). Spearman-Brown ile
kullanılabilir güvenilirlik (rho ≥ 0.7) için koşul başına ~80 deneme gerekiyor;
şu an 10 var. Pilotun kişisel en iyileri (6 no_noise, 5 N1, 1 N2) rastgeleliğin
üreteceğiyle tutarlı.

**Öğrenme kontrol edildi.** Oturum boyunca iyileşme var ve gürültü etkisinden
büyük: ortalama −0.047 derece/deneme, 50 denemede −2.29 derece, 11/12 kişide
(Wilcoxon p = 0.016); gürültünün etkisi ise +1.41 derece. Koşullar deneme
sırasına dengeli dağıtıldığı için karışmıyor (koşul ortalamaları 24.6–26.5).
Trend çıkarılınca koşul sıralaması güvenilirliği 0.15 → 0.22 yükseliyor,
gerçek bir iyileşme ama yetmiyor; varyans ayrışımı neredeyse hiç oynamıyor.
Yan sonuç: öğrenme 50 denemede ölçülebiliyor, yani ana deneyin ölçmek istediği
şey bu görevde var. Sınır: kimse platoya ulaşmadı, pilot anlık performansı
değil öğrenmenin ortasındaki performansı ölçtü. P007 üçüncü kez aykırı
(tek kötüleşen kişi, +0.078, p = 0.0005).

### Dokümantasyon düzeltmeleri

NB92 §1 bir sağlama üretti ve üç doküman düzeltildi:

1. **[Yontem/06](Yontem/06_Karar_Istatistigi.md) §2 — test seçimi gerekçesi.**
   "n = 12'de normallik varsayımı sınanamaz; parametrik testler riskli"
   yazıyordu. Sınanabiliyor: `mae_angle_deg` Shapiro p = 0.99, `stab_time_s`
   p = 0.15, ve RM-ANOVA Friedman'la aynı sonucu veriyor. Ama
   `falls_angle_per_trial` p = 0.0009 ile normalliği reddediyor (sayım
   değişkeni). Tercih savunulabilir, gerekçe düzeltildi.
2. **[Yontem/06](Yontem/06_Karar_Istatistigi.md) §5 — çoklu karşılaştırma.**
   Metrikler arası düzeltme yapılmama gerekçesi `mae_angle_deg`–`rms_angle_deg`
   r = 0.98'e dayandırılmıştı; `rms_angle_deg` karar metriği değil, dolayısıyla
   geçersiz bir dayanak. Doğru sayılar konuldu (kişi içi: mae–stab −0.86,
   mae–düşüş 0.42) ve düzeltme fiilen hesaplandı: Holm sonrası lineer
   0.0015 / 0.0049 / 0.0020, üçü de anlamlı kalıyor. Sonuç değişmiyor.
3. **Duyarlılık cümlesi.** "Hiçbir p oynamıyor" fazla güçlüydü: `stab_time_s`
   kuadratiği 0.57 → 0.62 oynuyor. İkisi de anlamlılıktan uzak.

Ayrıca düzeltilenler: stabilizasyon eşiği taraması 10°–45° değil **5°–45°**
(üç dosyada yanlıştı); koşul sıralaması cümlesinde N2 ile N4 yer değiştirmişti;
başlangıç |θ| yayılımı 0.32° değil **0.35°**; CLAUDE.md'deki veri katmanları
zinciri 31 Ağustos'taki `events` → `input_events` yeniden adlandırmasına göre
güncellenmedi kalmıştı ve `state_events` katmanı eksikti; düşüş sayısı
tablosuna kapsam etiketi eklendi (1.241 + 140 practice dahil, 1.025 + 131
sadece measurement).

## 2026-08-31 — NB06: karar verildi, SR desteklenmiyor

> **Düzeltme, 2026-09-02.** Bu girişteki iki ayrıntı sonradan düzeltildi:
> eşik taraması 10°–45° değil 5°–45°, ve "hiçbir p oynamıyor" tam doğru değil
> (`stab_time_s` kuadratiği 0.57 → 0.62). Karar etkilenmiyor. Ayrıntı üstteki
> 2026-09-02 girişinde.

`src/decide.py` + `06_noise_decision.ipynb`. Çıktı
`data/processed/karar/decision_stats.csv` ve `decision_table.csv`.
Yöntem kaydı: [Yontem/06](Yontem/06_Karar_Istatistigi.md), sonuçlar
[Pilot_Sonuc_Ozeti.md](Pilot_Sonuc_Ozeti.md).

**Sonuç: stochastic resonance desteklenmiyor.** Kuadratik kontrast — U
şeklinin doğrudan testi — üç karar metriğinde de null (p = 0.57–0.62).
Lineer kontrast üçünde de anlamli (p = 0.0005 / 0.0049 / 0.001) ve
`mae_angle_deg`'de 12 katılımcının 12'sinde aynı yönde. Noise arttıkça
düzenli bozulma var, ortada tepe yok.

**N1 baseline'dan ayırt edilemiyor** (üç metrikte de p ≈ 0.90,
d<sub>z</sub> ≤ 0.20, 6/12). N2/N3/N4 `mae_angle_deg`'de Holm sonrası
anlamlı (d<sub>z</sub> 0.96–1.18, 11/12).

**Bir nüans kayda değer:** grup ortalamasında üç metrikte de sayısal olarak
en iyi koşul N1. Yüzeyde U şekli gibi duruyor ama fark gürültünün içinde ve
kuadratik kontrast null. `decide.interior_optimum` bu kontrolü kuadratik
testin yanına koymak için yazıldı — tek bir null teste dayanmamak için.
Composite'te kimsenin en iyisi N3/N4 değil (6 no_noise, 5 N1, 1 N2).

**İki duyarlılık kontrolü de temiz.** P011'in iki `paused` trial'ı
çıkarılınca hiçbir p oynamıyor. Stabilizasyon eşiği 10°–45° taramasında her
eşikte lineer anlamlı, hiçbirinde kuadratik anlamlı değil.

**Aday sıralaması ana deneyin tasarımına bağlı** ve bu hâlâ açık soru:
kontrol grubu varsa N2 (N1–baseline farkı saptanamayacak kadar küçük),
herkes aynı noise'u alıyorsa N1 (noise öğrenmeyi ölçmeyi engellememeli).
NB06 her iki durum için gereken sayıları üretti.

**Not:** `Pilot_Sonuc_Ozeti.md` artık sunum notebook'unun değil zincirin
sayılarını taşıyor. Tek farklılık düşüş metriğinde — sunum bütün düşüşleri
sayıyordu, karar seti sadece açı kaynaklı olanları.

---

## 2026-08-31 — NB04 yazıldı: action timing ölçüldü, koşul etkisi yok

`src/timing.py` + `04_control.ipynb` + `config.yaml` → `timing` bloğu.
Çıktılar `state_events.parquet` (91.165 olay) ve `timing_cells.parquet`.
Bütün sayılar ve tablolar [Yontem/05](Yontem/05_Action_Timing.md) §5'te.

**Dört bulgu, önem sırasına göre:**

1. **Gürültünün action timing'i bozduğuna dair kanıt yok.** Koşullar arası
   yayılım 15 ms, kişi içi koşullar arası sd 27,6 ms, kişiler arası yayılım
   269 ms. Medyanla profil düzleşiyor, açı bantları arasında işaret
   değiştiriyor. Pilot kararı (NB06) NB03'ün performans metrikleriyle
   verilmeye devam edecek.
2. **Ölçüt bu veride sağlam.** Havuz eğrisi −52,6 ms (bootstrap %95 CI
   −55,6…−49,5), tek geçiş, amplitude/standart hata 154×. 60 katılımcı × koşul
   hücresinin 60'ı dolu. %73,9 sıfır girdi endişesi tamamen boşa çıktı.
3. **Öğrenme kayması sağlam değil.** Pencere ortalamalarında −39 → −93 ms
   görünüyor ama P007 ve P012 çıkarılınca düzleşiyor, medyan zaten düz.
   İkisi de seansa reaktif başlayıp gruba yaklaşıyor — regression to the
   mean tek başına açıklıyor. Kompozisyon kontrolü (orta velocity stratum tek
   başına) kaymayı kısmen koruyor, kişi kontrolü korumuyor.
4. **Yavaş geçişlerde ölçüt tanımsız — yöntemsel bulgu.** Yavaş stratum'da
   ortalama eğri baştan sona pozitif kalıyor, yani hiç reversal yok;
   "zero crossing" düz eğrinin gürültüsünden okunuyor ve −440 ms gibi
   anlamsız değerler üretiyor. Bunun üzerine `curve_stats`'a `reversal_ok`
   ve `guvenilir` bayrakları eklendi (`timing.min_amp_sem_ratio = 10`).
   Bu bulgu Ludolph'ta görünmez çünkü o zaten %20–80 dışını atıyor;
   **eleme yerine stratification kararı (05 §3.3) karşılığını verdi.**

**Ek:** action variability gürültüyle düşüyor (N4'te dz −0,77) ama amplitude'a
bölününce etki kayboluyor (dz −0,27) — insanlar daha tutarlı davranmıyor,
sadece daha az kuvvet uyguluyor. Zero crossing NB03 metrikleriyle ilişkisiz
(r ~ 0,06), yani ayrı bir konstrukt.

**Yapılmadı:** I/CR/D/A dağılımının koşula göre değişimi öncelik dışı
bırakıldı; A sınıfı kararı açık kaldı.

**Ölçek kararı:** NB03 ile aynı dil — katılımcı içi merkezlenmiş profil, dz,
kaç kişide aynı yön. p değeri yok. Action timing karar metrik setinde
olmadığı için NB06'ya da gitmiyor; mekanizma ölçütü olarak raporlanacak.

---

## 2026-08-31 — `events` → `input_events` isimlendirmesi

Aynı kelimenin iki farklı kavram için kullanılması sorunu kapandı. NB04'te
iki olay tablosu yan yana duracaktı; karışma riski gerçekti.

| Eski | Yeni |
|---|---|
| `build.detect_events` | `build.detect_input_events` |
| `events.parquet` | `input_events.parquet` |
| config `events:` | config `input_events:` (eski anahtar fallback olarak okunuyor) |
| NB02 §6 "Event" | "Girdi olayları" |

Ludolph'un durum tarafındaki olayları NB04'te **`state_events`** adıyla
üretilecek.

**Bu arada NB02'de yanlış bir cümle bulundu ve düzeltildi.** §6 markdown'ında
"`reversal` = kuvvetin yön değiştirdiği an (Ludolph'un action timing'i bunu kullanır)"
yazıyordu. Kullanmıyor: Ludolph'un ölçümü, state event'e ortalanmış kuvvet
segmentlerinin ortalamasının zero crossing — bizim `reversal` sayımımız değil.
Bu cümle NB02 yazıldığında action timing prosedürü henüz okunmamışken
konmuştu.

NB02 yeniden çalıştırıldı, çıktılar aynı (35.519 olay, dosya boyutu birebir),
eski `events.parquet` silindi. Zincir doğrulandı: `detect_input_events`
import oluyor, `performance.load_built` çalışıyor, `fall` sayısı hâlâ
Unity'nin `fall_count`'uyla birebir.

---

## 2026-08-30 (akşam) — Sigmoid fizibilite kontrolü, `05_Action_Timing.md`

Action timing'in tek açık maddesi kapandı: **Ludolph'un yöntemi bizim veride
çalışıyor.**

**Test.** Düşüş yönlü tamsayı açı geçişlerine ortalanmış ±0.5 s'lik input
segmentleri çıkarılıp ortalandı (alt-frame interpolasyonlu, episode sınırını
aşanlar atılarak, negatif açılar işaret çevrilerek havuzlanarak).

**Sonuç.** |θ| = 10°'de 4.553 segmentin ortalaması temiz bir sigmoid: tek
zero crossing (−53 ms), amplitude 0.297, ortalamanın standart hatası 0.0014–0.0043
(sinyal/gürültü ~70×), sıfır civarı eğim +0.92 birim/s. Segmentlerin %63'ü tam
sıfır örneklerden oluşmasına rağmen ortalama pürüzsüz — reversal anı
segmentler arasında biraz kaydığı için ortalama sürekli bir rampa üretiyor.
**%74 sıfır endişesi boşa çıktı.**

Asıl granülaritede de sağlam: katılımcı × koşul 60 hücrenin 60'ı dolu (medyan
384 segment), 59'unda tek zero crossing, 0'ında geçiş yok. Çoklu geçiş için
kural: en dik yükselişin olduğu geçiş seçilir; dar bir açı bandı havuzlamak
sorunu zaten büyük ölçüde çözüyor.

### Ön gözlemler (NB04 sonucu değil, eleme adımı henüz uygulanmadı)

- 12 katılımcının 11'i bütün koşullarda **öngörülü** (ort. ≈ −60 ms).
- **P007 beş koşulda da tepkisel** (+77…+177 ms). Aksiyon dağılımındaki
  aykırılığıyla örtüşüyor (D %15.2 vs ~%2). İki bağımsız ölçüde aynı kişinin
  ayrışması, ölçünün gerçek bir şey yakaladığına işaret.
- **Koşul etkisi küçük:** katılımcı içi profil −8.1 / −1.5 / +7.4 / −1.6 /
  +3.8 ms, yayılım ~15 ms. Kişiler arası yayılım −180…+177 ms — bireysel
  farklar bir mertebe büyük.
- **Öğrenme ekseninde belirgin kayma yok:** deneme beşlikleri −42.0 / −63.9 /
  −55.2 / −50.2 / −55.1 ms. İlk on denemeden sonra sıçrama, sonra düz.
  §3.2'deki beklenti uyarısıyla tutarlı.

### Yeni kural: açılar arası karşılaştırma yapılmayacak

Zero crossing açı büyüdükçe negatifleşiyor (−13/−53/−98/−145 ms). Bu "büyük
açılarda daha öngörülü" değil: pole önce 5°'yi sonra 20°'yi geçtiği için aynı
reversal olayı daha geç referanslara göre daha negatif çıkıyor. Ölçtük —
aynı düşüşte 5°→20° geçişi medyan 256 ms sürüyor, zero crossing farkı 132 ms.
Yani gradyanın kabaca yarısı geometri. **Açı sabitlenip koşul/deneme sırası
boyunca karşılaştırılacak.**

`Documentation/Yontem/05_Action_Timing.md` yazıldı; NB04'ün ne yapacağı orada
maddelendi. Fizibilite scriptleri scratchpad'de, kod henüz `src/`'ye alınmadı.

---

## 2026-08-30 — Belgelendirme altyapısı

- `Documentation/Yontem/` kuruldu: veri işleme, fizik/T₀, durum-aksiyon-episode,
  performans metrikleri. Her kayıtta tanım, kod referansı, karar, kanıt ve
  neyi beslediği var.
- `Pilot_Sonuc_Ozeti.md` yazıldı — sunumun sonucu ilk kez metin olarak kayda
  geçti. Daha önce sadece `90_sunum.ipynb` ve HTML'de duruyordu; klasördeki
  pptx/docx 26 Ağustos tarihli ve 12 katılımcılık analizden önce hazırlandığı
  için sayıları geçersiz.
- `Veri_Kayit_Istekleri.md` 12 katılımcıya göre revize edildi.
- Dört `ABOUT.md` placeholder'ı gerçek içerikle değiştirildi.
- **Action timing yazılmadı**, önce yöntem kararları verilecek. Ludolph'un
  prosedürü çıkarıldı ve transferde karar gerektiren noktalar belirlendi
  (aşağıda).

### Sorular üzerine yapılan düzeltmeler ve ölçümler

Anlatım artifact'ı (`Ters Sarkaç Analiz Rehberi`) üzerine gelen sorular birkaç
hatayı ve eksiği ortaya çıkardı:

- **Girdi cihazı klavye değil, `Xbox Controller`.** Metadata'ya bakmadan veri
  desenine bakıp klavye çıkarımı yapmıştım, yanlıştı. Doğrusu analog kol:
  sıfır olmayan 136 farklı büyüklük, ~0.0098 adım, doyum örnekleri sıfır
  olmayanların ~%5'i. Girdi dereceli. Bu, Ludolph'un "ortalama kuvvet eğrisi
  sigmoid" varsayımı için iyi haber — action timing risk seviyesi
  "muhtemelen çalışmaz"dan "muhtemelen çalışır, teyit et"e indi.
- **"Korelasyon 0.988–0.997, model doğrulandı" eksik bir ifadeydi.**
  Korelasyon ölçekten bağımsız. `l = 1.0` ile korelasyon neredeyse aynı
  (0.9884–0.9971), ama RMS hatası 0.189'dan 0.997'ye çıkıyor. `l = 0.5`'i
  pinleyen şey RMS ve serbest düşüş testi. `l` = mafsaldan kütle merkezine
  mesafe; `4/3` katsayısı çubuğun atalet momentinden.
- **"11 örnek yeterli mi" sorusu yanlış çerçeveydi.** T₀ tahmin edilmiyor,
  modelden deterministik hesaplanıyor; 11 episode bir sınav. `l = 1.0` ile
  oran her seferinde ~0.71 çıkardı. Sınırı: 11 episode T₀'nın 2.20–3.38 s
  aralığını kapsıyor, üst uç (9.68 s'ye kadar) test edilmedi.
- **T₀'ın kalan işi netleştirildi:** doğrulama (bitti), zorluk kovaryantı,
  survival analizi. Performans metriği değil.
- **Ludolph tipi olay sayıları ölçüldü** — fizibilite sorunu yok:
  ±25° 110.091, ±15° 79.607, ±10° 57.549, ±5° 29.198 düşüş yönlü geçiş.

### Action timing çerçevesinde iki düzeltme

1. **Duvar saatine ihtiyaç yok, `trial_order` zaten zaman ekseni.** Denemeler
   arka arkaya yapılıyor, oturum ~21 dakika (53 × 20 s aktif + ~115 s reset +
   53 × 1.5 s ara). Ludolph'un 2 dakikalık penceresi ≈ 6 deneme. Pencerenin
   asıl işi öğrenme izlemek değil, ortalama alacak kadar segment toplamak.
2. **Action timing'e iki eksende birden bakılacak:** deneme sırası (öğrenme —
   tepkiden öngörüye geçiş) ve koşul (gürültü bunu bozuyor mu). Önceki
   öneri sadece koşul eksenine daraltıyordu, yanlıştı. Uyarı: Ludolph bir
   saatten uzun ve zorluğu artan bir görevde öğrenme ölçtü; bizde tek oturum,
   21 dakika, sabit g — öğrenme sinyali çıkmazsa "öğrenme yok" demek olmayabilir.

Ayrıca velocity elemesi için **atmak yerine stratification** önerildi (yavaş/orta/hızlı
bantlar), ve açı aralığı tek değer yerine taranacak (±25, ±15, ±10, ±5).

### Açık kalan: action timing transfer kararları

Ludolph'un dört adımı (makale s. 11) çıkarıldı: (i) −25..+25° tamsayı açılar
event, alt-frame çözünürlük lineer interpolasyonla; (ii) pole yukarı
dönüyorsa ve açısal hız %20–80 kuantilleri dışındaysa eleme; (iii) event'e
ortalanmış 1 s'lik force segmenti; (iv) 2 dakikalık kayan pencerede
ortalama, ortalama segmentin zero crossing = action timing. Variability =
zero crossing çevresinde ±60 ms'de force'un ortalama sd'si.

Beş karar açılmıştı; dördü yukarıdaki tartışmayla kapandı, biri açık kaldı.

1. ~~Toplama birimi~~ → **kapandı.** `trial_order` zaman ekseni olarak
   kullanılacak; action timing hem deneme sırasına hem koşula göre bakılacak.
2. ~~Hız kuantili elemesi~~ → **kapandı.** Bant katılımcı başına, bütün
   koşullar havuzlanarak hesaplanacak. Ayrıca elemek yerine **stratification**
   tercih edilecek (yavaş/orta/hızlı). Eleme gerekçesi: yöntem onlarca
   segmenti üst üste bindirip ortalıyor; çok farklı hızlardaki geçişleri aynı
   ortalamaya koymak eğriyi bulanıklaştırır ve sıfır kesişimini anlamsızlaştırır.
3. ~~Event aralığı~~ → **kapandı.** Tek değer yerine ±25 / ±15 / ±10 / ±5
   taranacak. Olay sayıları hepsinde yeterli.
4. ~~Episode sınırını aşan segmentler~~ → **kapandı.** Sınırı aşan segmentler
   kırpılmadan tamamen atılacak (reset satırlarında `applied_force_n` sahte).
5. **Açık: sigmoid varsayımı.** Ludolph'un yöntemi "ortalama segment
   sigmoiddir, sıfırı bir kez keser" varsayımına dayanıyor. Analog kol bunu
   destekliyor ama aktif örneklerin %73.9'u tam sıfır. Kod yazmadan önce tek
   bir event açısında ampirik kontrol yapılacak.

---

## 2026-08-28 — NB02 yeniden çalıştırma, NB03

- **NB02, 12 katılımcıyla yeniden çalıştırıldı.** Çıktıları 7 katılımcılık
  kalmıştı (P008–P012 27 Ağustos 17:00'de inmiş, NB01 yeniden koşmuş ama
  NB02 koşmamıştı). Sonuç: 846.060 sample, 2.017 episode, 18.891 regime run,
  35.519 event.
- Üç doğrulama da tuttu: fizik modeli korelasyon 0.988–0.997; T₀ serbest
  düşüş testi **11 episode'un 11'inde** `duration/T₀ = 1.0000`; `fall` event
  sayısı Unity'nin `fall_count`'uyla birebir (1.381).
- **`check_angle_stream` 12 katılımcıyla çalıştırıldı.** P001–P007 hâlâ tek
  ortak açı dizisinden okuyor; P008–P012 ayrı gruplara düşüyor. Bu "farklı
  seed" değil — metadata'da hepsinde 12345 var ve hiçbiri offset 0'da değil.
  Bitişik ama örtüşmeyen dilimler eşleştirilemediği için algoritma zinciri
  göremiyor. Pratik sonuç: katılımcılar arası hizalama kısmen kırılmış,
  yanlılığın sönmeme riski azalmış. Başlangıç |θ| yayılımı 0.47° → 0.35°,
  `fall_count` korelasyonu +0.14 → +0.066.
- **NB03 yazıldı ve çalıştırıldı.** `src/performance.py` + `03_performance.ipynb`.
  Çıktı: `trial_metrics.parquet` (600), `participant_condition.parquet` (60).

### Kararlar

- **sIQR_theta ve sIQR_omega karar setine girmiyor.** Kriter korelasyondan
  trend'e çevrildi: asıl soru metriğin RMS'ten farklı olup olmadığı değil,
  RMS'in görmediği bir noise trendi görüp görmediği. sIQR_theta trendin
  %9'unu, sIQR_omega %21'ini (ters işaretli) taşıyor. maPA da RMS'in kopyası
  (r = 0.98) — ikisinden sadece biri raporlanacak, maPA seçildi.
- **Bağımsız süre metriği kullanılmıyor, T/T₀ reddedildi.** `mean_episode_s`
  düşüş sayısının deterministik dönüşümü çıktı (`corr = 1.0000`, çünkü
  episode sayısı = düşüş + 1 ve trial sabit 20 s). T₀'a bölmek kirliliği
  azaltmıyor artırıyor (katılımcı × koşul düzeyinde θ₀ korelasyonu 0.229 →
  0.645). Sansürsüz sürümler hayatta kalma yanlılığı taşıyor. Ludolph'un
  süre ölçütü için survival analizi gerekir; gerekirse NB05.
- **Stabilizasyon süresi kendi eşiğimizle.** Unity'nin `within_bounds_time_s`'i
  failure limitini kullanıyor, 600 trial'da ortalama 19.97 s sd 0.04 — tavana
  yapışık. 30° eşiğiyle 18.22 s, sd 1.67.
- İstatistiksel test NB03'e **girmiyor**, NB06'nın işi. Sunum notebook'u
  aceleye geldiği için ikisini birleştirmişti; zincir o şekilde bırakılmadı.

### Yeni tespitler

- `valid_trial` artık hep 1 değil: P011'in T030 ve T034 trial'ları
  `invalid_reason = "paused"` işaretli. Bizim `flag_trials`'ımız bu kolona
  bakmıyor, ikisi de `qc_pass`. İncelendi, veri normal görünüyor (1200 tam
  sample, focus kaybı yok). 600'de 2, düşük etkili ama kural eklenmeli.
- `check_angle_stream` `src/qc.py`'de var ama NB01 §7'de çağrılmıyor.
  CLAUDE.md çağrıldığını söylüyordu, düzeltildi.

---

## 2026-08-28 (sabah) — Sunum analizi

`90_sunum.ipynb` + `src/presentation.py` yazıldı ve 12 katılımcıyla
çalıştırıldı. İzole modül: zincirin geri kalanı import etmiyor, sadece
`data/interim` okuyor.

**Bulgu: U şekli yok, monoton bozulma.** Lineer kontrast maPA'da p = 0.0005,
kuadratik p = 0.62. N2/N3/N4 baseline'dan anlamlı kötü (Holm sonrası), N1'de
fark yok. Ayrıntı: [Pilot_Sonuc_Ozeti.md](Pilot_Sonuc_Ozeti.md).

---

## 2026-08-27 — NB01, NB02, veri büyümesi

- NB01 (load & QC) ve NB02 (build) yazıldı.
- Gün içinde katılımcı sayısı 7'den 12'ye çıktı; NB01 yeniden çalıştırıldı.
- Fizik modeli veriden çıkarıldı ve doğrulandı; `l = 0.5` (yarım uzunluk)
  tespiti yapıldı.
- Park'ın işaret konvansiyonunun **aynen aktarılamayacağı** ölçüldü:
  düzeltici kuvvet bizde θ ile **aynı** işaretli.
- Düşüş sebebinin iki tane olduğu (`angle` / `track`) bulundu, `TrackLoss`
  etiketi eklendi.
- `randomizationSeed` sorunu veriden doğrulandı.

---

## 2026-08-26 — Kurulum

- Repo yapısı, `drive_sync.py` ile Drive'dan veri çekme.
- İlk pilot verisi (P001, P002) incelendi, `Veri_Kayit_Istekleri.md` yazılıp
  ekibe iletildi.
- Not: o günkü P001/P002 smoke test verisiydi ve sonradan silindi. Şu anki
  P001/P002 farklı, gerçek katılımcılar.
