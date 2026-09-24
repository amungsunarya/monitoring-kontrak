from flask import Blueprint, render_template
from app.middlewares.auth_middleware import login_required
from app.repositories.log_repo import LogRepository

log_bp = Blueprint('log', __name__)


@log_bp.route('/')
@login_required
def list():
    data = LogRepository.recent(500)
    return render_template('log/list.html', data=data)