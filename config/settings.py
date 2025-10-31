"""
Uygulama Ayarları ve Sabitler
"""

# Uygulama Bilgileri
APP_NAME = "SQL Panel - Veritabanı Yönetim Sistemi"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Berkay AVCI"

# Pencere Ayarları
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION}"

# Renk Paleti
COLORS = {
    # Ana Renkler
    'primary': '#3498DB',  # Mavi
    'success': '#27AE60',  # Yeşil
    'danger': '#E74C3C',  # Kırmızı
    'warning': '#F39C12',  # Turuncu
    'info': '#9B59B6',  # Mor
    'dark': '#34495E',  # Koyu gri
    'light': '#ECF0F1',  # Açık gri

    # Arka Plan Renkleri
    'bg_dark': '#2C3E50',
    'bg_medium': '#34495E',
    'bg_light': '#F8F9FA',
    'bg_white': '#FFFFFF',

    # Metin Renkleri
    'text_white': '#FFFFFF',
    'text_dark': '#2C3E50',
    'text_gray': '#7F8C8D',
    'text_light': '#ECF0F1',

    # Durum Renkleri
    'status_active': '#2ECC71',
    'status_inactive': '#95A5A6',
    'status_error': '#E74C3C',

    # Treeview Renkleri
    'tree_even': '#F8F9FA',
    'tree_odd': '#FFFFFF',
    'tree_changed': '#FFF3CD',
    'tree_new': '#D1ECF1',
    'tree_deleted': '#F8D7DA',
}

# Font Ayarları
FONTS = {
    'title': ('Arial', 14, 'bold'),
    'subtitle': ('Arial', 12, 'bold'),
    'normal': ('Arial', 10),
    'small': ('Arial', 9),
    'code': ('Consolas', 11),
    'footer': ('Arial', 9, 'italic'),
}

# Veritabanı Ayarları
DB_SETTINGS = {
    'timeout': 10,  # Bağlantı timeout (saniye)
    'check_same_thread': False,  # Thread kontrolü
    'isolation_level': None,  # Otomatik commit
}

# Treeview Ayarları
TREEVIEW_SETTINGS = {
    'row_height': 25,
    'column_width': 120,
    'show_lines': True,
}

# Veri Önizleme Limitleri
DATA_LIMITS = {
    'preview_rows': 50,  # Tablo önizlemesinde gösterilecek satır
    'large_table_threshold': 1000,  # Büyük tablo uyarı limiti
    'max_export_rows': 100000,  # Excel export limiti
}

# Dosya Ayarları
FILE_TYPES = {
    'db': [("SQLite Database", "*.db"), ("All Files", "*.*")],
    'csv': [("CSV Files", "*.csv"), ("Text Files", "*.txt"), ("All Files", "*.*")],
    'excel': [("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")],
    'sql': [("SQL Files", "*.sql"), ("Text Files", "*.txt"), ("All Files", "*.*")],
}

# Hızlı Sorgular
QUICK_QUERIES = [
    ("📋 Tüm Veritabanları", "PRAGMA database_list;"),
    ("🗂️ Ana DB Tabloları", "SELECT name FROM sqlite_master WHERE type='table';"),
    ("🔗 Attached DB Tabloları", "SELECT name FROM attached_db.sqlite_master WHERE type='table';"),
    ("📊 Tablo Sayısı", "SELECT COUNT(*) as tablo_sayisi FROM sqlite_master WHERE type='table';"),
    ("🔍 Tablo Yapısı", "PRAGMA table_info(tablo_adi);"),
    ("🔢 Kayıt Sayısı", "SELECT COUNT(*) FROM tablo_adi;"),
    ("📅 Son Değişiklik", "SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name;"),
]

# Mesajlar
MESSAGES = {
    'no_db': "⚠️ Önce bir veritabanı açın!",
    'no_table': "⚠️ Önce bir tablo seçin!",
    'no_data': "⚠️ Gösterilecek veri yok!",
    'success': "✅ İşlem başarılı!",
    'error': "❌ Bir hata oluştu!",
    'confirm_delete': "❓ Silmek istediğinizden emin misiniz?",
    'confirm_close': "❓ Uygulamayı kapatmak istiyor musunuz?",
}

# İkonlar (Emoji)
ICONS = {
    'database': '🗄️',
    'table': '📋',
    'query': '🔍',
    'edit': '✏️',
    'add': '➕',
    'delete': '🗑️',
    'save': '💾',
    'export': '📤',
    'import': '📥',
    'refresh': '🔄',
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'connect': '🔗',
    'disconnect': '❌',
}