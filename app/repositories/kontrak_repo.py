from app.database import execute
from typing import Any, cast


class KontrakRepository:
    # Tidak pakai alias akhir_efektif — biar dihitung di model
    BASE_QUERY = """
        SELECT k.*
        FROM kontrak k
    """

    @staticmethod
    def all(limit=None):
        sql = KontrakRepository.BASE_QUERY + " ORDER BY k.id DESC"
        if limit:
            sql += " LIMIT ?"
            return execute(sql, (limit,))
        return execute(sql)

    @staticmethod
    def by_id(id):
        rows = cast(list[Any], execute(KontrakRepository.BASE_QUERY + " WHERE k.id=?", (id,)))
        return rows[0] if rows else None

    @staticmethod
    def search(keyword=None, limit=None):
        if not keyword:
            return KontrakRepository.all(limit=limit)

        # Escape wildcard
        kw = keyword.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        like = f'%{kw}%'

        sql = KontrakRepository.BASE_QUERY + """
            WHERE k.no_kontrak LIKE ? ESCAPE '\\'
               OR k.uraian_pekerjaan LIKE ? ESCAPE '\\'
               OR k.vendor LIKE ? ESCAPE '\\'
            ORDER BY k.id DESC
        """
        params = [like, like, like]
        if limit:
            sql += " LIMIT ?"
            params.append(limit)
        return execute(sql, params)

    @staticmethod
    def create(data):
        cols = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        sql = f"INSERT INTO kontrak ({cols}) VALUES ({placeholders})"
        return execute(sql, list(data.values()), fetch=False)

    @staticmethod
    def update(id, data):
        sets = ', '.join([f"{k}=?" for k in data.keys()])
        sql = f"UPDATE kontrak SET {sets} WHERE id=?"
        execute(sql, list(data.values()) + [id], fetch=False)

    @staticmethod
    def delete(id):
        execute("DELETE FROM kontrak WHERE id=?", (id,), fetch=False)

    @staticmethod
    def all_for_sheet():
        """Untuk sync ke Google Sheets — di sini boleh pakai alias."""
        return execute("""
            SELECT no_kontrak, uraian_pekerjaan, jenis, link_dokumen, vendor,
                   status_pekerjaan, awal_kontrak, akhir_kontrak,
                   progres_bayar, progres_fisik, termin, update_lkp, catatan,
                   akhir_jampel, akhir_jamhar, masa_pemeliharaan, akhir_amandemen,
                   COALESCE(akhir_amandemen, akhir_kontrak) AS akhir_efektif
            FROM kontrak ORDER BY id
        """)