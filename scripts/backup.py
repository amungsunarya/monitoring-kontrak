"""
Backup SQLite database.
Usage: python scripts/backup.py
Output: backups/kontrak_YYYYMMDD_HHMMSS.db
"""
import os
import shutil
from datetime import datetime

DB_PATH = 'instance/kontrak.db'
BACKUP_DIR = 'backups'


def backup():
    if not os.path.exists(DB_PATH):
        print(f'Database tidak ditemukan: {DB_PATH}')
        return

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f'kontrak_{timestamp}.db')

    shutil.copy2(DB_PATH, backup_file)
    size_kb = os.path.getsize(backup_file) / 1024
    print(f'Backup berhasil: {backup_file} ({size_kb:.1f} KB)')


if __name__ == '__main__':
    backup()