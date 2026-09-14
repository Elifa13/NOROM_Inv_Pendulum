# GAP: Modelleme Planı

rev 4, 2026-09-09. Random force kolu bu belgenin dışında.

Bu belge benim çalışma planım. Toplantıya giren belge
[01_Kayit_Istekleri.md](01_Kayit_Istekleri.md). Buradaki her analiz, oradaki
bir kayıt isteğinin gerekçesi. Tasarımın tamamı [00_Tasarim.md](00_Tasarim.md).

**Rev 3'te değişenler.** Yerçekimi artışı sabit takvime bağlandığı için C
analizindeki regression to the mean tartışması gereksizleşti. Buna karşılık
occlusion deneme sayısı belli oldu ve az: kişi başına 80, Ludolph'ta 440. D ve
E analizlerinin kişi düzeyinde yapılabilirliği açık bir soru haline geldi ve
simülasyonla güç hesabı önceliğe çıktı.

**Rev 4'te değişenler.** Kontrol grubunun bütün seans boyunca g = 1.0'da
kaldığı netleşti. Bu, planın çerçevesini değiştiriyor. Gruplar arası
karşılaştırma artık "aynı zorlukta kim daha iyi" değil, "aynı iki noktada kim
ne kadar kaydı". Bütün ana analizler difference-in-differences şeklinde
yeniden kuruldu. Occlusion uyaranlarının hepsinin g = 1.0 olduğu kesinleşti ve
bu, korktuğum confound'u hipotezin aleyhine çevirdiği için sorun olmaktan
çıktı.

---

## Neden model kuruyoruz

Ölçmek istediğimiz üç şeyin hiçbiri doğrudan gözlenmiyor.

Kişinin ne kadar öğrendiği gözlenmiyor, performansı gözleniyor.
Kişinin kafasındaki yerçekimi gözlenmiyor, verdiği kuvvet gözleniyor.
Kişinin iç modeli gözlenmiyor, tahmini gözleniyor.

Üçü de latent değişken. Gözlenen davranıştan geri çıkarılmaları gerekiyor. Bu
bir system identification problemi ve trial ortalamalarıyla çözülmüyor.

---

## Bütün analizler için geçerli üç kural

**Gruplar sadece g = 1.0'da karşılaştırılır.** Kontrol grubu bütün seansı
1.0'da geçiriyor, gradual grup ise sadece aşama 1, 2, 3 ve 8'de orada. Geri
kalan her yerde iki grup farklı yerçekimlerinde farklı görevler yapıyor ve
aradaki performans farkı öğrenme farkı değil, zorluk farkı. Yani gruplar arası
her karşılaştırma bu dört aşamada kurulur.

Bunun doğal sonucu, ana analizlerin difference-in-differences olması. Gradual
grubun aşama 8 eksi aşama 2 farkı iki şey içeriyor: aftereffect, artı seans
boyunca pratik yapmaktan gelen genel iyileşme. Kontrol grubu aynı iki noktayı
hiç adaptasyon yaşamadan veriyor, yani o genel iyileşmenin ölçüsü. İki farkın
farkı saf aftereffect. Aynı yapı algısal tarafta da geçerli: post-test eksi
pre-test, gradual grupta kontrol grubundakinden farklı mı.

**Bu tasarım Ludolph'un sorusunu soramaz.** Onun sabit kolu 3.5'teydi ve iki
grup aynı zorlukta bitiyordu, o yüzden "kademeli eğitim daha iyi mi"
sorulabiliyordu. Burada öyle bir nokta yok. Rapor yazılırken bu iddia
kurulmayacak.

**Sabit grupta yerçekimi adımı yok.** Adıma dayanan analizlerin (B ve C)
örneklemi tek gruptur, gradual grup. Kontrol grubu orada yok.

**Occlusion tarafında asıl büyüklük kişi içi değişimdir.** İki ölçüm noktamız
var, aynı kişide, aynı uyaranlarla. Kişi içi fark, kişi düzeyi gürültüyü
(genel dikkat, görev anlayışı, temel yanlılık) siliyor. Ludolph bunu
yapamamış, çünkü onun motor grubu 335 gün önce eğitilmişti ve tek ölçüm
noktası vardı. Bu, az deneme sayısının bir kısmını telafi eden şey.

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
`gravity_step_index` ve `phase_label`. Zamanlama için `frame_time_s` ve
`render_frame_count`.

**Yöntem.** İki aşamalı model, çünkü input dağılımı yığılmalı. Pilotta
örneklerin %73.9'u tam sıfır. Düz regression bu veride sürekli sıfıra yakın
tahmin eder ve hiçbir şey öğrenmez.

1. Müdahale var mı yok mu. Binary sınıflandırma.
2. Varsa ne kadar ve hangi işarette. Regression.

Gecikme varsayılmaz, fit edilir. State t eksi d anından okunuyor, d 0 ile 400 ms
arasında taranıp held-out likelihood'u maksimize eden seçiliyor. d'nin kendisi
de bir sonuç.

Model merdiveni: ridge, sonra LightGBM, gerekirse küçük bir MLP. Her basamağa
çıkmak için held-out kazancın gerçek olması şart.

**Bölümleme, rev 3'te sadeleşti.** Rev 2'de "adım başına çok az trial düşebilir,
fit oturmaz" diye adımları birleştirmeyi planlamıştım. Bu endişe geçersiz:
tasarım dengeli, her adımda tam 8 trial var ve hepsi 20 saniye. Adım başına
8 x 20 x 60 = 9.600 örnek düşüyor, ridge fit için fazlasıyla yeterli. Yani
politika **adım adım** fit edilebilir, on ayrı fit. Aralık birleştirmek
gerekirse bu bir sadeleştirme tercihi olur, zorunluluk değil.

**Kritik metodolojik nokta.** 60 Hz'de ardışık örnekler birbirinin neredeyse
kopyası. Cross-validation asla rastgele sample bölerek yapılmaz, hep trial ya da
blok bloğu ayrılır. Aksi halde her şey anlamlı çıkar ve hepsi sahtedir.

Analiz ikinci bir birimde de tekrarlanacak: input event. Onset anındaki state
girdi, o event'in genliği ve süresi çıktı. Bu, otokorelasyon problemini kökünden
çözüyor. Sample modeli detay için, event modeli karar için.

**İç kontrol.** Politikanın gerçekten değiştiğini doğrulamak için, sadece
kişinin inputundan yerçekimini tahmin etmeye çalışacağız. Buradaki incelik
önemli: modele state verilmez. Verilirse model yerçekimini kişinin
davranışından değil doğrudan fizikten okur, çünkü pole'un ivmesi zaten
yerçekiminin fonksiyonu. O zaman ölçtüğün şey bir fizik dedektörü olur, insanla
ilgisi kalmaz. Bu yüzden bu bir kontrol, ayrı bir bulgu değil.

**Çıktı.** Her (kişi × adım) için gain vektörü, gecikme, held-out skor.

**Bağlı istekler.** `gravity`, `gravity_step_index`, `stick_raw`,
`frame_time_s`, `render_frame_count`.

---

### B. Politika kayması

**Amaç.** Adaptation hızını, hiçbir parametreyi yorumlamadan ölçmek.

**Hangi veri.** A'nın fit edilmiş modelleri.

**Yöntem.** Adım k'de fit edilen modeli adım j'nin verisinde test et. Bütün
çiftler için yap. On adım varsa 10 x 10'luk bir kayıp matrisi çıkıyor.
Köşegenden uzaklaştıkça bozulmanın hızı, politikanın ne kadar hızlı
değiştiğini veriyor.

**Çıktı.** Kişi başına bir matris ve ondan türeyen tek bir kayma hızı sayısı.

**Neden model gerekli.** Fonksiyonel form varsayımı yok. "Gain arttı mı"
tartışmasına girmeden politikanın değiştiğini gösteriyor.

**Örneklem.** Sadece gradual grup.

---

### C. Yerçekimi adımlarına tepki

**Amaç.** Yerçekimi her arttığında yaşanan bozulmayı ve toparlanmayı ölçmek.

**Hangi veri.** `trial_summary` performans metrikleri, A'nın gecikme çıktısı,
`gravity_step_index`, `trial_index_in_step`. Başarı ölçütü kayıttan gelmiyor,
`fall_event` üstünden kendimiz tanımlıyoruz (pilottaki gibi: düşüş sayısı ve
`falls_angle_per_trial`).

**Rev 2'deki sorun ortadan kalktı.** Ludolph'ta yerçekimi başarılı bir
trial'dan sonra artıyor, yani adım rastgele gelmiyor, iyi performansın ardından
geliyor. Adım sonrası düşüşün ne kadarı yerçekiminden ne kadarı regression to
the mean'den, ayrılmıyor. Ludolph bunu ele almamış ve rev 2'de bunu düzeltmek
için sabit grubu kontrol olarak kullanmayı planlamıştım. Bu tasarımda artış
sabit takvimle olduğu için sorun yok: adım, performanstan bağımsız olarak
her sekiz trial'da bir geliyor. Adım sonrası bozulma doğrudan yorumlanabilir.

**Yöntem.** Ludolph'un tanımı doğrudan uygulanabiliyor. Her adım için ilk üç
trial (`trial_index_in_step` 1-3) ve son üç trial (6-8) ortalanıyor. Adım içi
iyileşme son üçlü eksi ilk üçlü, adımlar arası bozulma bir sonraki adımın ilk
üçlüsü eksi bu adımın son üçlüsü. Aynı hesap trial uzunluğu, action timing ve
action variability için ayrı ayrı yapılıyor.

Adım başına trial sayısı az olduğu için tek tek adım fitleri gürültülü olur.
Hierarchical model kullanılacak, yani her adımın eğrisi kişinin ve grubun
ortalamasından ödünç alıyor.

**Çıktı.** Her (kişi × adım) için bozulmanın büyüklüğü ve toparlanma zaman
sabiti.

**Asıl soru.** Zaman sabiti adımlar ilerledikçe küçülüyor mu. Yani kişi sadece
görevi değil, uyum sağlamayı da öğreniyor mu.

**Güç konusunda dürüst olalım, ve aritmetik değişti.** Ludolph'ta kişi başına
25 adım vardı ve her adım 0.1 m/s². Bizde 10 adım var ve her adım 0.25 m/s².
İki değişiklik ters yönde çalışıyor: adımlar iki buçuk kat büyüdüğü için adım
başına beklenen etki büyüyor, ama ortalanacak adım sayısı yarıdan aza indi.
Ludolph'un kendi verisinde tek tek adımların etkisi gürültülüydü ve sadece
ortalamada anlamlı çıkıyordu, hatta variability etkisi için ilk üç adımı atmak
zorunda kalmışlardı. Bizde adımların büyük olması bunu kolaylaştırabilir ama
10 adım üstünden ortalama almak, 25 adım üstünden ortalama almaktan daha
gürültülüdür. Net etkinin yönü belli değil, simülasyonla bakılacak.

Doğru ifade şu: tekrarlı within-subject olaylar mixed model'e iki noktanın
farkından çok daha fazla dayanak veriyor. Ama bunlara bağımsız tekrarmış gibi
davranan bir analiz yanlış olur.

**Örneklem.** Gradual grup. Kontrol grubu bu analizde yok, çünkü onda adım yok.

**Motor aftereffect ayrı bir madde değil, C'nin devamı.** Aşama 8 g = 1.0'da ve
aftereffect ilk trial'larda en büyük, sonrakilerde sönüyor. Yani 8 tek bir
ortalama değil, bir sönme eğrisi ve C'nin adım içi toparlanma eğrisiyle aynı
matematiksel biçimde. Aynı hierarchical modelle fit edilecek, tek fark
perturbasyonun işareti. Karşılaştırma noktası aşama 2, düzeltme kontrol
grubunun aynı iki noktası.

---

### D. Occlusion hatasının ayrıştırılması ve içsel yerçekimi

**Amaç.** Occlusion testindeki hatanın neden değiştiğini bulmak, ve kişinin
kafasındaki yerçekimini bir sayıya çevirmek.

**Hangi veri.** `occlusion_responses.csv`, özellikle `onset_` kolonları ve
`stimulus_gravity`. `occlusion_stimuli.csv` varsa gözlem fazı da modellenebilir.

Occlusion testi ayrı bir blok. Denek oynamıyor, başkalarının kayıtlarını
izliyor, uyaranlar herkeste ortak. İkisi de analiz açısından iyi haber: kişinin
kendi davranışı doğru cevabı etkilemiyor, ve kişiler arası karşılaştırma aynı
uyaranlar üstünden yapılıyor.

**Yöntem.** Her deneme için:

1. Uyaranın gizlenme anındaki durumundan başla.
2. Varsayılan bir yerçekimi değeriyle, sıfır kuvvet altında, occlusion süresi
   kadar ileri simüle et. Bu bizim `src/physics.py` içindeki RK4 ile birebir
   aynı hesap.
3. Elde edilen açıyı en yakın yanıt seçeneğine yuvarla.
4. Gözlenen cevapla karşılaştır.

İki serbest parametre maximum likelihood ile bulunuyor: kişinin varsaydığı
yerçekimi, ve cevabındaki gürültünün büyüklüğü. Occlusion sırasında kuvvet
sıfır olduğu için sonuç sadece başlangıç durumunun ve yerçekiminin fonksiyonu.
Parametreyi tanımlanabilir kılan şey bu.

**Neden model gerekli.** Ortalama hata tek sayıdır ve iki farklı şeyi
karıştırır. Bias küçüldüyse kişi sistemin fiziğini öğrenmiştir. Sadece gürültü
küçüldüyse kişi göreve alışmıştır ama iç modeli değişmemiştir. İkisi de aynı
ortalama hata düşüşünü üretir.

**Asıl kısıt, rev 3'ün en önemli maddesi.** Kişi başına 2 blok x 40 = 80
occlusion denemesi var. Ludolph 11 blok x 40 = 440 kullanmış ve bulduğu grup
farkı 5.3 derece, yanıt çözünürlüğü ise 10.8 derece. Yani etki yarım seçenek
adımı büyüklüğünde ve ancak çok sayıda deneme üstünden ortalanınca görünür hale
geliyor. Bizde blok başına 40 deneme aynı ama blok sayısı beşte bir.

Bu, D'yi tamamen öldürmez ama ölçeğini belirler. Üç senaryo var ve hangisinin
geçerli olduğunu simülasyon söyleyecek:

| Senaryo | Ne yapılabilir |
|---|---|
| 40 deneme kişi başına parametre için yeterli | D ve E tam haliyle yapılır |
| 40 yetmez ama 80 yeter | Parametre kişi başına tek sefer (iki blok birleştirilerek) tahmin edilir. Pre-post değişimi kişi düzeyinde ölçülemez, sadece grup düzeyinde |
| 80 de yetmez | Parametre yalnızca grup düzeyinde hierarchical modelle tahmin edilir. E analizi düşer |

İki parametrenin birbirine karışma riski de burada: çok gürültülü bir kişinin
cevapları dağıldığı için sanki küçük bir yerçekimi varsayıyormuş gibi
görünebilir. Likelihood yüzeyinin bu ikisini gerçekten ayırıp ayırmadığı aynı
simülasyonla kontrol edilecek.

**Uyaranların yerçekimi: karar verildi ve lehimize.** Bütün uyaranlar pilotun
no-noise trial'larından kesiliyor, hepsi g = 1.0. Yani test dünyası kontrol
grubunun dünyası. Uyaranlar 3.5'ten kesilseydi confound hipotezin lehine
çalışırdı, çünkü beklediğimiz sonuç gradual grubun kayması ve o grup teste
yakın yaşamış olurdu. Bu haliyle tersi: gradual grup uzaklaşan taraf, bulunacak
etki ev sahibi avantajına rağmen bulunmuş oluyor.

Tek bir yerçekiminde kalmak içsel yerçekimi tahminini engellemiyor. Uyaranlar
farklı başlangıç açısı ve hızıyla başlıyor ve o çeşitlilik parametreyi
belirlemeye yetiyor. Kaybettiğimiz şey, kişinin iç modelinin bütün aralıkta mı
yoksa sadece bir noktada mı doğru olduğunu görebilmek. Bu, aralığa yayılmış
uyaranlarla mümkün olurdu ama tasarım kararı verildi.

**Yorumun yönü ters döndü, bu yazılırken unutulmamalı.** İki grup da düşük
yerçekiminde test ediliyor, gradual grup ise yüksek yerçekimine uyum sağlamış
halde geliyor. İç modeli yükselen kişi g = 1.0'daki düşüşü olduğundan hızlı
tahmin eder. Yani gradual grupta beklenen şey "daha isabetli tahmin" değil,
"yukarı kaymış tahmin". Bu algısal bir aftereffect.

Burada bir tuzak var. Ludolph'ta herkes düşüşü sistematik olarak az tahmin
ediyor, ortalama hata negatif. İç modelin yukarı kayması hatayı pozitif yöne,
yani sıfıra doğru iter. Göreve alışıp gerçekten iyileşmek de aynı yöne iter.
Ortalama hataya bakarak ikisi ayrılmıyor. Ayrılmalarının tek yolu iki
parametreli fit: içsel yerçekimi 1.0'ın altından 1.0'a gelirse bu iyileşme,
1.0'ı geçip yukarı çıkarsa bu aftereffect. D'nin model kurma gerekçesi asıl
burada.

**Çıktı.** Her (kişi × blok) için iki sayı: içsel yerçekimi ve tepki gürültüsü.
Asıl ilgilendiğim büyüklük ikisi arasındaki fark, yani pre'den post'a değişim.

**Not.** Ludolph aynı iskeleti farklı parametrelendirmiş. Yerçekimini manipüle
edemediği için "iç model kaç milisaniye doğru kalıyor" parametresini fit etmiş.
Aynı iskeletle o da fit edilip karşılaştırılabilir.

---

### E. İki bağımsız içsel yerçekimi ölçümünün karşılaştırılması

**Amaç.** Kişinin kafasındaki yerçekimi iki ayrı yerden ölçülüyor. Aynı
çıkıyorlar mı.

**Hangi veri.** D'nin çıktısı (algısal ölçüm) ve A ile mevcut action timing
kodundan türetilen motor ölçüm.

**Neden bu en iddialı madde.** İki ölçüm birbirinden tamamen bağımsız. Biri
algısal bir görevden, diğeri motor davranıştan geliyor. Kişiler arasında
birbirini tutuyorlarsa, motor öğrenmeyle algısal iç modelin aynı temsili
paylaştığını göstermiş oluyoruz. Ludolph bunu tartışıyor ama gösteremiyor,
çünkü iki deneyi ayrı yürütmüş ve motor grubu 335 gün önce eğitilmiş.

**Üç zayıflık, üçü de baştan kabul edilmeli.**

Motor taraftaki yerçekimi tahmini iyi tanımlı değil. Kişinin erken kuvvet
uygulaması ya iyi bir iç modelden gelir ya da temkinli olmasından. Yani motor
ölçüm, politikanın ne kadar agresif olduğuyla karışıyor. Bu, algısal taraf için
geçerli değil, orada kişinin davranışı doğru cevabı etkilemiyor.

İki ölçüm de gürültülüyse aralarındaki korelasyon sönümlenir. İki eksende de
gürültü varken, gerçek ilişki büyük olmadıkça bulunamaz. Ve null sonuç hiçbir
şey söylemez, çünkü "ilişki yok" ile "ölçemedim" ayrılmaz.

Üçüncüsü rev 3'te eklendi: algısal ölçümün dayandığı deneme sayısı Ludolph'un
beşte biri. D'nin senaryo tablosunda üçüncü satır çıkarsa E kendiliğinden
düşer.

**Tasarımın kaçırdığı fırsat.** İki aftereffect'in aynı temsili paylaştığını
göstermenin en doğrudan yolu, ikisinin birlikte sönüp sönmediğine bakmaktı.
Bunun için washout'tan sonra kısa bir prediction bloğu daha gerekirdi. Şu anki
tasarımda yok, yani soruyu kişi içi bir kontrastla soramıyoruz ve E'nin zayıf
yoluna, kişiler arası korelasyona mahkumuz. Bu, E'nin raporda ne kadar iddialı
yazılabileceğinin sınırını belirliyor.

**Güvenilirlik kapısı.** E çalıştırılmadan önce iki ölçümün de split-half
güvenilirliği hesaplanacak. Güvenilirlik düşükse E yapılmayacak ve rapor
edilmeyecek. Bu bir ön koşul, sonradan bulunacak bir bahane değil. Güvenilirlik
yeterliyse korelasyon sönümlenmeye göre düzeltilerek raporlanacak.

**Risk yönetimi.** E tutmazsa diğer altı analiz etkilenmiyor, hepsi kendi
başına ayakta.

---

### F. Öğrenme eğrileri

**Amaç.** Öğrenmeyi iki noktanın farkı yerine eğri olarak ölçmek.

**Hangi veri.** `trial_summary`, trial sırasına göre.

**Yöntem.** Kişi başına üstel ya da güç yasası eğrisi, hierarchical model
içinde.

**Çıktı.** Kişi başına üç parametre: başlangıç seviyesi, öğrenme hızı,
asimptot. Grup farkı ortalamada değil bu parametrelerde aranıyor.

**Neden model gerekli.** İki kişi aynı son performansa farklı yollardan
varabilir. Biri hızlı öğrenip platoya oturur, diğeri yavaş ama sürekli ilerler.
Ortalama eğri ikisini aynı gösterir. Ayrıca eğri parametresi, öncesi-sonrası
farkından daha az gürültülü bir sayı.

**Uyarı, rev 3'te kolaylaştı.** Gradual grupta yerçekimi zamanla arttığı için
ham performans eğrisi öğrenme ile artan zorluğun toplamı. İki etki ayrılmadan
grup karşılaştırması yapılamaz. Ludolph bunu normalize ederek çözmüş. Bizde
yerçekimi bilinen, sabit ve bütün katılımcılarda aynı bir zaman fonksiyonu
olduğu için modele açık bir terim olarak konması doğrudan mümkün. Ludolph'ta
her kişinin kendi yerçekimi profili vardı, bizde tek bir profil var.

---

### G. Değişkenlik ayrıştırması

**Amaç.** Motor variability'yi ham standart sapmadan daha temiz ölçmek.

**Hangi veri.** A'nın artıkları.

**Yöntem.** Input varyansını üçe ayır: state'in açıkladığı kısım, bağlamın
açıkladığı kısım, artık. Artık kısım motor gürültü.

**Neden model gerekli.** Ham değişkenlik, kişinin ne kadar zorlandığıyla
karışıyor. Zor durumda herkes çok hareket eder. Modelin açıkladığı kısmı
çıkardıktan sonra kalan, gerçekten gürültü olan kısım.

**İkincil soru, keşifsel.** Erken adımlardaki artık değişkenlik, o kişinin
sonraki öğrenme hızını yorduyor mu. Wu ve arkadaşlarının 2014 iddiası bu. Ama
iki gürültülü kişi düzeyi tahmini arasında korelasyon arıyoruz ve üçüncü
değişken riski yüksek: beceri, motivasyon, uyanıklık. Bir şey çıkarsa iddia
olarak değil, gözlem olarak yazılacak.

**Bağlı istek.** `stick_raw`. Deadzone küçük hareketleri sildiği için mevcut
kolonlarla bu analiz yapılamıyor.

---

## Veri gelmeden yapılacak iş: simülasyonla güç hesabı

Rev 2'de bu "yapılsa iyi olur" işiydi. Rev 3'te D ve E'nin yapılıp
yapılamayacağını belirleyen ön koşul. Deneme sayısı artık belli ve az.

Fizik kodu elimizde. Yapılacak iş:

1. Ludolph'unkine benzer bir uyaran kümesi üret, başlangıç açısı ve hızı
   çeşitli olsun. Uyaran yerçekimi için iki senaryo kur: hepsi 3.5, ve aralığa
   yayılmış.
2. Bilinen bir içsel yerçekimi ve bilinen bir tepki gürültüsüyle sahte
   katılımcılar üret.
3. Bu sahte veriden parametreleri geri tahmin et.
4. Deneme sayısını 20, 40, 80 ve 440'ta ayrı ayrı dene.

Çıktı üç şey. Kişi başına parametre tahmininin 40 ve 80 denemede ne kadar
hassas olduğu, iki parametrenin birbirine karışıp karışmadığı, ve uyaranların
aralığa yayılmasının tahmini ne kadar iyileştirdiği. Üçü de ekibe verilebilecek
somut sayılar ve üçü de D'nin senaryo tablosundan hangisinin geçerli olduğunu
söylüyor.

Aynı simülasyon C için de kurulacak: 10 adım x 0.25 ile 25 adım x 0.1'in adım
etkisini yakalama gücü karşılaştırılacak.

---

## Hangi kolon hangi analiz için

| Kolon | Analizler | Olmazsa ne olur |
|---|---|---|
| `gravity` (trial_summary) | A, B, C, F | Politikanın hangi yerçekiminde ölçüldüğü bilinmez. Öğrenme ile artan zorluk ayrılamaz |
| `phase_label` | A, C, D, F | Hangi trial'ın hangi aşamaya ait olduğu bilinmez. Sekiz aşama birbirinden ayrılamaz |
| `stick_raw` | A, B, E, G | Küçük hareketler kayıp. G tamamen ölür, A zayıflar |
| `log_schema_version` | hepsi | Toplama sırasında format değişirse fark edilmez |
| `occlusion_responses.csv` | D, E | Prediction ölçümü hiç yapılamaz |
| `frame_time_s`, `render_frame_count` | A, E | Gecikme tahmini yanlı olur ve ne kadar olduğu bilinemez |
| `gravity_step_index` | A, B, C | Adım birimi elle yeniden kurulur, hata payı girer |
| `trial_index_in_step` | C | Early/late ayrımı elle kurulur, C'nin ana hesabı bu ayrıma dayanıyor |
| `gravity_current` (timeseries) | doğrulama | Trial düzeyi yerçekimi yanlış yazılırsa yakalanamaz |
| `session_time_s` | C, D | Dengeleme ve occlusion tek zaman çizgisine dizilemez. Aşama 6 ile 7 arasındaki süre bilinemez |
| `probe_config` | D | Seçeneklerin eşit aralıklı olduğu varsayılmak zorunda kalınır |
| `input_pipeline` | A, G | `stick_raw` ile uygulanan değer arasındaki dönüşüm yeniden üretilemez |
| `occlusion_stimuli.csv` | D | Gözlem fazı modellenemez. Az deneme sayısında bu ek bilgi değerli |

---

## Sıra

1. Simülasyonla güç hesabı. Veri beklemez, bu hafta yapılabilir ve D ile E'nin
   kaderini belirliyor.
2. A, çünkü B, E ve G onun üstüne kuruluyor.
3. F ve C, birbirinden bağımsız, veri gelir gelmez yapılabilir.
4. D, occlusion dosyaları gelince. A'ya bağlı değil.
5. B, A bittikten sonra.
6. G, A'nın artıkları hazır olunca.
7. E en son, ve ancak güvenilirlik kapısını geçerse.

---

## Hesap maliyeti

GPU gerekmiyor.

Kişi başına 115 dengeleme trial'ı, 20 saniye, 60 Hz, yani 138.000 satır.
Katılımcı sayısı henüz belirlenmedi; 40 kişilik bir senaryoda toplam 5.5
milyon satır, float32 parquet olarak yarım gigabaytın altı. Kişi kişi
işlenince RAM sorunu olmuyor.

Ridge fitleri milisaniye. Gecikme taraması birkaç dakika. LightGBM kişi başına
birkaç saniye. Transfer matrisi dakikalar. Occlusion fitleri küçük veri,
saniyeler.

Asıl maliyet bootstrap. Güven aralıkları blok düzeyinde bootstrap ile
üretiliyor ve 500 ile 1000 tekrar her şeyi o kadar çarpıyor. Çözüm, bootstrap'ı
sadece nihai büyüklüklere uygulamak ve çekirdeklere paralelleştirmek. En kötü
senaryo bir gece çalışan bir iş.

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
