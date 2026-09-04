from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from ..models import Organization, Department, CoalitionMember
from ..extensions import db
from ..utils.audit import log_activity


organizations_bp = Blueprint('organizations', __name__)


@organizations_bp.route('/')
@login_required
def index():
    orgs = Organization.query.order_by(Organization.name).all()
    return render_template('admin/organizations/index.html', orgs=orgs)


@organizations_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():

    if request.method == 'POST':

        org = Organization(
            name=request.form.get('name', '').strip(),
            code=request.form.get('code', '').strip(),
            department_id=request.form.get('department_id', type=int),
            description=request.form.get('description', ''),
            is_active=True
        )

        db.session.add(org)
        db.session.commit()

        log_activity(
            'Menambah himpunan',
            'organization',
            org.id
        )

        flash('Himpunan ditambahkan.', 'success')

        return redirect(url_for('organizations.index'))

    depts = Department.query.all()

    return render_template(
        'admin/organizations/form.html',
        org=None,
        depts=depts
    )


@organizations_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):

    org = Organization.query.get_or_404(id)

    if request.method == 'POST':

        org.name = request.form.get('name', '').strip()
        org.code = request.form.get('code', '').strip()
        org.department_id = request.form.get(
            'department_id',
            type=int
        )
        org.description = request.form.get(
            'description',
            ''
        )
        org.is_active = bool(
            request.form.get('is_active')
        )

        db.session.commit()

        log_activity(
            'Mengedit himpunan',
            'organization',
            org.id
        )

        flash(
            'Himpunan diperbarui.',
            'success'
        )

        return redirect(
            url_for('organizations.index')
        )

    depts = Department.query.all()

    return render_template(
        'admin/organizations/form.html',
        org=org,
        depts=depts
    )


@organizations_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):

    org = Organization.query.get_or_404(id)

    # Simpan ID terlebih dahulu untuk audit
    org_id = org.id

    # ==========================================================
    # HAPUS RELASI HIMPUNAN DENGAN KOALISI TERLEBIH DAHULU
    # ==========================================================
    CoalitionMember.query.filter_by(
        organization_id=org.id
    ).delete(
        synchronize_session=False
    )

    # Setelah relasi dihapus, baru hapus organisasi
    db.session.delete(org)

    db.session.commit()

    # Catat aktivitas setelah berhasil dihapus
    log_activity(
        'Menghapus himpunan',
        'organization',
        org_id
    )

    flash(
        'Himpunan berhasil dihapus.',
        'success'
    )

    return redirect(
        url_for('organizations.index')
    )