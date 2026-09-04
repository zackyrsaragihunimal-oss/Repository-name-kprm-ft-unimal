from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from ..models import ElectionPeriod, ElectionPhase
from ..extensions import db
from ..utils.audit import log_activity
from datetime import datetime

elections_bp = Blueprint('elections', __name__)

@elections_bp.route('/')
@login_required
def index():
    elections = ElectionPeriod.query.order_by(ElectionPeriod.year.desc()).all()
    return render_template('admin/elections/index.html', elections=elections)

@elections_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        ep = ElectionPeriod(
            name=request.form.get('name', '').strip(), year=request.form.get('year', type=int),
            description=request.form.get('description', ''), status=request.form.get('status', 'persiapan'),
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date() if request.form.get('start_date') else None,
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date() if request.form.get('end_date') else None,
        )
        db.session.add(ep)
        db.session.commit()
        log_activity('Menambah periode pemilihan', 'election_period', ep.id)
        flash('Periode pemilihan ditambahkan.', 'success')
        return redirect(url_for('elections.index'))
    return render_template('admin/elections/form.html', election=None)

@elections_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    ep = ElectionPeriod.query.get_or_404(id)
    if request.method == 'POST':
        ep.name = request.form.get('name', '').strip()
        ep.year = request.form.get('year', type=int)
        ep.description = request.form.get('description', '')
        ep.status = request.form.get('status', 'persiapan')
        ep.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date() if request.form.get('start_date') else None
        ep.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date() if request.form.get('end_date') else None
        db.session.commit()
        log_activity('Mengedit periode pemilihan', 'election_period', ep.id)
        flash('Periode diperbarui.', 'success')
        return redirect(url_for('elections.index'))
    return render_template('admin/elections/form.html', election=ep)

@elections_bp.route('/phases/<int:election_id>')
@login_required
def phases(election_id):
    ep = ElectionPeriod.query.get_or_404(election_id)
    phases = ElectionPhase.query.filter_by(election_period_id=election_id).order_by(ElectionPhase.order_number).all()
    return render_template('admin/elections/phases.html', election=ep, phases=phases)

@elections_bp.route('/phases/<int:election_id>/create', methods=['POST'])
@login_required
def create_phase(election_id):
    ph = ElectionPhase(
        election_period_id=election_id, name=request.form.get('name', '').strip(),
        description=request.form.get('description', ''),
        start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date() if request.form.get('start_date') else None,
        end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date() if request.form.get('end_date') else None,
        status=request.form.get('status', 'upcoming'),
        order_number=request.form.get('order_number', 0, type=int)
    )
    db.session.add(ph)
    db.session.commit()
    log_activity('Menambah tahapan', 'election_phase', ph.id)
    flash('Tahapan ditambahkan.', 'success')
    return redirect(url_for('elections.phases', election_id=election_id))

@elections_bp.route('/phases/delete/<int:id>', methods=['POST'])
@login_required
def delete_phase(id):
    ph = ElectionPhase.query.get_or_404(id)
    eid = ph.election_period_id
    log_activity('Menghapus tahapan', 'election_phase', ph.id)
    db.session.delete(ph)
    db.session.commit()
    flash('Tahapan dihapus.', 'success')
    return redirect(url_for('elections.phases', election_id=eid))

@elections_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    ep = ElectionPeriod.query.get_or_404(id)
    log_activity('Menghapus periode', 'election_period', ep.id)
    ElectionPhase.query.filter_by(election_period_id=ep.id).delete()
    db.session.delete(ep)
    db.session.commit()
    flash('Periode dihapus.', 'success')
    return redirect(url_for('elections.index'))
