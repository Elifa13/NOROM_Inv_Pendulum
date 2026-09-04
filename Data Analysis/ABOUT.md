# Data Analysis

Pilot verisinin analiz zinciri. Mantık `src/` altında modül olur,
notebook'lar ince kalır. Eşikler `config.yaml`'da, koda gömülmez.

## Yapı

```
config.yaml       bütün eşikler ve parametreler + datasets bloğu
src/              analiz mantığı (veri setinden bağımsız)
Notebooks/        pilot1 zinciri
Notebooks/pilot2/ pilot2 zinciri, tek fark ilk hücredeki DATASET
data/
  pilot1/         12 katılımcı, noise σ 0 .02 .05 .08 .25
  pilot2/          9 katılımcı, noise σ 0 .005 .010 .015 .020
    raw/          Drive'dan inen ham veri (git'te tutulmaz)
    interim/      ara çıktılar, parquet (git'te tutulmaz)
    processed/    figürler ve rapor çıktıları
```

**İki veri seti birbirine karışmaz.** Katılımcı id'leri iki sette de P001…
diye gidiyor ama aynı kişiler değil; koşul etiketleri de aynı ama sigmalar
farklı. Ayrım klasör düzeyinde: aktif set notebook'un ilk hücresindeki
`DATASET` değişkeni, yolları `src/dataset.load_config` çözüyor.
`dataset.dirs` interim'e bir `.dataset` damgası bırakıyor — yanlış set
yanlış klasöre yazmaya kalkarsa hata verir.

## Modüller

| Dosya | İş |
|---|---|
| `dataset.py` | Veri seti seçimi, yol çözümleme, karışma koruması |
| `drive_sync.py` | Drive'dan veri çekme; copy semantiği, var olanı atlar. Yol tam üç parça olmalı — iç içe klasör (başka veri seti) indirilmez, atlananlar raporlanır |
| `loader.py` | Oturumları bulma, üç dosyayı okuma, iki tablo üretme |
| `qc.py` | Yapısal bütünlük, zaman, sinyal, trial bayrakları, analiz maskesi, randomizasyon |
| `physics.py` | Cart-pole modeli, doğrulaması, T₀ |
| `build.py` | Episode ve regime run segmentasyonu, state, action sınıfları, girdi olayı tespiti (`input_events`) |
| `performance.py` | Trial ve katılımcı × koşul düzeyi metrikler, metrik seti seçimi |
| `timing.py` | Ludolph action timing: durum olayları (`state_events`), segment çıkarma, velocity stratification, zero crossing |
| `decide.py` | NB06 karar istatistiği: Friedman, Wilcoxon/Holm, trend kontrastları, duyarlılık |
| `presentation.py` | **İzole.** Sunum notebook'u için; zincirin geri kalanı import etmez |

## Veri katmanları

```
Raw Sample (FixedUpdate satırı)
  → Clean Sample (QC'den geçmiş, maskeli)
  → Girdi olayı (onset / offset / reversal)  |  Durum olayı (açı geçişi)
  → Regime run (Safe / Saved / Failed / TrackLoss)
  → Episode (reset'ten reset'e)
  → Trial
  → Participant × Condition   ← analiz birimi
```

Episode ve regime run **aynı şey değil** — ilki Ludolph'un süre analizine,
ikincisi Park'ın rejim sınıflandırmasına hizmet ediyor. Ayrıntı:
`../Documentation/Yontem/03_Durum_Aksiyon_Episode.md`.

## Yöntem kayıtları

Her hesabın tanımı, gerekçesi ve kanıtı `../Documentation/Yontem/` altında.
Kod okumadan önce oraya bakmak genellikle daha hızlı.
