"""
Base repository — helper untuk query umum.
Repo lain bisa inherit atau pakai langsung.
"""
from app.database import execute


class BaseRepository:
    table = None  # override di subclass

    @classmethod
    def all(cls, order_by='id DESC'):
        return execute(f"SELECT * FROM {cls.table} ORDER BY {order_by}")

    @classmethod
    def by_id(cls, id):
        rows = execute(f"SELECT * FROM {cls.table} WHERE id=?", (id,))
        return rows[0] if isinstance(rows, (list, tuple)) and rows else None

    @classmethod
    def count(cls):
        r = execute(f"SELECT COUNT(*) AS c FROM {cls.table}")[0] # type: ignore
        return r['c']

    @classmethod
    def create(cls, data):
        cols = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        sql = f"INSERT INTO {cls.table} ({cols}) VALUES ({placeholders})"
        return execute(sql, list(data.values()), fetch=False)

    @classmethod
    def update(cls, id, data):
        sets = ', '.join([f"{k}=?" for k in data.keys()])
        sql = f"UPDATE {cls.table} SET {sets} WHERE id=?"
        execute(sql, list(data.values()) + [id], fetch=False)

    @classmethod
    def delete(cls, id):
        execute(f"DELETE FROM {cls.table} WHERE id=?", (id,), fetch=False)