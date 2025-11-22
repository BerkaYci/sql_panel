"""
Loading Ekranı Modülü
Modern ve profesyonel yükleme ekranı
"""

import tkinter as tk
from tkinter import ttk, Canvas
import threading
import time
import math

from config.settings import COLORS, FONTS, APP_NAME, APP_VERSION


class LoadingScreen:
    """Modern loading ekranı"""

    def __init__(self, parent=None):
        # Toplevel window (bağımsız pencere)
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self.root.title("")
        
        # Pencere ayarları
        self.width = 600
        self.height = 400
        self.setup_window()
        
        # Loading durumu
        self.is_loading = True
        self.progress_value = 0
        self.current_message = "Başlatılıyor..."
        
        # GUI elemanları
        self.setup_gui()
        
        # Animasyon thread'i
        self.animation_thread = None
        
    def setup_window(self):
        """Pencere özelliklerini ayarla"""
        # Pencereyi ortala
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        
        # Pencere özelliklerini ayarla
        self.root.overrideredirect(True)  # Başlık çubuğunu kaldır
        self.root.attributes('-topmost', True)  # Her zaman üstte
        
        # Windows için şeffaflık
        if self.root.tk.call('tk', 'windowingsystem') == 'win32':
            self.root.attributes('-alpha', 0.95)
        
        # Gölge efekti için arka plan
        self.root.configure(bg='black')
        
    def setup_gui(self):
        """GUI elemanlarını oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.root, bg=COLORS['bg_dark'])
        main_frame.place(x=2, y=2, width=self.width-4, height=self.height-4)
        
        # Canvas (gradient arka plan için)
        self.canvas = Canvas(
            main_frame,
            width=self.width-4,
            height=self.height-4,
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Köşe yuvarlama efekti için kenar çizgileri
        self.create_rounded_corners()
        
        # Gradient arka plan
        self.create_gradient()
        
        # Logo veya başlık
        self.title_label = tk.Label(
            self.canvas,
            text=APP_NAME,
            font=('Arial', 24, 'bold'),
            fg=COLORS['text_white'],
            bg=COLORS['bg_dark']
        )
        self.canvas.create_window(
            self.width//2, 100,
            window=self.title_label
        )
        
        # Versiyon
        version_label = tk.Label(
            self.canvas,
            text=f"v{APP_VERSION}",
            font=('Arial', 12),
            fg=COLORS['text_gray'],
            bg=COLORS['bg_dark']
        )
        self.canvas.create_window(
            self.width//2, 140,
            window=version_label
        )
        
        # Animasyonlu loading circle
        self.loading_circle_id = None
        self.create_loading_circle()
        
        # Progress bar arka planı (daha modern görünüm için)
        progress_bg = tk.Frame(self.canvas, bg=COLORS['bg_medium'], height=8)
        progress_bg_window = self.canvas.create_window(
            self.width//2, 280,
            window=progress_bg,
            width=300
        )
        
        # Progress bar
        self.progress_style = ttk.Style()
        self.progress_style.theme_use('clam')
        self.progress_style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor=COLORS['bg_medium'],
            background=COLORS['primary'],
            bordercolor=COLORS['bg_dark'],
            lightcolor=COLORS['primary'],
            darkcolor=COLORS['primary'],
            borderwidth=0,
            relief='flat'
        )
        
        self.progress = ttk.Progressbar(
            self.canvas,
            style="Custom.Horizontal.TProgressbar",
            length=300,
            mode='determinate',
            maximum=100
        )
        self.canvas.create_window(
            self.width//2, 280,
            window=self.progress
        )
        
        # Yükleme mesajı
        self.message_label = tk.Label(
            self.canvas,
            text=self.current_message,
            font=('Arial', 11),
            fg=COLORS['text_light'],
            bg=COLORS['bg_dark']
        )
        self.canvas.create_window(
            self.width//2, 320,
            window=self.message_label
        )
        
        # İlerleme yüzdesi
        self.percent_label = tk.Label(
            self.canvas,
            text="0%",
            font=('Arial', 10, 'bold'),
            fg=COLORS['primary'],
            bg=COLORS['bg_dark']
        )
        self.canvas.create_window(
            self.width//2 + 170, 280,
            window=self.percent_label
        )
        
        # Alt bilgi
        footer_label = tk.Label(
            self.canvas,
            text="Lütfen bekleyin...",
            font=('Arial', 9),
            fg=COLORS['text_gray'],
            bg=COLORS['bg_dark']
        )
        self.canvas.create_window(
            self.width//2, 360,
            window=footer_label
        )
        
    def create_rounded_corners(self):
        """Köşe yuvarlama efekti"""
        # Modern köşe çizgileri
        corner_size = 20
        
        # Sol üst köşe
        self.canvas.create_arc(0, 0, corner_size*2, corner_size*2, 
                              start=90, extent=90, outline=COLORS['bg_dark'], 
                              width=2, style='arc')
        
        # Sağ üst köşe
        self.canvas.create_arc(self.width-corner_size*2-4, 0, self.width-4, corner_size*2, 
                              start=0, extent=90, outline=COLORS['bg_dark'], 
                              width=2, style='arc')
        
        # Sol alt köşe
        self.canvas.create_arc(0, self.height-corner_size*2-4, corner_size*2, self.height-4, 
                              start=180, extent=90, outline=COLORS['bg_dark'], 
                              width=2, style='arc')
        
        # Sağ alt köşe
        self.canvas.create_arc(self.width-corner_size*2-4, self.height-corner_size*2-4, 
                              self.width-4, self.height-4, 
                              start=270, extent=90, outline=COLORS['bg_dark'], 
                              width=2, style='arc')
    
    def create_gradient(self):
        """Gradient arka plan oluştur"""
        # Gradient renkleri
        color1 = COLORS['bg_dark']
        color2 = COLORS['bg_medium']
        
        # Canvas boyutları
        width = self.width - 4
        height = self.height - 4
        
        # Gradient çiz
        for i in range(height):
            # Renk geçişi hesapla
            ratio = i / height
            r1 = int(color1[1:3], 16)
            g1 = int(color1[3:5], 16)
            b1 = int(color1[5:7], 16)
            
            r2 = int(color2[1:3], 16)
            g2 = int(color2[3:5], 16)
            b2 = int(color2[5:7], 16)
            
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            
            color = f"#{r:02x}{g:02x}{b:02x}"
            
            self.canvas.create_line(
                0, i, width, i,
                fill=color, width=1
            )
    
    def create_loading_circle(self):
        """Animasyonlu loading circle oluştur"""
        center_x = self.width // 2
        center_y = 200
        radius = 30
        
        # Daire parçaları
        self.circle_parts = []
        parts = 12
        
        # Glow efekti için arka plan dairesi
        self.glow_circle = self.canvas.create_oval(
            center_x - radius - 15, center_y - radius - 15,
            center_x + radius + 15, center_y + radius + 15,
            fill='', outline=self.adjust_color_opacity(COLORS['primary'], 0.1),
            width=30
        )
        
        for i in range(parts):
            angle = i * (360 / parts)
            start_angle = angle - 30
            
            part = self.canvas.create_arc(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                start=start_angle,
                extent=30,
                outline=COLORS['primary'],
                width=3,
                style='arc'
            )
            self.circle_parts.append(part)
            
        # Merkez nokta (pulse efekti için)
        self.center_dot = self.canvas.create_oval(
            center_x - 5, center_y - 5,
            center_x + 5, center_y + 5,
            fill=COLORS['primary'], outline=''
        )
    
    def animate_loading_circle(self):
        """Loading circle animasyonu"""
        angle = 0
        pulse_size = 0
        pulse_direction = 1
        glow_opacity = 0.1
        glow_direction = 1
        
        while self.is_loading:
            # Dönen parçalar animasyonu
            for i, part in enumerate(self.circle_parts):
                # Opaklık efekti
                opacity = 1.0 - (i * 0.08)
                color = self.adjust_color_opacity(COLORS['primary'], opacity)
                self.canvas.itemconfig(part, outline=color)
            
            # Listeyi döndür
            self.circle_parts.append(self.circle_parts.pop(0))
            
            # Pulse efekti (merkez nokta)
            pulse_size += pulse_direction * 0.5
            if pulse_size > 3 or pulse_size < -3:
                pulse_direction *= -1
            
            center_x = self.width // 2
            center_y = 200
            self.canvas.coords(
                self.center_dot,
                center_x - 5 - pulse_size, center_y - 5 - pulse_size,
                center_x + 5 + pulse_size, center_y + 5 + pulse_size
            )
            
            # Glow efekti animasyonu
            glow_opacity += glow_direction * 0.02
            if glow_opacity > 0.3 or glow_opacity < 0.1:
                glow_direction *= -1
            
            glow_color = self.adjust_color_opacity(COLORS['primary'], glow_opacity)
            self.canvas.itemconfig(self.glow_circle, outline=glow_color)
            
            self.root.update()
            time.sleep(0.05)
    
    def adjust_color_opacity(self, hex_color, opacity):
        """Renk opaklığını ayarla"""
        # Basit bir yaklaşım - rengi beyaza yaklaştır
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        r = int(r + (255 - r) * (1 - opacity))
        g = int(g + (255 - g) * (1 - opacity))
        b = int(b + (255 - b) * (1 - opacity))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def update_progress(self, value, message=None):
        """Progress değerini güncelle"""
        self.progress_value = min(100, max(0, value))
        self.progress['value'] = self.progress_value
        
        # Yüzde göstergesini güncelle
        self.percent_label.config(text=f"{int(self.progress_value)}%")
        
        if message:
            self.current_message = message
            self.message_label.config(text=message)
        
        self.root.update()
    
    def start_animation(self):
        """Animasyonları başlat"""
        self.animation_thread = threading.Thread(
            target=self.animate_loading_circle,
            daemon=True
        )
        self.animation_thread.start()
    
    def show(self):
        """Loading ekranını göster"""
        # Fade in efekti
        for i in range(0, 11):
            if self.root.tk.call('tk', 'windowingsystem') == 'win32':
                self.root.attributes('-alpha', i/10)
            self.root.update()
            time.sleep(0.02)
        
        # Animasyonu başlat
        self.start_animation()
    
    def hide(self):
        """Loading ekranını gizle"""
        self.is_loading = False
        
        # Progress'i tamamla
        for i in range(int(self.progress_value), 101, 2):
            self.update_progress(i)
            time.sleep(0.01)
        
        # Tamamlandı mesajı
        self.update_progress(100, "✅ Yükleme tamamlandı!")
        time.sleep(0.5)
        
        # Fade out efekti
        for i in range(10, -1, -1):
            if self.root.tk.call('tk', 'windowingsystem') == 'win32':
                self.root.attributes('-alpha', i/10)
            self.root.update()
            time.sleep(0.02)
        
        self.root.destroy()
    
    def simulate_loading(self, tasks):
        """Yükleme simülasyonu (örnek kullanım için)"""
        total_tasks = len(tasks)
        
        for i, (task_name, duration) in enumerate(tasks):
            # Mesajı güncelle
            self.update_progress(
                (i / total_tasks) * 100,
                f"⏳ {task_name}..."
            )
            
            # Görevi simüle et
            time.sleep(duration)
        
        # Tamamla
        self.hide()


class SplashScreen(LoadingScreen):
    """Özel splash screen versiyonu"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Özel ayarlar
        self.width = 500
        self.height = 350
        
        # Logo ekle (eğer varsa)
        self.add_logo()
    
    def add_logo(self):
        """Logo veya özel grafik ekle"""
        # SQL Panel için özel bir logo tasarımı
        logo_frame = tk.Frame(self.canvas, bg=COLORS['bg_dark'])
        self.canvas.create_window(
            self.width//2, 80,
            window=logo_frame
        )
        
        # SQL sembolü
        sql_label = tk.Label(
            logo_frame,
            text="< SQL >",
            font=('Consolas', 28, 'bold'),
            fg=COLORS['primary'],
            bg=COLORS['bg_dark']
        )
        sql_label.pack()
        
        # Panel metni
        panel_label = tk.Label(
            logo_frame,
            text="PANEL",
            font=('Arial', 20, 'bold'),
            fg=COLORS['text_white'],
            bg=COLORS['bg_dark']
        )
        panel_label.pack()


# Test için
if __name__ == "__main__":
    # Loading screen testi
    loading = LoadingScreen()
    loading.show()
    
    # Örnek görevler
    tasks = [
        ("Veritabanı bağlantısı kuruluyor", 0.5),
        ("Modüller yükleniyor", 0.8),
        ("Arayüz hazırlanıyor", 0.6),
        ("Ayarlar yükleniyor", 0.4),
        ("Önbellek temizleniyor", 0.3),
    ]
    
    loading.simulate_loading(tasks)