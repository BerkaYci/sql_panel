"""
Tablolar Sekmesi
Tablo görüntüleme ve bilgi edinme
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from config.settings import *


class TablesTab:
    """Tablolar görüntüleme sekmesi"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main = main_window

        self.frame = ttk.Frame(parent)
        self.current_table = None

        self.setup_ui()

    def setup_ui(self):
        """UI bileşenlerini oluştur"""
        # Database selector
        db_selector = tk.Frame(self.frame, bg=COLORS['bg_light'], height=50)
        db_selector.pack(fill="x", padx=5, pady=5)
        db_selector.pack_propagate(False)

        tk.Label(db_selector, text=f"{ICONS['database']} Veritabanı Seç:",
                bg=COLORS['bg_light'], font=FONTS['subtitle']).pack(side="left", padx=10, pady=15)

        self.tables_db_var = tk.StringVar()
        self.tables_db_combo = ttk.Combobox(db_selector, textvariable=self.tables_db_var,
                                           width=25, state="readonly")
        self.tables_db_combo.pack(side="left", padx=5, pady=15)
        self.tables_db_combo.bind('<<ComboboxSelected>>', self.refresh)

        # Main container
        main_container = tk.Frame(self.frame)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Left panel - Tables list
        left_panel = tk.Frame(main_container, width=250, bg=COLORS['bg_light'])
        left_panel.pack(side="left", fill="y", padx=(0, 5))
        left_panel.pack_propagate(False)

        tk.Label(left_panel, text=f"{ICONS['table']} Tablolar:",
                font=FONTS['subtitle'], bg=COLORS['bg_light']).pack(anchor="w", padx=10, pady=10)

        # Tables listbox
        tables_list_frame = tk.Frame(left_panel, bg=COLORS['bg_light'])
        tables_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tables_listbox = tk.Listbox(tables_list_frame, font=FONTS['normal'], bg="white")
        tables_scrollbar = ttk.Scrollbar(tables_list_frame, orient="vertical",
                                        command=self.tables_listbox.yview)
        self.tables_listbox.configure(yscrollcommand=tables_scrollbar.set)

        self.tables_listbox.pack(side="left", fill="both", expand=True)
        tables_scrollbar.pack(side="right", fill="y")

        self.tables_listbox.bind('<Double-1>', self.load_table_data)
        self.tables_listbox.bind('<<ListboxSelect>>', self.on_table_select)

        # Control buttons
        btn_frame = tk.Frame(left_panel, bg=COLORS['bg_light'])
        btn_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(btn_frame, text=f"{ICONS['refresh']} Yenile", command=self.refresh,
                 bg=COLORS['primary'], fg=COLORS['text_white'],
                 font=FONTS['normal']).pack(fill="x", pady=2)

        tk.Button(btn_frame, text=f"{ICONS['delete']} Tabloyu Sil", command=self.delete_table,
                 bg=COLORS['danger'], fg=COLORS['text_white'],
                 font=FONTS['normal']).pack(fill="x", pady=2)

        # Right panel - Table details
        right_panel = tk.Frame(main_container)
        right_panel.pack(side="right", fill="both", expand=True)

        # Table info section
        info_label_frame = tk.Frame(right_panel)
        info_label_frame.pack(fill="x", pady=(0, 5))

        tk.Label(info_label_frame, text=f"{ICONS['info']} Tablo Bilgileri:",
                font=FONTS['subtitle']).pack(side="left")

        self.record_count_label = tk.Label(info_label_frame, text="",
                                          font=FONTS['normal'], fg=COLORS['success'])
        self.record_count_label.pack(side="right")

        # Table info text
        info_frame = tk.Frame(right_panel)
        info_frame.pack(fill="x", pady=(0, 10))

        self.table_info_text = tk.Text(info_frame, height=8, font=FONTS['code'],
                                       bg=COLORS['bg_light'])
        info_scrollbar = ttk.Scrollbar(info_frame, orient="vertical",
                                      command=self.table_info_text.yview)
        self.table_info_text.configure(yscrollcommand=info_scrollbar.set)

        self.table_info_text.pack(side="left", fill="both", expand=True)
        info_scrollbar.pack(side="right", fill="y")

        # Table data preview
        tk.Label(right_panel, text=f"👀 Veri Önizleme (İlk {DATA_LIMITS['preview_rows']} Kayıt):",
                font=FONTS['subtitle']).pack(anchor="w", pady=(10, 5))

        # Table data treeview
        data_frame = tk.Frame(right_panel)
        data_frame.pack(fill="both", expand=True)

        self.table_data_tree = ttk.Treeview(data_frame, show="headings")

        data_v_scroll = ttk.Scrollbar(data_frame, orient="vertical",
                                     command=self.table_data_tree.yview)
        data_h_scroll = ttk.Scrollbar(data_frame, orient="horizontal",
                                     command=self.table_data_tree.xview)

        self.table_data_tree.configure(yscrollcommand=data_v_scroll.set,
                                       xscrollcommand=data_h_scroll.set)

        self.table_data_tree.grid(row=0, column=0, sticky="nsew")
        data_v_scroll.grid(row=0, column=1, sticky="ns")
        data_h_scroll.grid(row=1, column=0, sticky="ew")

        data_frame.grid_rowconfigure(0, weight=1)
        data_frame.grid_columnconfigure(0, weight=1)

    def refresh(self, event=None):
        """Tablo listesini yenile"""
        db_alias = self.tables_db_var.get()
        if not db_alias:
            # Update combo first
            db_list = self.main.db_manager.get_database_list()
            self.tables_db_combo['values'] = db_list
            if self.main.db_manager.active_db:
                self.tables_db_combo.set(self.main.db_manager.active_db)
                db_alias = self.main.db_manager.active_db
            elif db_list:
                self.tables_db_combo.set(db_list[0])
                db_alias = db_list[0]
            else:
                return

        # Get tables
        tables = self.main.db_manager.get_tables(db_alias)

        # Update listbox
        self.tables_listbox.delete(0, tk.END)
        for table in tables:
            self.tables_listbox.insert(tk.END, table)

    def on_table_select(self, event):
        """Tablo seçildiğinde"""
        selection = self.tables_listbox.curselection()
        if selection:
            table_name = self.tables_listbox.get(selection[0])
            self.current_table = table_name

    def load_table_data(self, event):
        """Tablo verilerini yükle"""
        selection = self.tables_listbox.curselection()
        if not selection:
            return

        table_name = self.tables_listbox.get(selection[0])
        db_alias = self.tables_db_var.get()

        if not db_alias:
            return

        try:
            # Get table structure
            columns_info = self.main.db_manager.get_table_info(table_name, db_alias)

            # Get record count
            record_count = self.main.db_manager.get_table_row_count(table_name, db_alias)

            # Display table info
            info_text = f"{ICONS['database']} Veritabanı: {db_alias}\n"
            info_text += f"{ICONS['table']} Tablo: {table_name}\n"
            info_text += f"📊 Toplam Kayıt: {record_count:,}\n"
            info_text += f"🔢 Sütun Sayısı: {len(columns_info)}\n\n"
            info_text += "📌 Sütun Detayları:\n"
            info_text += "-" * 60 + "\n"

            for col in columns_info:
                # col: (cid, name, type, notnull, dflt_value, pk)
                primary_key = " (🔑 PRIMARY KEY)" if col[5] else ""
                not_null = " (❗ NOT NULL)" if col[3] else ""
                default_val = f" (📝 Default: {col[4]})" if col[4] else ""
                info_text += f"📋 {col[1]} - {col[2]}{primary_key}{not_null}{default_val}\n"

            self.table_info_text.delete("1.0", tk.END)
            self.table_info_text.insert("1.0", info_text)

            # Update record count label
            self.record_count_label.config(text=f"📊 Toplam: {record_count:,} kayıt")

            # Load preview data
            preview_limit = DATA_LIMITS['preview_rows']
            success, result, message = self.main.query_executor.execute(
                f"SELECT * FROM `{table_name}` LIMIT {preview_limit}",
                alias=db_alias
            )

            if success and result and result.get('type') == 'select':
                self.display_preview(result['rows'], result['columns'])

            # Large table warning
            if record_count > DATA_LIMITS['large_table_threshold']:
                messagebox.showinfo(
                    f"{ICONS['warning']} Büyük Tablo",
                    f"Bu tablo {record_count:,} kayıt içeriyor.\n"
                    f"Sadece ilk {preview_limit} kayıt gösteriliyor.\n\n"
                    f"Tüm veriyi görmek için SQL sorgusu kullanın."
                )

        except Exception as e:
            messagebox.showerror(f"{ICONS['error']} Hata",
                               f"Tablo verisi yüklenemedi:\n{str(e)}")

    def display_preview(self, rows, columns):
        """Önizleme verilerini göster"""
        # Clear old data
        for col in self.table_data_tree.get_children():
            self.table_data_tree.delete(col)

        # Set columns
        self.table_data_tree["columns"] = columns
        self.table_data_tree["show"] = "headings"

        for col in columns:
            self.table_data_tree.heading(col, text=col)
            self.table_data_tree.column(col, width=120, anchor="center")

        # Add data with alternating colors
        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            self.table_data_tree.insert("", tk.END, values=row, tags=(tag,))

        # Configure row colors
        self.table_data_tree.tag_configure("even", background=COLORS['tree_even'])
        self.table_data_tree.tag_configure("odd", background=COLORS['tree_odd'])

    def delete_table(self):
        """Tabloyu sil"""
        selection = self.tables_listbox.curselection()
        if not selection:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı",
                                 "Silinecek tabloyu seçin!")
            return

        table_name = self.tables_listbox.get(selection[0])
        db_alias = self.tables_db_var.get()

        # Confirmation
        if not messagebox.askyesno(
            f"{ICONS['warning']} TEHLİKELİ İŞLEM",
            f"'{table_name}' tablosunu silmek istediğinizden emin misiniz?\n\n"
            f"⚠️ Bu işlem GERİ ALINAMAZ!\n"
            f"⚠️ Tablodaki TÜM VERİLER silinecek!"
        ):
            return

        # Double confirmation
        confirm_text = simpledialog.askstring(
            "Son Onay",
            f"Silmek için tablo adını yazın: {table_name}"
        )

        if confirm_text != table_name:
            messagebox.showinfo(f"{ICONS['info']} İptal", "Tablo adı eşleşmedi, işlem iptal edildi.")
            return

        # Execute DROP TABLE
        success, result, message = self.main.query_executor.execute(
            f"DROP TABLE `{table_name}`",
            alias=db_alias
        )

        if success:
            messagebox.showinfo(f"{ICONS['success']} Başarılı",
                              f"'{table_name}' tablosu silindi!")
            self.refresh()
            self.main.refresh_all()
        else:
            messagebox.showerror(f"{ICONS['error']} Hata",
                               f"Tablo silinemedi:\n{message}")
