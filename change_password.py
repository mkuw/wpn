#!/usr/bin/python

import argparse

from flask import Flask
from lib.models import db, User
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db.init_app(app)

def parse_args():
    parser = argparse.ArgumentParser(description="Resetta la password")
    parser.add_argument("username", type=str)
    parser.add_argument("password", type=str)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()

    with app.app_context():
        db.create_all()
        user = User.query.filter_by(username=args.username).first()
        if user:
            hashed_password = sha256_crypt.hash(args.password)
            user.password = hashed_password
            db.session.commit()
            print("Password resettata")
        else:
            print("Utente non trovato")
