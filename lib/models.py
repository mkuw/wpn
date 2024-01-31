import datetime
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

class Season(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    multipliers = db.Column(db.JSON)

    def __init__(self, title, start_date, end_date, multipliers=None):
        self.title = title
        self.start_date = start_date
        self.end_date = end_date
        self.multipliers = multipliers or {}

    @staticmethod
    def get_current_season():
        today = datetime.datetime.today().date()
        return Season.query.filter(Season.start_date <= today, Season.end_date >= today).first()

def get_entries_for_season(season):
    return Entry.query.filter(
        Entry.date.between(season.start_date, season.end_date)).all()

def get_user_by_id(user_id):
    return User.query.get(int(user_id))

def get_season_by_title(season_title):
    return Season.query.filter_by(title=season_title).first()

def get_users_in_competition(entries):
    users = set()
    for entry in entries:
        users.add(get_user_by_id(entry.user_id).username)
    return list(users)

def get_season_days(season):
    end_date = min(season.end_date, datetime.date.today())
    delta = end_date - season.start_date
    past_days = [season.start_date + datetime.timedelta(days=i) for i in range(delta.days + 1)]
    delta = season.end_date - season.start_date
    all_days = [season.start_date + datetime.timedelta(days=i) for i in range(delta.days + 1)]
    return past_days, all_days

def get_multipliers(season):
    _, all_days = get_season_days(season)
    multipliers = []
    for day in all_days:
        key = day.strftime("%d/%m/%Y")
        if key in season.multipliers:
            multiplier = season.multipliers[key]
        else:
            multiplier = 1.0
        multipliers.append(multiplier)
    return multipliers

def get_podium(season):
    entries = get_entries_for_season(season)
    users = get_users_in_competition(entries)
    multipliers = get_multipliers(season)

    season_entries = {}
    for entry in entries:
        date_string = entry.date.strftime("%d/%m")
        username = get_user_by_id(entry.user_id).username
        season_entries[f"{date_string}_{username}"] = entry

    points_by_user = {}
    for user in users:
        total_points_by_user[user] = 0.0

    for multiplier, day in zip(multipliers, day):
        date_string = entry.date.strftime("%d/%m")
        for username in users:
            key = f"{date_string}_{username}"
            if key in season_entries:
                entry = season_entries[key]
                total = entry.w + entry.p + entry.n
            else:
                total = 24
            total *= multiplier
            total_points_by_user[username] += total
    print(total_points_by_user)
