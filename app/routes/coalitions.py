from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from ..models import Coalition, CoalitionMember, Organization, ElectionPeriod
from ..extensions import db
from ..utils.audit import log_activity
from ..utils.upload import save_file, allowed_image

coalitions_bp = Blueprint('coalitions', __name__)

@coalitions_bp.route('/')
@login_required
def index():
    coalitions = Coalition.query.order_by(Coalition.name).all()
    return render_template('admin/coalitions/index.html', coalitions=coalitions)

@coalitions_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        logo_path = None
        if 'logo' in request.files:
            f = request.files['logo']
            if f and allowed_image(f.filename):
                logo_path = save_file(f, 'coalitions')
        coal = Coalition(
            election_period_id=request.form.get('election_period_id', type=int),
            name=request.form.get('name', '').strip(), code=request.form.get('code', '').strip(),
            logo=logo_path, color=request.form.get('color', '#1B3A5C'),
            description=request.form.get('description', ''), is_active=True
        )
        db.session.add(coal)
        db.session.commit()
        org_ids = request.form.getlist('org_ids[]')
        for oid in org_ids:
            db.session.add(CoalitionMember(coalition_id=coal.id, organization_id=int(oid)))
        db.session.commit()
        log_activity('Menambah koalisi', 'coalition', coal.id)
        flash('Koalisi berhasil ditambahkan.', 'success')
        return redirect(url_for('coalitions.index'))
    elections = ElectionPeriod.query.all()
    orgs = Organization.query.filter_by(is_active=True).all()
    return render_template('admin/coalitions/form.html', coalition=None, elections=elections, orgs=orgs)

@coalitions_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    coal = Coalition.query.get_or_404(id)
    if request.method == 'POST':
        if 'logo' in request.files:
            f = request.files['logo']
            if f and f.filename and allowed_image(f.filename):
                coal.logo = save_file(f, 'coalitions')
        coal.name = request.form.get('name', '').strip()
        coal.code = request.form.get('code', '').strip()
        coal.color = request.form.get('color', '#1B3A5C')
        coal.description = request.form.get('description', '')
        coal.is_active = bool(request.form.get('is_active'))
        CoalitionMember.query.filter_by(coalition_id=coal.id).delete()
        for oid in request.form.getlist('org_ids[]'):
            db.session.add(CoalitionMember(coalition_id=coal.id, organization_id=int(oid)))
        db.session.commit()
        log_activity('Mengedit koalisi', 'coalition', coal.id)
        flash('Koalisi diperbarui.', 'success')
        return redirect(url_for('coalitions.index'))
    elections = ElectionPeriod.query.all()
    orgs = Organization.query.filter_by(is_active=True).all()
    return render_template('admin/coalitions/form.html', coalition=coal, elections=elections, orgs=orgs)

@coalitions_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    coal = Coalition.query.get_or_404(id)
    log_activity('Menghapus koalisi', 'coalition', coal.id)
    CoalitionMember.query.filter_by(coalition_id=coal.id).delete()
    db.session.delete(coal)
    db.session.commit()
    flash('Koalisi dihapus.', 'success')
    return redirect(url_for('coalitions.index'))
