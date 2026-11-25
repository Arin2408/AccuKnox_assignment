import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for folder in ("problem1_books", "problem2_scores", "problem3_csv"):
    sys.path.insert(0, str(ROOT / folder))
import books
import import_users
import scores


class Tests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.addCleanup(self.conn.close)

    def test_parse_books_handles_missing_fields(self):
        payload = {"docs": [{"key": "k1", "title": "T"}, {"title": "no key"}]}
        self.assertEqual(books.parse_books(payload), [("k1", "T", "Unknown", None)])

    def test_books_rerun_updates_without_duplicates(self):
        books.save_books(self.conn, [("k1", "Old", "A", 2000)])
        books.save_books(self.conn, [("k1", "New", "A", 2001)])
        self.assertEqual(self.conn.execute("SELECT title FROM books").fetchall(), [("New",)])

    def test_sql_injection_text_is_stored_as_data(self):
        evil = "x'); DROP TABLE books;--"
        books.save_books(self.conn, [("k1", evil, "A", None)])
        self.assertEqual(self.conn.execute("SELECT title FROM books").fetchone()[0], evil)

    def test_scores_are_validated(self):
        records = [{"name": "a", "score": s} for s in (50, 100, None, "9", -1, 101, True)]
        valid, rejected = scores.clean_scores(records)
        self.assertEqual((len(valid), len(rejected)), (2, 5))
        self.assertEqual(scores.average(valid), 75)

    def test_average_of_nothing_is_an_error(self):
        with self.assertRaises(ValueError):
            scores.average([])

    def test_csv_import_and_rerun(self):
        path = ROOT / "problem3_csv" / "users.csv"
        inserted, problems = import_users.import_users(self.conn, path)
        self.assertEqual((inserted, len(problems)), (3, 3))
        self.assertEqual(import_users.import_users(self.conn, path)[0], 0)

    def test_csv_missing_column(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.csv"
            path.write_text("name\nA\n")
            with self.assertRaises(ValueError):
                import_users.import_users(self.conn, path)


if __name__ == "__main__":
    unittest.main()
