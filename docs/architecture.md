# Arsitektur Aplikasi

## Stack
- **Backend**: Flask 3.0
- **Database**: SQLite (file lokal `instance/kontrak.db`)
- **Frontend**: Bootstrap 5 + Chart.js + ApexCharts + Frappe Gantt
- **Scheduler**: APScheduler
- **Sync**: Google Sheets API
- **Deploy**: Docker + Gunicorn

## Layer
routes → services → repositories → database.py → SQLite

## Kenapa SQLite?
- Tidak perlu install server DB
- Tidak perlu buka port
- Backup = copy 1 file
- Cocok untuk internal, < 50 user
- Jalan di mana saja (Windows/Linux/Docker)

## Fitur
- Login & role-based
- CRUD Kontrak (18 kolom)
- CRUD User
- Dashboard 7 chart
- Sync Google Sheets
- Reminder Telegram
- Export Excel
- Log aktivitas
- PWA