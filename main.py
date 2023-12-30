#!/usr/bin/python

from flask_login import LoginManager

from lib.models import db, User
from lib.config import create_app

app = create_app()

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':

    with app.app_context():
        db.create_all()
        login_manager.init_app(app)
    app.run(debug=True)
