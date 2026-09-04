from flask import Blueprint, render_template
from flask_login import login_required
from ..models import *
from ..extensions import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    stats = {
        'total_voters': Student.query.count(),
        'total_candidates': Candidate.query.count(),
        'total_coalitions': Coalition.query.count(),
        'total_organizations': Organization.query.count(),
        'total_votes': Vote.query.count(),
        'valid_votes': Vote.query.filter_by(is_valid=True).count(),
        'invalid_votes': Vote.query.filter_by(is_valid=False).count(),
        'total_news': News.query.count(),
    }
    # Get current election
    election = ElectionPeriod.query.order_by(ElectionPeriod.id.desc()).first()
    if election:
        stats['election_name'] = election.name
        stats['election_status'] = election.status
        reg_count = VoterRegistration.query.filter_by(election_period_id=election.id).count()
        voted_count = VoterRegistration.query.filter_by(election_period_id=election.id, has_voted=True).count()
        stats['registered_voters'] = reg_count
        stats['participation'] = round((voted_count / reg_count * 100), 1) if reg_count > 0 else 0
    # Candidate votes for chart
    candidates = []
    if election:
        for c in Candidate.query.filter_by(election_period_id=election.id, status='approved').all():
            vote_count = Vote.query.filter_by(candidate_id=c.id, is_valid=True).count()
            candidates.append({'name': c.name, 'number': c.candidate_number, 'votes': vote_count, 'color': c.coalition.color if c.coalition else '#999'})
    recent_logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html', stats=stats, candidates=candidates, recent_logs=recent_logs, election=election)
