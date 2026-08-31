# 03 — Durum, aksiyon sınıfları, episode ve regime run

**Notebook:** `Data Analysis/Notebooks/02_build.ipynb`
**Kod:** `src/build.py`
**Config:** `config.yaml` → `build`, `input_events`
**Çıktı:** `samples_built`, `episodes`, `regimes`, `input_events` parquet
**Kaynak:** Park et al. 2025, *Exp Brain Res* 243:44

---

## 1. Durum: phase plane

Park'ın tanımı, aynen alındı:

```
fall_state  = θ · ω > 0    # hem eğik hem düşeceği tarafa dönüyor
safe_state  = θ · ω < 0    # eğik ama dikeye dönüyor
```

**Mevcut dağılım (12 katılımcı, active örnekler):** fall %63.5, safe %36.5.

Not: Ludolph'un action timing analizinde event filtresi olarak kullandığı
"pole aşağı dönüyor" koşulu ile Park'ın fall kuadranı **aynı kriter**. İki
makaleyi bağlayan yer burası.

## 2. İşaret konvansiyonu — veriden doğrulandı, varsayılmadı

Park "joystick işareti θ'nın **tersi** = düzeltici" diyor. Bu bize **aynen
aktarılamaz**: Park'ın VIP'inde joystick doğrudan açısal ivme veriyor, bizim
cart-pole'da kuvvet cart'a gidiyor ve etki pole'a ters çevrilerek yansıyor.

**Ölçüm:**

- `F > 0` iken ortalama `dθ/dt = −21.0 °/s`
- `F < 0` iken ortalama `dθ/dt = +25.6 °/s`
- Katılımcı davranışı da aynı yönde: θ = +2..+10° iken ortalama input +0.025

**Sonuç: düzeltici kuvvet θ ile aynı işaretli.** Bütün aksiyon sınıfları bu
çevrilmiş konvansiyonda tanımlı.

Bu, literatürden aynen alınamayan ve veriden türetilmesi gereken bir şeydi.
Yanlış alınsaydı CR ile D sınıfları yer değiştirirdi.

## 3. Aksiyon sınıfları

```
I  : |u| ≤ band              nötr banddaki kalıcı girdi
CR : u·θ > 0                 düzeltici (Corrective Reaction), her kuadranda
A  : u·θ < 0  ve  θ·ω < 0    dikeye dönüşü frenleme (Anticipatory, sadece safe)
D  : u·θ < 0  ve  θ·ω > 0    düşüş yönüne kuvvet (Destabilizing, sadece fall)
X  : sınıflandırılmayan      banddan geçici geçiş / dejenere işaret
```

`u` = `input_applied`.

### Eşikler ve gerekçeleri

| Eşik | Değer | Gerekçe |
|---|---|---|
| `build.input_neutral_band` | 0.02 | Örneklerin **%73.9'u tam sıfır**, sıfır olmayan en küçük değer 0.0153. Unity deadzone'u zaten uygulamış; band pratikte "tam sıfır" demek |
| `build.neutral_transient_max_samples` | 3 | Park'ın footnote'u: banda takılıp kalan değerler I sayılır, joystick soldan sağa geçerken banddan hızlı geçiş I sayılmaz. Bu eşikten kısa nötr diziler zıt işaretli sapmalar arasındaysa X etiketlenir |

`input_raw` ile `input_applied` **birebir aynı** (maksimum fark 0.000000),
iki kolon gereksiz.

### Girdi cihazı: analog kol

`metadata.input_device` = **`Xbox Controller`**, platform `WindowsPlayer`.
Veri de bunu doğruluyor:

- Sıfır olmayan **136 farklı büyüklük**, ~0.0098 adımlarla nicelenmiş
  (analog eksenin çözünürlüğü)
- En küçük sıfır olmayan değer 0.0153 — ölü bölgenin kenarı
- Doyuma (|u| = 1.0) giden örnekler, sıfır olmayanların sadece ~%5'i

Yani girdi **dereceli**, aç-kapa değil. %73.9 tam sıfır olması yaylı kolun
merkeze dönmesi ve ölü bölgenin küçük değerleri kırpması demek — tuhaf değil.

Bu, Ludolph'un action timing yöntemi için iyi haber: onun yöntemi "ortalama
kuvvet eğrisi düzgün bir S çizer ve sıfırı bir kez keser" varsayımına
dayanıyor ve bu varsayım analog kolda makul. Yine de ampirik teyit gerekiyor
(bkz. 05_Action_Timing.md, henüz yazılmadı).

### Mevcut dağılım (12 katılımcı, active örnekler)

```
I  74.5%    CR 22.5%    D 2.7%    A 0.30%    X 0.01%
```

**A çok seyrek (%0.30).** Park'ta anlamlı bir orandı. Muhtemel sebep:
zamanın %63.5'i fall kuadranında geçiyor, katılımcılar düşüşle boğuşuyor,
dikey civarında ince ayar yapmıyor. Bulgu, bug değil — ama bu seyreklikte
istatistiksel olarak kullanılıp kullanılamayacağı NB04'te karara bağlanacak.

Rejim başına profil Park'ın niteliksel örüntüsüyle uyuşuyor: Failed'da D en
yüksek (%26.5) ve CR en düşük (%19.0); Safe'te CR en yüksek (%38.8).

## 4. Episode ve regime run — aynı şey değil

Bu ikisinin karıştırılmaması kritik. Farklı literatürlere hizmet ediyorlar.

| Birim | Tanım | Sayı (12 katılımcı) | Ne için |
|---|---|---|---|
| **Episode** | reset'ten reset'e | 2.017 | T₀, süre (Ludolph) |
| **Regime run** | kuadran dizisi; θ·ω işaret değiştirince yeni run | 18.891 | Safe/Saved/Failed (Park) |

Episode başına ortalama 9.4 run düşüyor. Run'lar episode sınırını aşmaz.

### Episode (`segment_episodes`)

Her episode bir trial içinde, iki reset arasında (ya da trial başı / trial
sonu ile bir reset arasında) kalan kesintisiz active parça. Kaydedilenler:
başlangıç açısı ve hızı, süre, maksimum |θ|, düşüşle mi bitti, düşüş sebebi,
sansürlü mü, T₀ ve T/T₀.

**Sansürlü episode** = düşüşle bitmeyen, trial 20 s dolduğu için kesilen
episode. 1.756 measurement episode'un **600'ü sansürlü (%34.2)**. Bu oran
göz ardı edilemez; süre analizinde nasıl ele alındığı için bkz.
[04 §4](04_Performans_Metrikleri.md#4-süre-ölçütü-üç-aday-da-elendi).

### Regime run (`segment_regimes`)

| Etiket | Tanım | Oran |
|---|---|---|
| `Safe` | safe kuadranındaki run, dikeye dönüyor | %45.4 |
| `Saved` | fall kuadranında başladı, sınıra varmadan kurtarıldı | %45.2 |
| `Failed` | **açı** limitine (±60°) varan run | %6.6 |
| `censored` | fall kuadranındaki son run, trial bitişiyle kesildi | %2.1 |
| `TrackLoss` | cart ray limitine çarpmasıyla biten run | %0.7 |

`build.regime_min_samples` = 2. Bundan kısa run'lar (135 tane) ayrıca not
edilir.

## 5. Düşüş sebebi ikiye ayrılıyor

`fall_event` iki farklı sebeple tetikleniyor ve **ayırt edilmesi şart**:

| Sebep | n | Düşüş anında ort. &#124;θ&#124; |
|---|---|---|
| `angle` — pole ±60°'ye vardı | 1.241 | 61.0° |
| `track` — cart ±5 m ray sınırına çarptı | 140 | 21.3° |

Örtüşme sıfır, açıklanamayan sıfır. Ray kaynaklı düşüşlerin biri **0.27°'de**
olmuş — pole dimdikken cart raydan çıkmış. 140'ının **42'si safe
kuadranında**, yani pole dikeye dönerken.

**Karar:** `Failed` sadece açı kaynaklı düşüşler için kullanılıyor (Park'la
karşılaştırılabilir olan bu), ray kaybına ayrı `TrackLoss` etiketi veriliyor
ve Park karşılaştırmalarından çıkarılıyor. Park'ta bunun karşılığı yok çünkü
onun VIP'inde ray yok.

## 6. Girdi olayları (`detect_input_events`)

**Dikkat: bunlar Ludolph'un event'leri DEĞİL.** İsimlendirme 2026-08-31'de
ayrıldı: girdi tarafındaki olaylar `input_events`, Ludolph'un durum
tarafındaki olayları `state_events` (NB04'te üretilecek).

Bu tablodaki olaylar **girdi tarafında** tanımlı:

| Event | Tanım |
|---|---|
| `onset` | nötr banddan çıkış (`input_events.onset_min_samples` = 3 örnek band dışında kalmalı) |
| `offset` | nötr banda dönüş |
| `reversal` | kuvvet yön değiştirme (nötr örnekler atlanarak) |
| `fall` | düşüş anı |

**Mevcut sayılar:** onset 14.001, offset 13.288, reversal 6.849, fall 1.381.
`fall` event sayısı Unity'nin `trial_summary.fall_count` toplamıyla birebir
aynı (1.381) — bağımsız doğrulama.

Olaylar **episode içinde** aranır. Reset satırları zaten dışarıda olduğu için
parçalar arası sahte zero-crossing oluşmaz. Bu ayrım önemli çünkü reset
satırlarında `applied_force_n` sıfıra zorlanıp `input_applied` son değerinde
kalıyor (bkz. `Veri_Kayit_Istekleri.md` madde 2).

Ludolph'un event'i ise **durum tarafında** tanımlı: pole belirli bir tamsayı
açıdan aşağı dönerken geçiyor. Bu iki tanımın ilişkilendirilmesi ve action
timing hesabı `05_Action_Timing.md`'nin konusu — **henüz yazılmadı**.

Bu olaylar **tanımlayıcı istatistik ve QC** için; `fall` sayısının Unity'nin
`fall_count`'uyla karşılaştırılması bağımsız bir doğrulama. Ludolph'un action
timing'i bunları **kullanmıyor** — bkz. [05](05_Action_Timing.md).

Ludolph tipi olayların sayısı ölçüldü (düşüş yönlü geçişler, measurement +
`analysis_include`):

| Açı aralığı | Geçiş | Katılımcı × koşul başına |
|---|---|---|
| ±25° | 110.091 | ~1.835 |
| ±15° | 79.607 | ~1.327 |
| ±10° | 57.549 | ~959 |
| ±5° | 29.198 | ~487 |

Ortalama almak için her aralıkta fazlasıyla yeterli; aralık seçimi bir
fizibilite sorunu değil, bir yorum sorusu.
