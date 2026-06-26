# 🧠 CFG'den PDA'e Otomatik Dönüştürücü ve Yığınlı Otomat Simülatörü

Bu proje; Otomata Teorisi, Biçimsel Diller ve Derleyici Tasarımı (Compiler Design) prensipleri doğrultusunda geliştirilmiş, **Bağlamdan Bağımsız Gramerleri (CFG)** otomatik olarak eşdeğer birer **Yığınlı Otomata (Pushdown Automata - PDA)** dönüştüren bir derleyici mimarisi ve adım adım çalışan görsel simülatör uygulamasıdır.

---

##  Proje Mimarisi ve Modüler Dağılım

Proje, kuramsal bilgisayar bilimi kurallarını nesne modellerine dönüştüren 4 ana Python scripti ve veri katmanlarından oluşur:

### 1. Çekirdek ve Derleyici Katmanı (Compiler Layer)
* **`pda_olusturucu.py`**: Sistemin matematiksel kalbidir. JSON formatındaki CFG üretim kurallarını okur; yığın başlangıç sembollerini ($), değişken açılımlarını (`push`) ve terminal eşleşme (`pop`) lojiklerini uygulayarak kuralları otomatik olarak durum geçiş matrislerine dönüştürür.

### 2. Dosya İşleme ve Veri Katmanı (Data Layer)
* **`dosya_okuma.py`**: Gramer dosyalarını bütünlük kontrolünden geçirerek doğrular, boş string (Epsilon - ε) sembollerini normalize eder.
* **`gramer.json` & `gramer_a_bm_c2n.json`**: Test edilecek dillerin ($L = \{a^n b^n\}$ ve $L = \{a^n b^m c^{2n}\}$) matematiksel tanımlamalarını barındıran konfigürasyon dosyaları.
* **`girdiler.txt`**: Otomatın kabul veya reddetme performansını ölçmek için kullanılan örnek kelime listeleri.

### 3. Görsel Arayüz Katmanı (GUI Layer)
* **`arayuz.py` & `main.py`**: `Tkinter` kütüphanesi ile tasarlanmış gelişmiş simülasyon ekranı. Çalışma zamanında (Runtime) otomatın anlık durumunu (`State`), girdi bandında okunan karakterleri, kalan string dizilimini ve dinamik yığının (`Stack`) anlık derinliğini görselleştirir.

---

##  Öne Çıkan Fonksiyonel Özellikler

* **Çoklu Oynatma Modları:** Simülasyon; adımları tek tek incelemek için "İleri/Geri" butonu ile manuel veya otomatın akışını izlemek için "Otomatik Oynat" modunda çalıştırılabilir.
* **Dinamik Yığın Görselleştirme:** Yığının (Stack) RAM üzerindeki anlık doluluk ve boşalma hareketleri arayüzdeki liste panelinde gerçek zamanlı olarak grafiksel takip edilebilir.
* **Epsilon (ε) Kontrolü:** Girdi bandından karakter tüketmeden yığın manipülasyonu yapabilen epsilon geçişleri hatasız olarak simüle edilir.

---

##  Kurulum ve Çalıştırma Talimatı

Uygulama standart Python kütüphanelerini temel aldığı için harici hiçbir `pip` paket bağımlılığına ihtiyaç duymaz.

1. Bu depoyu bilgisayarınıza indirin veya klonlayın.
2. Tüm dosyaların **aynı klasör içinde** olduğundan emin olun.
3. Terminal veya Komut İstemi'ni (CMD) açarak proje klasör dizinine gidin.
4. Simülatörü başlatmak için şu komutu çalıştırın:
   ```bash
   python main.py
