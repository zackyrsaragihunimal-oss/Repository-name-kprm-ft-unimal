from flask import Blueprint, jsonify
from ..models import Vote, Candidate, ElectionPeriod, VoterRegistration, PollingStation
from ..extensions import db
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/live-counting')
def live_counting():
    election = ElectionPeriod.query.order_by(ElectionPeriod.id.desc()).first()
    if not election:
        return jsonify({'error': 'No active election'}), 404
    total_registered = VoterRegistration.query.filter_by(election_period_id=election.id).count()
    total_voted = VoterRegistration.query.filter_by(election_period_id=election.id, has_voted=True).count()
    total_votes = Vote.query.filter_by(election_period_id=election.id).count()
    valid_votes = Vote.query.filter_by(election_period_id=election.id, is_valid=True).count()
    invalid_votes = Vote.query.filter_by(election_period_id=election.id, is_valid=False).count()
    participation = round((total_voted / total_registered * 100), 1) if total_registered > 0 else 0
    candidates_data = []
    for c in Candidate.query.filter_by(election_period_id=election.id, status='approved').order_by(Candidate.candidate_number).all():
        cv = Vote.query.filter_by(election_period_id=election.id, candidate_id=c.id, is_valid=True).count()
        pct = round((cv / valid_votes * 100), 1) if valid_votes > 0 else 0
        candidates_data.append({
            'id': c.id, 'number': c.candidate_number, 'name': c.name,
            'coalition': c.coalition.name if c.coalition else '-',
            'color': c.coalition.color if c.coalition else '#999',
            'votes': cv, 'percentage': pct,
            'photo': c.photo
        })
    return jsonify({
        'election': election.name, 'status': election.status,
        'total_registered': total_registered, 'total_voted': total_voted,
        'total_votes': total_votes, 'valid_votes': valid_votes,
        'invalid_votes': invalid_votes, 'participation': participation,
        'candidates': candidates_data, 'last_updated': datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')
    })

@api_bp.route('/stats')
def stats():
    election = ElectionPeriod.query.order_by(ElectionPeriod.id.desc()).first()
    from ..models import Student, Coalition, Organization
    return jsonify({
        'total_voters': Student.query.count(),
        'total_candidates': Candidate.query.filter_by(status='approved').count() if election else 0,
        'total_coalitions': Coalition.query.count(),
        'total_organizations': Organization.query.count(),
    })
