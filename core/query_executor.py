"""
SQL Sorgu Çalıştırıcı
Sorgu geçmişi, validasyon ve güvenli çalıştırma
"""

import sqlite3
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime


class QueryExecutor:
    """SQL sorgularını yöneten ve çalıştıran sınıf"""

    def __init__(self, database_manager):
        self.db_manager = database_manager
        self.query_history: List[Dict] = []
        self.max_history = 100

    def execute(self, query: str, alias: Optional[str] = None) -> Tuple[bool, Any, str]:
        """
        SQL sorgusu çalıştır
        Returns: (başarılı_mı, sonuç, mesaj)
        """
        # Query validation
        is_valid, validation_msg = self.validate_query(query)
        if not is_valid:
            return False, None, validation_msg

        # Veritabanı bağlantısını al
        if alias:
            conn = self.db_manager.get_connection(alias)
            db_name = alias
        else:
            conn = self.db_manager.get_active_connection()
            db_name = self.db_manager.active_db

        if not conn:
            return False, None, "Aktif veritabanı bağlantısı bulunamadı!"

        start_time = datetime.now()

        try:
            cursor = conn.cursor()
            cursor.execute(query)

            # SELECT, PRAGMA, WITH gibi sorguları kontrol et
            query_upper = query.strip().upper()

            if query_upper.startswith(('SELECT', 'WITH', 'PRAGMA', 'EXPLAIN')):
                # Veri döndüren sorgular
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []

                result = {
                    'type': 'select',
                    'rows': rows,
                    'columns': columns,
                    'row_count': len(rows)
                }

                message = f"✅ {len(rows)} kayıt getirildi"

            else:
                # INSERT, UPDATE, DELETE, CREATE gibi sorgular
                conn.commit()
                affected = cursor.rowcount

                result = {
                    'type': 'modify',
                    'affected_rows': affected
                }

                message = f"✅ {affected} satır etkilendi"

            # Çalışma süresini hesapla
            execution_time = (datetime.now() - start_time).total_seconds()

            # Sorgu geçmişine ekle
            self._add_to_history(query, db_name, True, execution_time)

            return True, result, message

        except sqlite3.Error as e:
            error_msg = f"❌ SQL Hatası: {str(e)}"
            self._add_to_history(query, db_name, False, 0, str(e))
            return False, None, error_msg

        except Exception as e:
            error_msg = f"❌ Beklenmeyen Hata: {str(e)}"
            self._add_to_history(query, db_name, False, 0, str(e))
            return False, None, error_msg

    def execute_batch(self, queries: List[str], alias: Optional[str] = None) -> List[Tuple[bool, Any, str]]:
        """Birden fazla sorguyu sırayla çalıştır"""
        results = []
        for query in queries:
            if query.strip():  # Boş sorguları atla
                result = self.execute(query, alias)
                results.append(result)
        return results

    def execute_script(self, script: str, alias: Optional[str] = None) -> Tuple[bool, str]:
        """
        SQL script dosyasını çalıştır (noktalı virgülle ayrılmış çoklu sorgu)
        """
        if alias:
            conn = self.db_manager.get_connection(alias)
        else:
            conn = self.db_manager.get_active_connection()

        if not conn:
            return False, "Aktif veritabanı bağlantısı bulunamadı!"

        try:
            cursor = conn.cursor()
            cursor.executescript(script)
            conn.commit()
            return True, "✅ Script başarıyla çalıştırıldı"

        except Exception as e:
            return False, f"❌ Script hatası: {str(e)}"

    def validate_query(self, query: str) -> Tuple[bool, str]:
        """Sorgu validasyonu"""
        if not query or not query.strip():
            return False, "Sorgu boş olamaz!"

        query_stripped = query.strip().upper()

        # Tehlikeli komutları kontrol et (opsiyonel)
        dangerous_keywords = ['DROP DATABASE', 'FORMAT', 'SHUTDOWN']
        for keyword in dangerous_keywords:
            if keyword in query_stripped:
                return False, f"⚠️ Güvenlik: '{keyword}' komutu kullanılamaz!"

        return True, "OK"

    def _add_to_history(self, query: str, database: str, success: bool,
                        execution_time: float, error: Optional[str] = None):
        """Sorgu geçmişine ekle"""
        history_entry = {
            'query': query,
            'database': database,
            'timestamp': datetime.now(),
            'success': success,
            'execution_time': execution_time,
            'error': error
        }

        self.query_history.insert(0, history_entry)

        # Maksimum geçmiş sayısını kontrol et
        if len(self.query_history) > self.max_history:
            self.query_history = self.query_history[:self.max_history]

    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Sorgu geçmişini getir"""
        if limit:
            return self.query_history[:limit]
        return self.query_history

    def get_successful_queries(self, limit: Optional[int] = None) -> List[Dict]:
        """Sadece başarılı sorguları getir"""
        successful = [q for q in self.query_history if q['success']]
        if limit:
            return successful[:limit]
        return successful

    def get_failed_queries(self, limit: Optional[int] = None) -> List[Dict]:
        """Sadece başarısız sorguları getir"""
        failed = [q for q in self.query_history if not q['success']]
        if limit:
            return failed[:limit]
        return failed

    def clear_history(self):
        """Sorgu geçmişini temizle"""
        self.query_history.clear()

    def export_history(self, filepath: str) -> Tuple[bool, str]:
        """Sorgu geçmişini dosyaya kaydet"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("-- SQL Sorgu Geçmişi\n")
                f.write(f"-- Oluşturulma: {datetime.now()}\n")
                f.write(f"-- Toplam Sorgu: {len(self.query_history)}\n\n")

                for i, entry in enumerate(self.query_history, 1):
                    status = "✅ BAŞARILI" if entry['success'] else "❌ BAŞARISIZ"
                    f.write(f"-- [{i}] {status} | {entry['timestamp']} | DB: {entry['database']}\n")
                    f.write(f"-- Süre: {entry['execution_time']:.4f}s\n")

                    if entry['error']:
                        f.write(f"-- Hata: {entry['error']}\n")

                    f.write(f"{entry['query']}\n\n")

            return True, f"Geçmiş kaydedildi: {filepath}"

        except Exception as e:
            return False, f"Kaydetme hatası: {str(e)}"

    def get_query_statistics(self) -> Dict:
        """Sorgu istatistiklerini getir"""
        if not self.query_history:
            return {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'avg_execution_time': 0
            }

        successful = len([q for q in self.query_history if q['success']])
        failed = len([q for q in self.query_history if not q['success']])

        total_time = sum(q['execution_time'] for q in self.query_history if q['success'])
        avg_time = total_time / successful if successful > 0 else 0

        return {
            'total': len(self.query_history),
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / len(self.query_history)) * 100,
            'avg_execution_time': avg_time,
            'total_execution_time': total_time
        }

    def suggest_query(self, table_name: str, query_type: str = 'select') -> str:
        """Tablo için örnek sorgu öner"""
        suggestions = {
            'select': f"SELECT * FROM `{table_name}` LIMIT 10;",
            'count': f"SELECT COUNT(*) as toplam FROM `{table_name}`;",
            'structure': f"PRAGMA table_info(`{table_name}`);",
            'delete_all': f"DELETE FROM `{table_name}`;",
            'drop': f"DROP TABLE `{table_name}`;",
        }

        return suggestions.get(query_type, suggestions['select'])

    def format_query(self, query: str) -> str:
        """Sorguyu formatla (basit)"""
        # Basit SQL formatlama
        keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN',
                    'INNER JOIN', 'ORDER BY', 'GROUP BY', 'HAVING', 'LIMIT',
                    'INSERT INTO', 'UPDATE', 'DELETE FROM', 'CREATE TABLE', 'ALTER TABLE']

        formatted = query
        for keyword in keywords:
            formatted = formatted.replace(keyword, f'\n{keyword}')
            formatted = formatted.replace(keyword.lower(), f'\n{keyword}')

        # Gereksiz boşlukları temizle
        lines = [line.strip() for line in formatted.split('\n') if line.strip()]
        return '\n'.join(lines)