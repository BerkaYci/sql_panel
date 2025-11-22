"""
Profesyonel açılış/loading ekranı
"""

from __future__ import annotations

import random
from typing import Callable, Optional

import tkinter as tk
from tkinter import ttk

from config.settings import APP_NAME, APP_VERSION, APP_AUTHOR, COLORS, FONTS


class LoadingScreen:
    """Minimal fakat profesyonel görünümlü splash ekranı."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.active = True
        self._pulse_job: Optional[str] = None
        self._tip_job: Optional[str] = None
        self._close_callback: Optional[Callable[[], None]] = None

        self.top = tk.Toplevel(root)
        self.top.overrideredirect(True)
        self.top.transient(root)
        self.top.configure(bg=COLORS['bg_dark'])
        self.top.attributes("-alpha", 0.0)
        self.top.attributes("-topmost", True)

        self.width = 560
        self.height = 340
        self._position_window()

        self._build_ui()
        self._fade_in()
        self._start_accent_animation()
        self._start_tip_rotation()

    def _position_window(self):
        """Splash ekranını ekran ortasına yerleştir."""
        self.top.update_idletasks()
        screen_w = self.top.winfo_screenwidth()
        screen_h = self.top.winfo_screenheight()
        pos_x = int((screen_w - self.width) / 2)
        pos_y = int((screen_h - self.height) / 2)
        self.top.geometry(f"{self.width}x{self.height}+{pos_x}+{pos_y}")

    def _build_ui(self):
        """Kart tarzı UI bileşenlerini oluştur."""
        card = tk.Frame(self.top, bg=COLORS['bg_white'], bd=0, highlightthickness=0)
        card.place(relx=0.5, rely=0.5, anchor="center", width=self.width - 40, height=self.height - 40)
        self.card = card

        self.accent_bar = tk.Frame(card, bg=COLORS['primary'], height=4)
        self.accent_bar.pack(fill="x")

        header = tk.Frame(card, bg=COLORS['bg_white'])
        header.pack(fill="x", padx=28, pady=(22, 8))

        title_font = (FONTS['title'][0], FONTS['title'][1] + 8, 'bold')
        subtitle_font = (FONTS['subtitle'][0], FONTS['subtitle'][1] + 1)

        tk.Label(
            header,
            text=APP_NAME,
            font=title_font,
            bg=COLORS['bg_white'],
            fg=COLORS['text_dark'],
            justify="left",
            wraplength=self.width - 80,
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Modüler SQLite operasyon merkezi",
            font=subtitle_font,
            bg=COLORS['bg_white'],
            fg=COLORS['text_gray'],
        ).pack(anchor="w", pady=(4, 0))

        badge_frame = tk.Frame(card, bg=COLORS['bg_white'])
        badge_frame.pack(fill="x", padx=28, pady=(0, 18))

        self._create_badge(badge_frame, f"Sürüm {APP_VERSION}")
        self._create_badge(badge_frame, f"{APP_AUTHOR}")
        self._create_badge(badge_frame, "Çoklu veritabanı")

        insights = tk.Frame(card, bg=COLORS['bg_white'])
        insights.pack(fill="x", padx=28, pady=(0, 10))
        insight_items = [
            ("⚡", "Optimize sorgu motoru"),
            ("🛡️", "Güvenli bağlantı yönetimi"),
            ("📊", "Veri düzenleme araçları"),
        ]
        for icon, text in insight_items:
            tk.Label(
                insights,
                text=f"{icon} {text}",
                font=FONTS['small'],
                bg=COLORS['bg_white'],
                fg=COLORS['text_gray'],
            ).pack(side="left", padx=(0, 12))

        progress_frame = tk.Frame(card, bg=COLORS['bg_white'])
        progress_frame.pack(fill="x", padx=28, pady=(4, 8))

        style = ttk.Style(self.top)
        style.theme_use("clam")
        style.configure(
            "Loading.Horizontal.TProgressbar",
            troughcolor=COLORS['bg_light'],
            background=COLORS['primary'],
            bordercolor=COLORS['bg_light'],
            lightcolor=COLORS['primary'],
            darkcolor=COLORS['dark'],
            thickness=14,
        )

        self.progress = ttk.Progressbar(
            progress_frame,
            style="Loading.Horizontal.TProgressbar",
            maximum=100,
            mode="determinate",
        )
        self.progress.pack(fill="x")

        info_frame = tk.Frame(card, bg=COLORS['bg_white'])
        info_frame.pack(fill="x", padx=28, pady=(6, 10))

        self.message_var = tk.StringVar(value="Uygulama başlatılıyor")
        self.percent_var = tk.StringVar(value="%00")

        self.message_label = tk.Label(
            info_frame,
            textvariable=self.message_var,
            font=FONTS['normal'],
            bg=COLORS['bg_white'],
            fg=COLORS['text_dark'],
        )
        self.message_label.pack(side="left")

        self.percent_label = tk.Label(
            info_frame,
            textvariable=self.percent_var,
            font=(FONTS['subtitle'][0], FONTS['subtitle'][1] + 2, 'bold'),
            bg=COLORS['bg_white'],
            fg=COLORS['primary'],
        )
        self.percent_label.pack(side="right")

        divider = tk.Frame(card, bg=COLORS['bg_light'], height=1)
        divider.pack(fill="x", padx=28, pady=(4, 10))

        self.tip_var = tk.StringVar(value="")
        self.tip_label = tk.Label(
            card,
            textvariable=self.tip_var,
            font=FONTS['small'],
            bg=COLORS['bg_white'],
            fg=COLORS['text_gray'],
            wraplength=self.width - 80,
            justify="left",
        )
        self.tip_label.pack(fill="x", padx=28)

        footer = tk.Frame(card, bg=COLORS['bg_white'])
        footer.pack(side="bottom", fill="x", padx=28, pady=16)

        tk.Label(
            footer,
            text="SQL Panel yükleniyor",
            font=FONTS['normal'],
            bg=COLORS['bg_white'],
            fg=COLORS['text_gray'],
        ).pack(side="left")

        tk.Label(
            footer,
            text="Hazırlanıyor...",
            font=FONTS['small'],
            bg=COLORS['bg_white'],
            fg=COLORS['text_gray'],
        ).pack(side="right")

        self.tips = [
            "CTRL + ENTER ile sorguları anında çalıştırabilirsiniz.",
            "Tablolar sekmesinden şema ve veri önizlemesine aynı anda erişin.",
            "Kaydedilmiş sorgularınızı JSON olarak dışa aktararak paylaşın.",
            "Veri düzenleme sekmesi lazy loading ile büyük tabloları hızla getirir.",
            "Performans araçları sayesinde sorgu maliyetlerini takip edin.",
        ]
        random.shuffle(self.tips)
        self._tip_index = 0

        self.accent_colors = [
            "#1B4F72",
            "#21618C",
            "#2471A3",
            "#2E86C1",
            "#3498DB",
            "#5DADE2",
        ]
        self._accent_step = 0

    def _create_badge(self, parent: tk.Frame, text: str):
        """Mini bilgi etiketleri."""
        tk.Label(
            parent,
            text=text,
            font=FONTS['small'],
            bg=COLORS['bg_light'],
            fg=COLORS['text_dark'],
            padx=10,
            pady=4,
        ).pack(side="left", padx=(0, 8))

    def _fade_in(self, alpha: float = 0.0):
        """Nazik fade-in efekti."""
        if not self.active:
            return
        next_alpha = min(alpha + 0.08, 1.0)
        self.top.attributes("-alpha", next_alpha)
        if next_alpha < 1.0:
            self.top.after(20, self._fade_in, next_alpha)

    def _start_accent_animation(self):
        """Accent bar ve yüzde rengi için canlı animasyon."""
        if not self.active:
            return
        color = self.accent_colors[self._accent_step % len(self.accent_colors)]
        self.accent_bar.configure(bg=color)
        self.percent_label.configure(fg=color)
        self._accent_step += 1
        self._pulse_job = self.top.after(180, self._start_accent_animation)

    def _start_tip_rotation(self):
        """İpucu metinlerini döndür."""
        if not self.active or not self.tips:
            return
        tip = self.tips[self._tip_index % len(self.tips)]
        self.tip_var.set(f"💡 {tip}")
        self._tip_index += 1
        self._tip_job = self.top.after(3200, self._start_tip_rotation)

    def update_stage(self, message: str, progress: int):
        """Mesaj ve progress değerini güncelle."""
        if not self.active:
            return
        safe_value = max(0, min(100, progress))
        self.message_var.set(message)
        self.percent_var.set(f"%{safe_value:02d}")
        self.progress['value'] = safe_value
        self.top.update_idletasks()

    def finish(self, callback: Optional[Callable[[], None]] = None):
        """Yükleme tamamlandığında kapanma animasyonu."""
        if not self.active:
            if callback:
                callback()
            return
        self.update_stage("SQL Panel hazır", 100)
        self.top.after(350, lambda: self.close(callback))

    def close(self, callback: Optional[Callable[[], None]] = None):
        """Fade-out ile pencereyi kapat."""
        if not self.active:
            if callback:
                callback()
            return
        self._close_callback = callback
        self._fade_out(1.0)

    def force_close(self, callback: Optional[Callable[[], None]] = None):
        """Herhangi bir animasyon olmadan pencereyi kapat."""
        if not self.active:
            if callback:
                callback()
            return
        self.active = False
        if self._pulse_job:
            self.top.after_cancel(self._pulse_job)
        if self._tip_job:
            self.top.after_cancel(self._tip_job)
        self.top.destroy()
        if callback:
            callback()

    def _fade_out(self, alpha: float):
        """Fade-out animasyonu."""
        if not self.active:
            return
        next_alpha = alpha - 0.12
        if next_alpha <= 0:
            callback = self._close_callback
            self.force_close(callback)
            self._close_callback = None
        else:
            self.top.attributes("-alpha", next_alpha)
            self.top.after(20, self._fade_out, next_alpha)
