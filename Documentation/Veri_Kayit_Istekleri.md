# Pilot verisi: kayıt formatı için istekler

İlk pilot verisini (P001 ve P002, 26.08.2026, toplam 106 measurement trial) inceledim. Kayıt mekaniği büyük ölçüde sağlam: FixedUpdate'te örnekleme yapılıyor, 1200 sample tam 20 saniyeye denk geliyor, açı -180/+180 aralığında ve dik konum 0°, hız kolonları pozisyonların türeviyle tutarlı (r = 0.9998), NaN yok, duplicate yok, 10 round × 5 koşul dengesi tam, fizik parametreleri Ludolph ile uyuşuyor.

Aşağıdaki maddeler analiz sırasında somut olarak tıkanan noktalar. Her biri için verideki kanıtı ve olmazsa ne kaybedildiğini yazdım.

---

## 1. randomizationSeed participant_id'den türetilsin

**Şu an:** `randomizationSeed: 12345` sabit.

**Veride görünen:** P001 ve P002'nin `condition_order` listesi birebir aynı. Dahası, 53 trial'ın `noise_seed` değerlerinin tamamı da aynı.

**Neden önemli:** Sırayı randomize etmenin amacı, katılımcı deney ilerledikçe yorulursa veya öğrenirse bu etkinin her katılımcıda farklı koşullara dağılması. Sıra herkeste aynı olursa, 7. sıradaki koşul her katılımcıda aynı koşul oluyor ve yorulma etkisi koşul etkisinden ayrılamıyor. Ayrıca herkes birebir aynı noise pattern'ini görüyor; o tek pattern tesadüfen sıradışıysa bunu anlamanın yolu yok.

**Olmazsa:** Katılımcı sayısını artırmak koşul etkisi hakkında yeni bilgi üretmiyor. 20 kişi de toplansa hepsi aynı stimulus'u aynı sırada görmüş oluyor.

**Not:** Kendi dökümanınızın 11. bölüm kontrol listesi madde 9 zaten bunu istiyor ("İki farklı participant aynı noise seed/sırasını yanlışlıkla paylaşmıyor mu?").

---

## 2. Reset satırlarında applied_force_n'e 0 yazılmasın, boş bırakılsın

**Şu an:** `phase=reset` satırlarında `applied_force_n` zorla 0.0 yazılıyor, ama `input_applied` katılımcının son değerinde kalıyor (reset satırlarının %32'sinde sıfırdan farklı).

**Neden önemli:** Ludolph'un ana analizi olan action timing, katılımcının kuvvetin yönünü değiştirdiği anı ölçüyor. Yani force eğrisinin sıfırı kestiği nokta. Her reset'te 60 kare boyunca force kolonuna sert bir 0 yazınca, katılımcının hiç yapmadığı bir yön değiştirme olayı üretilmiş oluyor. Tek oturumda 209 reset var, yani 209 sahte olay.

**Olmazsa:** Action timing yanlış çıkıyor ve gerçek geçişleri sahtelerinden ayırmanın temiz bir yolu yok.

**Ek istek:** Bir `bout_index` kolonu (trial içinde her düşmede artan sayaç). Şu an bunu `fall_event`'ten türetiyorum ama kolon olarak gelirse analiz penceresinin yanlışlıkla bir reset'in üstünden atlamadığından emin olmak kolaylaşır.

---

## 3. Her sample'da device_connected (0/1)

**Veride görünen:** 5 trial'da `input_raw` 20 saniye boyunca tam 0.0000. Beşi de `valid_trial=1`, `invalid_reason` boş.

**Neden önemli:** Hiç hareket etmeyen bir katılımcı ile kopmuş bir controller birebir aynı veriyi üretiyor. Birincisi gerçek (kötü) bir performans ve analizde kalmalı; ikincisi kayıp veri ve çıkarılmalı. Şu an hangisi olduğunu ayırt edemiyorum.

**Olmazsa:** Ya bozuk trial'ları analize sokuyorum ya da gerçek trial'ları atıyorum, ikisi de tahmin.

---

## 4. Reset'te hızlar sıfırlansın

**Şu an:** Reset sonrası pole açısı doğru şekilde U(-7.5°, +7.5°) dağılıyor ve cart merkeze dönüyor, ama hızlar tam sıfırlanmıyor.

**Veride görünen:** 209 reset'in 40'ında başlangıçta artık açısal hız var, 13.7 deg/s'ye kadar. Cart hızı 0.16 m/s'ye kadar çıkıyor.

**Neden önemli:** Ludolph'ta her deneme aynı tip durumdan başlar: rastgele açı, diğer her şey sıfır. Ne kadar dengede kalınabildiği başlangıç durumuna çok duyarlı. Bazı denemeler pole zaten dönmekteyken başlıyorsa, o denemeler koşulla ilgisi olmayan bir sebeple daha zor oluyor. Üstelik bu artık hız bir önceki düşmeden geliyor, yani rastgele bile değil.

**Olmazsa:** Açıklanamayan ek varyans ve birbiriyle karşılaştırılabilir olmayan başlangıç koşulları.

---

## 5. Her sample'da gerçek frame süresi

**Şu an:** Sadece trial özetinde `mean_fps`, `min_fps`, `dropped_frame_count` var.

**Veride görünen:** `mean_fps` her koşulda 59.95-59.99, yani ortalama 60 Hz sorunsuz. Ama `min_fps` 53/53 trial'da 50'nin altında, P002'de 20'ye kadar düşüyor. Bu no_noise trial'larında da aynı, yani noise render'ından kaynaklanmıyor.

**Neden önemli:** 16.7 ms yerine 50 ms süren bir kare, katılımcının eski bir görüntüye baktığı ve fizik motorunun görsel geri bildirim olmadan ilerlediği bir an demek. Tam da kontrol hatası gibi görünecek türden bir an. Şu an her trial'da böyle bir an olduğunu biliyorum ama nerede olduğunu göremediğim için o sample'ları dışarıda bırakamıyorum.

**Olmazsa:** Katılımcı hatasını ekran takılmasından ayıramıyorum.

**İstenen:** Timeseries'e sample başına gerçek `frame_time_ms` (veya `dropped_frame` bayrağı). `window_focused` zaten var, kalsın.

---

## 6. Metadata'ya eklenmesi gerekenler

Dökümanın 7. bölümünde listelenmiş ama `metadata.json` dosyasında olmayanlar:

```
screen_width_px, screen_height_px, screen_physical_width_cm,
viewing_distance_cm, refresh_rate_hz, full_screen
input_axis_name, deadzone, sensitivity, invert_axis
noise: texture_width_px, texture_height_px, update_rate_hz,
       mean, clipping_method, monochrome_or_rgb, overlay_opacity
balance_angle_limit_deg, balance_cart_limit_m
experiment_version, build_id, scene_name, operating_system, session_start_utc
```

**Bunlardan en kritiği ekran ve izleme mesafesi grubu.** Sunumda "1 sanal metre = 2.3 fiziksel cm" ve "noise elemanının görsel açısı 0.04°" deniyor. İkisi de nesnelerin retinadaki fiziksel boyutuyla ilgili iddialar. Doğrulamak için ekran çözünürlüğü, fiziksel ekran genişliği ve izleme mesafesi gerekiyor; üçü de kayıtta yok. `noise_element_size_px: 4` kayıtlı ama 4 piksel her monitörde ve her mesafede farklı bir görsel açıya denk geliyor.

Hipotezin tamamı görsel noise hakkında olduğu için, şu an katılımcının gerçekte ne gördüğünü sayısal olarak ifade edemiyorum.

**Ufak not:** `noise_sigma` değerleri float32 artifact'i olarak yazılıyor (`0.019999999552965165`). Double olarak yazılması veya yuvarlanması yeterli.

---

## 7. Geçerlilik kararını yazılım vermesin, ham sinyal yazılsın

`valid_trial` 106 trial'ın hepsinde 1, `invalid_reason` hiç tetiklenmiyor. Dökümanda tanımlı `device_disconnect`, `focus_lost`, `missing_samples` gibi durumlar pratikte hiç yakalanmıyor (yukarıdaki 5 ölü controller trial'ı dahil).

Bunu düzeltmenizi istemek yerine önerim şu: **trial'ın geçerli olup olmadığına yazılım karar vermesin.** Bunun yerine yukarıdaki 3 ve 5 numaralı ham sinyaller (`device_connected`, `frame_time_ms`) yazılsın, filtrelemeyi analiz tarafında ben yapayım. Hem sizin için daha az iş, hem eşikler sonradan değiştirilebilir oluyor.

---

## Ayrıca not düşmek istediğim iki tasarım gözlemi

Bunlar kayıt formatı isteği değil, analizden çıkan gözlemler. Karar sizin, sadece kayda geçsin diye yazıyorum.

**Floor effect.** 100 measurement trial'ın sadece 9'u 20 saniyeyi düşmeden tamamlıyor, trial başına ortalama 3.4 düşme var. Ludolph'un T/T₀ ölçüsünü (denemenin, hiçbir şey yapılmasaydı süreceği süreye oranı) hesapladım: medyan değerler bütün koşullarda 1'e çok yakın çıkıyor. Yani katılımcılar yaklaşık olarak "hiçbir şey yapmamak" seviyesinde performans gösteriyor. Bu seviyede hiçbir manipülasyon koşullar arasında fark üretemez. Nitekim trial düzeyinde hiçbir metrikte anlamlı koşul farkı yok (en iyi durumda p = 0.13) ve iki katılımcının koşul sıralaması arasındaki korelasyon 0.0.

**Sinyalin gücü.** Treviño ve arkadaşlarının stochastic resonance etkisi, sinyal bilerek eşiğin altına indirildiğinde gözlenmiş (coherence ve luminance birlikte düşürülerek), ve makalede performansın luminance %12'nin üzerinde doyduğu belirtiliyor. Buradaki pole ise yüksek kontrastlı, ekranda büyük ve 60 dereceye kadar açılan bir nesne, yani açıkça eşiğin çok üzerinde. Ayrıca sigma seviyeleri (0, 0.02, 0.05, 0.08, 0.25) altta neredeyse lineer aralıklı, sonra 3.1 katlık bir sıçrama yapıyor; Treviño'da seviyeler logaritmik ölçekte.
