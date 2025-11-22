# SQL Panel - Veritabanı Yönetim Sistemi

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

## 📖 Hakkında

SQL Panel, SQLite veritabanları için geliştirilmiş modern ve kullanıcı dostu bir masaüstü yönetim aracıdır. Çoklu veritabanı desteği, görsel veri düzenleme, Excel/CSV entegrasyonu ve performans optimizasyonu özellikleri ile profesyonel veritabanı yönetimini kolaylaştırır.

## ✨ Özellikler

### 🗄️ Veritabanı Yönetimi
- Çoklu veritabanı bağlantısı
- ATTACH database desteği
- Veritabanı bilgileri görüntüleme
- Backup ve vacuum işlemleri

### 🔍 SQL Sorgu Editörü
- Syntax highlighting
- Sorgu geçmişi
- Sorgu kaydetme ve yönetme
- Hızlı sorgu şablonları
- Batch sorgu desteği

### 📊 Veri Görüntüleme ve Düzenleme
- Tablo verilerini görüntüleme
- Satır bazlı veri düzenleme
- Filtreleme ve sıralama
- Excel benzeri veri girişi

### 📤 Import/Export
- Excel dosyası okuma/yazma
- CSV dosyası desteği
- Formatlı Excel export
- Toplu veri aktarımı

### ⚡ Performans
- Büyük veri setleri için sayfalama
- Progressive loading
- Sorgu optimizasyonu
- Bellek yönetimi

## 🚀 Kurulum

### Gereksinimler
- Python 3.8 veya üzeri
- pip paket yöneticisi

### Adımlar

1. Projeyi klonlayın:
```bash
git clone https://github.com/kullanici/sql-panel.git
cd sql-panel
```

2. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

3. Uygulamayı başlatın:
```bash
python main.py
```

## 💻 Kullanım

### Ana Sekmeler

#### 1. SQL Sorguları
- SQL sorguları yazın ve çalıştırın
- Sonuçları tablo formatında görüntüleyin
- Sorguları kaydedin ve yönetin

#### 2. Sorgularım
- Kayıtlı sorguları kategorilere göre düzenleyin
- Hızlı arama ve filtreleme
- Sorgu düzenleme ve silme

#### 3. Veritabanları
- Yeni veritabanı oluşturma
- Mevcut veritabanlarını açma
- ATTACH işlemleri
- Veritabanı bilgilerini görüntüleme

#### 4. Tablolar
- Tablo listesini görüntüleme
- Tablo yapısını inceleme
- Veri önizleme
- Tablo işlemleri

#### 5. Veri Düzenleme
- Satır ekleme/silme/güncelleme
- Excel benzeri veri girişi
- Toplu değişiklik yapma
- Değişiklikleri kaydetme

### Kısa Yollar

- `Ctrl+Enter`: Sorguyu çalıştır
- `Ctrl+S`: Sorguyu kaydet
- `Ctrl+O`: Veritabanı aç
- `Ctrl+N`: Yeni veritabanı
- `F5`: Yenile

## 📁 Proje Yapısı

```
sql-panel/
├── config/           # Uygulama ayarları
├── core/            # İş mantığı katmanı
├── gui/             # Kullanıcı arayüzü
│   ├── tabs/        # Uygulama sekmeleri
│   └── widgets/     # Özel bileşenler
├── utils/           # Yardımcı araçlar
├── main.py          # Ana başlatıcı
└── requirements.txt # Bağımlılıklar
```

## 🔧 Yapılandırma

`config/settings.py` dosyasından:
- Pencere boyutları
- Renk temaları
- Font ayarları
- Veri limitleri
- Dosya türleri

## 📊 Desteklenen Özellikler

### Veritabanı İşlemleri
- ✅ CREATE, ALTER, DROP
- ✅ SELECT, INSERT, UPDATE, DELETE
- ✅ JOIN, UNION, SUBQUERY
- ✅ PRAGMA komutları
- ✅ Transaction desteği

### Veri Tipleri
- ✅ INTEGER, REAL, TEXT
- ✅ BLOB, NULL
- ✅ DATE, DATETIME

### Export Formatları
- ✅ Excel (.xlsx, .xls)
- ✅ CSV (.csv)
- ✅ SQL Script (.sql)

## 🤝 Katkıda Bulunma

1. Projeyi fork edin
2. Feature branch oluşturun (`git checkout -b feature/YeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Branch'e push edin (`git push origin feature/YeniOzellik`)
5. Pull Request açın

## 🐛 Bilinen Sorunlar

- Çok büyük BLOB verileri görüntülenemeyebilir
- Bazı özel karakterler export sırasında sorun çıkarabilir

## 📜 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 👤 Geliştirici

**Berkay AVCI**

- GitHub: [@berkayavci](https://github.com/berkayavci)
- Email: berkay@example.com

## 🙏 Teşekkürler

- Python topluluğuna
- Tkinter dokümantasyonu
- pandas ve openpyxl geliştiricilerine

---
⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!