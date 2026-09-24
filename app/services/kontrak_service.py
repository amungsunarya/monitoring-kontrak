from app.repositories.kontrak_repo import KontrakRepository
from app.repositories.log_repo import LogRepository
from app.models.kontrak import Kontrak
from datetime import date


class KontrakService:
    @staticmethod
    def list_semua(keyword=None, status=None):
        rows = KontrakRepository.search(keyword)
        items = Kontrak.from_rows(rows)
        if status:
            items = [k for k in items if k.status_masa_kontrak == status]
        return items

    @staticmethod
    def detail(id):
        return Kontrak.from_row(KontrakRepository.by_id(id))

    @staticmethod
    def buat(data, user_id=None):
        if not data.get('no_kontrak'):
            raise ValueError('No kontrak wajib diisi')
        if not data.get('awal_kontrak') or not data.get('akhir_kontrak'):
            raise ValueError('Tanggal kontrak wajib diisi')
        _validate_dates(data)
        new_id = KontrakRepository.create(data)
        LogRepository.add(user_id, 'ADD', f"Tambah kontrak: {data['no_kontrak']}")
        _sync_sheets_safe()
        return new_id

    @staticmethod
    def update(id, data, user_id=None):
        if not KontrakRepository.by_id(id):
            raise ValueError('Kontrak tidak ditemukan')
        if not data.get('no_kontrak'):
            raise ValueError('No kontrak wajib diisi')
        _validate_dates(data)
        KontrakRepository.update(id, data)
        LogRepository.add(user_id, 'EDIT', f"Edit kontrak ID {id}")
        _sync_sheets_safe()

    @staticmethod
    def hapus(id, user_id=None):
        k = KontrakRepository.by_id(id)
        KontrakRepository.delete(id)
        LogRepository.add(user_id, 'DELETE', f"Hapus kontrak: {k['no_kontrak'] if k else id}")
        _sync_sheets_safe()

    @staticmethod
    def ringkasan():
        kontraks = KontrakService.list_semua()
        return {
            'total': len(kontraks),
            'aktif': sum(1 for k in kontraks if k.status_masa_kontrak == 'aktif'),
            'akan': sum(1 for k in kontraks if k.status_masa_kontrak == 'akan'),
            'berakhir': sum(1 for k in kontraks if k.status_masa_kontrak == 'berakhir'),
        }


def _sync_sheets_safe():
    try:
        from app.services.sheets_service import SheetsService
        SheetsService.sync_all()
    except Exception as e:
        try:
            from flask import current_app
            current_app.logger.error(f"Sheets sync error: {e}")
        except Exception:
            print(f"Sheets sync error: {e}")


def _validate_dates(data):
    try:
        awal = date.fromisoformat(str(data['awal_kontrak']))
        akhir = date.fromisoformat(str(data['akhir_kontrak']))
        amandemen = data.get('akhir_amandemen')
        amandemen = date.fromisoformat(str(amandemen)) if amandemen else None
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError('Format tanggal kontrak tidak valid.') from exc
    if akhir < awal:
        raise ValueError('Akhir kontrak tidak boleh sebelum awal kontrak.')
    if amandemen and amandemen < awal:
        raise ValueError('Akhir amandemen tidak boleh sebelum awal kontrak.')