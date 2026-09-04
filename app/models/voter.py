from ..extensions import db
from datetime import datetime

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    nim = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    semester = db.Column(db.Integer)
    is_eligible = db.Column(db.Boolean, default=True)
    photo = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    registrations = db.relationship('VoterRegistration', backref='student', lazy='dynamic')

class VoterRegistration(db.Model):
    __tablename__ = 'voter_registrations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    election_period_id = db.Column(db.Integer, db.ForeignKey('election_periods.id'), nullable=False)
    polling_station_id = db.Column(db.Integer, db.ForeignKey('polling_stations.id'))
    is_registered = db.Column(db.Boolean, default=True)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    has_voted = db.Column(db.Boolean, default=False)
    voted_at = db.Column(db.DateTime)

    __table_args__ = (db.UniqueConstraint('student_id', 'election_period_id', name='uq_voter_election'),)
