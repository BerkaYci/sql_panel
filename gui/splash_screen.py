"""
Splash Screen Modülü
Profesyonel açılış ekranı
"""

import tkinter as tk
from tkinter import ttk
import time
from config.settings import COLORS, APP_NAME, APP_VERSION, APP_AUTHOR, FONTS

class SplashScreen:
    """Profesyonel açılış ekranı sınıfı"""
    
    def __init__(self, root):
        self.root = root
        self.window = tk.Toplevel(root)
        
        # Pencere özelliklerini ayarla
        self.width = 600
        self.height = 350
        
        # Ekranın ortasına konumlandır
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        
        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")
        
        # Pencere dekorasyonunu kaldır (başlık çubuğu vs.)
        self.window.overrideredirect(True)
        
        # Arka plan rengi
        self.window.configure(bg=COLORS['bg_dark'])
        
        # Gölgelendirme efekti (Windows için opsiyonel, Linux'ta çalışmayabilir)
        # self.window.attributes('-alpha', 0.95)
        
        self.setup_ui()
        
        # Her zaman en üstte tut
        self.window.attributes('-topmost', True)
        self.window.update()

    def setup_ui(self):
        """Arayüz bileşenlerini oluştur"""
        
        # Ana container
        main_frame = tk.Frame(
            self.window, 
            bg=COLORS['bg_dark'], 
            bd=2, 
            relief="raised" # Hafif çerçeve efekti
        )
        main_frame.pack(fill="both", expand=True)
        
        # İçerik container
        content_frame = tk.Frame(main_frame, bg=COLORS['bg_dark'])
        content_frame.place(relx=0.5, rely=0.45, anchor="center")
        
        # Logo/İkon (Emoji olarak)
        icon_label = tk.Label(
            content_frame,
            text="🗄️",  # Database icon
            font=("Arial", 48),
            bg=COLORS['bg_dark'],
            fg=COLORS['primary']
        )
        icon_label.pack(pady=(0, 10))
        
        # Başlık
        title_label = tk.Label(
            content_frame,
            text=APP_NAME.split(' - ')[0], # Sadece ana isim
            font=("Segoe UI", 24, "bold"),
            bg=COLORS['bg_dark'],
            fg=COLORS['text_white']
        )
        title_label.pack(pady=5)
        
        # Alt Başlık
        subtitle_label = tk.Label(
            content_frame,
            text="Veritabanı Yönetim Sistemi",
            font=("Segoe UI", 12),
            bg=COLORS['bg_dark'],
            fg=COLORS['text_gray']
        )
        subtitle_label.pack(pady=0)
        
        # Version
        version_label = tk.Label(
            content_frame,
            text=f"v{APP_VERSION}",
            font=("Consolas", 10),
            bg=COLORS['bg_dark'],
            fg=COLORS['info']
        )
        version_label.pack(pady=(5, 20))
        
        # Loading Container (Alt kısım)
        self.loading_frame = tk.Frame(main_frame, bg=COLORS['bg_dark'])
        self.loading_frame.pack(side="bottom", fill="x", padx=40, pady=30)
        
        # Durum metni
        self.status_label = tk.Label(
            self.loading_frame,
            text="Başlatılıyor...",
            font=("Segoe UI", 9),
            bg=COLORS['bg_dark'],
            fg=COLORS['text_light'],
            anchor="w"
        )
        self.status_label.pack(fill="x", pady=(0, 5))
        
        # Custom Progress Bar Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Splash.Horizontal.TProgressbar",
            troughcolor=COLORS['bg_medium'],
            background=COLORS['primary'],
            bordercolor=COLORS['bg_dark'],
            lightcolor=COLORS['primary'],
            darkcolor=COLORS['primary']
        )
        
        # Progress Bar
        self.progress = ttk.Progressbar(
            self.loading_frame,
            style="Splash.Horizontal.TProgressbar",
            orient="horizontal",
            length=100,
            mode="determinate"
        )
        self.progress.pack(fill="x")
        
        # Copyright
        copyright_label = tk.Label(
            main_frame,
            text=f"© 2024 {APP_AUTHOR}",
            font=("Arial", 8),
            bg=COLORS['bg_dark'],
            fg=COLORS['text_gray']
        )
        copyright_label.place(relx=0.5, rely=0.95, anchor="center")

    def update_status(self, message, progress_value):
        """Durum ve ilerleme çubuğunu güncelle"""
        self.status_label.config(text=message)
        self.progress['value'] = progress_value
        self.window.update()

    def destroy(self):
        """Ekranı kapat"""
        self.window.destroy()
