"""
Kaydedilmiş Sorgular Sekmesi
Kullanıcının kendi sorgularını yönetme
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

from config.settings import *


class MyQueriesTab:
    """Kaydedilmiş sorgular sekmesi"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main = main_window

        self.frame = ttk.Frame(parent)
        self.selected_query_id = None

        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        """UI bileşenlerini oluştur"""
        # Top controls
        controls_frame = tk.Frame(self.frame, bg=COLORS['bg_light'], height=80)
        controls_frame.pack(fill="x", padx=5, pady=5)
        controls_frame.pack_propagate(False)

        tk.Label(controls_frame, text="💾 Kaydedilmiş Sorgularım",
                bg=COLORS['bg_light'], font=FONTS['title']).pack(pady=10)

        btn_frame = tk.Frame(controls_frame, bg=COLORS['bg_light'])
        btn_frame.pack()

        tk.Button(btn_frame, text=f"{ICONS['add']} Yeni Sorgu", command=self.add_query,
                 bg=COLORS['success'], fg=COLORS['text_white'],
                 font=FONTS['normal']).pack(side="left", padx=5)
        tk.Button(btn_frame, text=f"{ICONS['edit']} Düzenle", command=self.edit_query,
                 bg=COLORS['primary'], fg=COLORS['text_white'],
                 font=FONTS['normal']).pack(side="left", padx=5)
        tk.Button(btn_frame, text=f"{ICONS['delete']} Sil", command=self.delete_query,
                 bg=COLORS['danger'], fg=COLORS['text_white'],
                 font=FONTS['normal']).pack(side="left", padx=5)
        tk.Button(btn_frame, text=f"{ICONS['refresh']} Yenile", command=self.refresh_list,
                 bg=COLORS['info'], fg=COLORS['text_white'],
                 font=FONTS['normal']).pack(side="left", padx=5)
        tk.Button(btn_frame, text="📤 Dışa Aktar", command=self.export_queries,
                 bg=COLORS['warning'], fg=COLORS['text_white'],
                 font=FONTS['normal']).pack(side="left", padx=5)
        tk.Button(btn_frame, text="📥 İçe Aktar", command=self.import_queries,
                 bg=COLORS['dark'], fg=COLORS['text_white'],
                 font=FONTS['normal']).pack(side="left", padx=5)

        # Main container
        main_container = tk.Frame(self.frame)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Left panel - Query list
        left_panel = tk.Frame(main_container, width=350, bg=COLORS['bg_light'])
        left_panel.pack(side="left", fill="y", padx=(0, 5))
        left_panel.pack_propagate(False)

        # Search
        search_frame = tk.Frame(left_panel, bg=COLORS['bg_light'])
        search_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(search_frame, text="🔍 Ara:", bg=COLORS['bg_light'],
                font=FONTS['normal']).pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               font=FONTS['normal'])
        search_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Category filter
        filter_frame = tk.Frame(left_panel, bg=COLORS['bg_light'])
        filter_frame.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(filter_frame, text="Kategori:", bg=COLORS['bg_light'],
                font=FONTS['small']).pack(side="left")

        self.category_var = tk.StringVar(value="Tümü")
        self.category_combo = ttk.Combobox(filter_frame, textvariable=self.category_var,
                                          width=15, state="readonly")
        self.category_combo.pack(side="left", padx=5)
        self.category_combo.bind('<<ComboboxSelected>>', self.on_category_change)

        # Query list
        list_frame = tk.Frame(left_panel, bg=COLORS['bg_light'])
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Treeview for queries
        self.queries_tree = ttk.Treeview(list_frame,
                                        columns=("name", "category", "usage"),
                                        show="headings", height=20)

        self.queries_tree.heading("name", text="📋 Sorgu Adı")
        self.queries_tree.heading("category", text="📁 Kategori")
        self.queries_tree.heading("usage", text="📊 Kullanım")

        self.queries_tree.column("name", width=88)
        self.queries_tree.column("category", width=72)
        self.queries_tree.column("usage", width=80, anchor="center")

        tree_scroll = ttk.Scrollbar(list_frame, orient="vertical",
                                   command=self.queries_tree.yview)
        self.queries_tree.configure(yscrollcommand=tree_scroll.set)

        self.queries_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        self.queries_tree.bind('<<TreeviewSelect>>', self.on_query_select)
        self.queries_tree.bind('<Double-1>', self.use_query)

        # Statistics
        stats_frame = tk.Frame(left_panel, bg=COLORS['bg_light'])
        stats_frame.pack(fill="x", padx=10, pady=5)

        self.stats_label = tk.Label(stats_frame, text="", bg=COLORS['bg_light'],
                                    font=FONTS['small'], fg=COLORS['text_gray'])
        self.stats_label.pack()

        # Right panel - Query details
        right_panel = tk.Frame(main_container)
        right_panel.pack(side="right", fill="both", expand=True)

        # Query info
        info_frame = tk.Frame(right_panel)
        info_frame.pack(fill="x", pady=(0, 10))

        tk.Label(info_frame, text="📋 Sorgu Detayları:",
                font=FONTS['subtitle']).pack(anchor="w")

        self.info_text = tk.Text(info_frame, height=4, font=FONTS['small'],
                                bg=COLORS['bg_light'], wrap="word")
        self.info_text.pack(fill="x", pady=5)

        # Query preview
        tk.Label(right_panel, text="👀 Sorgu Önizleme:",
                font=FONTS['subtitle']).pack(anchor="w", pady=(10, 5))

        preview_frame = tk.Frame(right_panel)
        preview_frame.pack(fill="both", expand=True)

        self.query_preview = tk.Text(preview_frame, font=FONTS['code'],
                                     bg=COLORS['bg_dark'], fg=COLORS['text_light'],
                                     wrap="word")

        preview_scroll = ttk.Scrollbar(preview_frame, orient="vertical",
                                      command=self.query_preview.yview)
        self.query_preview.configure(yscrollcommand=preview_scroll.set)

        self.query_preview.pack(side="left", fill="both", expand=True)
        preview_scroll.pack(side="right", fill="y")

        # Action buttons
        action_frame = tk.Frame(right_panel)
        action_frame.pack(fill="x", pady=10)

        tk.Button(action_frame, text="▶️ Sorguyu Çalıştır", command=self.use_query,
                 bg=COLORS['success'], fg=COLORS['text_white'],
                 font=FONTS['subtitle'], padx=20).pack(side="left", padx=5)
        tk.Button(action_frame, text="📋 Panoya Kopyala", command=self.copy_query,
                 bg=COLORS['primary'], fg=COLORS['text_white'],
                 font=FONTS['subtitle'], padx=20).pack(side="left", padx=5)

    def refresh_list(self):
        """Sorgu listesini yenile"""
        # Clear tree
        for item in self.queries_tree.get_children():
            self.queries_tree.delete(item)

        # Get queries
        if self.category_var.get() == "Tümü":
            queries = self.main.saved_queries.get_all_queries()
        else:
            queries = self.main.saved_queries.get_queries_by_category(
                self.category_var.get()
            )

        # Add to tree
        for q in queries:
            self.queries_tree.insert("", tk.END,
                                    values=(q['name'], q['category'], q['usage_count']),
                                    tags=(q['id'],))

        # Update categories
        categories = ["Tümü"] + self.main.saved_queries.get_categories()
        self.category_combo['values'] = categories

        # Update statistics
        stats = self.main.saved_queries.get_statistics()
        stats_text = f"📊 Toplam: {stats['total']} sorgu | "
        stats_text += f"📁 {stats['categories']} kategori | "
        stats_text += f"🔥 {stats['total_usage']} kullanım"
        self.stats_label.config(text=stats_text)

    def on_query_select(self, event):
        """Sorgu seçildiğinde"""
        selected = self.queries_tree.selection()
        if not selected:
            return

        item = selected[0]
        query_id = self.queries_tree.item(item)['tags'][0]
        self.selected_query_id = query_id

        # Get query details
        query_data = self.main.saved_queries.get_query(query_id)
        if query_data:
            # Update info
            info = f"📋 İsim: {query_data['name']}\n"
            info += f"📁 Kategori: {query_data['category']}\n"
            info += f"📝 Açıklama: {query_data['description'] or 'Yok'}\n"
            info += f"📊 Kullanım: {query_data['usage_count']} kez"

            self.info_text.delete("1.0", tk.END)
            self.info_text.insert("1.0", info)

            # Update preview
            self.query_preview.delete("1.0", tk.END)
            self.query_preview.insert("1.0", query_data['query'])

    def add_query(self):
        """Yeni sorgu ekle"""
        dialog = QueryDialog(self.main.root, "Yeni Sorgu Ekle")
        self.main.root.wait_window(dialog.dialog)  # Dialog kapanana kadar bekle

        if dialog.result:
            success, message = self.main.saved_queries.add_query(
                dialog.result['name'],
                dialog.result['query'],
                dialog.result['description'],
                dialog.result['category']
            )

            if success:
                messagebox.showinfo(f"{ICONS['success']} Başarılı", message)
                self.refresh_list()
            else:
                messagebox.showerror(f"{ICONS['error']} Hata", message)

    def edit_query(self):
        """Sorgu düzenle"""
        if not self.selected_query_id:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı",
                                 "Düzenlenecek sorguyu seçin!")
            return

        query_data = self.main.saved_queries.get_query(self.selected_query_id)
        if not query_data:
            return

        dialog = QueryDialog(self.main.root, "Sorgu Düzenle", query_data)
        self.main.root.wait_window(dialog.dialog)  # Dialog kapanana kadar bekle

        if dialog.result:
            success, message = self.main.saved_queries.update_query(
                self.selected_query_id,
                dialog.result['name'],
                dialog.result['query'],
                dialog.result['description'],
                dialog.result['category']
            )

            if success:
                messagebox.showinfo(f"{ICONS['success']} Başarılı", message)
                self.refresh_list()
                self.main.query_tab.refresh_saved_queries()  # SQL sekmesini güncelle
            else:
                messagebox.showerror(f"{ICONS['error']} Hata", message)

    def delete_query(self):
        """Sorgu sil"""
        if not self.selected_query_id:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı",
                                 "Silinecek sorguyu seçin!")
            return

        query_data = self.main.saved_queries.get_query(self.selected_query_id)
        if not query_data:
            return

        if messagebox.askyesno(f"{ICONS['warning']} Onay",
                              f"'{query_data['name']}' sorgusunu silmek istiyor musunuz?"):
            success, message = self.main.saved_queries.delete_query(self.selected_query_id)

            if success:
                messagebox.showinfo(f"{ICONS['success']} Başarılı", message)
                self.selected_query_id = None
                self.info_text.delete("1.0", tk.END)
                self.query_preview.delete("1.0", tk.END)
                self.refresh_list()
                self.main.query_tab.refresh_saved_queries()  # SQL sekmesini güncelle
            else:
                messagebox.showerror(f"{ICONS['error']} Hata", message)

    def use_query(self, event=None):
        """Sorguyu SQL sekmesinde çalıştır"""
        if not self.selected_query_id:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı",
                                 "Çalıştırılacak sorguyu seçin!")
            return

        query_data = self.main.saved_queries.get_query(self.selected_query_id)
        if query_data:
            # Kullanım sayısını artır
            self.main.saved_queries.increment_usage(self.selected_query_id)

            # SQL sekmesine geç ve sorguyu ekle
            self.main.notebook.select(0)  # İlk sekme (SQL Sorguları)
            self.main.query_tab.insert_query(query_data['query'])

            messagebox.showinfo(f"{ICONS['success']} Başarılı",
                              f"'{query_data['name']}' sorgusu SQL sekmesine eklendi!")

    def copy_query(self):
        """Sorguyu panoya kopyala"""
        query_text = self.query_preview.get("1.0", tk.END).strip()
        if query_text:
            self.main.root.clipboard_clear()
            self.main.root.clipboard_append(query_text)
            messagebox.showinfo(f"{ICONS['success']}", "Sorgu panoya kopyalandı!")
        else:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı",
                                 "Kopyalanacak sorgu yok!")

    def on_search(self, *args):
        """Arama yapıldığında"""
        keyword = self.search_var.get()
        if keyword:
            queries = self.main.saved_queries.search_queries(keyword)
        else:
            queries = self.main.saved_queries.get_all_queries()

        # Update tree
        for item in self.queries_tree.get_children():
            self.queries_tree.delete(item)

        for q in queries:
            self.queries_tree.insert("", tk.END,
                                    values=(q['name'], q['category'], q['usage_count']),
                                    tags=(q['id'],))

    def on_category_change(self, event):
        """Kategori değiştiğinde"""
        self.refresh_list()

    def export_queries(self):
        """Sorguları dışa aktar"""
        file_path = filedialog.asksaveasfilename(
            title="Sorguları Dışa Aktar",
            filetypes=[("JSON files", "*.json")],
            defaultextension=".json"
        )

        if file_path:
            success, message = self.main.saved_queries.export_queries(file_path)

            if success:
                messagebox.showinfo(f"{ICONS['success']} Başarılı", message)
            else:
                messagebox.showerror(f"{ICONS['error']} Hata", message)

    def import_queries(self):
        """Sorguları içe aktar"""
        file_path = filedialog.askopenfilename(
            title="Sorguları İçe Aktar",
            filetypes=[("JSON files", "*.json")]
        )

        if file_path:
            merge = messagebox.askyesno(
                "İçe Aktarma Modu",
                "Mevcut sorgularınızı korumak istiyor musunuz?\n\n"
                "EVET: Yeni sorgular eklenecek\n"
                "HAYIR: Mevcut sorgular silinecek"
            )

            success, message = self.main.saved_queries.import_queries(file_path, merge)

            if success:
                messagebox.showinfo(f"{ICONS['success']} Başarılı", message)
                self.refresh_list()
            else:
                messagebox.showerror(f"{ICONS['error']} Hata", message)


class QueryDialog:
    """Sorgu ekleme/düzenleme dialog"""

    def __init__(self, parent, title, query_data=None):
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Name
        tk.Label(self.dialog, text="Sorgu Adı:", font=FONTS['subtitle']).pack(anchor="w", padx=10, pady=(10, 0))
        self.name_var = tk.StringVar(value=query_data['name'] if query_data else "")
        tk.Entry(self.dialog, textvariable=self.name_var, font=FONTS['normal']).pack(fill="x", padx=10, pady=5)

        # Category
        tk.Label(self.dialog, text="Kategori:", font=FONTS['subtitle']).pack(anchor="w", padx=10, pady=(10, 0))
        self.category_var = tk.StringVar(value=query_data['category'] if query_data else "Genel")
        category_combo = ttk.Combobox(self.dialog, textvariable=self.category_var,
                                     values=["Genel", "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "Diğer"])
        category_combo.pack(fill="x", padx=10, pady=5)

        # Description
        tk.Label(self.dialog, text="Açıklama:", font=FONTS['subtitle']).pack(anchor="w", padx=10, pady=(10, 0))
        self.desc_text = tk.Text(self.dialog, height=3, font=FONTS['normal'])
        self.desc_text.pack(fill="x", padx=10, pady=5)
        if query_data:
            self.desc_text.insert("1.0", query_data['description'])

        # Query
        tk.Label(self.dialog, text="SQL Sorgusu:", font=FONTS['subtitle']).pack(anchor="w", padx=10, pady=(10, 0))

        query_frame = tk.Frame(self.dialog)
        query_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.query_text = tk.Text(query_frame, font=FONTS['code'], wrap="word",
                                 bg=COLORS['bg_dark'], fg=COLORS['text_light'])
        query_scroll = ttk.Scrollbar(query_frame, orient="vertical", command=self.query_text.yview)
        self.query_text.configure(yscrollcommand=query_scroll.set)

        self.query_text.pack(side="left", fill="both", expand=True)
        query_scroll.pack(side="right", fill="y")

        if query_data:
            self.query_text.insert("1.0", query_data['query'])

        # Buttons
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(btn_frame, text=f"{ICONS['save']} Kaydet", command=self.save,
                 bg=COLORS['success'], fg=COLORS['text_white'],
                 font=FONTS['subtitle'], padx=20).pack(side="right", padx=5)
        tk.Button(btn_frame, text="❌ İptal", command=self.dialog.destroy,
                 bg=COLORS['danger'], fg=COLORS['text_white'],
                 font=FONTS['subtitle'], padx=20).pack(side="right", padx=5)

    def save(self):
        """Kaydet"""
        name = self.name_var.get().strip()
        category = self.category_var.get().strip()
        description = self.desc_text.get("1.0", tk.END).strip()
        query = self.query_text.get("1.0", tk.END).strip()

        if not name:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı", "Sorgu adı boş olamaz!")
            return

        if not query:
            messagebox.showwarning(f"{ICONS['warning']} Uyarı", "Sorgu metni boş olamaz!")
            return

        self.result = {
            'name': name,
            'category': category or "Genel",
            'description': description,
            'query': query
        }

        self.dialog.destroy()