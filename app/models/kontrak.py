from datetime import date, datetime


def _parse_date(v):
    """Konversi value apapun ke date atau None."""
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


class Kontrak:
    # Daftar property yang TIDAK boleh di-set dari __init__
    _READONLY_PROPS = {
        'akhir_efektif', 'sisa_hari',
        'status_masa_kontrak', 'status_masa_kontrak_label',
        'status_masa_kontrak_badge', 'deviasi', 'is_terlambat',
        '_akhir_kontrak_date', '_akhir_amandemen_date',
    }

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            # Skip key yang berupa property (read-only)
            if k in self._READONLY_PROPS:
                continue
            # Skip juga kalau nama property sudah didefinisikan di class
            if isinstance(getattr(type(self), k, None), property):
                continue
            setattr(self, k, v)

    # ---------- Tanggal ----------
    @property
    def _akhir_kontrak_date(self):
        return _parse_date(getattr(self, 'akhir_kontrak', None))

    @property
    def _akhir_amandemen_date(self):
        return _parse_date(getattr(self, 'akhir_amandemen', None))

    @property
    def akhir_efektif(self):
        """Tanggal akhir efektif — amandemen kalau ada, else kontrak."""
        return self._akhir_amandemen_date or self._akhir_kontrak_date

    @property
    def sisa_hari(self):
        akhir = self.akhir_efektif
        if not akhir:
            return None
        return (akhir - date.today()).days

    # ---------- Status ----------
    @property
    def status_masa_kontrak(self):
        s = self.sisa_hari
        if s is None:
            return 'unknown'
        if s < 0:
            return 'berakhir'
        if s <= 30:
            return 'akan'
        return 'aktif'

    @property
    def status_masa_kontrak_label(self):
        return {
            'aktif': f'Aktif ({self.sisa_hari} hari)',
            'akan': f'Akan Berakhir ({self.sisa_hari} hari)',
            'berakhir': 'Berakhir',
            'unknown': 'Cek Tanggal',
        }.get(self.status_masa_kontrak, '-')

    @property
    def status_masa_kontrak_badge(self):
        return {
            'aktif': 'badge-aktif',
            'akan': 'badge-akan',
            'berakhir': 'badge-berakhir',
            'unknown': 'badge-secondary',
        }.get(self.status_masa_kontrak, 'badge-secondary')

    # ---------- Analisa ----------
    @property
    def deviasi(self):
        """Selisih progres fisik vs bayar (untuk deteksi anomali)."""
        return (getattr(self, 'progres_fisik', 0) or 0) - (getattr(self, 'progres_bayar', 0) or 0)

    @property
    def is_terlambat(self):
        """Progres fisik < progres ideal (linear)?"""
        akhir = self._akhir_kontrak_date
        awal = _parse_date(getattr(self, 'awal_kontrak', None))
        if not awal or not akhir:
            return False
        total_hari = (akhir - awal).days
        if total_hari <= 0:
            return False
        hari_berjalan = (date.today() - awal).days
        if hari_berjalan <= 0:
            return False
        ideal = min(100, hari_berjalan / total_hari * 100)
        return (getattr(self, 'progres_fisik', 0) or 0) < (ideal - 10)

    # ---------- Factory ----------
    @classmethod
    def from_row(cls, row):
        return cls(**row) if row else None

    @classmethod
    def from_rows(cls, rows):
        return [cls(**r) for r in rows]

    # ---------- Serialization ----------
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}

    def __repr__(self):
        return f"<Kontrak id={getattr(self, 'id', None)} no={getattr(self, 'no_kontrak', '')}>"