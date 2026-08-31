# Pilot verisi: kayıt formatı için istekler

**Revizyon 2 — 30.08.2026.** İlk sürüm 26.08.2026'da P001–P002'nin (o zamanki
smoke test verisi, sonradan silindi) 106 trial'ına dayanıyordu. Bu sürüm
**12 gerçek katılımcının 636 trial'ına** (600 measurement) dayanıyor.
Sayıların hepsi yeniden ölçüldü; birkaç madde zayıfladı, biri tamamen
düştü, biri güçlendi.

Kayıt mekaniği sağlam: FixedUpdate'te örnekleme yapılıyor, her measurement
trial'da tam 1200 sample var ve tam 20 saniyeye denk geliyor, açı −180/+180
aralığında ve dik konum 0°, hız kolonları pozisyonların türeviyle tutarlı,
NaN yok, duplicate yok, 10 tur × 5 koşul dengesi tam, fizik parametreleri
Ludolph ile uyuşuyor. Fizik modelini veriden yeniden türetip doğruladık:
gözlenen açısal ivmeyle korelasyon 0.988–0.997.

Aşağıdaki maddeler analiz sırasında somut olarak tıkanan noktalar. Her biri
için verideki kanıtı ve olmazsa ne kaybedildiğini yazdım. **Önem sırasına
göre.**

---

## 1. randomizationSeed participant_id'den türetilsin ve her oturumda yeniden tohumlansın

**Bu belgedeki en önemli madde. İlk sürümden bu yana kanıt çok güçlendi.**

**Şu an:** `randomizationSeed: 12345` sabit, 12 katılımcının hepsinde.

**Veride görünen — üç ayrı sonuç:**

- **Koşul sırası özdeş.** 12 katılımcının hepsi aynı 50 trial'lık diziyi
  alıyor.
- **`noise_seed` dizisi özdeş.** Herkes birebir aynı noise desenini görmüş.
- **Başlangıç açıları da tek bir sabit listeden.** P001–P007'nin hepsi aynı
  açı dizisinden okuyor (hizalama %100). Giriş noktaları farklı:
  P001/P002/P004/P006 offset 0, P003 76, P007 89, P005 253. Offsetler oturum
  zincirini birebir doğruluyor — P002 tam 76 çekiliş yapmış ve P003 76'dan
  giriyor; P004 tam 253 yapmış ve P005 253'ten giriyor.

Yani **uygulama katılımcılar arasında kapatılmadığında RNG akışı kaldığı
yerden devam ediyor, kapatılınca 0'a dönüyor.** P008–P012 de hiçbiri offset
0'da değil (olsalardı P001'in ilk 152 çekilişiyle eşleşirlerdi), yani 27
Ağustos öğleden sonra uygulama hiç kapatılmamış görünüyor.

Açıların dışarıdan bağımsız görünmesinin sebebi: imleç davranışa göre
ilerliyor, her düşüş bir çekiliş tüketiyor. Farklı düşüş sayısı → aynı
listenin farklı yerleri. İz: P001'in T002'de aldığı −4.0469°'yi P002 T005'te
alıyor.

**Neden önemli:** Sırayı randomize etmenin amacı, katılımcı yorulur veya
öğrenirse bu etkinin her katılımcıda farklı koşullara dağılması. Sıra
herkeste aynı olursa 7. sıradaki koşul her katılımcıda aynı koşul oluyor.
Ayrıca herkes aynı noise desenini gördüğü için, o tek desen tesadüfen
sıradışıysa bunu anlamanın yolu yok.

**Şu anki etkisi ölçüldü ve küçük:** başlangıç |θ| koşullar arasında dengeli
(ortalamalar 3.53–3.85°, yayılım 0.32°) ve sonuçla korelasyonu zayıf
(düşüş sayısıyla r = +0.066). Koşul sırası tarafında da her tur içinde
yeniden karılıyor; her koşulun ortalama `trial_order`'ı 24.6–26.5 (1–50
aralığında), yani öğrenme/yorgunluk koşulla karışmamış.

**Olmazsa:** Katılımcı sayısını artırmak stimulus çeşitliliği hakkında yeni
bilgi üretmiyor. 20 kişi de toplansa hepsi aynı deseni aynı sırada görmüş
oluyor. Koşullar birbirine yakın çıktığında bu yanlılık ölçülmek istenen
etkiyle aynı büyüklüğe gelir.

**İstenen:** Seed `participant_id`'den türetilsin **ve her oturum başında
RNG yeniden tohumlansın.** Bu üç sorunu birden çözer.

**Not:** Kendi dökümanınızın 11. bölüm kontrol listesi madde 9 zaten bunu
istiyor ("İki farklı participant aynı noise seed/sırasını yanlışlıkla
paylaşmıyor mu?").

---

## 2. Reset satırlarında applied_force_n'e 0 yazılmasın, boş bırakılsın

**Şu an:** `phase = reset` satırlarında `applied_force_n` zorla 0.0 yazılıyor
(82.860 reset satırının hepsinde), ama `input_applied` katılımcının son
değerinde kalıyor — reset satırlarının **%35.8'inde** sıfırdan farklı.

**Neden önemli:** Ludolph'un ana analizi olan action timing, kuvvet
eğrisinin sıfırı kestiği anı ölçüyor. Her reset'te 60 kare boyunca force
kolonuna sert bir 0 yazınca, katılımcının hiç yapmadığı bir yön değiştirme
olayı üretilmiş oluyor. Veride **1.381 reset** var, yani 1.381 sahte olay.

Şu an bunu analiz tarafında episode sınırlarıyla çözüyoruz (olaylar sadece
kesintisiz active parçalar içinde aranıyor), ama bu her analizde tekrar
tekrar dikkat edilmesi gereken bir tuzak.

**Olmazsa:** Action timing yanlış çıkıyor ve gerçek geçişleri sahtelerinden
ayırmak analiz tarafında sürekli ekstra iş.

**Ek istek:** Bir `bout_index` kolonu (trial içinde her düşmede artan
sayaç). Şu an bunu `fall_event`'ten türetiyoruz; kolon olarak gelirse analiz
penceresinin yanlışlıkla bir reset'in üstünden atlamadığından emin olmak
kolaylaşır.

---

## 3. Reset'te hızlar sıfırlansın

**Şu an:** Reset sonrası pole açısı doğru şekilde U(−7.5°, +7.5°) dağılıyor
ve cart merkeze dönüyor, ama hızlar sıfırlanmıyor.

**Veride görünen:** Trial içi 1.381 restart'ın **1.380'inde** başlangıçta
artık açısal hız var, 13.7 °/s'ye kadar çıkıyor. (İlk sürümde "209 reset'in
40'ında" yazıyordu; daha çok veriyle görülüyor ki istisna değil, kural.)

**Neden önemli:** Ludolph'ta her deneme aynı tip durumdan başlar: rastgele
açı, diğer her şey sıfır. Ne kadar dengede kalınabildiği başlangıç durumuna
çok duyarlı. Bazı denemeler pole zaten dönmekteyken başlıyorsa, o denemeler
koşulla ilgisi olmayan bir sebeple daha zor oluyor. Üstelik bu artık hız bir
önceki düşmeden geliyor, yani rastgele bile değil — kötü giden bir denemenin
ardından gelen deneme sistematik olarak daha zor başlıyor.

**Olmazsa:** Açıklanamayan ek varyans ve birbiriyle karşılaştırılabilir
olmayan başlangıç koşulları. T₀ hesabı ω = 0 varsayıyor; ω ≠ 0 olduğunda
T₀ gerçek zorluğu tam yansıtmıyor.

---

## 4. Metadata'ya eklenmesi gerekenler

Dökümanın 7. bölümünde listelenmiş ama `metadata.json` dosyasında olmayanlar.
**24 alanın 24'ü hâlâ eksik.**

```
screen_width_px, screen_height_px, screen_physical_width_cm,
viewing_distance_cm, refresh_rate_hz, full_screen
input_axis_name, deadzone, sensitivity, invert_axis
noise: texture_width_px, texture_height_px, update_rate_hz,
       mean, clipping_method, monochrome_or_rgb, overlay_opacity
balance_angle_limit_deg, balance_cart_limit_m
experiment_version, build_id, scene_name, operating_system, session_start_utc
```

**Bunlardan en kritiği ekran ve izleme mesafesi grubu.** Sunumda "1 sanal
metre = 2.3 fiziksel cm" ve "noise elemanının görsel açısı 0.04°" deniyor.
İkisi de nesnelerin retinadaki fiziksel boyutuyla ilgili iddialar.
Doğrulamak için ekran çözünürlüğü, fiziksel ekran genişliği ve izleme
mesafesi gerekiyor; üçü de kayıtta yok. `noise_element_size_px: 4` kayıtlı
ama 4 piksel her monitörde ve her mesafede farklı bir görsel açıya denk
geliyor.

Hipotezin tamamı görsel noise hakkında olduğu için, katılımcının gerçekte ne
gördüğünü şu an sayısal olarak ifade edemiyoruz. Treviño ile
karşılaştırabilmek için bu şart (onlarda 60 cm izleme mesafesi ve 2×2 piksel
≈ 0.08° görsel açı belirtilmiş).

**İkinci öncelik input grubu.** `deadzone` ve `sensitivity` bilinmiyor.
Veriden görüldüğü kadarıyla girdi −1..1 arasında rampalanıyor (186 farklı
değer, sıfır olmayan en küçüğü 0.0153) ve örneklerin %73.9'u tam sıfır —
yani deadzone zaten uygulanmış ama değeri kayıtlı değil.

**Ufak not:** `noiseLevels[].sigma` float32 artifact'i olarak yazılıyor
(`0.019999999552965164`, `0.05000000074505806`, `0.07999999821186066`).
Double olarak yazılması veya yuvarlanması yeterli. Timeseries'teki
`noise_sigma` kolonu temiz geliyor, sorun sadece metadata'da.

---

## 5. Her sample'da gerçek frame süresi

**Şu an:** Sadece trial özetinde `mean_fps`, `min_fps`,
`dropped_frame_count` var.

**Veride görünen:** `mean_fps` 59.92–60.00, yani ortalama 60 Hz sorunsuz.
Ama 636 trial'ın **53'ünde** `min_fps < 50`, en düşüğü 29.1. Toplam
`dropped_frame_count` 44. Bu no_noise trial'larında da oluyor, yani noise
render'ından kaynaklanmıyor.

(İlk sürümde "53/53 trial'da 50'nin altında" yazıyordu — o smoke test
verisinin özelliğiymiş, gerçek veride oran çok daha düşük: %8.3.)

**Neden önemli:** 16.7 ms yerine 34 ms süren bir kare, katılımcının eski bir
görüntüye baktığı ve fizik motorunun görsel geri bildirim olmadan ilerlediği
bir an demek. Tam da kontrol hatası gibi görünecek türden bir an. Örnekleme
FixedUpdate'te olduğu için sample kaybı yok (her trial 1200 tam), ama
katılımcının **gördüğü** şey eksik.

**Olmazsa:** Katılımcı hatasını ekran takılmasından ayıramıyoruz. Görsel
noise'un algılanmasıyla ilgili bir deneyde render hızı doğrudan bağımsız
değişkeni etkiliyor.

**İstenen:** Timeseries'e sample başına `frame_time_ms` (veya
`dropped_frame` bayrağı). `window_focused` zaten var ve işe yarıyor, kalsın.

---

## 6. Geçerlilik kararını yazılım vermesin, ham sinyal yazılsın

**Şu an:** `valid_trial` 636 trial'ın 634'ünde 1. İki trial'da (P011 T030 ve
T034) 0 ve `invalid_reason = "paused"`. Yani mekanizma çalışıyor, ama
sadece bu tek durum için.

Dökümanda tanımlı `device_disconnect`, `focus_lost`, `missing_samples`
durumları pratikte hiç tetiklenmiyor. Mevcut veride bunların gerçekten
olmadığı da doğru olabilir — `window_focused` her sample'da 1, ölü input
trial'ı yok, her trial 1200 tam sample. Yani şu an bir çelişki görmüyoruz.

**Önerim yine de aynı: trial'ın geçerli olup olmadığına yazılım karar
vermesin.** Bunun yerine ham sinyaller (`device_connected`,
`frame_time_ms`) yazılsın, filtrelemeyi analiz tarafında yapalım. Hem sizin
için daha az iş, hem eşikler sonradan değiştirilebilir oluyor. `paused`
bilgisi değerli, kalsın — ama "geçersiz" kararı yerine olayın kendisi
kaydedilsin (ne zaman, ne kadar süreyle duraklatıldı).

**Ufak hata:** `config.participantId` hiç güncellenmiyor — 12 katılımcının
metadata'sında da "P001" yazıyor. Üst düzeydeki `participant_id` alanı
doğru, sadece `config` bloğundaki kopya yanlış. Analizi etkilemiyor ama
karışıklığa açık.

---

## Ayrıca not düşmek istediğim iki tasarım gözlemi

Bunlar kayıt formatı isteği değil, analizden çıkan gözlemler. Karar sizin,
sadece kayda geçsin diye yazıyorum.

**Floor effect endişesi büyük ölçüde geçti.** İlk sürümde smoke test
verisine bakarak "100 trial'ın sadece 9'u düşmeden tamamlanıyor, trial
başına 3.4 düşme, T/T₀ medyanı 1'e çok yakın, yani katılımcılar
*hiçbir şey yapmamak* seviyesinde" demiştim ve hiçbir koşulda anlamlı fark
bulamamıştım. **Gerçek veride tablo farklı:** 600 measurement trial'ın
**224'ü (%37.3)** düşmeden tamamlanıyor, trial başına ortalama 1.93 düşme
var, episode düzeyinde T/T₀ medyanı 1.52. Katılımcılar hiçbir şey
yapmamanın belirgin şekilde üzerinde. Nitekim koşullar arasında anlamlı
farklar da çıkıyor. Görev zorluğu şu haliyle uygun görünüyor.

**Sinyalin gücü hâlâ açık bir soru.** Treviño ve arkadaşlarının stochastic
resonance etkisi, sinyal bilerek eşiğin altına indirildiğinde gözlenmiş
(coherence ve luminance birlikte düşürülerek) ve makalede performansın
luminance %12'nin üzerinde doyduğu belirtiliyor. Buradaki pole ise yüksek
kontrastlı, ekranda büyük ve 60 dereceye kadar açılan bir nesne — açıkça
eşiğin çok üzerinde. Ayrıca sigma seviyeleri (0, 0.02, 0.05, 0.08, 0.25)
altta neredeyse lineer aralıklı, sonra 3.1 katlık bir sıçrama yapıyor;
Treviño'da seviyeler logaritmik ölçekte aralıklı.

Pilot sonucu bu endişeyi destekliyor: orta seviyede iyileşme yok, noise
arttıkça performans monoton olarak bozuluyor (bkz.
[Pilot_Sonuc_Ozeti.md](Pilot_Sonuc_Ozeti.md)). Yani gözlenen şey klasik
bir maskeleme etkisi gibi duruyor, stochastic resonance gibi değil.
