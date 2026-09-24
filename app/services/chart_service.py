"""
Chart Service — siapkan data untuk semua chart dashboard.
"""
import re
from datetime import date, datetime
from typing import Any, cast

from app.database import execute


# ============================================================
# HELPER
# ============================================================
def _to_date(v):
    """Konversi value dari SQLite (str/date/datetime) ke date."""
    if v is None or v == '':
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    if isinstance(v, str):
        for fmt in ('%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y'):
            try:
                return datetime.strptime(v[:19], fmt).date()
            except ValueError:
                continue
    return None


def _to_int(v, default=0):
    """Konversi value ke int dengan aman."""
    if v is None:
        return default
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return default


def _to_iso_date(v):
    """Konversi value apapun ke string 'YYYY-MM-DD' atau None."""
    d = _to_date(v)
    if not d:
        return None
    return d.strftime('%Y-%m-%d')


def _get(row, key, default=None):
    """Akses field dari dict / sqlite3.Row dengan aman."""
    try:
        # dict biasa
        if isinstance(row, dict):
            return row.get(key, default)
        # sqlite3.Row
        if hasattr(row, 'keys'):
            keys = row.keys()
            if key in keys:
                val = row[key]
                return val if val is not None else default
        return default
    except Exception:
        return default


# ============================================================
# CHART SERVICE
# ============================================================
class ChartService:

    # ---------- PIE STATUS ----------
    @staticmethod
    def status_kontrak():
        today = date.today()
        rows = execute(
            "SELECT COALESCE(akhir_amandemen, akhir_kontrak) AS akhir FROM kontrak"
        )
        aktif = akan = berakhir = 0

        for r in rows:
            akhir = _to_date(_get(r, 'akhir'))
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

    # ---------- BAR VENDOR ----------
    @staticmethod
    def top_vendor(limit=10):
        rows = execute("""
            SELECT COALESCE(vendor, 'Tanpa Vendor') AS nama, COUNT(*) AS jml
            FROM kontrak
            GROUP BY vendor
            ORDER BY jml DESC
            LIMIT ?
        """, (limit,))
        return {
            'labels': [_get(r, 'nama', '-') for r in rows],
            'data': [_to_int(_get(r, 'jml')) for r in rows]
        }

    # ---------- LINE TREN ----------
    @staticmethod
    def tren_bulanan():
        rows = execute("""
            SELECT strftime('%Y-%m', awal_kontrak) AS bulan, COUNT(*) AS jml
            FROM kontrak
            WHERE awal_kontrak IS NOT NULL
            GROUP BY bulan
            ORDER BY bulan
        """)
        return {
            'labels': [_get(r, 'bulan', '-') for r in rows],
            'jml': [_to_int(_get(r, 'jml')) for r in rows]
        }

    # ---------- GAUGE ----------
    @staticmethod
    def gauge_progres():
        rows = execute("""
            SELECT COALESCE(AVG(progres_fisik), 0) AS avg_fisik,
                   COALESCE(AVG(progres_bayar), 0) AS avg_bayar,
                   COUNT(*) AS total
            FROM kontrak
        """)
        if not rows:
            return {'fisik': 0, 'bayar': 0, 'total': 0}

        r = rows[0]
        return {
            'fisik': round(float(_get(r, 'avg_fisik', 0) or 0), 1),
            'bayar': round(float(_get(r, 'avg_bayar', 0) or 0), 1),
            'total': _to_int(_get(r, 'total'))
        }

    # ---------- HEATMAP ----------
    @staticmethod
    def heatmap_bulanan():
        rows = execute("""
            SELECT CAST(strftime('%Y', awal_kontrak) AS INTEGER) AS tahun,
                   CAST(strftime('%m', awal_kontrak) AS INTEGER) - 1 AS bulan,
                   COUNT(*) AS jml
            FROM kontrak
            WHERE awal_kontrak IS NOT NULL
            GROUP BY tahun, bulan
            ORDER BY tahun, bulan
        """)
        # Pastikan return format konsisten
        return [
            {
                'tahun': _to_int(_get(r, 'tahun')),
                'bulan': _to_int(_get(r, 'bulan')),
                'jml': _to_int(_get(r, 'jml'))
            }
            for r in rows
        ]

    # ---------- GANTT ----------
    @staticmethod
    def gantt_data(limit=100):
        """
        Data untuk Gantt chart.

        Return list dict dengan format:
        {
            id: 'k1',                       # WAJIB unik, format aman
            kontrak_id: 1,                  # untuk klik → detail
            no_kontrak_asli: '0024/...',    # untuk display
            name: '0024/... — PT Xxx',      # display di bar
            start: '2026-01-01',            # WAJIB YYYY-MM-DD
            end: '2026-12-01',              # WAJIB YYYY-MM-DD
            progress: 85,                   # WAJIB integer 0-100
            dependencies: '',               # WAJIB string
            custom_class: 'bar-active',     # untuk styling warna
        }
        """
        rows = execute("""
            SELECT k.id,
                   k.no_kontrak,
                   k.vendor,
                   k.awal_kontrak,
                   k.akhir_kontrak,
                   k.akhir_amandemen,
                   COALESCE(k.akhir_amandemen, k.akhir_kontrak) AS akhir_efektif,
                   COALESCE(k.progres_fisik, 0) AS progres,
                   COALESCE(k.status_pekerjaan, 'Berjalan') AS status_pekerjaan
            FROM kontrak k
            WHERE k.awal_kontrak IS NOT NULL
              AND k.akhir_kontrak IS NOT NULL
            ORDER BY k.awal_kontrak ASC
            LIMIT ?
        """, (limit,))

        result = []
        used_ids = set()

        for r in rows:
            # Ambil tanggal
            start_str = _to_iso_date(_get(r, 'awal_kontrak'))
            end_str = _to_iso_date(_get(r, 'akhir_efektif'))

            if not start_str or not end_str:
                continue

            # Pastikan end >= start
            if end_str < start_str:
                start_str, end_str = end_str, start_str

            # Ambil kontrak_id
            kontrak_id = _to_int(_get(r, 'id'), 0)
            if kontrak_id <= 0:
                continue

            # Buat ID unik dan aman
            task_id = f"k{kontrak_id}"
            counter = 1
            while task_id in used_ids:
                task_id = f"k{kontrak_id}_{counter}"
                counter += 1
            used_ids.add(task_id)

            # Warna berdasarkan status
            status = str(_get(r, 'status_pekerjaan', 'Berjalan') or 'Berjalan').strip()
            if status == 'Selesai':
                custom_class = 'bar-done'
            elif status == 'Ditunda':
                custom_class = 'bar-pending'
            elif status == 'Batal':
                custom_class = 'bar-cancelled'
            else:
                custom_class = 'bar-active'

            # Progress — paksa integer 0-100
            progress_val = _to_int(_get(r, 'progres'), 0)
            progress_val = max(0, min(100, progress_val))

            # Nama — batasi panjang
            no_kontrak_asli = str(_get(r, 'no_kontrak', '') or '')
            no_kontrak_short = no_kontrak_asli
            if len(no_kontrak_short) > 40:
                no_kontrak_short = no_kontrak_short[:37] + '...'

            vendor_short = str(_get(r, 'vendor', '') or 'Tanpa Vendor')
            if len(vendor_short) > 30:
                vendor_short = vendor_short[:27] + '...'

            result.append({
                'id': task_id,
                'kontrak_id': kontrak_id,
                'no_kontrak_asli': no_kontrak_asli,
                'name': f"{no_kontrak_short} — {vendor_short}",
                'start': start_str,
                'end': end_str,
                'progress': progress_val,
                'dependencies': '',
                'custom_class': custom_class,
            })

        return result

    # ---------- S-CURVE ----------
    @staticmethod
    def scurve(kontrak_id):
        rows = execute("SELECT * FROM kontrak WHERE id=?", (kontrak_id,))
        if not rows:
            return None

        k = rows[0]
        start = _to_date(_get(k, 'awal_kontrak'))
        end = _to_date(_get(k, 'akhir_kontrak'))

        if not start or not end:
            return None

        progres_fisik = _to_int(_get(k, 'progres_fisik'), 0)
        progres_bayar = _to_int(_get(k, 'progres_bayar'), 0)

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
                realisasi_val = round(rencana_val * progres_fisik / 100, 1)
            else:
                realisasi_val = None

            labels.append(cur.strftime('%b %Y'))
            rencana.append(rencana_val)
            realisasi.append(realisasi_val)

            # Next month
            if cur.month == 12:
                cur = date(cur.year + 1, 1, 1)
            else:
                cur = date(cur.year, cur.month + 1, 1)
            idx += 1

        return {
            'no_kontrak': str(_get(k, 'no_kontrak', '') or ''),
            'labels': labels,
            'rencana': rencana,
            'realisasi': realisasi,
            'progres_fisik': progres_fisik,
            'progres_bayar': progres_bayar
        }

    # ---------- DEVIASI ----------
    @staticmethod
    def deviasi_progres():
        rows = execute("""
            SELECT no_kontrak,
                   COALESCE(progres_fisik, 0) AS fisik,
                   COALESCE(progres_bayar, 0) AS bayar
            FROM kontrak
            ORDER BY ABS(COALESCE(progres_fisik,0) - COALESCE(progres_bayar,0)) DESC
            LIMIT 15
        """)
        return {
            'labels': [str(_get(r, 'no_kontrak', '-') or '-')[:30] for r in rows],
            'fisik': [_to_int(_get(r, 'fisik')) for r in rows],
            'bayar': [_to_int(_get(r, 'bayar')) for r in rows]
        }