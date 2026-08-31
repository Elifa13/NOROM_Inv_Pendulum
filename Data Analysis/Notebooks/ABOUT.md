# Notebooks

Zincir sırayla çalışır; her biri bir öncekinin parquet çıktısını okur.
Notebook'lar ince — mantık `../src/` altında.

| # | Notebook | İçerik | Durum |
|---|---|---|---|
| 01 | `01_load_qc.ipynb` | Drive'dan çekme, yükleme, yapısal bütünlük, zaman/sinyal kontrolleri, QC bayrakları, analiz maskesi, randomizasyon doğrulaması | çalıştı, 12 katılımcı |
| 02 | `02_build.ipynb` | Fizik modeli doğrulaması, episode + regime run segmentasyonu, state, action sınıfları, T₀, event tespiti | çalıştı, 12 katılımcı |
| 03 | `03_performance.ipynb` | Trial düzeyi metrikler, metrik seti seçimi, katılımcı × koşul birimine toplama | çalıştı, 12 katılımcı |
| 04 | `04_control.ipynb` | Action timing (Ludolph), hız tabakalama, action variability, açı bandı taraması. I/CR/D/A dağılımı öncelik dışı bırakıldı | çalıştı, 12 katılımcı |
| 05 | Learning | Pilotta varyans/güç tahmini; koşullar arası öğrenme karşılaştırması DEĞİL | **yazılmadı** |
| 06 | Noise kararı | Koşul × metrik tablosu, U-şekil kontrolü, aday seçimi | **yazılmadı** |
| 90 | `90_sunum.ipynb` | Acil sunum. **İzole** — `presentation.py` kullanır, zincirin parçası değil, silinse zincir etkilenmez | çalıştı, 12 katılımcı |

## Zincir mantığı

02 var çünkü 03 ve 04 aynı türetmeyi iki kere yapmasın. 04, 05'ten önce
çünkü learning kriteri action timing'i girdi olarak kullanıyor.

Drive'dan veri çekme NB01'in ilk hücresinde (`sync_data`); yeni katılımcı
geldiğinde o hücreyi çalıştırmak yeterli, var olan dosyalar tekrar
indirilmez.

## Çalıştırma

Notebook'lar repo kökündeki `.venv` kernel'ini kullanıyor. Paket kurulumu
her notebook'un ilk hücresinde `%pip install` ile — terminal pip'i farklı
bir Python'a kurabiliyor.

## Yöntem kayıtları

Bir notebook'un neden öyle hesapladığı `../../Documentation/Yontem/`
altında. NB03'ün metrik seti kararları ve NB04'ün action timing transfer kararları orada.
