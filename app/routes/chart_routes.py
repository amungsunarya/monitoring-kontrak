from flask import Blueprint, jsonify
from app.middlewares.auth_middleware import login_required
from app.services.chart_service import ChartService
from app.database import execute

chart_bp = Blueprint('chart', __name__)


@chart_bp.route('/status')
@login_required
def status():
    return jsonify(ChartService.status_kontrak())


@chart_bp.route('/vendor')
@login_required
def vendor():
    return jsonify(ChartService.top_vendor())


@chart_bp.route('/tren')
@login_required
def tren():
    return jsonify(ChartService.tren_bulanan())


@chart_bp.route('/gauge')
@login_required
def gauge():
    return jsonify(ChartService.gauge_progres())


@chart_bp.route('/heatmap')
@login_required
def heatmap():
    return jsonify(ChartService.heatmap_bulanan())


@chart_bp.route('/gantt')
@login_required
def gantt():
    return jsonify(ChartService.gantt_data())


@chart_bp.route('/scurve/<int:id>')
@login_required
def scurve(id):
    r = ChartService.scurve(id)
    if not r:
        return jsonify({'error': 'Data tidak ditemukan'}), 404
    return jsonify(r)


@chart_bp.route('/deviasi')
@login_required
def deviasi():
    return jsonify(ChartService.deviasi_progres())


@chart_bp.route('/kontrak-list')
@login_required
def kontrak_list():
    rows = execute("SELECT id, no_kontrak FROM kontrak ORDER BY no_kontrak")
    return jsonify(rows)