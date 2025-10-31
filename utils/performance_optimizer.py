"""
Performans Optimizasyon Modülü
Büyük veri setleri için pagination, lazy loading ve caching
"""

import sqlite3
from typing import List, Dict, Tuple, Optional, Any
from threading import Thread, Lock
import time


class DataPaginator:
    """Veri sayfalama ve cache yönetimi"""

    def __init__(self, page_size: int = 100):
        self.page_size = page_size
        self.current_page = 0
        self.total_rows = 0
        self.total_pages = 0
        self.cache = {}
        self.cache_lock = Lock()
        self.max_cache_pages = 10  # Maksimum 10 sayfa cache'le

    def set_total_rows(self, total: int):
        """Toplam satır sayısını ayarla"""
        self.total_rows = total
        self.total_pages = (total + self.page_size - 1) // self.page_size

    def get_page_data(self, conn: sqlite3.Connection, table_name: str,
                     page: int, columns: Optional[List[str]] = None) -> Tuple[List, int]:
        """Belirli bir sayfanın verilerini getir (cache'li)"""

        # Cache kontrolü
        cache_key = f"{table_name}_{page}"
        with self.cache_lock:
            if cache_key in self.cache:
                return self.cache[cache_key], page

        # Veritabanından çek
        offset = page * self.page_size

        if columns:
            cols = ', '.join([f'`{col}`' for col in columns])
            query = f"SELECT rowid, {cols} FROM `{table_name}` LIMIT ? OFFSET ?"
        else:
            query = f"SELECT rowid, * FROM `{table_name}` LIMIT ? OFFSET ?"

        cursor = conn.cursor()
        cursor.execute(query, (self.page_size, offset))
        data = cursor.fetchall()

        # Cache'e ekle
        with self.cache_lock:
            # Cache boyutu kontrolü
            if len(self.cache) >= self.max_cache_pages:
                # En eski sayfayı çıkar (FIFO)
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]

            self.cache[cache_key] = data

        return data, page

    def prefetch_next_page(self, conn: sqlite3.Connection, table_name: str,
                          current_page: int, columns: Optional[List[str]] = None):
        """Sonraki sayfayı arka planda önceden yükle"""
        next_page = current_page + 1
        if next_page < self.total_pages:
            cache_key = f"{table_name}_{next_page}"
            with self.cache_lock:
                if cache_key not in self.cache:
                    # Arka planda yükle
                    Thread(target=self.get_page_data,
                          args=(conn, table_name, next_page, columns),
                          daemon=True).start()

    def clear_cache(self):
        """Cache'i temizle"""
        with self.cache_lock:
            self.cache.clear()

    def get_page_info(self) -> Dict:
        """Sayfa bilgilerini getir"""
        return {
            'current_page': self.current_page,
            'total_pages': self.total_pages,
            'page_size': self.page_size,
            'total_rows': self.total_rows,
            'start_row': self.current_page * self.page_size + 1,
            'end_row': min((self.current_page + 1) * self.page_size, self.total_rows)
        }


class VirtualScrollManager:
    """Virtual scrolling için yönetici (LazyLoading)"""

    def __init__(self, total_rows: int, visible_rows: int = 20):
        self.total_rows = total_rows
        self.visible_rows = visible_rows
        self.current_top = 0
        self.buffer_size = visible_rows * 2  # Yukarı ve aşağı buffer

    def get_visible_range(self, scroll_position: float) -> Tuple[int, int]:
        """Görünür satır aralığını hesapla"""
        # scroll_position: 0.0 - 1.0 arası
        self.current_top = int(scroll_position * max(0, self.total_rows - self.visible_rows))

        start = max(0, self.current_top - self.visible_rows)
        end = min(self.total_rows, self.current_top + self.buffer_size)

        return start, end

    def needs_update(self, new_position: float, threshold: float = 0.1) -> bool:
        """Scroll pozisyonu güncelleme gerektiriyor mu?"""
        new_top = int(new_position * max(0, self.total_rows - self.visible_rows))
        return abs(new_top - self.current_top) > (self.visible_rows * threshold)


class QueryOptimizer:
    """SQL sorgu optimizasyonu"""

    @staticmethod
    def add_limit_if_missing(query: str, limit: int = 1000) -> Tuple[str, bool]:
        """Sorguya LIMIT ekle (yoksa)"""
        query_upper = query.upper().strip()

        # Zaten LIMIT var mı?
        if 'LIMIT' in query_upper:
            return query, False

        # SELECT sorgusu mu?
        if query_upper.startswith('SELECT'):
            # Noktalı virgül varsa önüne ekle
            if query.rstrip().endswith(';'):
                optimized = query.rstrip()[:-1] + f' LIMIT {limit};'
            else:
                optimized = query + f' LIMIT {limit}'
            return optimized, True

        return query, False

    @staticmethod
    def estimate_result_size(conn: sqlite3.Connection, query: str) -> Optional[int]:
        """Sorgu sonuç boyutunu tahmin et (EXPLAIN QUERY PLAN)"""
        try:
            # COUNT(*) ile tahmin
            if 'SELECT' in query.upper():
                # SELECT'i COUNT'a çevir
                count_query = query.upper().replace('SELECT', 'SELECT COUNT(*) FROM (SELECT', 1)
                count_query = count_query.rstrip(';') + ') AS count_table;'

                cursor = conn.cursor()
                cursor.execute(count_query)
                result = cursor.fetchone()
                return result[0] if result else None
        except:
            return None

    @staticmethod
    def suggest_indexes(conn: sqlite3.Connection, table_name: str) -> List[str]:
        """Index önerileri"""
        suggestions = []

        try:
            cursor = conn.cursor()

            # Mevcut indexleri al
            cursor.execute(f"PRAGMA index_list(`{table_name}`)")
            existing_indexes = {row[1] for row in cursor.fetchall()}

            # Tablo yapısını al
            cursor.execute(f"PRAGMA table_info(`{table_name}`)")
            columns = cursor.fetchall()

            # Foreign key ve sık kullanılan sütunlar için index öner
            for col in columns:
                col_name = col[1]
                col_type = col[2]

                # Zaten index varsa atla
                index_name = f"idx_{table_name}_{col_name}"
                if index_name in existing_indexes:
                    continue

                # Numeric ve text sütunlar için öner
                if col_type.upper() in ['INTEGER', 'TEXT', 'VARCHAR', 'CHAR']:
                    suggestions.append(
                        f"CREATE INDEX {index_name} ON `{table_name}`(`{col_name}`);"
                    )

        except Exception:
            pass

        return suggestions


class ProgressiveLoader:
    """Aşamalı veri yükleme"""

    def __init__(self, chunk_size: int = 50):
        self.chunk_size = chunk_size
        self.loaded_chunks = set()
        self.loading = False

    def load_chunk(self, conn: sqlite3.Connection, table_name: str,
                  chunk_index: int, columns: Optional[List[str]] = None,
                  callback=None) -> List:
        """Bir chunk (parça) yükle"""

        if chunk_index in self.loaded_chunks:
            return []

        offset = chunk_index * self.chunk_size

        if columns:
            cols = ', '.join([f'`{col}`' for col in columns])
            query = f"SELECT rowid, {cols} FROM `{table_name}` LIMIT ? OFFSET ?"
        else:
            query = f"SELECT rowid, * FROM `{table_name}` LIMIT ? OFFSET ?"

        cursor = conn.cursor()
        cursor.execute(query, (self.chunk_size, offset))
        data = cursor.fetchall()

        self.loaded_chunks.add(chunk_index)

        if callback:
            callback(data, chunk_index)

        return data

    def reset(self):
        """Yüklenmiş chunk'ları sıfırla"""
        self.loaded_chunks.clear()


class PerformanceMonitor:
    """Performans izleme"""

    def __init__(self):
        self.metrics = {
            'query_times': [],
            'load_times': [],
            'render_times': []
        }
        self.start_time = None

    def start_timer(self):
        """Zamanlayıcı başlat"""
        self.start_time = time.time()

    def stop_timer(self, operation: str) -> float:
        """Zamanlayıcı durdur ve kaydet"""
        if self.start_time is None:
            return 0.0

        elapsed = time.time() - self.start_time

        if operation in self.metrics:
            self.metrics[operation].append(elapsed)

        self.start_time = None
        return elapsed

    def get_average(self, operation: str) -> float:
        """Ortalama süre"""
        if operation in self.metrics and self.metrics[operation]:
            return sum(self.metrics[operation]) / len(self.metrics[operation])
        return 0.0

    def get_stats(self) -> Dict:
        """İstatistikleri getir"""
        stats = {}
        for op, times in self.metrics.items():
            if times:
                stats[op] = {
                    'avg': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times),
                    'count': len(times)
                }
        return stats

    def reset(self):
        """Metrikleri sıfırla"""
        for key in self.metrics:
            self.metrics[key].clear()


class SmartCache:
    """Akıllı veri önbellekleme"""

    def __init__(self, max_size_mb: int = 100):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache = {}
        self.access_count = {}
        self.cache_lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        """Cache'den veri al"""
        with self.cache_lock:
            if key in self.cache:
                self.access_count[key] = self.access_count.get(key, 0) + 1
                return self.cache[key]
        return None

    def set(self, key: str, value: Any):
        """Cache'e veri ekle"""
        with self.cache_lock:
            # Boyut kontrolü (basit tahmin)
            estimated_size = len(str(value))

            # Cache doluysa en az kullanılanı çıkar
            while len(self.cache) > 0:
                current_size = sum(len(str(v)) for v in self.cache.values())
                if current_size + estimated_size <= self.max_size_bytes:
                    break

                # En az kullanılanı bul
                lfu_key = min(self.access_count, key=self.access_count.get)
                del self.cache[lfu_key]
                del self.access_count[lfu_key]

            self.cache[key] = value
            self.access_count[key] = 0

    def clear(self):
        """Cache'i temizle"""
        with self.cache_lock:
            self.cache.clear()
            self.access_count.clear()

    def get_stats(self) -> Dict:
        """Cache istatistikleri"""
        with self.cache_lock:
            total_size = sum(len(str(v)) for v in self.cache.values())
            return {
                'items': len(self.cache),
                'size_mb': total_size / (1024 * 1024),
                'max_size_mb': self.max_size_bytes / (1024 * 1024),
                'usage_percent': (total_size / self.max_size_bytes) * 100
            }