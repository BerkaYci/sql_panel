"""
Veritabanı Yöneticisi
Tüm veritabanı bağlantılarını ve işlemlerini yönetir
"""

import sqlite3
import os
from typing import Dict, List, Tuple, Optional, Any


class DatabaseManager:
    """Çoklu veritabanı bağlantılarını yöneten sınıf"""

    def __init__(self):
        self.connections: Dict[str, Dict] = {}
        self.active_db: Optional[str] = None

    def create_database(self, db_path: str, alias: str) -> Tuple[bool, str]:
        """Yeni veritabanı oluştur"""
        try:
            if alias in self.connections:
                return False, f"'{alias}' takma adı zaten kullanılıyor!"

            conn = sqlite3.connect(db_path, timeout=10)
            conn.execute("PRAGMA foreign_keys = ON")  # Foreign key desteği

            self.connections[alias] = {
                'conn': conn,
                'path': db_path,
                'active': True
            }

            self.active_db = alias
            return True, f"Veritabanı oluşturuldu: {alias}"

        except Exception as e:
            return False, f"Veritabanı oluşturulamadı: {str(e)}"

    def open_database(self, db_path: str, alias: str, replace: bool = False) -> Tuple[bool, str]:
        """Mevcut veritabanını aç"""
        try:
            if not os.path.exists(db_path):
                return False, "Veritabanı dosyası bulunamadı!"

            if alias in self.connections:
                if replace:
                    self.close_database(alias)
                else:
                    return False, f"'{alias}' zaten bağlı!"

            conn = sqlite3.connect(db_path, timeout=10)
            conn.execute("PRAGMA foreign_keys = ON")

            self.connections[alias] = {
                'conn': conn,
                'path': db_path,
                'active': True
            }

            self.active_db = alias
            return True, f"Veritabanına bağlanıldı: {alias}"

        except Exception as e:
            return False, f"Bağlantı hatası: {str(e)}"

    def attach_database(self, db_path: str, attach_alias: str) -> Tuple[bool, str]:
        """Mevcut oturuma başka bir veritabanı ekle (ATTACH)"""
        try:
            if not self.active_db:
                return False, "Önce bir ana veritabanı açın!"

            if not os.path.exists(db_path):
                return False, "Veritabanı dosyası bulunamadı!"

            conn = self.get_active_connection()
            if not conn:
                return False, "Aktif bağlantı bulunamadı!"

            conn.execute(f"ATTACH DATABASE '{db_path}' AS {attach_alias}")

            return True, f"Veritabanı eklendi: {attach_alias}"

        except Exception as e:
            return False, f"Attach hatası: {str(e)}"

    def close_database(self, alias: str) -> Tuple[bool, str]:
        """Veritabanı bağlantısını kapat"""
        try:
            if alias not in self.connections:
                return False, f"'{alias}' bağlantısı bulunamadı!"

            self.connections[alias]['conn'].close()
            del self.connections[alias]

            # Aktif DB kapatıldıysa başka birini aktif yap
            if self.active_db == alias:
                if self.connections:
                    self.active_db = list(self.connections.keys())[0]
                else:
                    self.active_db = None

            return True, f"Bağlantı kapatıldı: {alias}"

        except Exception as e:
            return False, f"Kapatma hatası: {str(e)}"

    def close_all(self) -> int:
        """Tüm bağlantıları kapat"""
        count = 0
        for alias in list(self.connections.keys()):
            success, _ = self.close_database(alias)
            if success:
                count += 1
        return count

    def set_active_database(self, alias: str) -> bool:
        """Aktif veritabanını değiştir"""
        if alias in self.connections:
            self.active_db = alias
            return True
        return False

    def get_active_connection(self) -> Optional[sqlite3.Connection]:
        """Aktif veritabanı bağlantısını getir"""
        if self.active_db and self.active_db in self.connections:
            return self.connections[self.active_db]['conn']
        return None

    def get_connection(self, alias: str) -> Optional[sqlite3.Connection]:
        """Belirli bir veritabanı bağlantısını getir"""
        if alias in self.connections:
            return self.connections[alias]['conn']
        return None

    def get_database_list(self) -> List[str]:
        """Bağlı veritabanı listesini getir"""
        return list(self.connections.keys())

    def get_database_info(self, alias: str) -> Optional[Dict]:
        """Veritabanı bilgilerini getir"""
        if alias not in self.connections:
            return None

        db_info = self.connections[alias].copy()

        try:
            # Dosya boyutu
            db_info['size'] = os.path.getsize(db_info['path'])

            # Tablo sayısı
            conn = db_info['conn']
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            db_info['table_count'] = cursor.fetchone()[0]

            # Dosya adı
            db_info['filename'] = os.path.basename(db_info['path'])

            # Aktif mi?
            db_info['is_active'] = (alias == self.active_db)

        except Exception as e:
            db_info['error'] = str(e)

        return db_info

    def get_all_database_info(self) -> List[Dict]:
        """Tüm veritabanlarının bilgilerini getir"""
        return [self.get_database_info(alias) for alias in self.connections.keys()]

    def get_tables(self, alias: Optional[str] = None) -> List[str]:
        """Veritabanındaki tabloları listele"""
        try:
            if alias:
                conn = self.get_connection(alias)
            else:
                conn = self.get_active_connection()

            if not conn:
                return []

            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            return [row[0] for row in cursor.fetchall()]

        except Exception:
            return []

    def get_table_info(self, table_name: str, alias: Optional[str] = None) -> List[Tuple]:
        """Tablo yapısını getir (PRAGMA table_info)"""
        try:
            if alias:
                conn = self.get_connection(alias)
            else:
                conn = self.get_active_connection()

            if not conn:
                return []

            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info(`{table_name}`)")
            return cursor.fetchall()

        except Exception:
            return []

    def get_table_row_count(self, table_name: str, alias: Optional[str] = None) -> int:
        """Tablodaki kayıt sayısını getir"""
        try:
            if alias:
                conn = self.get_connection(alias)
            else:
                conn = self.get_active_connection()

            if not conn:
                return 0

            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
            return cursor.fetchone()[0]

        except Exception:
            return 0

    def execute_query(self, query: str, params: Optional[Tuple] = None,
                      alias: Optional[str] = None) -> Tuple[bool, Any]:
        """SQL sorgusu çalıştır"""
        try:
            if alias:
                conn = self.get_connection(alias)
            else:
                conn = self.get_active_connection()

            if not conn:
                return False, "Aktif bağlantı bulunamadı!"

            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # SELECT sorgusu mu kontrol et
            if query.strip().upper().startswith(('SELECT', 'PRAGMA')):
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                return True, {'rows': results, 'columns': columns}
            else:
                conn.commit()
                return True, {'affected': cursor.rowcount}

        except Exception as e:
            return False, str(e)

    def export_table_to_dict(self, table_name: str, limit: Optional[int] = None,
                             alias: Optional[str] = None) -> List[Dict]:
        """Tablo verisini dictionary listesi olarak dışa aktar"""
        try:
            if alias:
                conn = self.get_connection(alias)
            else:
                conn = self.get_active_connection()

            if not conn:
                return []

            # Sütun isimlerini al
            columns_info = self.get_table_info(table_name, alias)
            columns = [col[1] for col in columns_info]

            # Veriyi çek
            cursor = conn.cursor()
            if limit:
                cursor.execute(f"SELECT * FROM `{table_name}` LIMIT {limit}")
            else:
                cursor.execute(f"SELECT * FROM `{table_name}`")

            rows = cursor.fetchall()

            # Dictionary formatına çevir
            return [dict(zip(columns, row)) for row in rows]

        except Exception:
            return []

    def vacuum_database(self, alias: Optional[str] = None) -> Tuple[bool, str]:
        """Veritabanını optimize et (VACUUM)"""
        try:
            if alias:
                conn = self.get_connection(alias)
            else:
                conn = self.get_active_connection()

            if not conn:
                return False, "Aktif bağlantı bulunamadı!"

            conn.execute("VACUUM")
            return True, "Veritabanı optimize edildi!"

        except Exception as e:
            return False, f"Optimize hatası: {str(e)}"

    def backup_database(self, alias: str, backup_path: str) -> Tuple[bool, str]:
        """Veritabanının yedeğini al"""
        try:
            if alias not in self.connections:
                return False, "Veritabanı bulunamadı!"

            source_conn = self.connections[alias]['conn']
            backup_conn = sqlite3.connect(backup_path)

            source_conn.backup(backup_conn)
            backup_conn.close()

            return True, f"Yedek oluşturuldu: {backup_path}"

        except Exception as e:
            return False, f"Yedekleme hatası: {str(e)}"