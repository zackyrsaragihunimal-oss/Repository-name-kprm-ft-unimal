from ..extensions import db
from datetime import datetime

class Candidate(db.Model):
    __tablename__ = 'candidates'
    id = db.Column(db.Integer, primary_key=True)
    election_period_id = db.Column(db.Integer, db.ForeignKey('election_periods.id'), nullable=False)
    coalition_id = db.Column(db.Integer, db.ForeignKey('coalitions.id'))
    candidate_number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    nim = db.Column(db.String(20))
    photo = db.Column(db.String(255))
    position = db.Column(db.String(50), default='Ketua BEM FT')
    vision = db.Column(db.Text)
    mission = db.Column(db.Text)
    biography = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    programs = db.relationship('CandidateProgram', backref='candidate', lazy='dynamic', order_by='CandidateProgram.priority')
    votes = db.relationship('Vote', backref='candidate', lazy='dynamic')

    __table_args__ = (db.UniqueConstraint('election_period_id', 'candidate_number', name='uq_candidate_number'),)

class CandidateProgram(db.Model):
    __tablename__ = 'candidate_programs'
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
