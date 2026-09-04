from ..extensions import db
from datetime import datetime

class Coalition(db.Model):
    __tablename__ = 'coalitions'
    id = db.Column(db.Integer, primary_key=True)
    election_period_id = db.Column(db.Integer, db.ForeignKey('election_periods.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20))
    logo = db.Column(db.String(255))
    color = db.Column(db.String(7), default='#1B3A5C')
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    members = db.relationship('CoalitionMember', backref='coalition', lazy='dynamic')
    candidates = db.relationship('Candidate', backref='coalition', lazy='dynamic')

class CoalitionMember(db.Model):
    __tablename__ = 'coalition_members'
    id = db.Column(db.Integer, primary_key=True)
    coalition_id = db.Column(db.Integer, db.ForeignKey('coalitions.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    role = db.Column(db.String(50))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    organization = db.relationship('Organization', backref='coalition_memberships')
