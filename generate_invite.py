#!/usr/bin/python

import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# Define the InviteCode model
class InviteCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)

def generate_invite_code():
    code = secrets.token_hex(16)
    print(code)

    # Append the code to the database
    new_code = InviteCode(code=code)
    db.session.add(new_code)
    db.session.commit()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        n = int(sys.argv[1])
    else:
        n = 1
    with app.app_context():
        db.create_all()
        for _ in range(n):
            generate_invite_code()
        print("Invite codes generated and added to the database.")
