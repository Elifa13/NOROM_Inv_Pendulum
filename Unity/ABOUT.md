# Unity

Deneyi çalıştıran Unity projesi buraya gelecek. **Şu an boş** — proje
deney ekibinde, bu repoda yok.

Analiz tarafı Unity'ye sadece üretilen veri üzerinden bağlı. Kayıt formatına
dair istekler ekibe ayrı bir belgeyle iletiliyor:
[../Documentation/Veri_Kayit_Istekleri.md](../Documentation/Veri_Kayit_Istekleri.md).

## Veriden bilinen build bilgisi

| | |
|---|---|
| Unity sürümü | 6000.3.11f1 (12 katılımcının hepsinde aynı) |
| Örnekleme | FixedUpdate, 60 Hz (`fixed_delta_time_s` = 1/60) |
| Noise | Full-screen uniform pixel noise, orta gri ± σ, her display frame'de yenileniyor, eleman boyutu 4 px |
| Trial | 20 s aktif + 1 s reset, 3 practice + 50 measurement |

Fizik modeli metadata'da yazmıyor; veriden türetildi ve doğrulandı (bkz.
[../Documentation/Yontem/02_Fizik_ve_T0.md](../Documentation/Yontem/02_Fizik_ve_T0.md)).
Standart cart-pole, düzgün çubuk, RK4, Δt = 1/60. Dinamik denklemine
**yarım** pole uzunluğu (0.5 m) giriyor.

## Analiz tarafını etkileyen kayıt davranışları

Ayrıntı ve gerekçe `Veri_Kayit_Istekleri.md`'de; burada sadece uyarı olarak:

- `randomizationSeed` 12345'e sabit — bütün katılımcılar aynı koşul sırasını,
  aynı noise desenini ve aynı başlangıç açısı dizisini alıyor
- Reset satırlarında `applied_force_n` sıfıra zorlanıyor ama `input_applied`
  son değerinde kalıyor → sahte zero-crossing üretiyor
- Reset'te hızlar sıfırlanmıyor
- `config.participantId` hiç güncellenmiyor, hepsinde "P001" yazıyor
