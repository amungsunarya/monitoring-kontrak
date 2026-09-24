from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services.auth_service import AuthService
from app.repositories.log_repo import LogRepository

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = AuthService.login(
            request.form.get('username', '').strip(),
            request.form.get('password', ''),
            request.remote_addr)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['nama'] = user['nama']
            session['role'] = user['role']
            return redirect(url_for('dashboard.index'))
        flash('Username atau password salah!', 'danger')
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    if 'user_id' in session:
        LogRepository.add(session['user_id'], 'LOGOUT', 'Logout')
    session.clear()
    return redirect(url_for('auth.login'))