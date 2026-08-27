# CLAUDE.md

## Proje

Cart-pole dengeleme görevinde görsel noise seviyelerinin motor öğrenmeye etkisini araştıran bir deney. Stochastic resonance hipotezi: orta düzey görsel noise, zayıf/dinamik sinyalin algılanmasını kolaylaştırarak kontrolü iyileştirebilir (Treviño 2016). Pilot çalışma 5 koşul (no_noise, N1=σ0.02, N2=σ0.05, N3=σ0.08, N4=σ0.25) × 10 tekrar = 50 measurement trial. Ana deney büyük ihtimalle pilottan seçilen tek bir noise seviyesini kullanacak.

## Rolüm

Veriyi ben analiz ediyorum, deneyi ben yapmıyorum, tasarımı değiştiremem. Kayıt tarafına sadece "şu alanı da kaydedin" diyebiliyorum (bkz. `Documentation/Veri_Kayit_Istekleri.md`).

## Veri durumu

2026-08-27 itibariyle Drive'daki katılımcılar **gerçek**. Eski smoke test verisi (P001/P002) silindi, artık Drive'da yok. O gün içinde P001–P007'ye ulaşıldı, veri toplama sürüyor — sayı NB01'in ilk hücresi çalıştırıldığında güncellenir.

Her katılımcı tek oturum, 53 trial (3 practice + 50 measurement). Davranışsal analiz yapılabilir. Randomizasyon durumu için bkz. "Veride görülen sorunlar" §1.

## Veri

### Kaynak

Google Drive klasörü `Pendulum_Data`, id `1iDMZt3iUN-mHaemXXI_qNA9GkYUMf5t6`

Klasör "bağlantıya sahip herkes" olarak paylaşıldığı için kimlik doğrulama yok: API anahtarı, OAuth, `client_secrets.json`, `rclone config` — hiçbiri gerekmiyor. `src/drive_sync.py` `gdown` ile klasörü listeler, sadece beklenen üç dosya tipini indirir. Var olan dosya tekrar indirilmez, yerelde olup Drive'da olmayan hiçbir şey silinmez (sync değil, copy semantiği). Veri repoya commit edilmez.

### Klasör yapısı

```
Pendulum_Data/
└── <participant_id>/                       # P001, P002, ...
    └── <session_id>/                       # S20260826_100227
        ├── <pid>_<sid>_metadata.json
        ├── <pid>_<sid>_timeseries.csv
        └── <pid>_<sid>_trial_summary.csv
```

Lokal hedef: `Data Analysis/data/raw/`

### metadata.json — oturumda bir kez

Mevcut alanlar: `participant_id`, `session_id`, `created_at`, `unity_version`, `platform`, `input_device`, `noise_type`, `noise_definition`, `noise_element_size_px`, `fixed_delta_time_s`, `gravity`, `cart_mass_kg`, `pole_mass_kg`, `pole_length_m`, `max_force_n`, `track_limit_m`, `angle_limit_deg`, `config` (`participantId`, `practiceTrials`, `rounds`, `trialDurationS`, `resetDurationS`, `interTrialPauseS`, `breakEveryNTrials`, `randomizationSeed`, `noiseLevels[]`), `condition_order[]`

### timeseries.csv — her FixedUpdate'te bir satır (60 Hz)

24 kolon: `participant_id`, `session_id`, `trial_id`, `trial_order`, `round_index`, `condition_order_in_round`, `practice`, `noise_level_id`, `noise_sigma`, `noise_seed`, `sample_index`, `t_trial_s`, `fixed_delta_time_s`, `phase`, `pole_angle_deg`, `pole_angular_velocity_deg_s`, `cart_position_m`, `cart_velocity_m_s`, `input_raw`, `input_applied`, `applied_force_n`, `fall_event`, `is_resetting`, `window_focused`

### trial_summary.csv — trial sonunda tek satır

27 kolon: `participant_id`, `session_id`, `trial_id`, `trial_order`, `round_index`, `condition_order_in_round`, `practice`, `noise_level_id`, `noise_sigma`, `noise_seed`, `planned_duration_s`, `active_duration_s`, `reset_duration_s`, `fall_count`, `within_bounds_time_s`, `mean_abs_pole_angle_deg`, `rms_pole_angle_deg`, `max_abs_pole_angle_deg`, `mean_abs_cart_position_m`, `rms_input_applied`, `sample_count`, `termination_reason`, `valid_trial`, `invalid_reason`, `mean_fps`, `min_fps`, `dropped_frame_count`

### Veri katmanları

Raw Sample (FixedUpdate satırı) → Clean Sample (preprocessed) → Event (onset / offset / reversal / fall) → **Regime run** (Safe / Saved / Failed / TrackLoss) → **Episode** (reset'ten reset'e) → Trial → Participant × Condition (10 tekrarın özeti)

Episode ve regime run **aynı şey değil**, karıştırılmamalı:

| Birim | Tanım | Sayı (7 katılımcı) | Ne için |
|---|---|---|---|
| Episode | reset'ten reset'e | 1.277 | T₀, süre (Ludolph) |
| Regime run | kuadran dizisi, θ·ω işaret değiştirince yeni run | 10.855 | Safe/Saved/Failed (Park) |

Episode başına ortalama 8.5 run düşüyor.

## Fizik parametreleri (Ludolph 2017 ile aynı)

| Parametre | Değer | Kaynak |
|---|---|---|
| Cart kütlesi | 0.40 kg | Ludolph |
| Pole kütlesi | 0.08 kg | Ludolph |
| Pole uzunluğu | 1.00 m | Ludolph |
| Yerçekimi | 1.00 m/s² | Ludolph başlangıç seviyesi, pilotta sabit |
| Kuvvet sınırı | ±4 N | Ludolph |
| Ray sınırı | ±5 m | Ludolph |
| Açı sınırı (fall) | ±60° | Ludolph |
| Başlangıç açısı | U(−7.5°, +7.5°) | Ludolph |
| İntegrasyon | RK4, Δt = 1/60 s | Ludolph |
| Trial süresi | 20 s | Pilot kararı |
| Reset süresi | 1.0 s | Pilot kararı |

Not: Ludolph'ta yerçekimi performansa göre 3.5 m/s²'ye yükseliyordu; pilot noise etkisini izole etmek için g'yi 1.0'da tutuyor.

## Literatürden alınacak ölçütler

### Ludolph et al. 2017 (Scientific Reports 7:13191)

- Fizik parametreleri (yukarıdaki tablo)
- **T/T₀**: normalized trial length. T = gerçek trial süresi, T₀ = force uygulanmasaydı serbest düşüşle kaç saniyede fall limitine varırdı. Performansı "hiçbir şey yapmamak"a göre ölçer. **Aynen aktarılamaz** — bkz. aşağıdaki T₀ bölümü.
- **Action timing**: pole belirli bir tamsayı açıdan geçerken force'un yön değiştirme zamanı (zero crossing). Negatif = predictive (olay öncesi), pozitif = reactive. 2 dakikalık pencerelerle hesaplanır.
- **Action variability**: force yön değiştirme anı civarında (±60 ms pencere) force'un standart sapması.
- Trial length 30 s cap, başarılı = düşmeden tamamlanan. Inter-success interval.
- İki grup: gradual gravity (g=1.0→3.5, performansa bağlı artış) vs. constant gravity (g=3.5). Gradual grup daha iyi öğreniyor.

### Park et al. 2025 (Experimental Brain Research 243:44)

- **State space**: phase plane (θ, ω). `θ*ω > 0` → falling state (açı ve hız aynı yöne, düşmeye doğru). `θ*ω < 0` → safe state (dikeye dönüyor).
- **Action taksonomisi** (joystick command türleri):
  - **I** (Inactivity): girdi yok
  - **CR** (Corrective Reaction): safe state'e doğru kuvvet
  - **D** (Destabilizing): falling state'te düşme yönüne kuvvet
  - **A** (Anticipatory): overshoot engellemek için erken frenleme
- Düzeltici kuvvetin işareti veriden doğrulanmalı, varsayılmamalı.
- **Üç balancing regime**: Safe (DOB civarı), Saved (fall quadrant girip kurtarılan), Failed (fall boundary'ye ulaşan). OA vs YA farkı sadece Failed regime'de belirgin. Bizde dördüncü bir etiket gerekti: **TrackLoss** (bkz. aşağıdaki düşüş sebebi bölümü).
- Park'ın I tanımı: joystick sapmasında ±1°'lik nötr band. Footnote önemli — banda takılıp kalan değerler I sayılır, joystick soldan sağa geçerken banddan hızlı geçiş sayılmaz.
- VIP: Kp = 171.9°/s², Kj = 9.5 s⁻², ±60° fall boundary, 30 s trial, 50 Hz render + 200 Hz sampling.

### Treviño et al. 2016 (Frontiers in Human Neuroscience 10:572)

- **Stochastic resonance**: orta düzey noise, subthreshold sinyalin algılanabilirliğini artırır. Inverted-U response (%CCI vs. noise luminance).
- Optimal noise: %5 luminance'ta peak, %25'te performans düşüşü. %12 üzerinde doyma.
- Noise: her frame'de yenilenen dinamik uniform pixel noise. Dot size 2×2 pixel ≈ 0.08° görsel açı. 60 cm izleme mesafesi.
- **Kritik ön koşul**: sinyal kasıtlı olarak threshold'un altına indirilmiş (düşük coherence + düşük luminance). Cart-pole'daki pole ise yüksek kontrastlı ve büyük — threshold'un çok üzerinde. SR hipotezinin bu göreve transfer edilebilirliği açık bir soru.
- Noise seviyeleri logaritmik ölçekte aralıklı. Pilotun seviyeleri (0, 0.02, 0.05, 0.08, 0.25) altta yaklaşık lineer, sonra 3.1× sıçrama.

## Noise seviyeleri

| Koşul | noise_sigma | Not |
|---|---|---|
| no_noise | 0.00 | Noise üretimi kapalı |
| N1 | 0.02 | Düşük |
| N2 | 0.05 | Orta-düşük |
| N3 | 0.08 | Orta |
| N4 | 0.25 | Yüksek |

## Notebook zinciri

| # | Notebook | İçerik |
|---|---|---|
| 01 | Load & QC | Veri yükleme, yapısal bütünlük, zaman/sinyal kontrolleri, QC bayrakları |
| 02 | Build | Episode + regime run segmentasyonu, state (safe/fall), action sınıfı (I/CR/A/D/X), T₀, event tespiti. Çıktı: `samples_built` / `episodes` / `regimes` / `events` parquet |
| 03 | Performance | Trial düzeyi metrikler (maPA, falls, within_bounds, RMS, control effort, sIQR) |
| 04 | Control mechanism | Action timing, variability, latency, I/CR/D/A dağılımları |
| 05 | Learning | Pilotta işi varyans/güç tahmini; koşullar arası öğrenme karşılaştırması DEĞİL |
| 06 | Noise kararı | Koşul × metrik tablosu, U-şekil kontrolü, aday seçimi |

02 var çünkü 03 ve 04 aynı türetmeyi iki kere yapmasın. 04, 05'ten önce çünkü learning kriteri action timing'i girdi olarak kullanıyor. Drive'dan veri çekme NB01'in ilk hücresi (`src/drive_sync.py`).

## Notebook 01 içeriği

0. **Drive'dan çek**: `sync_data`, var olanı atlar
1. **Keşif ve yükleme**: oturumları bul, üç dosyayı oku, sample düzeyi ve trial düzeyi iki tablo üret
2. **Yapısal bütünlük**: dosya varlığı, trial sayıları (3 practice + 50 measurement bekleniyor), koşul dengesi (her turda 5 koşul × 1), metadata alanları
3. **Zaman ve örnekleme**: dt vs fixed_delta_time_s, time reversal, gap, sample_index atlaması, duplicate, NaN, açı aralığı (−180°..+180°)
4. **Sinyal akıl sağlığı**: hızlar pozisyon türeviyle tutuyor mu, force = input_applied × max_force_n mı, fall_event sadece ilk adımda mı, phase/is_resetting tutarlı mı. Türev kontrolü kesintisiz `active` parçalarda ayrı yapılır — trial içinde düşüş olunca 1 s reset bloğu giriyor ve pole yeni başlangıç açısıyla devam ediyor; `phase == "active"` satırlarını uç uca eklemek sahte sıçrama üretir.
5. **Trial geçerliliği**: valid_trial kolonuna GÜVENİLMEZ, kendi `qc_pass` ve `qc_flags` bayrağımız üretilir
6. **Sample maskesi**: `analysis_include = (phase == "active") & (practice == 0) & qc_pass & (window_focused == 1)`. (is_resetting == 0 gereksiz, phase == "active" ile birebir aynı)
7. **Randomizasyon doğrulaması**: metadata'daki `condition_order` iddiası trial_summary ile karşılaştırılır; katılımcılar arası koşul sırası / noise_seed özdeşliği veriden ölçülür; koşul × trial_order ve tur içi pozisyon tabloları; başlangıç açısının koşullar arası dengesi ve sonuca etkisi; `check_angle_stream` ile ortak RNG açı dizisi ve giriş offsetleri
8. **Format regresyon takibi**: `Veri_Kayit_Istekleri.md`'deki istenen alanlar geldi mi

### NB01 kararları

- Bir katılımcının birden fazla oturum klasörü varsa en çok measurement trial içeren alınır, diğerleri raporda "yarım" olarak görünür. Birleştirilemez: uygulama yeniden başlayınca aynı condition_order ile trial 1'den başlıyor, trial'lar tekrar oluyor.
- QC'den düşen trial sadece kendisi çıkar, oturum düşmez. Rapor eşik üstünde uyarır.
- Şimdilik sadece ölü input kuralı (`max(|input_raw|) == 0` tüm trial boyunca). fps ve düşük aktivite eşikleri gerçek veri gelene kadar config'te null, kod null ise o kuralı atlar.

## Notebook 06: noise seviyesi nasıl seçilecek

Koşul tablosu — satırlar: no_noise / N1 / N2 / N3 / N4, sütunlar: falls (düşük iyi), within_bounds (yüksek iyi), maPA (düşük iyi), RMS_theta, control effort (düşük iyi)

Prosedür:
1. Katılımcı başına 10 tekrarın özeti
2. Participant × condition düzeyinde birleştir
3. Grup genelinde noise–performance eğrisine bak, U şekli var mı
4. Ana kriterler birbirine çok yakın çıkarsa RMS_theta ve control effort tie-breaker
5. Seçilen sonucu katılımcı düzeyinde kontrol et: tek bir kişinin kötü performansından mı geliyor

## Veride görülen sorunlar

Önem sırasına göre. 1 ve 8 gerçek veride doğrulandı, geri kalanı hâlâ "bakılacak" listesinde:

1. **randomizationSeed 12345'e sabitlenmiş.** Veriden doğrulandı (metadata'ya bakmadan, NB01 §7):

   - **Koşul sırası özdeş** — bütün katılımcılar aynı 50 trial'lık diziyi alıyor.
   - **noise_seed dizisi özdeş** — herkes aynı noise desenini görmüş.
   - **Başlangıç açıları da aynı listeden** — tek bir sabit açı dizisi var, yedi katılımcının hepsi ondan okuyor (hizalama %100). Giriş noktaları farklı: P001/P002/P004/P006 offset 0, P003 76, P007 89, P005 253. Offsetler oturum zincirini birebir doğruluyor — P002 tam 76 çekiliş yapmış ve P003 76'dan giriyor; P004 tam 253 yapmış ve P005 253'ten giriyor. Yani **uygulama katılımcılar arasında kapatılmadığında RNG akışı kaldığı yerden devam ediyor**, kapatılınca 0'a dönüyor.

   Açıların dışarıdan bağımsız görünmesinin sebebi: imleç davranışa göre ilerliyor, her düşüş bir çekiliş tüketiyor. Farklı düşüş sayısı → aynı listenin farklı yerleri. İz: P001'in T002'de aldığı −4.0469'u P002 T005'te alıyor.

   **Pilot kararına (NB06) etkisi ölçüldü, küçük:** başlangıç |θ| koşullar arasında dengeli (ortalamalar 3.48–3.95°, yayılım 0.47°, trial içi sd 2.09°) ve sonuçla korelasyonu zayıf (fall_count ile r=+0.14). Tahmini bulaşma koşul ortalamasında ~0.1 düşüş, tipik ~2.2 düşüşün %5'i.

   Asıl mesele şu: bu ~%5'lik yanlılık herkeste **aynı yönde** olduğu için katılımcı ekledikçe sönmüyor. Koşullar birbirine yakın çıkarsa (tie-breaker senaryosu) yanlılık ölçülmek istenen etkiyle aynı büyüklükte olur. Düzeltme için bkz. T₀ bölümü — Ludolph'un T/T₀'ı aynen değil, episode düzeyinde uygulanmalı.

   Koşul sırası tarafında ise **her tur içinde yeniden karılıyor**, sabit olan 50 trial'lık dizinin tamamı. Her koşulun ortalama `trial_order`'ı 24.6–26.5 (1–50 aralığında) — öğrenme/yorgunluk koşulla karışmamış, asıl korkulan confound yok. Tur içi pozisyon dağılımı tümsekli ama tur sayısı az (hücre başına beklenen 2), bu büyüklükte sapma tek çekilişte şansa girer; tablo betimleyicidir, kusur testi değil.

   **Ekibe tek istek:** seed'i katılımcı id'sinden türetin ve her oturumda RNG'yi yeniden tohumlayın. Bu üç sorunu birden çözer. NB01'de `shared_condition_order` / `shared_randomization_seed` WARN veriyor, §7'de `check_angle_stream` akışı gösteriyor.
2. **Reset satırlarında applied_force_n 0'a zorlanıyor** ama input_applied son değerinde kalıyor. Action timing analizi için sorun: sahte zero-crossing'ler üretiyor.
3. **Reset'te hızlar tam sıfırlanmıyor** — Ludolph ikisinin de sıfır olmasını istiyor. Başlangıç koşulları karşılaştırılabilir olmuyor.
4. **valid_trial her trial'da 1**, invalid_reason hiç dolmuyor (ölü controller trial'ları dahil).
5. **Metadata'da eksik alanlar**: ekran boyutu/çözünürlük/izleme mesafesi, input deadzone, noise texture parametreleri, balance eşikleri. Tam liste: `Documentation/Veri_Kayit_Istekleri.md` §6.
6. **within_bounds_time_s** failure limitini (60°/5 m) kullanıyor, her trial'da ~19.95 s çıkıyor; ayrı ve daha dar bir eşik seçilmeli.
7. **Sample düzeyinde frame timing yok** — düşük öncelikli.
8. **`config.participantId` hiç güncellenmiyor** — P002–P005'in metadata'sında da "P001" yazıyor. `participant_id` alanı doğru, sadece `config` bloğundaki kopya yanlış. NB01'de `config_participant_id` kontrolü WARN veriyor.

## Park state ve action tanımları

```
fall_state  = θ * ω > 0    # hem eğik hem düşeceği tarafa dönüyor
safe_state  = θ * ω < 0    # eğik ama dikeye dönüyor
```

### İşaret konvansiyonu — veriden doğrulandı

Park "joystick işareti θ'nın **tersi** = CR" diyor. Bu bize **aynen aktarılamaz**: Park'ın VIP'inde joystick doğrudan açısal ivme veriyor, bizim cart-pole'da kuvvet cart'a gidiyor ve işaret ters çevriliyor.

Ölçüm: `F > 0` iken ortalama `dθ/dt = −21°/s`, `F < 0` iken `+25.6°/s`. Katılımcı davranışı da aynı yönde (θ = +2..+10° iken ortalama input +0.025). Yani **düzeltici kuvvet θ ile aynı işaretli.**

### Sınıflar (çevrilmiş konvansiyonda, `src/build.py`)

```
I  : |u| ≤ band              nötr banddaki kalıcı girdi
CR : u·θ > 0                 düzeltici, her kuadranda
A  : u·θ < 0  ve  θ·ω < 0    dikeye dönüşü frenleme (sadece safe)
D  : u·θ < 0  ve  θ·ω > 0    düşüş yönüne kuvvet (sadece fall)
X  : sınıflandırılmayan      banddan geçici geçiş / dejenere işaret
```

Eşikler `config.yaml` → `build`: `input_neutral_band: 0.02`, `neutral_transient_max_samples: 3`.

Band 0.02 seçildi çünkü örneklerin **%73.5'i tam sıfır**, sıfır olmayan en küçük değer ~0.015 — Unity deadzone'u zaten uygulamış. `input_raw` ile `input_applied` birebir aynı (max fark 0.000000), iki kolon gereksiz.

### Mevcut dağılım (7 katılımcı, active örnekler)

```
I  73.5%    CR 22.8%    D 3.4%    A 0.29%    X 0.01%
kuadran: fall 64.2%, safe 35.8%
```

**A çok seyrek (%0.29).** Park'ta anlamlı bir orandı. Muhtemel sebep: zamanın %64'ü fall kuadranında geçiyor, katılımcılar düşüşle boğuşuyor, dikey civarında ince ayar yapmıyor. Bulgu, bug değil — ama bu seyreklikte istatistiksel olarak kullanılıp kullanılamayacağına NB04'te karar verilecek.

Rejim başına profil Park'ın niteliksel örüntüsüyle uyuşuyor: Failed'da D en yüksek (%28.8) ve CR en düşük (%17.0); Safe'te CR en yüksek (%40.1).

## Düşüş sebebi: iki tane var

`fall_event` iki farklı sebeple tetikleniyor ve **ayırt edilmeli**:

| Sebep | n | Düşüş anında ort. abs(θ) |
|---|---|---|
| `angle` — pole ±60°'ye vardı | 814 | 61.0° |
| `track` — cart ±5 m ray sınırına çarptı | 92 | 21.0° |

Örtüşme sıfır, açıklanamayan sıfır. Ray kaynaklı düşüşlerin biri 0.27°'de olmuş — pole dimdikken cart raydan çıkmış. 92'sinin **29'u safe kuadranında**, yani pole dikeye dönerken.

Park'ta bunun karşılığı yok. O yüzden `Failed` sadece açı kaynaklı düşüşler için kullanılıyor (Park'la karşılaştırılabilir olan bu), ray kaybına ayrı `TrackLoss` etiketi veriliyor ve Park karşılaştırmalarından çıkarılıyor.

Rejim dağılımı: Safe %44.9, Saved %44.6, Failed %7.5, censored %2.2, TrackLoss %0.8.



## T₀ ve fizik modeli

### Doğrulanmış model

Model veriden doğrulandı (8 uzun kesintisiz parça, gözlenen açısal ivme ile korelasyon **0.989–0.997**). Standart cart-pole:

```
temp = (F + m_p · l · ω² · sinθ) / (m_c + m_p)
θ''  = (g · sinθ − cosθ · temp) / (l · (4/3 − m_p · cos²θ / (m_c + m_p)))
x''  = temp − m_p · l · θ'' · cosθ / (m_c + m_p)
```

- `m_c = 0.40`, `m_p = 0.08`, **`l = 0.5`** (yarım uzunluk; tam pole 1.0 m, düzgün çubuk), `g = 1.0`
- `F` işareti `applied_force_n` ile doğrudan aynı, kuvvet gecikmesi yok, sönüm yok
- RK4, Δt = 1/60

Kod: `src/physics.py` — `params_from_config`, `cartpole_deriv`, `rk4_step`, `compute_T0`, `T0_for_angles` (aynı açı tekrar ettiği için cache'li), `verify_model`. Parametreler `config.yaml` → `physics` ve `t0` altında.

### T₀ hesabı

T₀ = (θ₀, ω=0) durumundan sıfır kuvvetle |θ| = 60°'ye varana kadar geçen süre. F=0 iken dinamik sadece (θ, ω)'da kapalı, x ve v geri beslemiyor — yani T₀ tek başına θ₀'ın fonksiyonu.

| θ₀ | 0.5° | 1° | 2° | 3° | 4° | 5° | 6° | 7° | 7.5° |
|---|---|---|---|---|---|---|---|---|---|
| T₀ | 4.23 s | 3.70 | 3.18 | 2.87 | 2.65 | 2.48 | 2.33 | 2.22 | 2.17 |

Gerçek episode'larda: ort 2.93 s, aralık 2.17–9.68 s.

**Ampirik doğrulama (NB02 §2b).** Katılımcının hiç girdi vermediği ve açı limitiyle biten episode'lar tanım gereği serbest düşüştür — süreleri T₀'a eşit olmalı. Böyle 5 episode var ve beşinde de `duration/T₀ = 1.0000`, standart sapma sıfır. Fizik modeli, RK4 adımı, T₀ hesabı ve episode segmentasyonu zincirinin tamamı tek testte doğrulanmış oluyor. Kod: `build.validate_T0_freefall`.

### Ludolph'un T/T₀'ı aynen aktarılamaz

Ludolph'ta trial düşünce **biter**, o yüzden T değişken ve T/T₀ anlamlı. Bu pilotta trial sabit 20 s, düşüş olunca reset olup devam ediyor — T hep ≈20 s, dolayısıyla T/T₀ = 20/T₀ oluyor, yani saf θ₀ fonksiyonu. Ölçülen: `corr(|θ₀|, trial T/T₀) = +0.975`. Performans ölçmüyor.

Doğru karşılık **episode düzeyi**: her episode kendi başlangıç açısından başlar (trial başı ya da düşüş sonrası restart), süresi düşüşe ya da trial sonuna kadardır.

| Ölçüt | corr(&#124;θ₀&#124;, ölçüt) |
|---|---|
| Trial düzeyi T/T₀ | +0.975 |
| Episode düzeyi T_ep/T₀ | +0.116 |
| Episode süresi (ham) | −0.091 |

Not: ham episode süresi zaten başlangıç açısından neredeyse bağımsız; T₀'a bölmek hafif aşırı düzeltiyor. NB03'te ikisi de bakılır, hangisinin kullanılacağına orada karar verilir. Trial sonuna kadar giden episode'lar sağdan sansürlü (1107 episode'un 350'si), bu ayrıca ele alınmalı.

## Ek metrikler ve sinyal işleme

- **control effort** = RMS_u = sqrt(mean(u²)), u = input_applied
- **sIQR_theta** = (Q75(θ) − Q25(θ)) / 2
- **sIQR_omega** = aynısı angular velocity için
- sIQR'ın gerekçesi: iki katılımcının maPA'sı aynı olabilir ama biri çoğunlukla ±5° durup ara sıra ±50°'ye giderken diğeri sürekli ±15°'te olabilir. RMS birinciyi orantısız cezalandırır. sIQR_omega açı büyüklüğünden bağımsız olarak hareketin ne kadar dalgalı olduğunu ölçer.
- NB03'te bunların RMS'in üstüne bilgi getirip getirmediği KONTROL EDİLECEK, getirmiyorsa kullanılmayacak.
- Gerektiğinde filtre: action onset tespiti, force derivative, jerk, küçük salınımlar (scipy.signal).

## Çalışma kuralları

- Kod yazmadan önce sor. Ne yazacağını anlat, onay al, sonra yaz.
- Amaç dışı şeylerin peşine düşme. Bir veri kalitesi detayı noise seviyesi kararını değiştirmiyorsa uğraşma. Önemli olduğunu düşünüyorsan önce ne kadar önemli olduğunu söyle.
- Her şeyi eşit acil gösteren düz liste verme, etkiye göre sırala.
- Eşikler config.yaml'da, koda gömülmez.
- Mantık src/ altında modül olur, notebook'lar ince kalır.
- Kısa konuş. Rapor veya slayt formatı değil, düz anlat.
- Türkçe, teknik terimler İngilizce.

## Açık sorular

- Ana deney tek noise seviyesi + no_noise kontrol grubu mu, yoksa herkes aynı noise'u mu alıyor? Ekibe sorulacak, NB06'nın ne üreteceğini değiştirir.
- Pilot seviyeyi anlık performansa göre seçiyor, ana deney öğrenmeyi ölçecek. Ludolph'un bulgusu bu ikisinin ayrışabileceği yönünde. Rapora tek seviye yerine sıralı iki aday yazmak makul bir hedge.

## Veri kaynağı ve git

Kaynak: Google Drive klasörü `Pendulum_Data`, id `1iDMZt3iUN-mHaemXXI_qNA9GkYUMf5t6`
drive link: https://drive.google.com/drive/folders/1iDMZt3iUN-mHaemXXI_qNA9GkYUMf5t6

Yapı: `Pendulum_Data/<participant>/<session>/` ve içinde üç dosya.

Çekme: NB01'in "0. Drive'dan veri çek" hücresi, `sync_data(folder_id, RAW_DIR)`. Kimlik doğrulama yok — klasör herkese açık. Kodu çalıştıran herkes aynı veriyi kendi diskine indirebiliyor, o yüzden git'te tutmaya gerek yok.
