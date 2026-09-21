# GAP: Deney Tasarımı

**GAP = Gravity Adaptation and Prediction.**
rev 2, 2026-09-09. Kaynak: 2026-09-08 tarihli el yazısı akış notu ve sonraki
netleştirmeler.

Tasarım deney ekibinde, ben değiştiremiyorum. Bu belgenin işi tasarımı
eksiksiz kaydetmek, Ludolph'tan geleni gelmeyenden ayırmak ve henüz
belirlenmemiş olanı açıkça işaretlemek. Kayıt istekleri
[01_Kayit_Istekleri.md](01_Kayit_Istekleri.md), analiz planı
[02_Modelleme_Plani.md](02_Modelleme_Plani.md).

## Soru

Kişi kademeli olarak zorlaşan bir sisteme uyum sağladığında iç modeli
değişiyor mu, ve bu değişim hem motor davranışta hem algısal bir testte
görünüyor mu.

Ölçüm iki bağımsız yerden alınıyor. Motor tarafta kişinin kontrol politikası
ve zamanlaması, algısal tarafta occlusion testindeki tahmin isabeti. İkisi de
aynı latent değişkeni, kişinin varsaydığı yerçekimini ölçmeye çalışıyor.

## Gruplar

| Grup | Yerçekimi | n |
|---|---|---|
| Gradual gravity (GG) | 1.0'dan 3.5'e kademeli, sonra 1.0'a dönüş | belirlenmedi |
| Constant gravity (CG), kontrol | **bütün seans boyunca 1.0** | belirlenmedi |

Kontrol grubu hiçbir aşamada 3.5'i görmüyor. Trial sayıları ve seans uzunluğu
gradual grupla eşit, tek fark yerçekiminin sabit kalması. Yani CG bir zaman ve
pratik kontrolü: aynı süre, aynı deneme sayısı, dinamik değişmiyor.

**Bu, Ludolph'un kontrol grubu değil.** Ludolph'ta sabit kol 3.5'teydi ve iki
grup da aynı zorlukta bitiyordu; sorusu "kademeli eğitim ani eğitimden daha
iyi mi" idi. Buradaki kontrol grubu 1.0'da kalıyor. Sonuçları aşağıda,
"Bu tasarım neyi sorabilir" başlığında.

## Akış

| # | Aşama | Trial | GG | CG |
|---|---|---|---|---|
| 1 | Familiarization | 3 x 20 s | 1.0 | 1.0 |
| 2 | Motor baseline | 8 x 20 s | 1.0 | 1.0 |
| 3 | Prediction pre-test | 40 deneme | uyaranlar 1.0 | aynı |
| 4 | Stepped gradual adaptation | 10 adım x 8 trial x 20 s | 1.0 → 3.5, adım başına +0.25 | 1.0'da aynı sayıda trial |
| 5 | Late adaptation | 8 x 20 s | 3.5'te ekstra alıştırma | 1.0'da 8 trial |
| 6 | Prediction post-test | 40 deneme | uyaranlar 1.0 | aynı |
| 7 | Re-adaptation | 8 x 20 s | 3.5'te hatırlatma | 1.0'da 8 trial |
| 8 | Washout | 8 x 20 s | 1.0, aftereffect | 1.0'da 8 trial |

Toplam 115 dengeleme trial'ı ve 80 occlusion denemesi. Trial sayıları iki
grupta birebir aynı, tek fark yerçekimi.

### 2. Motor baseline

Sekiz trial'ın altısı, yani 6 x 20 = 120 saniyesi action timing için analiz
penceresi olarak ayrılıyor. Bu bir kayıt ayarı değil, analiz kararı: Ludolph'un
action timing ölçütü olayları iki dakikalık pencerede havuzluyor
([Duzenek/05_Action_Timing.md](../Duzenek/05_Action_Timing.md)).

Olay sayısı yeterli. Pilot g = 1.0'da toplandı ve 12 katılımcıda 91.165 durum
olayı çıktı, yani kişi başına saniyede yaklaşık yedi buçuk olay. 120 saniyelik
pencere bu ölçüt için yeterli malzeme veriyor.

Bu aşama aftereffect'in karşılaştırma noktası. Aşama 8 buna göre okunuyor,
ikisi de g = 1.0'da ve aynı kişide.

### 3 ve 6. Prediction testi

Ludolph'un PLOS ONE prosedürünün aynısı. Tek deneme şöyle işliyor:

1. 4.5 saniye gözlem. Başka birinin balancing kaydından kesilmiş sekans
   oynatılıyor, uygulanan kuvvet kırmızı okla gösteriliyor.
2. Kuvvet sıfıra çekiliyor ve sistem 1 saniye daha simüle ediliyor. Pole ilk
   100 ms görünür kalıyor.
3. Kalan 900 ms boyunca pole gizli, cart görünür. Kuvvet sıfır olduğu için
   sonuç yalnızca gizlenme anındaki duruma ve yerçekimine bağlı.
4. Yanıt. [-65, +65] derece aralığına eşit dağıtılmış 13 seçenekten biri.

Blok başına 40 deneme, kişi başına iki blok (pre ve post), toplam 80 deneme.
Denek oynamıyor, uyaranlar herkeste ortak, tek dosya.

**Uyaranlar pilotun no-noise trial'larından kesiliyor, hepsi g = 1.0.**
Karar verildi. **Doğru cevap gösterilmiyor**, feedback yok. Ludolph'ta doğru
cevabın gösterildiği bloklarda gruplar arası fark tamamen siliniyor, o yüzden
bu şart.

### 4. Stepped gradual adaptation

GG için g = 1.0'dan başlıyor, 3.5'e kadar 0.25'lik adımlarla çıkıyor. On
seviye, her seviyede 8 trial, toplam 80 trial.

**Artış başarıdan bağımsız.** Kişi başarılı olsun olmasın, 8 trial dolunca g
bir kademe artıyor. Ludolph'tan en önemli ayrım bu, sonuçları aşağıda.

Step içi bölümleme: trial 1-3 early, trial 6-8 late. Bu, Ludolph'un her
gravity step'in ilk üçte biri ile son üçte birini karşılaştıran P1,g ve P2,g
tanımının karşılığı.

CG aynı 80 trial'ı g = 1.0'da yapıyor. Onda adım yok, `gravity_step_index`
kolonu yine yazılıyor ki trial'lar eşleştirilebilsin.

### 5, 7 ve 8. Late adaptation, re-adaptation, washout

Aşama 7'nin sebebi aşama 6. Prediction post-test yaklaşık beş dakika sürüyor
ve o süre boyunca kişi hiç dengeleme yapmıyor, adaptasyon kısmen sönüyor.
Re-adaptation 3.5'te bir hatırlatma yapıp washout'u düzgün bir başlangıç
noktasından başlatıyor. Tasarım bu sorunu görmüş ve çözmüş.

Aftereffect aşama 8'in **ilk trial'larında** en büyük ve sonraki trial'larda
sönüyor. Yani 8 tek bir sayı değil, bir sönme eğrisi. Blok ortalaması
aftereffect'i siler çünkü ilk trial ile son trial birbirinin tersi. Bu blok
trial düzeyinde analiz edilecek.

Sekiz trial bu iş için yeterli. Sönme eğrisini görebilmek için sönmenin
tamamlanması gerekiyor; üç dört trial aftereffect'in varlığını gösterir ama
hızını göstermez. Sekiz trial, aşama 4'teki adım uzunluğuyla da aynı, yani
adım içi toparlanma eğrileriyle doğrudan karşılaştırılabiliyor. Aynı
bölümleme burada da geçerli: trial 1-3 early, 6-8 late.

CG için 7 ve 8'in ayrı bir anlamı yok, o grup zaten hiç 1.0'dan çıkmadı.
Oradaki trial'lar zaman ve pratik kontrolü olarak duruyor ve sayıları GG ile
eşleşmek zorunda. Eşleşmezse aftereffect'in büyüklüğü yorumlanamaz.

## Bu tasarım neyi sorabilir, neyi soramaz

**Soramaz: Ludolph'un gradual-ile-ani sorusunu.** İki grup başlangıç dışında
hiçbir noktada aynı yerçekiminde dengeleme yapmıyor. Seans sonunda biri 3.5'te,
diğeri 1.0'da. O noktadaki performans farkı öğrenme farkı değil, zorluk farkı.
"Gradual grup daha iyi öğrendi" cümlesi bu tasarımla kurulamaz. Kurmak için
kontrol grubunun 3.5'te olması gerekirdi.

**Sorabilir: aftereffect sorusunu.** Kişi 3.5'e uyum sağladıktan sonra 1.0'ın
fiziğini yanlış tahmin etmeye başlıyor mu, ve bu hem motor davranışta hem
algısal testte görünüyor mu. Ludolph'un Conclusions bölümünde açık soru olarak
bıraktığı şey tam olarak bu.

Karşılaştırmanın kurulduğu yer şu. GG'nin aşama 8'i ile aşama 2'si arasındaki
fark iki şey içeriyor: aftereffect, artı seans boyunca pratik yapmaktan gelen
genel iyileşme. CG aynı iki noktayı hiç adaptasyon yaşamadan veriyor, yani o
genel iyileşmenin ölçüsü. GG'nin farkından CG'ninkini çıkarınca geriye saf
aftereffect kalıyor. Kontrol grubunun asıl işi bu.

Aynı mantık algısal tarafta da geçerli: prediction post-test eksi pre-test,
GG'de CG'dekinden farklı mı.

**Uyaranların g = 1.0 olması bu çerçevede lehimize.** Test dünyası kontrol
grubunun dünyası. GG ondan uzaklaşan taraf, yani bulunacak etki ev sahibi
avantajına rağmen bulunmuş oluyor. Confound hipotezin aleyhine çalışıyor, bu
istenen yön.

## Ludolph'tan gelen ve gelmeyen

| Öğe | Durum |
|---|---|
| Fizik parametreleri, ±60° açı ve ±5 m ray sınırı, ±4 N kuvvet | Aynen alındı |
| Occlusion testinin tamamı: 4.5 s, 100 ms, 900 ms, 13 seçenek, [-65, +65], feedback yok | Aynen alındı |
| g aralığı 1.0 → 3.5 | Aynen alındı |
| Kontrol grubunun yerçekimi | **Değiştirildi.** Ludolph'ta 3.5 (aynı zorlukta biten ikinci kol), bizde 1.0 (zaman ve pratik kontrolü) |
| g artış kuralı | **Değiştirildi.** Ludolph'ta her başarılı trial'dan sonra +0.1, başarı = 30 s düşmeden dengede kalmak, 25 artış. Bizde sabit takvim, 8 trial'da bir +0.25, 10 artış |
| Trial süresi | **Değiştirildi.** Ludolph'ta üst sınır 30 s ve düşünce trial biter. Bizde sabit 20 s, düşünce reset olup devam eder |
| Seans yapısı | **Değiştirildi.** Ludolph'ta süre sınırı var (90 dk), trial sayısı serbest. Bizde trial sayısı sabit |
| Occlusion blok sayısı | **Değiştirildi.** Ludolph'ta 11 blok x 40 = 440 deneme. Bizde 2 blok x 40 = 80 deneme |
| Occlusion uyaranlarının yerçekimi | Ludolph'ta 3.5, yani eğitimin bittiği yerle aynı. Bizde 1.0, yani GG için farklı. Bu fark tasarımı aftereffect deneyine çeviriyor |
| Aşama 5, 7 ve 8 (late adaptation, re-adaptation, washout) | **Ludolph'ta yok.** Makalenin Conclusions bölümü bunları açık soru olarak sayıyor: g geri çekildiğinde timing'de after-effect var mı, gradual ile sudden arasında retention farkı var mı |

## Sabit takvimin analize etkisi

Ludolph'ta g başarılı bir trial'dan sonra arttığı için, adım sonrası performans
düşüşünün ne kadarının yerçekiminden ne kadarının regression to the mean'den
geldiği ayrılmıyor. Adımdan önceki trial tanım gereği iyi bir trial ve
ardından doğal bir gerileme bekleniyor. Ludolph bunu ele almamış.

Bizde g başarıdan bağımsız arttığı için bu confound yok. Sonuçları:

- Adım sonrası bozulma doğrudan yorumlanabiliyor, düzeltme gerekmiyor.
- `trial_success` kolonu kayıt isteklerinden tamamen çıktı. Artışı tetikleyen
  bir bayrak olmadığı için gereksiz, ve 20 saniyede sabit trial'da "başarılı"
  tanımı zaten belirsiz. Performans ölçütü olarak `fall_event`'ten
  türetiliyor.

İkinci etki: her katılımcı aynı 10 seviyede aynı 8 trial'ı yaptığı için tasarım
dengeli ve within-subject. Pilotun katılımcı × koşul yapısıyla aynı şekil,
sadece koşul yerine gravity step geçiyor. Mevcut analiz kodunun büyük kısmı
bu eksende yeniden kullanılabiliyor.

## Süre

| Aşama | Süre |
|---|---|
| 1. Familiarization | 1 dk |
| 2. Motor baseline | 3 dk |
| 3. Prediction pre-test | ~5 dk |
| 4. Adaptation | ~27 dk |
| 5. Late adaptation | 3 dk |
| 6. Prediction post-test | ~5 dk |
| 7. Re-adaptation | 3 dk |
| 8. Washout | 3 dk |
| **Toplam** | **~49 dk** |

Bu saf dengeleme ve test süresi. Trial başına 1 saniyelik reset eklendiğinde
115 trial için yaklaşık 2 dakika daha çıkıyor. Talimat, mola ve geçişlerle
birlikte seans gerçekte bir saati bulur.

## Belirlenmemiş tek şey

Grup başına katılımcı sayısı. Bunu simülasyonla güç hesabından çıkaracağım,
ekibe soru olarak gitmiyor. Hesap occlusion tarafındaki 80 denemenin kişi
düzeyinde parametre tahmini için yetip yetmediğini söyleyecek ve gereken
asgari grup büyüklüğünü verecek.

## Kaynaklar

- Ludolph N, Giese MA, Ilg W (2017). Interacting Learning Processes during
  Skill Acquisition. *Scientific Reports* 7:13191.
- Ludolph N, Plöger J, Giese MA, Ilg W (2017). Motor expertise facilitates the
  accuracy of state extrapolation in perception. *PLOS ONE* 12(11):e0187666.
