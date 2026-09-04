from ..extensions import db
from datetime import datetime

class PollingStation(db.Model):
    __tablename__ = 'polling_stations'
    id = db.Column(db.Integer, primary_key=True)
    election_period_id = db.Column(db.Integer, db.ForeignKey('election_periods.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20))
    location = db.Column(db.String(200))
    capacity = db.Column(db.Integer, default=100)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    voter_registrations = db.relationship('VoterRegistration', backref='polling_station', lazy='dynamic')
    votes = db.relationship('Vote', backref='polling_station', lazy='dynamic')
    recapitulations = db.relationship('VoteRecapitulation', backref='polling_station', lazy='dynamic')

class Vote(db.Model):
    __tablename__ = 'votes'
    id = db.Column(db.Integer, primary_key=True)
    election_period_id = db.Column(db.Integer, db.ForeignKey('election_periods.id'), nullable=False)
    polling_station_id = db.Column(db.Integer, db.ForeignKey('polling_stations.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'))
    is_valid = db.Column(db.Boolean, default=True)
    voted_at = db.Column(db.DateTime, default=datetime.utcnow)
    # NOTE: NO foreign key to students table - ballot secrecy

class VoteRecapitulation(db.Model):
    __tablename__ = 'vote_recapitulations'
    id = db.Column(db.Integer, primary_key=True)
    election_period_id = db.Column(db.Integer, db.ForeignKey('election_periods.id'), nullable=False)
    polling_station_id = db.Column(db.Integer, db.ForeignKey('polling_stations.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    valid_votes = db.Column(db.Integer, default=0)
    invalid_votes = db.Column(db.Integer, default=0)
    total_votes = db.Column(db.Integer, default=0)
    recapitulated_at = db.Column(db.DateTime, default=datetime.utcnow)
    recapitulated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
