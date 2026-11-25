"""Fetch books from the Open Library REST API, store in SQLite, display them.

Usage: python problem1_books/books.py [--subject python] [--limit 10]
"""
import argparse
import sqlite3
from pathlib import Path

import requests

API_URL = "https://openlibrary.org/search.json"
DEFAULT_DB = Path(__file__).with_name("books.db")


def fetch_books(subject, limit):
    response = requests.get(
        API_URL,
        params={
            "q": f"subject:{subject}",
            "fields": "key,title,author_name,first_publish_year",
            "limit": limit,
        },
        timeout=30,
    )
    response.raise_for_status()  # turn 4xx/5xx into an exception
    return parse_books(response.json())


def parse_books(payload):
    """Flatten API records; skip those without an id or title."""
    books = []
    for doc in payload.get("docs", []):
        if not doc.get("key") or not doc.get("title"):
            continue
        authors = ", ".join(doc.get("author_name") or ["Unknown"])
        books.append((doc["key"], doc["title"], authors, doc.get("first_publish_year")))
    return books


def save_books(conn, books):
    with conn:  # one transaction: commit all rows or roll back
        conn.execute(
            """CREATE TABLE IF NOT EXISTS books (
                   id TEXT PRIMARY KEY,
                   title TEXT NOT NULL,
                   author TEXT NOT NULL,
                   publication_year INTEGER
               )"""
        )
        # Upsert: a re-run refreshes rows rather than duplicating them.
        conn.executemany(
            """INSERT INTO books VALUES (?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET
                   title = excluded.title,
                   author = excluded.author,
                   publication_year = excluded.publication_year""",
            books,
        )


def display_books(conn):
    rows = conn.execute(
        "SELECT title, author, publication_year FROM books ORDER BY title"
    ).fetchall()
    print(f"{'Title':<45} {'Author':<35} Year")
    print("-" * 86)
    for title, author, year in rows:
        print(f"{title[:44]:<45} {author[:34]:<35} {year or 'n/a'}")
    print(f"{len(rows)} book(s) stored")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", default="python")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--db", default=DEFAULT_DB)
    args = parser.parse_args()
    conn = sqlite3.connect(args.db)
    try:
        save_books(conn, fetch_books(args.subject, args.limit))
        display_books(conn)
    except requests.RequestException as exc:
        raise SystemExit(f"API request failed: {exc}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
