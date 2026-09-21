# Yöntem kayıtları

Bu klasör "ne hesapladık ve nasıl hesapladık" sorusunun cevabını tutar. Amaç,
aylar sonra bir sayıya bakıldığında onun nereden geldiğinin, hangi kararla
öyle hesaplandığının ve hangi sonucu beslediğinin yazılı olması.

## Kural

Bir metrik bir karara giriyorsa buraya girer. Her kaydın içinde şunlar olmalı:

1. **Tanım** — formül veya prosedür, belirsizlik bırakmayacak kadar açık
2. **Kod referansı** — hangi dosya, hangi fonksiyon
3. **Karar** — hangi seçenekler vardı, hangisi neden seçildi
4. **Kanıt** — seçimi destekleyen sayı, veriden ölçülmüş hali
5. **Neyi besliyor** — hangi notebook, hangi sonuç

Literatürden aynen alınmayan her şey ayrıca işaretlenir: neden aynen
alınamadı, yerine ne kondu.

## İçindekiler

| Dosya | Kapsam | Notebook |
|---|---|---|
| [01_Veri_Isleme.md](01_Veri_Isleme.md) | Kaynak, yükleme, QC kuralları, analiz maskesi | NB01 |
| [02_Fizik_ve_T0.md](02_Fizik_ve_T0.md) | Cart-pole modeli, doğrulaması, T₀ | NB02 |
| [03_Durum_Aksiyon_Episode.md](03_Durum_Aksiyon_Episode.md) | Park state/action, işaret konvansiyonu, episode ve regime run | NB02 |
| [04_Performans_Metrikleri.md](04_Performans_Metrikleri.md) | Trial metrikleri, metrik seti seçimi | NB03 |
| [05_Action_Timing.md](05_Action_Timing.md) | Ludolph'un event-triggered averaging'i; transfer kararları, fizibilite ve NB04 sonuçları | NB04 |
| [06_Karar_Istatistigi.md](06_Karar_Istatistigi.md) | Test seçimi, trend kontrastları (SR testi), çoklu karşılaştırma, duyarlılık | NB06 |

## İlgili belgeler

- [../Analiz_Gunlugu.md](../Analiz_Gunlugu.md) — tarihli çalışma günlüğü, ne zaman ne karara bağlandı
- [../Pilot_Sonuc_Ozeti.md](../Pilot_Sonuc_Ozeti.md) — pilotun bulgusu, sunumun metin karşılığı
- [../Veri_Kayit_Istekleri.md](../Veri_Kayit_Istekleri.md) — Unity ekibine iletilen kayıt formatı istekleri
- `../../CLAUDE.md` — çalışma bağlamı ve güncel sayılar; bu klasörün özeti değil, tamamlayıcısı
