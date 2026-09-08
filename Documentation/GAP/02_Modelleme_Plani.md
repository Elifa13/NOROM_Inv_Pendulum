# Ana Deney: Modelleme Planı

2026-09-07, rev 2. Random force kolu bu belgenin dışında.

Bu belge benim çalışma planım. Toplantıya giren belge `Ana_Deney_Kayit_Istekleri.md`.
Buradaki her analiz, oradaki bir kayıt isteğinin gerekçesi.

Rev 2'de eleştiriler üzerine üç değişiklik yapıldı. Yerçekimini davranıştan okuma
analizi ayrı bir madde olmaktan çıkarıldı, çünkü olduğu haliyle insanı değil fiziği
ölçüyordu. Adım analizine sabit grup kontrolü eklendi, çünkü adımların başarıyla
tetiklenmesi bir confound üretiyor. İki içsel yerçekimi ölçümünün karşılaştırılmasına
güvenilirlik kapısı kondu.

---

## Neden model kuruyoruz

Ölçmek istediğimiz üç şeyin hiçbiri doğrudan gözlenmiyor.

Kişinin ne kadar öğrendiği gözlenmiyor, performansı gözleniyor.
Kişinin kafasındaki yerçekimi gözlenmiyor, verdiği kuvvet gözleniyor.
Kişinin iç modeli gözlenmiyor, tahmini gözleniyor.

Üçü de latent değişken. Gözlenen davranıştan geri çıkarılmaları gerekiyor. Bu bir
system identification problemi ve trial ortalamalarıyla çözülmüyor.

---

## Bütün analizler için geçerli iki kural

**Gruplar sadece aynı yerçekiminde adil karşılaştırılır.** Gradual grup seansın
başında 1.0'da, sabit grup 3.5'te. Bu noktada performans farkı çıkması kaçınılmaz
ve öğrenmeyle ilgisi yok, sadece zorluk farkı. Anlamlı karşılaştırma, ikisinin de
3.5'te olduğu son bölümde ve occlusion testlerinde. Ludolph da tam olarak böyle
yapmış.

**Sabit grupta yerçekimi adımı yok.** Adıma dayanan analizlerin (B ve C) örneklemi
20 kişi, 40 değil. Sabit grup orada karşılaştırma grubu değil, kontrol.

---

## Analizler

Yedi analiz var. A ve D temel, diğerleri onların üstüne kuruluyor.

---

### A. Kontrolcü tanımlaması

**Amaç.** Kişinin kontrol politikasını bir fonksiyon olarak çıkarmak, ve bu
fonksiyonun yerçekimi arttıkça nasıl değiştiğini görmek.

**Hangi veri.** `timeseries.csv`, sadece aktif örnekler. Girdi olarak
`pole_angle_deg`, `pole_angular_velocity_deg_s`, `cart_position_m`,
`cart_velocity_m_s` ve bir önceki input. Hedef olarak `stick_raw`. Bölmek için
`trial_summary`'deki `gravity` ve `phase_label`. Zamanlama için `frame_time_s` ve
`render_frame_count`.

**Yöntem.** İki aşamalı model, çünkü input dağılımı yığılmalı. Pilotta örneklerin
%73.9'u tam sıfır. Düz regression bu veride sürekli sıfıra yakın tahmin eder ve
hiçbir şey öğrenmez.

1. Müdahale var mı yok mu. Binary sınıflandırma.
2. Varsa ne kadar ve hangi işarette. Regression.

Gecikme varsayılmaz, fit edilir. State t eksi d anından okunuyor, d 0 ile 400 ms
arasında taranıp held-out likelihood'u maksimize eden seçiliyor. d'nin kendisi de
bir sonuç.

Model merdiveni: ridge, sonra LightGBM, gerekirse küçük bir MLP. Her basamağa
çıkmak için held-out kazancın gerçek olması şart.

**Bölümleme.** Politikayı her yerçekimi adımı için ayrı fit etmek çekici ama
tehlikeli. Erken adımlarda başarı hızlı geldiği için adım başına çok az trial
düşebilir ve fit oturmaz. Bu yüzden adım adım değil, veri hacmine göre uyarlanmış
yerçekimi aralıklarına bölünecek. Aralık sınırları veri geldikten sonra, her
aralıkta yeterli trial olacak şekilde belirlenecek.

**Kritik metodolojik nokta.** 60 Hz'de ardışık örnekler birbirinin neredeyse
kopyası. Cross-validation asla rastgele sample bölerek yapılmaz, hep trial ya da
blok bloğu ayrılır. Aksi halde her şey anlamlı çıkar ve hepsi sahtedir.

Analiz ikinci bir birimde de tekrarlanacak: input event. Onset anındaki state
girdi, o event'in genliği ve süresi çıktı. Bu, otokorelasyon problemini kökünden
çözüyor. Sample modeli detay için, event modeli karar için.

**İç kontrol.** Politikanın gerçekten değiştiğini doğrulamak için, sadece kişinin
inputundan yerçekimini tahmin etmeye çalışacağız. Buradaki incelik önemli: modele
state verilmez. Verilirse model yerçekimini kişinin davranışından değil doğrudan
fizikten okur, çünkü pole'un ivmesi zaten yerçekiminin fonksiyonu. O zaman ölçtüğün
şey bir fizik dedektörü olur, insanla ilgisi kalmaz. Bu yüzden bu bir kontrol,
ayrı bir bulgu değil.

**Çıktı.** Her (kişi × yerçekimi aralığı) için gain vektörü, gecikme, held-out skor.

**Neden model gerekli.** Gain ve gecikme doğrudan ölçülebilen şeyler değil,
davranıştan geri çıkarılıyorlar. Ortada özetlenecek bir kolon yok.

**Bağlı istekler.** `gravity`, `stick_raw`, `frame_time_s`, `render_frame_count`.

---

### B. Politika kayması

**Amaç.** Adaptation hızını, hiçbir parametreyi yorumlamadan ölçmek.

**Hangi veri.** A'nın fit edilmiş modelleri.

**Yöntem.** Aralık k'de fit edilen modeli aralık j'nin verisinde test et. Bütün
çiftler için yap. Kayıp matrisinde köşegenden uzaklaştıkça bozulma hızı,
politikanın ne kadar hızlı değiştiğini veriyor.

**Çıktı.** Kişi başına bir matris ve ondan türeyen tek bir kayma hızı sayısı.

**Neden model gerekli.** Fonksiyonel form varsayımı yok. "Gain arttı mı"
tartışmasına girmeden politikanın değiştiğini gösteriyor.

**Örneklem.** Sadece gradual grup, 20 kişi.

---

### C. Yerçekimi adımlarına tepki

**Amaç.** Yerçekimi her arttığında yaşanan bozulmayı ve toparlanmayı ölçmek.

**Hangi veri.** `trial_summary` performans metrikleri, A'nın gecikme çıktısı,
`gravity` ve `trial_success`.

**Buradaki asıl sorun ve çözümü.** Yerçekimi başarılı bir trial'dan sonra artıyor.
Yani adım rastgele gelmiyor, iyi performansın ardından geliyor. Adımdan önceki
trial tanım gereği başarılı. Bu durumda adım sonrası performans düşüşünün ne kadarı
yerçekiminden, ne kadarı regression to the mean'den, ayrılmıyor. Ludolph'ta da bu
sorun var ve ele alınmamış.

Çözüm sabit grup. Orada da başarılar oluyor ama yerçekimi değişmiyor. Sabit gruptaki
başarı sonrası performans yörüngesi tam olarak regression to the mean'in ölçüsü.
Gradual gruptaki adım sonrası düşüşten onu çıkarınca geriye yerçekimi değişiminin
gerçek etkisi kalıyor.

Bu, sabit grubun planlanmamış ama en değerli kullanımı, ve tek şartı iki grupta da
`trial_success` bayrağının kayıtlı olması.

**Yöntem.** Her adım için toparlanma eğrisi fit ediliyor. Adım başına trial sayısı
az olacağı için tek tek fit gürültülü olur. Hierarchical model kullanılacak, yani
her adımın eğrisi kişinin ve grubun ortalamasından ödünç alıyor.

**Çıktı.** Her (kişi × adım) için bozulmanın büyüklüğü ve toparlanma zaman sabiti.

**Asıl soru.** Zaman sabiti adımlar ilerledikçe küçülüyor mu. Yani kişi sadece
görevi değil, uyum sağlamayı da öğreniyor mu.

**Güç konusunda dürüst olalım.** Kişi başına yaklaşık 25 adım var ama bunlar
bağımsız tekrar değil. Adımlar 0.1 m/s², yani küçük. Ardışıklar, birbirleriyle ve
zamanla karışıyorlar. Adım başına trial sayısı da eşit değil. Ludolph'un kendi
verisinde tek tek adımların etkisi gürültülü, sadece ortalamada anlamlı çıkıyor,
hatta variability etkisi için ilk üç adımı atmak zorunda kalmışlar.

Doğru ifade şu: tekrarlı within-subject olaylar mixed model'e iki noktanın
farkından çok daha fazla dayanak veriyor. Ama bunlara bağımsız tekrarmış gibi
davranan bir analiz yanlış olur.

**Örneklem.** Gradual grup 20 kişi, sabit grup kontrol olarak 20 kişi.

**Bağlı istekler.** `trial_success` (bunsuz olmaz), `gravity`, `gravity_step_index`.

---

### D. Occlusion hatasının ayrıştırılması ve içsel yerçekimi

**Amaç.** Occlusion testindeki hatanın neden değiştiğini bulmak, ve kişinin
kafasındaki yerçekimini bir sayıya çevirmek.

**Hangi veri.** `occlusion_responses.csv`, özellikle `onset_` kolonları ve
`stimulus_gravity`. `occlusion_stimuli.csv` varsa gözlem fazı da modellenebilir.

Occlusion testi ayrı bir blok. Denek oynamıyor, başkalarının kayıtlarını izliyor,
uyaranlar herkeste ortak. İkisi de analiz açısından iyi haber: kişinin kendi
davranışı doğru cevabı etkilemiyor, ve kişiler arası karşılaştırma aynı uyaranlar
üstünden yapılıyor.

**Yöntem.** Her deneme için:

1. Uyaranın gizlenme anındaki durumundan başla.
2. Varsayılan bir yerçekimi değeriyle, sıfır kuvvet altında, occlusion süresi kadar
   ileri simüle et. Bu bizim `src/physics.py` içindeki RK4 ile birebir aynı hesap.
3. Elde edilen açıyı en yakın yanıt seçeneğine yuvarla.
4. Gözlenen cevapla karşılaştır.

Bütün denemeler üzerinden iki serbest parametre maximum likelihood ile bulunuyor:
kişinin varsaydığı yerçekimi, ve cevabındaki gürültünün büyüklüğü.

Occlusion sırasında kuvvet sıfır olduğu için sonuç sadece başlangıç durumunun ve
yerçekiminin fonksiyonu. Parametreyi tanımlanabilir kılan şey bu.

**Neden model gerekli.** Ortalama hata tek sayıdır ve iki farklı şeyi karıştırır.
Bias küçüldüyse kişi sistemin fiziğini öğrenmiştir. Sadece gürültü küçüldüyse kişi
göreve alışmıştır ama iç modeli değişmemiştir. İkisi de aynı ortalama hata düşüşünü
üretir.

**Bilinen risk: iki parametre birbirine karışabilir.** Çok gürültülü bir kişinin
cevapları dağıldığı için, sanki küçük bir yerçekimi varsayıyormuş gibi görünebilir.
Likelihood yüzeyinin bu iki parametreyi gerçekten ayırıp ayırmadığı simülasyonla
kontrol edilecek (aşağıda).

**Açık risk: uyaranların yerçekimi.** Uyaranlar hangi yerçekiminden kesildiyse o
dünyada yaşamış grup avantajlı olur. Hepsi 3.5'ten kesilirse sabit grup bütün
seansı orada geçirmiş olur. Çözüm uyaranların aralığa yayılması, ve bunun ayrıca
bir kazancı var: kişinin iç modelinin sadece son gördüğü yerçekiminde mi yoksa
bütün aralıkta mı doğru olduğu ölçülebilir hale geliyor. Ludolph'un yapamadığı şey bu.

Uyaran yerçekimi tek bir değerde sabit kalsa bile içsel yerçekimi yine tahmin
edilebilir, çünkü uyaranlar farklı başlangıç açısı ve hızıyla başlıyor ve o
çeşitlilik parametreyi belirlemeye yetiyor. Aralığa yaymak bunu güçlendiriyor ve
confound'u kaldırıyor, ama olmazsa olmaz değil.

**Çıktı.** Her (kişi × blok) için iki sayı: içsel yerçekimi ve tepki gürültüsü.

**Not.** Ludolph aynı iskeleti farklı parametrelendirmiş. Yerçekimini manipüle
edemediği için "iç model kaç milisaniye doğru kalıyor" parametresini fit etmiş.
Aynı iskeletle o da fit edilip karşılaştırılabilir.

---

### E. İki bağımsız içsel yerçekimi ölçümünün karşılaştırılması

**Amaç.** Kişinin kafasındaki yerçekimi iki ayrı yerden ölçülüyor. Aynı çıkıyorlar mı.

**Hangi veri.** D'nin çıktısı (algısal ölçüm) ve A ile mevcut action timing
kodundan türetilen motor ölçüm.

**Neden bu en iddialı madde.** İki ölçüm birbirinden tamamen bağımsız. Biri algısal
bir görevden, diğeri motor davranıştan geliyor. Kişiler arasında birbirini
tutuyorlarsa, motor öğrenmeyle algısal iç modelin aynı temsili paylaştığını
göstermiş oluyoruz. Ludolph bunu tartışıyor ama gösteremiyor, çünkü iki deneyi
ayrı yürütmüş ve motor grubu 335 gün önce eğitilmiş.

**İki ciddi zayıflık, ikisi de baştan kabul edilmeli.**

Motor taraftaki yerçekimi tahmini iyi tanımlı değil. Kişinin erken kuvvet uygulaması
ya iyi bir iç modelden gelir ya da temkinli olmasından. Yani motor ölçüm,
politikanın ne kadar agresif olduğuyla karışıyor. Bu, algısal taraf için geçerli
değil, orada kişinin davranışı doğru cevabı etkilemiyor.

İki ölçüm de gürültülüyse aralarındaki korelasyon sönümlenir. 40 kişide, iki
eksende de gürültü varken, gerçek ilişki büyük olmadıkça bulunamaz. Ve null sonuç
hiçbir şey söylemez, çünkü "ilişki yok" ile "ölçemedim" ayrılmaz.

**Güvenilirlik kapısı.** E çalıştırılmadan önce iki ölçümün de split-half
güvenilirliği hesaplanacak. Güvenilirlik düşükse E yapılmayacak ve rapor edilmeyecek.
Bu bir ön koşul, sonradan bulunacak bir bahane değil. Güvenilirlik yeterliyse
korelasyon sönümlenmeye göre düzeltilerek raporlanacak.

**Risk yönetimi.** E tutmazsa diğer altı analiz etkilenmiyor, hepsi kendi başına
ayakta.

---

### F. Öğrenme eğrileri

**Amaç.** Öğrenmeyi iki noktanın farkı yerine eğri olarak ölçmek.

**Hangi veri.** `trial_summary`, trial sırasına göre.

**Yöntem.** Kişi başına üstel ya da güç yasası eğrisi, hierarchical model içinde.

**Çıktı.** Kişi başına üç parametre: başlangıç seviyesi, öğrenme hızı, asimptot.
Grup farkı ortalamada değil bu parametrelerde aranıyor.

**Neden model gerekli.** İki kişi aynı son performansa farklı yollardan varabilir.
Biri hızlı öğrenip platoya oturur, diğeri yavaş ama sürekli ilerler. Ortalama eğri
ikisini aynı gösterir. Ayrıca eğri parametresi, öncesi-sonrası farkından daha az
gürültülü bir sayı.

**Uyarı.** Gradual grupta yerçekimi zamanla arttığı için ham performans eğrisi
öğrenme ile artan zorluğun toplamı. İki etki ayrılmadan grup karşılaştırması
yapılamaz. Ludolph bunu normalize ederek çözmüş, biz de yerçekimini eğri modeline
açık bir terim olarak koyacağız.

---

### G. Değişkenlik ayrıştırması

**Amaç.** Motor variability'yi ham standart sapmadan daha temiz ölçmek.

**Hangi veri.** A'nın artıkları.

**Yöntem.** Input varyansını üçe ayır: state'in açıkladığı kısım, bağlamın
açıkladığı kısım, artık. Artık kısım motor gürültü.

**Neden model gerekli.** Ham değişkenlik, kişinin ne kadar zorlandığıyla karışıyor.
Zor durumda herkes çok hareket eder. Modelin açıkladığı kısmı çıkardıktan sonra
kalan, gerçekten gürültü olan kısım.

**İkincil soru, keşifsel.** Erken bloklardaki artık değişkenlik, o kişinin sonraki
öğrenme hızını yorduyor mu. Wu ve arkadaşlarının 2014 iddiası bu. Ama 40 kişide,
iki gürültülü kişi düzeyi tahmini arasında korelasyon arıyoruz ve üçüncü değişken
riski yüksek: beceri, motivasyon, uyanıklık. Bir şey çıkarsa iddia olarak değil,
gözlem olarak yazılacak.

**Bağlı istek.** `stick_raw`. Deadzone küçük hareketleri sildiği için mevcut
kolonlarla bu analiz yapılamıyor.

---

## Veri gelmeden yapılacak iş: simülasyonla güç hesabı

D ve E'nin yapılabilirliği tamamen occlusion deneme sayısına bağlı ve bu sayı henüz
belli değil.

Ludolph blok başına 40 deneme, 11 blok kullanmış ve bulduğu grup farkı 5.3 derece.
Yanıt çözünürlüğü 10.8 derece, yani etki yarım seçenek adımı. Deneme sayısı yetersiz
olursa kişi başına yerçekimi tahmini gürültüden ibaret olur ve E kendiliğinden ölür.

Bu, veri beklemeden cevaplanabilecek bir soru. Fizik kodu elimizde. Yapılacak iş:

1. Ludolph'unkine benzer bir uyaran kümesi üret, başlangıç açısı ve hızı çeşitli olsun.
2. Bilinen bir içsel yerçekimi ve bilinen bir tepki gürültüsüyle sahte katılımcılar üret.
3. Bu sahte veriden parametreleri geri tahmin et.
4. Deneme sayısını değiştirerek tahminin ne kadar hassas olduğunu ölç.

Çıktı iki şey: kişi başına gereken asgari deneme sayısı, ve iki parametrenin
birbirine karışıp karışmadığı. Birincisi ekibe verilebilecek somut bir sayı,
ikincisi D'nin geçerliliğinin ön koşulu.

---

## Hangi kolon hangi analiz için

| Kolon | Analizler | Olmazsa ne olur |
|---|---|---|
| `gravity` (trial_summary) | A, B, C, F | Politikanın hangi yerçekiminde ölçüldüğü bilinmez. Öğrenme ile artan zorluk ayrılamaz |
| `trial_success` | C | Adımların başarıyla tetiklenmesinden doğan confound düzeltilemez. C'nin geçerliliği buna bağlı |
| `block_id`, `phase_label` | A, C, D, F | Hangi trial'ın hangi aşamaya ait olduğu bilinmez |
| `stick_raw` | A, B, E, G | Küçük hareketler kayıp. G tamamen ölür, A zayıflar |
| `log_schema_version` | hepsi | Toplama sırasında format değişirse fark edilmez |
| `occlusion_responses.csv` | D, E | Prediction ölçümü hiç yapılamaz |
| `frame_time_s`, `render_frame_count` | A, E | Gecikme tahmini yanlı olur ve ne kadar olduğu bilinemez |
| `gravity_current` (timeseries) | doğrulama | Trial düzeyi yerçekimi yanlış yazılırsa yakalanamaz |
| `session_time_s` | C, D | Dengeleme ve occlusion tek zaman çizgisine dizilemez |
| `probe_config` (seçenek listesi) | D | Seçeneklerin eşit aralıklı olduğu varsayılmak zorunda kalınır |
| `input_pipeline` | A, G | `stick_raw` ile uygulanan değer arasındaki dönüşüm yeniden üretilemez |
| `occlusion_stimuli.csv` | D | Gözlem fazı modellenemez. Asıl hesap yine yapılabilir |

---

## Sıra

1. Simülasyonla güç hesabı. Veri beklemez, bu hafta yapılabilir.
2. A, çünkü B, E ve G onun üstüne kuruluyor.
3. F ve C, birbirinden bağımsız, veri gelir gelmez yapılabilir.
4. D, occlusion dosyaları gelince. A'ya bağlı değil.
5. B, A bittikten sonra.
6. G, A'nın artıkları hazır olunca.
7. E en son, ve ancak güvenilirlik kapısını geçerse.

---

## Hesap maliyeti

GPU gerekmiyor.

40 kişi, kişi başına birkaç yüz trial, 60 Hz. Toplam 10 ile 20 milyon satır arası.
float32 parquet olarak 0.5 ile 1.5 GB. Kişi kişi işlenince RAM sorunu olmuyor.

Ridge fitleri milisaniye. Gecikme taraması birkaç dakika. LightGBM kişi başına
birkaç saniye. Transfer matrisi dakikalar. Occlusion fitleri küçük veri, saniyeler.

Asıl maliyet bootstrap. Güven aralıkları blok düzeyinde bootstrap ile üretiliyor ve
500 ile 1000 tekrar her şeyi o kadar çarpıyor. Çözüm, bootstrap'ı sadece nihai
büyüklüklere uygulamak ve çekirdeklere paralelleştirmek. En kötü senaryo bir gece
çalışan bir iş.

---

## Bu planın dışında bıraktıklarım

- Koşul etiketini tahmin eden derin ağ.
- Katılımcıları strateji kümelerine ayıran unsupervised clustering.
- Performansı zamandan tahmin eden sequence modeli.
- Yerçekimini state'ten decode eden model. Bu artık ayrı bir analiz değil, A'nın
  içinde bir kontrol. Sebebi yukarıda A'da yazıyor.

---

## Kaynaklar

- Ludolph N, Giese MA, Ilg W (2017). Interacting Learning Processes during Skill
  Acquisition. *Scientific Reports* 7:13191.
- Ludolph N, Plöger J, Giese MA, Ilg W (2017). Motor expertise facilitates the
  accuracy of state extrapolation in perception. *PLOS ONE* 12(11):e0187666.
- Wu HG, Miyamoto YR, Gonzalez Castro LN, Ölveczky BP, Smith MA (2014). Temporal
  structure of motor variability is dynamically regulated and predicts motor
  learning ability. *Nature Neuroscience* 17:312-321.
