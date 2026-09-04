from ..extensions import db
from datetime import datetime

class ElectionPeriod(db.Model):
    __tablename__ = 'election_periods'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(30), default='persiapan')
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    phases = db.relationship('ElectionPhase', backref='election_period', lazy='dynamic', order_by='ElectionPhase.order_number')
    candidates = db.relationship('Candidate', backref='election_period', lazy='dynamic')
    coalitions = db.relationship('Coalition', backref='election_period', lazy='dynamic')
    polling_stations = db.relationship('PollingStation', backref='election_period', lazy='dynamic')

class ElectionPhase(db.Model):
    __tablename__ = 'election_phases'
    id = db.Column(db.Integer, primary_key=True)
    election_period_id = db.Column(db.Integer, db.ForeignKey('election_periods.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='upcoming')
    order_number = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
