from app import db
from datetime import datetime
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    account_type = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    personal_counter=db.Column(db.Integer, default=0)


# class TrashData(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     total_trash_collected = db.Column(db.Integer, default=60000)


