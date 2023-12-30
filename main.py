#!/usr/bin/python

from flask import redirect, url_for
from flask_login import LoginManager, current_user

from lib.models import db, User
from lib.config import create_app

app = create_app()

@app.route("/")
def default_page():
    if current_user.is_authenticated:
        return redirect(url_for("insert_page.insert"))
    else:
        return redirect(url_for("login_page.login"))

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == "__main__":

    with app.app_context():
        db.create_all()
        login_manager.init_app(app)
    app.run(debug=True)
