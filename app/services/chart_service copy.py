from datetime import date, datetime
from typing import Any, cast
from app.database import execute


def _to_date(v):
    """Konversi value dari SQLite (str/date/datetime) ke date."""
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


class ChartService:
    @staticmethod
    def status_kontrak():
        today = date.today()
        rows = cast(list[dict[str, Any]], execute(
            "SELECT COALESCE(akhir_amandemen, akhir_kontrak) AS akhir FROM kontrak"
        ))
        aktif = akan = berakhir = 0
        for r in rows:
            akhir = _to_date(r['akhir'])
            if not akhir:
                continue
            sisa = (akhir - today).days
            if sisa < 0:
                berakhir += 1
            elif sisa <= 30:
                akan += 1
            else:
                aktif += 1
        return {
            'labels': ['Aktif', 'Akan Berakhir', 'Berakhir'],
            'data': [aktif, akan, berakhir],
            'colors': ['#38ef7d', '#f2c94c', '#f45c43']
        }

    @staticmethod
    def top_vendor(limit=10):
        rows = cast(list[dict[str, Any]], execute("""
            SELECT COALESCE(vendor, 'Tanpa Vendor') AS nama, COUNT(*) AS jml
            FROM kontrak GROUP BY vendor ORDER BY jml DESC LIMIT ?
        """, (limit,))
        )
        return {
            'labels': [r['nama'] for r in rows],
            'data': [r['jml'] for r in rows]
        }

    @staticmethod
    def tren_bulanan():
        rows = cast(list[dict[str, Any]], execute("""
            SELECT strftime('%Y-%m', awal_kontrak) AS bulan, COUNT(*) AS jml
            FROM kontrak WHERE awal_kontrak IS NOT NULL
            GROUP BY bulan ORDER BY bulan
        """))
        return {
            'labels': [r['bulan'] for r in rows],
            'jml': [r['jml'] for r in rows]
        }

    @staticmethod
    def gauge_progres():
        rows = cast(list[dict[str, Any]], execute("""
            SELECT COALESCE(AVG(progres_fisik), 0) AS avg_fisik,
                   COALESCE(AVG(progres_bayar), 0) AS avg_bayar,
                   COUNT(*) AS total FROM kontrak
        """))
        r = rows[0]
        return {
            'fisik': round(float(r['avg_fisik']), 1),
            'bayar': round(float(r['avg_bayar']), 1),
            'total': r['total']
        }

    @staticmethod
    def heatmap_bulanan():
        return execute("""
            SELECT CAST(strftime('%Y', awal_kontrak) AS INTEGER) AS tahun,
                   CAST(strftime('%m', awal_kontrak) AS INTEGER) - 1 AS bulan,
                   COUNT(*) AS jml
            FROM kontrak WHERE awal_kontrak IS NOT NULL
            GROUP BY tahun, bulan ORDER BY tahun, bulan
        """)

    @staticmethod
    def gantt_data(limit=100):
        """Data untuk Gantt chart — semua kontrak dengan timeline-nya."""
        import re

        rows = execute("""
            SELECT k.id,
                k.no_kontrak,
                k.vendor,
                k.awal_kontrak,
                k.akhir_kontrak,
                k.akhir_amandemen,
                COALESCE(k.akhir_amandemen, k.akhir_kontrak) AS akhir_efektif,
                COALESCE(k.progres_fisik, 0) AS progres,
                k.status_pekerjaan
            FROM kontrak k
            WHERE k.awal_kontrak IS NOT NULL
            AND k.akhir_kontrak IS NOT NULL
            ORDER BY k.awal_kontrak ASC
            LIMIT ?
        """, (limit,))

        def to_iso_date(v):
            if not v:
                return None
            s = str(v)[:10]
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', s):
                return None
            return s

        def safe_id(s):
            """Buat ID yang aman untuk CSS selector."""
            # Ganti semua karakter non-alphanumeric jadi underscore
            s = re.sub(r'[^a-zA-Z0-9]', '_', str(s))
            # Batasi panjang
            return s[:50]

        result = []
        used_ids = set()

        for r in rows:
            start = to_iso_date(r['awal_kontrak'])
            end = to_iso_date(r['akhir_efektif'])

            if not start or not end:
                continue

            if end < start:
                start, end = end, start

            # ID AMAN — pakai kontrak_id (integer) yang pasti unik
            task_id = f"k{r['id']}"

            # Fallback: pastikan unik
            base_id = task_id
            counter = 1
            while task_id in used_ids:
                task_id = f"{base_id}_{counter}"
                counter += 1
            used_ids.add(task_id)

            # Warna berdasarkan status
            status = (r.get('status_pekerjaan') or 'Berjalan').strip()
            if status == 'Selesai':
                custom_class = 'bar-done'
            elif status == 'Ditunda':
                custom_class = 'bar-pending'
            elif status == 'Batal':
                custom_class = 'bar-cancelled'
            else:
                custom_class = 'bar-active'

            # Progress
            try:
                progress_val = int(float(r['progres'] or 0))
                progress_val = max(0, min(100, progress_val))
            except (ValueError, TypeError):
                progress_val = 0

            # Nama — batasi panjang
            no_kontrak_short = str(r['no_kontrak'] or '')
            if len(no_kontrak_short) > 40:
                no_kontrak_short = no_kontrak_short[:37] + '...'

            vendor_short = str(r['vendor'] or 'Tanpa Vendor')
            if len(vendor_short) > 30:
                vendor_short = vendor_short[:27] + '...'

            result.append({
                'id': task_id,                             # ← AMAN: k1, k2, k3...
                'kontrak_id': int(r['id']),
                'no_kontrak_asli': str(r['no_kontrak'] or ''),  # ← asli, untuk popup
                'name': f"{no_kontrak_short} — {vendor_short}",
                'start': str(start),
                'end': str(end),
                'progress': progress_val,
                'dependencies': '',
                'custom_class': custom_class,
            })

        return result

    @staticmethod
    def scurve(kontrak_id):
        rows = cast(list[dict[str, Any]], execute(
            "SELECT * FROM kontrak WHERE id=?", (kontrak_id,)
        ))
        if not rows:
            return None
        k = rows[0]
        start = _to_date(k['awal_kontrak'])
        end = _to_date(k['akhir_kontrak'])
        if not start or not end:
            return None

        labels, rencana, realisasi = [], [], []
        cur = date(start.year, start.month, 1)
        end_check = date(end.year, end.month, 1)
        today = date.today()
        idx = 0
        total_bulan = ((end.year - start.year) * 12 + (end.month - start.month)) or 1

        while cur <= end_check and idx < 60:
            ratio = idx / total_bulan
            s = 1 / (1 + pow(2.718, -8 * (ratio - 0.5)))
            s_akhir = 1 / (1 + pow(2.718, -8 * 0.5))
            rencana_val = round((s / s_akhir) * 100, 1)
            if cur <= today:
                realisasi_val = round(rencana_val * (k['progres_fisik'] or 0) / 100, 1)
            else:
                realisasi_val = None
            labels.append(cur.strftime('%b %Y'))
            rencana.append(rencana_val)
            realisasi.append(realisasi_val)
            cur = date(cur.year + 1, 1, 1) if cur.month == 12 else date(cur.year, cur.month + 1, 1)
            idx += 1

        return {
            'no_kontrak': k['no_kontrak'],
            'labels': labels,
            'rencana': rencana,
            'realisasi': realisasi,
            'progres_fisik': k['progres_fisik'] or 0,
            'progres_bayar': k['progres_bayar'] or 0
        }

    @staticmethod
    def deviasi_progres():
        rows = cast(list[dict[str, Any]], execute("""
            SELECT no_kontrak,
                   COALESCE(progres_fisik, 0) AS fisik,
                   COALESCE(progres_bayar, 0) AS bayar
            FROM kontrak
            ORDER BY ABS(COALESCE(progres_fisik,0) - COALESCE(progres_bayar,0)) DESC
            LIMIT 15
        """))
        return {
            'labels': [r['no_kontrak'] for r in rows],
            'fisik': [r['fisik'] for r in rows],
            'bayar': [r['bayar'] for r in rows]
        }