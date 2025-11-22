"""
Profesyonel Loading Screen Widget
Modern animasyonlu yükleme ekranı
"""

import tkinter as tk
from tkinter import ttk
import math
import threading


class LoadingScreen:
    """Profesyonel animasyonlu loading ekranı"""
    
    def __init__(self, parent=None):
        """
        Loading screen oluştur
        Args:
            parent: Ana pencere (None ise kendi penceresini oluşturur)
        """
        # Ana pencere
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            self.window = tk.Tk()
        
        # Pencere ayarları
        self.window.title("Loading...")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        
        # Pencereyi merkeze al
        self.center_window()
        
        # Pencereyi en üstte tut
        self.window.attributes('-topmost', True)
        
        # Pencere çerçevesini kaldır (modern görünüm)
        self.window.overrideredirect(True)
        
        # Animasyon değişkenleri
        self.spinner_angle = 0
        self.progress_value = 0
        self.fade_alpha = 0
        self.is_running = True
        self.animation_speed = 50  # ms
        
        # Renkler (Gradient için)
        self.colors = {
            'bg_start': '#2C3E50',
            'bg_end': '#34495E',
            'primary': '#3498DB',
            'secondary': '#2980B9',
            'accent': '#1ABC9C',
            'text': '#ECF0F1',
            'text_gray': '#BDC3C7',
        }
        
        # GUI oluştur
        self.setup_gui()
        
        # Fade-in animasyonu başlat
        self.fade_in()
        
        # Spinner animasyonu başlat
        self.animate_spinner()
    
    def center_window(self):
        """Pencereyi ekranın ortasına yerleştir"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_gui(self):
        """GUI bileşenlerini oluştur"""
        # Ana container (gradient arkaplan için)
        self.main_frame = tk.Frame(
            self.window,
            bg=self.colors['bg_start'],
            highlightthickness=2,
            highlightbackground=self.colors['primary']
        )
        self.main_frame.pack(fill="both", expand=True)
        
        # Logo/Title Frame
        title_frame = tk.Frame(self.main_frame, bg=self.colors['bg_start'])
        title_frame.pack(pady=40)
        
        # Ana başlık
        self.title_label = tk.Label(
            title_frame,
            text="🗄️ SQL Panel",
            font=('Arial', 28, 'bold'),
            bg=self.colors['bg_start'],
            fg=self.colors['text']
        )
        self.title_label.pack()
        
        # Alt başlık
        self.subtitle_label = tk.Label(
            title_frame,
            text="Veritabanı Yönetim Sistemi",
            font=('Arial', 12),
            bg=self.colors['bg_start'],
            fg=self.colors['text_gray']
        )
        self.subtitle_label.pack(pady=5)
        
        # Spinner Canvas
        self.canvas = tk.Canvas(
            self.main_frame,
            width=120,
            height=120,
            bg=self.colors['bg_start'],
            highlightthickness=0
        )
        self.canvas.pack(pady=30)
        
        # Status label
        self.status_label = tk.Label(
            self.main_frame,
            text="Yükleniyor...",
            font=('Arial', 11),
            bg=self.colors['bg_start'],
            fg=self.colors['text']
        )
        self.status_label.pack(pady=10)
        
        # Progress bar frame
        progress_frame = tk.Frame(self.main_frame, bg=self.colors['bg_start'])
        progress_frame.pack(pady=20, padx=50, fill="x")
        
        # Custom progress bar (Canvas kullanarak)
        self.progress_canvas = tk.Canvas(
            progress_frame,
            width=400,
            height=8,
            bg=self.colors['bg_start'],
            highlightthickness=0
        )
        self.progress_canvas.pack()
        
        # Progress bar arka plan
        self.progress_canvas.create_rectangle(
            0, 0, 400, 8,
            fill=self.colors['bg_end'],
            outline=self.colors['bg_end'],
            tags="bg"
        )
        
        # Progress bar dolgu
        self.progress_bar = self.progress_canvas.create_rectangle(
            0, 0, 0, 8,
            fill=self.colors['primary'],
            outline=self.colors['secondary'],
            tags="progress"
        )
        
        # Version label
        version_label = tk.Label(
            self.main_frame,
            text="v2.0.0",
            font=('Arial', 9, 'italic'),
            bg=self.colors['bg_start'],
            fg=self.colors['text_gray']
        )
        version_label.pack(side="bottom", pady=10)
    
    def animate_spinner(self):
        """Spinner animasyonu"""
        if not self.is_running:
            return
        
        # Canvas'ı temizle
        self.canvas.delete("spinner")
        
        # Dönen daire segmentleri çiz
        center_x = 60
        center_y = 60
        radius = 40
        segments = 12
        
        for i in range(segments):
            angle = (self.spinner_angle + (i * 360 / segments)) % 360
            angle_rad = math.radians(angle)
            
            # Segment başlangıç noktası
            x1 = center_x + radius * math.cos(angle_rad)
            y1 = center_y + radius * math.sin(angle_rad)
            
            # Segment bitiş noktası (daha kısa)
            x2 = center_x + (radius - 15) * math.cos(angle_rad)
            y2 = center_y + (radius - 15) * math.sin(angle_rad)
            
            # Opacity efekti (fade effect)
            opacity = 1 - (i / segments)
            color = self.interpolate_color(
                self.colors['primary'],
                self.colors['bg_start'],
                opacity
            )
            
            # Çizgi kalınlığı
            width = 4 if i < segments // 4 else 3
            
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=color,
                width=width,
                capstyle="round",
                tags="spinner"
            )
        
        # Açıyı artır
        self.spinner_angle = (self.spinner_angle + 10) % 360
        
        # Animasyonu devam ettir
        self.window.after(self.animation_speed, self.animate_spinner)
    
    def interpolate_color(self, color1, color2, factor):
        """İki renk arasında interpolasyon yap"""
        # Hex to RGB
        c1 = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
        c2 = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))
        
        # Interpolate
        r = int(c1[0] * factor + c2[0] * (1 - factor))
        g = int(c1[1] * factor + c2[1] * (1 - factor))
        b = int(c1[2] * factor + c2[2] * (1 - factor))
        
        # RGB to Hex
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def update_progress(self, value, status_text=None):
        """
        Progress bar'ı güncelle
        Args:
            value: 0-100 arası değer
            status_text: Gösterilecek durum metni
        """
        self.progress_value = max(0, min(100, value))
        
        # Progress bar'ı güncelle
        width = (400 * self.progress_value) / 100
        self.progress_canvas.coords(self.progress_bar, 0, 0, width, 8)
        
        # Renk geçişi efekti
        if self.progress_value < 30:
            color = self.colors['accent']
        elif self.progress_value < 70:
            color = self.colors['primary']
        else:
            color = self.colors['secondary']
        
        self.progress_canvas.itemconfig(self.progress_bar, fill=color)
        
        # Status text güncelle
        if status_text:
            self.status_label.config(text=status_text)
        
        self.window.update()
    
    def fade_in(self):
        """Fade-in animasyonu"""
        if self.fade_alpha < 1.0:
            self.fade_alpha += 0.05
            try:
                self.window.attributes('-alpha', self.fade_alpha)
            except:
                pass  # Bazı sistemlerde alpha desteği olmayabilir
            
            self.window.after(20, self.fade_in)
    
    def fade_out(self, callback=None):
        """
        Fade-out animasyonu
        Args:
            callback: Animasyon bitince çağrılacak fonksiyon
        """
        self.is_running = False
        
        if self.fade_alpha > 0:
            self.fade_alpha -= 0.1
            try:
                self.window.attributes('-alpha', self.fade_alpha)
            except:
                pass
            
            self.window.after(30, lambda: self.fade_out(callback))
        else:
            if callback:
                callback()
            self.close()
    
    def close(self):
        """Loading screen'i kapat"""
        self.is_running = False
        try:
            self.window.destroy()
        except:
            pass
    
    def show(self):
        """Loading screen'i göster"""
        self.window.deiconify()
    
    def hide(self):
        """Loading screen'i gizle"""
        self.window.withdraw()


# Test için
if __name__ == "__main__":
    import time
    
    # Loading screen oluştur
    loading = LoadingScreen()
    
    def simulate_loading():
        """Yükleme simülasyonu"""
        steps = [
            (20, "Modüller yükleniyor..."),
            (40, "Veritabanı bağlantısı kuruluyor..."),
            (60, "GUI hazırlanıyor..."),
            (80, "Bileşenler başlatılıyor..."),
            (100, "Tamamlandı!")
        ]
        
        for progress, text in steps:
            time.sleep(0.5)
            loading.update_progress(progress, text)
        
        time.sleep(0.5)
        loading.fade_out()
    
    # Thread'de yükle
    thread = threading.Thread(target=simulate_loading, daemon=True)
    thread.start()
    
    # Ana loop
    loading.window.mainloop()
