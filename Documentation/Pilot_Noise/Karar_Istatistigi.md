# 06 — Karar istatistiği

**Notebook:** `06_noise_decision.ipynb`
**Kod:** `src/decide.py`
**Çıktı:** `data/<dataset>/processed/karar/decision_stats.csv`, `decision_table.csv`
**Durum:** uygulandı (2026-08-31)

Bu kayıt "hangi testi neden kullandık" sorusunun cevabı. Sonuçların kendisi
[../Pilot_Sonuc_Ozeti.md](../Pilot_Sonuc_Ozeti.md)'de.

---

## 0. Terimler

| Terim | Ne demek |
|---|---|
| **within-subject** | Her katılımcı bütün koşulları gördü; karşılaştırma kişinin kendi içinde yapılıyor. Kişiler arası devasa fark böyle devre dışı kalıyor. |
| **Friedman test** | Tekrarlı ölçümde "bu k koşul arasında herhangi bir fark var mı" sorusunun non-parametrik (sıralama tabanlı) omnibus testi. ANOVA'nın dağılım varsayımı gerektirmeyen karşılığı. |
| **Kendall's W** | Friedman'ın etki büyüklüğü. 0 = katılımcılar koşulları rastgele sıralıyor, 1 = hepsi aynı sırada. `W = χ² / (n(k−1))`. |
| **Wilcoxon signed-rank** | İki eşleşmiş ölçüm arasındaki farkın testi. Paired t-test'in non-parametrik karşılığı. n = 12'de exact hesaplanıyor. |
| **Holm düzeltmesi** | Çoklu karşılaştırmada yanlış pozitif riskini kontrol eder. Bonferroni'nin daha az muhafazakâr, adım adım (step-down) sürümü. |
| **orthogonal contrast** | Koşul ortalamalarına ağırlık verip tek bir skora indirmek. Ağırlıklar ortogonal seçilirse lineer ve kuadratik bileşen birbirinden bağımsız test edilir. |
| **rank-biserial correlation** | Eşleşmiş Wilcoxon'un etki büyüklüğü: sıfır olmayan farkların \|d\| sıralamasında pozitiflerin payı eksi negatiflerin payı, −1…+1. |
| **d<sub>z</sub>** | Eşleşmiş fark etki büyüklüğü: ortalama fark ÷ farkların standart sapması. |

## 1. Analiz birimi ve neden

**Katılımcı × koşul**, her hücre o kişinin o koşuldaki 10 measurement
trial'ının ortalaması. 12 × 5 = 60 hücre.

Trial düzeyinde test edilmiyor çünkü aynı kişinin trial'ları bağımsız değil;
600 trial'ı bağımsız gözlem saymak yanlış pozitif üretir. Hücre düzeyi bu
bağımlılığı katılımcı içine kapatıyor.

## 2. Test seçimi

**n = 12.** Bütün testler sıralama tabanlı.

**Uygulama notu (2026-09-02).** Bu bölümün ilk hali "n = 12'de normallik
varsayımı sınanamaz; parametrik testler riskli" diyordu. Sınandı, ve gerekçe
düzeltilmesi gerekiyor. `92_varyans_ayrisimi.ipynb` §1, aynı katılımcı × koşul
tablosunda:

| Metrik | Shapiro p | RM-ANOVA | Friedman |
|---|---|---|---|
| `mae_angle_deg` | 0.99 | F(4,44) = 6.71, p = 0.0003 | p = 0.0014 |
| `stab_time_s` | 0.15 | F(4,44) = 3.18, p = 0.022 | p = 0.021 |
| `falls_angle_per_trial` | **0.0009** | F(4,44) = 3.16, p = 0.023 | p = 0.0051 |

İlk ikisinde normallik reddedilmiyor ve parametrik test aynı sonucu veriyor.
Üçüncüsünde normallik açıkça reddediliyor — sayım değişkeni olduğu için
beklenen bir şey — ve orada Friedman parametrik testten daha güçlü çıkıyor.

Yani sıralama tabanlı tercih **savunulabilir**, ama gerekçesi "sınanamaz"
değil: (a) karar metriklerinden biri gerçekten normal değil, (b) n = 12'de
Shapiro'nun gücü düşük olduğu için diğer ikisinde "reddedilmedi" ile "normal"
aynı şey değil, (c) üç metrik için tek bir test ailesinde kalmak tutarlı.
Hiçbir metrikte sonuç test ailesine bağlı olmadığı için karar etkilenmiyor.

| Soru | Test | Neden |
|---|---|---|
| Beş koşul arasında herhangi bir fark var mı | Friedman + Kendall's W | Tekrarlı ölçüm, non-parametrik omnibus |
| Hangi seviye baseline'dan farklı | Wilcoxon signed-rank + Holm | Eşleşmiş, exact, çoklu karşılaştırma düzeltmeli |
| **Şekil: U var mı** | ortogonal kontrast + tek örneklem Wilcoxon | Aşağıda |

## 3. Şekil testi — bu notebook'un asıl işi

Stochastic resonance bir **U şekli** iddiası: uçlar kötü, orta iyi. Bunu
"koşullar farklı mı" sorusuyla test edemezsin — monoton bozulma da farklılık
üretir. Şekli ayrı test etmek gerekiyor.

İki ortogonal polinom kontrastı:

| Kontrast | Ağırlıklar | Ne sorar |
|---|---|---|
| lineer | −2, −1, 0, +1, +2 | Noise arttıkça düzenli bir gidiş var mı |
| **kuadratik** | +2, −1, −2, −1, +2 | **Ortada tepe/çukur var mı — SR testi** |

Prosedür: her katılımcının beş koşul değerine ağırlıklar uygulanıp tek bir
skor çıkarılıyor (`arr @ weights`), sonra skorlar üzerinde **tek örneklem
Wilcoxon** (H₀: skorların medyanı sıfır). Yani "bu şekil bileşeni
katılımcılar arasında tutarlı olarak sıfırdan farklı mı".

**Ağırlıklar ordinal pozisyon üzerinden.** σ değerleri eşit aralıklı değil
(0, 0.02, 0.05, 0.08, 0.25) ve sıfır içerdiği için log alınamıyor. Ordinal
kontrast "sıradaki bir sonraki seviye" varsayımı yapıyor; σ ölçeğinde
gerçek aralıklar dikkate alınmıyor. Bu bir sınır, kayıtta dursun.

## 4. Kuadratik kontrastın yanına ikinci bir kontrol

Kontrast testi tek başına bırakılmadı, çünkü null bir kuadratik "U yok"
demenin en zayıf yolu. `decide.interior_optimum` doğrudan bakıyor:

- Grup ortalamasında en iyi koşul hangisi, **iç** bir koşul mu (N1/N2/N3)
- Kaç katılımcının kendi en iyisi bir iç koşul

Bu ikinci kontrol nüans üretti: **grup ortalamasında üç metrikte de en iyi
koşul N1**, yani sayısal tepe iç bir koşulda. Ama N1–baseline farkı hiçbir
metrikte anlamlı değil ve kuadratik kontrast null. Yorum: bu bir U değil,
no_noise ile N1'in ayırt edilemezliği.

`decide.personal_best` composite: her metrik katılımcı içinde z-skora
çevrilip yönüne göre işaretleniyor, metrikler ortalanıyor, en yüksek skorlu
koşul alınıyor. Sonuç 6 no_noise / 5 N1 / 1 N2 — kimsenin en iyisi N3 ya da
N4 değil.

## 5. Çoklu karşılaştırma: nerede düzeltildi, nerede düzeltilmedi

Holm **bir metriğin dört baseline karşılaştırması içinde** uygulandı.

Metrikler arası ek düzeltme **yapılmadı**, çünkü üç karar metriği bağımsız
aile değil.

**Düzeltme (2026-09-02).** Bu gerekçe önce `mae_angle_deg` ile
`rms_angle_deg` arasındaki r = 0.98'e dayandırılmıştı. O geçersiz bir
dayanak: `rms_angle_deg` karar metriği değil, dolayısıyla o korelasyon üç
karar metriğinin ilişkisi hakkında bir şey söylemiyor. Doğru sayılar, kişi
içi merkezlenmiş katılımcı × koşul tablosunda:

| | mae | stab | falls |
|---|---|---|---|
| `mae_angle_deg` | 1.00 | −0.86 | 0.42 |
| `stab_time_s` | −0.86 | 1.00 | −0.39 |
| `falls_angle_per_trial` | 0.42 | −0.39 | 1.00 |

mae ile stab birbirinin neredeyse kopyası; `falls_angle_per_trial` ise
kısmen ayrı bir bilgi taşıyor (r ≈ 0.4). Yani "üçü de aynı konstrukt"
ifadesi ilk ikisi için doğru, üçüncüsü için fazla güçlü.

Ama sonucu değiştirmiyor, çünkü düzeltme fiilen hesaplandı. Lineer
kontrastın üç metriğe Holm uygulanmış hali 0.0015 / 0.0049 / 0.0020 — üçü de
anlamlı kalıyor. Kuadratik zaten üçünde de 1.00'a düzeltiliyor. Karar
lineer/kuadratik kontrasta dayandığı için etkilenmiyor.

## 6. Duyarlılık kontrolleri

Karar iki seçime duyarlı olabilirdi; ikisi de test edildi.

**`valid_trial` (`decide.drop_invalid_trials`).** Unity 600 trial'ın 2'sini
`paused` işaretlemiş; NB01 o kolona bakmıyor (bilinen açık madde), ikisi de
analize giriyor. Çıkarıldığında koşul sıralaması aynı kalıyor ve tek bir p
değeri oynuyor: `stab_time_s` kuadratik 0.5693 → 0.6221. İkisi de anlamlılık
eşiğinden uzak, yani sonuç etkilenmiyor. (İlk hali "hiçbir p oynamıyor"
diyordu; §6'daki liste zaten 0.62 gösteriyordu, cümle fazla güçlüydü.)
Kural yine de NB01'e eklenmeli, ama karar buna bağlı değil.

**Stabilizasyon eşiği (`decide.threshold_sensitivity`).** `stab_time_s`
bizim eşiğimizle hesaplanıyor (|θ| ≤ 30°, gerekçe `Yontem/04`). Eşik bizim
seçimimiz olduğu için sonuç ona duyarlı olmamalı. 5°–45° taraması: her
eşikte lineer anlamlı (p ≤ 0.0068), hiçbirinde kuadratik anlamlı değil
(p = 0.38–0.57).

## 7. Neyi beslediği

Ana deneyin noise seviyesi seçimi. Aday sıralaması ve ekibe sorulacak soru
[../Pilot_Sonuc_Ozeti.md](../Pilot_Sonuc_Ozeti.md) → "Ana deney için aday
sıralaması" bölümünde.

## 8. Bu kayıtta olmayanlar

- **Güç analizi yok.** "Bu tasarımla ne kadar küçük bir etki saptanabilirdi"
  sorusu NB05'in işi. N1'in null çıkması "fark yok" değil, "bu örneklemle
  saptanamadı" demek. Kısmen kapandı: `92_varyans_ayrisimi.ipynb` varyans
  ayrışımını ve kişi içi güvenilirliği ölçtü, oradan gereken deneme sayısı
  için bir mertebe tahmini çıkıyor. Klasik güç analizi hâlâ yok.
- **Bayes faktörü hesaplanmadı.** Null bulguyu (N1 = baseline) kanıt olarak
  sunmak istersek gereken şey bu; şimdilik sadece "ayırt edilemedi" deniyor.
- **Action timing dahil değil** (NB04). Koşullar arasında ayırt edici
  olmadığı için karar setine girmedi.
