"""
Profesyonel görünümlü yükleme ekranı bileşeni.
"""

import tkinter as tk
from tkinter import ttk

from config.settings import COLORS, FONTS, APP_NAME, APP_VERSION


class LoadingScreen:
    """Uygulama başlatılırken gösterilen splash ekranı."""

    def __init__(self, parent: tk.Tk):
        self.parent = parent
        self.splash = tk.Toplevel(parent)
        self.splash.withdraw()
        self.splash.overrideredirect(True)
        self.splash.configure(bg=COLORS['bg_dark'])
        self.splash.resizable(False, False)
        self.splash.attributes('-topmost', True)

        self.status_var = tk.StringVar(value="Başlatılıyor...")
        self.detail_var = tk.StringVar(value="Çekirdek servisler yükleniyor")
        self.progress_var = tk.DoubleVar(value=0)

        self._tip_index = 0
        self._tip_cycle_job = None
        self._detail_override = False
        self._fade_job = None
        self._indeterminate = True

        self._tips = [
            "Sorgu motoru optimize ediliyor",
            "Veritabanı bağlantıları doğrulanıyor",
            "Akıllı önbellek hazırlanıyor",
            "Güvenlik politikaları uygulanıyor",
            "Modüler arayüz bileşenleri yükleniyor",
            "İleri seviye raporlama araçları etkinleştiriliyor",
        ]

        self._build_ui()
        self._center_window()
        self.splash.deiconify()
        self.splash.lift()
        self._start_tip_cycle()

    def _build_ui(self):
        style = ttk.Style(self.splash)
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass

        style.configure(
            "Loading.Horizontal.TProgressbar",
            troughcolor=COLORS['bg_medium'],
            background=COLORS['primary'],
            bordercolor=COLORS['bg_medium'],
            lightcolor=COLORS['primary'],
            darkcolor=COLORS['primary'],
        )

        container = tk.Frame(self.splash, bg=COLORS['bg_dark'])
        container.pack(fill="both", expand=True, padx=24, pady=24)

        card = tk.Frame(
            container,
            bg=COLORS['bg_medium'],
            bd=0,
            highlightthickness=0,
            relief="flat"
        )
        card.pack(fill="both", expand=True)
        card.pack_propagate(False)

        accent = tk.Frame(card, bg=COLORS['primary'], height=5)
        accent.pack(fill="x", side="top")

        content = tk.Frame(card, bg=COLORS['bg_medium'])
        content.pack(fill="both", expand=True, padx=30, pady=25)

        title = tk.Label(
            content,
            text=APP_NAME,
            font=('Arial', 18, 'bold'),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_white'],
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            content,
            text=f"v{APP_VERSION} • Profesyonel SQL kontrol paneli",
            font=FONTS['small'],
            bg=COLORS['bg_medium'],
            fg=COLORS['text_light'],
        )
        subtitle.pack(anchor="w", pady=(4, 20))

        badge_frame = tk.Frame(content, bg=COLORS['bg_medium'])
        badge_frame.pack(anchor="w", pady=(0, 20))

        for text in ("Kurumsal güvenlik", "Canlı performans izleme"):
            badge = tk.Label(
                badge_frame,
                text=f"● {text}",
                font=FONTS['small'],
                bg=COLORS['bg_medium'],
                fg=COLORS['text_light'],
                padx=10,
                pady=2,
            )
            badge.pack(side="left", padx=(0, 10))

        status_label = tk.Label(
            content,
            textvariable=self.status_var,
            font=FONTS['subtitle'],
            bg=COLORS['bg_medium'],
            fg=COLORS['text_white'],
        )
        status_label.pack(anchor="w")

        detail_label = tk.Label(
            content,
            textvariable=self.detail_var,
            font=FONTS['normal'],
            bg=COLORS['bg_medium'],
            fg=COLORS['text_light'],
        )
        detail_label.pack(anchor="w", pady=(2, 12))

        self.progress_bar = ttk.Progressbar(
            content,
            orient="horizontal",
            length=360,
            mode='indeterminate',
            variable=self.progress_var,
            style="Loading.Horizontal.TProgressbar",
        )
        self.progress_bar.pack(fill="x", pady=(0, 18))
        self.progress_bar.start(12)

        footer = tk.Frame(content, bg=COLORS['bg_medium'])
        footer.pack(fill="x", side="bottom")

        footer_label = tk.Label(
            footer,
            text="SQL Panel Enterprise Suite",
            font=FONTS['small'],
            bg=COLORS['bg_medium'],
            fg=COLORS['text_gray'],
        )
        footer_label.pack(side="left")

        self.tip_label = tk.Label(
            footer,
            text="",
            font=FONTS['small'],
            bg=COLORS['bg_medium'],
            fg=COLORS['text_light'],
        )
        self.tip_label.pack(side="right")

    def _center_window(self, width: int = 520, height: int = 320):
        self.parent.update_idletasks()
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        x_pos = (screen_width // 2) - (width // 2)
        y_pos = (screen_height // 2) - (height // 2)
        self.splash.geometry(f"{width}x{height}+{x_pos}+{y_pos}")

    def _start_tip_cycle(self):
        self._tip_cycle_job = self.splash.after(2000, self._rotate_tip)

    def _rotate_tip(self):
        if self._detail_override:
            self._start_tip_cycle()
            return
        self._tip_index = (self._tip_index + 1) % len(self._tips)
        self.tip_label.config(text=self._tips[self._tip_index])
        self.detail_var.set(self._tips[self._tip_index])
        self._start_tip_cycle()

    def update_status(self, message: str, progress: float | None = None, detail: str | None = None):
        """Durum mesajını ve ilerlemeyi güncelle."""
        self.status_var.set(message)

        if detail:
            self._detail_override = True
            self.detail_var.set(detail)
            self.tip_label.config(text=detail)
            if self._tip_cycle_job:
                self.splash.after_cancel(self._tip_cycle_job)
            self._tip_cycle_job = self.splash.after(2500, self._release_detail_override)

        if progress is not None:
            if self._indeterminate:
                self.progress_bar.stop()
                self.progress_bar.config(mode='determinate', maximum=100)
                self._indeterminate = False
            self.progress_var.set(progress)
            self.progress_bar['value'] = progress

        self.splash.update_idletasks()

    def _release_detail_override(self):
        self._detail_override = False
        self._start_tip_cycle()

    def finish(self, on_complete=None):
        """Yükleme ekranını yumuşakça kapat."""
        self.update_status("Hazır", 100, "Arayüz başlatılıyor")
        self.progress_bar.stop()
        self._fade_out(on_complete)

    def _fade_out(self, on_complete, alpha: float = 1.0):
        try:
            self.splash.attributes('-alpha', alpha)
        except tk.TclError:
            self.destroy()
            if on_complete:
                on_complete()
            return

        if alpha <= 0:
            self.destroy()
            if on_complete:
                on_complete()
            return

        self._fade_job = self.splash.after(30, lambda: self._fade_out(on_complete, alpha - 0.1))

    def destroy(self):
        if self._tip_cycle_job:
            self.splash.after_cancel(self._tip_cycle_job)
            self._tip_cycle_job = None
        if self._fade_job:
            self.splash.after_cancel(self._fade_job)
            self._fade_job = None
        if self.splash.winfo_exists():
            self.splash.destroy()

    def force_close(self):
        """Herhangi bir animasyon beklemeden pencereyi kapat."""
        self.destroy()
