from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from ..models.system import Setting
from ..extensions import db
from ..utils.audit import log_activity
from ..utils.auth import admin_required

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
def index():

    if request.method == 'POST':

        for key in request.form:

            if key.startswith('setting_'):

                skey = key.replace('setting_', '')

                s = Setting.query.filter_by(key=skey).first()

                if s:
                    s.value = request.form[key]

                else:
                    db.session.add(
                        Setting(
                            key=skey,
                            value=request.form[key]
                        )
                    )

        db.session.commit()

        log_activity(
            'Mengubah pengaturan sistem',
            'setting',
            None
        )

        flash(
            'Pengaturan disimpan.',
            'success'
        )

        return redirect(
            url_for('settings.index')
        )

    settings = {
        s.key: s
        for s in Setting.query.all()
    }

    return render_template(
        'admin/settings/index.html',
        settings=settings
    )