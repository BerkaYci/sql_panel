SQL Panel – Modüler SQLite Yönetim Aracı
=======================================

Python + Tkinter ile geliştirilen SQL Panel, birden fazla SQLite veritabanını tek arayüzden yönetmenizi sağlar. Sorgu yazma, tablo önizleme, veri düzenleme, Excel/CSV içe–dışa aktarma, kaydedilmiş sorgular ve bağlantı bakımı gibi günlük veri operasyonlarını hızlandırır.

Öne Çıkan Özellikler
--------------------
- 🔍 **SQL Sorgu Editörü**: Otomatik LIMIT önerisi, performans ölçümü, sonuç treeview’u ve Excel’e aktarım.
- 🗂️ **Çoklu Veritabanı Yönetimi**: DB oluşturma/açma/attach, aktif bağlantı takibi, VACUUM/backup işlemleri.
- 📊 **Tablo Gezgini**: Şema bilgisi, veri önizleme, büyük tablo uyarıları ve güvenli DROP akışı.
- ✏️ **Veri Düzenleme**: Sayfalama, lazy loading, cache, Excel’den toplu güncelleme ve değişiklik takip sistemi.
- 💾 **Sorgu Kutuphanesi**: Kaydet, kategorize et, JSON’a export/import yap, SQL sekmesine tek tıkla gönder.
- ⚙️ **Performans Araçları**: `DataPaginator`, `ProgressiveLoader`, `SmartCache` ile büyük veri setlerinde akıcı deneyim.

Kurulum
-------
1. Depoyu klonlayın veya kaynak dosyaları indirin.
2. Bir sanal ortam oluşturup etkinleştirin (önerilir):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

Çalıştırma
----------
```bash
python main.py
```
Uygulama Tkinter penceresi açar. Menü çubuğundan veritabanı oluşturup açtıktan sonra sekmeler (SQL Sorguları, Sorgularım, Veritabanları, Tablolar, Veri Düzenleme) aktif hale gelir.

Proje Yapısı
------------
```
config/              # Uygulama ayarları, renk & ikon sabitleri
core/                # Veritabanı yönetimi, sorgu yürütücü, kaydedilmiş sorgular
gui/                 # Tkinter ana pencere, sekmeler ve widget'lar
utils/               # Excel/CSV handler'ları, performans optimizasyon araçları
saved_queries.json   # Varsayılan sorgu arşivi
main.py              # Uygulama giriş noktası
```

Geliştirme / Test
-----------------
- Python 3.10+ önerilir (Tkinter + pandas uyumluluğu için).
- GUI’yi çalıştırmadan önce `saved_queries.json` yazma iznine sahip olduğunuzdan emin olun.
- Çekirdek modüller için birim testler `tests/` klasöründedir; çalıştırmak için:
  ```bash
  python -m unittest discover tests
  ```

Geri Bildirim & Katkı
---------------------
Hata, öneri veya katkılarınız için issue/pull request açabilirsiniz. Büyük dataset senaryolarında gözlemlediğiniz performans notları özellikle değerlidir.
