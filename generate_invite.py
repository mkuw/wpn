#!/usr/bin/python

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Update with your actual database URI
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
    with app.app_context():
        db.create_all()
        generate_invite_code()
        print("Invite code generated and added to the database.")
