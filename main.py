"""
SQL Panel - Modüler Veritabanı Yönetim Sistemi
Ana Başlatıcı Dosya
"""

import sys
from pathlib import Path
import tkinter as tk
import threading
import time

# Modülleri import et
from gui.main_window import MainWindow
from gui.widgets.loading_screen import SplashScreen

def load_application(loading_screen, root):
    """Uygulamayı yükle ve loading ekranını güncelle"""
    try:
        # Adım 1: Temel modülleri yükle
        loading_screen.update_progress(10, "📦 Modüller yükleniyor...")
        time.sleep(0.3)
        
        # Adım 2: Veritabanı bileşenlerini yükle
        loading_screen.update_progress(25, "🗄️ Veritabanı yöneticisi hazırlanıyor...")
        from core.database_manager import DatabaseManager
        time.sleep(0.2)
        
        # Adım 3: Sorgu yürütücüsünü yükle
        loading_screen.update_progress(40, "🔍 Sorgu yürütücüsü başlatılıyor...")
        from core.query_executor import QueryExecutor
        time.sleep(0.2)
        
        # Adım 4: GUI bileşenlerini yükle
        loading_screen.update_progress(55, "🎨 Arayüz bileşenleri hazırlanıyor...")
        from gui.tabs import QueryTab, DatabasesTab, TablesTab, EditorTab, MyQueriesTab
        time.sleep(0.3)
        
        # Adım 5: Ana pencereyi oluştur
        loading_screen.update_progress(70, "🏗️ Ana pencere oluşturuluyor...")
        app = MainWindow(root)
        time.sleep(0.2)
        
        # Adım 6: Ayarları yükle
        loading_screen.update_progress(85, "⚙️ Ayarlar yükleniyor...")
        from core.saved_queries_manager import SavedQueriesManager
        time.sleep(0.2)
        
        # Adım 7: Son kontroller
        loading_screen.update_progress(95, "✨ Son dokunuşlar yapılıyor...")
        time.sleep(0.3)
        
        # Tamamlandı
        loading_screen.update_progress(100, "✅ Başlatma tamamlandı!")
        time.sleep(0.5)
        
        # Loading ekranını kapat
        loading_screen.hide()
        
        # Ana pencereyi göster
        root.deiconify()
        
        return app
        
    except Exception as e:
        loading_screen.hide()
        raise e

def main():
    """Uygulamayı başlat"""
    try:
        # Ana Tkinter root'u oluştur ama gizle
        root = tk.Tk()
        root.withdraw()  # Pencereyi gizle
        
        # Loading ekranını göster
        loading_screen = SplashScreen(root)
        loading_screen.show()
        
        # Thread'de uygulamayı yükle
        app_ref = {'app': None}
        
        def load_thread():
            app_ref['app'] = load_application(loading_screen, root)
        
        load_thread = threading.Thread(target=load_thread)
        load_thread.daemon = True
        load_thread.start()
        
        # Loading ekranının event loop'unu çalıştır
        while load_thread.is_alive():
            loading_screen.root.update()
            time.sleep(0.01)
        
        # Uygulama yüklendiyse çalıştır
        if app_ref['app']:
            root.mainloop()
            
    except ImportError as e:
        print("❌ Gerekli kütüphaneler eksik!")
        print("Lütfen şu komutu çalıştırın:")
        print("pip install pandas openpyxl")
        print(f"\nDetaylı hata: {e}")
    except Exception as e:
        print(f"❌ Uygulama başlatılamadı: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()