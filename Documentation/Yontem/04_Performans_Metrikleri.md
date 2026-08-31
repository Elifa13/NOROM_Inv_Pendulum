# 04 — Performans metrikleri ve metrik seti seçimi

**Notebook:** `Data Analysis/Notebooks/03_performance.ipynb`
**Kod:** `src/performance.py`
**Config:** `config.yaml` → `performance`
**Çıktı:** `data/interim/trial_metrics.parquet` (600 trial), `participant_condition.parquet` (60 hücre)

---

## 1. Analiz birimi ve payda

**Analiz birimi: katılımcı × koşul.** Her hücre 10 measurement trial'ın
ortalaması. 12 katılımcı × 5 koşul = 60 hücre. Trial düzeyi tablo ara ürün
(NB04 de kullanacak).

Maske `analysis_include` (bkz. [01 §3.5](01_Veri_Isleme.md#35-sample-maskesi-add_analysis_mask)).
Reset frameleri tamamen dışarıda, her measurement trial'da tam 1200 active
sample var — yani **payda sabit**.

Bu, gözden kaçması kolay ama önemli: eğer reset frameleri dahil olsaydı çok
düşen bir katılımcının "kötü" zamanı reset'lerle seyreltilir ve yapay olarak
iyi görünürdü.

## 2. Trial düzeyi metrikler

`u` = `input_applied`, `θ` = `pole_angle_deg`, `x` = `cart_position_m`.

| Metrik | Formül | Yön |
|---|---|---|
| `mae_angle_deg` | mean(&#124;θ&#124;) | düşük iyi |
| `rms_angle_deg` | sqrt(mean(θ²)) | düşük iyi |
| `siqr_theta_deg` | (Q75(θ) − Q25(θ)) / 2 | düşük iyi |
| `siqr_omega_deg_s` | aynısı ω için | düşük iyi |
| `max_abs_angle_deg` | max(&#124;θ&#124;) | düşük iyi |
| `stab_time_s` | &#124;θ&#124; ≤ eşik olan süre | yüksek iyi |
| `falls_per_trial` | `fall_event` toplamı | düşük iyi |
| `falls_angle_per_trial` | sebebi `angle` olan düşüşler | düşük iyi |
| `falls_track_per_trial` | sebebi `track` olan düşüşler | düşük iyi |
| `control_effort` | sqrt(mean(u²)) | belirsiz |
| `cart_rms_m` | sqrt(mean(x²)) | belirsiz |

Episode türevleri (trial başına): `n_episodes`, `n_episodes_censored`,
`mean_episode_s`, `mean_T_over_T0` ve bunların sansürsüz sürümleri,
`mean_theta0_abs_deg`.

### Neden `control_effort` ve `cart_rms_m` "belirsiz"

İkisinde de düşük değer iki farklı şey demek olabilir: iyi kontrol, ya da
hiç müdahale etmemek. Tek başlarına "iyi/kötü" demiyorlar, sadece
tie-breaker olarak kullanılıyorlar.

### Stabilizasyon süresi kendi eşiğimizle hesaplanıyor

Unity'nin `within_bounds_time_s` kolonu **failure limitini** (60° / 5 m)
eşik alıyor. Sonuç: 600 trial'da ortalama **19.97 s**, sd 0.04 — tavana
yapışık, koşulları ayırt etmesi imkânsız.

Kendi eşiğimiz `performance.stab_angle_deg` = **30°**. Bununla ortalama
18.22 s, sd 1.67.

Eşiğin kendisi bir seçim; sunum notebook'unda 5°–45° arası taranmış ve
sonucun yönü bütün eşiklerde aynı çıkmış (bkz.
[../Pilot_Sonuc_Ozeti.md](../Pilot_Sonuc_Ozeti.md#eşik-seçimi-sonucu-değiştirmiyor)).

### Düşüş sayımı üç kaynakta tutuyor

600 measurement trial'ın **600'ünde** üçü de aynı: sample düzeyi
`fall_event` toplamı, sebebe göre ayrılmış toplam (açı 1.025 + ray 131) ve
Unity'nin `fall_count`'u (1.156).

## 3. sIQR gereksiz mi — kontrol edildi, ikisi de karar setine girmiyor

### Neden sorduk

`CLAUDE.md`'nin gerekçesi: iki katılımcının maPA'sı aynı olabilir ama biri
çoğunlukla ±5°'de durup ara sıra ±50°'ye giderken diğeri sürekli ±15°'te
olabilir. RMS birincisini orantısız cezalandırır. sIQR bu farkı yakalar.

### Kriter — korelasyondan trend'e çevrildi

İlk kriter "RMS ile korelasyon > 0.9 ise kopya"ydı. Bu **yanlış soru**:
metrik RMS'ten farklı bir şey ölçse bile, *koşulları ayırt etmiyorsa* karar
setine girmemeli.

Uygulanan kriter (`performance.redundancy_check`):

1. Hedef metrik ve RMS **katılımcı içi merkezlenir** — within-subject
   tasarımda doğru ölçek bu; katılımcılar arası seviye farkı korelasyonu
   şişiriyor
2. Hedef, RMS üzerine regres edilir
3. Artığın koşul profilinde **lineer kontrastın** ne kadarı hayatta kalıyor

Kontrast ağırlıkları ordinal pozisyon üzerinden `[−2, −1, 0, +1, +2]`.
σ değerleri (0, 0.02, 0.05, 0.08, 0.25) eşit aralıklı değil ve sıfır
içerdiği için log alınamıyor; ordinal sıralama en savunulabilir seçim.

Eşikler: `redundancy_abs_r` = 0.9, `redundancy_retained_trend` = 0.25.
İkisinden biri tetiklerse metrik gereksiz sayılır.

### Sonuç

| Metrik | r (within) | Ham lineer kontrast | Artık | Korunan trend | Karar |
|---|---|---|---|---|---|
| `siqr_theta_deg` | 0.848 | +3.082 | +0.282 | **%9** | gereksiz |
| `siqr_omega_deg_s` | 0.597 | +2.695 | −0.576 | **%21** | gereksiz |
| `mae_angle_deg` | 0.982 | +4.130 | +0.232 | **%6** | RMS'in kopyası |

- **sIQR_theta** RMS'in neredeyse kopyası, noise trendinin %9'unu taşıyor.
- **sIQR_omega** ayrı bir konstrukt (r = 0.60 — CLAUDE.md'nin "açı
  büyüklüğünden bağımsız salınım" beklentisi doğru çıktı) ama noise
  trendinin %79'unu yine RMS açıklıyor ve kalan %21 **ters işaretli**, yani
  düzensiz.
- **maPA ile RMS** birbirinin kopyası; ikisinden sadece biri raporlanmalı.
  maPA seçildi, daha okunaklı.

Üçü de `trial_metrics.parquet`'te duruyor. sIQR_omega NB04'te kontrol
mekanizmasını betimlerken kullanılabilir — sadece **karar metriği** değil.

## 4. Süre ölçütü: üç aday da elendi

Ludolph'un T/T₀'ı trial düzeyinde anlamsız (bkz.
[02 §6](02_Fizik_ve_T0.md#6-ludolphun-tt₀ı-aynen-aktarılamaz)). Episode
düzeyinde dört aday denendi, hepsi elendi.

### 4.1 `mean_episode_s` — düşüş sayısının deterministik dönüşümü

Episode'lar trial'ı tam kaplıyor (toplam 20 s) ve her düşüş bir episode
sınırı. Dolayısıyla:

```
n_episodes  = falls + 1          (600 trial'ın 600'ünde doğrulandı)
mean_episode_s = 20 / (falls + 1)
```

`corr(mean_episode_s, 20/(falls+1)) = 1.0000`. **Yeni hiçbir bilgi
taşımıyor**, `falls_per_trial`'ın yeniden yazılmış hali.

### 4.2 `mean_T_over_T0` — T₀'a bölmek fazla düzeltiyor

T₀, θ₀ büyüdükçe küçülüyor. Süreyi T₀'a bölmek ≈ 1/T₀ ile çarpmak, yani
θ₀ bağımlılığını **azaltmak yerine artırıyor**:

| Düzey | Ham süre | T₀'a bölünmüş |
|---|---|---|
| Episode | −0.075 | +0.141 |
| Katılımcı × koşul | +0.229 | **+0.645** |

Ludolph'un normalizasyonu bizim tasarımımızda ters çalışıyor.

### 4.3 Sansürsüz sürümler — hayatta kalma yanlılığı

Sansürlü episode demek "trial sonuna kadar düşmedi", yani **en iyi
denemeler**. Onları atınca:

- no_noise ortalaması 12.10 s → 7.38 s'ye düşüyor ve **en düşük** koşul
  haline geliyor — saçma bir sonuç
- N4 etkisi işaret değiştiriyor: dz −1.03 → +0.25

1.756 episode'un 600'ü sansürlü (%34.2), göz ardı edilecek oran değil.

### 4.4 Karar

**Bağımsız bir süre metriği kullanılmıyor; `falls_angle_per_trial` yeterli
istatistik.**

Ludolph'un süre temelli ölçütünü düzgün kullanmak için sağ sansürü ele alan
bir survival analizi (Kaplan-Meier / Cox) gerekir. NB03'ün kapsamı dışında;
gerekirse NB05'te yapılır.

## 5. Karar metrik seti (NB06'ya giden)

| Metrik | Yön | Not |
|---|---|---|
| `mae_angle_deg` | düşük iyi | RMS ile r = 0.98, ikisinden biri |
| `stab_time_s` | yüksek iyi | kendi eşiğimiz, 30° |
| `falls_angle_per_trial` | düşük iyi | Park'ın Failed'iyla karşılaştırılabilir olan |
| `control_effort` | belirsiz | tie-breaker |
| `cart_rms_m` | belirsiz | tie-breaker |

**Dışarıda:** sIQR'lar (§3), süre metrikleri (§4), `falls_track_per_trial`
(koşulla ilgisiz görünüyor, dz'ler ±0.12 içinde; Park karşılaştırmasından
zaten çıkarılıyor).

## 6. Betimleyici etki büyüklükleri

Bu notebook **istatistiksel test yapmaz**. Friedman / Wilcoxon ve noise
seviyesi kararı NB06'nın işi.

Raporlananlar:

- `baseline_farki` = koşul − no_noise, katılımcı başına eşleşmiş fark
- `dz` = mean(fark) / sd(fark)
- `n_kotu` = 12 katılımcının kaçında fark metriğin kötü yönünde

**maPA sonucu:** N1'de fark yok (dz −0.03, 6/12). N2, N3, N4'te
katılımcıların **11/12'sinde** baseline'dan kötü (dz 0.96–1.18).

Bütün ana metriklerde aynı şekil: no_noise ile N1 yapışık, N2'den itibaren
monoton bozulma. **U şekli yok.**

## 7. Başlangıç açısı kirliliği

`mean_theta0_abs_deg` katılımcı × koşul düzeyinde 3.53–3.85° aralığında
(yayılım 0.32°); trial düzeyinde 3.43–3.78°, yayılım 0.35°, trial içi sd
2.11°. `fall_count` ile korelasyon +0.066.

Yön **bulgunun aleyhine**: en zor başlangıçlar (3.85°) no_noise'da, yani
yanlılık gözlenen bozulmayı şişirmiş olamaz.

Randomizasyon sorununun kendisi için bkz. `CLAUDE.md` → "Veride görülen
sorunlar" §1.
