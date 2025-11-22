import os
import tempfile
import unittest

from core.database_manager import DatabaseManager
from core.query_executor import QueryExecutor


class DatabaseManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        self.manager = DatabaseManager()

    def tearDown(self):
        self.manager.close_all()
        self.temp_dir.cleanup()

    def test_create_database_registers_alias(self):
        success, _ = self.manager.create_database(self.db_path, "main_db")
        self.assertTrue(success, "Veritabanı oluşturulamadı")
        self.assertTrue(os.path.exists(self.db_path))

        db_list = self.manager.get_database_list()
        self.assertIn("main_db", db_list)

        db_info = self.manager.get_database_info("main_db")
        self.assertIsNotNone(db_info)
        self.assertEqual(db_info["alias"], "main_db")
        self.assertIn("table_count", db_info)

    def test_get_all_database_info_includes_alias(self):
        self.manager.create_database(self.db_path, "info_db")
        infos = self.manager.get_all_database_info()
        self.assertTrue(any(info["alias"] == "info_db" for info in infos))


class QueryExecutorTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "exec.db")
        self.manager = DatabaseManager()
        self.manager.create_database(self.db_path, "exec_db")
        self.executor = QueryExecutor(self.manager)

    def tearDown(self):
        self.manager.close_all()
        self.temp_dir.cleanup()

    def test_execute_select_and_modify_queries(self):
        create_success, _, _ = self.executor.execute(
            "CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)"
        )
        self.assertTrue(create_success, "Tablo oluşturulamadı")

        insert_success, modify_result, _ = self.executor.execute(
            "INSERT INTO items (name) VALUES ('widget')"
        )
        self.assertTrue(insert_success)
        self.assertEqual(modify_result["type"], "modify")
        self.assertEqual(modify_result["affected_rows"], 1)

        select_success, select_result, _ = self.executor.execute(
            "SELECT * FROM items"
        )
        self.assertTrue(select_success)
        self.assertEqual(select_result["type"], "select")
        self.assertEqual(select_result["row_count"], 1)
        self.assertEqual(select_result["rows"][0][1], "widget")
        self.assertEqual(select_result["columns"], ["id", "name"])


if __name__ == "__main__":
    unittest.main()
