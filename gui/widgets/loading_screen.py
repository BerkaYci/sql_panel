"""
Profesyonel Loading Screen Widget
Animasyonlu spinner ve progress bar ile modern yükleme ekranı
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from config.settings import *


class LoadingScreen:
    """Profesyonel loading screen widget"""

    def __init__(self, parent, message: str = "Yükleniyor...", 
                 show_progress: bool = False, cancelable: bool = False):
        """
        Loading screen oluştur
        
        Args:
            parent: Parent widget (tk.Tk veya tk.Toplevel)
            message: Gösterilecek mesaj
            show_progress: Progress bar gösterilsin mi
            cancelable: İptal butonu gösterilsin mi
        """
        self.parent = parent
        self.message = message
        self.show_progress = show_progress
        self.cancelable = cancelable
        self.cancelled = False
        
        # Ana pencere
        self.window = tk.Toplevel(parent)
        self.window.title("Yükleniyor...")
        self.window.geometry("450x250")
        self.window.resizable(False, False)
        
        # Pencereyi merkeze al
        self._center_window()
        
        # Pencereyi modal yap (opsiyonel - kullanıcı etkileşimini engelle)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Arka plan rengi
        self.window.configure(bg=COLORS['bg_white'])
        
        # UI oluştur
        self._create_ui()
        
        # Animasyon başlat
        self.animation_running = True
        self.animation_thread = None
        self._start_animation()

    def _center_window(self):
        """Pencereyi ekranın ortasına yerleştir"""
        self.window.update_idletasks()
        
        # Parent pencerenin pozisyonunu al
        try:
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
        except:
            parent_x = 0
            parent_y = 0
            parent_width = 1920
            parent_height = 1080
        
        # Loading penceresinin boyutunu al
        width = 450
        height = 250
        
        # Merkez koordinatlarını hesapla
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def _create_ui(self):
        """UI bileşenlerini oluştur"""
        # Ana container
        main_frame = tk.Frame(self.window, bg=COLORS['bg_white'])
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Logo/Icon alanı (spinner için)
        icon_frame = tk.Frame(main_frame, bg=COLORS['bg_white'], height=80)
        icon_frame.pack(fill="x", pady=(0, 20))
        icon_frame.pack_propagate(False)
        
        # Spinner canvas (animasyonlu daire)
        self.spinner_canvas = tk.Canvas(
            icon_frame,
            width=80,
            height=80,
            bg=COLORS['bg_white'],
            highlightthickness=0
        )
        self.spinner_canvas.pack()
        
        # Mesaj label
        self.message_label = tk.Label(
            main_frame,
            text=self.message,
            bg=COLORS['bg_white'],
            fg=COLORS['text_dark'],
            font=FONTS['subtitle'],
            wraplength=350
        )
        self.message_label.pack(pady=(0, 15))
        
        # Progress bar (opsiyonel)
        if self.show_progress:
            self.progress_var = tk.DoubleVar()
            self.progress_bar = ttk.Progressbar(
                main_frame,
                variable=self.progress_var,
                maximum=100,
                length=350,
                mode='determinate'
            )
            self.progress_bar.pack(pady=(0, 10))
            
            self.progress_label = tk.Label(
                main_frame,
                text="0%",
                bg=COLORS['bg_white'],
                fg=COLORS['text_gray'],
                font=FONTS['small']
            )
            self.progress_label.pack()
        else:
            # Indeterminate progress bar (sürekli animasyon)
            self.progress_bar = ttk.Progressbar(
                main_frame,
                maximum=100,
                length=350,
                mode='indeterminate'
            )
            self.progress_bar.pack(pady=(0, 10))
            self.progress_bar.start(10)  # Animasyonu başlat
        
        # İptal butonu (opsiyonel)
        if self.cancelable:
            cancel_frame = tk.Frame(main_frame, bg=COLORS['bg_white'])
            cancel_frame.pack(pady=(10, 0))
            
            cancel_btn = tk.Button(
                cancel_frame,
                text="İptal",
                command=self._on_cancel,
                bg=COLORS['danger'],
                fg=COLORS['text_white'],
                font=FONTS['normal'],
                padx=20,
                pady=5,
                relief="flat",
                cursor="hand2"
            )
            cancel_btn.pack()

    def _start_animation(self):
        """Spinner animasyonunu başlat"""
        self.angle = 0
        self._animate_spinner()

    def _animate_spinner(self):
        """Spinner animasyonunu çiz"""
        if not self.animation_running:
            return
        
        # Canvas'ı temizle
        self.spinner_canvas.delete("all")
        
        # Merkez koordinatları
        center_x, center_y = 40, 40
        radius = 30
        
        # 8 noktalı spinner çiz
        num_points = 8
        for i in range(num_points):
            angle = (self.angle + (i * 360 / num_points)) * 3.14159 / 180
            x = center_x + radius * 0.7 * (angle / 3.14159)
            y = center_y + radius * 0.7 * (angle / 3.14159)
            
            # Opacity hesapla (fade efekti)
            opacity = 1.0 - (i / num_points) * 0.7
            
            # Renk hesapla
            r = int(int(COLORS['primary'][1:3], 16) * opacity)
            g = int(int(COLORS['primary'][3:5], 16) * opacity)
            b = int(int(COLORS['primary'][5:7], 16) * opacity)
            color = f"#{r:02x}{g:02x}{b:02x}"
            
            # Nokta çiz
            self.spinner_canvas.create_oval(
                x - 5, y - 5, x + 5, y + 5,
                fill=color,
                outline=""
            )
        
        # Açıyı güncelle
        self.angle = (self.angle + 15) % 360
        
        # Sonraki frame'i planla
        self.window.after(50, self._animate_spinner)

    def _on_cancel(self):
        """İptal butonuna tıklandığında"""
        self.cancelled = True
        self.close()

    def update_message(self, message: str):
        """Mesajı güncelle"""
        self.message = message
        if hasattr(self, 'message_label'):
            self.message_label.config(text=message)
        self.window.update_idletasks()

    def update_progress(self, value: float, max_value: float = 100):
        """Progress bar'ı güncelle (0-100 arası)"""
        if not self.show_progress:
            return
        
        percentage = min(100, max(0, (value / max_value) * 100))
        self.progress_var.set(percentage)
        
        if hasattr(self, 'progress_label'):
            self.progress_label.config(text=f"{percentage:.1f}%")
        
        self.window.update_idletasks()

    def close(self):
        """Loading screen'i kapat"""
        self.animation_running = False
        if hasattr(self, 'progress_bar') and not self.show_progress:
            self.progress_bar.stop()
        
        try:
            self.window.destroy()
        except:
            pass

    def is_cancelled(self) -> bool:
        """İptal edildi mi kontrol et"""
        return self.cancelled


class LoadingOverlay:
    """Pencere üzerinde overlay loading ekranı (daha hafif)"""
    
    def __init__(self, parent, message: str = "Yükleniyor..."):
        """
        Overlay loading ekranı oluştur
        
        Args:
            parent: Parent widget
            message: Gösterilecek mesaj
        """
        self.parent = parent
        self.message = message
        
        # Overlay frame (tüm pencereyi kaplar)
        self.overlay = tk.Frame(
            parent,
            bg='#000000',
            cursor="wait"
        )
        self.overlay.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Merkez container
        center_frame = tk.Frame(
            self.overlay,
            bg=COLORS['bg_white'],
            relief="raised",
            bd=2
        )
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # İçerik
        content_frame = tk.Frame(center_frame, bg=COLORS['bg_white'])
        content_frame.pack(padx=40, pady=30)
        
        # Spinner
        spinner_frame = tk.Frame(content_frame, bg=COLORS['bg_white'], height=60)
        spinner_frame.pack(pady=(0, 15))
        spinner_frame.pack_propagate(False)
        
        self.spinner_canvas = tk.Canvas(
            spinner_frame,
            width=60,
            height=60,
            bg=COLORS['bg_white'],
            highlightthickness=0
        )
        self.spinner_canvas.pack()
        
        # Mesaj
        self.message_label = tk.Label(
            content_frame,
            text=message,
            bg=COLORS['bg_white'],
            fg=COLORS['text_dark'],
            font=FONTS['subtitle']
        )
        self.message_label.pack()
        
        # Animasyon başlat
        self.angle = 0
        self._animate_spinner()
    
    def _animate_spinner(self):
        """Spinner animasyonu"""
        self.spinner_canvas.delete("all")
        
        center_x, center_y = 30, 30
        radius = 20
        
        num_points = 8
        for i in range(num_points):
            angle_rad = (self.angle + (i * 360 / num_points)) * 3.14159 / 180
            x = center_x + radius * 0.6 * (angle_rad / 3.14159)
            y = center_y + radius * 0.6 * (angle_rad / 3.14159)
            
            opacity = 1.0 - (i / num_points) * 0.7
            
            r = int(int(COLORS['primary'][1:3], 16) * opacity)
            g = int(int(COLORS['primary'][3:5], 16) * opacity)
            b = int(int(COLORS['primary'][5:7], 16) * opacity)
            color = f"#{r:02x}{g:02x}{b:02x}"
            
            self.spinner_canvas.create_oval(
                x - 4, y - 4, x + 4, y + 4,
                fill=color,
                outline=""
            )
        
        self.angle = (self.angle + 15) % 360
        self.parent.after(50, self._animate_spinner)
    
    def update_message(self, message: str):
        """Mesajı güncelle"""
        self.message = message
        if hasattr(self, 'message_label'):
            self.message_label.config(text=message)
    
    def close(self):
        """Overlay'i kapat"""
        try:
            self.overlay.destroy()
        except:
            pass
