from datetime import date
from dateutil.relativedelta import relativedelta

BULAN_INDO = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
              'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']


def hitung_durasi(awal, akhir):
    """Hitung durasi dalam bulan + hari."""
    if not awal or not akhir:
        return None
    rd = relativedelta(akhir, awal)
    return {
        'tahun': rd.years,
        'bulan': rd.months + (rd.years * 12),
        'hari': rd.days
    }


def format_indo(d):
    if not d:
        return '-'
    return f"{d.day} {BULAN_INDO[d.month]} {d.year}"


def sisa_hari(akhir):
    if not akhir:
        return None
    return (akhir - date.today()).days