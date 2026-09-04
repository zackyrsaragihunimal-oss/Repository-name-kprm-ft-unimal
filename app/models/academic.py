from ..extensions import db
from datetime import datetime

class Faculty(db.Model):
    __tablename__ = 'faculties'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10))
    dean = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    departments = db.relationship('Department', backref='faculty', lazy='dynamic')

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculties.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10))
    head = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    organizations = db.relationship('Organization', backref='department', lazy='dynamic')
    students = db.relationship('Student', backref='department', lazy='dynamic')

class Organization(db.Model):
    __tablename__ = 'organizations'
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20))
    logo = db.Column(db.String(255))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
