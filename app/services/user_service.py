from app.repositories.user_repo import UserRepository
from app.repositories.log_repo import LogRepository
from app.extensions import bcrypt


class UserService:
    @staticmethod
    def semua():
        return UserRepository.all()

    @staticmethod
    def buat(form, actor_id=None):
        username = form['username'].strip()
        if not username:
            raise ValueError('Username wajib diisi')
        if UserRepository.by_username(username):
            raise ValueError('Username sudah dipakai')
        if not form.get('password'):
            raise ValueError('Password wajib diisi')
        data = {
            'username': username,
            'password': bcrypt.generate_password_hash(form['password']).decode(),
            'nama': form['nama'],
            'role': form.get('role', 'user'),
            'telegram_chat_id': form.get('telegram') or None,
        }
        UserRepository.create(data)
        LogRepository.add(actor_id, 'ADD_USER', f"Tambah user: {username}")

    @staticmethod
    def update(id, form, actor_id=None):
        data = {
            'username': form['username'].strip(),
            'nama': form['nama'],
            'role': form.get('role', 'user'),
            'telegram_chat_id': form.get('telegram') or None,
            'aktif': 1 if form.get('aktif') else 0,
        }
        if form.get('password'):
            data['password'] = bcrypt.generate_password_hash(form['password']).decode()
        UserRepository.update(id, data)
        LogRepository.add(actor_id, 'EDIT_USER', f"Edit user ID {id}")

    @staticmethod
    def hapus(id, actor_id=None):
        UserRepository.delete(id)
        LogRepository.add(actor_id, 'DELETE_USER', f"Hapus user ID {id}")