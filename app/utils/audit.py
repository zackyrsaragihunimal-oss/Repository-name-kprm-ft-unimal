from ..extensions import db
from ..models.system import ActivityLog
from flask import request
from flask_login import current_user
import json

def log_activity(action, entity_type=None, entity_id=None, old_data=None, new_data=None):
    try:
        log = ActivityLog(
            user_id=current_user.id if current_user and current_user.is_authenticated else None,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_data=json.dumps(old_data) if old_data else None,
            new_data=json.dumps(new_data) if new_data else None,
            ip_address=request.remote_addr if request else None
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()
