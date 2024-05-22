from app import db
from sqlalchemy import LargeBinary
from sqlalchemy import CheckConstraint

from datetime import datetime
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    account_type = db.Column(db.String(100), nullable=False)
    trash_collected = db.Column(db.Integer, default=0)
    unallocated_trash = db.Column(db.Integer, default=0)
    profile_picture = db.Column(db.LargeBinary, nullable=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    organization = db.relationship('Organization', backref=db.backref('users', lazy=True))


class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    image = db.Column(db.LargeBinary, nullable=True)
    total_trash = db.Column(db.Integer, default=0)

    __table_args__ = (
        CheckConstraint(type.in_(['school', 'company', 'volunteer']), name='check_organization_type'),
    )

# class TrashCounter(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     total_trash_collected = db.Column(db.Integer, default=60000)