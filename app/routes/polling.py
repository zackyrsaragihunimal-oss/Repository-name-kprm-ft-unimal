from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from ..models import PollingStation, ElectionPeriod
from ..extensions import db
from ..utils.audit import log_activity

polling_bp = Blueprint('polling', __name__)

@polling_bp.route('/')
@login_required
def index():
    tps_list = PollingStation.query.order_by(PollingStation.code).all()
    return render_template('admin/polling/index.html', tps_list=tps_list)

@polling_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        tps = PollingStation(
            election_period_id=request.form.get('election_period_id', type=int),
            name=request.form.get('name', '').strip(), code=request.form.get('code', '').strip(),
            location=request.form.get('location', '').strip(),
            capacity=request.form.get('capacity', 100, type=int), status='active'
        )
        db.session.add(tps)
        db.session.commit()
        log_activity('Menambah TPS', 'polling_station', tps.id)
        flash('TPS ditambahkan.', 'success')
        return redirect(url_for('polling.index'))
    elections = ElectionPeriod.query.all()
    return render_template('admin/polling/form.html', tps=None, elections=elections)

@polling_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    tps = PollingStation.query.get_or_404(id)
    if request.method == 'POST':
        tps.name = request.form.get('name', '').strip()
        tps.code = request.form.get('code', '').strip()
        tps.location = request.form.get('location', '').strip()
        tps.capacity = request.form.get('capacity', 100, type=int)
        tps.status = request.form.get('status', 'active')
        db.session.commit()
        log_activity('Mengedit TPS', 'polling_station', tps.id)
        flash('TPS diperbarui.', 'success')
        return redirect(url_for('polling.index'))
    elections = ElectionPeriod.query.all()
    return render_template('admin/polling/form.html', tps=tps, elections=elections)

@polling_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    tps = PollingStation.query.get_or_404(id)
    log_activity('Menghapus TPS', 'polling_station', tps.id)
    db.session.delete(tps)
    db.session.commit()
    flash('TPS dihapus.', 'success')
    return redirect(url_for('polling.index'))
