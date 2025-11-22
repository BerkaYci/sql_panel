"""
Araç Çubuğu Widget
Üst menü ve hızlı erişim butonları
"""

import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
import os

from config.settings import *


class Toolbar:
    """Üst araç çubuğu"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main = main_window

        self.frame = tk.Frame(parent, bg=COLORS['bg_dark'], height=100)
        self.frame.pack_propagate(False)

        self.setup_toolbar()

    def setup_toolbar(self):
        """Araç çubuğunu oluştur"""
        # Database section
        db_section = tk.Frame(self.frame, bg=COLORS['bg_dark'])
        db_section.pack(side="left", padx=10, pady=10)

        tk.Label(db_section, text=f"{ICONS['database']} Veritabanları:",
                bg=COLORS['bg_dark'], fg=COLORS['text_white'],
                font=FONTS['subtitle']).pack(anchor="w")

        db_controls = tk.Frame(db_section, bg=COLORS['bg_dark'])
        db_controls.pack(fill="x")

        self.create_button(db_controls, f"{ICONS['add']} Yeni",
                          self.create_new_db, COLORS['success'], small=True)
        self.create_button(db_controls, "📂 Aç",
                          self.open_db, COLORS['primary'], small=True)
        self.create_button(db_controls, "🔗 Bağla",
                          self.attach_db, COLORS['info'], small=True)

        # Active database dropdown
        active_db_frame = tk.Frame(db_section, bg=COLORS['bg_dark'])
        active_db_frame.pack(fill="x", pady=(5, 0))

        tk.Label(active_db_frame, text="Aktif:",
                bg=COLORS['bg_dark'], fg=COLORS['text_white'],
                font=FONTS['small']).pack(side="left")

        self.active_db_var = tk.StringVar()
        self.active_db_combo = ttk.Combobox(active_db_frame,
                                           textvariable=self.active_db_var,
                                           width=15, state="readonly",
                                           font=FONTS['small'])
        self.active_db_combo.pack(side="left", padx=(5, 0))
        self.active_db_combo.bind('<<ComboboxSelected>>', self.change_active_db)

        # File operations section
        file_section = tk.Frame(self.frame, bg=COLORS['bg_dark'])
        file_section.pack(side="left", padx=20, pady=10)

        tk.Label(file_section, text="📁 Dosya İşlemleri:",
                bg=COLORS['bg_dark'], fg=COLORS['text_white'],
                font=FONTS['subtitle']).pack(anchor="w")

        file_controls = tk.Frame(file_section, bg=COLORS['bg_dark'])
        file_controls.pack(fill="x")

        self.create_button(file_controls, f"{ICONS['import']} CSV",
                          self.import_csv, COLORS['warning'], small=True)
        self.create_button(file_controls, f"{ICONS['import']} Excel",
                          self.import_excel, COLORS['warning'], small=True)
        self.create_button(file_controls, f"{ICONS['export']} Dışa Aktar",
                          self.export_data, COLORS['danger'], small=True)

        # Database info section
        info_section = tk.Frame(self.frame, bg=COLORS['bg_dark'])
        info_section.pack(side="right", padx=10, pady=10)

        self.db_info_frame = tk.Frame(info_section, bg=COLORS['bg_dark'])
        self.db_info_frame.pack()

        self.update_info()

    def create_button(self, parent, text, command, color, small=False):
        """Stil sahibi buton oluştur"""
        font_size = 8 if small else 9
        padx = 8 if small else 15
        pady = 3 if small else 5

        btn = tk.Button(parent, text=text, command=command,
                       bg=color, fg=COLORS['text_white'],
                       font=("Arial", font_size, "bold"),
                       relief="flat", padx=padx, pady=pady,
                       cursor="hand2")
        btn.pack(side="left", padx=2)

        # Hover effects
        def on_enter(e):
            btn.config(bg=self.lighten_color(color))

        def on_leave(e):
            btn.config(bg=color)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

    def lighten_color(self, color):
        """Rengi açıklaştır (hover için)"""
        colors = {
            COLORS['success']: "#2ECC71",
            COLORS['primary']: "#5DADE2",
            COLORS['warning']: "#F4D03F",
            COLORS['danger']: "#EC7063",
            COLORS['info']: "#BB8FCE",
            COLORS['dark']: "#5D6D7E"
        }
        return colors.get(color, color)

    # Database operations
    def create_new_db(self):
        """Yeni veritabanı oluştur"""
        db_path = filedialog.asksaveasfilename(
            title="Yeni Veritabanı Oluştur",
            filetypes=FILE_TYPES['db'],
            defaultextension=".db"
        )

        if db_path:
            alias = simpledialog.askstring("Veritabanı Takma Adı",
                                          "Bu veritabanı için bir takma ad girin:",
                                          initialvalue=os.path.splitext(os.path.basename(db_path))[0])
            if not alias:
                return

            success, message = self.main.db_manager.create_database(db_path, alias)

            if success:
                messagebox.showinfo(f"{ICONS['success']} Başarılı", message)
                self.update_info()
                self.main.refresh_all()
            else:
                messagebox.showerror(f"{ICONS['error']} Hata", message)

    def open_db(self):
        """Veritabanı aç"""
        db_path = filedialog.askopenfilename(
            title="Veritabanı Seç",
            filetypes=FILE_TYPES['db']
        )

        if db_path:
            alias = simpledialog.askstring("Veritabanı Takma Adı",
                                          "Bu veritabanı için bir takma ad girin:",
                                          initialvalue=os.path.splitext(os.path.basename(db_path))[0])
            if not alias:
                return

            # Mevcut bağlantı kontrolü
            replace = False
            if alias in self.main.db_manager.connections:
                replace = messagebox.askyesno(f"{ICONS['warning']} Var olan bağlantı",
                                            f"'{alias}' zaten bağlı. Yeniden bağlanmak istiyor musunuz?")
                if not replace:
                    return

            success, message = self.main.db_manager.open_database(db_path, alias, replace)

            if success:
                messagebox.showinfo(f"{ICONS['success']} Başarılı", message)
                self.update_info()
                self.main.refresh_all()
            else:
                messagebox.showerror(f"{ICONS['error']} Hata", message)

    def attach_db(self):
        """Veritabanı ekle (ATTACH)"""
        if not self.main.db_manager.active_db:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı", MESSAGES['no_db'])
            return

        db_path = filedialog.askopenfilename(
            title="Bağlanacak Veritabanı Seç",
            filetypes=FILE_TYPES['db']
        )

        if db_path:
            alias = simpledialog.askstring("Bağlı DB Takma Adı",
                                          "Bağlanacak veritabanı için takma ad:",
                                          initialvalue=f"attached_{os.path.splitext(os.path.basename(db_path))[0]}")
            if not alias:
                return

            success, message = self.main.db_manager.attach_database(db_path, alias)

            if success:
                messagebox.showinfo(f"{ICONS['success']} Başarılı",
                                  f"{message}\n\n"
                                  f"Sorgu örnekleri:\n"
                                  f"• SELECT * FROM {alias}.tablo_adi\n"
                                  f"• INSERT INTO {alias}.tablo VALUES (...)")
                self.main.refresh_all()
            else:
                messagebox.showerror(f"{ICONS['error']} Hata", message)

    def change_active_db(self, event=None):
        """Aktif veritabanını değiştir"""
        new_active = self.active_db_var.get()
        if new_active and self.main.db_manager.set_active_database(new_active):
            self.update_info()
            self.main.refresh_all()

    # File operations
    def import_csv(self):
        """CSV import"""
        if not self.main.db_manager.active_db:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı", MESSAGES['no_db'])
            return

        messagebox.showinfo(f"{ICONS['info']} Geliştirme",
                          "CSV import özelliği 'SQL Sorguları' sekmesinde mevcuttur.")

    def import_excel(self):
        """Excel import"""
        if not self.main.db_manager.active_db:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı", MESSAGES['no_db'])
            return

        messagebox.showinfo(f"{ICONS['info']} Geliştirme",
                          "Excel import özelliği 'SQL Sorguları' sekmesinde mevcuttur.")

    def export_data(self):
        """Veri dışa aktar"""
        messagebox.showinfo(f"{ICONS['info']} Geliştirme",
                          "Export özelliği 'SQL Sorguları' sekmesinde mevcuttur.")

    def update_info(self):
        """Veritabanı bilgilerini güncelle"""
        # Clear previous info
        for widget in self.db_info_frame.winfo_children():
            widget.destroy()

        db_infos = self.main.db_manager.get_all_database_info()

        if db_infos:
            tk.Label(
                self.db_info_frame,
                text=f"{ICONS['connect']} Bağlı Veritabanları:",
                bg=COLORS['bg_dark'],
                fg=COLORS['text_white'],
                font=FONTS['subtitle']
            ).pack(anchor="w")

            for info in db_infos:
                alias = info.get('alias', '?')
                is_active = "🟢" if info.get('is_active') else "⚪"

                size_bytes = info.get('size')
                if size_bytes is not None:
                    size_kb = size_bytes / 1024
                    size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb / 1024:.1f} MB"
                else:
                    size_str = "?"

                table_count = info.get('table_count', '?')
                filename = info.get('filename', os.path.basename(info.get('path', '')))
                info_text = (
                    f"{is_active} {alias}: {filename or info.get('path', 'Bilinmiyor')}"
                    f" ({size_str}, {table_count} tablo)"
                )

                if info.get('error'):
                    info_text += f" • Hata: {info['error']}"

                tk.Label(
                    self.db_info_frame,
                    text=info_text,
                    bg=COLORS['bg_dark'],
                    fg=COLORS['text_light'],
                    font=FONTS['small']
                ).pack(anchor="w")
        else:
            tk.Label(
                self.db_info_frame,
                text=f"{ICONS['error']} Bağlı veritabanı yok",
                bg=COLORS['bg_dark'],
                fg=COLORS['danger'],
                font=FONTS['subtitle']
            ).pack()

        # Update combo regardless of state
        db_list = self.main.db_manager.get_database_list()
        self.active_db_combo['values'] = db_list

        if self.main.db_manager.active_db:
            self.active_db_combo.set(self.main.db_manager.active_db)
        elif not db_list:
            self.active_db_combo.set("")