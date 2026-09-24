from flask import Blueprint, render_template
from app.middlewares.auth_middleware import login_required
from app.services.kontrak_service import KontrakService
from app.services.dashboard_service import DashboardService

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    ringkasan = KontrakService.ringkasan()
    chart_data = DashboardService.siapkan_chart()
    alerts = DashboardService.ambil_alerts(limit=10)
    return render_template(
        'dashboard/index.html',
        ringkasan=ringkasan,
        chart_data=chart_data,
        alerts=alerts
    )