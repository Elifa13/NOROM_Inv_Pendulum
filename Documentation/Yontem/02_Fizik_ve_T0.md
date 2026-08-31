# 02 — Fizik modeli ve T₀

**Notebook:** `Data Analysis/Notebooks/02_build.ipynb` §1, §2b
**Kod:** `src/physics.py`
**Config:** `config.yaml` → `physics`, `t0`

---

## 1. Neden fizik modeline ihtiyacımız var

T₀ hesabı için. T₀ = "katılımcı hiçbir şey yapmasaydı pole kaç saniyede
düşme sınırına varırdı". Bu ölçülemez, simüle edilmesi gerekir; simüle etmek
için de Unity'nin kullandığı dinamiği bilmek gerekir. Model doğru değilse
T₀ yanlış olur ve T/T₀ türevi her şey çöker.

Model metadata'da yazmıyor, veriden çıkarıldı ve doğrulandı.

## 2. Model

Standart cart-pole (düzgün çubuk, 4/3 atalet katsayısı):

```
temp = (F + m_p · l · ω² · sinθ) / (m_c + m_p)
θ''  = (g · sinθ − cosθ · temp) / (l · (4/3 − m_p · cos²θ / (m_c + m_p)))
x''  = temp − m_p · l · θ'' · cosθ / (m_c + m_p)
```

| Parametre | Değer | Not |
|---|---|---|
| `m_c` cart kütlesi | 0.40 kg | Ludolph |
| `m_p` pole kütlesi | 0.08 kg | Ludolph |
| `l` | **0.5 m** | **Yarım uzunluk.** Tam pole 1.0 m; dinamik denklemine yarısı giriyor |
| `g` | 1.00 m/s² | Ludolph'un başlangıç seviyesi, pilotta sabit |
| `F` | `applied_force_n` | İşaret doğrudan aynı, kuvvet gecikmesi yok, sönüm yok |
| Fall sınırı | ±60° | Ludolph |
| Ray sınırı | ±5 m | Ludolph |
| İntegrasyon | RK4, Δt = 1/60 s | |

`l = 0.5` ayrımı önemli ve kolay kaçırılır. `config.yaml`'da hem
`pole_length_m: 1.0` hem `pole_half_length_m: 0.5` var; koda giren ikincisi.

**Ludolph'tan sapma:** Ludolph'ta yerçekimi performansa göre 3.5 m/s²'ye
yükseliyordu (gradual gravity koşulu). Pilot, noise etkisini izole etmek
için g'yi 1.0'da sabit tutuyor. Bu, pilotun Ludolph'un öğrenme bulgusuyla
doğrudan karşılaştırılamaması demek.

## 3. Modelin doğrulanması

**Yöntem** (`physics.verify_model`): kesintisiz active parçalarda, ölçülen
(θ, ω, x, v, F) durumundan modelin öngördüğü açısal ivme hesaplanır ve
gözlenen açısal ivmeyle karşılaştırılır. Gözlenen ivme `pole_angular_velocity_deg_s`
kolonunun sayısal türevi.

Parçaların kesintisiz olması şart — reset sınırını aşan bir pencere sahte
ivme üretir.

**Sonuç:** 8 uzun parça, korelasyon **0.9884 – 0.9972**.

**Ama korelasyon tek başına yetmiyor — bu önemli.** Korelasyon ölçekten
bağımsızdır: eğrinin *şeklini* doğrular, *büyüklüğünü* değil. `l = 1.0` ile
tekrar çalıştırdık:

| | korelasyon | ortalama RMS hata |
|---|---|---|
| `l = 0.5` | 0.9884 – 0.9972 | **0.189** |
| `l = 1.0` | 0.9884 – 0.9971 | 0.997 |

Korelasyon neredeyse hiç değişmiyor, RMS hatası beş katına çıkıyor. Yani
`l` değerini pinleyen şey korelasyon değil, RMS ve aşağıdaki serbest düşüş
testi. "Korelasyon 0.988–0.997, model doğrulandı" demek eksik bir ifade.

## 4. T₀ hesabı

**Tanım:** (θ₀, ω = 0) durumundan başlayıp **sıfır kuvvetle** |θ| = 60°'ye
varana kadar geçen süre.

F = 0 iken dinamik sadece (θ, ω)'da kapalı — x ve v geri beslemiyor. Yani
**T₀ tek başına θ₀'ın fonksiyonu.** Bu, hesabı cache'lenebilir yapıyor
(`T0_for_angles`, aynı açı tekrar ettiği için).

| θ₀ | 0.5° | 1° | 2° | 3° | 4° | 5° | 6° | 7° | 7.5° |
|---|---|---|---|---|---|---|---|---|---|
| T₀ | 4.23 s | 3.70 | 3.18 | 2.87 | 2.65 | 2.48 | 2.33 | 2.22 | 2.17 |

Gerçek episode'larda: ortalama 2.93 s, aralık 2.17–9.68 s.

Başlangıç açısı dağılımı U(−7.5°, +7.5°) — Ludolph ile aynı.

## 5. T₀'ın ampirik doğrulanması

**Fikir:** katılımcının hiç girdi vermediği ve açı limitiyle biten bir
episode tanım gereği serbest düşüştür. Süresi T₀'a **eşit olmalı**. Bu tek
test fizik modelini, RK4 adımını, T₀ hesabını ve episode segmentasyonunu
aynı anda doğrular.

**Kod:** `build.validate_T0_freefall`

**Sonuç (12 katılımcı):** 11 böyle episode var, **on birinde de
`duration/T₀ = 1.0000`**, 1.0'dan maksimum sapma 0.0000.

**"11 örnek az değil mi?" — burada örneklem mantığı işlemiyor.** T₀ tahmin
edilmiyor, modelden deterministik olarak hesaplanıyor. Bu bir parametre
tahmini değil, bir *sınav*. Yanlış model 1.0000 vermez: `l = 1.0` ile
T₀(7.5°) = 3.07 s olurdu (2.17 yerine), yani oran her seferinde ~0.71
çıkardı. 11 farklı başlangıç açısında sapmanın tam sıfır olması tesadüf
olamaz.

**Gerçek sınır — kapsama.** Bu 11 episode θ₀ = 1.52°–7.25°, yani T₀ =
2.20–3.38 s aralığını kapsıyor. Tüm episode'larda T₀ 2.17–9.68 s aralığında;
üst uç (dike çok yakın başlangıçlar) test edilmedi. Risk düşük — model
denklemi açıdan bağımsız — ama yazılı olsun.

Zincirin tamamı (fizik modeli, RK4 adımı, T₀ hesabı, episode segmentasyonu)
tek testte doğrulanmış oluyor.

## 5b. T₀ bundan sonra ne işe yarıyor

Performans metriği olarak **kullanılmıyor** (§6 ve
[04 §4](04_Performans_Metrikleri.md#4-süre-ölçütü-üç-aday-da-elendi)).
Kalan üç işi:

1. **Doğrulama** — yukarıdaki test. Bitti, tek seferlik.
2. **Zorluk değişkeni** — T₀ tamamen θ₀'ın fonksiyonu olduğu için "bu episode
   ne kadar zor bir açıdan başladı"nın tek sayılık özeti. Randomizasyon
   yanlılığını kontrol ederken doğal kovaryant.
3. **Survival analizi yapılırsa** kovaryant olarak girer.

Bunların dışında T₀ iskele: modeli kurmaya ve kanıtlamaya yaradı.

## 6. Ludolph'un T/T₀'ı aynen aktarılamaz

**Ludolph'ta:** trial düşünce **biter**. T (gerçek trial süresi) değişkendir
ve T/T₀ "hiçbir şey yapmamaya göre ne kadar iyi/kötü" anlamına gelir.

**Bizde:** trial sabit 20 s, düşüş olunca reset olup devam ediyor. T hep
≈20 s, dolayısıyla T/T₀ = 20/T₀ oluyor — yani **saf θ₀ fonksiyonu**.
Ölçülen: `corr(|θ₀|, trial düzeyi T/T₀) = +0.972`. Performans ölçmüyor.

**Doğru karşılık episode düzeyi:** her episode kendi başlangıç açısından
başlar (trial başı ya da düşüş sonrası restart), süresi düşüşe ya da trial
sonuna kadardır.

| Ölçüt | corr(&#124;θ₀&#124;, ölçüt) |
|---|---|
| Trial düzeyi T/T₀ | +0.972 |
| Episode düzeyi T_ep/T₀ | +0.128 |
| Episode süresi (ham) | −0.078 |

Bu tablonun devamı ve **episode düzeyinde de T/T₀'ın reddedilme gerekçesi**
için bkz. [04_Performans_Metrikleri.md §4](04_Performans_Metrikleri.md#4-süre-ölçütü-üç-aday-da-elendi).
Kısaca: T₀'a bölmek kirliliği azaltmıyor, artırıyor.
