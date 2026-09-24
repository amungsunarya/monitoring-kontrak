"""
Scheduler runner untuk reminder Telegram & sync Google Sheets.
Jalankan terpisah dari web: python -m scheduler.runner
"""
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from app import create_app
from scheduler.jobs import check_reminders, daily_summary, sync_sheets_daily

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)


def main():
    app = create_app('production')
    with app.app_context():
        scheduler = BlockingScheduler(timezone='Asia/Jakarta')

        scheduler.add_job(sync_sheets_daily, 'cron', hour=6, minute=0)
        scheduler.add_job(daily_summary, 'cron', hour=7, minute=0)
        scheduler.add_job(check_reminders, 'cron', hour=8, minute=0)

        logging.info("Scheduler berjalan... Tekan Ctrl+C untuk stop.")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logging.info("Scheduler dihentikan.")


if __name__ == '__main__':
    main()