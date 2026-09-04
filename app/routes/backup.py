from flask import Blueprint, render_template, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from ..models.system import Backup
from ..extensions import db
from ..utils.backup import create_backup
from ..utils.audit import log_activity
from ..utils.auth import admin_required
import os

backup_bp = Blueprint('backup', __name__)


@backup_bp.route('/')
@login_required
@admin_required
def index():
    backups = Backup.query.order_by(
        Backup.created_at.desc()
    ).all()

    return render_template(
        'admin/backup/index.html',
        backups=backups
    )


@backup_bp.route('/create', methods=['POST'])
@login_required
@admin_required
def create():
    try:
        filename, filepath, size = create_backup()

        b = Backup(
            filename=filename,
            filepath=filepath,
            size_bytes=size,
            created_by=current_user.id
        )

        db.session.add(b)
        db.session.commit()

        log_activity(
            'Membuat backup database',
            'backup',
            b.id
        )

        flash(
            f'Backup berhasil dibuat: {filename}',
            'success'
        )

    except Exception as e:
        db.session.rollback()

        flash(
            f'Backup gagal: {str(e)}',
            'danger'
        )

    return redirect(
        url_for('backup.index')
    )


@backup_bp.route('/download/<int:id>')
@login_required
@admin_required
def download(id):
    backup = Backup.query.get_or_404(id)

    filepath = backup.filepath

    # Jika path yang tersimpan relatif,
    # ubah menjadi path absolut
    if not os.path.isabs(filepath):
        filepath = os.path.abspath(filepath)

    # Pastikan file benar-benar ada
    if not os.path.exists(filepath):
        flash(
            'File backup tidak ditemukan di server.',
            'danger'
        )

        return redirect(
            url_for('backup.index')
        )

    log_activity(
        'Mengunduh backup database',
        'backup',
        backup.id
    )

    return send_file(
        filepath,
        as_attachment=True,
        download_name=backup.filename
    )