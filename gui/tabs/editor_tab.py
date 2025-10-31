"""
Veri Düzenleme Sekmesi - PERFORMANS OPTİMİZE EDİLMİŞ
Büyük veri setleri için pagination, lazy loading ve caching
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from typing import Optional, List, Dict

# Performance optimizer'ı import et
from utils.performance_optimizer import DataPaginator, PerformanceMonitor, SmartCache

from config.settings import *


class EditorTab:
    """Veri düzenleme sekmesi - OPTIMIZE EDİLMİŞ"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main = main_window

        self.frame = ttk.Frame(parent)

        # Değişiklik takibi
        self.original_data = {}
        self.pending_changes = {}
        self.deleted_rows = set()
        self.new_rows = {}
        self.next_new_id = -1
        self.current_table = None
        self.current_db = None

        # 🚀 YENİ: Performans optimizasyon araçları
        self.paginator = DataPaginator(page_size=100)  # Her sayfada 100 satır
        self.performance_monitor = PerformanceMonitor()
        self.cache = SmartCache(max_size_mb=50)  # 50 MB cache
        self.is_large_dataset = False  # Büyük veri seti bayrağı

        self.setup_ui()

    def setup_ui(self):
        """UI bileşenlerini oluştur - OPTİMİZE EDİLMİŞ"""
        # Database and table selector
        selector_frame = tk.Frame(self.frame, bg=COLORS['bg_medium'], height=100)
        selector_frame.pack(fill="x", padx=5, pady=5)
        selector_frame.pack_propagate(False)

        # Database selector
        db_frame = tk.Frame(selector_frame, bg=COLORS['bg_medium'])
        db_frame.pack(side="left", padx=10, pady=10)

        tk.Label(db_frame, text=f"{ICONS['database']} Veritabanı:",
                bg=COLORS['bg_medium'], fg=COLORS['text_white'],
                font=FONTS['subtitle']).pack(anchor="w")

        self.edit_db_var = tk.StringVar()
        self.edit_db_combo = ttk.Combobox(db_frame, textvariable=self.edit_db_var,
                                         width=15, state="readonly")
        self.edit_db_combo.pack(pady=2)
        self.edit_db_combo.bind('<<ComboboxSelected>>', self.update_tables)

        # Table selector
        table_frame = tk.Frame(selector_frame, bg=COLORS['bg_medium'])
        table_frame.pack(side="left", padx=10, pady=10)

        tk.Label(table_frame, text=f"{ICONS['table']} Tablo:",
                bg=COLORS['bg_medium'], fg=COLORS['text_white'],
                font=FONTS['subtitle']).pack(anchor="w")

        self.edit_table_var = tk.StringVar()
        self.edit_table_combo = ttk.Combobox(table_frame, textvariable=self.edit_table_var,
                                            width=20, state="readonly")
        self.edit_table_combo.pack(pady=2)

        tk.Button(table_frame, text=f"{ICONS['import']} Yükle",
                 command=self.load_table_for_editing,
                 bg=COLORS['primary'], fg=COLORS['text_white'],
                 font=("Arial", 10, "bold"), padx=10, pady=5).pack(pady=5)

        # Action buttons - TEK SATIRDA
        right_controls = tk.Frame(selector_frame, bg=COLORS['bg_medium'])
        right_controls.pack(side="right", padx=10, pady=10)

        # Tüm butonlar yan yana
        tk.Button(right_controls, text="➕ Yeni", command=self.add_new_row,
                 bg=COLORS['success'], fg=COLORS['text_white'],
                 font=("Arial", 8, "bold"), padx=8, pady=3).pack(side="left", padx=2)
        tk.Button(right_controls, text="🗑️ Sil", command=self.delete_selected_row,
                 bg=COLORS['danger'], fg=COLORS['text_white'],
                 font=("Arial", 8, "bold"), padx=8, pady=3).pack(side="left", padx=2)
        tk.Button(right_controls, text="📥 Excel", command=self.bulk_update_from_excel,
                 bg=COLORS['info'], fg=COLORS['text_white'],
                 font=("Arial", 8, "bold"), padx=8, pady=3).pack(side="left", padx=2)
        tk.Button(right_controls, text="💾 Kaydet", command=self.save_changes,
                 bg=COLORS['warning'], fg=COLORS['text_white'],
                 font=("Arial", 8, "bold"), padx=8, pady=3).pack(side="left", padx=2)
        tk.Button(right_controls, text="🔄 Geri", command=self.revert_changes,
                 bg=COLORS['dark'], fg=COLORS['text_white'],
                 font=("Arial", 8, "bold"), padx=8, pady=3).pack(side="left", padx=2)

        # 🚀 YENİ: Pagination kontrolü frame
        pagination_frame = tk.Frame(self.frame, bg=COLORS['bg_light'], height=50)
        pagination_frame.pack(fill="x", padx=5, pady=5)
        pagination_frame.pack_propagate(False)

        # Sayfa bilgisi
        self.page_info_label = tk.Label(pagination_frame,
                                        text="Veri yüklenmedi",
                                        bg=COLORS['bg_light'],
                                        font=FONTS['normal'])
        self.page_info_label.pack(side="left", padx=10)

        # Pagination butonları
        pagination_buttons = tk.Frame(pagination_frame, bg=COLORS['bg_light'])
        pagination_buttons.pack(side="right", padx=10)

        self.btn_first = tk.Button(pagination_buttons, text="⏮ İlk",
                                   command=self.goto_first_page,
                                   bg=COLORS['primary'], fg=COLORS['text_white'],
                                   font=("Arial", 9), padx=10, pady=3, state="disabled")
        self.btn_first.pack(side="left", padx=2)

        self.btn_prev = tk.Button(pagination_buttons, text="◀ Önceki",
                                 command=self.goto_prev_page,
                                 bg=COLORS['primary'], fg=COLORS['text_white'],
                                 font=("Arial", 9), padx=10, pady=3, state="disabled")
        self.btn_prev.pack(side="left", padx=2)

        # Sayfa numarası göstergesi
        self.current_page_label = tk.Label(pagination_buttons,
                                          text="Sayfa: - / -",
                                          bg=COLORS['bg_light'],
                                          font=FONTS['subtitle'])
        self.current_page_label.pack(side="left", padx=10)

        self.btn_next = tk.Button(pagination_buttons, text="Sonraki ▶",
                                 command=self.goto_next_page,
                                 bg=COLORS['primary'], fg=COLORS['text_white'],
                                 font=("Arial", 9), padx=10, pady=3, state="disabled")
        self.btn_next.pack(side="left", padx=2)

        self.btn_last = tk.Button(pagination_buttons, text="Son ⏭",
                                  command=self.goto_last_page,
                                  bg=COLORS['primary'], fg=COLORS['text_white'],
                                  font=("Arial", 9), padx=10, pady=3, state="disabled")
        self.btn_last.pack(side="left", padx=2)

        # Sayfa seçici
        tk.Label(pagination_buttons, text="Git:",
                bg=COLORS['bg_light'], font=FONTS['small']).pack(side="left", padx=(20, 5))

        self.page_entry = tk.Entry(pagination_buttons, width=5, font=FONTS['normal'])
        self.page_entry.pack(side="left", padx=2)
        self.page_entry.bind('<Return>', lambda e: self.goto_specific_page())

        tk.Button(pagination_buttons, text="Git",
                 command=self.goto_specific_page,
                 bg=COLORS['info'], fg=COLORS['text_white'],
                 font=("Arial", 8), padx=5, pady=2).pack(side="left", padx=2)

        # Status frame
        status_frame = tk.Frame(self.frame)
        status_frame.pack(fill="x", padx=5)

        self.changes_label = tk.Label(status_frame, text=f"{ICONS['success']} Değişiklik yok",
                                      font=FONTS['normal'], fg=COLORS['success'])
        self.changes_label.pack(side="left")

        # 🚀 YENİ: Performans bilgisi
        self.performance_label = tk.Label(status_frame, text="",
                                         font=FONTS['small'], fg=COLORS['text_gray'])
        self.performance_label.pack(side="right", padx=10)

        self.edit_info_label = tk.Label(status_frame,
                                        text="💡 Düzenlemek için hücreye çift tıklayın",
                                        font=FONTS['normal'], fg=COLORS['text_gray'])
        self.edit_info_label.pack(side="right")

        # Editable treeview
        edit_tree_frame = tk.Frame(self.frame)
        edit_tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.edit_tree = ttk.Treeview(edit_tree_frame, show="headings")

        edit_v_scroll = ttk.Scrollbar(edit_tree_frame, orient="vertical", command=self.edit_tree.yview)
        edit_h_scroll = ttk.Scrollbar(edit_tree_frame, orient="horizontal", command=self.edit_tree.xview)

        self.edit_tree.configure(yscrollcommand=edit_v_scroll.set, xscrollcommand=edit_h_scroll.set)

        self.edit_tree.grid(row=0, column=0, sticky="nsew")
        edit_v_scroll.grid(row=0, column=1, sticky="ns")
        edit_h_scroll.grid(row=1, column=0, sticky="ew")

        edit_tree_frame.grid_rowconfigure(0, weight=1)
        edit_tree_frame.grid_columnconfigure(0, weight=1)

        # Bind edit events
        self.edit_tree.bind('<Double-1>', self.edit_cell)
        self.edit_tree.bind('<Delete>', self.delete_selected_row)

        # Initial refresh
        self.refresh()

    def update_tables(self, event=None):
        """Tablo listesini güncelle"""
        db_alias = self.edit_db_var.get()
        if not db_alias:
            return

        tables = self.main.db_manager.get_tables(db_alias)
        self.edit_table_combo['values'] = tables
        if tables:
            self.edit_table_combo.set(tables[0])

    def load_table_for_editing(self):
        """Tabloyu düzenleme için yükle - OPTİMİZE EDİLMİŞ"""
        db_alias = self.edit_db_var.get()
        table_name = self.edit_table_var.get()

        if not db_alias or not table_name:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı",
                                 "Veritabanı ve tablo seçin!")
            return

        # 🚀 Performans monitörü başlat
        self.performance_monitor.start_timer()

        try:
            conn = self.main.db_manager.get_connection(db_alias)

            # Toplam satır sayısını al
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
            total_rows = cursor.fetchone()[0]

            # 🚀 Büyük veri seti kontrolü
            self.is_large_dataset = total_rows > 1000

            if self.is_large_dataset:
                response = messagebox.askyesno(
                    "📊 Büyük Veri Seti Tespit Edildi!",
                    f"Bu tablo {total_rows:,} kayıt içeriyor.\n\n"
                    f"🚀 Optimizasyon Aktif!\n"
                    f"• Sayfalama kullanılacak (100 satır/sayfa)\n"
                    f"• Sadece görünen veriler yüklenecek\n"
                    f"• Değişiklikler sayfa bazlı kaydedilecek\n\n"
                    f"Devam edilsin mi?"
                )

                if not response:
                    return

            # Get table structure
            columns_info = self.main.db_manager.get_table_info(table_name, db_alias)

            # Clear existing data
            for item in self.edit_tree.get_children():
                self.edit_tree.delete(item)

            # Setup columns (rowid + actual columns)
            col_names = ["rowid"] + [col[1] for col in columns_info]
            self.edit_tree["columns"] = col_names
            self.edit_tree["show"] = "headings"

            # Configure columns
            for col in col_names:
                if col == "rowid":
                    self.edit_tree.heading(col, text="🔢 ID")
                    self.edit_tree.column(col, width=70, anchor="center")
                else:
                    self.edit_tree.heading(col, text=col)
                    self.edit_tree.column(col, width=120, anchor="center")

            # 🚀 Pagination kurulumu
            self.paginator.set_total_rows(total_rows)
            self.paginator.current_page = 0

            # İlk sayfayı yükle
            self._load_page(0, conn, table_name, col_names)

            # 🚀 Pagination butonlarını aktifleştir
            self._update_pagination_buttons()

            # 🚀 Sonraki sayfayı arka planda önceden yükle
            if total_rows > self.paginator.page_size:
                self.paginator.prefetch_next_page(conn, table_name, 0, col_names[1:])

            # Configure colors
            self.edit_tree.tag_configure("even", background=COLORS['tree_even'])
            self.edit_tree.tag_configure("odd", background=COLORS['tree_odd'])
            self.edit_tree.tag_configure("changed", background=COLORS['tree_changed'])
            self.edit_tree.tag_configure("new", background=COLORS['tree_new'])
            self.edit_tree.tag_configure("deleted", background=COLORS['tree_deleted'])

            # Reset tracking
            self.pending_changes = {}
            self.deleted_rows = set()
            self.new_rows = {}
            self.next_new_id = -1
            self.current_table = table_name
            self.current_db = db_alias

            self.update_changes_status()

            # 🚀 Performans raporla
            load_time = self.performance_monitor.stop_timer('load_times')
            page_info = self.paginator.get_page_info()

            self.performance_label.config(
                text=f"⚡ Yükleme: {load_time:.2f}s | "
                     f"📊 {page_info['start_row']}-{page_info['end_row']} / {total_rows:,}"
            )

            if self.is_large_dataset:
                messagebox.showinfo(f"{ICONS['success']} Başarılı",
                                  f"✅ Tablo yüklendi (Optimize mod)\n\n"
                                  f"📊 Toplam: {total_rows:,} kayıt\n"
                                  f"📄 Sayfa: {page_info['total_pages']} sayfa\n"
                                  f"⚡ Yükleme: {load_time:.2f} saniye\n\n"
                                  f"💡 Sayfa butonlarıyla gezinebilirsiniz")
            else:
                messagebox.showinfo(f"{ICONS['success']} Başarılı",
                                  f"{total_rows:,} kayıt yüklendi")

        except Exception as e:
            messagebox.showerror(f"{ICONS['error']} Hata",
                               f"Yükleme hatası:\n{str(e)}")

    def _load_page(self, page: int, conn, table_name: str, col_names: List[str]):
        """Belirli bir sayfayı yükle"""
        # Cache kontrolü
        cache_key = f"{table_name}_{page}"
        cached_data = self.cache.get(cache_key)

        if cached_data:
            data = cached_data
        else:
            # Veritabanından çek
            data, _ = self.paginator.get_page_data(conn, table_name, page, col_names[1:])
            self.cache.set(cache_key, data)

        # Treeview'i temizle
        for item in self.edit_tree.get_children():
            self.edit_tree.delete(item)

        # Veriyi göster
        self.original_data = {}
        for i, row in enumerate(data):
            item_id = self.edit_tree.insert("", tk.END, values=row)
            self.original_data[item_id] = row

            # Alternate colors
            tag = "even" if i % 2 == 0 else "odd"
            self.edit_tree.item(item_id, tags=(tag,))

        # Sayfa bilgisini güncelle
        page_info = self.paginator.get_page_info()
        self.page_info_label.config(
            text=f"📊 Gösterilen: {page_info['start_row']}-{page_info['end_row']} / {page_info['total_rows']:,} kayıt"
        )

        self.current_page_label.config(
            text=f"Sayfa: {page + 1} / {page_info['total_pages']}"
        )

    def _update_pagination_buttons(self):
        """Pagination butonlarının durumunu güncelle"""
        page_info = self.paginator.get_page_info()
        current = page_info['current_page']
        total = page_info['total_pages']

        # İlk ve önceki butonlar
        if current == 0:
            self.btn_first.config(state="disabled")
            self.btn_prev.config(state="disabled")
        else:
            self.btn_first.config(state="normal")
            self.btn_prev.config(state="normal")

        # Sonraki ve son butonlar
        if current >= total - 1:
            self.btn_next.config(state="disabled")
            self.btn_last.config(state="disabled")
        else:
            self.btn_next.config(state="normal")
            self.btn_last.config(state="normal")

    def goto_first_page(self):
        """İlk sayfaya git"""
        if not self.current_table or not self.current_db:
            return

        self.paginator.current_page = 0
        conn = self.main.db_manager.get_connection(self.current_db)
        col_names = list(self.edit_tree["columns"])
        self._load_page(0, conn, self.current_table, col_names)
        self._update_pagination_buttons()

    def goto_prev_page(self):
        """Önceki sayfaya git"""
        if not self.current_table or not self.current_db:
            return

        if self.paginator.current_page > 0:
            self.paginator.current_page -= 1
            conn = self.main.db_manager.get_connection(self.current_db)
            col_names = list(self.edit_tree["columns"])
            self._load_page(self.paginator.current_page, conn, self.current_table, col_names)
            self._update_pagination_buttons()

    def goto_next_page(self):
        """Sonraki sayfaya git"""
        if not self.current_table or not self.current_db:
            return

        page_info = self.paginator.get_page_info()
        if self.paginator.current_page < page_info['total_pages'] - 1:
            self.paginator.current_page += 1
            conn = self.main.db_manager.get_connection(self.current_db)
            col_names = list(self.edit_tree["columns"])
            self._load_page(self.paginator.current_page, conn, self.current_table, col_names)
            self._update_pagination_buttons()

            # 🚀 Sonraki sayfayı arka planda yükle
            self.paginator.prefetch_next_page(conn, self.current_table,
                                             self.paginator.current_page, col_names[1:])

    def goto_last_page(self):
        """Son sayfaya git"""
        if not self.current_table or not self.current_db:
            return

        page_info = self.paginator.get_page_info()
        self.paginator.current_page = page_info['total_pages'] - 1
        conn = self.main.db_manager.get_connection(self.current_db)
        col_names = list(self.edit_tree["columns"])
        self._load_page(self.paginator.current_page, conn, self.current_table, col_names)
        self._update_pagination_buttons()

    def goto_specific_page(self):
        """Belirli bir sayfaya git"""
        try:
            page_num = int(self.page_entry.get()) - 1  # Kullanıcı 1'den başlar
            page_info = self.paginator.get_page_info()

            if 0 <= page_num < page_info['total_pages']:
                self.paginator.current_page = page_num
                conn = self.main.db_manager.get_connection(self.current_db)
                col_names = list(self.edit_tree["columns"])
                self._load_page(page_num, conn, self.current_table, col_names)
                self._update_pagination_buttons()
            else:
                messagebox.showwarning("Geçersiz Sayfa",
                                     f"Lütfen 1-{page_info['total_pages']} arasında bir sayı girin")
        except ValueError:
            messagebox.showwarning("Geçersiz Girdi", "Lütfen geçerli bir sayı girin")

    # ===== Diğer metodlar aynı kalacak (edit_cell, add_new_row, etc.) =====

    def edit_cell(self, event):
        """Hücre düzenle - AYNEN KALIYOR"""
        selected = self.edit_tree.selection()
        if not selected:
            return

        item = selected[0]
        column = self.edit_tree.identify_column(event.x)
        col_num = int(column.replace('#', '')) - 1

        if col_num == 0:  # rowid düzenlenemez
            messagebox.showwarning(f"{ICONS['warning']} Uyarı",
                                 "ID sütunu düzenlenemez!")
            return

        # Get current value
        current_value = self.edit_tree.item(item)['values'][col_num]

        # Edit dialog
        new_value = simpledialog.askstring(
            "Hücre Düzenle",
            f"Yeni değer girin:\n\nMevcut: {current_value}",
            initialvalue=str(current_value) if current_value else ""
        )

        if new_value is not None:
            # Update treeview
            values = list(self.edit_tree.item(item)['values'])
            values[col_num] = new_value
            self.edit_tree.item(item, values=values)

            # Mark as changed
            self.edit_tree.item(item, tags=('changed',))

            # Track change
            if item not in self.pending_changes:
                self.pending_changes[item] = {}

            col_name = self.edit_tree['columns'][col_num]
            self.pending_changes[item][col_name] = new_value

            self.update_changes_status()

    def add_new_row(self):
        """Yeni satır ekle - AYNEN KALIYOR"""
        if not self.current_table:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı",
                                 "Önce bir tablo yükleyin!")
            return

        # Create empty row
        num_cols = len(self.edit_tree['columns'])
        new_values = [self.next_new_id] + [""] * (num_cols - 1)

        item_id = self.edit_tree.insert("", tk.END, values=new_values)
        self.edit_tree.item(item_id, tags=('new',))

        self.new_rows[item_id] = new_values[1:]  # rowid hariç
        self.next_new_id -= 1

        self.update_changes_status()

    def delete_selected_row(self, event=None):
        """Seçili satırı sil - AYNEN KALIYOR"""
        selected = self.edit_tree.selection()
        if not selected:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı",
                                 "Silinecek satırı seçin!")
            return

        if messagebox.askyesno(f"{ICONS['warning']} Onay",
                              "Seçili satırı silmek istiyor musunuz?"):
            for item in selected:
                self.deleted_rows.add(item)
                self.edit_tree.item(item, tags=('deleted',))

            self.update_changes_status()

    def save_changes(self):
        """Değişiklikleri kaydet - AYNEN KALIYOR (ama uyarı ekliyoruz)"""
        if not self.pending_changes and not self.deleted_rows and not self.new_rows:
            messagebox.showinfo(f"{ICONS['info']} Bilgi",
                              "Kaydedilecek değişiklik yok!")
            return

        if not self.current_table or not self.current_db:
            return

        # 🚀 Büyük veri seti uyarısı
        if self.is_large_dataset:
            response = messagebox.askyesno(
                "💾 Değişiklikler Kaydedilecek",
                f"⚠️ Bu sayfadaki değişiklikler kaydedilecek:\n\n"
                f"• Güncellenen: {len(self.pending_changes)}\n"
                f"• Silinen: {len(self.deleted_rows)}\n"
                f"• Eklenen: {len(self.new_rows)}\n\n"
                f"💡 Diğer sayfalardaki değişiklikler etkilenmeyecek.\n\n"
                f"Devam edilsin mi?"
            )

            if not response:
                return

        try:
            conn = self.main.db_manager.get_connection(self.current_db)
            cursor = conn.cursor()

            # Apply updates
            for item, changes in self.pending_changes.items():
                rowid = self.edit_tree.item(item)['values'][0]

                set_clause = ", ".join([f"`{col}` = ?" for col in changes.keys()])
                values = list(changes.values()) + [rowid]

                query = f"UPDATE `{self.current_table}` SET {set_clause} WHERE rowid = ?"
                cursor.execute(query, values)

            # Apply deletes
            for item in self.deleted_rows:
                if item in self.original_data:
                    rowid = self.original_data[item][0]
                    cursor.execute(f"DELETE FROM `{self.current_table}` WHERE rowid = ?", (rowid,))
                    self.edit_tree.delete(item)

            # Apply inserts
            for item, values in self.new_rows.items():
                columns = self.edit_tree['columns'][1:]  # rowid hariç
                placeholders = ", ".join(["?"] * len(values))
                cols_str = ", ".join([f"`{col}`" for col in columns])

                query = f"INSERT INTO `{self.current_table}` ({cols_str}) VALUES ({placeholders})"
                cursor.execute(query, values)

            conn.commit()

            messagebox.showinfo(f"{ICONS['success']} Başarılı",
                              f"Değişiklikler kaydedildi!\n\n"
                              f"Güncellenen: {len(self.pending_changes)}\n"
                              f"Silinen: {len(self.deleted_rows)}\n"
                              f"Eklenen: {len(self.new_rows)}")

            # 🚀 Cache'i temizle ve mevcut sayfayı yeniden yükle
            self.cache.clear()
            current_page = self.paginator.current_page
            col_names = list(self.edit_tree["columns"])
            self._load_page(current_page, conn, self.current_table, col_names)

            self.main.refresh_all()

        except Exception as e:
            conn.rollback()
            messagebox.showerror(f"{ICONS['error']} Hata",
                               f"Kaydetme hatası:\n{str(e)}")

    def revert_changes(self):
        """Değişiklikleri geri al - AYNEN KALIYOR"""
        if not self.pending_changes and not self.deleted_rows and not self.new_rows:
            messagebox.showinfo(f"{ICONS['info']} Bilgi",
                              "Geri alınacak değişiklik yok!")
            return

        if messagebox.askyesno(f"{ICONS['warning']} Onay",
                              "Tüm değişiklikleri geri almak istiyor musunuz?"):
            # Mevcut sayfayı yeniden yükle
            if self.current_table and self.current_db:
                conn = self.main.db_manager.get_connection(self.current_db)
                col_names = list(self.edit_tree["columns"])
                current_page = self.paginator.current_page
                self._load_page(current_page, conn, self.current_table, col_names)

                # Tracking'i sıfırla
                self.pending_changes = {}
                self.deleted_rows = set()
                self.new_rows = {}

                self.update_changes_status()

    def update_changes_status(self):
        """Değişiklik durumunu güncelle - AYNEN KALIYOR"""
        total_changes = len(self.pending_changes) + len(self.deleted_rows) + len(self.new_rows)

        if total_changes == 0:
            self.changes_label.config(
                text=f"{ICONS['success']} Değişiklik yok",
                fg=COLORS['success']
            )
        else:
            self.changes_label.config(
                text=f"{ICONS['warning']} {total_changes} değişiklik (Güncelleme: {len(self.pending_changes)}, "
                     f"Silme: {len(self.deleted_rows)}, Ekleme: {len(self.new_rows)})",
                fg=COLORS['warning']
            )

    def bulk_update_from_excel(self):
        """Excel'den toplu güncelleme - AYNEN KALIYOR (tüm kod korunuyor)"""
        if not self.current_table or not self.current_db:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı",
                                 "Önce bir tablo yükleyin!")
            return

        file_path = filedialog.askopenfilename(
            title="Güncelleme Excel Dosyası Seçin",
            filetypes=FILE_TYPES['excel']
        )

        if not file_path:
            return

        try:
            from utils.excel_handler import ExcelHandler

            # Excel'i oku
            success, df = ExcelHandler.import_excel(file_path)

            if not success:
                messagebox.showerror(f"{ICONS['error']} Hata", df)
                return

            # id sütunu var mı kontrol et
            if 'id' not in df.columns:
                messagebox.showerror(f"{ICONS['error']} Hata",
                                   "Excel'de 'id' sütunu bulunamadı!\n\n"
                                   "Toplu güncelleme için Excel'de 'id' sütunu olmalıdır.")
                return

            # Mevcut tablo sütunlarını al
            conn = self.main.db_manager.get_connection(self.current_db)
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info(`{self.current_table}`)")
            table_columns = [col[1] for col in cursor.fetchall()]

            # Güncellenebilecek sütunları bul (id hariç, tabloda olan)
            updatable_columns = [col for col in df.columns
                               if col != 'id' and col in table_columns]

            if not updatable_columns:
                messagebox.showwarning(f"{ICONS['warning']} Uyarı",
                                     "Güncellenecek sütun bulunamadı!\n\n"
                                     "Excel'deki sütunlar tablodaki sütunlarla eşleşmiyor.")
                return

            # Önizleme dialog
            preview_dialog = tk.Toplevel(self.main.root)
            preview_dialog.title("📄 Toplu Güncelleme Önizleme")
            preview_dialog.geometry("600x500")
            preview_dialog.transient(self.main.root)
            preview_dialog.grab_set()

            tk.Label(preview_dialog, text="📋 Toplu Güncelleme Özeti",
                    font=FONTS['title']).pack(pady=10)

            # Bilgi frame
            info_frame = tk.Frame(preview_dialog, bg=COLORS['bg_light'])
            info_frame.pack(fill="x", padx=20, pady=10)

            tk.Label(info_frame, text=f"📊 Toplam Kayıt: {len(df)}\n"
                                     f"🔑 Eşleşme Anahtarı: id\n"
                                     f"📝 Güncellenecek Sütunlar: {', '.join(updatable_columns)}",
                    bg=COLORS['bg_light'], font=FONTS['normal'],
                    justify="left").pack(pady=10)

            # Sütun seçici
            tk.Label(preview_dialog, text="Güncellenecek sütunları seçin:",
                    font=FONTS['subtitle']).pack(anchor="w", padx=20, pady=(10, 5))

            columns_frame = tk.Frame(preview_dialog)
            columns_frame.pack(fill="both", expand=True, padx=20, pady=10)

            # Scrollable frame için canvas
            canvas = tk.Canvas(columns_frame, height=200)
            scrollbar = ttk.Scrollbar(columns_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Checkbox'lar
            column_vars = {}
            for col in updatable_columns:
                var = tk.BooleanVar(value=True)
                column_vars[col] = var
                tk.Checkbutton(scrollable_frame, text=f"☑ {col}",
                             variable=var, font=FONTS['normal']).pack(anchor="w", padx=10, pady=2)

            result = {'confirmed': False}

            def confirm_update():
                selected_columns = [col for col, var in column_vars.items() if var.get()]

                if not selected_columns:
                    messagebox.showwarning(f"{ICONS['warning']} Uyarı",
                                         "En az bir sütun seçmelisiniz!")
                    return

                result['confirmed'] = True
                result['columns'] = selected_columns
                preview_dialog.destroy()

            # Butonlar
            btn_frame = tk.Frame(preview_dialog)
            btn_frame.pack(pady=20)

            tk.Button(btn_frame, text="💾 Toplu Güncelle", command=confirm_update,
                     bg=COLORS['success'], fg=COLORS['text_white'],
                     font=FONTS['subtitle'], padx=20).pack(side="left", padx=5)
            tk.Button(btn_frame, text="İptal", command=preview_dialog.destroy,
                     bg=COLORS['danger'], fg=COLORS['text_white'],
                     font=FONTS['subtitle'], padx=20).pack(side="left", padx=5)

            self.main.root.wait_window(preview_dialog)

            if not result.get('confirmed'):
                return

            # Toplu güncelleme yap
            selected_columns = result['columns']
            updated_count = 0
            not_found_count = 0

            cursor = conn.cursor()

            for _, row in df.iterrows():
                row_id = row['id']

                # Bu id var mı kontrol et
                cursor.execute(f"SELECT COUNT(*) FROM `{self.current_table}` WHERE id = ?", (row_id,))
                if cursor.fetchone()[0] == 0:
                    not_found_count += 1
                    continue

                # UPDATE sorgusu oluştur
                set_clause = ", ".join([f"`{col}` = ?" for col in selected_columns])
                # Pandas Timestamp'leri string'e çevir
                values = []
                for col in selected_columns:
                    val = row[col]
                    # Timestamp veya datetime ise string'e çevir
                    if hasattr(val, 'strftime'):
                        values.append(val.strftime('%Y-%m-%d %H:%M:%S'))
                    else:
                        values.append(val)
                values.append(row_id)

                update_query = f"UPDATE `{self.current_table}` SET {set_clause} WHERE id = ?"
                cursor.execute(update_query, values)
                updated_count += 1

            conn.commit()

            messagebox.showinfo(f"{ICONS['success']} Başarılı",
                              f"✅ Toplu güncelleme tamamlandı!\n\n"
                              f"📊 Güncellenen: {updated_count} kayıt\n"
                              f"⚠️ Bulunamayan: {not_found_count} kayıt\n"
                              f"📝 Güncellenen Sütunlar: {', '.join(selected_columns)}")

            # 🚀 Cache'i temizle ve tabloyu yeniden yükle
            self.cache.clear()
            self.load_table_for_editing()

        except Exception as e:
            messagebox.showerror(f"{ICONS['error']} Hata",
                               f"Toplu güncelleme hatası:\n{str(e)}")

    def refresh(self):
        """Sekmeyi yenile - AYNEN KALIYOR"""
        db_list = self.main.db_manager.get_database_list()
        self.edit_db_combo['values'] = db_list

        if self.main.db_manager.active_db:
            self.edit_db_combo.set(self.main.db_manager.active_db)
            self.update_tables()

        # Eğer bir tablo yüklüyse, onu otomatik yenile
        if self.current_table and self.current_db:
            # Kaydedilmemiş değişiklikler var mı kontrol et
            if self.pending_changes or self.deleted_rows or self.new_rows:
                # Kullanıcıya sor
                response = messagebox.askyesno(
                    f"{ICONS['warning']} Kaydedilmemiş Değişiklikler",
                    "Tabloda kaydedilmemiş değişiklikler var!\n\n"
                    "Tabloyu yenilemek değişiklikleri kaybettirecek.\n\n"
                    "Yine de yenilemek istiyor musunuz?"
                )

                if response:
                    # Değişiklikleri sıfırla ve tabloyu yeniden yükle
                    self.pending_changes = {}
                    self.deleted_rows = set()
                    self.new_rows = {}

                    # Mevcut sayfayı yeniden yükle
                    conn = self.main.db_manager.get_connection(self.current_db)
                    col_names = list(self.edit_tree["columns"])
                    current_page = self.paginator.current_page
                    self._load_page(current_page, conn, self.current_table, col_names)
            else:
                # Değişiklik yoksa direkt yenile
                conn = self.main.db_manager.get_connection(self.current_db)
                col_names = list(self.edit_tree["columns"])
                current_page = self.paginator.current_page
                self._load_page(current_page, conn, self.current_table, col_names)