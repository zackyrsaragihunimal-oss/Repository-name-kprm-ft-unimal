from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from ..models.user import User
from ..extensions import db
from ..utils.audit import log_activity
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password) and user.is_active:

            login_user(user)

            user.last_login = datetime.utcnow()

            db.session.commit()

            log_activity(
                'Login',
                'user',
                user.id
            )

            flash('Login berhasil!', 'success')

            next_page = request.args.get('next')

            return redirect(
                next_page or url_for('dashboard.index')
            )

        flash(
            'Username atau password salah.',
            'danger'
        )

    return render_template('admin/login.html')


@auth_bp.route('/logout')
def logout():

    if current_user.is_authenticated:

        log_activity(
            'Logout',
            'user',
            current_user.id
        )

    logout_user()

    flash(
        'Anda telah logout.',
        'info'
    )

    return redirect(
        url_for('public.home')
    )