# Notebooks

Zincir sırayla çalışır; her biri bir öncekinin parquet çıktısını okur.
Notebook'lar ince — mantık `../src/` altında.

**İki kopya var.** Bu klasördekiler `pilot1` verisini (12 katılımcı),
`pilot2/` altındakiler `pilot2` verisini (9 katılımcı) işler. Tek fark ilk
hücredeki `DATASET` değişkeni; `src/` çoğaltılmadı. Aşağıdaki durum sütunu
pilot1'e ait. Pilot2 sonuçları:
`../../Documentation/Pilot2_Sonuc_Ozeti.md`.

| # | Notebook | İçerik | Durum |
|---|---|---|---|
| 01 | `01_load_qc.ipynb` | Drive'dan çekme, yükleme, yapısal bütünlük, zaman/sinyal kontrolleri, QC bayrakları, analiz maskesi, randomizasyon doğrulaması | çalıştı, 12 katılımcı |
| 02 | `02_build.ipynb` | Fizik modeli doğrulaması, episode + regime run segmentasyonu, state, action sınıfları, T₀, event tespiti | çalıştı, 12 katılımcı |
| 03 | `03_performance.ipynb` | Trial düzeyi metrikler, metrik seti seçimi, katılımcı × koşul birimine toplama | çalıştı, 12 katılımcı |
| 04 | `04_control.ipynb` | Action timing (Ludolph), hız tabakalama, action variability, açı bandı taraması. I/CR/D/A dağılımı öncelik dışı bırakıldı | çalıştı, 12 katılımcı |
| 05 | Learning | Pilotta varyans/güç tahmini; koşullar arası öğrenme karşılaştırması DEĞİL | **yazılmadı** |
| 06 | `06_noise_decision.ipynb` | Friedman + Wilcoxon/Holm, lineer ve kuadratik trend kontrastları, U-şekil kontrolü, duyarlılık, aday seçimi | çalıştı, 12 katılımcı |
| 90 | `90_sunum.ipynb` | Acil sunum. **İzole** — `presentation.py` kullanır, zincirin parçası değil, silinse zincir etkilenmez | çalıştı, 12 katılımcı |
| 91 | `91_control_variability.ipynb` | Kontrol değişkenliği: Welch spektrumu, sample entropy, aksiyon aralıkları. **İzole** — kendi içinde tanımlı, `src/` modülü yok, zincirin parçası değil | çalıştı, koşul etkisi yok |
| 92 | `92_varyans_ayrisimi.ipynb` | Varyans ayrışımı (kişi/koşul/artık), ICC, split-half güvenilirlik, öğrenme kontrolü. **İzole** — kendi içinde tanımlı, `src/` modülü yok, zincirin parçası değil | çalıştı, 12 katılımcı |
| 93 | `93_ogrenme_ve_varyans.ipynb` | Trial düzeyi varyans ayrışımı (kişi/koşul/öğrenme/artık), koşul başına öğrenme eğimi ve eğimin güvenilirliği. **İzole** | çalıştı, 12 katılımcı |

## Zincir mantığı

02 var çünkü 03 ve 04 aynı türetmeyi iki kere yapmasın. 04, 05'ten önce
çünkü learning kriteri action timing'i girdi olarak kullanıyor. (Bu gerekçe
NB04'ten sonra kısmen geçersiz: action timing koşullar arasında ayırt edici
çıkmadı ve karar setine girmedi.)

90'lı seri izole. Zincirin hiçbir parçası onları okumaz, ve onlar da sadece
`data/interim` okur. 91 ve 92 repo kuralının (mantık `src/` altında, notebook
ince) dışında duruyor: ikisi de keşif taraması, bir sonuçları karara girerse
mantık `src/`'ye taşınır ve `Yontem/` altında kaydı açılır.

Drive'dan veri çekme NB01'in ilk hücresinde (`sync_data`); yeni katılımcı
geldiğinde o hücreyi çalıştırmak yeterli, var olan dosyalar tekrar
indirilmez. Hangi Drive klasörünün çekileceği aktif `DATASET`'ten gelir.

## Çalıştırma

Notebook'lar repo kökündeki `.venv` kernel'ini kullanıyor. Paket kurulumu
her notebook'un ilk hücresinde `%pip install` ile — terminal pip'i farklı
bir Python'a kurabiliyor.

## Yöntem kayıtları

Bir notebook'un neden öyle hesapladığı `../../Documentation/Yontem/`
altında. NB03'ün metrik seti kararları ve NB04'ün action timing transfer kararları orada.
