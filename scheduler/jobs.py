import requests
import logging
from datetime import datetime, timedelta, date
from typing import Any, cast
from flask import current_app
from app.database import execute


def _to_date(v):
    """Konversi value SQLite (str/datetime) ke date."""
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    if isinstance(v, str):
        try:
            return date.fromisoformat(v[:10])
        except ValueError:
            return None
    return None


def send_telegram(chat_id, message):
    token = current_app.config.get('TELEGRAM_BOT_TOKEN', '')
    if not token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(url, json={
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }, timeout=10)
        return r.status_code == 200
    except Exception as e:
        logging.error(f"Telegram error: {e}")
        return False


def check_reminders():
    """Cek kontrak yang akan berakhir & kirim notifikasi Telegram."""
    today = datetime.now().date()
    configured_days = current_app.config['REMINDER_DAYS']
    if isinstance(configured_days, int):
        days_list = {configured_days}
    else:
        days_list = set(cast(list[int], configured_days))

    kontraks = cast(list[Any], execute("""
        SELECT no_kontrak, uraian_pekerjaan, vendor,
               COALESCE(akhir_amandemen, akhir_kontrak) AS akhir
        FROM kontrak
        WHERE COALESCE(akhir_amandemen, akhir_kontrak) >= ?
    """, (today.isoformat(),)))

    recipient_rows = cast(Any, execute("""
        SELECT telegram_chat_id FROM users
        WHERE telegram_chat_id IS NOT NULL AND telegram_chat_id != '' AND aktif=1
    """))
    recipients = [r['telegram_chat_id'] for r in recipient_rows]

    admin_chat = current_app.config.get('TELEGRAM_ADMIN_CHAT')
    if admin_chat:
        recipients.append(admin_chat)
    recipients = list(set(recipients))

    for k in kontraks:
        akhir = _to_date(k['akhir'])
        if not akhir:
            continue
        sisa = (akhir - today).days
        if sisa in days_list:
            msg = (
                f"<b>REMINDER KONTRAK</b>\n\n"
                f"No: {k['no_kontrak']}\n"
                f"Uraian: {(k['uraian_pekerjaan'] or '-')[:100]}\n"
                f"Vendor: {k['vendor'] or '-'}\n"
                f"Akhir: {akhir.strftime('%d %B %Y')}\n"
                f"Sisa: <b>{sisa} hari</b>\n\n"
                f"{'SEGERA TINDAK LANJUTI!' if sisa <= 7 else 'Perlu persiapan.'}"
            )
            for c in recipients:
                send_telegram(c, msg)


def daily_summary():
    """Kirim ringkasan harian ke admin."""
    today = datetime.now().date()
    total = cast(Any, execute("SELECT COUNT(*) AS c FROM kontrak"))[0]['c']
    akan_rows = cast(Any, execute("""
        SELECT COUNT(*) AS c FROM kontrak
        WHERE COALESCE(akhir_amandemen, akhir_kontrak) BETWEEN ? AND ?
    """, (today.isoformat(), (today + timedelta(days=30)).isoformat())))
    akan_row = akan_rows[0]
    akan = akan_row['c']

    msg = (
        f"<b>RINGKASAN HARIAN KONTRAK</b>\n"
        f"{today.strftime('%d %B %Y')}\n\n"
        f"Total kontrak: <b>{total}</b>\n"
        f"Akan berakhir (30 hari): <b>{akan}</b>"
    )
    admin_chat = current_app.config.get('TELEGRAM_ADMIN_CHAT')
    if admin_chat:
        send_telegram(admin_chat, msg)


def sync_sheets_daily():
    """Sync ke Google Sheets tiap hari jam 6 pagi."""
    from app.services.sheets_service import SheetsService
    try:
        SheetsService.sync_all()
        logging.info("Sync Sheets harian berhasil")
    except Exception as e:
        logging.error(f"Sync Sheets harian gagal: {e}")