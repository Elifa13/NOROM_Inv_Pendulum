# Ana Deney: Kayıt İstekleri

2026-09-07, rev 2

## Ne yapacağım

Üç şeyi ayrı ayrı ölçmek istiyorum.

Genel öğrenme, yani seans boyunca performansın düzelmesi.
Yerçekimi her arttığında yaşanan geçici bozulma ve ardından toparlanma.
Occlusion testinde kişinin ne kadar isabetli tahmin ettiği.

Üçü aynı katılımcıda aynı anda oluyor ve tek bir performans eğrisine bakınca üçü
de aynı şekilde görünüyor. Ayırmak için hangi trial'ın hangi yerçekiminde ve hangi
aşamada olduğunun kayıtlı olması gerekiyor.

Hangi kolonun hangi analize girdiği `Ana_Deney_ML_Plani.md` içinde tablo halinde.

---

## 1. Olmazsa analiz yapılamaz

### Dengeleme tarafı

| Kolon | Dosya | Tip | Neden istiyorum |
|---|---|---|---|
| `gravity` | trial_summary | float, m/s² | O trial boyunca geçerli olan yerçekimi. Kişinin davranışını hangi yerçekiminde ölçtüğümü bilmeden ne öğrenme ne uyum analizi yapılabiliyor |
| `trial_success` | trial_summary | int 0/1 | Oyunun "bu trial başarılı" kararı, yani yerçekimini artırmaya karar verdiren bayrak. Sabit grupta da yazılsın, orada yerçekimi değişmese bile. Aşağıda neden önemli olduğunu ayrıca açıkladım |
| `block_id` | trial_summary | int | Blok numarası |
| `phase_label` | trial_summary | string | Sadece şu değerlerden biri: `practice`, `baseline`, `adaptation`, `washout`, `posttest`. Serbest metin olmasın, büyük küçük harf de sabit kalsın |
| `stick_raw` | timeseries | float, [-1, 1] | Cihazdan okunan ham değer, üzerinde hiçbir işlem yapılmadan. Şu anki iki input kolonu da işlenmiş halde ve örneklerin dörtte üçü tam sıfır. O sıfırların bir kısmı gerçekten müdahale yokluğu, bir kısmı eşiğin altında kalmış küçük hareketler. İkisini ayıramıyorum |
| `log_schema_version` | metadata | string | Kayıt kodu bu hafta yazılıyor ve toplama sırasında değişebilir. Hangi dosyanın hangi kolon setiyle yazıldığını bilmezsem elimde sessizce iki farklı format olur. Kolon eklendiğinde artırılsın |

`stick_raw` için iki ek not.

CSV'ye yazarken yuvarlanmasın, en az 6 ondalık basamak olsun. Yoksa kolonun amacı
olan küçük değerler sıfıra döner.

"Ham" derken tam olarak neyi kastettiğimi ayrıca yazmak gerekiyor, çünkü okuma ile
uygulanan değer arasında birden fazla işlem olabiliyor: deadzone, eğri, kırpma,
yumuşatma. İstediğim, cihazdan okunan değerin hiçbirine girmeden kaydedilmesi.
Ayrıca metadata'da bu işlemlerin **hangi sırayla** uygulandığı yazılsın (aşağıda).

### `trial_success` neden birinci kademede

Yerçekimi başarılı bir trial'dan sonra artıyor. Yani yerçekimi adımı rastgele
gelmiyor, iyi bir performansın ardından geliyor. Bu, "adımdan sonra performans
düştü" bulgusunu tek başına yorumlanamaz kılıyor, çünkü zaten iyi bir trial'ın
ardına bakıyoruz ve doğal olarak bir gerileme bekleniyor.

Bunu ayırmanın yolu sabit grup. Orada da başarılar oluyor ama yerçekimi değişmiyor.
Sabit gruptaki başarı sonrası gerilemeyi ölçüp, gradual gruptaki adım sonrası
düşüşten çıkarınca geriye yerçekimi değişiminin gerçek etkisi kalıyor.

Bu karşılaştırma iki grupta da başarı bayrağı kayıtlı değilse yapılamıyor.

### Occlusion tarafı

**`<pid>_<sid>_occlusion_responses.csv`**, bir satır = bir occlusion denemesi.

`participant_id`, `session_id`, `occlusion_block_id`, `phase_label`,
`occlusion_trial_id`, `stimulus_id`, `stimulus_gravity`, `session_time_s`,
`observation_duration_s`, `occlusion_duration_s`,
`onset_pole_angle_deg`, `onset_pole_angular_velocity_deg_s`,
`onset_cart_position_m`, `onset_cart_velocity_m_s`,
`true_pole_angle_at_occlusion_end_deg`,
`response_option_index`, `response_angle_deg`, `response_rt_s`, `response_valid`,
`force_during_occlusion_n`

Üç açıklama:

`onset_` ile başlayanlar pole'un **gizlendiği andaki** gerçek durum. Analizin
tamamı bunlara dayanıyor, çünkü doğru cevap sadece bu duruma ve yerçekimine bağlı.

`true_pole_angle_at_occlusion_end_deg` occlusion penceresinin **sonundaki** açı.
Yanıtın verildiği andaki değil. İsmi bu yüzden uzun, karışmasın diye.

`force_during_occlusion_n` tasarım gereği sıfır olmalı. Doğrulamak için istiyorum.

---

## 2. Ucuz, kritik değil

| Alan | Dosya | Neden istiyorum |
|---|---|---|
| `gravity_current` | timeseries | Yerçekimi trial içinde değişmiyorsa bu kolon trial_summary'nin kopyası. Yine de istiyorum, çünkü trial_summary trial bitince yazılıyorsa yanlışlıkla yeni yerçekimini yazma ihtimali var. İki kaynak varsa tutarsızlığı yakalarım. Maliyeti bir değişkeni satıra yazmak |
| `gravity_step_index` | trial_summary | Kaçıncı adımda olduğumuz. `trial_success` ve `gravity` varsa ben de çıkarabilirim, ama onlar yazıyorsa kolaylık olur |
| `session_time_s` | trial_summary ve occlusion_responses | Seans başlangıcına göre saniye. Dengeleme trial'larıyla occlusion denemelerini tek bir zaman çizgisine dizmek için |
| `frame_time_s` | timeseries | `Time.realtimeSinceStartup`. Fizik sayacı gerçek zamanı göstermiyor, bilgisayar takılsa da aynı artıyor. Takılmaların nerede olduğunu bulmak için |
| `render_frame_count` | timeseries | O satır yazılırken kaçıncı çizim karesindeyiz. Kaç fizik adımının aynı çizime ve aynı kol okumasına denk geldiğini gösteriyor. Frame rate düşerse aynı kol değeri birkaç satırda tekrar ediyor ve bu, kolu sabit tutmakla karışıyor |
| `group_id` | metadata | Kişi hangi grupta |
| `gravity_schedule` | metadata | Başlangıç değeri, artış adımı, artışı tetikleyen kriter, tavan değeri |
| `input_device` | metadata | Kullanılan cihazın adı ve modeli |
| `input_pipeline` | metadata | Ham okumadan uygulanan değere kadar yapılan işlemler, **sırasıyla**. Örneğin deadzone eşiği, sonra eğri tipi, sonra kırpma. `stick_raw` ile mevcut kolon arasındaki dönüşümü yeniden üretebilmek için |
| `probe_config` | metadata | Kaç blok, blok başına kaç deneme, gözlem süresi, occlusion süresi, ve **yanıt seçeneklerinin açı listesi**. Seçeneklerin eşit aralıklı olduğunu varsaymak istemiyorum, liste olsun |
| ekran bilgisi | metadata | Çözünürlük px, ekran boyutu cm, izleme mesafesi cm, refresh Hz |

---

## 3. Faydalı, olmasa da idare ederim

**`occlusion_stimuli.csv`**, deney başına tek dosya, bir satır = gösterilen
yörüngenin bir frame'i.

`stimulus_id`, `sample_index`, `t_s`, `pole_angle_deg`,
`pole_angular_velocity_deg_s`, `cart_position_m`, `cart_velocity_m_s`,
`applied_force_n`, `gravity`

Birinci kademedeki `onset_` kolonları varsa asıl hesabı zaten yapabiliyorum, çünkü
occlusion sırasında kuvvet sıfır ve sonuç sadece gizlenme anındaki duruma bağlı.

Bu dosya gözlem fazını da modellemek istersem işe yarıyor. Kişi pole'un hızını
gizlenmeden hemen önce mi okuyor yoksa biraz eskisini mi kullanıyor gibi sorular
ancak izlediği yörüngenin tamamı elimdeyse sorulabiliyor. Ludolph bunu modellemiş.

---

## 4. Format kuralları

- Kolon her zaman var olsun. O koşul o trial'da yoksa kolon silinmesin, sabit
  değer yazılsın.
- Boş hücre olmasın. Id'ler tam sayı, yokluk -1. Bayraklar 0/1, string değil.
- `phase_label` sadece belirlenen değerleri alsın, serbest metin olmasın.
- Ondalık ayırıcı nokta. `stick_raw` yuvarlanmasın.
- Mevcut kolonların adı ve sırası değişmesin, yeniler sona eklensin.
- Kolon seti değişirse `log_schema_version` artırılsın.

---

## 5. Cevap bekleyen sorular

1. **Occlusion uyaranları hangi yerçekimindeki kayıtlardan kesiliyor.** Bu, hangi
   grubun avantajlı olduğunu belirliyor. Uyaranlar sadece 3.5'ten kesilirse test,
   sabit grubun bütün seans boyunca yaşadığı dünyada yapılmış oluyor. Sadece düşük
   yerçekiminden kesilirse tersi olur. İki durumda da bulunan grup farkı "kim daha
   iyi öğrendi"yi değil, "kimin dünyası teste daha yakın"ı ölçme riski taşıyor.
   Öneri: 40 uyaran aralığa yayılsın, örneğin dörtte biri 1.0'dan, dörtte biri
   1.8'den, dörtte biri 2.6'dan, dörtte biri 3.5'ten.
2. **Occlusion testinde doğru cevap gösteriliyor mu.** Gösteriliyorsa ölçüm bozulur.
   Ludolph'ta doğru cevabın gösterildiği tek blok gruplar arası farkı siliyor.
3. **Blok başına kaç occlusion denemesi var.** Ludolph'ta 40. Bu sayı, kişi başına
   ayrı bir tahmin yapılabilip yapılamayacağını belirliyor. Simülasyonla gereken
   asgari sayıyı hesaplayıp size ayrıca söyleyeceğim.
4. Occlusion testi kaç blok ve seansın neresinde.
5. Gözlem süresi ve occlusion süresi ne kadar, kaç yanıt seçeneği var ve hangi açı
   aralığına yayılmış. Ludolph'ta 4.5 saniye, 900 ms, 13 seçenek, eksi 65 ile
   artı 65 derece arası.
6. Yerçekimi artış kuralı tam olarak ne. Ludolph'ta 1.0'dan başlıyor, her başarılı
   trial'dan sonra 0.1 artıyor, başarı 30 saniye düşmeden dengede kalmak, tavan 3.5.
7. Sonda yerçekimi başlangıç değerine geri dönüyor mu.
8. Grup başına kaç kişi, seans kaç dakika.
