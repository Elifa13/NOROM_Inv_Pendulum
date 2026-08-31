# Data Analysis

Pilot verisinin analiz zinciri. Mantık `src/` altında modül olur,
notebook'lar ince kalır. Eşikler `config.yaml`'da, koda gömülmez.

## Yapı

```
config.yaml     bütün eşikler ve parametreler
src/            analiz mantığı
Notebooks/      ince notebook'lar, zincir sırasıyla
data/
  raw/          Drive'dan inen ham veri (git'te tutulmaz)
  interim/      ara çıktılar, parquet (git'te tutulmaz)
  processed/    figürler ve rapor çıktıları
```

## Modüller

| Dosya | İş |
|---|---|
| `drive_sync.py` | Drive'dan veri çekme; copy semantiği, var olanı atlar |
| `loader.py` | Oturumları bulma, üç dosyayı okuma, iki tablo üretme |
| `qc.py` | Yapısal bütünlük, zaman, sinyal, trial bayrakları, analiz maskesi, randomizasyon |
| `physics.py` | Cart-pole modeli, doğrulaması, T₀ |
| `build.py` | Episode ve regime run segmentasyonu, state, action sınıfları, girdi olayı tespiti (`input_events`) |
| `performance.py` | Trial ve katılımcı × koşul düzeyi metrikler, metrik seti seçimi |
| `timing.py` | Ludolph action timing: durum olayları (`state_events`), segment çıkarma, hız tabakalama, sıfır geçişi |
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
