from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_enabled = db.Column(db.Boolean, default=True)
    # Required for Flask-Login
    def is_active(self):
        return self.is_enabled

class InviteCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('competitions', lazy=True))
    date = db.Column(db.Date, nullable=False)
    w  = db.Column(db.Integer, nullable=False)
    p = db.Column(db.Integer, nullable=False)
    n = db.Column(db.Integer, nullable=False)
