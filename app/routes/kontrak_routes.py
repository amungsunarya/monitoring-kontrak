from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.middlewares.auth_middleware import login_required, admin_required
from app.services.kontrak_service import KontrakService

kontrak_bp = Blueprint('kontrak', __name__)


@kontrak_bp.route('/')
@login_required
def list():
    keyword = request.args.get('q', '')
    status = request.args.get('status', '')
    data = KontrakService.list_semua(keyword=keyword, status=status)
    return render_template('kontrak/list.html', data=data, q=keyword, status_filter=status)


@kontrak_bp.route('/detail/<int:id>')
@login_required
def detail(id):
    """Halaman detail kontrak."""
    k = KontrakService.detail(id)
    if not k:
        flash('Kontrak tidak ditemukan', 'danger')
        return redirect(url_for('kontrak.list'))
    return render_template('kontrak/detail.html', k=k)


@kontrak_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        data = _form_to_dict(request.form)
        try:
            KontrakService.buat(data, session['user_id'])
            flash('Kontrak berhasil ditambahkan!', 'success')
            return redirect(url_for('kontrak.list'))
        except ValueError as e:
            flash(str(e), 'danger')
    return render_template('kontrak/form.html', k=None)


@kontrak_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if request.method == 'POST':
        data = _form_to_dict(request.form)
        KontrakService.update(id, data, session['user_id'])
        flash('Kontrak berhasil diperbarui!', 'success')
        return redirect(url_for('kontrak.detail', id=id))
    k = KontrakService.detail(id)
    return render_template('kontrak/form.html', k=k)


@kontrak_bp.route('/delete/<int:id>')
@login_required
@admin_required
def delete(id):
    KontrakService.hapus(id, session['user_id'])
    flash('Kontrak berhasil dihapus!', 'success')
    return redirect(url_for('kontrak.list'))


def _form_to_dict(form):
    return {
        'no_kontrak': form['no_kontrak'].strip(),
        'uraian_pekerjaan': form.get('uraian', ''),
        'jenis': form.get('jenis', ''),
        'link_dokumen': form.get('link', ''),
        'vendor': form.get('vendor', ''),
        'status_pekerjaan': form.get('status_pekerjaan', 'Berjalan'),
        'awal_kontrak': form['awal'],
        'akhir_kontrak': form['akhir'],
        'progres_bayar': int(form.get('bayar') or 0),
        'progres_fisik': int(form.get('fisik') or 0),
        'termin': form.get('termin', ''),
        'update_lkp': form.get('update_lkp') or None,
        'catatan': form.get('catatan', ''),
        'akhir_jampel': form.get('jampel') or None,
        'akhir_jamhar': form.get('jamhar') or None,
        'masa_pemeliharaan': form.get('pemeliharaan', ''),
        'akhir_amandemen': form.get('amandemen') or None,
    }