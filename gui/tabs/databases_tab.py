"""
Veritabanları Sekmesi
Bağlı veritabanlarını yönetme ve görüntüleme
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os

from config.settings import *
from gui.widgets.loading_screen import LoadingScreen


class DatabasesTab:
    """Veritabanları yönetim sekmesi"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main = main_window

        self.frame = ttk.Frame(parent)
        self.setup_ui()

    def setup_ui(self):
        """UI bileşenlerini oluştur"""
        # Controls section
        controls_frame = tk.Frame(self.frame, bg=COLORS['bg_light'], height=80)
        controls_frame.pack(fill="x", padx=5, pady=5)
        controls_frame.pack_propagate(False)

        tk.Label(controls_frame, text=f"{ICONS['database']} Veritabanı Yönetimi",
                 bg=COLORS['bg_light'], font=FONTS['title']).pack(pady=10)

        btn_frame = tk.Frame(controls_frame, bg=COLORS['bg_light'])
        btn_frame.pack()

        tk.Button(btn_frame, text=f"{ICONS['refresh']} Yenile", command=self.refresh,
                  bg=COLORS['primary'], fg=COLORS['text_white'],
                  font=FONTS['subtitle']).pack(side="left", padx=5)
        tk.Button(btn_frame, text=f"{ICONS['disconnect']} Bağlantıyı Kes", command=self.disconnect,
                  bg=COLORS['danger'], fg=COLORS['text_white'],
                  font=FONTS['subtitle']).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🔍 Çapraz Sorgu", command=self.show_cross_query,
                  bg=COLORS['info'], fg=COLORS['text_white'],
                  font=FONTS['subtitle']).pack(side="left", padx=5)
        tk.Button(btn_frame, text="💾 Yedek Al", command=self.backup_database,
                  bg=COLORS['success'], fg=COLORS['text_white'],
                  font=FONTS['subtitle']).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🔧 Optimize", command=self.optimize_database,
                  bg=COLORS['warning'], fg=COLORS['text_white'],
                  font=FONTS['subtitle']).pack(side="left", padx=5)

        # Database list
        list_frame = tk.Frame(self.frame)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Treeview
        self.db_tree = ttk.Treeview(list_frame,
                                    columns=("alias", "path", "size", "tables", "status"),
                                    show="headings")

        self.db_tree.heading("alias", text=f"{ICONS['database']} Takma Ad")
        self.db_tree.heading("path", text="📁 Dosya Yolu")
        self.db_tree.heading("size", text="📊 Boyut")
        self.db_tree.heading("tables", text=f"{ICONS['table']} Tablo Sayısı")
        self.db_tree.heading("status", text="⚡ Durum")

        self.db_tree.column("alias", width=150)
        self.db_tree.column("path", width=350)
        self.db_tree.column("size", width=100)
        self.db_tree.column("tables", width=100)
        self.db_tree.column("status", width=100)

        # Scrollbars
        db_scroll_y = ttk.Scrollbar(list_frame, orient="vertical", command=self.db_tree.yview)
        db_scroll_x = ttk.Scrollbar(list_frame, orient="horizontal", command=self.db_tree.xview)
        self.db_tree.configure(yscrollcommand=db_scroll_y.set, xscrollcommand=db_scroll_x.set)

        self.db_tree.grid(row=0, column=0, sticky="nsew")
        db_scroll_y.grid(row=0, column=1, sticky="ns")
        db_scroll_x.grid(row=1, column=0, sticky="ew")

        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        # Double-click to set as active
        self.db_tree.bind('<Double-1>', self.set_active_from_tree)

        # Initial load
        self.refresh()

    def refresh(self):
        """Veritabanı listesini yenile"""
        # Clear existing
        for item in self.db_tree.get_children():
            self.db_tree.delete(item)

        # Add databases
        for alias in self.main.db_manager.get_database_list():
            db_info = self.main.db_manager.get_database_info(alias)

            if db_info:
                # Size formatting
                size = db_info.get('size', 0) / 1024
                size_str = f"{size:.1f} KB" if size < 1024 else f"{size / 1024:.1f} MB"

                # Status
                status = "🟢 Aktif" if db_info['is_active'] else "⚪ Hazır"

                # Insert to tree
                self.db_tree.insert("", tk.END, values=(
                    alias,
                    db_info['path'],
                    size_str,
                    db_info.get('table_count', 0),
                    status
                ))

    def disconnect(self):
        """Seçili veritabanı bağlantısını kes"""
        selected = self.db_tree.selection()
        if not selected:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı",
                                   "Kesilecek bağlantıyı seçin!")
            return

        item = selected[0]
        alias = self.db_tree.item(item)['values'][0]

        if messagebox.askyesno(f"{ICONS['warning']} Onay",
                               f"'{alias}' veritabanı bağlantısını kesmek istiyor musunuz?"):
            success, message = self.main.db_manager.close_database(alias)

            if success:
                messagebox.showinfo(f"{ICONS['success']} Başarılı", message)
                self.refresh()
                self.main.refresh_all()
            else:
                messagebox.showerror(f"{ICONS['error']} Hata", message)

    def set_active_from_tree(self, event):
        """Çift tıklama ile aktif veritabanını değiştir"""
        selected = self.db_tree.selection()
        if selected:
            item = selected[0]
            alias = self.db_tree.item(item)['values'][0]

            if self.main.db_manager.set_active_database(alias):
                self.refresh()
                self.main.refresh_all()
                self.main.update_status(
                    f"{ICONS['success']} Aktif veritabanı: {alias}",
                    COLORS['success']
                )

    def show_cross_query(self):
        """Çapraz sorgu örnekleri göster"""
        db_list = self.main.db_manager.get_database_list()

        if len(db_list) < 2:
            messagebox.showinfo(f"{ICONS['info']} Bilgi",
                                "Çapraz sorgular için en az 2 veritabanı bağlantısı gereklidir.\n"
                                "ATTACH DATABASE komutu ile başka veritabanları bağlayabilirsiniz.")
            return

        # Examples window
        examples_window = tk.Toplevel(self.main.root)
        examples_window.title("🔍 Çapraz Sorgu Örnekleri")
        examples_window.geometry("700x500")

        tk.Label(examples_window, text="🔗 Çoklu Veritabanı Sorgu Örnekleri",
                 font=FONTS['title']).pack(pady=10)

        examples_text = tk.Text(examples_window, font=FONTS['code'], bg=COLORS['bg_light'])
        examples_text.pack(fill="both", expand=True, padx=10, pady=10)

        examples = f"""
-- 📊 Çapraz Veritabanı Sorgu Örnekleri
-- Bağlı Veritabanları: {', '.join(db_list)}

-- 1. Farklı veritabanlarından veri birleştirme
SELECT a.*, b.*
FROM {db_list[0]}.tablo1 a
JOIN {db_list[1] if len(db_list) > 1 else 'attached_db'}.tablo2 b 
ON a.id = b.id;

-- 2. Veritabanları arası veri kopyalama
INSERT INTO {db_list[0]}.hedef_tablo
SELECT * FROM {db_list[1] if len(db_list) > 1 else 'attached_db'}.kaynak_tablo;

-- 3. Karşılaştırmalı analiz
SELECT 
    '{db_list[0]}' as veritabani,
    COUNT(*) as kayit_sayisi
FROM {db_list[0]}.tablo1
UNION ALL
SELECT 
    '{db_list[1] if len(db_list) > 1 else 'attached_db'}' as veritabani,
    COUNT(*) as kayit_sayisi
FROM {db_list[1] if len(db_list) > 1 else 'attached_db'}.tablo1;

-- 4. Bağlı veritabanlarını listeleme
PRAGMA database_list;

-- 5. Her veritabanındaki tabloları listeleme
SELECT name, 'main' as db FROM sqlite_master WHERE type='table'
UNION
SELECT name, 'attached' as db FROM attached_db.sqlite_master WHERE type='table';

-- 💡 İPUCU: 
-- • Çapraz sorgular 'SQL Sorguları' sekmesinden çalıştırılır
-- • Her veritabanı için tablo listesi alabilirsiniz
-- • PRAGMA database_list; ile bağlı DB'leri görebilirsiniz
"""

        examples_text.insert("1.0", examples)
        examples_text.config(state="disabled")

        # Copy button
        def copy_examples():
            self.main.root.clipboard_clear()
            self.main.root.clipboard_append(examples_text.get("1.0", tk.END))
            messagebox.showinfo(f"{ICONS['success']}", "Örnekler panoya kopyalandı!")

        tk.Button(examples_window, text="📋 Panoya Kopyala", command=copy_examples,
                  bg=COLORS['primary'], fg=COLORS['text_white'],
                  font=FONTS['subtitle']).pack(pady=10)

    def backup_database(self):
        """Veritabanını yedekle"""
        selected = self.db_tree.selection()
        if not selected:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı",
                                   "Yedeklenecek veritabanını seçin!")
            return

        item = selected[0]
        alias = self.db_tree.item(item)['values'][0]

        from tkinter import filedialog
        backup_path = filedialog.asksaveasfilename(
            title="Yedek Dosyası",
            filetypes=FILE_TYPES['db'],
            defaultextension=".db",
            initialfile=f"{alias}_backup.db"
        )

        if backup_path:
            # Loading screen göster
            loading_screen = LoadingScreen(
                self.main.root,
                message=f"Veritabanı yedekleniyor...\n\nVeritabanı: {alias}\nHedef: {backup_path}",
                show_progress=False,
                cancelable=False
            )
            self.main.root.update()

            try:
                success, message = self.main.db_manager.backup_database(alias, backup_path)
            finally:
                loading_screen.close()
                self.main.root.update()

            if success:
                messagebox.showinfo(f"{ICONS['success']} Başarılı", message)
            else:
                messagebox.showerror(f"{ICONS['error']} Hata", message)

    def optimize_database(self):
        """Veritabanını optimize et (VACUUM)"""
        selected = self.db_tree.selection()
        if not selected:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı",
                                   "Optimize edilecek veritabanını seçin!")
            return

        item = selected[0]
        alias = self.db_tree.item(item)['values'][0]

        if messagebox.askyesno(f"{ICONS['warning']} Onay",
                               f"'{alias}' veritabanını optimize etmek istiyor musunuz?\n"
                               f"Bu işlem zaman alabilir."):
            # Loading screen göster
            loading_screen = LoadingScreen(
                self.main.root,
                message=f"Veritabanı optimize ediliyor...\n\nVeritabanı: {alias}\n\nBu işlem biraz zaman alabilir.",
                show_progress=False,
                cancelable=False
            )
            self.main.root.update()

            try:
                success, message = self.main.db_manager.vacuum_database(alias)
            finally:
                loading_screen.close()
                self.main.root.update()

            if success:
                messagebox.showinfo(f"{ICONS['success']} Başarılı", message)
                self.refresh()
            else:
                messagebox.showerror(f"{ICONS['error']} Hata", message)