"""
SQL Panel - Modüler Veritabanı Yönetim Sistemi
Ana Başlatıcı Dosya
"""

import sys
from pathlib import Path
import threading
import time

# Modülleri import et
from gui.widgets.loading_screen import LoadingScreen
from gui.main_window import MainWindow


def load_application(loading_screen):
    """
    Uygulamayı arka planda yükle
    Args:
        loading_screen: LoadingScreen nesnesi
    """
    try:
        # Adım 1: Modülleri yükle
        loading_screen.update_progress(20, "Modüller yükleniyor...")
        time.sleep(0.3)
        
        # Adım 2: Yapılandırma dosyalarını yükle
        loading_screen.update_progress(40, "Yapılandırma yükleniyor...")
        time.sleep(0.3)
        
        # Adım 3: Veritabanı bağlantılarını hazırla
        loading_screen.update_progress(60, "Veritabanı hazırlanıyor...")
        time.sleep(0.3)
        
        # Adım 4: GUI bileşenlerini oluştur
        loading_screen.update_progress(80, "Arayüz hazırlanıyor...")
        
        # Ana pencereyi oluştur
        app = MainWindow()
        
        # Adım 5: Tamamlandı
        loading_screen.update_progress(100, "Başlatılıyor...")
        time.sleep(0.3)
        
        # Loading screen'i fade-out ile kapat
        loading_screen.fade_out()
        
        # Ana uygulamayı başlat
        app.run()
        
    except ImportError as e:
        loading_screen.close()
        print("❌ Gerekli kütüphaneler eksik!")
        print("Lütfen şu komutu çalıştırın:")
        print("pip install pandas openpyxl")
        print(f"\nDetaylı hata: {e}")
    except Exception as e:
        loading_screen.close()
        print(f"❌ Uygulama başlatılamadı: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Uygulamayı başlat"""
    # Profesyonel loading screen oluştur
    loading_screen = LoadingScreen()
    
    # Uygulamayı arka planda yükle
    loading_thread = threading.Thread(
        target=load_application,
        args=(loading_screen,),
        daemon=True
    )
    loading_thread.start()
    
    # Loading screen'i göster
    loading_screen.window.mainloop()


if __name__ == "__main__":
    main()