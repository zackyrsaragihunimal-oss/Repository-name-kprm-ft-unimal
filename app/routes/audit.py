from flask import Blueprint, render_template, request
from flask_login import login_required
from ..models.system import ActivityLog

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).paginate(page=page, per_page=50)
    return render_template('admin/audit/index.html', logs=logs)
