# Monitoring Kontrak

Aplikasi monitoring kontrak berbasis Flask + SQLite + Google Sheets sync.

## Quick Start

1. `pip install -r requirements.txt`
2. `flask init-db`
3. `flask create-admin`
4. `python run.py`
5. Buka `http://localhost:8001`

## Backup

`python scripts/backup.py` → hasil di `backups/`

## Fitur

- Login & role-based
- CRUD Kontrak (18 kolom)
- CRUD User
- Dashboard 7 chart (Pie, Bar, Line, Gantt, S-Curve, Heatmap, Gauge)
- Sync ke Google Sheets
- Reminder Telegram
- Export Excel
- Log aktivitas