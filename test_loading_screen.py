#!/usr/bin/env python3
"""
Loading ekranını test etmek için script
"""

import tkinter as tk
import time
import threading
from gui.widgets.loading_screen import LoadingScreen, SplashScreen


def test_loading_screen():
    """LoadingScreen test fonksiyonu"""
    # Root pencere (gizli)
    root = tk.Tk()
    root.withdraw()
    
    # Loading ekranı
    loading = LoadingScreen(root)
    loading.show()
    
    # Test görevleri
    def simulate_tasks():
        tasks = [
            ("Sistem kontrolleri yapılıyor", 10),
            ("Veritabanı bağlantısı kuruluyor", 20),
            ("Modüller yükleniyor", 35),
            ("Arayüz bileşenleri hazırlanıyor", 50),
            ("Kullanıcı ayarları yükleniyor", 65),
            ("Tema dosyaları kontrol ediliyor", 75),
            ("Eklentiler başlatılıyor", 85),
            ("Son dokunuşlar yapılıyor", 95),
        ]
        
        for message, progress in tasks:
            loading.update_progress(progress, f"⏳ {message}...")
            time.sleep(0.8)
        
        loading.hide()
        root.quit()
    
    # Thread'de çalıştır
    task_thread = threading.Thread(target=simulate_tasks)
    task_thread.start()
    
    # Ana döngü
    root.mainloop()


def test_splash_screen():
    """SplashScreen test fonksiyonu"""
    # Root pencere (gizli)
    root = tk.Tk()
    root.withdraw()
    
    # Splash ekranı
    splash = SplashScreen(root)
    splash.show()
    
    # Test görevleri
    tasks = [
        ("Başlatılıyor", 0.5),
        ("Çekirdek modüller yükleniyor", 0.8),
        ("Veritabanı servisleri", 0.6),
        ("Kullanıcı arayüzü", 0.7),
        ("Son kontroller", 0.5),
    ]
    
    splash.simulate_loading(tasks)
    root.quit()


if __name__ == "__main__":
    print("Loading Screen Test'i başlatılıyor...")
    print("1 - Normal Loading Screen")
    print("2 - Splash Screen")
    
    choice = input("Seçiminiz (1 veya 2): ").strip()
    
    if choice == "1":
        test_loading_screen()
    elif choice == "2":
        test_splash_screen()
    else:
        print("Geçersiz seçim!")