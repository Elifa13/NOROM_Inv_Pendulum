# CLAUDE.md

## Proje

Cart-pole dengeleme görevinde görsel noise seviyelerinin motor öğrenmeye etkisini araştıran bir deney. Stochastic resonance hipotezi: orta düzey görsel noise, zayıf/dinamik sinyalin algılanmasını kolaylaştırarak kontrolü iyileştirebilir (Treviño 2016). Pilot çalışma 5 koşul (no_noise, N1=σ0.02, N2=σ0.05, N3=σ0.08, N4=σ0.25) × 10 tekrar = 50 measurement trial. Ana deney büyük ihtimalle pilottan seçilen tek bir noise seviyesini kullanacak.

## Rolüm

Veriyi ben analiz ediyorum, deneyi ben yapmıyorum, tasarımı değiştiremem. Kayıt tarafına sadece "şu alanı da kaydedin" diyebiliyorum (bkz. `Documentation/Veri_Kayit_Istekleri.md`).

## Veri durumu

2026-08-28 itibariyle Drive'da **12 katılımcı** var (P001–P012), hepsi gerçek. Eski smoke test verisi (P001/P002) silindi, artık Drive'da yok. Toplama 26–27 Ağustos'ta yapıldı; 28 Ağustos'ta Drive'da yeni dosya yok. Sayı NB01'in ilk hücresi çalıştırıldığında güncellenir.

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

| Birim | Tanım | Sayı (12 katılımcı) | Ne için |
|---|---|---|---|
| Episode | reset'ten reset'e | 2.017 | T₀, süre (Ludolph) |
| Regime run | kuadran dizisi, θ·ω işaret değiştirince yeni run | 18.891 | Safe/Saved/Failed (Park) |

Episode başına ortalama 9.4 run düşüyor.

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
- **Action timing**: pole belirli bir tamsayı açıdan geçerken force'un reversal zamanı (zero crossing). Negatif = predictive (olay öncesi), pozitif = reactive. 2 dakikalık pencerelerle hesaplanır.
- **Action variability**: force reversal anı civarında (±60 ms pencere) force'un standart sapması.
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
| 02 | Build | Episode + regime run segmentasyonu, state (safe/fall), action sınıfı (I/CR/A/D/X), T₀, girdi olayı tespiti. Çıktı: `samples_built` / `episodes` / `regimes` / `input_events` parquet |
| 03 | Performance | Trial düzeyi metrikler, metrik seti seçimi, katılımcı × koşul birimine toplama. Çıktı: `trial_metrics` / `participant_condition` parquet |
| 04 | Control mechanism | Action timing (Ludolph), variability, velocity stratification, açı bandı taraması. Çıktı: `state_events` / `timing_cells` parquet. I/CR/D/A dağılımı öncelik dışı bırakıldı |
| 05 | Learning | Pilotta işi varyans/güç tahmini; koşullar arası öğrenme karşılaştırması DEĞİL |
| 06 | Noise kararı | Friedman + Wilcoxon/Holm, lineer ve kuadratik trend kontrastı (SR testi), duyarlılık, aday sıralaması. Çıktı: `data/processed/karar/` |

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

## Notebook 03 kararları

**Karar metrik seti (NB06'ya giden):**

| Metrik | Yön | Not |
|---|---|---|
| `mae_angle_deg` | düşük iyi | RMS ile r=0.98, ikisinden biri |
| `stab_time_s` | yüksek iyi | kendi eşiğimiz, `performance.stab_angle_deg` = 30° |
| `falls_angle_per_trial` | düşük iyi | Park'ın Failed'iyla karşılaştırılabilir olan |
| `control_effort` | belirsiz | tie-breaker |
| `cart_rms_m` | belirsiz | tie-breaker |

Dışarıda: sIQR'lar, süre metrikleri (yukarıdaki iki bölüm), `falls_track_per_trial` (koşulla ilgisiz, dz'ler ±0.12 içinde; Park karşılaştırmasından zaten çıkıyor).

**Stabilizasyon süresi kendi eşiğimizle hesaplanıyor.** Unity'nin `within_bounds_time_s`'i failure limitini kullandığı için 600 trial'da ort. 19.97 s, sd 0.04 — tavana yapışık, koşulları ayırt etmiyor. |θ| ≤ 30° eşiğiyle ort. 18.22 s, sd 1.67.

**Düşüş sayımı üç kaynakta tutuyor:** sample düzeyi `fall_event` toplamı, sebebe göre ayrılmış toplam (açı 1.025 + ray 131) ve Unity'nin `fall_count`'u — 600 measurement trial'ın 600'ünde birebir aynı.

**Betimleyici sonuç:** bütün ana metriklerde aynı şekil — no_noise ile N1 yapışık, N2'den itibaren monoton bozulma. maPA'da N2/N3/N4 katılımcıların 11/12'sinde baseline'dan kötü (dz 0.96–1.18), N1'de fark yok (dz −0.03, 6/12). **U şekli yok.** Testler NB06'da.

## Notebook 04 kararları

Kod `src/timing.py`, eşikler `config.yaml` → `timing`, gerekçeler `Yontem/05_Action_Timing.md` §5. Çıktı `state_events.parquet` (91.165 olay) ve `timing_cells.parquet`.

**Ölçüt (action timing):** pole tamsayı açıyı **düşerken** geçtiği ana ortalanmış ±0.5 s'lik input segmentlerinin ortalaması; o eğrinin zero crossing'i action timing'dir. Negatif = predictive.

**Analiz birimi angle band:** merkez ± 2°, merkezler 5/10/15/20. Ana bant **10 ± 2**. Tek tamsayı açıda ortalama eğri bazen sıfırı birden fazla kesiyordu; bant tek geçişe indiriyor. Bantlar arası **değer** karşılaştırılmaz (geometri), sadece örüntü.

| Bulgu | Sayı |
|---|---|
| Havuz eğrisi zero crossing (bant 10) | −52.6 ms, bootstrap %95 CI −55.6…−49.5 |
| Amplitude / standart hata | 154× — %73.9 sıfır girdi endişesi boşa çıktı |
| Katılımcı × koşul hücresi | 60/60 dolu, 59'unda tek geçiş |
| Kişiler arası yayılım | 269 ms (−143 … +126) |
| Koşullar arası yayılım | **15 ms** (kişi içi sd 27.6 ms) |

- **Koşul etkisi yok.** Medyanla profil düz, açı bantları arasında işaret değiştiriyor. Action timing karar setine girmiyor, NB06'ya gitmiyor.
- **Öğrenme kayması sağlam değil.** Ortalamada −39 → −93 ms ama P007 + P012 çıkarılınca düzleşiyor, medyan zaten düz. Kompozisyon kontrolü (orta velocity stratum) geçiyor, kişi kontrolü geçmiyor.
- **Yavaş geçişlerde ölçüt tanımsız.** Ortalama eğri baştan sona pozitif kalıyor — hiç reversal yok, "zero crossing" düz eğrinin gürültüsü. `curve_stats` bunun için `reversal_ok` ve `guvenilir` (amplitude ≥ 10× SE) bayrakları üretiyor. Ludolph'ta görünmez çünkü o %20–80 dışını atıyor; bizim stratification kararımız görünür kıldı.
- **Action variability ayrı bilgi taşımıyor.** Gürültüyle düşüyor (N4 dz −0.77) ama amplitude'a bölününce kayboluyor (dz −0.27) — kuvvet küçülüyor, tutarlılık artmıyor.
- **P007 iki bağımsız ölçüde de aykırı:** tek reaktif kişi (+126 ms) ve NB02'de D oranı %15.2 (diğerleri ~%2).

## Notebook 06 sonucu: karar

Kod `src/decide.py`, gerekçeler `Yontem/06_Karar_Istatistigi.md`, sonuç metni `Pilot_Sonuc_Ozeti.md`. Analiz birimi katılımcı × koşul, n = 12, bütün testler within-subject ve non-parametrik.

**Stochastic resonance desteklenmiyor.** U şeklinin doğrudan testi kuadratik ortogonal kontrast; üç karar metriğinde de null.

| Metrik | Friedman p | Kendall W | Lineer p | **Kuadratik p** |
|---|---|---|---|---|
| `mae_angle_deg` | 0.0014 | 0.37 | 0.00049 (12/12 aynı yön) | **0.62** |
| `stab_time_s` | 0.021 | 0.24 | 0.0049 (10/12) | **0.57** |
| `falls_angle_per_trial` | 0.0051 | 0.31 | 0.00098 (11/12) | **0.58** |
| `control_effort` | 0.75 | 0.04 | 1.00 | 0.38 |
| `cart_rms_m` | 0.13 | 0.15 | 0.68 | 1.00 |

**N1 baseline'dan ayırt edilemiyor:** üç metrikte de p ≈ 0.90, dz ≤ 0.20, 6/12. N2/N3/N4 maPA'da Holm sonrası anlamlı (dz 0.96–1.18, 11/12); diğer iki metrikte Holm sonrası yalnız N4 kalıyor.

**Nüans:** grup ortalamasında üç metrikte de sayısal en iyi koşul N1 — tepe iç bir koşulda. Ama fark gürültünün içinde ve kuadratik null; bu U değil, no_noise ile N1'in ayırt edilemezliği. Composite'te kimsenin en iyisi N3/N4 değil (6 no_noise, 5 N1, 1 N2).

**Duyarlılık:** P011'in iki `paused` trial'ı çıkarılınca hiçbir p oynamıyor. Stabilizasyon eşiği 10°–45° taramasında her eşikte lineer anlamlı, hiçbirinde kuadratik anlamlı değil.

**Aday sıralaması:** 1) N1 (σ=0.02) — noise var ama performansı bozmuyor. 2) N2 (σ=0.05) — etkisi ölçülebilir en düşük seviye. N3/N4 eleniyor. **Sıra, ana deneyin tasarımına bağlı** (bkz. Açık sorular).

## Veride görülen sorunlar

Önem sırasına göre. 1 ve 8 gerçek veride doğrulandı, geri kalanı hâlâ "bakılacak" listesinde:

1. **randomizationSeed 12345'e sabitlenmiş.** Veriden doğrulandı (metadata'ya bakmadan, NB01 §7):

   - **Koşul sırası özdeş** — bütün katılımcılar aynı 50 trial'lık diziyi alıyor.
   - **noise_seed dizisi özdeş** — herkes aynı noise desenini görmüş.
   - **Başlangıç açıları da aynı listeden** — tek bir sabit açı dizisi var. P001–P007 hepsi ondan okuyor (hizalama %100). Giriş noktaları farklı: P001/P002/P004/P006 offset 0, P003 76, P007 89, P005 253. Offsetler oturum zincirini birebir doğruluyor — P002 tam 76 çekiliş yapmış ve P003 76'dan giriyor; P004 tam 253 yapmış ve P005 253'ten giriyor. Yani **uygulama katılımcılar arasında kapatılmadığında RNG akışı kaldığı yerden devam ediyor**, kapatılınca 0'a dönüyor.

     P008–P012 `check_angle_stream`'de ayrı gruplara düşüyor, ama bu "farklı seed" demek değil: metadata'da hepsinde seed 12345 ve aynı Unity build var, ayrıca hiçbiri offset 0'da değil (olsaydı P001'in ilk 152 çekilişiyle eşleşirlerdi). Bitişik ama örtüşmeyen dilimler eşleştirilemediği için algoritma zinciri göremiyor. P007 89+479 = 568'de bitiyor; P008–P012 sırayla 568'den itibaren devam ediyorsa gözlenen tablo aynen çıkar. Yani **27 Ağustos öğleden sonra uygulama hiç kapatılmamış** görünüyor — kanıtlanamıyor ama tüm alternatifler (0'a dönüş) elendi.

   Açıların dışarıdan bağımsız görünmesinin sebebi: imleç davranışa göre ilerliyor, her düşüş bir çekiliş tüketiyor. Farklı düşüş sayısı → aynı listenin farklı yerleri. İz: P001'in T002'de aldığı −4.0469'u P002 T005'te alıyor.

   **Pilot kararına (NB06) etkisi ölçüldü, 12 katılımcıda 7'dekinden de küçük:** başlangıç |θ| koşullar arasında dengeli (ortalamalar 3.43–3.78°, yayılım 0.35°, trial içi sd 2.11°) ve sonuçla korelasyonu zayıf (fall_count ile r=+0.066; 7 katılımcıda +0.14 idi). Yön de lehimize: en zor başlangıçlar (ort. 3.78°) **no_noise** koşulunda, yani yanlılık "noise performansı bozuyor" bulgusunu şişirmiyor, aksine ona karşı çalışıyor.

   Yanlılığın sönmeme riski P001–P007 için geçerliydi (hepsi aynı açı dizisinden okuyordu). P008–P012 dizinin farklı bir yerinden okuduğu için katılımcılar arası hizalama kısmen kırıldı. Yine de koşullar birbirine çok yakın çıkarsa (tie-breaker senaryosu) akılda tutulmalı. Düzeltme için bkz. T₀ bölümü — Ludolph'un T/T₀'ı aynen değil, episode düzeyinde uygulanmalı.

   Koşul sırası tarafında ise **her tur içinde yeniden karılıyor**, sabit olan 50 trial'lık dizinin tamamı. Her koşulun ortalama `trial_order`'ı 24.6–26.5 (1–50 aralığında) — öğrenme/yorgunluk koşulla karışmamış, asıl korkulan confound yok. Tur içi pozisyon dağılımı tümsekli ama tur sayısı az (hücre başına beklenen 2), bu büyüklükte sapma tek çekilişte şansa girer; tablo betimleyicidir, kusur testi değil.

   **Ekibe tek istek:** seed'i katılımcı id'sinden türetin ve her oturumda RNG'yi yeniden tohumlayın. Bu üç sorunu birden çözer. NB01'de `shared_condition_order` / `shared_randomization_seed` WARN veriyor. `check_angle_stream` `src/qc.py`'de var ama NB01 §7'de **çağrılmıyor** — akış tablosu istenirse elle çalıştırılmalı.
2. **Reset satırlarında applied_force_n 0'a zorlanıyor** ama input_applied son değerinde kalıyor. Action timing analizi için sorun: sahte zero-crossing'ler üretiyor.
3. **Reset'te hızlar tam sıfırlanmıyor** — Ludolph ikisinin de sıfır olmasını istiyor. Başlangıç koşulları karşılaştırılabilir olmuyor.
4. **`valid_trial` neredeyse hep 1.** 636 trial'ın 634'ünde 1; sadece P011 T030 ve T034'te 0 ve `invalid_reason = "paused"`. Yani mekanizma çalışıyor ama tek durum için. Asıl açık bizim tarafımızda: `flag_trials` bu kolona bakmıyor, o iki trial `qc_pass` ve maskeye giriyor. İncelendi, veri normal (1200 tam sample, focus kaybı yok, davranış olağan); 600'de 2, düşük etkili — ama kural eklenmeli.
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

Band 0.02 seçildi çünkü örneklerin **%73.9'u tam sıfır**, sıfır olmayan en küçük değer 0.0153 — deadzone zaten uygulanmış. `input_raw` ile `input_applied` birebir aynı (max fark 0.000000), iki kolon gereksiz.

**Girdi cihazı `Xbox Controller`** (metadata `input_device`), yani analog kol — klavye değil. Sıfır olmayan 136 farklı büyüklük, ~0.0098 adımlarla nicelenmiş; doyuma giden örnekler sıfır olmayanların ~%5'i. Girdi dereceli. %73.9 sıfır, yaylı kolun merkeze dönmesi. Bu Ludolph'un sigmoid varsayımı için iyi haber.

### Mevcut dağılım (12 katılımcı, active örnekler)

```
I  74.5%    CR 22.5%    D 2.7%    A 0.30%    X 0.01%
kuadran: fall 63.5%, safe 36.5%
```

**A çok seyrek (%0.30).** Park'ta anlamlı bir orandı. Muhtemel sebep: zamanın %63.5'i fall kuadranında geçiyor, katılımcılar düşüşle boğuşuyor, dikey civarında ince ayar yapmıyor. Bulgu, bug değil. NB04'te karara bağlanacaktı ama koşula göre dağılım öncelik dışı bırakıldı (2026-08-31); karar hâlâ açık.

Rejim başına profil Park'ın niteliksel örüntüsüyle uyuşuyor: Failed'da D en yüksek (%26.5) ve CR en düşük (%19.0); Safe'te CR en yüksek (%38.8).

## Düşüş sebebi: iki tane var

`fall_event` iki farklı sebeple tetikleniyor ve **ayırt edilmeli**:

| Sebep | n | Düşüş anında ort. abs(θ) |
|---|---|---|
| `angle` — pole ±60°'ye vardı | 1.241 | 61.0° |
| `track` — cart ±5 m ray sınırına çarptı | 140 | 21.3° |

Örtüşme sıfır, açıklanamayan sıfır. Ray kaynaklı düşüşlerin biri 0.27°'de olmuş — pole dimdikken cart raydan çıkmış. 140'ının **42'si safe kuadranında**, yani pole dikeye dönerken.

Park'ta bunun karşılığı yok. O yüzden `Failed` sadece açı kaynaklı düşüşler için kullanılıyor (Park'la karşılaştırılabilir olan bu), ray kaybına ayrı `TrackLoss` etiketi veriliyor ve Park karşılaştırmalarından çıkarılıyor.

Rejim dağılımı: Safe %45.4, Saved %45.2, Failed %6.6, censored %2.1, TrackLoss %0.7.



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

**Ampirik doğrulama (NB02 §2b).** Katılımcının hiç girdi vermediği ve açı limitiyle biten episode'lar tanım gereği serbest düşüştür — süreleri T₀'a eşit olmalı. Böyle 11 episode var ve on birinde de `duration/T₀ = 1.0000`, standart sapma sıfır. Fizik modeli, RK4 adımı, T₀ hesabı ve episode segmentasyonu zincirinin tamamı tek testte doğrulanmış oluyor. Kod: `build.validate_T0_freefall`.

### Ludolph'un T/T₀'ı aynen aktarılamaz

Ludolph'ta trial düşünce **biter**, o yüzden T değişken ve T/T₀ anlamlı. Bu pilotta trial sabit 20 s, düşüş olunca reset olup devam ediyor — T hep ≈20 s, dolayısıyla T/T₀ = 20/T₀ oluyor, yani saf θ₀ fonksiyonu. Ölçülen: `corr(|θ₀|, trial T/T₀) = +0.972`. Performans ölçmüyor.

Doğru karşılık **episode düzeyi**: her episode kendi başlangıç açısından başlar (trial başı ya da düşüş sonrası restart), süresi düşüşe ya da trial sonuna kadardır.

| Ölçüt | corr(&#124;θ₀&#124;, ölçüt) |
|---|---|
| Trial düzeyi T/T₀ | +0.972 |
| Episode düzeyi T_ep/T₀ | +0.128 |
| Episode süresi (ham) | −0.078 |

**NB03 kararı: bağımsız bir süre metriği kullanılmıyor, T/T₀ reddedildi.** Üç aday da ayrı sebeplerle elendi:

- `mean_episode_s` düşüş sayısının deterministik dönüşümü. Trial sabit 20 s ve episode sayısı = düşüş + 1 olduğu için ortalama episode süresi tam olarak 20/(düşüş+1); `corr = 1.0000`. Yeni bilgi taşımıyor.
- T₀'a bölmek düzeltmiyor, **fazla düzeltiyor**. Episode düzeyinde ham sürenin θ₀ korelasyonu −0.075 iken bölünmüş hali +0.141; katılımcı × koşul düzeyinde 0.229'a karşı **0.645**. Ludolph'un normalizasyonu bu tasarımda kirliliği artırıyor.
- Sansürsüz sürümler hayatta kalma yanlılığı taşıyor. Sansürlü episode = "trial sonuna kadar düşmedi", yani en iyi denemeler. Atılınca no_noise ortalaması 12.10 s → 7.38 s'ye düşüp en **düşük** koşul oluyor, N4 etkisi işaret değiştiriyor (dz −1.03 → +0.25).

Ludolph'un süre ölçütünü düzgün kullanmak sağ sansürü ele alan survival analizi ister (1.756 measurement episode'un 600'ü sansürlü). Gerekirse NB05. Pilot kararı için `falls_angle_per_trial` aynı bilgiyi taşıyor.

## Ek metrikler ve sinyal işleme

- **control effort** = RMS_u = sqrt(mean(u²)), u = input_applied
- **sIQR_theta** = (Q75(θ) − Q25(θ)) / 2
- **sIQR_omega** = aynısı angular velocity için
- sIQR'ın gerekçesi: iki katılımcının maPA'sı aynı olabilir ama biri çoğunlukla ±5° durup ara sıra ±50°'ye giderken diğeri sürekli ±15°'te olabilir. RMS birinciyi orantısız cezalandırır. sIQR_omega açı büyüklüğünden bağımsız olarak hareketin ne kadar dalgalı olduğunu ölçer.
- **NB03'te kontrol edildi, ikisi de karar setine girmiyor.** Kriter: katılımcı içi merkezlenmiş artığın koşul profilinde lineer kontrastın ne kadarı hayatta kalıyor. sIQR_theta RMS'in neredeyse kopyası (r=0.85), trendin %9'u kalıyor. sIQR_omega ayrı bir konstrukt (r=0.60 — "açı büyüklüğünden bağımsız salınım" beklentisi doğru) ama trendin %79'unu yine RMS açıklıyor, kalan %21 ters işaretli. maPA da RMS'in kopyası (r=0.98, trendin %6'sı) — ikisinden sadece biri raporlanmalı. Üçü de `trial_metrics.parquet`'te duruyor; sIQR_omega hâlâ betimleyici olarak kullanılabilir (NB04'te kullanılmadı).
- Gerektiğinde filtre: action onset tespiti, force derivative, jerk, küçük salınımlar (scipy.signal).

## Belgelendirme

Kod ve sayılar burada, **gerekçeler `Documentation/` altında.** Bir metrik bir karara giriyorsa `Documentation/Yontem/` altında kaydı olur: tanım, kod referansı, hangi seçenekler vardı ve neden bu seçildi, kanıt, neyi beslediği. Literatürden aynen alınmayan her şey ayrıca işaretlenir.

| Belge | Ne için |
|---|---|
| `Documentation/Yontem/` | Hesap başına bir kayıt: 01 veri işleme, 02 fizik/T₀, 03 durum-aksiyon-episode, 04 performans metrikleri, 05 action timing, 06 karar istatistiği |
| `Documentation/Analiz_Gunlugu.md` | Tarihli günlük, yeni giriş üste. Ne zaman ne karara bağlandı |
| `Documentation/Pilot_Sonuc_Ozeti.md` | Pilotun bulgusu (sunumun metin karşılığı). Klasördeki pptx/docx 26 Ağustos tarihli, sayıları geçersiz |
| `Documentation/Veri_Kayit_Istekleri.md` | Ekibe giden kayıt formatı istekleri, rev. 2 (12 katılımcı) |

Yeni bir analiz kararı verildiğinde günlüğe bir giriş, ilgili yöntem kaydına bir güncelleme gider. CLAUDE.md bunların özeti değil, tamamlayıcısı — burada güncel sayılar ve çalışma bağlamı durur.

## Çalışma kuralları

- Kod yazmadan önce sor. Ne yazacağını anlat, onay al, sonra yaz.
- Amaç dışı şeylerin peşine düşme. Bir veri kalitesi detayı noise seviyesi kararını değiştirmiyorsa uğraşma. Önemli olduğunu düşünüyorsan önce ne kadar önemli olduğunu söyle.
- Her şeyi eşit acil gösteren düz liste verme, etkiye göre sırala.
- Eşikler config.yaml'da, koda gömülmez.
- Mantık src/ altında modül olur, notebook'lar ince kalır.
- Kısa konuş. Rapor veya slayt formatı değil, düz anlat.
- Türkçe, teknik terimler İngilizce.

## Açık sorular

- **Ana deney tek noise seviyesi + no_noise kontrol grubu mu, yoksa herkes aynı noise'u mu alıyor?** Ekibe soruldu, cevap gelmedi. NB06 çalıştı ama **aday sırası bu cevaba bağlı**: kontrol grubu varsa N2 (N1–baseline farkı bu pilotta saptanamayacak kadar küçük, muhtemelen null çıkar), herkes aynı noise'u alıyorsa N1 (noise öğrenmeyi ölçmeyi engellememeli).
- Pilot anlık performansa bakıyor, ana deney öğrenmeyi ölçecek. Ludolph'un bulgusu bu ikisinin ayrışabileceği yönünde — o yüzden rapora tek seviye değil sıralı iki aday yazıldı.
- **Güç analizi yok.** N1'in null çıkması "fark yok" değil "bu örneklemle saptanamadı" demek. NB05'in işi.
- A sınıfı (%0.30) istatistiksel olarak kullanılabilir mi — NB04'te öncelik dışı bırakıldı.

## Veri kaynağı ve git

Kaynak: Google Drive klasörü `Pendulum_Data`, id `1iDMZt3iUN-mHaemXXI_qNA9GkYUMf5t6`
drive link: https://drive.google.com/drive/folders/1iDMZt3iUN-mHaemXXI_qNA9GkYUMf5t6

Yapı: `Pendulum_Data/<participant>/<session>/` ve içinde üç dosya.

Çekme: NB01'in "0. Drive'dan veri çek" hücresi, `sync_data(folder_id, RAW_DIR)`. Kimlik doğrulama yok — klasör herkese açık. Kodu çalıştıran herkes aynı veriyi kendi diskine indirebiliyor, o yüzden git'te tutmaya gerek yok.
