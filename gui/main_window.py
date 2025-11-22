"""
Ana Pencere Modülü
Uygulamanın ana GUI yapısı
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os

# Config
from config.settings import *

# Core
from core.database_manager import DatabaseManager
from core.query_executor import QueryExecutor
from core.saved_queries_manager import SavedQueriesManager

# GUI Tabs
from gui.tabs.query_tab import QueryTab
from gui.tabs.databases_tab import DatabasesTab
from gui.tabs.tables_tab import TablesTab
from gui.tabs.editor_tab import EditorTab
from gui.tabs.my_queries_tab import MyQueriesTab

# GUI Widgets
from gui.widgets.toolbar import Toolbar
from gui.widgets.loading_screen import LoadingScreen


class MainWindow:
    """Ana uygulama penceresi"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # Maximize window
        if os.name == 'nt':  # Windows
            self.root.state('zoomed')

        # Loading screen göster (başlangıç)
        self.loading_screen = LoadingScreen(
            self.root,
            message="Uygulama başlatılıyor...",
            show_progress=False,
            cancelable=False
        )
        self.root.update()

        # Core components (yükleme sırasında)
        self.loading_screen.update_message("Veritabanı yöneticisi yükleniyor...")
        self.root.update()
        self.db_manager = DatabaseManager()
        
        self.loading_screen.update_message("Sorgu çalıştırıcı hazırlanıyor...")
        self.root.update()
        self.query_executor = QueryExecutor(self.db_manager)
        
        self.loading_screen.update_message("Kaydedilmiş sorgular yükleniyor...")
        self.root.update()
        self.saved_queries = SavedQueriesManager()

        # Style configuration
        self.loading_screen.update_message("Arayüz stilleri yükleniyor...")
        self.root.update()
        self.setup_style()

        # GUI setup
        self.loading_screen.update_message("Arayüz bileşenleri oluşturuluyor...")
        self.root.update()
        self.setup_gui()

        # Loading screen'i kapat
        self.loading_screen.close()
        self.root.update()

        # Pencere kapatma eventi
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_style(self):
        """Tkinter style ayarları"""
        style = ttk.Style()
        style.theme_use('clam')

        # Treeview style
        style.configure("Treeview",
                       background="white",
                       foreground=COLORS['text_dark'],
                       fieldbackground="white",
                       font=FONTS['normal'])

        style.configure("Treeview.Heading",
                       background=COLORS['bg_dark'],
                       foreground=COLORS['text_white'],
                       font=FONTS['subtitle'])

        # Combobox style
        style.configure("TCombobox",
                       fieldbackground="white",
                       background=COLORS['primary'])

    def setup_gui(self):
        """GUI bileşenlerini oluştur"""
        # Toolbar
        self.toolbar = Toolbar(self.root, self)
        self.toolbar.frame.pack(fill="x")

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Create tabs
        self.query_tab = QueryTab(self.notebook, self)
        self.my_queries_tab = MyQueriesTab(self.notebook, self)
        self.databases_tab = DatabasesTab(self.notebook, self)
        self.tables_tab = TablesTab(self.notebook, self)
        self.editor_tab = EditorTab(self.notebook, self)

        # Add tabs to notebook
        self.notebook.add(self.query_tab.frame, text=f"{ICONS['query']} SQL Sorguları")
        self.notebook.add(self.my_queries_tab.frame, text="💾 Sorgularım")
        self.notebook.add(self.databases_tab.frame, text=f"{ICONS['database']} Veritabanları")
        self.notebook.add(self.tables_tab.frame, text=f"{ICONS['table']} Tablolar")
        self.notebook.add(self.editor_tab.frame, text=f"{ICONS['edit']} Veri Düzenleme")

        # Footer
        self.setup_footer()

    def setup_footer(self):
        """Alt bilgi çubuğu"""
        footer_frame = tk.Frame(self.root, bg=COLORS['bg_dark'], height=30)
        footer_frame.pack(side="bottom", fill="x")
        footer_frame.pack_propagate(False)

        # Version
        version_label = tk.Label(
            footer_frame,
            text=f"Version {APP_VERSION}",
            bg=COLORS['bg_dark'],
            fg=COLORS['text_gray'],
            font=FONTS['small']
        )
        version_label.pack(side="left", padx=10, pady=5)

        # Author
        author_label = tk.Label(
            footer_frame,
            text=f"Developed by {APP_AUTHOR}",
            bg=COLORS['bg_dark'],
            fg=COLORS['text_white'],
            font=FONTS['footer']
        )
        author_label.pack(side="right", padx=10, pady=5)

        # Status
        self.status_label = tk.Label(
            footer_frame,
            text=f"{ICONS['info']} Hazır",
            bg=COLORS['bg_dark'],
            fg=COLORS['text_light'],
            font=FONTS['normal']
        )
        self.status_label.pack(side="left", padx=20, pady=5)

    def update_status(self, message: str, color: str = None):
        """Durum mesajını güncelle"""
        if color:
            self.status_label.config(text=message, fg=color)
        else:
            self.status_label.config(text=message)

        self.root.update_idletasks()

    def refresh_all(self):
        """Tüm sekmeleri yenile"""
        self.toolbar.update_info()
        self.databases_tab.refresh()
        self.tables_tab.refresh()
        self.editor_tab.refresh()
        self.query_tab.update_db_combo()

    def on_closing(self):
        """Pencere kapatılırken"""
        if messagebox.askokcancel("Çıkış", MESSAGES['confirm_close']):
            # Tüm bağlantıları kapat
            count = self.db_manager.close_all()
            if count > 0:
                self.update_status(f"{ICONS['success']} {count} bağlantı kapatıldı",
                                 COLORS['success'])

            self.root.destroy()

    def run(self):
        """Uygulamayı başlat"""
        self.root.mainloop()