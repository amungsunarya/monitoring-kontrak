import requests
from flask import current_app


class NotificationService:
    @staticmethod
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
            current_app.logger.error(f"Telegram error: {e}")
            return False