# Analiz günlüğü

Ne zaman ne yapıldı, ne karara bağlandı. Yeni giriş **üste** eklenir.

Kayıt tutma amacı: aylar sonra "bu sayı neden böyle" diye sorulduğunda
cevabın ve o günkü gerekçenin bulunabilmesi. Yöntem ayrıntıları
[Yontem/](Yontem/) altında, bu dosya sadece kronoloji ve kararlar.

---

## 2026-08-31 — NB06: karar verildi, SR desteklenmiyor

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
