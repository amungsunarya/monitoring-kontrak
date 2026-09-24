from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.middlewares.auth_middleware import login_required, admin_required
from app.services.user_service import UserService

user_bp = Blueprint('user', __name__)


@user_bp.route('/')
@login_required
@admin_required
def list():
    data = UserService.semua()
    return render_template('users/list.html', data=data)


@user_bp.route('/add', methods=['POST'])
@login_required
@admin_required
def add():
    try:
        UserService.buat(request.form, session['user_id'])
        flash('User berhasil ditambahkan!', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('user.list'))


@user_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
@admin_required
def edit(id):
    try:
        UserService.update(id, request.form, session['user_id'])
        flash('User berhasil diperbarui!', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('user.list'))


@user_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete(id):
    if id == session['user_id']:
        flash('Tidak bisa hapus akun sendiri!', 'danger')
        return redirect(url_for('user.list'))
    UserService.hapus(id, session['user_id'])
    flash('User dihapus!', 'success')
    return redirect(url_for('user.list'))