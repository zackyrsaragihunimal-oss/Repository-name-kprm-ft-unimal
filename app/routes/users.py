from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from ..models.user import User, Role
from ..extensions import db
from ..utils.audit import log_activity
from ..utils.auth import admin_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/')
@login_required
@admin_required
def index():
    users = User.query.all()
    return render_template('admin/users/index.html', users=users)

@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    if request.method == 'POST':
        u = User(username=request.form.get('username', '').strip(), email=request.form.get('email', '').strip(),
                 full_name=request.form.get('full_name', '').strip(), role_id=request.form.get('role_id', type=int), is_active=True)
        u.set_password(request.form.get('password', ''))
        db.session.add(u)
        db.session.commit()
        log_activity('Menambah user', 'user', u.id)
        flash('User ditambahkan.', 'success')
        return redirect(url_for('users.index'))
    roles = Role.query.all()
    return render_template('admin/users/form.html', user=None, roles=roles)

@users_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    u = User.query.get_or_404(id)
    if request.method == 'POST':
        u.username = request.form.get('username', '').strip()
        u.email = request.form.get('email', '').strip()
        u.full_name = request.form.get('full_name', '').strip()
        u.role_id = request.form.get('role_id', type=int)
        u.is_active = bool(request.form.get('is_active'))
        if request.form.get('password'):
            u.set_password(request.form['password'])
        db.session.commit()
        log_activity('Mengedit user', 'user', u.id)
        flash('User diperbarui.', 'success')
        return redirect(url_for('users.index'))
    roles = Role.query.all()
    return render_template('admin/users/form.html', user=u, roles=roles)

@users_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete(id):
    u = User.query.get_or_404(id)
    log_activity('Menghapus user', 'user', u.id)
    db.session.delete(u)
    db.session.commit()
    flash('User dihapus.', 'success')
    return redirect(url_for('users.index'))
