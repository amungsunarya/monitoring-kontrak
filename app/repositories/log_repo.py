from app.database import execute


class LogRepository:
    @staticmethod
    def add(user_id, aksi, keterangan, ip=None):
        execute("""
            INSERT INTO log_aktivitas (user_id, aksi, keterangan, ip)
            VALUES (?, ?, ?, ?)
        """, (user_id, aksi, keterangan, ip), fetch=False)

    @staticmethod
    def recent(limit=500):
        return execute("""
            SELECT l.*, u.nama
            FROM log_aktivitas l
            LEFT JOIN users u ON u.id = l.user_id
            ORDER BY l.id DESC LIMIT ?
        """, (limit,))