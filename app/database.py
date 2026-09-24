"""
SQLite database helper.
Menggunakan modul sqlite3 built-in Python.
File database: instance/kontrak.db
"""
import sqlite3
import os
from flask import g, current_app


def get_db():
    """Ambil koneksi DB. Reuse per request via flask.g."""
    if 'db' not in g:
        db_path = current_app.config['DB_PATH']

        if db_path != ':memory:':
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            timeout=10,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
        g.db.execute('PRAGMA journal_mode = WAL')
    return g.db


def close_db(e=None):
    """Tutup koneksi DB di akhir request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def execute(query, params=None, fetch=True):
    """
    Helper eksekusi query.
    - fetch=True  -> SELECT, return list of dict
    - fetch=False -> INSERT/UPDATE/DELETE, return lastrowid / rowcount
    """
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute(query, params or ())
        if fetch:
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        else:
            db.commit()
            return cur.lastrowid if cur.lastrowid else cur.rowcount
    except sqlite3.Error as e:
        db.rollback()
        try:
            current_app.logger.error(f"Query error: {e} | SQL: {query[:150]}")
        except Exception:
            print(f"Query error: {e}")
        raise
    finally:
        cur.close()


def init_app(app):
    """Register close_db ke app teardown."""
    app.teardown_appcontext(close_db)