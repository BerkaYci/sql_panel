"""
SQL Sorguları Sekmesi - PERFORMANS OPTİMİZE EDİLMİŞ
Büyük sonuç setleri için akıllı limit, pagination ve progressive loading
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import pandas as pd

# Performance optimizer'ı import et
from utils.performance_optimizer import (
    QueryOptimizer,
    DataPaginator,
    PerformanceMonitor,
    ProgressiveLoader
)

from config.settings import *
from utils.excel_handler import ExcelHandler
from utils.csv_handler import CSVHandler


class QueryTab:
    """SQL Sorguları sekmesi - OPTİMİZE EDİLMİŞ"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main = main_window

        self.frame = ttk.Frame(parent)
        self.current_results = None

        # 🚀 YENİ: Performans araçları
        self.query_optimizer = QueryOptimizer()
        self.paginator = DataPaginator(page_size=1000)  # Sorgu sonuçları için 1000 satır/sayfa
        self.performance_monitor = PerformanceMonitor()
        self.progressive_loader = ProgressiveLoader(chunk_size=100)

        self.setup_ui()

    def setup_ui(self):
        """UI bileşenlerini oluştur - OPTİMİZE EDİLMİŞ"""
        # Database selector
        db_select_frame = tk.Frame(self.frame, bg=COLORS['bg_medium'], height=40)
        db_select_frame.pack(fill="x", padx=5, pady=(5, 0))
        db_select_frame.pack_propagate(False)

        tk.Label(db_select_frame, text=f"{ICONS['database']} Sorgu Veritabanı:",
                bg=COLORS['bg_medium'], fg=COLORS['text_white'],
                font=FONTS['subtitle']).pack(side="left", padx=10, pady=10)

        self.query_db_var = tk.StringVar()
        self.query_db_combo = ttk.Combobox(self.frame, textvariable=self.query_db_var,
                                          width=20, state="readonly")
        self.query_db_combo.pack(in_=db_select_frame, side="left", padx=5, pady=10)

        # Top section - Query editor and quick queries
        top_section = tk.Frame(self.frame)
        top_section.pack(fill="x", padx=5, pady=5)

        # Left panel - Query editor
        left_panel = tk.Frame(top_section)
        left_panel.pack(side="left", fill="both", expand=True)

        query_label = tk.Label(left_panel, text="SQL Sorgusu:", font=FONTS['subtitle'])
        query_label.pack(anchor="w")

        # Query text with scrollbars
        text_frame = tk.Frame(left_panel)
        text_frame.pack(fill="both", expand=True)

        self.text_query = tk.Text(text_frame, height=12, font=FONTS['code'], wrap="none",
                                 bg=COLORS['bg_dark'], fg=COLORS['text_light'],
                                 insertbackground="white")

        query_scroll_y = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_query.yview)
        query_scroll_x = ttk.Scrollbar(text_frame, orient="horizontal", command=self.text_query.xview)
        self.text_query.configure(yscrollcommand=query_scroll_y.set, xscrollcommand=query_scroll_x.set)

        self.text_query.grid(row=0, column=0, sticky="nsew")
        query_scroll_y.grid(row=0, column=1, sticky="ns")
        query_scroll_x.grid(row=1, column=0, sticky="ew")

        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        # Query controls
        query_controls = tk.Frame(left_panel)
        query_controls.pack(fill="x", pady=(5, 0))

        tk.Button(query_controls, text=f"▶️ Çalıştır", command=self.run_query,
                 bg=COLORS['success'], fg=COLORS['text_white'],
                 font=FONTS['subtitle'], padx=20).pack(side="left", padx=2)
        tk.Button(query_controls, text=f"{ICONS['delete']} Temizle", command=self.clear_query,
                 bg=COLORS['danger'], fg=COLORS['text_white'], padx=15).pack(side="left", padx=2)
        tk.Button(query_controls, text=f"{ICONS['import']} Excel İçe Aktar", command=self.import_excel,
                 bg=COLORS['info'], fg=COLORS['text_white'], padx=15).pack(side="left", padx=2)
        tk.Button(query_controls, text=f"{ICONS['export']} Excel", command=self.export_results,
                 bg=COLORS['warning'], fg=COLORS['text_white'], padx=15).pack(side="left", padx=2)
        tk.Button(query_controls, text=f"{ICONS['save']} Kaydet", command=self.save_query,
                 bg=COLORS['dark'], fg=COLORS['text_white'], padx=15).pack(side="left", padx=2)

        # Right panel - Quick queries
        right_panel = tk.Frame(top_section, width=300)
        right_panel.pack(side="right", fill="y", padx=(10, 0))
        right_panel.pack_propagate(False)

        tk.Label(right_panel, text="🚀 Hızlı Sorgular:", font=FONTS['subtitle']).pack(anchor="w")

        for text, query in QUICK_QUERIES:
            btn = tk.Button(right_panel, text=text,
                          command=lambda q=query: self.insert_query(q),
                          bg=COLORS['bg_medium'], fg=COLORS['text_white'],
                          anchor="w", padx=10)
            btn.pack(fill="x", pady=1)

        # 🚀 YENİ: Query optimization info
        opt_frame = tk.Frame(right_panel, bg=COLORS['bg_light'])
        opt_frame.pack(fill="x", pady=10, padx=5)

        tk.Label(opt_frame, text="⚡ Akıllı Optimizasyon",
                bg=COLORS['bg_light'], font=FONTS['subtitle'],
                fg=COLORS['primary']).pack(pady=5)

        tk.Label(opt_frame,
                text="• Büyük sonuçlar otomatik limit\n"
                     "• Sayfalama ile hızlı yükleme\n"
                     "• Performans takibi aktif",
                bg=COLORS['bg_light'], font=FONTS['small'],
                fg=COLORS['text_gray'], justify="left").pack(padx=5, pady=5)

        # 🚀 YENİ: Result info bar (sonuç bilgisi)
        result_info_frame = tk.Frame(self.frame, bg=COLORS['bg_light'], height=35)
        result_info_frame.pack(fill="x", padx=5, pady=5)
        result_info_frame.pack_propagate(False)

        self.result_info_label = tk.Label(result_info_frame,
                                          text="📊 Sorgu çalıştırılmadı",
                                          bg=COLORS['bg_light'],
                                          font=FONTS['normal'])
        self.result_info_label.pack(side="left", padx=10, pady=5)

        self.performance_label = tk.Label(result_info_frame,
                                         text="",
                                         bg=COLORS['bg_light'],
                                         font=FONTS['small'],
                                         fg=COLORS['text_gray'])
        self.performance_label.pack(side="right", padx=10, pady=5)

        # Results section
        results_frame = tk.Frame(self.frame)
        results_frame.pack(fill="both", expand=True, padx=5, pady=(10, 5))

        result_label = tk.Label(results_frame, text="📊 Sonuçlar:", font=FONTS['subtitle'])
        result_label.pack(anchor="w")

        # Results treeview
        tree_frame = tk.Frame(results_frame)
        tree_frame.pack(fill="both", expand=True, pady=(5, 0))

        self.tree = ttk.Treeview(tree_frame, show="headings")

        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

    def insert_query(self, query: str):
        """Sorgu metnini editöre ekle - AYNEN KALIYOR"""
        self.text_query.delete("1.0", tk.END)
        self.text_query.insert("1.0", query)

    def clear_query(self):
        """Sorgu ve sonuçları temizle - AYNEN KALIYOR"""
        self.text_query.delete("1.0", tk.END)
        for col in self.tree.get_children():
            self.tree.delete(col)
        self.current_results = None
        self.result_info_label.config(text="📊 Sonuçlar temizlendi")
        self.performance_label.config(text="")

    def run_query(self):
        """SQL sorgusunu çalıştır - OPTİMİZE EDİLMİŞ"""
        query = self.text_query.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı", "Sorgu boş olamaz!")
            return

        # Get selected database
        db_alias = self.query_db_var.get()
        if not db_alias:
            db_alias = self.main.db_manager.active_db

        if not db_alias:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı", MESSAGES['no_db'])
            return

        # 🚀 YENİ: Akıllı limit kontrolü
        original_query = query
        optimized_query, was_optimized = self.query_optimizer.add_limit_if_missing(
            query,
            limit=10000  # Maksimum 10,000 satır döndür
        )

        if was_optimized:
            response = messagebox.askyesno(
                "⚡ Otomatik Optimizasyon",
                f"🎯 Sorgunuz optimize edildi!\n\n"
                f"ÖNCEKİ:\n{original_query[:100]}...\n\n"
                f"YENİ (LIMIT 10000 eklendi):\n{optimized_query[:100]}...\n\n"
                f"💡 Büyük veri setlerinde performans için LIMIT önerilir.\n\n"
                f"Optimize edilmiş sorguyu çalıştırmak ister misiniz?\n"
                f"(HAYIR derseniz orijinal sorgu çalışır)"
            )

            if response:
                query = optimized_query

        # 🚀 Performans monitörü başlat
        self.performance_monitor.start_timer()

        # Execute query
        self.main.update_status(f"{ICONS['info']} Sorgu çalıştırılıyor...", COLORS['warning'])

        success, result, message = self.main.query_executor.execute(query, db_alias)

        if success:
            if result['type'] == 'select':
                # 🚀 Performans metriğini kaydet
                exec_time = self.performance_monitor.stop_timer('query_times')

                # Display results
                self.display_results(result['rows'], result['columns'])
                self.current_results = result

                # 🚀 Büyük sonuç seti uyarısı
                row_count = len(result['rows'])
                if row_count >= 10000:
                    warning_msg = (
                        f"⚠️ Maksimum limit (10,000 satır) döndürüldü!\n\n"
                        f"📊 Daha fazla sonuç olabilir.\n"
                        f"💡 WHERE veya daha spesifik filtreler kullanın."
                    )
                    messagebox.showwarning("Büyük Sonuç Seti", warning_msg)

                self.main.update_status(
                    f"{ICONS['success']} {row_count:,} kayıt getirildi | DB: {db_alias}",
                    COLORS['success']
                )

                # 🚀 Performans bilgisi göster
                self.result_info_label.config(
                    text=f"✅ {row_count:,} kayıt | {len(result['columns'])} sütun | DB: {db_alias}"
                )

                self.performance_label.config(
                    text=f"⚡ Sorgu: {exec_time:.3f}s"
                )

                messagebox.showinfo(f"{ICONS['success']} Başarılı",
                                  f"{message}\n"
                                  f"📊 DB: {db_alias}\n"
                                  f"⚡ Süre: {exec_time:.3f} saniye")
            else:
                # Modify query (INSERT, UPDATE, DELETE)
                messagebox.showinfo(f"{ICONS['success']} Başarılı",
                                  f"{message}\n📊 DB: {db_alias}")
                self.main.update_status(
                    f"{ICONS['success']} {result['affected_rows']} satır etkilendi | DB: {db_alias}",
                    COLORS['success']
                )

                self.result_info_label.config(
                    text=f"✅ {result['affected_rows']} satır etkilendi"
                )

                # Refresh other tabs
                self.main.refresh_all()
        else:
            messagebox.showerror(f"{ICONS['error']} Hata",
                               f"{message}\n\n📊 DB: {db_alias}")
            self.main.update_status(f"{ICONS['error']} Sorgu hatası", COLORS['danger'])
            self.result_info_label.config(text="❌ Sorgu başarısız")

    def display_results(self, rows, columns):
        """Sorgu sonuçlarını göster - OPTİMİZE EDİLMİŞ"""
        # 🚀 Performans monitörü başlat
        self.performance_monitor.start_timer()

        # Clear old data
        for col in self.tree.get_children():
            self.tree.delete(col)

        # Update columns
        self.tree["columns"] = columns
        self.tree["show"] = "headings"

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        # 🚀 YENİ: Progresif yükleme için chunk'lara böl
        total_rows = len(rows)
        chunk_size = 100  # Her seferde 100 satır ekle

        if total_rows > 1000:
            # Büyük veri seti - önce ilk chunk'ı yükle
            first_chunk = rows[:chunk_size]
            for i, row in enumerate(first_chunk):
                tag = "even" if i % 2 == 0 else "odd"
                self.tree.insert("", tk.END, values=row, tags=(tag,))

            # Kullanıcıya bilgi ver
            remaining = total_rows - chunk_size
            if remaining > 0:
                response = messagebox.askyesno(
                    "📊 Büyük Sonuç Seti",
                    f"✅ İlk {chunk_size} satır yüklendi\n"
                    f"📊 Kalan: {remaining:,} satır\n\n"
                    f"Tüm sonuçları yüklemek ister misiniz?\n"
                    f"(Bu işlem zaman alabilir)"
                )

                if response:
                    # Geri kalan satırları yükle (batch olarak)
                    self._load_remaining_rows(rows[chunk_size:], chunk_size)
        else:
            # Normal yükleme
            for i, row in enumerate(rows):
                tag = "even" if i % 2 == 0 else "odd"
                self.tree.insert("", tk.END, values=row, tags=(tag,))

        # Configure row colors
        self.tree.tag_configure("even", background=COLORS['tree_even'])
        self.tree.tag_configure("odd", background=COLORS['tree_odd'])

        # 🚀 Render süresini kaydet
        render_time = self.performance_monitor.stop_timer('render_times')

        # Performans istatistiklerini güncelle
        current_perf = self.performance_label.cget("text")
        if current_perf:
            self.performance_label.config(
                text=f"{current_perf} | Render: {render_time:.3f}s"
            )

    def _load_remaining_rows(self, remaining_rows, chunk_size):
        """Geri kalan satırları batch olarak yükle"""
        total = len(remaining_rows)
        loaded = 0

        # Progress dialog oluştur
        progress_window = tk.Toplevel(self.main.root)
        progress_window.title("Yükleniyor...")
        progress_window.geometry("400x150")
        progress_window.transient(self.main.root)
        progress_window.grab_set()

        tk.Label(progress_window, text="📊 Sonuçlar Yükleniyor...",
                font=FONTS['title']).pack(pady=20)

        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var,
                                      maximum=100, length=350)
        progress_bar.pack(pady=10)

        status_label = tk.Label(progress_window, text="",
                               font=FONTS['normal'])
        status_label.pack(pady=10)

        def load_batch():
            nonlocal loaded

            while loaded < total:
                batch = remaining_rows[loaded:loaded + chunk_size]

                for i, row in enumerate(batch):
                    tree_index = loaded + chunk_size + i  # İlk chunk'tan sonra
                    tag = "even" if tree_index % 2 == 0 else "odd"
                    self.tree.insert("", tk.END, values=row, tags=(tag,))

                loaded += len(batch)
                progress = (loaded / total) * 100
                progress_var.set(progress)
                status_label.config(text=f"{loaded:,} / {total:,} satır yüklendi")

                # UI'ı güncelle
                progress_window.update()

                # Küçük gecikme (UI'ın donmaması için)
                if loaded % 500 == 0:
                    self.main.root.update_idletasks()

            progress_window.destroy()
            messagebox.showinfo("✅ Tamamlandı",
                              f"Tüm {total:,} satır başarıyla yüklendi!")

        # Yüklemeyi başlat
        self.main.root.after(100, load_batch)

    def export_results(self):
        """Sorgu sonuçlarını Excel'e aktar - AYNEN KALIYOR"""
        if not self.current_results or not self.current_results.get('rows'):
            messagebox.showwarning(f"{ICONS['warning']} Uyarı", MESSAGES['no_data'])
            return

        file_path = filedialog.asksaveasfilename(
            title="Excel Dosyası Kaydet",
            filetypes=FILE_TYPES['excel'],
            defaultextension=".xlsx"
        )

        if file_path:
            success, message = ExcelHandler.export_to_excel(
                self.current_results['rows'],
                self.current_results['columns'],
                file_path,
                styled=True
            )

            if success:
                messagebox.showinfo(f"{ICONS['success']} Başarılı",
                                  f"{message}\n📈 {len(self.current_results['rows']):,} satır")
            else:
                messagebox.showerror(f"{ICONS['error']} Hata", message)

    def save_query(self):
        """Sorguyu dosyaya kaydet - AYNEN KALIYOR"""
        query = self.text_query.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı", "Kaydedilecek sorgu yok!")
            return

        file_path = filedialog.asksaveasfilename(
            title="SQL Sorgusunu Kaydet",
            filetypes=FILE_TYPES['sql'],
            defaultextension=".sql"
        )

        if file_path:
            try:
                from datetime import datetime
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"-- SQL Sorgusu\n")
                    f.write(f"-- Oluşturulma: {datetime.now()}\n")
                    f.write(f"-- Veritabanı: {self.query_db_var.get() or self.main.db_manager.active_db}\n\n")
                    f.write(query)

                messagebox.showinfo(f"{ICONS['success']} Başarılı",
                                  f"Sorgu kaydedildi:\n{file_path}")
            except Exception as e:
                messagebox.showerror(f"{ICONS['error']} Hata",
                                   f"Kaydetme hatası:\n{str(e)}")

    def import_excel(self):
        """Excel dosyasını içe aktar - AYNEN KALIYOR (TÜM KOD KORUNUYOR)"""
        if not self.main.db_manager.active_db:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı", MESSAGES['no_db'])
            return

        file_path = filedialog.askopenfilename(
            title="Excel Dosyası Seçin",
            filetypes=FILE_TYPES['excel']
        )

        if not file_path:
            return

        try:
            # Get sheet names
            success, sheet_names = ExcelHandler.get_sheet_names(file_path)

            if not success:
                messagebox.showerror(f"{ICONS['error']} Hata", sheet_names)
                return

            # If multiple sheets, let user choose
            if len(sheet_names) > 1:
                sheet_dialog = tk.Toplevel(self.main.root)
                sheet_dialog.title("📊 Sayfa Seçimi")
                sheet_dialog.geometry("400x300")
                sheet_dialog.transient(self.main.root)
                sheet_dialog.grab_set()

                tk.Label(sheet_dialog, text="Excel sayfası seçin:",
                        font=FONTS['subtitle']).pack(pady=10)

                selected_sheet = tk.StringVar(value=sheet_names[0])

                for sheet in sheet_names:
                    tk.Radiobutton(sheet_dialog, text=sheet,
                                 variable=selected_sheet, value=sheet,
                                 font=FONTS['normal']).pack(anchor="w", padx=30, pady=2)

                def continue_import():
                    sheet_dialog.destroy()
                    self._do_excel_import(file_path, selected_sheet.get())

                tk.Button(sheet_dialog, text="Devam", command=continue_import,
                         bg=COLORS['primary'], fg=COLORS['text_white'],
                         font=FONTS['subtitle']).pack(pady=20)
            else:
                self._do_excel_import(file_path, sheet_names[0])

        except Exception as e:
            messagebox.showerror(f"{ICONS['error']} Hata",
                               f"Excel okunamadı:\n{str(e)}")

    def _do_excel_import(self, file_path, sheet_name):
        """Excel import işlemini gerçekleştir - AYNEN KALIYOR"""
        try:
            # Import Excel
            success, df = ExcelHandler.import_excel(file_path, sheet_name)

            if not success:
                messagebox.showerror(f"{ICONS['error']} Hata", df)
                return

            # Ask for table name
            table_name = simpledialog.askstring(
                "Tablo Adı",
                f"'{sheet_name}' için tablo adı girin:",
                initialvalue=sheet_name.replace(" ", "_").lower()
            )

            if not table_name:
                return

            # Ask for import mode
            mode_dialog = tk.Toplevel(self.main.root)
            mode_dialog.title("İçe Aktarma Modu")
            mode_dialog.geometry("400x200")
            mode_dialog.transient(self.main.root)
            mode_dialog.grab_set()

            tk.Label(mode_dialog, text="İçe aktarma modunu seçin:",
                    font=FONTS['subtitle']).pack(pady=20)

            mode_var = tk.StringVar(value="append")

            tk.Radiobutton(mode_dialog, text="🔄 Tabloyu Değiştir (Replace) - Eski veri silinir",
                         variable=mode_var, value="replace",
                         font=FONTS['normal']).pack(anchor="w", padx=30, pady=5)

            tk.Radiobutton(mode_dialog, text="➕ Altına Ekle (Append) - Eski veri kalır",
                         variable=mode_var, value="append",
                         font=FONTS['normal']).pack(anchor="w", padx=30, pady=5)

            result = {'confirmed': False}

            def confirm():
                result['confirmed'] = True
                result['mode'] = mode_var.get()
                mode_dialog.destroy()

            def cancel():
                mode_dialog.destroy()

            btn_frame = tk.Frame(mode_dialog)
            btn_frame.pack(pady=20)

            tk.Button(btn_frame, text="İçe Aktar", command=confirm,
                     bg=COLORS['success'], fg=COLORS['text_white'],
                     font=FONTS['subtitle'], padx=20).pack(side="left", padx=5)
            tk.Button(btn_frame, text="İptal", command=cancel,
                     bg=COLORS['danger'], fg=COLORS['text_white'],
                     font=FONTS['subtitle'], padx=20).pack(side="left", padx=5)

            self.main.root.wait_window(mode_dialog)

            if not result.get('confirmed'):
                return

            # Import to database
            conn = self.main.db_manager.get_active_connection()
            if_exists = result['mode']  # 'replace' or 'append'
            df.to_sql(table_name, conn, if_exists=if_exists, index=False)

            mode_text = "değiştirildi" if if_exists == 'replace' else "altına eklendi"

            messagebox.showinfo(f"{ICONS['success']} Başarılı",
                              f"✅ Excel içe aktarıldı!\n\n"
                              f"📄 Sayfa: {sheet_name}\n"
                              f"📋 Tablo: {table_name}\n"
                              f"📊 Satır: {len(df):,}\n"
                              f"📊 Sütun: {len(df.columns)}\n"
                              f"🔧 Mod: {mode_text.upper()}")

            self.main.refresh_all()

        except Exception as e:
            messagebox.showerror(f"{ICONS['error']} Hata",
                               f"Excel içe aktarılamadı:\n{str(e)}")

    def update_db_combo(self):
        """Veritabanı listesini güncelle - AYNEN KALIYOR"""
        db_list = self.main.db_manager.get_database_list()
        self.query_db_combo['values'] = db_list

        if self.main.db_manager.active_db:
            self.query_db_combo.set(self.main.db_manager.active_db)
        elif db_list:
            self.query_db_combo.set(db_list[0])

    def refresh_saved_queries(self):
        """Kaydedilmiş sorgu listesini güncelle - YENİ METOD"""
        # Bu metod my_queries_tab.py tarafından çağrılıyor
        # Şu an için sadece pass, gelecekte burada bir dropdown eklenebilir
        pass