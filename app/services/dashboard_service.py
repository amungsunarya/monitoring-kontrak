from app.services.kontrak_service import KontrakService
from app.database import execute
from typing import cast


class DashboardService:
    @staticmethod
    def siapkan_chart():
        ringkasan = KontrakService.ringkasan()
        per_vendor = execute("""
            SELECT COALESCE(vendor, 'Tanpa Vendor') AS nama, COUNT(*) AS jml
            FROM kontrak GROUP BY vendor ORDER BY jml DESC LIMIT 10
        """)
        per_bulan = execute("""
            SELECT strftime('%Y-%m', awal_kontrak) AS bulan, COUNT(*) AS jml
            FROM kontrak WHERE awal_kontrak IS NOT NULL
            GROUP BY bulan ORDER BY bulan
        """)
        return {
            'status': {
                'Aktif': ringkasan['aktif'],
                'Akan Berakhir': ringkasan['akan'],
                'Berakhir': ringkasan['berakhir'],
            },
            'per_vendor': per_vendor,
            'per_bulan': per_bulan,
        }

    @staticmethod
    def ambil_alerts(limit=10):
        kontraks = KontrakService.list_semua()
        alerts = [k for k in kontraks if k.sisa_hari is not None and 0 <= k.sisa_hari <= 30]
        return sorted(alerts, key=lambda x: cast(int, x.sisa_hari))[:limit]