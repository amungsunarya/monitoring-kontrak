import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)


class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me')
    APP_NAME = os.getenv('APP_NAME', 'Monitoring Kontrak')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # SQLite
    DB_PATH = os.path.join(PROJECT_ROOT, os.getenv('DB_PATH', 'instance/kontrak.db'))

    # Google Sheets
    GSHEET_ID = os.getenv('GSHEET_ID', '')
    GSHEET_NAME = os.getenv('GSHEET_NAME', 'Kontrak')
    GSHEET_CREDENTIALS = os.getenv('GSHEET_CREDENTIALS', 'credentials.json')

    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_ADMIN_CHAT = os.getenv('TELEGRAM_ADMIN_CHAT', '')

    REMINDER_DAYS = [int(x) for x in os.getenv('REMINDER_DAYS', '30,14,7,3,1').split(',')]

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600 * 8


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV = 'development'


class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV = 'production'
    SESSION_COOKIE_SECURE = False


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    DB_PATH = ':memory:'


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}