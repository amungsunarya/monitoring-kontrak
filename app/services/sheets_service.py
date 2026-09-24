"""Sync data kontrak ke Google Sheets."""
import os
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import current_app

SCOPES = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

HEADERS = [
    'NO. KONTRAK', 'URAIAN PEKERJAAN', 'Jenis', 'Link Dokumen', 'VENDOR',
    'Status Pekerjaan', 'Awal Kontrak', 'Akhir Kontrak',
    'Progres bayar', 'Progres Fisik', 'Termin', 'Update LKP', 'Catatan',
    'Akhir JamPel', 'Akhir JamHar', 'Masa Pemeliharaan',
    'Akhir Amandemen', 'STATUS Masa Kontrak'
]


class SheetsService:
    _client = None
    _sheet = None

    @classmethod
    def _connect(cls):
        if cls._client is not None:
            return
        creds_file = current_app.config.get('GSHEET_CREDENTIALS', 'credentials.json')
        sheet_id = current_app.config.get('GSHEET_ID', '')
        sheet_name = current_app.config.get('GSHEET_NAME', 'Kontrak')
        if not os.path.exists(creds_file):
            raise FileNotFoundError(f"File credentials tidak ditemukan: {creds_file}")
        if not sheet_id:
            raise ValueError("GSHEET_ID belum diset di .env")
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, SCOPES)
        cls._client = gspread.authorize(creds)
        spreadsheet = cls._client.open_by_key(sheet_id)
        try:
            cls._sheet = spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            cls._sheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            cls._sheet.append_row(HEADERS)
        current_app.logger.info(f"Google Sheets connected: {sheet_name}")

    @classmethod
    def sync_all(cls):
        try:
            cls._connect()
            from app.repositories.kontrak_repo import KontrakRepository
            sheet = cls._sheet
            data = KontrakRepository.all_for_sheet()
            today = date.today()
            rows = [HEADERS]
            for d in data:
                ae = d['akhir_efektif']
                if ae:
                    sisa = (ae - today).days
                    if sisa < 0:
                        sm = 'Berakhir'
                    elif sisa <= 30:
                        sm = f'Akan Berakhir ({sisa} hari)'
                    else:
                        sm = f'Aktif ({sisa} hari)'
                else:
                    sm = '-'
                rows.append([
                    d['no_kontrak'] or '',
                    d['uraian_pekerjaan'] or '',
                    d['jenis'] or '',
                    d['link_dokumen'] or '',
                    d['vendor'] or '',
                    d['status_pekerjaan'] or '',
                    str(d['awal_kontrak']) if d['awal_kontrak'] else '',
                    str(d['akhir_kontrak']) if d['akhir_kontrak'] else '',
                    d['progres_bayar'] or 0,
                    d['progres_fisik'] or 0,
                    d['termin'] or '',
                    str(d['update_lkp']) if d['update_lkp'] else '',
                    d['catatan'] or '',
                    str(d['akhir_jampel']) if d['akhir_jampel'] else '',
                    str(d['akhir_jamhar']) if d['akhir_jamhar'] else '',
                    d['masa_pemeliharaan'] or '',
                    str(d['akhir_amandemen']) if d['akhir_amandemen'] else '',
                    sm,
                ])
            sheet.clear()
            sheet.update('A1', rows, value_input_option='USER_ENTERED')
            sheet.format('A1:R1', {
                'textFormat': {
                    'bold': True,
                    'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}
                },
                'backgroundColor': {'red': 0.2, 'green': 0.28, 'blue': 0.37},
            })
            sheet.freeze(rows=1)
            current_app.logger.info(f"Sync {len(data)} kontrak ke Google Sheets")
            return True
        except Exception as e:
            current_app.logger.error(f"Gagal sync ke Sheets: {e}")
            return False