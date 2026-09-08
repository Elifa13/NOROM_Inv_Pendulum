# 01 — Veri işleme, QC ve analiz maskesi

**Notebook:** `Data Analysis/Notebooks/01_load_qc.ipynb`
**Kod:** `src/drive_sync.py`, `src/loader.py`, `src/qc.py`
**Çıktı:** `data/<dataset>/interim/samples_clean.parquet`, `.../trials_clean.parquet`
**Son çalıştırma:** 2026-08-27, 12 katılımcı

---

## 1. Kaynak ve çekme

Google Drive klasörü `Pendulum_Data`, id `1iDMZt3iUN-mHaemXXI_qNA9GkYUMf5t6`.
Klasör "bağlantıya sahip herkes" olarak paylaşıldığı için kimlik doğrulama
yok — API anahtarı, OAuth, `client_secrets.json`, `rclone config` hiçbiri
gerekmiyor.

`sync_data(folder_id, RAW_DIR)` `gdown` ile klasörü listeler ve sadece
beklenen üç dosya tipini indirir. **Sync değil, copy semantiği:** var olan
dosya tekrar indirilmez, yerelde olup Drive'da olmayan hiçbir şey silinmez.
Veri repoya commit edilmez; kodu çalıştıran herkes aynı veriyi kendi diskine
indirebildiği için git'te tutmanın anlamı yok.

Klasör yapısı `<kok>/<participant_id>/<session_id>/` ve içinde üç
dosya: `<pid>_<sid>_metadata.json`, `_timeseries.csv`, `_trial_summary.csv`.
Yerel hedef `Data Analysis/data/<dataset>/raw/` (aktif set için bkz. CLAUDE.md "Veri setleri").

**Yol tam üç parça olmalı** (2026-09-04'te eklendi). gdown yolları istenen
klasöre göre veriyor; daha derin bir yol, içeriye konmuş **başka bir veri
seti** demek. Eskiden son üç parça alınıyordu ve pilot2'nin `DataV2/` alt
klasörü pilot1 çekilirken pilot1'in klasörüne iniyordu — katılımcı id'leri
çakıştığı için sessizce karışıyordu. Artık `P\d+/S\d{8}_\d{6}/<pid>_<sid>_*`
kalıbına uymayan girdi indirilmiyor ve atlananlar sayısıyla birlikte
yazdırılıyor. Pilot1 çekilirken 28 girdinin atlandığını söyleyen uyarı
beklenen davranıştır.

**Durum:** pilot1 12 katılımcı × 3 dosya = 36 dosya (26–27 Ağustos 2026);
pilot2 9 katılımcı × 3 dosya = 27 dosya (2–3 Eylül 2026).

## 2. Yükleme

`loader.load_all` oturumları bulur, üç dosyayı okur ve iki tablo üretir:
sample düzeyi (timeseries) ve trial düzeyi (trial_summary), metadata ayrı
bir sözlükte.

**Karar — birden fazla oturum klasörü olursa.** En çok measurement trial
içeren oturum alınır, diğerleri raporda "yarım" olarak görünür.
Birleştirilmez: uygulama yeniden başlayınca aynı `condition_order` ile
trial 1'den başlıyor, yani trial'lar tekrar ediyor ve iki oturumu uç uca
eklemek aynı koşulu iki kez saymak olur.

## 3. QC kontrolleri

`src/qc.py` içinde altı grup. Hiçbiri veriyi değiştirmez, hepsi rapor üretir.

### 3.1 Yapısal bütünlük (`check_structural_integrity`)

Dosya varlığı, trial sayıları (3 practice + 50 measurement bekleniyor),
koşul dengesi (her turda 5 koşul × 1), zorunlu metadata alanları.

Bu kontrolün ürettiği iki kalıcı WARN:

- `shared_condition_order` — bütün katılımcılar aynı 50 trial'lık koşul
  dizisini alıyor
- `shared_randomization_seed` — metadata'da hepsinde `12345`
- `config_participant_id` — `config.participantId` hiç güncellenmiyor,
  12 katılımcının metadata'sında da "P001" yazıyor. `participant_id` alanı
  doğru, sadece `config` bloğundaki kopya yanlış.

Ayrıntı ve etki ölçümü için bkz. [randomizasyon bölümü](#7-randomizasyon-doğrulaması).

### 3.2 Zaman ve örnekleme (`check_timing`)

`dt` ile `fixed_delta_time_s` uyumu (tolerans `qc.dt_tolerance` = 0.001),
zamanda geri gitme, boşluk, `sample_index` atlaması, duplicate, NaN, açı
aralığının −180°..+180° içinde olması.

### 3.3 Sinyal akıl sağlığı (`check_signals`)

- Hızlar pozisyonun türeviyle tutuyor mu (uyarı eşiği `qc.velocity_correlation_warn` = 0.99)
- `applied_force_n` = `input_applied` × `max_force_n` mi
- `fall_event` sadece düşüşün ilk adımında mı işaretli
- `phase` ile `is_resetting` tutarlı mı

**Karar — türev kontrolü kesintisiz parçalarda yapılır.** Trial içinde düşüş
olunca 1 saniyelik reset bloğu giriyor ve pole yeni bir başlangıç açısıyla
devam ediyor. `phase == "active"` satırlarını uç uca eklemek reset
sınırlarında sahte sıçrama üretir ve korelasyonu düşürür. `_active_segments`
kesintisiz active parçaları ayırır, korelasyon her parçada ayrı hesaplanır.

### 3.4 Trial geçerliliği (`flag_trials`)

**Unity'nin `valid_trial` kolonuna güvenilmiyor**, kendi `qc_pass` /
`qc_flags` bayrağımız üretiliyor.

Şu an uygulanan tek kural **ölü input**: bir trial boyunca
`max(|input_raw|) == 0` ise `dead_input` bayrağı. Eşik
`qc.dead_input_threshold` = 0.0.

`qc.min_fps` ve `qc.low_activity_threshold` config'te `null`. Kod null ise o
kuralı atlar — gerçek veri gelene kadar eşik uydurmamak için bilinçli
bırakıldı.

**Karar — QC'den düşen trial sadece kendisi çıkar, oturum düşmez.** Rapor
eşik üstünde uyarır.

**Mevcut veride sonuç:** 636 trial'ın hiçbiri bayraklanmadı, `qc_pass`
636/636. Ölü input trial'ı kalmadı (P001/P002 döneminde 5 tane vardı, o veri
silindi).

### 3.5 Sample maskesi (`add_analysis_mask`)

```
analysis_include = (phase == "active") & (practice == 0) & qc_pass & (window_focused == 1)
```

`is_resetting == 0` koşulu gereksiz — `phase == "active"` ile birebir aynı
sonucu veriyor.

**Mevcut veride:** 720.000 sample = 600 measurement trial × tam 1200 sample.
Hiç focus kaybı yok, hiç QC düşüşü yok. Bu, oran hesaplarında **paydanın
sabit olduğu** anlamına geliyor: çok düşen bir katılımcı reset sayesinde
yapay olarak iyi görünmüyor, çünkü reset frameleri zaten maskenin dışında.

### 3.6 Format regresyon takibi (`check_format_regression`)

`Veri_Kayit_Istekleri.md`'de istenen alanların gelip gelmediğini kontrol
eder. Liste `config.metadata_requested_fields` altında.

**Durum:** istenen 24 alanın 24'ü hâlâ eksik.

## 4. Randomizasyon doğrulaması

`check_randomization` metadata'nın `condition_order` iddiasını trial_summary
ile karşılaştırır ve katılımcılar arası özdeşliği **veriden** ölçer.

Sonuçlar ve pilot kararına etkisi `CLAUDE.md` → "Veride görülen sorunlar" §1.
Özet: koşul sırası ve `noise_seed` dizisi 12 katılımcıda birebir aynı;
başlangıç açıları tek bir sabit RNG dizisinden okunuyor.

`check_angle_stream` bu akışı katılımcı çiftlerinde hizalayarak her
katılımcıya ortak listede bir giriş noktası atar. **Bu fonksiyon NB01'de
çağrılmıyor** — `src/qc.py`'de duruyor, akış tablosu istendiğinde elle
çalıştırılıyor. Eşikler `qc.angle_stream_*` altında.

Fonksiyonun bilinen sınırı: bitişik ama örtüşmeyen dilimleri
eşleştiremiyor. P008–P012 bu yüzden ayrı gruplara düşüyor; bu "farklı seed"
demek değil (bkz. CLAUDE.md §1).

## 5. Bilinen açıklar

Önem sırasına göre.

1. **`valid_trial == 0` olan trial'lar maskeye giriyor.** P011'in T030 ve
   T034 trial'ları `invalid_reason = "paused"` ile işaretli ama bizim
   `flag_trials`'ımız bu kolona bakmıyor, ikisi de `qc_pass`. İncelendi:
   ikisinde de 1200 tam active sample var, focus kaybı yok, davranış normal
   (maPA 10.1° ve 6.0°, birer düşüş). 600 trial'da 2 tanesi, düşük etkili.
   Yine de kural eklenmeli: `invalid_reason` doluysa en azından bayrak.
2. **fps eşiği yok.** 54 trial'da `min_fps < 55`, 47'sinde `< 45`, en düşük
   29.1. `mean_fps` her trial'da ~60. Anlık düşüşler sample kaybına yol
   açmıyor (her trial 1200 sample tam) çünkü örnekleme FixedUpdate'te,
   render'dan bağımsız. Yine de görsel noise'un algılanmasıyla ilgili bir
   deneyde render hızı doğrudan bağımsız değişkeni etkiliyor — eşik
   konulmalı mı, karara bağlanmadı.
3. **Sample düzeyinde frame timing yok** — düşük öncelikli.
