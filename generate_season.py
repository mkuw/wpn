#!/usr/bin/python

import datetime
from flask import Flask
from lib.models import db, Season

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db.init_app(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        test_season = Season(title="Test Season",
            start_date=datetime.datetime(2023, 12, 1).date(),
            end_date=datetime.datetime(2023, 12, 31).date())
        db.session.add(test_season)
        db.session.commit()
        print("Test season added to the database.")
