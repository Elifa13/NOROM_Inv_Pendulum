# CLAUDE.md

Bu dosya yönlendiricidir, bilgi deposu değil. Burada yalnızca çalışmalar üstü
olan şeyler durur: düzenek, veri formatı, repo haritası, çalışma kuralları.
Bir sayı ya da bulgu tek bir çalışmaya aitse burada değil, o çalışmanın
klasöründedir. Kural aşağıda, "Nereye ne yazılır" başlığında.

## Proje

Cart-pole (inverted pendulum) dengeleme görevinde motor öğrenme ve içsel model
çalışılıyor. Düzenek Ludolph 2017'nin aynısı, virtual reality yok, ekran ve
analog kol var.

**Aktif çalışma: GAP (Gravity Adaptation and Prediction).** Yerçekimi kademeli
olarak 1.0'dan 3.5 m/s²'ye çıkarken kişinin kontrol politikası nasıl değişiyor,
ve bu değişim occlusion tabanlı bir algısal testte görünüyor mu. İki grup:
gradual gravity ve constant gravity (kontrol). Sekiz aşamalı seans. Tasarımın
tamamı `Documentation/GAP/00_Tasarim.md`.

**Kapanmış çalışma: görsel noise / stochastic resonance.** İki pilot, 21
katılımcı, dokuz noise seviyesi. Ters-U bulunamadı, hipotez desteklenmedi,
çalışma kapatıldı. Özet ve devredilen kararlar `Documentation/Pilot_Noise/`.

## Rolüm

Veriyi ben analiz ediyorum, deneyi ben yapmıyorum, tasarımı değiştiremem.
Kayıt tarafına sadece "şu alanı da kaydedin" diyebiliyorum. Yani "şunu da
ölçelim" önerisi ancak mevcut ya da istenen kolonlardan türetilebiliyorsa
uygulanabilir.

## Repo haritası

| Yer | Ne var |
|---|---|
| `Documentation/Duzenek/` | Düzeneğe ait yöntem kayıtları. Her çalışmada geçerli: veri işleme ve QC, fizik modeli ve T₀, state/action/episode tanımları, performans metrikleri, action timing |
| `Documentation/GAP/` | Aktif çalışma: tasarım, kayıt istekleri, modelleme planı |
| `Documentation/Pilot_Noise/` | Kapanmış çalışma: iki pilot özeti, karar istatistiği, o dönemin kayıt istekleri, `arsiv/` altında eski Office belgeleri |
| `Documentation/Analiz_Gunlugu.md` | Tarihli günlük, yeni giriş üste. Ne zaman ne karara bağlandı |
| `Data Analysis/src/` | Analiz mantığı. Notebook'lar ince kalır, mantık burada |
| `Data Analysis/Notebooks/pilot_noise/` | Kapanmış çalışmanın iki zinciri, dondurulmuş |
| `Data Analysis/data/` | Ham ve türetilmiş veri. Git'te tutulmaz, kaynak Google Drive |
| `Literature/` | Makaleler ve kaynak kaydı |
| `Unity/` | Deneyi çalıştıran proje. Şu an boş, proje deney ekibinde |

## Düzenek

Fizik parametreleri Ludolph 2017 ile aynı. Motor değişmiyor, çalışmadan
çalışmaya değişen tek şey yerçekimi ve seans yapısı.

| Parametre | Değer |
|---|---|
| Cart kütlesi | 0.40 kg |
| Pole kütlesi | 0.08 kg |
| Pole uzunluğu | 1.00 m (dinamik denklemine yarım uzunluk, 0.5 m girer) |
| Kuvvet sınırı | ±4 N |
| Ray sınırı | ±5 m |
| Açı sınırı (fall) | ±60° |
| Başlangıç açısı | U(−7.5°, +7.5°) |
| İntegrasyon | RK4, Δt = 1/60 s |
| Örnekleme | FixedUpdate, 60 Hz |
| Yerçekimi | çalışmaya göre değişir |

Model veriden doğrulandı, gözlenen açısal ivmeyle korelasyon 0.989–0.997.
Türetme, doğrulama ve T₀ hesabı `Documentation/Duzenek/02_Fizik_ve_T0.md`.

## Veri

Kaynak Google Drive, klasör bağlantıya sahip herkese açık, kimlik doğrulama
yok. `src/drive_sync.py` `gdown` ile çeker, var olanı tekrar indirmez, yerelde
olup uzakta olmayanı silmez. Veri repoya commit edilmez.

Klasör yapısı `<participant_id>/<session_id>/` ve içinde üç dosya:
`metadata.json` (oturumda bir kez), `timeseries.csv` (her FixedUpdate'te bir
satır), `trial_summary.csv` (trial sonunda tek satır). Kolon listeleri her
çalışmanın kayıt istekleri belgesinde.

Veri katmanları:

```
Raw Sample → Clean Sample (QC'den geçmiş, maskeli)
  → Girdi olayı (onset / offset / reversal)  |  Durum olayı (açı geçişi)
  → Regime run (Safe / Saved / Failed / TrackLoss)
  → Episode (reset'ten reset'e)
  → Trial
  → Analiz birimi (çalışmaya göre: katılımcı × koşul, katılımcı × gravity step)
```

Episode ve regime run aynı şey değil. İlki Ludolph'un süre analizine, ikincisi
Park'ın rejim sınıflandırmasına hizmet ediyor. Ayrıntı
`Documentation/Duzenek/03_Durum_Aksiyon_Episode.md`.

### Veri setleri

Setler hiçbir aşamada birleştirilmez, ayrım klasör düzeyinde. Katılımcı
id'leri her sette P001… diye gidiyor ama aynı kişiler değil.

| Set | Çalışma | Durum |
|---|---|---|
| `pilot1` | noise | 12 katılımcı, Ağustos 2026, kapandı |
| `pilot2` | noise | 9 katılımcı, Eylül 2026, kapandı |
| `gap` | GAP | henüz veri yok |

Aktif set notebook'un ilk hücresindeki `DATASET` değişkeni. Yolları
`src/dataset.load_config` çözer, `dataset.dirs` interim'e bir `.dataset`
damgası bırakır, yanlış set yanlış klasöre yazmaya kalkarsa hata verir.

### Bilinen kayıt davranışları

Analizi etkileyen ve ekibe iletilmiş olanlar: reset satırlarında
`applied_force_n` sıfıra zorlanıyor ama `input_applied` son değerinde kalıyor
(sahte zero-crossing üretir), reset'te hızlar sıfırlanmıyor, `valid_trial`
kolonuna güvenilmez, seed pilot1'de sabitti pilot2'de düzeldi. Ayrıntı
`Unity/ABOUT.md` ve `Documentation/Pilot_Noise/Kayit_Istekleri.md`.

## Nereye ne yazılır

Bu reponun daha önce bozulma sebebi buydu, o yüzden kural açık:

- Bir hesap her çalışmada aynı şekilde yapılıyorsa kaydı `Documentation/Duzenek/`
  altına girer. Her kayıtta tanım, kod referansı, hangi seçenekler vardı ve
  neden bu seçildi, kanıt, neyi beslediği bulunur.
- Bir sayı, bulgu ya da karar tek bir çalışmaya aitse o çalışmanın klasörüne
  girer, buraya değil.
- Yeni bir analiz kararı verildiğinde `Documentation/Analiz_Gunlugu.md`'ye bir
  giriş, ilgili yöntem kaydına bir güncelleme gider.
- Literatürden aynen alınmayan her şey işaretlenir: neden aynen alınamadı,
  yerine ne kondu.

## Çalışma kuralları

- Kod yazmadan önce sor. Ne yazacağını anlat, onay al, sonra yaz.
- Amaç dışı şeylerin peşine düşme. Bir veri kalitesi detayı eldeki kararı
  değiştirmiyorsa uğraşma. Önemli olduğunu düşünüyorsan önce ne kadar önemli
  olduğunu söyle.
- Her şeyi eşit acil gösteren düz liste verme, etkiye göre sırala.
- Eşikler `config.yaml`'da, koda gömülmez.
- Mantık `src/` altında modül olur, notebook'lar ince kalır.
- Kısa konuş. Rapor veya slayt formatı değil, düz anlat.
- Türkçe yaz, teknik terimleri İngilizce bırak.
