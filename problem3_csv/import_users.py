"""Import users (name, email) from CSV into SQLite.

Usage: python problem3_csv/import_users.py [csv_path] [--db users.db]
"""
import argparse
import csv
import re
import sqlite3
from pathlib import Path

HERE = Path(__file__).parent
# Basic shape check only; only a confirmation email proves an address works.
EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def read_users(csv_path):
    """Yield (line_number, name, email), with whitespace/case normalised."""
    # utf-8-sig also strips the byte-order mark Excel may add.
    with open(csv_path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        missing = {"name", "email"} - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing column(s): {sorted(missing)}")
        for row in reader:
            yield (reader.line_num, (row["name"] or "").strip(),
                   (row["email"] or "").strip().lower())


def import_users(conn, csv_path):
    """Return (inserted_count, [problem messages])."""
    inserted, problems = 0, []
    with conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS users (
                   id INTEGER PRIMARY KEY,
                   name TEXT NOT NULL,
                   email TEXT NOT NULL UNIQUE
               )"""
        )
        for line, name, email in read_users(csv_path):
            if not name or not EMAIL_RE.fullmatch(email):
                problems.append(f"line {line}: invalid name or email")
                continue
            cursor = conn.execute(
                """INSERT INTO users (name, email) VALUES (?, ?)
                   ON CONFLICT(email) DO NOTHING""",
                (name, email),
            )
            if cursor.rowcount:
                inserted += 1
            else:
                problems.append(f"line {line}: email already exists")
    return inserted, problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", nargs="?", default=HERE / "users.csv")
    parser.add_argument("--db", default=HERE / "users.db")
    args = parser.parse_args()
    conn = sqlite3.connect(args.db)
    try:
        inserted, problems = import_users(conn, args.csv_path)
        for problem in problems:
            print(f"Skipped {problem}")
        print(f"Inserted {inserted}, skipped {len(problems)}")
        for row in conn.execute("SELECT id, name, email FROM users"):
            print(row)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Error: {exc}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
