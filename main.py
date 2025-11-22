"""
SQL Panel - Modüler Veritabanı Yönetim Sistemi
Ana Başlatıcı Dosya
"""

import sys
import os
import time
import tkinter as tk
from pathlib import Path

# Modülleri import et
try:
    from gui.splash_screen import SplashScreen
    from gui.main_window import MainWindow
except ImportError as e:
    print("❌ Gerekli kütüphaneler eksik!")
    print("Lütfen şu komutu çalıştırın:")
    print("pip install pandas openpyxl")
    print(f"\nDetaylı hata: {e}")
    sys.exit(1)

def main():
    """Uygulamayı başlat"""
    try:
        # Ana pencereyi oluştur ama gizle
        root = tk.Tk()
        root.withdraw()
        
        # Splash screen'i göster
        splash = SplashScreen(root)
        splash.update_status("Sistem başlatılıyor...", 0)
        
        # 1. Konfigürasyon Yükleme
        splash.update_status("Ayarlar yükleniyor...", 20)
        time.sleep(0.5) # Kullanıcı görsün diye kısa bekleme
        
        # 2. Core Modülleri Hazırlama
        splash.update_status("Veritabanı sürücüleri kontrol ediliyor...", 40)
        # Burada gerekirse ağır importlar yapılabilir
        time.sleep(0.5)
        
        # 3. Arayüz Hazırlığı
        splash.update_status("Kullanıcı arayüzü oluşturuluyor...", 60)
        
        # Ana uygulamayı başlat
        # Bu kısım MainWindow init içindeki işlemleri yapar
        app = MainWindow(root)
        
        # 4. Son Hazırlıklar
        splash.update_status("Eklentiler yükleniyor...", 80)
        time.sleep(0.5)
        
        splash.update_status("Hazır!", 100)
        time.sleep(0.3)
        
        # Splash'i kapat ve ana pencereyi göster
        splash.destroy()
        root.deiconify()
        
        # Windows'ta tam ekran yap
        if os.name == 'nt':
            root.state('zoomed')
        
        # Event loop'u başlat
        app.run()
        
    except Exception as e:
        print(f"❌ Uygulama başlatılamadı: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
