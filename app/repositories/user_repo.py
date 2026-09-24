from app.database import execute


class UserRepository:
    @staticmethod
    def by_username(username):
        rows = execute("SELECT * FROM users WHERE username=?", (username,))
        return rows[0] if isinstance(rows, (list, tuple)) and rows else None

    @staticmethod
    def by_id(id):
        rows = execute("SELECT * FROM users WHERE id=?", (id,))
        return rows[0] if isinstance(rows, (list, tuple)) and rows else None

    @staticmethod
    def all():
        return execute("""
            SELECT id, username, nama, role, telegram_chat_id, aktif, created_at
            FROM users ORDER BY id
        """)

    @staticmethod
    def create(data):
        return execute("""
            INSERT INTO users (username, password, nama, role, telegram_chat_id)
            VALUES (?, ?, ?, ?, ?)
        """, (data['username'], data['password'], data['nama'],
              data['role'], data.get('telegram_chat_id')), fetch=False)

    @staticmethod
    def update(id, data):
        sets = ', '.join([f"{k}=?" for k in data.keys()])
        execute(f"UPDATE users SET {sets} WHERE id=?",
                list(data.values()) + [id], fetch=False)

    @staticmethod
    def delete(id):
        execute("DELETE FROM users WHERE id=?", (id,), fetch=False)