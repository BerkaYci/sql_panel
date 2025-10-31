"""
CSV İşlem Modülü
CSV import/export ve dönüşüm işlemleri
"""

import pandas as pd
import csv
import os
from typing import List, Dict, Tuple, Optional


class CSVHandler:
    """CSV dosya işlemlerini yöneten sınıf"""

    @staticmethod
    def import_csv(file_path: str, encoding: str = 'utf-8',
                   delimiter: str = ',', preview_rows: Optional[int] = None) -> Tuple[bool, any]:
        """
        CSV dosyasını oku
        Returns: (başarılı_mı, DataFrame veya hata_mesajı)
        """
        try:
            if not os.path.exists(file_path):
                return False, "Dosya bulunamadı!"

            # Encoding hatalarını handle et
            try:
                df = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter,
                                 nrows=preview_rows)
            except UnicodeDecodeError:
                # UTF-8 başarısız olduysa latin1 dene
                df = pd.read_csv(file_path, encoding='latin1', delimiter=delimiter,
                                 nrows=preview_rows)

            return True, df

        except Exception as e:
            return False, f"CSV okuma hatası: {str(e)}"

    @staticmethod
    def detect_delimiter(file_path: str, sample_size: int = 10) -> str:
        """CSV delimiter'ını otomatik algıla"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sample = ''.join([f.readline() for _ in range(sample_size)])

            # csv.Sniffer kullanarak delimiter'ı tahmin et
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            return delimiter

        except Exception:
            # Varsayılan olarak virgül döndür
            return ','

    @staticmethod
    def detect_encoding(file_path: str) -> str:
        """Dosya encoding'ini algıla"""
        try:
            # Önce UTF-8 dene
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1000)
            return 'utf-8'
        except UnicodeDecodeError:
            # UTF-8 değilse latin1 dene
            try:
                with open(file_path, 'r', encoding='latin1') as f:
                    f.read(1000)
                return 'latin1'
            except:
                return 'cp1252'  # Windows default

    @staticmethod
    def export_to_csv(data: List[List], columns: List[str], file_path: str,
                      encoding: str = 'utf-8', delimiter: str = ',') -> Tuple[bool, str]:
        """Veriyi CSV'ye aktar"""
        try:
            df = pd.DataFrame(data, columns=columns)
            df.to_csv(file_path, index=False, encoding=encoding, sep=delimiter)

            return True, f"CSV'ye aktarıldı: {os.path.basename(file_path)}"

        except Exception as e:
            return False, f"CSV export hatası: {str(e)}"

    @staticmethod
    def get_csv_info(file_path: str) -> Dict:
        """CSV dosyası hakkında bilgi al"""
        try:
            # Encoding'i algıla
            encoding = CSVHandler.detect_encoding(file_path)
            delimiter = CSVHandler.detect_delimiter(file_path)

            # İlk 5 satırı oku
            df_sample = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter, nrows=5)

            # Tüm satır sayısı için hızlı sayım
            with open(file_path, 'r', encoding=encoding) as f:
                row_count = sum(1 for _ in f) - 1  # Header hariç

            info = {
                'file_name': os.path.basename(file_path),
                'file_size': os.path.getsize(file_path),
                'encoding': encoding,
                'delimiter': delimiter,
                'row_count': row_count,
                'column_count': len(df_sample.columns),
                'columns': list(df_sample.columns),
                'sample_data': df_sample.to_dict('records')
            }

            return info

        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def validate_csv_file(file_path: str) -> Tuple[bool, str]:
        """CSV dosyasını doğrula"""
        if not os.path.exists(file_path):
            return False, "Dosya bulunamadı!"

        if not file_path.lower().endswith(('.csv', '.txt')):
            return False, "Geçersiz CSV dosyası!"

        try:
            # İlk satırı okumayı dene
            encoding = CSVHandler.detect_encoding(file_path)
            pd.read_csv(file_path, encoding=encoding, nrows=1)
            return True, "Geçerli CSV dosyası"
        except Exception as e:
            return False, f"CSV dosyası hatalı: {str(e)}"

    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """DataFrame'i temizle"""
        # Boş satırları kaldır
        df = df.dropna(how='all')

        # Sütun isimlerindeki boşlukları temizle
        df.columns = df.columns.str.strip()

        # String sütunlardaki boşlukları temizle
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].str.strip()

        return df

    @staticmethod
    def dataframe_to_sql_create(df: pd.DataFrame, table_name: str) -> str:
        """DataFrame'den CREATE TABLE query'si oluştur"""
        columns_def = []

        for col in df.columns:
            # Pandas dtype'ına göre SQL type belirle
            dtype = df[col].dtype

            if dtype == 'int64':
                sql_type = 'INTEGER'
            elif dtype == 'float64':
                sql_type = 'REAL'
            elif dtype == 'bool':
                sql_type = 'BOOLEAN'
            elif dtype == 'datetime64[ns]':
                sql_type = 'DATETIME'
            else:
                sql_type = 'TEXT'

            columns_def.append(f'`{col}` {sql_type}')

        columns_str = ',\n    '.join(columns_def)
        query = f"CREATE TABLE `{table_name}` (\n    {columns_str}\n);"

        return query

    @staticmethod
    def convert_csv_to_sql(csv_path: str, table_name: str) -> Tuple[bool, List[str]]:
        """CSV'yi SQL komutlarına çevir"""
        try:
            # CSV'yi oku
            encoding = CSVHandler.detect_encoding(csv_path)
            delimiter = CSVHandler.detect_delimiter(csv_path)
            df = pd.read_csv(csv_path, encoding=encoding, delimiter=delimiter)

            # Temizle
            df = CSVHandler.clean_dataframe(df)

            queries = []

            # CREATE TABLE
            create_query = CSVHandler.dataframe_to_sql_create(df, table_name)
            queries.append(create_query)

            # INSERT statements
            columns = ', '.join([f'`{col}`' for col in df.columns])

            for _, row in df.iterrows():
                values = []
                for val in row:
                    if pd.isna(val):
                        values.append('NULL')
                    elif isinstance(val, str):
                        val_escaped = val.replace("'", "''")
                        values.append(f"'{val_escaped}'")
                    else:
                        values.append(str(val))

                values_str = ', '.join(values)
                query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({values_str});"
                queries.append(query)

            return True, queries

        except Exception as e:
            return False, [f"-- Hata: {str(e)}"]