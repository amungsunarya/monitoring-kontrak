from app.repositories.user_repo import UserRepository
from app.repositories.log_repo import LogRepository
from app.extensions import bcrypt


class AuthService:
    @staticmethod
    def login(username, password, ip=None):
        user = UserRepository.by_username(username)
        if not user or not user['aktif']:
            return None
        if not bcrypt.check_password_hash(user['password'], password):
            return None
        LogRepository.add(user['id'], 'LOGIN', 'Login sukses', ip)
        return user