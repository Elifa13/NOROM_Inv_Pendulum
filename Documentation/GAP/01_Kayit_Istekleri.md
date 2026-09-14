# GAP: Kayıt İstekleri

rev 4, 2026-09-09. Random force kolu bu belgenin dışında.

Tasarımın tamamı [00_Tasarim.md](00_Tasarim.md) içinde. Hangi kolonun hangi
analize girdiği [02_Modelleme_Plani.md](02_Modelleme_Plani.md) içinde tablo halinde.

**Rev 3'te değişenler.** Sekiz aşamalı akış netleşti, bu yüzden `phase_label`
listesi yeniden yazıldı. Yerçekimi artışının başarıya değil sabit takvime
bağlı olduğu kesinleşti, bu yüzden `trial_success` birinci kademeden ikinciye
indi. Occlusion testinin yapısı belli olduğu için `occlusion_stimuli.csv`
üçüncü kademeden ikinciye çıktı.

**Rev 4'te değişenler.** Kontrol grubunun bütün seans boyunca g = 1.0'da
kaldığı netleşti, kolon istekleri buna göre güncellendi. Occlusion
uyaranlarının pilotun no-noise trial'larından kesileceği ve hepsinin g = 1.0
olacağı kesinleşti. Doğru cevabın gösterilmeyeceği onaylandı. Bu üç cevapla
soru listesi bire indi.

`trial_success` isteği tamamen çıkarıldı. Yerçekimi artık başarıya bağlı
olmadığı için analizin geçerlilik şartı değildi, ve trial 20 saniyede sabit
olduğu için "başarılı" tanımı da belirsiz kalıyordu. Aynı bilgiyi `fall_event`
üstünden kendimiz türetebiliyoruz, pilotta da öyle yapıldı.

## Ne yapacağım

Üç şeyi ayrı ayrı ölçmek istiyorum.

Genel öğrenme, yani seans boyunca performansın düzelmesi.
Yerçekimi her arttığında yaşanan geçici bozulma ve ardından toparlanma.
Occlusion testinde kişinin ne kadar isabetli tahmin ettiği.

Üçü aynı katılımcıda aynı anda oluyor ve tek bir performans eğrisine bakınca
üçü de aynı şekilde görünüyor. Ayırmak için hangi trial'ın hangi yerçekiminde
ve hangi aşamada olduğunun kayıtlı olması gerekiyor.

---

## 1. Olmazsa analiz yapılamaz

### Dengeleme tarafı

| Kolon | Dosya | Tip | Neden istiyorum |
|---|---|---|---|
| `gravity` | trial_summary | float, m/s² | O trial boyunca geçerli olan yerçekimi. Kişinin davranışını hangi yerçekiminde ölçtüğümü bilmeden ne öğrenme ne uyum analizi yapılabiliyor |
| `phase_label` | trial_summary | string | Trial hangi aşamaya ait. Aşağıda değer listesi var. Serbest metin olmasın, büyük küçük harf sabit kalsın |
| `block_id` | trial_summary | int | Blok numarası |
| `stick_raw` | timeseries | float, [-1, 1] | Cihazdan okunan ham değer, üzerinde hiçbir işlem yapılmadan. Şu anki iki input kolonu da işlenmiş halde ve örneklerin dörtte üçü tam sıfır. O sıfırların bir kısmı gerçekten müdahale yokluğu, bir kısmı eşiğin altında kalmış küçük hareketler. İkisini ayıramıyorum |
| `log_schema_version` | metadata | string | Kayıt kodu bu hafta yazılıyor ve toplama sırasında değişebilir. Hangi dosyanın hangi kolon setiyle yazıldığını bilmezsem elimde sessizce iki farklı format olur. Kolon eklendiğinde artırılsın |

### `phase_label` değerleri

Sekiz aşamanın her biri ayrı bir etiket alsın. Aşağıdaki liste dışında değer
yazılmasın:

| Değer | Aşama | Not |
|---|---|---|
| `familiarization` | 1 | Analize girmiyor ama etiketlensin, atılabilmesi için |
| `baseline` | 2 | |
| `prediction_pre` | 3 | occlusion_responses.csv'de de bu değer |
| `adaptation` | 4 | |
| `late_adaptation` | 5 | |
| `prediction_post` | 6 | occlusion_responses.csv'de de bu değer |
| `readaptation` | 7 | |
| `washout` | 8 | |

Bu liste kritik. Aşamalar birbirinden yalnızca bu kolonla ayrılıyor. Tek bir
etiket eksik ya da birleşik olursa (örneğin adaptation ile late adaptation
aynı etiketi alırsa) o iki aşama analizde ayrılamaz ve geri dönüşü yok.

Aşama 3 ve 6'da dengeleme trial'ı yok. Yine de o aşamalarda trial_summary
satırı yazılıyorsa etiketi yukarıdaki gibi olsun, boş kalmasın.

**Kontrol grubu da aynı sekiz etiketi kullansın.** O grup bütün seansı
g = 1.0'da geçiriyor ve aşama 5, 7, 8'in onda ayrı bir anlamı yok. Ama
trial'ların iki grup arasında eşleştirilebilmesi için etiketler aynı olmalı.
Aksi halde "gradual grubun washout'u ile kontrol grubunun aynı andaki
trial'ları" karşılaştırılamaz ve aftereffect hesabı yapılamaz.

### `stick_raw` için iki not

CSV'ye yazarken yuvarlanmasın, en az 6 ondalık basamak olsun. Yoksa kolonun
amacı olan küçük değerler sıfıra döner.

"Ham" derken tam olarak neyi kastettiğimi ayrıca yazmak gerekiyor, çünkü okuma
ile uygulanan değer arasında birden fazla işlem olabiliyor: deadzone, eğri,
kırpma, yumuşatma. İstediğim, cihazdan okunan değerin hiçbirine girmeden
kaydedilmesi. Ayrıca metadata'da bu işlemlerin **hangi sırayla** uygulandığı
yazılsın (aşağıda `input_pipeline`).

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
tamamı bunlara dayanıyor, çünkü doğru cevap sadece bu duruma ve yerçekimine
bağlı.

`true_pole_angle_at_occlusion_end_deg` occlusion penceresinin **sonundaki**
açı. Yanıtın verildiği andaki değil. İsmi bu yüzden uzun, karışmasın diye.

`force_during_occlusion_n` tasarım gereği sıfır olmalı. Doğrulamak için
istiyorum.

`stimulus_id` iki dosya arasındaki bağlantı anahtarı. Sunum sırası kişiden
kişiye ve bloktan bloğa değiştiği için satırlar ancak bununla eşleşiyor. Üç
şartı var: aynı uyaran bütün katılımcılarda aynı id'yi taşısın, pre ve post
testinde de aynı id'yi taşısın, ve id `occlusion_stimuli.csv` içindekiyle
birebir aynı olsun. Bu tutmazsa uyaran içi karşılaştırma kurulamaz.

`occlusion_trial_id` ise sunum sırası, yani o denemenin blok içinde kaçıncı
olduğu. Sıra etkisini (blok içinde yorgunluk ya da dikkat kayması) kontrol
etmek için ve randomizasyonun gerçekten kişiden kişiye farklı olduğunu
doğrulamak için gerekiyor. İkincisi teorik bir endişe değil: pilot 1'de seed
sabitlenmişti ve bütün katılımcılar aynı sırayı görmüştü, bunu ancak veriden
fark ettik.

`stimulus_gravity` bütün uyaranlarda 1.0 olacak, çünkü uyaranlar pilotun
no-noise trial'larından kesiliyor. Sabit bir değer olsa da kolon yazılsın:
analizin doğru cevabı hesaplaması bu sayıya bağlı ve ileride başka bir
yerçekiminden uyaran eklenirse format değişmemiş olur.

Doğru cevap katılımcıya gösterilmeyecek. Bu kayıt tarafını değil uygulamayı
ilgilendiriyor ama buraya da yazıyorum, çünkü Ludolph'ta feedback verilen
bloklarda gruplar arası fark tamamen siliniyor.

---

## 2. Ucuz, kritik değil

| Alan | Dosya | Neden istiyorum |
|---|---|---|
| `gravity_step_index` | trial_summary | Kaçıncı adımda olduğumuz, 1'den 10'a. Kontrol grubunda yerçekimi değişmiyor ama kolon yine yazılsın, aynı numarayla: iki grubun trial'ları ancak böyle eşleştirilebiliyor |
| `trial_index_in_step` | trial_summary | Adım içinde kaçıncı trial, 1'den 8'e. Early (1-3) ve late (6-8) ayrımı doğrudan bu kolondan geliyor. Sıralamayı ben yeniden kurmak zorunda kalmayayım |
| `gravity_current` | timeseries | Yerçekimi trial içinde değişmiyorsa bu kolon trial_summary'nin kopyası. Yine de istiyorum, çünkü trial_summary trial bitince yazılıyorsa yanlışlıkla yeni yerçekimini yazma ihtimali var. İki kaynak varsa tutarsızlığı yakalarım |
| `session_time_s` | trial_summary ve occlusion_responses | Seans başlangıcına göre saniye. Dengeleme trial'larıyla occlusion denemelerini tek bir zaman çizgisine dizmek için. Aşama 6 ile 7 arasında ne kadar süre geçtiğini de bundan okuyacağım |
| `frame_time_s` | timeseries | `Time.realtimeSinceStartup`. Fizik sayacı gerçek zamanı göstermiyor, bilgisayar takılsa da aynı artıyor. Takılmaların nerede olduğunu bulmak için |
| `render_frame_count` | timeseries | O satır yazılırken kaçıncı çizim karesindeyiz. Kaç fizik adımının aynı çizime ve aynı kol okumasına denk geldiğini gösteriyor. Frame rate düşerse aynı kol değeri birkaç satırda tekrar ediyor ve bu, kolu sabit tutmakla karışıyor |
| `group_id` | metadata | Kişi hangi grupta: gradual ya da constant |
| `gravity_schedule` | metadata | O kişinin aşama aşama yerçekimi planı. Gradual grup için başlangıç değeri, adım büyüklüğü, adım başına trial sayısı, tavan; kontrol grubu için sabit 1.0. Artış sabit takvimle olduğu için tetikleyici kriter alanı gerekmiyor, ama takvimin kendisi yazılsın. İki grubun aynı alanı farklı doldurması yeterli, ayrı alan gerekmiyor |
| `input_device` | metadata | Kullanılan cihazın adı ve modeli |
| `input_pipeline` | metadata | Ham okumadan uygulanan değere kadar yapılan işlemler, **sırasıyla**. Örneğin deadzone eşiği, sonra eğri tipi, sonra kırpma. `stick_raw` ile mevcut kolon arasındaki dönüşümü yeniden üretebilmek için |
| `probe_config` | metadata | Blok sayısı, blok başına deneme sayısı, gözlem süresi, occlusion süresi, ve **yanıt seçeneklerinin açı listesi**. Seçeneklerin eşit aralıklı olduğunu varsaymak istemiyorum, liste olsun |
| ekran bilgisi | metadata | Çözünürlük px, ekran boyutu cm, izleme mesafesi cm, refresh Hz |

**`occlusion_stimuli.csv`**, deney başına tek dosya, bir satır = gösterilen
yörüngenin bir frame'i.

`stimulus_id`, `sample_index`, `t_s`, `pole_angle_deg`,
`pole_angular_velocity_deg_s`, `cart_position_m`, `cart_velocity_m_s`,
`applied_force_n`, `gravity`

Bu dosya rev 2'de "olmasa da olur" kademesindeydi, artık değil. Sebebi deneme
sayısı: kişi başına 2 blok x 40 = 80 occlusion denemesi var, Ludolph 440
kullanmış. Bu kadar az denemeyle kişi başına parametre tahmini zorlanacak ve
gözlem fazını da modele katabilmek elimizdeki tek ek bilgi kaynağı.

Uyaranlar herkeste ortak olduğu için dosya **deney başına tek**, katılımcı
başına değil. 40 uyaran, her biri 5.5 saniye (4.5 s gözlem + 1 s sıfır
kuvvet), 60 Hz'de uyaran başına 330 satır, toplam yaklaşık 13.200 satır.
Maliyeti bir kez yazmak.

**Pre ve post testinde aynı 40 uyaran kullanılsın.** Farklı setler
kullanılırsa iki test arasındaki fark, iç modelin değişmesinden mi ikinci
setin daha zor olmasından mı geliyor, ayrılamaz. Aynı set kullanılınca uyaran
zorluğu tamamen düşüyor ve karşılaştırma hem kişi içi hem uyaran içi oluyor.
Feedback verilmediği için doğru cevabı hatırlama riski yok; Ludolph da aynı
40 uyaranı on bir blokta tekrarlamış.

---

## 3. Format kuralları

- Kolon her zaman var olsun. O koşul o trial'da yoksa kolon silinmesin, sabit
  değer yazılsın.
- Boş hücre olmasın. Id'ler tam sayı, yokluk -1. Bayraklar 0/1, string değil.
- `phase_label` sadece yukarıdaki sekiz değeri alsın, serbest metin olmasın.
- Ondalık ayırıcı nokta. `stick_raw` yuvarlanmasın.
- Mevcut kolonların adı ve sırası değişmesin, yeniler sona eklensin.
- Kolon seti değişirse `log_schema_version` artırılsın.

---

## 4. Sayılar

Sekiz aşamanın trial sayıları kesinleşti: familiarization 3, motor baseline 8,
adaptation 10 adım x 8, late adaptation 8, re-adaptation 8, washout 8. Toplam
115 dengeleme trial'ı. Prediction testleri 40'ar deneme, toplam 80.

**İki grupta da bütün sayılar aynı**, tek fark yerçekimi. Kontrol grubu her
aşamada aynı sayıda trial'ı g = 1.0'da yapıyor. Aftereffect'in büyüklüğü ancak
bu eşleşme korunursa hesaplanabiliyor.

Grup başına katılımcı sayısını simülasyonla güç hesabından çıkarıp ayrıca
ileteceğim.
