from datetime import date, timedelta
from app.models.kontrak import Kontrak


def test_sisa_hari_positif():
    k = Kontrak(
        akhir_kontrak=date.today() + timedelta(days=100),
        akhir_amandemen=None
    )
    assert k.sisa_hari == 100
    assert k.status_masa_kontrak == 'aktif'


def test_akan_berakhir_30_hari():
    k = Kontrak(
        akhir_kontrak=date.today() + timedelta(days=15),
        akhir_amandemen=None
    )
    assert k.status_masa_kontrak == 'akan'


def test_sudah_berakhir():
    k = Kontrak(
        akhir_kontrak=date.today() - timedelta(days=5),
        akhir_amandemen=None
    )
    assert k.status_masa_kontrak == 'berakhir'


def test_amandemen_lebih_diprioritaskan():
    k = Kontrak(
        akhir_kontrak=date.today() - timedelta(days=5),
        akhir_amandemen=date.today() + timedelta(days=200)
    )
    assert k.status_masa_kontrak == 'aktif'
    assert k.sisa_hari == 200


def test_badge_label():
    k = Kontrak(
        akhir_kontrak=date.today() + timedelta(days=100),
        akhir_amandemen=None
    )
    assert 'badge-aktif' in k.status_masa_kontrak_badge
    assert 'Aktif' in k.status_masa_kontrak_label


def test_tanpa_tanggal():
    k = Kontrak(akhir_kontrak=None, akhir_amandemen=None)
    assert k.sisa_hari is None
    assert k.status_masa_kontrak == 'unknown'