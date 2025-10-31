"""
Kaydedilmiş Sorgu Yöneticisi
Kullanıcının kendi sorgularını kaydetme ve yönetme
"""

import json
import os
from typing import List, Dict, Tuple, Optional
from datetime import datetime


class SavedQueriesManager:
    """Kaydedilmiş sorguları yöneten sınıf"""

    def __init__(self, storage_file: str = "saved_queries.json"):
        self.storage_file = storage_file
        self.queries: List[Dict] = []
        self.load_queries()

    def load_queries(self) -> bool:
        """Kaydedilmiş sorguları yükle"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self.queries = json.load(f)
                return True
            else:
                self.queries = []
                return True
        except Exception as e:
            print(f"Sorgu yükleme hatası: {e}")
            self.queries = []
            return False

    def save_queries(self) -> bool:
        """Sorguları dosyaya kaydet"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.queries, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Sorgu kaydetme hatası: {e}")
            return False

    def add_query(self, name: str, query: str, description: str = "",
                  category: str = "Genel") -> Tuple[bool, str]:
        """Yeni sorgu ekle"""
        # İsim kontrolü
        if not name or not name.strip():
            return False, "Sorgu adı boş olamaz!"

        if not query or not query.strip():
            return False, "Sorgu metni boş olamaz!"

        # Aynı isimde sorgu var mı?
        if any(q['name'] == name for q in self.queries):
            return False, f"'{name}' adında bir sorgu zaten var!"

        # Yeni sorgu oluştur
        new_query = {
            'id': self._generate_id(),
            'name': name.strip(),
            'query': query.strip(),
            'description': description.strip(),
            'category': category.strip(),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'usage_count': 0,
            'last_used': None
        }

        self.queries.append(new_query)
        self.save_queries()

        return True, f"'{name}' sorgusu kaydedildi!"

    def update_query(self, query_id: str, name: Optional[str] = None,
                     query: Optional[str] = None, description: Optional[str] = None,
                     category: Optional[str] = None) -> Tuple[bool, str]:
        """Sorgu güncelle"""
        for q in self.queries:
            if q['id'] == query_id:
                if name is not None:
                    # Başka bir sorguda aynı isim var mı kontrol et
                    if any(sq['name'] == name and sq['id'] != query_id for sq in self.queries):
                        return False, f"'{name}' adında başka bir sorgu var!"
                    q['name'] = name.strip()

                if query is not None:
                    q['query'] = query.strip()

                if description is not None:
                    q['description'] = description.strip()

                if category is not None:
                    q['category'] = category.strip()

                q['updated_at'] = datetime.now().isoformat()
                self.save_queries()

                return True, f"'{q['name']}' güncellendi!"

        return False, "Sorgu bulunamadı!"

    def delete_query(self, query_id: str) -> Tuple[bool, str]:
        """Sorgu sil"""
        for i, q in enumerate(self.queries):
            if q['id'] == query_id:
                name = q['name']
                del self.queries[i]
                self.save_queries()
                return True, f"'{name}' silindi!"

        return False, "Sorgu bulunamadı!"

    def get_query(self, query_id: str) -> Optional[Dict]:
        """ID'ye göre sorgu getir"""
        for q in self.queries:
            if q['id'] == query_id:
                return q
        return None

    def get_query_by_name(self, name: str) -> Optional[Dict]:
        """İsme göre sorgu getir"""
        for q in self.queries:
            if q['name'] == name:
                return q
        return None

    def get_all_queries(self) -> List[Dict]:
        """Tüm sorguları getir"""
        return self.queries.copy()

    def get_queries_by_category(self, category: str) -> List[Dict]:
        """Kategoriye göre sorguları getir"""
        return [q for q in self.queries if q['category'] == category]

    def get_categories(self) -> List[str]:
        """Tüm kategorileri getir"""
        categories = set(q['category'] for q in self.queries)
        return sorted(list(categories))

    def search_queries(self, keyword: str) -> List[Dict]:
        """Sorgu ara (isim, açıklama, sorgu metninde)"""
        keyword_lower = keyword.lower()
        results = []

        for q in self.queries:
            if (keyword_lower in q['name'].lower() or
                    keyword_lower in q['description'].lower() or
                    keyword_lower in q['query'].lower()):
                results.append(q)

        return results

    def increment_usage(self, query_id: str):
        """Sorgu kullanım sayısını artır"""
        for q in self.queries:
            if q['id'] == query_id:
                q['usage_count'] += 1
                q['last_used'] = datetime.now().isoformat()
                self.save_queries()
                break

    def get_most_used(self, limit: int = 10) -> List[Dict]:
        """En çok kullanılan sorguları getir"""
        sorted_queries = sorted(self.queries, key=lambda x: x['usage_count'], reverse=True)
        return sorted_queries[:limit]

    def get_recently_used(self, limit: int = 10) -> List[Dict]:
        """Son kullanılan sorguları getir"""
        used_queries = [q for q in self.queries if q['last_used']]
        sorted_queries = sorted(used_queries, key=lambda x: x['last_used'], reverse=True)
        return sorted_queries[:limit]

    def export_queries(self, filepath: str, category: Optional[str] = None) -> Tuple[bool, str]:
        """Sorguları dışa aktar"""
        try:
            if category:
                queries_to_export = self.get_queries_by_category(category)
            else:
                queries_to_export = self.queries

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(queries_to_export, f, indent=2, ensure_ascii=False)

            return True, f"{len(queries_to_export)} sorgu dışa aktarıldı!"
        except Exception as e:
            return False, f"Dışa aktarma hatası: {str(e)}"

    def import_queries(self, filepath: str, merge: bool = True) -> Tuple[bool, str]:
        """Sorguları içe aktar"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_queries = json.load(f)

            if not merge:
                self.queries = imported_queries
            else:
                # Mevcut sorguları koruyarak ekle
                imported_count = 0
                skipped_count = 0

                for q in imported_queries:
                    # Aynı isimde sorgu var mı?
                    if not any(sq['name'] == q['name'] for sq in self.queries):
                        # Yeni ID oluştur
                        q['id'] = self._generate_id()
                        self.queries.append(q)
                        imported_count += 1
                    else:
                        skipped_count += 1

                message = f"{imported_count} sorgu içe aktarıldı!"
                if skipped_count > 0:
                    message += f" ({skipped_count} sorgu atlandı - aynı isimde)"

            self.save_queries()
            return True, message

        except Exception as e:
            return False, f"İçe aktarma hatası: {str(e)}"

    def _generate_id(self) -> str:
        """Benzersiz ID oluştur"""
        import uuid
        return str(uuid.uuid4())[:8]

    def get_statistics(self) -> Dict:
        """İstatistikler"""
        if not self.queries:
            return {
                'total': 0,
                'categories': 0,
                'total_usage': 0,
                'most_used': None
            }

        most_used = max(self.queries, key=lambda x: x['usage_count'])

        return {
            'total': len(self.queries),
            'categories': len(self.get_categories()),
            'total_usage': sum(q['usage_count'] for q in self.queries),
            'most_used': most_used['name'] if most_used['usage_count'] > 0 else None
        }