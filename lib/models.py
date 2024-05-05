import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """Sql model for the user, contains the id, the username,
    the hash of the password, and the is_enabled field for
    the flask login."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_enabled = db.Column(db.Boolean, default=True)

    def is_active(self):
        """Check if the user is enabled."""
        return self.is_enabled

    @staticmethod
    def get_user_by_id(user_id):
        """Get the user by the id."""
        return User.query.get(int(user_id))

    @staticmethod
    def get_user_by_name(name):
        """Get the user by the name."""
        return User.query.filter_by(username=name).first()


class InviteCode(db.Model):
    """Sql model for the invite code."""
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)

class Entry(db.Model):
    """Sql model for the entry, contains the id, the user_id,
    the date, and the w p n scores."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('competitions', lazy=True))
    date = db.Column(db.Date, nullable=False)
    w  = db.Column(db.Integer, nullable=False)
    p = db.Column(db.Integer, nullable=False)
    n = db.Column(db.Integer, nullable=False)

class Season(db.Model):

    """Sql model for the season, contains the id, the title,
    the start date, the end date and multipliers."""

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
        """Get the current season based on today's date."""
        today = datetime.datetime.today().date()
        return Season.get_season_by_date(today)

    @staticmethod
    def get_season_by_date(date):
        return Season.query.filter(Season.start_date <= date, Season.end_date >= date).first()

    @staticmethod
    def get_season_by_title(season_title):
        """Get the season by title."""
        return Season.query.filter_by(title=season_title).first()

    @staticmethod
    def get_all_season():
        """Get the list of all the seasons."""
        return Season.query.all()

class SeasonService:

    """Class for doing season analysis, it is detached from
    the SQL model."""

    def __init__(self, season):
        self.season = season

    def is_none(self):
        return self.season is None

    def get_entries_for_season(self):
        """Return all the entries for the season."""
        return Entry.query.filter(
            Entry.date.between(self.season.start_date,
                               self.season.end_date)).all()

    def get_users_in_competition(self):
        """Return all the users which played in the season."""
        entries = self.get_entries_for_season()
        users = set()
        for entry in entries:
            users.add(User.get_user_by_id(entry.user_id).username)
        return list(users)

    def get_season_days(self):
        """Return the days of the season."""
        end_date = min(self.season.end_date, datetime.date.today())
        delta = end_date - self.season.start_date
        delta = self.season.end_date - self.season.start_date
        return [self.season.start_date + datetime.timedelta(days=i) for i in range(delta.days + 1)]

    def get_multipliers(self):
        """Return the multipliers of the season."""
        days = self.get_season_days()
        multipliers = []
        for day in days:
            key = day.strftime("%d/%m/%Y")
            if key in self.season.multipliers:
                multiplier = self.season.multipliers[key]
            else:
                multiplier = 1.0
            multipliers.append(multiplier)
        return multipliers

    def get_entries_dictionary(self):
        """Get the season entries as a dictionary with
        dates and users as keys."""
        season_entries = {}
        for entry in self.get_entries_for_season():
            date_string = entry.date.strftime("%d/%m")
            #if entry.user_id == 0 or isinstance(entry.user_id, str):
            #    db.session.delete(entry)
            #    db.session.commit()
            #    raise ValueError("Removed a broken entry")
            username = User.get_user_by_id(entry.user_id).username
            season_entries[f"{date_string}_{username}"] = entry
        return season_entries

    def get_start_end_dates(self):
        """Get the season start and end dates."""
        start_date = self.season.start_date.strftime("%d/%m/%Y")
        end_date = self.season.end_date.strftime("%d/%m/%Y")
        return start_date, end_date

    def get_title(self):
        """Get the season title."""
        return self.season.title

    def get_penalty(self, date, username):
        users = self.get_users_in_competition()
        season_entries = self.get_entries_dictionary()
        user_id = User.get_user_by_name(username).id
        date_string = date.strftime("%d/%m")
        if self.season.start_date >= datetime.date(2024, 4, 30):
            w = []
            p = []
            n = []
            for username in users:
                key = f"{date_string}_{username}"
                if key in season_entries:
                    entry = season_entries[key]
                    w.append(entry.w)
                    p.append(entry.p)
                    n.append(entry.p)
            penalty_w = min(max(w) + 1, 8)
            penalty_p = min(max(p) + 1, 8)
            penalty_n = min(max(n) + 1, 8)
        else:
            penalty_w = 8
            penalty_p = 8
            penalty_n = 8
        return Entry(user_id=user_id, date=date,
            w=penalty_w, p=penalty_p, n=penalty_n)

    def get_leaderboard(self):
        """Get the scores as a list of dictionaries, each
        containing user, points and position."""
        users = self.get_users_in_competition()
        multipliers = self.get_multipliers()
        season_days = self.get_season_days()

        season_entries = self.get_entries_dictionary()

        total_points_by_user = {}
        for user in users:
            total_points_by_user[user] = 0.0

        for multiplier, day in zip(multipliers, season_days):
            date_string = day.strftime("%d/%m")
            for username in users:
                key = f"{date_string}_{username}"
                if key in season_entries:
                    entry = season_entries[key]
                else:
                    entry = self.get_penalty(day, username)

                total = entry.w + entry.p + entry.n
                total *= multiplier
                total_points_by_user[username] += total

        sorted_users = sorted(total_points_by_user.items(), key=lambda x: x[1])
        leaderboard = []

        current_points = None
        current_position = 0

        for user, points in sorted_users:
            if points != current_points:
                current_points = points
                current_position += 1

            leaderboard.append({"user": user, "position": current_position, "points": points})

        return leaderboard
