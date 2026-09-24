"""
Migration runner untuk SQLite.
Usage:
    python scripts/migrate.py status
    python scripts/migrate.py up
"""
import sys
import os
import glob
import sqlite3

DB_PATH = 'instance/kontrak.db'


def ensure_migration_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


def get_applied(conn):
    cur = conn.execute("SELECT filename FROM _migrations ORDER BY id")
    return {r[0] for r in cur.fetchall()}


def list_migrations():
    return sorted(glob.glob('migrations/*.sql'))


def status():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    ensure_migration_table(conn)
    applied = get_applied(conn)
    print("Migration Status:")
    print("-" * 50)
    for f in list_migrations():
        name = os.path.basename(f)
        mark = '[OK]' if name in applied else '[  ]'
        print(f"{mark}  {name}")
    conn.close()


def up():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    ensure_migration_table(conn)
    applied = get_applied(conn)

    for f in list_migrations():
        name = os.path.basename(f)
        if name in applied:
            print(f"Skip (already applied): {name}")
            continue
        print(f"Applying: {name}")
        with open(f, 'r', encoding='utf-8') as fh:
            sql = fh.read()
        try:
            conn.executescript(sql)
            conn.execute("INSERT INTO _migrations (filename) VALUES (?)", (name,))
            conn.commit()
            print(f"  Applied {name}")
        except sqlite3.Error as e:
            print(f"  Error: {e}")
    conn.close()


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if cmd == 'status':
        status()
    elif cmd == 'up':
        up()
    else:
        print(f"Perintah tidak dikenal: {cmd}")
        sys.exit(1)